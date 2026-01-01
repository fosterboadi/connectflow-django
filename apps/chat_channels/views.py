from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Channel, Message, MessageReaction, Attachment
from .forms import ChannelForm, MessageForm, BreakoutRoomForm


@login_required
def channel_list(request):
    """List all channels user has access to."""
    user = request.user
    
    if not user.organization:
        messages.warning(request, 'You are not assigned to any organization.')
        return redirect('accounts:dashboard')
    
    # Get channels user can access
    channels = Channel.objects.filter(
        organization=user.organization,
        is_archived=False
    ).select_related('department', 'team', 'created_by').prefetch_related('members')
    
    # Filter by type
    official_channels = channels.filter(channel_type=Channel.ChannelType.OFFICIAL)
    department_channels = channels.filter(channel_type=Channel.ChannelType.DEPARTMENT)
    team_channels = channels.filter(channel_type=Channel.ChannelType.TEAM)
    project_channels = channels.filter(channel_type=Channel.ChannelType.PROJECT)
    private_channels = channels.filter(channel_type=Channel.ChannelType.PRIVATE, members=user)
    direct_messages = channels.filter(channel_type=Channel.ChannelType.DIRECT, members=user)
    
    context = {
        'official_channels': official_channels,
        'department_channels': department_channels,
        'team_channels': team_channels,
        'project_channels': project_channels,
        'private_channels': private_channels,
        'direct_messages': direct_messages,
        'can_create': user.is_admin or user.is_manager
    }
    return render(request, 'chat_channels/channel_list.html', context)


@login_required
def start_direct_message(request, user_id):
    """Start or get a direct message channel with another user."""
    user = request.user
    # Need to import User here or at top
    from apps.accounts.models import User
    other_user = get_object_or_404(User, id=user_id, organization=user.organization)
    
    if user == other_user:
        messages.error(request, "You cannot start a direct message with yourself.")
        return redirect('chat_channels:channel_list')
    
    # Check if a direct message channel already exists between these two users
    channel = Channel.objects.filter(
        channel_type=Channel.ChannelType.DIRECT,
        organization=user.organization,
        members=user
    ).filter(members=other_user).first()
    
    if not channel:
        # Create a new direct message channel
        # Use a unique but deterministic name
        ids = sorted([str(user.id), str(other_user.id)])
        channel_name = f"dm-{ids[0][:8]}-{ids[1][:8]}"
        channel = Channel.objects.create(
            name=channel_name,
            channel_type=Channel.ChannelType.DIRECT,
            organization=user.organization,
            is_private=True
        )
        channel.members.add(user, other_user)
    
    return redirect('chat_channels:channel_detail', pk=channel.pk)


@login_required
def breakout_create(request, channel_id):
    """Create a breakout room from a parent channel."""
    user = request.user
    parent_channel = get_object_or_404(Channel, pk=channel_id, organization=user.organization)
    
    # Check permission to create (must be member of parent channel)
    if not parent_channel.can_user_view(user):
        messages.error(request, 'You do not have permission to create a breakout room here.')
        return redirect('chat_channels:channel_detail', pk=channel_id)

    if request.method == 'POST':
        form = BreakoutRoomForm(request.POST, parent_channel=parent_channel)
        if form.is_valid():
            breakout = form.save(commit=False)
            breakout.channel_type = Channel.ChannelType.BREAKOUT
            breakout.organization = user.organization
            breakout.parent_channel = parent_channel
            breakout.created_by = user
            breakout.is_private = True  # Breakout rooms are implicitly private to invitees
            breakout.save()
            
            form.save_m2m()
            # Ensure creator is a member
            breakout.members.add(user)
            
            messages.success(request, f'Breakout room "{breakout.name}" started!')
            return redirect('chat_channels:channel_detail', pk=breakout.pk)
    else:
        form = BreakoutRoomForm(parent_channel=parent_channel)
    
    context = {
        'form': form,
        'parent_channel': parent_channel,
        'action': 'Start Breakout Room'
    }
    return render(request, 'chat_channels/breakout_form.html', context)


