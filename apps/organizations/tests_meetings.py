from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, SharedProject, ProjectMeeting
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ProjectMeetingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password', email='test@test.com', email_verified=True)
        self.org = Organization.objects.create(name='Test Org', code='TEST')
        self.user.organization = self.org
        self.user.save()
        self.client.force_login(self.user)
        
        self.project = SharedProject.objects.create(
            name='Test Project',
            host_organization=self.org,
            created_by=self.user
        )
        self.project.members.add(self.user)
        
        self.url = reverse('organizations:project_meetings', kwargs={'pk': self.project.pk})

    def test_create_meeting(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=1)
        
        data = {
            'title': 'Test Meeting',
            'description': 'Discussion',
            'start_time': start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end.strftime('%Y-%m-%dT%H:%M'),
            'meeting_link': 'https://meet.google.com/abc-defg-hij'
        }
        
        response = self.client.post(self.url, data)
        
        # Check for redirection (success)
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(ProjectMeeting.objects.count(), 1)
        
    def test_create_meeting_invalid(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200) # Form errors
        self.assertEqual(ProjectMeeting.objects.count(), 0)
