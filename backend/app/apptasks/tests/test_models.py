from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apptasks.models.configs import DiscordWebhook


class DiscordWebhookModelTest(TestCase):
    """Test cases for DiscordWebhook model."""
    
    def setUp(self):
        self.webhook_data = {
            'name': 'test-webhook',
            'description': 'Test webhook for notifications',
            'url': 'https://discord.com/api/webhooks/123456789/abcdefg'
        }
    
    def test_create_discord_webhook(self):
        """Test creating a Discord webhook."""
        webhook = DiscordWebhook.objects.create(**self.webhook_data)
        self.assertEqual(webhook.name, 'test-webhook')
        self.assertEqual(webhook.description, 'Test webhook for notifications')
        self.assertEqual(webhook.url, 'https://discord.com/api/webhooks/123456789/abcdefg')
    
    def test_default_description(self):
        """Test default description value."""
        webhook = DiscordWebhook.objects.create(
            name='minimal-webhook',
            url='https://discord.com/api/webhooks/123/abc'
        )
        self.assertEqual(webhook.description, '')
    
    def test_name_unique_constraint(self):
        """Test that name must be unique."""
        DiscordWebhook.objects.create(**self.webhook_data)
        with self.assertRaises(IntegrityError):
            DiscordWebhook.objects.create(
                name='test-webhook',  # Same name
                url='https://discord.com/api/webhooks/999/xyz'
            )
    
    def test_str_method(self):
        """Test the string representation."""
        webhook = DiscordWebhook.objects.create(**self.webhook_data)
        self.assertEqual(str(webhook), 'test-webhook')
    
    def test_url_validation(self):
        """Test URL field validation."""
        webhook = DiscordWebhook(
            name='invalid-url-webhook',
            url='not-a-valid-url'
        )
        with self.assertRaises(ValidationError):
            webhook.full_clean()
    
    def test_valid_urls(self):
        """Test various valid URL formats."""
        valid_urls = [
            'https://discord.com/api/webhooks/123/abc',
            'http://example.com/webhook',
            'https://hooks.slack.com/services/T00/B00/XXX',
            'https://webhook.site/unique-url'
        ]
        
        for i, url in enumerate(valid_urls):
            webhook = DiscordWebhook(
                name=f'webhook-{i}',
                url=url
            )
            webhook.full_clean()  # Should not raise
    
    def test_update_webhook(self):
        """Test updating webhook fields."""
        webhook = DiscordWebhook.objects.create(**self.webhook_data)
        
        webhook.description = 'Updated description'
        webhook.url = 'https://discord.com/api/webhooks/999/updated'
        webhook.save()
        
        webhook.refresh_from_db()
        self.assertEqual(webhook.description, 'Updated description')
        self.assertEqual(webhook.url, 'https://discord.com/api/webhooks/999/updated')
    
    def test_multiple_webhooks(self):
        """Test creating multiple webhooks with different names."""
        webhook1 = DiscordWebhook.objects.create(
            name='webhook-1',
            url='https://discord.com/api/webhooks/111/aaa'
        )
        webhook2 = DiscordWebhook.objects.create(
            name='webhook-2',
            url='https://discord.com/api/webhooks/222/bbb'
        )
        webhook3 = DiscordWebhook.objects.create(
            name='webhook-3',
            url='https://discord.com/api/webhooks/333/ccc'
        )
        
        self.assertEqual(DiscordWebhook.objects.count(), 3)
        self.assertNotEqual(webhook1.id, webhook2.id)
        self.assertNotEqual(webhook2.id, webhook3.id)
    
    def test_webhook_inherits_base_models(self):
        """Test that webhook inherits from BaseUUID and BaseAutoDate."""
        webhook = DiscordWebhook.objects.create(**self.webhook_data)
        
        # Check UUID field
        self.assertIsNotNone(webhook.id)
        import uuid
        uuid.UUID(str(webhook.id))  # Should not raise
        
        # Check auto date fields
        self.assertIsNotNone(webhook.created)
        self.assertIsNotNone(webhook.updated)
        self.assertEqual(webhook.created, webhook.updated)
        
        # Update and check updated field changes
        import time
        time.sleep(0.01)
        webhook.description = 'Modified'
        webhook.save()
        webhook.refresh_from_db()
        self.assertGreater(webhook.updated, webhook.created)