@login_required
def breakout_close(request, pk):
    """Close and archive a breakout room."""
    user = request.user
    channel = get_object_or_404(Channel, pk=pk, organization=user.organization, channel_type=Channel.ChannelType.BREAKOUT)
    
    # Only creator or admin can close
    if not (user.is_admin or channel.created_by == user):
        messages.error(request, 'You do not have permission to close this room.')
        return redirect('chat_channels:channel_detail', pk=pk)
    
    if request.method == 'POST':
        channel.is_active = False
        channel.is_archived = True
        channel.read_only = True
        channel.save()
        messages.success(request, 'Breakout room closed and archived.')
        
        # Redirect to parent channel if exists
        if channel.parent_channel:
            return redirect('chat_channels:channel_detail', pk=channel.parent_channel.pk)
        return redirect('chat_channels:channel_list')
        
    return render(request, 'chat_channels/breakout_confirm_close.html', {'channel': channel})


@login_required
def project_channel_create(request, project_id):
    """Create a new channel within a shared project."""
    user = request.user
    from apps.organizations.models import SharedProject
    project = get_object_or_404(SharedProject, pk=project_id)
    
    # Check permission (must be project member and admin of their org)
    if user not in project.members.all() or not user.is_admin:
        messages.error(request, 'You do not have permission to create channels for this project.')
        return redirect('organizations:shared_project_detail', pk=project_id)
    
    if request.method == 'POST':
        form = ChannelForm(request.POST, organization=user.organization, shared_project=project)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.organization = user.organization
            channel.shared_project = project
            channel.created_by = user
            channel.save()
            form.save_m2m()
            
            # Ensure creator is a member
            channel.members.add(user)
            
            messages.success(request, f'Channel "#{channel.name}" created for project!')
            return redirect('organizations:shared_project_detail', pk=project_id)
    else:
        form = ChannelForm(organization=user.organization, shared_project=project)
    
    context = {'form': form, 'action': 'Create Project Channel', 'project': project}
    return render(request, 'chat_channels/channel_form.html', context)


@login_required
def channel_create(request):
    """Create a new channel."""
    user = request.user
    
    if not (user.is_admin or user.is_manager):
        messages.error(request, 'You do not have permission to create channels.')
        return redirect('chat_channels:channel_list')
    
    if request.method == 'POST':
        form = ChannelForm(request.POST, organization=user.organization)
        if form.is_valid():
            # The form.save() now handles members and team/dept auto-add
            channel = form.save(commit=False)
            channel.organization = user.organization
            channel.created_by = user
            channel.save()
            form.save_m2m() # This will trigger the logic in form.save() correctly if called or we just call save()
            
            # Ensure creator is a member
            channel.members.add(user)
            
            messages.success(request, f'Channel "#{channel.name}" created successfully!')
            return redirect('chat_channels:channel_detail', pk=channel.pk)
    else:
        form = ChannelForm(organization=user.organization)
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'chat_channels/channel_form.html', context)


