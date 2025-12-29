from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Notification
from apps.organizations.models import Organization

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.org = Organization.objects.create(name='Test Org', code='TEST')
        self.user = User.objects.create_user(
            username='testuser', 
            password='password', 
            email='test@test.com',
            email_verified=True,
            organization=self.org
        )
        self.client.force_login(self.user)
        
        # Create unread notifications
        self.notif1 = Notification.notify(
            recipient=self.user,
            title="Test 1",
            content="Content 1",
            notification_type=Notification.NotificationType.SYSTEM
        )
        self.notif2 = Notification.notify(
            recipient=self.user,
            title="Test 2",
            content="Content 2",
            notification_type=Notification.NotificationType.MESSAGE
        )

    def test_notification_creation_defaults(self):
        self.assertFalse(self.notif1.is_read)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 2)

    def test_mark_as_read_view(self):
        url = reverse('accounts:mark_notifications_read')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        
        # Check DB
        self.notif1.refresh_from_db()
        self.notif2.refresh_from_db()
        self.assertTrue(self.notif1.is_read)
        self.assertTrue(self.notif2.is_read)
        self.assertEqual(Notification.objects.filter(recipient=self.user, is_read=False).count(), 0)

    def test_context_processor_integration(self):
        """Verify the global context processor shows correct count."""
        # This requires the context processor to be correctly registered in settings
        # and checking a rendered template or request context.
        # We can simulate the context processor logic here.
        from apps.accounts.context_processors import notifications_processor
        
        # Mock request with user
        class MockRequest:
            user = self.user
            
        context = notifications_processor(MockRequest())
        self.assertEqual(context['unread_notifications_count'], 2)
        
        # Mark one as read manually
        self.notif1.is_read = True
        self.notif1.save()
        
        context = notifications_processor(MockRequest())
        self.assertEqual(context['unread_notifications_count'], 1)
