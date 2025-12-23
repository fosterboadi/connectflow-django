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
from .forms import ProfileSettingsForm
from apps.organizations.models import Organization

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
    The actual registration logic is handled by Firebase on the frontend,
    which then sends the ID token to LoginView.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return render(request, 'accounts/register.html')


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
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not id_token or not org_name:
            return JsonResponse({'error': 'ID token and Organization Name are required.'}, status=400)

        # Authenticate user first
        user = authenticate(request, id_token=id_token)
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
                organization = Organization.objects.create(
                    name=org_name,
                    code=code,
                    is_active=True
                )
                
                # Update user role and organization
                user.organization = organization
                user.role = 'SUPER_ADMIN'
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


@login_required
@require_POST
def mark_notifications_as_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'success': True})


@login_required
@require_POST
def toggle_theme(request):
    """Toggle user's theme between light and dark."""
    user = request.user
    user.theme = 'DARK' if user.theme == 'LIGHT' else 'LIGHT'
    user.save()
    return JsonResponse({'status': 'ok', 'theme': user.theme})
