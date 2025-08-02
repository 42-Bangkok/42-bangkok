from django.test import TestCase
from django.db import IntegrityError
from appdata.models.intras import IntraProfile, HistIntraProfileData
from appdata.models.cadetmetas import CadetMeta


class IntraProfileModelTest(TestCase):
    """Test cases for IntraProfile model."""
    
    def setUp(self):
        self.profile_data = {
            'login': 'testuser',
            'intra_id': 12345,
            'pool_month': 'January',
            'pool_year': '2024',
            'cursus_ids': [1, 2, 3]
        }
    
    def test_create_intra_profile(self):
        """Test creating an IntraProfile."""
        profile = IntraProfile.objects.create(**self.profile_data)
        self.assertEqual(profile.login, 'testuser')
        self.assertEqual(profile.intra_id, 12345)
        self.assertFalse(profile.isBookmarked)
        self.assertEqual(profile.pool_month, 'January')
        self.assertEqual(profile.pool_year, '2024')
        self.assertEqual(profile.cursus_ids, [1, 2, 3])
    
    def test_intra_profile_defaults(self):
        """Test IntraProfile default values."""
        profile = IntraProfile.objects.create(intra_id=99999)
        self.assertIsNone(profile.login)
        self.assertFalse(profile.isBookmarked)
        self.assertIsNone(profile.pool_month)
        self.assertIsNone(profile.pool_year)
        self.assertEqual(profile.cursus_ids, [])
    
    def test_login_unique_constraint(self):
        """Test that login must be unique."""
        IntraProfile.objects.create(login='unique_user', intra_id=11111)
        with self.assertRaises(IntegrityError):
            IntraProfile.objects.create(login='unique_user', intra_id=22222)
    
    def test_intra_id_unique_constraint(self):
        """Test that intra_id must be unique."""
        IntraProfile.objects.create(login='user1', intra_id=11111)
        with self.assertRaises(IntegrityError):
            IntraProfile.objects.create(login='user2', intra_id=11111)
    
    def test_str_method(self):
        """Test the string representation."""
        profile = IntraProfile.objects.create(**self.profile_data)
        self.assertEqual(str(profile), 'testuser')
    
    def test_str_method_with_no_login(self):
        """Test string representation when login is None."""
        profile = IntraProfile.objects.create(intra_id=99999)
        self.assertEqual(str(profile), 'None')
    
    def test_bookmark_toggle(self):
        """Test bookmarking functionality."""
        profile = IntraProfile.objects.create(**self.profile_data)
        self.assertFalse(profile.isBookmarked)
        
        profile.isBookmarked = True
        profile.save()
        profile.refresh_from_db()
        self.assertTrue(profile.isBookmarked)
    
    def test_cursus_ids_array_field(self):
        """Test array field operations."""
        profile = IntraProfile.objects.create(intra_id=12345)
        self.assertEqual(profile.cursus_ids, [])
        
        profile.cursus_ids.append(1)
        profile.cursus_ids.extend([2, 3])
        profile.save()
        profile.refresh_from_db()
        self.assertEqual(profile.cursus_ids, [1, 2, 3])


class HistIntraProfileDataModelTest(TestCase):
    """Test cases for HistIntraProfileData model."""
    
    def setUp(self):
        self.profile = IntraProfile.objects.create(
            login='testuser',
            intra_id=12345
        )
        self.sample_data = {
            'id': 12345,
            'login': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_hist_data(self):
        """Test creating historical data."""
        hist_data = HistIntraProfileData.objects.create(
            profile=self.profile,
            data=self.sample_data
        )
        self.assertEqual(hist_data.profile, self.profile)
        self.assertEqual(hist_data.data, self.sample_data)
    
    def test_str_method(self):
        """Test the string representation."""
        hist_data = HistIntraProfileData.objects.create(
            profile=self.profile,
            data=self.sample_data
        )
        str_repr = str(hist_data)
        self.assertIn('testuser', str_repr)
        self.assertIn(str(hist_data.created.year), str_repr)
    
    def test_cascade_delete(self):
        """Test that historical data is deleted when profile is deleted."""
        hist_data = HistIntraProfileData.objects.create(
            profile=self.profile,
            data=self.sample_data
        )
        hist_id = hist_data.id
        self.profile.delete()
        self.assertFalse(HistIntraProfileData.objects.filter(id=hist_id).exists())
    
    def test_multiple_historical_entries(self):
        """Test creating multiple historical entries for same profile."""
        data1 = {'version': 1, 'data': 'old'}
        data2 = {'version': 2, 'data': 'new'}
        
        hist1 = HistIntraProfileData.objects.create(profile=self.profile, data=data1)
        hist2 = HistIntraProfileData.objects.create(profile=self.profile, data=data2)
        
        self.assertEqual(HistIntraProfileData.objects.filter(profile=self.profile).count(), 2)
        
        # Test getting latest data
        latest = HistIntraProfileData.objects.filter(
            profile=self.profile
        ).order_by('-created').first()
        self.assertEqual(latest.data, data2)
    
    def test_json_field_operations(self):
        """Test JSON field storage and retrieval."""
        complex_data = {
            'nested': {
                'key': 'value',
                'list': [1, 2, 3]
            },
            'boolean': True,
            'null': None
        }
        hist_data = HistIntraProfileData.objects.create(
            profile=self.profile,
            data=complex_data
        )
        hist_data.refresh_from_db()
        self.assertEqual(hist_data.data, complex_data)


class CadetMetaModelTest(TestCase):
    """Test cases for CadetMeta model."""
    
    def test_create_cadet_meta(self):
        """Test creating a CadetMeta."""
        meta = CadetMeta.objects.create(
            login='testcadet',
            note='This is a test note'
        )
        self.assertEqual(meta.login, 'testcadet')
        self.assertEqual(meta.note, 'This is a test note')
    
    def test_default_note(self):
        """Test default note value."""
        meta = CadetMeta.objects.create(login='testcadet')
        self.assertEqual(meta.note, '')
    
    def test_login_unique_constraint(self):
        """Test that login must be unique."""
        CadetMeta.objects.create(login='unique_cadet')
        with self.assertRaises(IntegrityError):
            CadetMeta.objects.create(login='unique_cadet')
    
    def test_str_method(self):
        """Test the string representation."""
        meta = CadetMeta.objects.create(login='testcadet')
        self.assertEqual(str(meta), 'testcadet')
    
    def test_note_text_field(self):
        """Test that note can store long text."""
        long_text = 'A' * 10000  # 10k characters
        meta = CadetMeta.objects.create(
            login='testcadet',
            note=long_text
        )
        meta.refresh_from_db()
        self.assertEqual(meta.note, long_text)
    
    def test_update_note(self):
        """Test updating the note field."""
        meta = CadetMeta.objects.create(
            login='testcadet',
            note='Initial note'
        )
        meta.note = 'Updated note'
        meta.save()
        meta.refresh_from_db()
        self.assertEqual(meta.note, 'Updated note')