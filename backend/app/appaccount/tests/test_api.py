from django.test import TestCase
from ninja.testing import TestClient
from unittest.mock import patch, MagicMock
from appaccount.models.accounts import User
from appaccount.models.auths import Session
from appaccount.api import router
from appcore.services.auths import ServiceBearerTokenAuth
from appaccount.services.auths import BearerTokenAuth


class AuthAPITest(TestCase):
    """Test cases for authentication API endpoints."""
    
    def setUp(self):
        self.client = TestClient(router)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('appaccount.routes.auths.create_session')
    def test_login_success(self, mock_create_session):
        """Test successful login."""
        # Mock the session creation
        mock_session = MagicMock()
        mock_session.access_token = 'test_access_token'
        mock_session.expires_in = 86400
        mock_session.refresh_token = 'test_refresh_token'
        mock_session.refresh_token_expires_in = 525600
        mock_create_session.return_value = mock_session
        
        # Mock service auth
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.post('/auths/login/', json={
                'uid': 'test123',
                'provider': '42',
                'email': 'test@example.com'
            })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['access_token'], 'test_access_token')
        self.assertEqual(data['expires_in'], 86400)
        self.assertEqual(data['refresh_token'], 'test_refresh_token')
        self.assertEqual(data['refresh_token_expires_in'], 525600)
    
    def test_logout_success(self):
        """Test successful logout."""
        # Create a real session
        session = Session.objects.create(user=self.user)
        
        # Mock auth to return the session
        with patch.object(BearerTokenAuth, '__call__', return_value=session):
            response = self.client.post('/auths/logout/')
        
        self.assertEqual(response.status_code, 204)
        # Verify session was deleted
        self.assertFalse(Session.objects.filter(id=session.id).exists())
    
    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # Create a session
        session = Session.objects.create(user=self.user)
        old_access_token = session.access_token
        
        response = self.client.post('/auths/refresh/', json={
            'refresh_token': session.refresh_token
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotEqual(data['access_token'], old_access_token)
        self.assertEqual(data['refresh_token'], session.refresh_token)
        self.assertEqual(data['expires_in'], 86400)
    
    def test_refresh_token_invalid(self):
        """Test refresh with invalid token."""
        response = self.client.post('/auths/refresh/', json={
            'refresh_token': 'invalid_token'
        })
        
        self.assertEqual(response.status_code, 401)
    
    def test_refresh_token_expired(self):
        """Test refresh with expired token."""
        session = Session.objects.create(user=self.user)
        
        # Mock the token as expired
        with patch.object(session, 'is_refresh_token_expired', return_value=True):
            response = self.client.post('/auths/refresh/', json={
                'refresh_token': session.refresh_token
            })
        
        self.assertEqual(response.status_code, 401)


class UserAPITest(TestCase):
    """Test cases for user-related API endpoints."""
    
    def setUp(self):
        self.client = TestClient(router)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create a profile for the user
        from appaccount.models.accounts import Profile
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            gender='m'
        )
        self.session = Session.objects.create(user=self.user)
        # Set userprofile attribute on user
        self.user.userprofile = self.profile
    
    def test_get_user_info_authenticated(self):
        """Test getting user info when authenticated."""
        # Mock auth to return the session
        with patch.object(BearerTokenAuth, '__call__', return_value=self.session):
            response = self.client.get('/users/me/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['first_name'], 'Test')
        self.assertEqual(data['last_name'], 'User')
        self.assertEqual(data['gender'], 'm')
    
    def test_patch_user_info(self):
        """Test updating user info."""
        with patch.object(BearerTokenAuth, '__call__', return_value=self.session):
            response = self.client.patch('/users/me/', json={
                'first_name': 'Updated',
                'last_name': 'Name',
                'gender': 'f'
            })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['first_name'], 'Updated')
        self.assertEqual(data['last_name'], 'Name')
        self.assertEqual(data['gender'], 'f')
        
        # Verify in database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'Updated')
    
    def test_patch_username(self):
        """Test updating username."""
        with patch.object(BearerTokenAuth, '__call__', return_value=self.session):
            response = self.client.patch('/users/me/', json={
                'username': 'newusername'
            })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['username'], 'newusername')
        
        # Verify in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
    
    def test_patch_username_already_exists(self):
        """Test updating to an existing username."""
        # Create another user
        User.objects.create_user(username='existing', email='existing@example.com')
        
        with patch.object(BearerTokenAuth, '__call__', return_value=self.session):
            response = self.client.patch('/users/me/', json={
                'username': 'existing'
            })
        
        # Should fail validation
        self.assertEqual(response.status_code, 422)
    
    def test_delete_user(self):
        """Test deleting user account."""
        user_id = self.user.id
        profile_id = self.profile.id
        
        with patch.object(BearerTokenAuth, '__call__', return_value=self.session):
            response = self.client.delete('/users/me/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify user and profile were deleted
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())