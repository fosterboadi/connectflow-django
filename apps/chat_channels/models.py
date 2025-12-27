from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid
from cloudinary.models import CloudinaryField

User = get_user_model()


class Channel(models.Model):
    """
    Channel model - represents communication channels.
    Different types: Official, Department, Team, Project, Private, Direct
    """
    
    class ChannelType(models.TextChoices):
        OFFICIAL = 'OFFICIAL', _('Official Announcement')
        DEPARTMENT = 'DEPARTMENT', _('Department Channel')
        TEAM = 'TEAM', _('Team Channel')
        PROJECT = 'PROJECT', _('Project Channel')
        PRIVATE = 'PRIVATE', _('Private Group')
        DIRECT = 'DIRECT', _('Direct Message')
        BREAKOUT = 'BREAKOUT', _('Breakout Room')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text=_("Channel name")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Channel description")
    )
    
    channel_type = models.CharField(
        max_length=20,
        choices=ChannelType.choices,
        default=ChannelType.TEAM,
        help_text=_("Type of channel")
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='channels',
        help_text=_("Organization this channel belongs to")
    )
    
    # Related entities (optional - depends on channel type)
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        related_name='channels',
        null=True,
        blank=True,
        help_text=_("Department (for department channels)")
    )
    
    team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.CASCADE,
        related_name='channels',
        null=True,
        blank=True,
        help_text=_("Team (for team channels)")
    )
    
    parent_channel = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='breakout_rooms',
        help_text=_("Parent channel for breakout rooms")
    )
    
    shared_project = models.ForeignKey(
        'organizations.SharedProject',
        on_delete=models.CASCADE,
        related_name='channels',
        null=True,
        blank=True,
        help_text=_("Shared project this channel belongs to")
    )
    
    # Channel ownership and membership
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_channels',
        help_text=_("User who created this channel")
    )
    
    members = models.ManyToManyField(
        User,
        related_name='channels',
        blank=True,
        help_text=_("Channel members")
    )
    
    # Channel settings
    is_private = models.BooleanField(
        default=False,
        help_text=_("Is this a private channel?")
    )
    
    is_archived = models.BooleanField(
        default=False,
        help_text=_("Is this channel archived?")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Is this breakout room active?")
    )
    
    read_only = models.BooleanField(
        default=False,
        help_text=_("Is this channel read-only? (only admins can post)")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'channels'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ['-created_at']
        unique_together = [['organization', 'name']]
    
    def __str__(self):
        return f"#{self.name} ({self.get_channel_type_display()})"
    
    @property
    def member_count(self):
        """Return number of members in this channel."""
        return self.members.count()
    
    def can_user_post(self, user):
        """Check if user can post in this channel."""
        if self.read_only:
            # Only super admins and channel creator can post in read-only channels
            return user.is_admin or self.created_by == user
        
        # In Shared Projects, all project members can usually post unless restricted
        if self.shared_project:
            return user in self.shared_project.members.all()
            
        return user in self.members.all()
    
    def can_user_view(self, user):
        """Check if user can view this channel."""
        # If it's a shared project channel, only project members can view
        if self.shared_project:
            return user in self.shared_project.members.all()

        # Super admins can view everything in their organization
        if user.is_admin and user.organization == self.organization:
            return True
        
        # Official channels - everyone in org can view
        if self.channel_type == self.ChannelType.OFFICIAL:
            return user.organization == self.organization
        
        # Department channels - department members can view
        if self.channel_type == self.ChannelType.DEPARTMENT and self.department:
            return user in self.department.teams.all().values_list('members', flat=True)
        
        # Team channels - team members can view
        if self.channel_type == self.ChannelType.TEAM and self.team:
            return user in self.team.members.all()
        
        # Private/Project/Direct/Breakout - only members can view
        return user in self.members.all()


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Message(models.Model):
    """
    Message model - represents messages in channels.
    Supports text, files, mentions, reactions, and threading.
    """
    
    # Managers
    objects = MessageManager()
    all_objects = models.Manager() # Default manager to access everything
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text=_("Channel this message belongs to")
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text=_("User who sent this message")
    )
    
    content = models.TextField(
        blank=True,
        default='',
        help_text=_("Message content")
    )
    
    # Threading support
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text=_("Parent message if this is a reply")
    )
    
    # Voice message
    voice_message = CloudinaryField(
        'voice_message',
        folder='messages/voice',
        resource_type='auto',
        null=True,
        blank=True,
        help_text=_("Voice message audio file")
    )
    
    voice_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Duration of voice message in seconds")
    )
    
    # Message status
    is_edited = models.BooleanField(
        default=False,
        help_text=_("Has this message been edited?")
    )

    is_pinned = models.BooleanField(
        default=False,
        help_text=_("Is this message pinned?")
    )

    starred_by = models.ManyToManyField(
        User,
        related_name='starred_messages',
        blank=True,
        help_text=_("Users who starred this message")
    )

    forwarded_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forwards',
        help_text=_("Original message if this was forwarded")
    )
    
    is_deleted = models.BooleanField(
        default=False,
        help_text=_("Is this message deleted?")
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the message was deleted")
    )

    deleted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_messages',
        help_text=_("User who deleted this message")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-is_pinned', 'created_at']
        indexes = [
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} in #{self.channel.name}: {self.content[:50]}"
    
    def delete(self, user=None, force=False, *args, **kwargs):
        """Soft delete by default, unless force=True."""
        if force:
            super().delete(*args, **kwargs)
        else:
            from django.utils import timezone
            self.is_deleted = True
            self.deleted_at = timezone.now()
            if user:
                self.deleted_by = user
            self.save()
    
    @property
    def reply_count(self):
        """Return number of replies to this message."""
        return self.replies.count()
    
    @property
    def reaction_summary(self):
        """Return summary of reactions."""
        reactions = self.reactions.values('emoji').annotate(count=models.Count('id'))
        return {r['emoji']: r['count'] for r in reactions}


