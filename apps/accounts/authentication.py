import firebase_admin
from firebase_admin import auth, credentials
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import authentication, exceptions
import os

User = get_user_model()

def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    try:
        firebase_admin.get_app()
    except ValueError:
        # Priority 1: Check for JSON content in environment variable (Best for Render/Heroku)
        firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
        
        if firebase_creds_json:
            import json
            try:
                cred_dict = json.loads(firebase_creds_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                return
            except json.JSONDecodeError:
                print("Error: FIREBASE_CREDENTIALS_JSON is not valid JSON.")
            except Exception as e:
                print(f"Error initializing Firebase from env var: {e}")

        # Priority 2: Check for file path in settings (Development)
        if hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') and settings.FIREBASE_CREDENTIALS_PATH:
             cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
             firebase_admin.initialize_app(cred)
        else:
             # Priority 3: Default (Google Application Credentials)
             firebase_admin.initialize_app()

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF Authentication class for Firebase.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        id_token = auth_header.split(' ').pop()
        
        try:
            initialize_firebase()
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f'Invalid Firebase token: {str(e)}')

        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        if not email:
            raise exceptions.AuthenticationFailed('Firebase token must have an email associated.')

        # Get or create local user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For this project, we might want to auto-create or fail depending on flow
            # We'll fail here because we want them to go through a proper registration flow 
            # if they don't exist, to assign Organization, etc.
            # However, for Google Sign In to work seamlessly, we often auto-create.
            # Let's return None here so the view handles the "User not found" case
            # OR we can create a temporary user. 
            
            # Strategy: If the user doesn't exist, we can't authenticate them into a specific Organization yet.
            # So we raise an error effectively saying "Not registered in ConnectFlow".
            return None

        return (user, None)

class FirebaseBackend:
    """
    Django Authentication Backend for standard views (not just DRF).
    Usage: login(request, user, backend='apps.accounts.authentication.FirebaseBackend')
    """
    def authenticate(self, request, id_token=None):
        if not id_token:
            return None
            
        try:
            initialize_firebase()
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            print(f"Firebase verification failed: {e}")
            return None

        email = decoded_token.get('email')
        uid = decoded_token.get('uid')

        if not email:
            return None

        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            # Logic for new users via Google Sign In
            # We can create a user instance but not save it yet? 
            # Or save it with a default/null organization and redirect to "Complete Profile" page.
            
            # For now, let's create the user so they are logged in, 
            # but they will need to be redirected to an onboarding flow if organization is missing.
            
            # Check if we have name data
            first_name = decoded_token.get('name', '').split(' ')[0]
            last_name = ' '.join(decoded_token.get('name', '').split(' ')[1:])
            
            user = User.objects.create_user(
                username=email.split('@')[0], # Fallback username
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='TEAM_MEMBER', # Default
            )
            # user.set_unusable_password() # They use Firebase
            user.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
