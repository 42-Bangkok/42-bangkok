from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from appaccount.models.accounts import Profile
from appaccount.models.auths import Session
from unittest.mock import patch

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for custom User model."""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a new user."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertIsNotNone(user.id)
    
    def test_user_has_uuid_primary_key(self):
        """Test that user has UUID as primary key."""
        user = User.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.id)
        # Check if it's a valid UUID by trying to recreate it
        import uuid
        uuid.UUID(str(user.id))


class ProfileModelTest(TestCase):
    """Test cases for Profile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_profile(self):
        """Test creating a profile."""
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            gender='m'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.gender, 'm')
    
    def test_profile_defaults(self):
        """Test profile default values."""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.first_name, '')
        self.assertEqual(profile.last_name, '')
        self.assertEqual(profile.gender, 'u')
        self.assertIsNone(profile.dob)
        self.assertIsNone(profile.time_of_birth)
        self.assertEqual(profile.medical_condition, '')
        self.assertEqual(profile.job_title, '')
    
    def test_profile_one_to_one_constraint(self):
        """Test that a user can have only one profile."""
        Profile.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)
    
    def test_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted."""
        profile = Profile.objects.create(user=self.user)
        profile_id = profile.id
        self.user.delete()
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())
    
    def test_gender_choices(self):
        """Test valid gender choices."""
        valid_choices = ['m', 'f', 'n', 'o', 'u']
        for choice in valid_choices:
            profile = Profile(user=self.user, gender=choice)
            profile.full_clean()  # Should not raise validation error


class SessionModelTest(TestCase):
    """Test cases for Session model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_session(self):
        """Test creating a session."""
        session = Session.objects.create(user=self.user)
        self.assertEqual(session.user, self.user)
        self.assertIsNotNone(session.access_token)
        self.assertIsNotNone(session.refresh_token)
        self.assertEqual(session.expires_in, 86400)  # 1 day
        self.assertEqual(session.refresh_token_expires_in, 525600)  # 365 days
    
    def test_tokens_are_generated(self):
        """Test that tokens are automatically generated."""
        session = Session.objects.create(user=self.user)
        self.assertTrue(len(session.access_token) > 0)
        self.assertTrue(len(session.refresh_token) > 0)
        self.assertNotEqual(session.access_token, session.refresh_token)
    
    def test_refresh_token_unique_constraint(self):
        """Test that refresh tokens must be unique."""
        session1 = Session.objects.create(user=self.user)
        session2 = Session(user=self.user, refresh_token=session1.refresh_token)
        with self.assertRaises(IntegrityError):
            session2.save()
    
    def test_is_expired_false(self):
        """Test that a fresh session is not expired."""
        session = Session.objects.create(user=self.user)
        self.assertFalse(session.is_expired())
    
    def test_is_expired_true(self):
        """Test that an old session is expired."""
        session = Session.objects.create(user=self.user)
        # Manually set created time to past
        session.access_token_created = timezone.now() - timedelta(seconds=86401)
        session.save()
        self.assertTrue(session.is_expired())
    
    def test_is_refresh_token_expired_false(self):
        """Test that a fresh refresh token is not expired."""
        session = Session.objects.create(user=self.user)
        self.assertFalse(session.is_refresh_token_expired())
    
    def test_is_refresh_token_expired_true(self):
        """Test that an old refresh token is expired."""
        session = Session.objects.create(user=self.user)
        # Manually set created time to past
        session.refresh_token_created = timezone.now() - timedelta(seconds=525601)
        session.save()
        self.assertTrue(session.is_refresh_token_expired())
    
    def test_destroy(self):
        """Test destroying a session."""
        session = Session.objects.create(user=self.user)
        session_id = session.id
        session.destroy()
        self.assertFalse(Session.objects.filter(id=session_id).exists())
    
    @patch('appaccount.models.auths.gen_token')
    def test_refresh_with_valid_token(self, mock_gen_token):
        """Test refreshing session with valid refresh token."""
        mock_gen_token.return_value = 'new_access_token'
        session = Session.objects.create(user=self.user)
        old_access_token = session.access_token
        old_created = session.access_token_created
        
        # Wait a bit to ensure time difference
        import time
        time.sleep(0.01)
        
        result = session.refresh(session.refresh_token)
        self.assertTrue(result)
        self.assertEqual(session.access_token, 'new_access_token')
        self.assertNotEqual(session.access_token, old_access_token)
        self.assertGreater(session.access_token_created, old_created)
    
    def test_refresh_with_invalid_token(self):
        """Test refreshing session with invalid refresh token."""
        session = Session.objects.create(user=self.user)
        old_access_token = session.access_token
        
        result = session.refresh('invalid_token')
        self.assertFalse(result)
        self.assertEqual(session.access_token, old_access_token)
    
    def test_session_cascade_delete(self):
        """Test that sessions are deleted when user is deleted."""
        session = Session.objects.create(user=self.user)
        session_id = session.id
        self.user.delete()
        self.assertFalse(Session.objects.filter(id=session_id).exists())