class Attachment(models.Model):
    """
    Attachment model - represents files attached to messages.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    message = models.ForeignKey(
        Message,
        related_name='attachments',
        on_delete=models.CASCADE,
        help_text=_("Message this attachment belongs to")
    )
    file = CloudinaryField(
        'file',
        folder='messages/attachments',
        resource_type='auto',
        help_text=_("Attached file")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'message_attachments'
        verbose_name = _('Message Attachment')
        verbose_name_plural = _('Message Attachments')
        ordering = ['uploaded_at']

    def __str__(self):
        return f"Attachment for Message ID: {self.message.id}"
        
    @property
    def is_image(self):
        """Check if file is an image."""
        try:
            if hasattr(self.file, 'resource_type'):
                return self.file.resource_type == 'image'
        except Exception:  # nosec
            pass
        
        extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg')
        name = str(self.file).lower()
        if name.endswith(extensions):
            return True
        try:
            return self.file.url.lower().split('?')[0].endswith(extensions)
        except Exception:  # nosec
            return False
    
    @property
    def is_video(self):
        """Check if file is a video."""
        try:
            if hasattr(self.file, 'resource_type'):
                return self.file.resource_type == 'video'
        except Exception:  # nosec
            pass

        extensions = ('.mp4', '.mov', '.webm', '.avi', '.mkv')
        name = str(self.file).lower()
        if name.endswith(extensions):
            return True
        try:
            return self.file.url.lower().split('?')[0].endswith(extensions)
        except Exception:  # nosec
            return False



class MessageReaction(models.Model):
    """
    MessageReaction model - represents emoji reactions to messages.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions',
        help_text=_("Message being reacted to")
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_reactions',
        help_text=_("User who reacted")
    )
    
    emoji = models.CharField(
        max_length=10,
        help_text=_("Emoji reaction (e.g., 👍, ❤️, 😊)")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reactions'
        verbose_name = _('Message Reaction')
        verbose_name_plural = _('Message Reactions')
        unique_together = [['message', 'user', 'emoji']]
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} to message"


class MessageReadReceipt(models.Model):
    """
    MessageReadReceipt model - tracks when users read messages.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts',
        help_text=_("Message that was read")
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='read_messages',
        help_text=_("User who read the message")
    )
    
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_receipts'
        verbose_name = _('Message Read Receipt')
        verbose_name_plural = _('Message Read Receipts')
        unique_together = [['message', 'user']]
        ordering = ['read_at']
    
    def __str__(self):
        return f"{self.user.username} read message at {self.read_at}"


# SIGNALS (Placed at the bottom to avoid NameErrors)
from django.db.models.signals import m2m_changed, post_delete
from django.dispatch import receiver
from django.urls import reverse
import cloudinary.uploader

@receiver(post_delete, sender=Message)
def delete_message_voice_from_cloudinary(sender, instance, **kwargs):
    if instance.voice_message:
        try:
            cloudinary.uploader.destroy(instance.voice_message.public_id)
        except Exception as e:
            try:
                cloudinary.uploader.destroy(instance.voice_message.name)
            except:
                print(f"Cloudinary deletion error: {e}")

@receiver(post_delete, sender=Attachment)
def delete_attachment_from_cloudinary(sender, instance, **kwargs):
    if instance.file:
        try:
            cloudinary.uploader.destroy(instance.file.public_id)
        except Exception as e:
            print(f"Cloudinary deletion error: {e}")

@receiver(m2m_changed, sender=Channel.members.through)
def notify_members_added_to_channel(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        from apps.accounts.models import Notification, User
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        
        channel_layer = get_channel_layer()
        
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                if user == instance.created_by:
                    continue
                
                link = reverse('chat_channels:channel_detail', kwargs={'pk': instance.pk})
                notification = Notification.notify(
                    recipient=user,
                    sender=instance.created_by,
                    title=f"New Channel: #{instance.name}",
                    content=f"You have been added to the channel #{instance.name}.",
                    notification_type='CHANNEL',
                    link=link
                )
                
                # Broadcast via WebSocket
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{user.id}",
                    {
                        'type': 'send_notification',
                        'id': str(notification.id),
                        'title': notification.title,
                        'content': notification.content,
                        'notification_type': notification.notification_type,
                        'link': notification.link,
                    }
                )
            except Exception as e:
                print(f"Error sending notification: {e}")