from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Channel

@login_required
def channels_for_forward(request):
    """Simple JSON endpoint for forward modal - bypasses DRF"""
    try:
        # Get user's channels
        channels = Channel.objects.filter(
            members=request.user,
            is_archived=False
        ).values('id', 'name', 'channel_type', 'description')
        
        # Convert to list and add member count
        channel_list = []
        for ch in channels:
            channel_list.append({
                'id': str(ch['id']),
                'name': ch['name'],
                'channel_type': ch['channel_type'],
                'description': ch.get('description', ''),
                'member_count': 2  # Simplified for now
            })
        
        return JsonResponse(channel_list, safe=False)
    except Exception as e:
        # Return error as JSON
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load channels'
        }, status=500)
