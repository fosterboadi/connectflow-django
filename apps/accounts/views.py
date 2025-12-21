from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserLoginForm, OrganizationSignupForm, ProfileSettingsForm
from apps.organizations.models import Organization


class RegisterView(View):
    """User registration view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to ConnectFlow Pro, {user.username}!')
            return redirect('accounts:dashboard')
        
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    """User login view."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        
        return render(request, 'accounts/login.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
    """User logout view."""
    
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class OrganizationSignupView(View):
    """Organization signup view for creating a company and super admin."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        form = OrganizationSignupForm()
        return render(request, 'accounts/organization_signup.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        
        form = OrganizationSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Generate organization code
                    org_code = form.generate_org_code(form.cleaned_data['org_name'])
                    
                    # Create organization
                    organization = Organization.objects.create(
                        name=form.cleaned_data['org_name'],
                        code=org_code,
                        is_active=True
                    )
                    
                    # Get the User model
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    
                    # Create super admin user
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password1'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        organization=organization,
                        role='SUPER_ADMIN'  # Set as Super Admin
                    )
                    
                    # Log the user in
                    login(request, user)
                    messages.success(
                        request, 
                        f'Welcome! Your organization "{organization.name}" has been created. '
                        f'Share code "{organization.code}" with your team members to join.'
                    )
                    return redirect('accounts:dashboard')
                    
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
        
        return render(request, 'accounts/organization_signup.html', {'form': form})


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
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile_settings')
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
