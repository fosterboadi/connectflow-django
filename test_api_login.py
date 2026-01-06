import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectflow.settings')
django.setup()

from django.contrib.auth import authenticate
from apps.accounts.models import User

# Check user
user = User.objects.get(email='apitest@test.com')
print(f'User: {user.email}')
print(f'Username: {user.username}')
print(f'Active: {user.is_active}')
print(f'Verified: {user.email_verified}')
print(f'Has password: {user.has_usable_password()}')
print(f'Check password: {user.check_password("testpass123")}')

# Test authentication with email as username
auth_user = authenticate(username='apitest@test.com', password='testpass123')
print(f'\nAuthenticate with email: {auth_user}')

# Test authentication with actual username
if user.username != user.email:
    auth_user2 = authenticate(username=user.username, password='testpass123')
    print(f'Authenticate with username: {auth_user2}')
