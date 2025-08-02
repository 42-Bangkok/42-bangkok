from django.test import TestCase
from appdata.serializers.cadetmeta import (
    CadetmetaGetOut, CadetmetaPatchIn, CadetmetaPatchOut, GetLastestCadetMetaOut
)
from appdata.models.cadetmetas import CadetMeta
from appdata.models.intras import IntraProfile, HistIntraProfileData
import uuid
from datetime import datetime
from django.utils import timezone


class CadetMetaSerializersTest(TestCase):
    """Test cases for CadetMeta serializers."""
    
    def setUp(self):
        self.cadet_meta = CadetMeta.objects.create(
            login='testcadet',
            note='Test note for cadet'
        )
    
    def test_cadetmeta_get_out(self):
        """Test CadetmetaGetOut serializer."""
        # Get all fields from the model
        data = {
            'id': str(self.cadet_meta.id),
            'created': self.cadet_meta.created.isoformat(),
            'updated': self.cadet_meta.updated.isoformat(),
            'login': 'testcadet',
            'note': 'Test note for cadet'
        }
        
        serializer = CadetmetaGetOut(**data)
        self.assertEqual(serializer.login, 'testcadet')
        self.assertEqual(serializer.note, 'Test note for cadet')
        self.assertEqual(str(serializer.id), str(self.cadet_meta.id))
    
    def test_cadetmeta_patch_in(self):
        """Test CadetmetaPatchIn serializer."""
        data = {
            'note': 'Updated note'
        }
        serializer = CadetmetaPatchIn(**data)
        self.assertEqual(serializer.note, 'Updated note')
    
    def test_cadetmeta_patch_in_only_allows_note(self):
        """Test that CadetmetaPatchIn only accepts note field."""
        # Try to include other fields that shouldn't be allowed
        data = {
            'note': 'Updated note',
            'login': 'shouldnotwork',  # This should be ignored
        }
        serializer = CadetmetaPatchIn(**data)
        # Only note should be in the dict
        self.assertEqual(serializer.dict(), {'note': 'Updated note'})
    
    def test_cadetmeta_patch_out(self):
        """Test CadetmetaPatchOut serializer (inherits from GetOut)."""
        data = {
            'id': str(self.cadet_meta.id),
            'created': self.cadet_meta.created.isoformat(),
            'updated': self.cadet_meta.updated.isoformat(),
            'login': 'testcadet',
            'note': 'Test note for cadet'
        }
        
        serializer = CadetmetaPatchOut(**data)
        self.assertEqual(serializer.login, 'testcadet')
        self.assertEqual(serializer.note, 'Test note for cadet')


class GetLatestCadetMetaOutTest(TestCase):
    """Test cases for GetLastestCadetMetaOut serializer."""
    
    def setUp(self):
        self.intra_profile = IntraProfile.objects.create(
            login='testuser',
            intra_id=12345
        )
        self.hist_data = HistIntraProfileData.objects.create(
            profile=self.intra_profile,
            data={'test': 'data', 'user': 'info'}
        )
    
    def test_get_latest_cadet_meta_out(self):
        """Test GetLastestCadetMetaOut serializer."""
        data = {
            'id': str(self.hist_data.id),
            'created': self.hist_data.created.isoformat(),
            'updated': self.hist_data.updated.isoformat(),
            'profile': str(self.hist_data.profile.id),
            'data': {'test': 'data', 'user': 'info'}
        }
        
        serializer = GetLastestCadetMetaOut(**data)
        self.assertEqual(serializer.data, {'test': 'data', 'user': 'info'})
        self.assertEqual(str(serializer.profile), str(self.intra_profile.id))