from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.chat_channels.models import Channel, Message
from rest_framework.test import APIClient
from rest_framework import status
import uuid

User = get_user_model()

class PinMessageTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        
        # Create organization
        self.org = Organization.objects.create(
            name='Test Org',
            code='test-org-123',
        )
        self.user.organization = self.org
        self.user.save()
        
        # Create channel
        self.channel = Channel.objects.create(
            name='general',
            organization=self.org,
            channel_type=Channel.ChannelType.TEAM,
            created_by=self.user
        )
        self.channel.members.add(self.user)
        
        # Create message
        self.message = Message.objects.create(
            channel=self.channel,
            sender=self.user,
            content="Hello world"
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = f'/api/v1/messages/{self.message.id}/pin/'

    def test_pin_message(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_pinned'])
        
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_pinned)

    def test_unpin_message(self):
        self.message.is_pinned = True
        self.message.save()
        
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_pinned'])
        
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_pinned)

    def test_broadcast_chat_message_integrity(self):
        """
        Ensure _broadcast handles chat_message event without KeyError
        (specifically validating sender_details['full_name']).
        """
        from apps.chat_channels.api_views import MessageViewSet
        viewset = MessageViewSet()
        viewset.request = type('obj', (object,), {'user': self.user})
        
        try:
            viewset._broadcast(self.message, 'chat_message')
        except KeyError as e:
            self.fail(f"_broadcast raised KeyError: {e}")
        except Exception as e:
            self.fail(f"_broadcast raised unexpected exception: {e}")