import uuid
from datetime import datetime
from django.test import TestCase
from django.utils import timezone
from django.db import models
from appcore.models.commons import BaseUUID, BaseAutoDate


class TestModel(BaseUUID, BaseAutoDate):
    """Test model that inherits from both base classes."""
    class Meta:
        app_label = 'appcore'


class BaseUUIDTest(TestCase):
    """Test cases for BaseUUID abstract model."""
    
    def test_uuid_field_created(self):
        """Test that a UUID is automatically generated."""
        obj = TestModel()
        self.assertIsNotNone(obj.id)
        self.assertIsInstance(obj.id, uuid.UUID)
    
    def test_uuid_is_unique(self):
        """Test that each instance gets a unique UUID."""
        obj1 = TestModel()
        obj2 = TestModel()
        self.assertNotEqual(obj1.id, obj2.id)
    
    def test_uuid_not_editable(self):
        """Test that UUID field is not editable."""
        field = TestModel._meta.get_field('id')
        self.assertFalse(field.editable)


class BaseAutoDateTest(TestCase):
    """Test cases for BaseAutoDate abstract model."""
    
    def test_created_date_auto_set(self):
        """Test that created date is automatically set."""
        obj = TestModel()
        obj.save()
        self.assertIsNotNone(obj.created)
        self.assertIsInstance(obj.created, datetime)
        self.assertLessEqual(obj.created, timezone.now())
    
    def test_updated_date_auto_set(self):
        """Test that updated date is automatically set."""
        obj = TestModel()
        obj.save()
        self.assertIsNotNone(obj.updated)
        self.assertIsInstance(obj.updated, datetime)
        self.assertLessEqual(obj.updated, timezone.now())
    
    def test_updated_date_changes_on_save(self):
        """Test that updated date changes when object is saved again."""
        obj = TestModel()
        obj.save()
        original_updated = obj.updated
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)
        
        obj.save()
        self.assertGreater(obj.updated, original_updated)
    
    def test_created_date_doesnt_change(self):
        """Test that created date doesn't change on subsequent saves."""
        obj = TestModel()
        obj.save()
        original_created = obj.created
        
        import time
        time.sleep(0.01)
        
        obj.save()
        self.assertEqual(obj.created, original_created)