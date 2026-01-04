from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Channel, Message
import json

@login_required
def channels_for_forward(request):
    """Simple JSON endpoint for forward modal - bypasses DRF"""
    try:
        # Get user's channels with member info
        channels = Channel.objects.filter(
            members=request.user,
            is_archived=False
        ).prefetch_related('members')
        
        # Build channel list with better names
        channel_list = []
        for ch in channels:
            display_name = ch.name
            
            # For DM channels, show the other person's name
            if ch.channel_type == Channel.ChannelType.DIRECT:
                # Get the other member (not current user)
                other_members = ch.members.exclude(id=request.user.id)
                if other_members.exists():
                    other_user = other_members.first()
                    full_name = other_user.get_full_name()
                    display_name = full_name if full_name else other_user.username
                else:
                    display_name = "Direct Message"
            
            channel_list.append({
                'id': str(ch.id),
                'name': ch.name,
                'display_name': display_name,
                'channel_type': ch.channel_type,
                'description': ch.description or '',
                'member_count': ch.members.count()
            })
        
        return JsonResponse(channel_list, safe=False)
    except Exception as e:
        # Return error as JSON
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to load channels'
        }, status=500)

@login_required
@require_POST
def forward_message(request):
    """Simple endpoint to forward a message"""
    try:
        data = json.loads(request.body)
        
        target_channel_id = data.get('channel')
        content = data.get('content', '')
        forwarded_from_id = data.get('forwarded_from')
        
        # Validate
        if not target_channel_id or not content:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get target channel
        target_channel = Channel.objects.get(id=target_channel_id)
        
        # Check user is member
        if not target_channel.members.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'Not a member of target channel'}, status=403)
        
        # Get original message if provided
        forwarded_from = None
        if forwarded_from_id:
            try:
                forwarded_from = Message.objects.get(id=forwarded_from_id)
            except Message.DoesNotExist:
                pass
        
        # Create forwarded message
        message = Message.objects.create(
            channel=target_channel,
            sender=request.user,
            content=content,
            forwarded_from=forwarded_from
        )
        
        return JsonResponse({
            'success': True,
            'message_id': str(message.id),
            'channel_id': str(target_channel.id)
        })
        
    except Channel.DoesNotExist:
        return JsonResponse({'error': 'Channel not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

