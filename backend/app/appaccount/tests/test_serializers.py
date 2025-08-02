from django.test import TestCase
from django.contrib.auth import get_user_model
from appaccount.serializers.auths import LoginPostIn, LoginPostOut, RefreshPostIn, RefreshPostOut
from appaccount.serializers.users import MeGetOut, MePatchIn, MePatchOut
from appaccount.models.accounts import Profile
from pydantic import ValidationError

User = get_user_model()


class AuthSerializersTest(TestCase):
    """Test cases for auth serializers."""
    
    def test_login_post_in_valid(self):
        """Test LoginPostIn with valid data."""
        data = {
            'uid': 'test123',
            'provider': '42',
            'email': 'test@example.com'
        }
        serializer = LoginPostIn(**data)
        self.assertEqual(serializer.uid, 'test123')
        self.assertEqual(serializer.provider, '42')
        self.assertEqual(serializer.email, 'test@example.com')
    
    def test_login_post_in_without_email(self):
        """Test LoginPostIn without email (optional)."""
        data = {
            'uid': 'test123',
            'provider': '42'
        }
        serializer = LoginPostIn(**data)
        self.assertEqual(serializer.uid, 'test123')
        self.assertEqual(serializer.provider, '42')
        self.assertIsNone(serializer.email)
    
    def test_login_post_in_invalid_provider(self):
        """Test LoginPostIn with invalid provider."""
        data = {
            'uid': 'test123',
            'provider': 'invalid',
            'email': 'test@example.com'
        }
        with self.assertRaises(ValidationError):
            LoginPostIn(**data)
    
    def test_login_post_in_invalid_email(self):
        """Test LoginPostIn with invalid email."""
        data = {
            'uid': 'test123',
            'provider': '42',
            'email': 'not-an-email'
        }
        with self.assertRaises(ValidationError):
            LoginPostIn(**data)
    
    def test_login_post_out(self):
        """Test LoginPostOut serializer."""
        data = {
            'access_token': 'test_access_token',
            'expires_in': 86400,
            'refresh_token': 'test_refresh_token',
            'refresh_token_expires_in': 525600
        }
        serializer = LoginPostOut(**data)
        self.assertEqual(serializer.access_token, 'test_access_token')
        self.assertEqual(serializer.expires_in, 86400)
        self.assertEqual(serializer.refresh_token, 'test_refresh_token')
        self.assertEqual(serializer.refresh_token_expires_in, 525600)
    
    def test_refresh_post_in(self):
        """Test RefreshPostIn serializer."""
        data = {'refresh_token': 'test_refresh_token'}
        serializer = RefreshPostIn(**data)
        self.assertEqual(serializer.refresh_token, 'test_refresh_token')
    
    def test_refresh_post_out(self):
        """Test RefreshPostOut serializer."""
        data = {
            'access_token': 'new_access_token',
            'expires_in': 86400,
            'refresh_token': 'same_refresh_token'
        }
        serializer = RefreshPostOut(**data)
        self.assertEqual(serializer.access_token, 'new_access_token')
        self.assertEqual(serializer.expires_in, 86400)
        self.assertEqual(serializer.refresh_token, 'same_refresh_token')


class UserSerializersTest(TestCase):
    """Test cases for user serializers."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            gender='m'
        )
    
    def test_me_get_out(self):
        """Test MeGetOut serializer."""
        profile_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'm',
            'dob': None,
            'time_of_birth': None,
            'medical_condition': '',
            'job_title': '',
            'created': self.profile.created,
            'updated': self.profile.updated
        }
        data = {**profile_data, 'username': 'testuser'}
        
        serializer = MeGetOut(**data)
        self.assertEqual(serializer.username, 'testuser')
        self.assertEqual(serializer.first_name, 'Test')
        self.assertEqual(serializer.last_name, 'User')
        self.assertEqual(serializer.gender, 'm')
    
    def test_me_patch_in_valid_gender(self):
        """Test MePatchIn with valid gender."""
        data = {
            'gender': 'f'
        }
        serializer = MePatchIn(**data)
        self.assertEqual(serializer.gender, 'f')
    
    def test_me_patch_in_invalid_gender(self):
        """Test MePatchIn with invalid gender."""
        data = {
            'gender': 'x'  # Invalid gender
        }
        with self.assertRaises(ValidationError) as context:
            MePatchIn(**data)
        self.assertIn('gender must be one of', str(context.exception))
    
    def test_me_patch_in_valid_username(self):
        """Test MePatchIn with valid new username."""
        data = {
            'username': 'newusername'
        }
        serializer = MePatchIn(**data)
        self.assertEqual(serializer.username, 'newusername')
    
    def test_me_patch_in_existing_username(self):
        """Test MePatchIn with existing username."""
        # Create another user
        User.objects.create_user(username='existing', email='existing@example.com')
        
        data = {
            'username': 'existing'
        }
        with self.assertRaises(ValidationError) as context:
            MePatchIn(**data)
        self.assertIn('username already exists', str(context.exception))
    
    def test_me_patch_in_username_too_short(self):
        """Test MePatchIn with username too short."""
        data = {
            'username': 'ab'  # Less than 3 characters
        }
        with self.assertRaises(ValidationError):
            MePatchIn(**data)
    
    def test_me_patch_in_username_too_long(self):
        """Test MePatchIn with username too long."""
        data = {
            'username': 'a' * 151  # More than 150 characters
        }
        with self.assertRaises(ValidationError):
            MePatchIn(**data)
    
    def test_me_patch_in_partial_update(self):
        """Test MePatchIn with partial data."""
        data = {
            'first_name': 'Updated'
            # Other fields not provided
        }
        serializer = MePatchIn(**data)
        self.assertEqual(serializer.first_name, 'Updated')
        # Check that dict excludes None values
        dict_data = serializer.dict(exclude_none=True)
        self.assertEqual(dict_data, {'first_name': 'Updated'})
    
    def test_me_patch_out(self):
        """Test MePatchOut serializer (inherits from MeGetOut)."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'm',
            'dob': None,
            'time_of_birth': None,
            'medical_condition': '',
            'job_title': '',
            'created': self.profile.created,
            'updated': self.profile.updated
        }
        serializer = MePatchOut(**data)
        self.assertEqual(serializer.username, 'testuser')