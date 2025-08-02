from django.test import TestCase
from ninja.testing import TestClient
from unittest.mock import patch, MagicMock
from appdata.api import router
from appdata.models.cadetmetas import CadetMeta
from appdata.models.intras import IntraProfile, HistIntraProfileData
from appcore.services.auths import ServiceBearerTokenAuth


class CadetMetaAPITest(TestCase):
    """Test cases for CadetMeta API endpoints."""
    
    def setUp(self):
        self.client = TestClient(router)
        # Create test data
        self.cadet_meta = CadetMeta.objects.create(
            login='testcadet',
            note='Test note'
        )
    
    def test_get_cadetmeta_existing(self):
        """Test getting existing cadetmeta."""
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.get('/cadetmeta/testcadet/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['login'], 'testcadet')
        self.assertEqual(data['note'], 'Test note')
    
    def test_get_cadetmeta_creates_if_not_exists(self):
        """Test that getting non-existent cadetmeta creates it."""
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.get('/cadetmeta/newcadet/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['login'], 'newcadet')
        self.assertEqual(data['note'], '')
        
        # Verify it was created in database
        self.assertTrue(CadetMeta.objects.filter(login='newcadet').exists())
    
    def test_patch_cadetmeta_existing(self):
        """Test updating existing cadetmeta."""
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.patch('/cadetmeta/testcadet/', json={
                'note': 'Updated note'
            })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['note'], 'Updated note')
        
        # Verify in database
        self.cadet_meta.refresh_from_db()
        self.assertEqual(self.cadet_meta.note, 'Updated note')
    
    def test_patch_cadetmeta_creates_if_not_exists(self):
        """Test that patching non-existent cadetmeta creates it."""
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.patch('/cadetmeta/anothernew/', json={
                'note': 'New cadet note'
            })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['login'], 'anothernew')
        self.assertEqual(data['note'], 'New cadet note')
        
        # Verify it was created in database
        cadet = CadetMeta.objects.get(login='anothernew')
        self.assertEqual(cadet.note, 'New cadet note')
    
    @patch('appdata.routes.cadetmeta.query_latest_hist_intra_profile_data')
    def test_get_latest_cadetmeta(self, mock_query):
        """Test getting latest cadetmeta list."""
        # Mock the query to return test data
        mock_query.return_value = []
        
        with patch.object(ServiceBearerTokenAuth, '__call__', return_value=True):
            response = self.client.get('/cadetmeta/latest/')
        
        self.assertEqual(response.status_code, 200)
        mock_query.assert_called_once()


class IntraAPITest(TestCase):
    """Test cases for Intra API endpoints."""
    
    def setUp(self):
        self.client = TestClient(router)
        # Create test data
        self.intra_profile = IntraProfile.objects.create(
            login='testuser',
            intra_id=12345,
            pool_month='January',
            pool_year='2024'
        )
        self.hist_data = HistIntraProfileData.objects.create(
            profile=self.intra_profile,
            data={'test': 'data'}
        )