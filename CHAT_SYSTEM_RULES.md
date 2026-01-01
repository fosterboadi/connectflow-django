# ConnectFlow Chat System Rules & Guidelines

## Overview

ConnectFlow Pro implements a sophisticated chat system with intelligent message grouping, real-time communication, and multi-organizational support. This document outlines all the chat rules, behaviors, and guidelines.

---

## 📋 Table of Contents

1. [Channel Types & Access Rules](#channel-types--access-rules)
2. [Message Types & Formats](#message-types--formats)
3. [Message Grouping Rules](#message-grouping-rules)
4. [Permission Rules](#permission-rules)
5. [Message Status Flow](#message-status-flow)
6. [Special Message Behaviors](#special-message-behaviors)
7. [WebSocket Communication Rules](#websocket-communication-rules)
8. [File Upload Rules](#file-upload-rules)
9. [Emoji Detection Rules](#emoji-detection-rules)
10. [Deletion & Edit Rules](#deletion--edit-rules)

---

## 🏷️ Channel Types & Access Rules

### 1. **OFFICIAL** - Official Announcements
**Access**: All users in the organization  
**Post Permissions**: Admins and channel creator only (typically read-only)  
**Use Case**: Company-wide announcements, policy updates

### 2. **DEPARTMENT** - Department Channels
**Access**: All members of teams within the department  
**Post Permissions**: Department members  
**Use Case**: Department-wide communication

### 3. **TEAM** - Team Channels
**Access**: Team members only  
**Post Permissions**: Team members  
**Use Case**: Team collaboration and discussions

### 4. **PROJECT** - Project Channels
**Access**: Project members only (cross-organizational)  
**Post Permissions**: Project members  
**Use Case**: Project-specific communication for shared projects

### 5. **PRIVATE** - Private Group Channels
**Access**: Invited members only  
**Post Permissions**: Group members  
**Use Case**: Private discussions, special interest groups

### 6. **DIRECT** - Direct Messages
**Access**: The two participants only  
**Post Permissions**: Both participants  
**Use Case**: One-on-one conversations

### 7. **BREAKOUT** - Breakout Rooms
**Access**: Invited members from parent channel  
**Post Permissions**: Breakout room members  
**Use Case**: Temporary focused discussions  
**Special**: Auto-linked to parent channel

---

## 💬 Message Types & Formats

### Message Type Enum

| Type | Code | Description | Display Behavior |
|------|------|-------------|------------------|
| **TEXT** | `TEXT` | Standard text message | Normal bubble with text |
| **EMOJI** | `EMOJI` | Pure emoji message (≤3 emojis) | Large emoji display (4rem) |
| **VOICE** | `VOICE` | Voice note/recording | Waveform player with play button |
| **IMAGE** | `IMAGE` | Image attachment | Thumbnail with lightbox |
| **VIDEO** | `VIDEO` | Video attachment | Video player embed |
| **FILE** | `FILE` | File attachment | File icon + download link |
| **SYSTEM** | `SYSTEM` | System-generated notice | Centered gray pill badge |

### Message Detection Logic

```python
# Emoji-Only Detection (auto-classified as EMOJI type)
- Contains ONLY emojis (no text)
- Up to 3 emojis → Display at 4rem (large)
- More than 3 emojis → Display at 2rem (medium)

# Text Detection (default)
- Any text with or without emojis
- Standard bubble styling
```

---

## 🔗 Message Grouping Rules

### Grouping Logic (Slack/WhatsApp-style)

Messages are **grouped** when ALL conditions are met:

1. ✅ **Same Sender**: Current message and previous message from same user
2. ✅ **Time Threshold**: Less than **5 minutes** apart
3. ✅ **Sequential**: No other user's message in between

### Grouped Message Behavior

When messages are grouped:
- ❌ **Avatar**: Hidden (invisible, not removed)
- ❌ **Sender Name**: Hidden
- ❌ **Timestamp**: Hidden
- ✅ **Reduced Top Margin**: `-1.25rem` to tighten spacing

### Visual Example

```
┌─────────────────────────────────────┐
│ 👤 John Doe              9:30 AM   │ ← First message (full display)
│ Hey team, quick update...          │
│                                     │
│ The project is going well          │ ← Grouped (no avatar/name)
│                                     │
│ Should be done by Friday           │ ← Grouped (no avatar/name)
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│              9:35 AM     Jane Smith │ ← New sender (full display)
│                   Thanks for update │
└─────────────────────────────────────┘
```

### Breaking Grouping

Grouping breaks when:
- ⏰ **More than 5 minutes** between messages
- 👤 **Different sender** posts
- 📌 **System message** appears
- 🔄 **Page reload** (grouping recalculated)

---

## 🔒 Permission Rules

### View Permissions

```python
def can_user_view(user, channel):
    # Super admins can view all org channels
    if user.is_admin and user.organization == channel.organization:
        return True
    
    # Official channels - all org members
    if channel.type == OFFICIAL:
        return user.organization == channel.organization
    
    # Department channels - department members
    if channel.type == DEPARTMENT:
        return user in channel.department.all_members
    
    # Team channels - team members
    if channel.type == TEAM:
        return user in channel.team.members
    
    # Project channels - project members (cross-org)
    if channel.type == PROJECT:
        return user in channel.shared_project.members
    
    # Private/Direct/Breakout - explicit members only
    return user in channel.members.all()
```

### Post Permissions

```python
def can_user_post(user, channel):
    # Read-only channels (official announcements)
    if channel.read_only:
        return user.is_admin or user == channel.created_by
    
    # Shared project channels
    if channel.shared_project:
        return user in channel.shared_project.members.all()
    
    # All other channels
    return user in channel.members.all()
```

### Management Permissions

| Action | Required Permission |
|--------|-------------------|
| **Create Channel** | Admin or Manager |
| **Edit Channel** | Admin or Creator |
| **Delete Channel** | Admin or Creator |
| **Add Members** | Admin, Creator, or Manager |
| **Remove Members** | Admin or Creator |
| **Pin Messages** | Any member |
| **Delete Own Message** | Message sender |
| **Delete Any Message** | Admin |
| **Create Breakout** | Channel member |

---

## 📊 Message Status Flow

### Status Lifecycle

```
SENDING → SENT → DELIVERED → READ
           ↓
        FAILED (on error)
```

### Status Definitions

| Status | Code | Description | Visible to |
|--------|------|-------------|------------|
| **SENDING** | `SENDING` | Message being transmitted | Sender only |
| **SENT** | `SENT` | Received by server | Sender only |
| **DELIVERED** | `DELIVERED` | Delivered to recipients | Sender only |
| **READ** | `READ` | Read by recipients | Sender only |
| **FAILED** | `FAILED` | Delivery failed | Sender only |

### Status Display

- Shown as small uppercase text below message
- Only visible to sender
- Format: `SENT`, `DELIVERED`, `READ`, etc.
- Hidden for deleted messages

---

## ✨ Special Message Behaviors

### 1. Reply Threading

**Rule**: Messages can reply to other messages

**Behavior**:
- Parent message shown as preview (indented blue bar)
- Click parent preview to jump to original message
- Preserves context in long conversations

**Visual**:
```
┌────────────────────────────────────┐
│ ┃ Original Message                │ ← Parent preview
│ ┃ This is the original...         │
│                                    │
│ This is my reply                   │ ← Actual message
└────────────────────────────────────┘
```

### 2. Message Reactions

**Rule**: Users can react with emojis to any message

**Behavior**:
- Reactions grouped and counted
- Displayed below message
- Multiple reactions allowed per user

**Example**: 
```
👍 3   ❤️ 5   😂 2
```

### 3. Voice Messages

**Rule**: Voice notes auto-transcribed and playable

**Behavior**:
- Waveform visualization
- Duration display
- Play/pause controls
- Audio stored in Cloudinary

### 4. Pinned Messages

**Rule**: Important messages can be pinned

**Behavior**:
- Pin icon shown on message
- Highlighted background (indigo tint)
- Accessible from sidebar
- Multiple pins allowed

### 5. System Notices

**Rule**: Auto-generated for system events

**Behavior**:
- Centered in chat
- Gray pill badge
- Uppercase text
- Non-deletable

**Triggers**:
- User joins channel
- Channel created
- Settings changed
- Breakout room started

---

## 🌐 WebSocket Communication Rules

### Message Broadcasting

**Rule**: Real-time updates via Django Channels

```javascript
// Message sent via WebSocket
{
    type: 'chat_message',
    message_id: 'uuid',
    message_type: 'TEXT',
    sender_id: 123,
    sender_name: 'John Doe',
    sender_avatar: 'url',
    message: 'Hello',
    timestamp: 'Jan 1, 10:30 AM',
    status: 'SENT'
}
```

### Validation Rules

1. ✅ **JSON Parsing**: Must be valid JSON
2. ✅ **Non-Empty**: Message, voice, or attachment required
3. ✅ **Type Check**: Valid message_type enum
4. ✅ **Authentication**: Valid user session
5. ✅ **Channel Access**: User must be member

### Error Handling

```javascript
// Invalid message format
{
    type: 'error',
    message: 'Invalid message format'
}

// Empty message
{
    type: 'error',
    message: 'Message cannot be empty'
}
```

---

## 📎 File Upload Rules

### File Size Limits

| File Type | Max Size | Format |
|-----------|----------|--------|
| **Images** | 10 MB | JPG, PNG, GIF, WebP, SVG |
| **Voice** | 10 MB | WebM, MP3, WAV |
| **Videos** | 50 MB | MP4, WebM, MOV |
| **Documents** | 10 MB | PDF, DOC, XLS, TXT, etc. |

### Storage Rules

- ✅ **Storage Provider**: Cloudinary
- ✅ **Organization Quota**: Checked before upload
- ✅ **Path Structure**: `{org_id}/channels/{channel_id}/{filename}`
- ✅ **Secure URLs**: HTTPS only
- ✅ **CDN**: Auto-optimized delivery

### Upload Behavior

```javascript
// Multi-file upload allowed
- Drag & drop support
- File preview before send
- Progress indicator
- Thumbnail generation (images)
- Metadata extraction
```

---

## 😀 Emoji Detection Rules

### Emoji-Only Classification

**Rule**: Messages with ONLY emojis get special treatment

**Detection Logic**:
```python
# Step 1: Remove all whitespace
text = text.strip()

# Step 2: Remove all emojis using Unicode ranges
text_without_emojis = remove_emojis(text)

# Step 3: Check if anything remains
if has_emojis(text) and len(text_without_emojis) == 0:
    message_type = EMOJI
```

### Emoji Sizing

| Emoji Count | Font Size | Use Case |
|-------------|-----------|----------|
| **1-3** | 4rem (64px) | Large display (WhatsApp style) |
| **4+** | 2rem (32px) | Medium display |
| **With text** | Inline | Normal text flow |

### Unicode Ranges Supported

```python
Emoticons: U+1F600 to U+1F64F
Symbols: U+1F300 to U+1F5FF
Transport: U+1F680 to U+1F6FF
Flags: U+1F1E0 to U+1F1FF
Dingbats: U+2702 to U+27B0
Extended: U+1F900 to U+1F9FF
Miscellaneous: U+2600 to U+26FF
```

---

## 🗑️ Deletion & Edit Rules

### Soft Delete

**Rule**: Messages are soft-deleted (marked as deleted, not removed)

**Behavior**:
```python
message.is_deleted = True
message.content = ""  # Cleared for privacy
message.save()
```

**Display**:
```
┌────────────────────────────────┐
│ 🗑️ This message was deleted.  │
│    (italic, grayed out)        │
└────────────────────────────────┘
```

### Who Can Delete

| Message Type | Can Delete |
|--------------|-----------|
| **Own Message** | Message sender |
| **Any Message** | Organization admins |
| **System Message** | Nobody (permanent) |

### Delete Restrictions

- ❌ Cannot restore deleted messages
- ❌ Reactions remain (but hidden)
- ❌ Replies still show as "[deleted]"
- ✅ Attachments removed from storage

### Edit Rules

**Current Status**: ❌ **NOT IMPLEMENTED**

**Planned Behavior**:
- Only text messages editable
- 15-minute edit window
- "Edited" indicator shown
- Edit history trackable

---

## 🎯 Context Menu Actions

### Available Actions

| Action | Icon | Description | Permission |
|--------|------|-------------|------------|
| **Reply** | ↩️ | Reply to message | All members |
| **React** | 😀 | Add emoji reaction | All members |
| **Copy Text** | 📋 | Copy to clipboard | All members |
| **Forward** | ➡️ | Forward to another channel | All members |
| **Pin** | 📌 | Pin/unpin message | All members |
| **Star** | ⭐ | Bookmark message | All members |
| **Create Task** | ✅ | Convert to project task | Project members |
| **Delete** | 🗑️ | Delete message | Sender or Admin |

---

## 🔔 Notification Rules

### When Notifications Trigger

1. ✅ **@Mention**: User specifically mentioned
2. ✅ **Direct Message**: New DM received
3. ✅ **Reply**: Someone replies to your message
4. ✅ **Channel Announcement**: Official channel post

### Notification Preferences

Users can toggle:
- Email notifications (ON/OFF)
- Mention notifications (ON/OFF)
- Desktop push notifications (browser-dependent)

---

## 🚫 Rate Limiting & Spam Prevention

### Current Rules

**Message Sending**:
- ❌ No hard rate limit (to be implemented)
- ✅ Validation on every message
- ✅ Duplicate detection (5-second window)

### Recommended Limits (To Implement)

```python
# Per user per channel
- 10 messages per minute
- 100 messages per hour
- 1000 messages per day

# File uploads
- 5 files per minute
- 50 MB total per 10 minutes
```

---

## 📱 Mobile & Responsive Rules

### Breakpoints

| Device | Width | Behavior |
|--------|-------|----------|
| **Desktop** | ≥1024px | 3-panel layout (sidebar, chat, context) |
| **Tablet** | 768-1023px | 2-panel layout (chat, collapsible sidebar) |
| **Mobile** | <768px | 1-panel layout (chat only, drawer menu) |

### Mobile-Specific Rules

- Sidebar collapses to hamburger menu
- Context panel hidden (swipe to reveal)
- Voice recording with mobile API
- File upload via camera/gallery
- Touch-optimized reactions

---

## 🔐 Security Rules

### Message Encryption

**Current**: ❌ End-to-end encryption NOT implemented  
**Transport**: ✅ HTTPS/WSS only  
**Storage**: ✅ Database encrypted at rest

### Data Privacy

1. ✅ **Organization Isolation**: Messages never cross organizations (except shared projects)
2. ✅ **Channel Isolation**: Messages only visible to channel members
3. ✅ **Deleted Content**: Cleared from database
4. ✅ **File Access**: Cloudinary URLs with signed tokens

---

## 📊 Performance Rules

### Message Loading

**Pagination**: 50 messages per page  
**Lazy Loading**: Scroll up to load more  
**Cache**: Template cache disabled in production (bust on updates)

### Optimization

```python
# Database queries optimized
- select_related() for user/sender
- prefetch_related() for reactions
- Indexed fields: sender, channel, created_at, status, message_type
```

---

## 🎨 UI/UX Rules

### Color Coding

| Element | Color | Purpose |
|---------|-------|---------|
| **Own Messages** | Indigo (bg-indigo-600) | Visual distinction |
| **Other Messages** | Gray (bg-gray-100) | Default state |
| **System Notices** | Gray pill | Non-interactive |
| **Pinned Messages** | Indigo tint border | Highlight important |
| **Online Status** | Green dot | Presence indicator |
| **Typing Indicator** | Animated dots | Real-time feedback |

### Accessibility

- ✅ **Keyboard Navigation**: Tab through messages
- ✅ **Screen Readers**: ARIA labels on actions
- ✅ **High Contrast**: Dark mode support
- ✅ **Font Scaling**: Respects browser zoom

---

## 🧪 Testing & Validation

### Message Validation Tests

```python
# Required tests
1. Empty message rejection
2. Max length enforcement (10,000 chars)
3. File size validation
4. Emoji-only detection
5. XSS prevention (auto-escaped)
6. SQL injection prevention (ORM)
```

### WebSocket Tests

```python
# Connection tests
1. Authentication required
2. Organization isolation
3. Reconnection handling
4. Message ordering
5. Delivery confirmation
```

---

## 📚 API Reference

### Send Message

```python
POST /channels/{channel_id}/messages/

{
    "message": "Hello world",
    "message_type": "TEXT",
    "parent_message_id": "uuid"  # Optional for replies
}
```

### React to Message

```python
POST /channels/messages/{message_id}/react/

{
    "emoji": "👍"
}
```

### Delete Message

```python
POST /channels/messages/{message_id}/delete/
```

---

## 🎯 Future Enhancements

### Planned Features

1. ⏳ **Message Editing** (15-minute window)
2. ⏳ **Read Receipts** (privacy-aware)
3. ⏳ **Typing Indicators** (real-time)
4. ⏳ **Search in Messages** (full-text search)
5. ⏳ **Message Scheduling** (send later)
6. ⏳ **Rich Text Formatting** (bold, italic, code blocks)
7. ⏳ **Thread Conversations** (nested replies)
8. ⏳ **Voice Transcription** (speech-to-text)
9. ⏳ **Video Calls** (WebRTC integration)
10. ⏳ **Screen Sharing** (collaboration)

---

## 📞 Support & Troubleshooting

### Common Issues

**Messages not sending?**
- Check WebSocket connection (green dot in UI)
- Verify channel permissions
- Check storage quota

**Messages not grouping?**
- Ensure < 5 minutes apart
- Same sender required
- Page refresh resets grouping

**Files not uploading?**
- Check file size (max 10MB)
- Verify organization storage quota
- Cloudinary credentials configured?

---

## 📝 Changelog

### Version 1.0.0 (January 2026)
- ✅ Real-time WebSocket messaging
- ✅ Message grouping (5-minute window)
- ✅ Emoji-only detection and large display
- ✅ Voice message support with waveform
- ✅ File attachments (images, documents)
- ✅ Message reactions
- ✅ Reply threading
- ✅ Pin messages
- ✅ Soft delete
- ✅ Multi-channel types
- ✅ Organization isolation
- ✅ Shared project channels
- ✅ Breakout rooms

---

## 👤 Author

**Foster Boadi**  
ConnectFlow Pro Development Team  
**Last Updated**: January 1, 2026  
**Version**: 1.0.0

---

**For technical implementation details, see**:
- `apps/chat_channels/models.py` - Data models
- `apps/chat_channels/consumers.py` - WebSocket handlers
- `apps/chat_channels/views.py` - HTTP views
- `templates/chat_channels/channel_detail.html` - Frontend UI
- `apps/chat_channels/templatetags/chat_filters.py` - Template filters

**Questions?** Contact: support@connectflow.pro