@login_required
def channel_detail(request, pk):
    """View channel details and messages."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    # Check if user can view this channel
    if not channel.can_user_view(user):
        messages.error(request, 'You do not have permission to view this channel.')
        return redirect('chat_channels:channel_list')
    
    # Get messages (WhatsApp style: all messages in one stream)
    messages_query = Message.objects.filter(
        channel=channel
    ).select_related('sender', 'parent_message').prefetch_related(
        'reactions',
        'attachments'
    )
    
    # Handle search
    search_query = request.GET.get('q')
    if search_query:
        messages_query = messages_query.filter(
            Q(content__icontains=search_query) |
            Q(sender__first_name__icontains=search_query) |
            Q(sender__last_name__icontains=search_query) |
            Q(sender__username__icontains=search_query)
        )
    
    channel_messages = messages_query.order_by('-is_pinned', 'created_at')
    
    # Add date separators info to messages
    messages_with_dates = []
    prev_date = None
    for msg in channel_messages:
        msg_date = msg.created_at.date()
        if prev_date is None or msg_date != prev_date:
            msg.show_date_separator = True
            msg.date_label = msg.created_at
        else:
            msg.show_date_separator = False
        prev_date = msg_date
        messages_with_dates.append(msg)
    
    channel_messages = messages_with_dates
    
    # Get active breakout rooms for this channel
    breakout_rooms = Channel.objects.filter(
        parent_channel=channel,
        is_active=True,
        channel_type=Channel.ChannelType.BREAKOUT
    )
    
    # Get sidebar conversation list
    user_channels_query = Channel.objects.filter(
        organization=user.organization,
        is_archived=False,
        members=user
    ).exclude(channel_type=Channel.ChannelType.DIRECT).distinct()

    # If the current channel is not a DM and not in user_channels (e.g. admin viewing it), add it to the list
    if channel.channel_type != Channel.ChannelType.DIRECT and channel not in user_channels_query:
        # Convert to list to allow appending
        user_channels = list(user_channels_query)
        user_channels.append(channel)
    else:
        user_channels = user_channels_query

    direct_messages = Channel.objects.filter(
        organization=user.organization,
        channel_type=Channel.ChannelType.DIRECT,
        members=user
    ).distinct()
    
    # Handle message posting
    if request.method == 'POST':
        # Manually ensure voice_message is in request.FILES if it was sent as such
        # This fixes issues where the widget might interfere or if sent via FormData
        if 'voice_message' in request.FILES:
             # Just to be sure it's available for the form
             pass

        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.channel = channel
            message.sender = request.user
            
            content = message.content.strip()
            
            # Identify message type
            if request.FILES.get('voice_message'):
                message.message_type = 'VOICE'
            elif request.FILES.getlist('attachments'):
                first_file = request.FILES.getlist('attachments')[0]
                if first_file.content_type.startswith('image/'):
                    message.message_type = 'IMAGE'
                elif first_file.content_type.startswith('video/'):
                    message.message_type = 'VIDEO'
                else:
                    message.message_type = 'FILE'
            else:
                # Check for Emoji-only
                import re
                emoji_pattern = re.compile(
                    "["
                    "\U0001F600-\U0001F64F"  # emoticons
                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                    "\U0001F680-\U0001F6FF"  # transport & map symbols
                    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                    "\U00002702-\U000027B0"  # dingbats
                    "\U000024C2-\U0001F251"
                    "\U0001F900-\U0001F9FF"  # supplemental symbols
                    "\U0001FA00-\U0001FA6F"  # extended symbols
                    "\U00002600-\U000026FF"  # miscellaneous symbols
                    "\U00002700-\U000027BF"  # dingbats
                    "\U0001F191-\U0001F19A"  # enclosed characters
                    "]+", 
                    flags=re.UNICODE
                )
                text_without_emoji = emoji_pattern.sub('', content).strip()
                has_emojis = bool(emoji_pattern.search(content))
                
                if has_emojis and not text_without_emoji:
                    message.message_type = 'EMOJI'
                else:
                    message.message_type = 'TEXT'
            
            message.save()
            
            processed_attachments = []
            try:
                # Handle multiple attachments
                attachments = request.FILES.getlist('attachments')
                for attachment_file in attachments:
                    att = Attachment.objects.create(message=message, file=attachment_file)
                    processed_attachments.append({
                        'url': att.file.url, 
                        'name': str(att.file).split('/')[-1],
                        'is_image': att.is_image,
                        'is_video': att.is_video
                    })
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Attachment upload failed: {str(e)}", exc_info=True)
                
                # If attachment upload fails, permanently delete the orphan message
                try:
                    message.delete(force=True)
                except:
                    pass  # Message might already be deleted
                    
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    error_msg = str(e) if str(e) else "Unknown upload error"
                    return JsonResponse({
                        'success': False, 
                        'error': f'Upload failed: {error_msg}'
                    }, status=400)  # Changed from 500 to 400
                messages.error(request, f'Failed to upload attachments: {e}')
                return redirect('chat_channels:channel_detail', pk=pk)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message_id': str(message.id),
                    'message_type': message.message_type,
                    'content': message.content,
                    'sender_avatar': request.user.avatar.url if request.user.avatar else None,
                    'voice_message_url': message.voice_message.url if message.voice_message else None,
                    'timestamp': message.created_at.strftime('%b %d, %I:%M %p'),
                    'attachments': [
                        {'name': att.file.name, 'url': att.file.url} for att in message.attachments.all()
                    ]
                })
            
            return redirect('chat_channels:channel_detail', pk=pk)
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return form errors as JSON
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'error': 'Form validation failed', 'details': errors}, status=400)
    else:
        form = MessageForm()
    
    context = {
        'channel': channel,
        'chat_messages': channel_messages,
        'breakout_rooms': breakout_rooms,
        'user_channels': user_channels,
        'direct_messages': direct_messages,
        'form': form,
        'search_query': search_query,
        'can_edit': user.is_admin or channel.created_by == user,
        'is_member': user in channel.members.all(),
        'can_post': channel.can_user_post(user) if hasattr(channel, 'can_user_post') else user in channel.members.all()
    }
    return render(request, 'chat_channels/channel_detail.html', context)


@login_required
def channel_edit(request, pk):
    """Edit a channel."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    if not (user.is_admin or channel.created_by == user):
        messages.error(request, 'You do not have permission to edit this channel.')
        return redirect('chat_channels:channel_detail', pk=pk)
    
    if request.method == 'POST':
        form = ChannelForm(request.POST, instance=channel, organization=user.organization)
        if form.is_valid():
            form.save()
            messages.success(request, f'Channel "#{channel.name}" updated successfully!')
            return redirect('chat_channels:channel_detail', pk=pk)
    else:
        form = ChannelForm(instance=channel, organization=user.organization)
    
    context = {'form': form, 'action': 'Edit', 'channel': channel}
    return render(request, 'chat_channels/channel_form.html', context)


