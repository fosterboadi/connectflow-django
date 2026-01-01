"""
Permissions Policy Middleware

Sets the Permissions-Policy HTTP header to allow microphone and camera access
for voice messages and video calls.
"""

class PermissionsPolicyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Set Permissions-Policy header
        # Allow microphone and camera on same origin only
        response['Permissions-Policy'] = (
            'microphone=(self), '
            'camera=(self), '
            'geolocation=(), '
            'payment=()'
        )
        
        return response
