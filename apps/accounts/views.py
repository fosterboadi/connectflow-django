from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
import os
from django.contrib.auth import get_user_model
from .forms import ProfileSettingsForm
from apps.organizations.models import Organization
from django.db.models import Q
from django.urls import reverse

User = get_user_model()

class GlobalSearchView(View):
    """
    Search across users, channels, projects and messages.
    Returns JSON for the live dropdown.
    """
    @method_decorator(login_required)
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query or len(query) < 2:
            return JsonResponse({'results': []})

        results = []
        user_org = request.user.organization
        
        # 1. Search Users in the same organization
        users = User.objects.filter(
            organization=user_org
        ).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(professional_role__icontains=query)
        )[:5]

        for u in users:
            results.append({
                'type': 'User',
                'title': u.get_full_name() or u.username,
                'subtitle': u.professional_role or u.email,
                'url': reverse('accounts:profile_detail', kwargs={'pk': u.pk}),
                'icon': 'user'
            })

        # 2. Search Channels
        from apps.chat_channels.models import Channel
        channels = Channel.objects.filter(
            organization=user_org,
            is_archived=False
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        
        # Filter by permission
        viewable_channels = [c for c in channels if c.can_user_view(request.user)][:5]
        
        for c in viewable_channels:
            results.append({
                'type': 'Channel',
                'title': f"#{c.name}",
                'subtitle': c.get_channel_type_display(),
                'url': reverse('chat_channels:channel_detail', kwargs={'pk': c.pk}),
                'icon': 'hashtag'
            })

        # 3. Search Shared Projects
        from apps.organizations.models import SharedProject
        projects = SharedProject.objects.filter(
            Q(host_organization=user_org) | Q(guest_organizations=user_org)
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()
        
        # Only show if user is a member
        my_projects = projects.filter(members=request.user)[:5]
        
        for p in my_projects:
            results.append({
                'type': 'Project',
                'title': p.name,
                'subtitle': f"Hosted by {p.host_organization.name}",
                'url': reverse('organizations:shared_project_detail', kwargs={'pk': p.pk}),
                'icon': 'folder'
            })

        return JsonResponse({'results': results})

class VerifyEmailView(View):
    """
    Renders the email verification required page.
    """
    def get(self, request):
        if request.user.is_authenticated and request.user.email_verified:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/verify_email.html')

@method_decorator(csrf_exempt, name='dispatch')
class SyncEmailVerificationView(View):
    """
    API endpoint to sync email verification status from Firebase ID token.
    """
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
            
        try:
            data = json.loads(request.body)
            id_token = data.get('id_token')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not id_token:
            return JsonResponse({'error': 'ID token is required.'}, status=400)

        # Authenticate with the token to sync status
        user = authenticate(request, id_token=id_token)
        
        if user and user == request.user:
            return JsonResponse({'status': 'ok', 'email_verified': user.email_verified})
        else:
            return JsonResponse({'error': 'Failed to sync or user mismatch.'}, status=400)


class LoginView(View):
    """
    Handles user login.
    GET: Renders the login page.
    POST: Authenticates user with Firebase ID token.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/login.html')

    @method_decorator(csrf_exempt)
    def post(self, request):
        if request.user.is_authenticated:
            return JsonResponse({'status': 'ok', 'message': 'Already logged in.'})
        
        try:
            data = json.loads(request.body)
            id_token = data.get('id_token')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not id_token:
            return JsonResponse({'error': 'ID token is required.'}, status=400)

        user = authenticate(request, id_token=id_token)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'error': 'Invalid token or user not found.'}, status=403)


class RegisterView(View):
    """
    Renders the registration page.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/register.html')


class RegisterAPIView(View):
    """
    API endpoint to register a user and join an organization using a code.
    """
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            id_token = data.get('id_token')
            org_code = data.get('org_code')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not id_token or not org_code:
            return JsonResponse({'error': 'ID token and Organization Code are required.'}, status=400)

        # 1. Verify Organization Code
        try:
            organization = Organization.objects.get(code=org_code, is_active=True)
        except Organization.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive organization code.'}, status=400)

        # 2. Authenticate User (syncs status and captures names if provided)
        user = authenticate(request, id_token=id_token, first_name=first_name, last_name=last_name)
        if not user:
            return JsonResponse({'error': 'Authentication failed.'}, status=403)
        
        # Explicitly check verification from token again to be sure (authenticate does it, but good for clarity)
        # Note: 'authenticate' already updated 'email_verified' via FirebaseBackend logic we just added.

        # 3. Associate with Organization
        user.organization = organization
        user.role = 'TEAM_MEMBER' # Default for joining via code
        user.save()

        login(request, user)
        messages.success(request, f'Successfully joined {organization.name}!')
        return JsonResponse({'status': 'ok'})


class OrganizationSignupView(View):
    """
    Renders the organization signup page.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/organization_signup.html')


class CreateOrganizationView(View):
    """
    API endpoint to create an organization and assign the user as Super Admin.
    """
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)
            id_token = data.get('id_token')
            org_name = data.get('org_name')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not id_token or not org_name:
            return JsonResponse({'error': 'ID token and Organization Name are required.'}, status=400)

        # Authenticate user first
        user = authenticate(request, id_token=id_token, first_name=first_name, last_name=last_name)
        if not user:
            return JsonResponse({'error': 'Authentication failed.'}, status=403)

        # Logic to generate Org Code (reused from form logic, simplified here)
        import re
        from datetime import datetime
        
        # Remove special characters and get first letters of each word
        words = re.sub(r'[^a-zA-Z0-9\s]', '', org_name).upper().split()
        if len(words) >= 2:
            base_code = ''.join(word[:2] for word in words[:2])
        else:
            base_code = words[0][:4] if words else 'ORG'
        
        year = datetime.now().year
        code = f"{base_code}{year}"
        
        # Ensure uniqueness
        counter = 1
        original_code = code
        while Organization.objects.filter(code=code).exists():
            code = f"{original_code}{counter}"
            counter += 1

        try:
            with transaction.atomic():
                # Try to find a default free plan
                from apps.organizations.models import SubscriptionPlan
                free_plan = SubscriptionPlan.objects.filter(price_monthly=0, is_active=True).first()

                organization = Organization.objects.create(
                    name=org_name,
                    code=code,
                    is_active=True,
                    subscription_plan=free_plan,
                    subscription_status='active' if free_plan else 'inactive'
                )
                
                # Update user role and organization
                user.organization = organization
                user.role = 'ORG_ADMIN'
                user.save()
                
                login(request, user)
                
                return JsonResponse({'status': 'ok', 'org_code': code})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    """User logout view."""
    
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


@login_required
def dashboard(request):
    """User dashboard view."""
    return render(request, 'accounts/dashboard.html')


@method_decorator(login_required, name='dispatch')
class ProfileSettingsView(View):
    """View for user to update their profile settings."""

    def get(self, request):
        form = ProfileSettingsForm(instance=request.user)
        return render(request, 'accounts/profile_settings.html', {'form': form})

    def post(self, request):
        form = ProfileSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Debug logging
            if user.avatar:
                print(f"[DEBUG] Avatar saved: {user.avatar}")
                print(f"[DEBUG] Avatar URL: {user.avatar.url}")
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile_settings')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        return render(request, 'accounts/profile_settings.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    """View to display another user's profile."""
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        user_to_view = get_object_or_404(User, pk=pk, organization=request.user.organization)
        return render(request, 'accounts/profile_detail.html', {'viewed_user': user_to_view})


@login_required
@require_POST
def mark_notifications_as_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
def toggle_theme(request):
    """Toggle user's theme between light and dark."""
    user = request.user
    user.theme = 'DARK' if user.theme == 'LIGHT' else 'LIGHT'
    user.save()
    return JsonResponse({'status': 'ok', 'theme': user.theme})


@login_required
def promote_me(request):
    """
    Secret view to promote the first Super Admin on a new deployment.
    Requires PLATFORM_SECRET_KEY to be set in environment.
    """
    if request.method == 'POST':
        secret = request.POST.get('secret_key')
        env_secret = os.environ.get('PLATFORM_SECRET_KEY')
        
        if not env_secret:
            messages.error(request, "Platform secret key is not configured on the server.")
            return redirect('accounts:dashboard')
            
        if secret == env_secret:
            user = request.user
            user.role = User.Role.SUPER_ADMIN
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.success(request, "Congratulations! You are now a Platform Super Admin.")
            return redirect('accounts:platform_dashboard')
        else:
            messages.error(request, "Invalid secret key.")
            
    return render(request, 'accounts/promote_me.html')