@login_required
def channel_delete(request, pk):
    """Delete a channel."""
    user = request.user
    channel = get_object_or_404(
        Channel, 
        pk=pk, 
        organization=user.organization
    )
    
    if not user.is_admin:
        messages.error(request, 'Only admins can delete channels.')
        return redirect('chat_channels:channel_detail', pk=pk)
    
    if request.method == 'POST':
        channel_name = channel.name
        channel.delete()
        messages.success(request, f'Channel "#{channel_name}" deleted successfully!')
        return redirect('chat_channels:channel_list')
    
    context = {'channel': channel}
    return render(request, 'chat_channels/channel_confirm_delete.html', context)


@login_required
@require_POST
def message_edit(request, pk):
    """Edit an existing message. Only sender can edit."""
    user = request.user
    message = get_object_or_404(Message, pk=pk)
    
    # Strictly only the sender can edit. Admins can delete but NOT edit.
    if message.sender != user:
        return JsonResponse({'success': False, 'error': 'Unauthorized: Only the author can edit this message.'}, status=403)
    
    # Cannot edit deleted messages
    if message.is_deleted:
        return JsonResponse({'success': False, 'error': 'Cannot edit deleted messages.'}, status=400)
    
    # Cannot edit voice messages or system messages
    if message.message_type in ['VOICE', 'SYSTEM']:
        return JsonResponse({'success': False, 'error': 'Cannot edit this type of message.'}, status=400)
    
    new_content = request.POST.get('content')
    if not new_content or not new_content.strip():
        return JsonResponse({'success': False, 'error': 'Content cannot be empty.'}, status=400)
    
    # Update message
    from django.utils import timezone
    message.content = new_content.strip()
    message.is_edited = True
    message.last_edited_at = timezone.now()
    message.edited_by = user
    message.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'content': message.content,
            'message_id': str(message.id),
            'edited_at': message.last_edited_at.strftime('%b %d, %I:%M %p') if message.last_edited_at else None
        })
    
    return redirect('chat_channels:channel_detail', pk=message.channel.pk)


@login_required
@require_POST
def message_delete(request, pk):
    """Soft delete a message and broadcast to the channel."""
    user = request.user
    message = get_object_or_404(Message, pk=pk)
    channel_id = str(message.channel.id)
    
    # Only sender or admin can delete
    if message.sender == user or user.is_admin:
        message.delete(user=user) # Uses soft delete
        
        # Broadcast via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{channel_id}',
            {
                'type': 'message_deleted',
                'message_id': str(pk),
                'deleted_at': message.deleted_at.isoformat() if message.deleted_at else None,
                'deleted_by': user.id
            }
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'deleted_at': message.deleted_at.isoformat() if message.deleted_at else None,
                'deleted_by': user.id
            })
    
    return redirect('chat_channels:channel_detail', pk=message.channel.pk)


@login_required
@require_POST
def message_react(request, pk):
    """Add or remove a reaction to a message."""
    user = request.user
    message = get_object_or_404(Message, pk=pk)
    emoji = request.POST.get('emoji', '👍')
    
    # Check if reaction already exists
    reaction, created = MessageReaction.objects.get_or_create(
        message=message,
        user=user,
        emoji=emoji
    )
    
    if not created:
        # Remove reaction if it already exists
        reaction.delete()
        action = 'removed'
    else:
        action = 'added'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Return JSON for AJAX requests
        return JsonResponse({
            'success': True,
            'action': action,
            'reaction_summary': message.reaction_summary
        })
    
    return redirect('chat_channels:channel_detail', pk=message.channel.pk)
