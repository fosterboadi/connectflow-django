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
    
    # Get messages (excluding replies - they'll be shown with parent)
    from django.db.models import Prefetch
    messages_query = Message.all_objects.filter(
        channel=channel,
        parent_message__isnull=True
    ).select_related('sender').prefetch_related(
        'reactions',
        Prefetch('replies', queryset=Message.all_objects.filter(is_deleted=False).select_related('sender')),
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
            message.sender = user
            
            # Handle parent message for threading
            parent_id = request.POST.get('parent_message')
            if parent_id:
                try:
                    message.parent_message = Message.objects.get(id=parent_id)
                except Message.DoesNotExist:
                    pass
            if message.voice_message and not message.content.strip():
                message.content = ''  # Empty string for voice-only messages
            
            # Save the message first
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
                # If attachment upload fails, permanently delete the orphan message
                message.delete(force=True) 
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': f'Upload failed: {str(e)}'}, status=500)
                messages.error(request, f'Failed to upload attachments: {e}')
                return redirect('chat_channels:channel_detail', pk=pk)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message_id': str(message.id),
                    'content': message.content,
                    'sender_name': user.get_full_name(),
                    'sender_avatar': user.avatar.url if user.avatar else None,
                    'timestamp': message.created_at.strftime('%b %d, %I:%M %p'),
                    'voice_message_url': message.voice_message.url if message.voice_message else None,
                    'voice_duration': message.voice_duration,
                    'attachments': processed_attachments
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
        'messages': channel_messages,
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
    
    new_content = request.POST.get('content')
    if not new_content:
        return JsonResponse({'success': False, 'error': 'Content cannot be empty.'}, status=400)
    
    message.content = new_content
    message.is_edited = True
    message.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'content': message.content,
            'message_id': str(message.id)
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
