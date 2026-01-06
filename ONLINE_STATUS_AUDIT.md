# Online Status System - Comprehensive Audit Report

**Date:** 2026-01-03  
**System:** ConnectFlow Pro  
**Status:** ⚠️ PARTIALLY IMPLEMENTED - Needs Fixes

---

## 🔍 Current Implementation Analysis

### ✅ What's Working

#### 1. **Database Model** (GOOD)
**File:** `apps/accounts/models.py`

```python
class User(AbstractUser):
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OFFLINE,  # ✅ Defaults to OFFLINE
        help_text=_("Current online status")
    )
    
    last_seen = models.DateTimeField(
        auto_now=True,  # ✅ Auto-updates on every save
        help_text=_("Last activity timestamp")
    )
```

**Status Options:**
- `ONLINE` - User is actively connected
- `OFFLINE` - User is disconnected
- `AWAY` - User is idle
- `BUSY` - User set manual status

#### 2. **WebSocket Status Updates** (GOOD)
**File:** `apps/chat_channels/consumers.py`

```python
async def connect(self):
    # Update user status to ONLINE
    await self.update_user_status('ONLINE')  # ✅ Sets ONLINE on connect
    
    # Broadcast presence
    await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'user_status_change',
            'user_id': self.user.id,
            'status': 'ONLINE'
        }
    )

async def disconnect(self, close_code):
    # Update user status to OFFLINE
    await self.update_user_status('OFFLINE')  # ✅ Sets OFFLINE on disconnect
    
    # Broadcast presence
    await self.channel_layer.group_send(...)

@database_sync_to_async
def update_user_status(self, status):
    User.objects.filter(id=self.user.id).update(
        status=status, 
        last_seen=timezone.now()  # ✅ Updates last_seen timestamp
    )
```

#### 3. **Frontend Real-Time Updates** (GOOD)
**File:** `templates/chat_channels/channel_detail.html`

```javascript
function handlePresence(data) {
    const statusDots = document.querySelectorAll(`[data-user-id="${data.user_id}"] .status-dot`);
    statusDots.forEach(dot => {
        // ✅ Updates status indicator in real-time
        dot.className = `... ${data.status === 'ONLINE' ? 'bg-green-500' : 'bg-gray-300'}`;
    });
}
```

#### 4. **Visual Status Indicators** (GOOD)
Multiple templates show online status:
- `channel_detail.html` - Green dot for online members
- `channel_list.html` - Status in member list
- `member_directory.html` - Shows "Last seen" time
- `profile_detail.html` - Profile page status

---

## ❌ Critical Issues Found

### Issue #1: **No Global Presence Tracking** ⚠️ HIGH PRIORITY

**Problem:**
- Status ONLY updates when users connect/disconnect from **chat channels**
- Status is NOT updated during regular browsing (dashboard, projects, etc.)
- Users appear OFFLINE even when actively using the platform

**Impact:**
```
User Journey:
1. User logs in → Status: OFFLINE ❌
2. User browses dashboard → Status: OFFLINE ❌
3. User opens a chat channel → Status: ONLINE ✅
4. User closes chat, browses projects → Status: OFFLINE ❌
5. User logs out → Status: OFFLINE ✅
```

**Root Cause:**
- No global WebSocket connection for presence
- Only `ChatConsumer` updates status
- No middleware tracking user activity

---

### Issue #2: **Login/Logout Don't Set Status** ⚠️ HIGH PRIORITY

**Problem:**
Login and logout views don't update user status.

**File:** `apps/accounts/views.py`

```python
class LoginView(View):
    def post(self, request):
        user = authenticate(request, id_token=id_token)
        if user:
            login(request, user)  # ❌ No status update
            return JsonResponse({'status': 'ok'})

class LogoutView(View):
    def get(self, request):
        logout(request)  # ❌ No status update
        return redirect('accounts:login')
```

**Expected Behavior:**
```python
# On Login:
user.status = User.Status.ONLINE
user.last_seen = timezone.now()
user.save()

# On Logout:
user.status = User.Status.OFFLINE
user.last_seen = timezone.now()
user.save()
```

---

### Issue #3: **No Idle/Away Status** ⚠️ MEDIUM PRIORITY

**Problem:**
- No automatic transition to "AWAY" status when user is idle
- No inactivity detection

**Current Behavior:**
- User opens chat → ONLINE
- User doesn't interact for 30 minutes → Still ONLINE ❌
- User closes browser tab → OFFLINE ✅

**Expected Behavior:**
- Idle for 5 minutes → AWAY
- Idle for 30 minutes → OFFLINE
- Any activity → ONLINE

---

### Issue #4: **Status Not Broadcast Globally** ⚠️ MEDIUM PRIORITY

**Problem:**
Status changes only broadcast to the specific chat channel room group, not globally.

**Current:**
```python
# Only users in the SAME channel see status change
await self.channel_layer.group_send(
    self.room_group_name,  # ❌ Only specific channel
    {'type': 'user_status_change', ...}
)
```

**Expected:**
```python
# ALL users in the organization should see status change
await self.channel_layer.group_send(
    f'org_{user.organization_id}',  # ✅ Organization-wide
    {'type': 'user_status_change', ...}
)
```

---

### Issue #5: **Stale Status on Server Restart** ⚠️ LOW PRIORITY

**Problem:**
If server restarts while users are connected, their status remains "ONLINE" in database.

**Scenario:**
1. 10 users connected → Status: ONLINE
2. Server crashes/restarts
3. Users' status in DB still shows ONLINE ❌
4. New users see everyone as online when they're not

---

## ✅ Recommended Fixes

### Fix #1: Global Presence WebSocket ⭐ CRITICAL

**Create a global presence consumer:**

**File:** `apps/accounts/consumers.py` (Update)

```python
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class PresenceConsumer(AsyncWebsocketConsumer):
    """
    Global presence tracking - connects on login, persists across pages.
    """
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join organization-wide presence group
        self.org_group = f'presence_org_{self.user.organization_id}'
        await self.channel_layer.group_add(self.org_group, self.channel_name)
        
        # Set user ONLINE
        await self.set_status('ONLINE')
        
        # Broadcast to organization
        await self.channel_layer.group_send(
            self.org_group,
            {
                'type': 'user_status_update',
                'user_id': self.user.id,
                'status': 'ONLINE',
                'username': self.user.get_full_name()
            }
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'org_group'):
            # Set user OFFLINE
            await self.set_status('OFFLINE')
            
            # Broadcast to organization
            await self.channel_layer.group_send(
                self.org_group,
                {
                    'type': 'user_status_update',
                    'user_id': self.user.id,
                    'status': 'OFFLINE'
                }
            )
            
            await self.channel_layer.group_discard(self.org_group, self.channel_name)
    
    async def receive(self, text_data):
        """Handle heartbeat pings to keep connection alive."""
        import json
        data = json.loads(text_data)
        
        if data.get('type') == 'heartbeat':
            # Update last_seen on heartbeat
            await self.update_activity()
            await self.send(text_data=json.dumps({'type': 'pong'}))
    
    async def user_status_update(self, event):
        """Broadcast status changes to all connected clients."""
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'user_id': event['user_id'],
            'status': event['status']
        }))
    
    @database_sync_to_async
    def set_status(self, status):
        User.objects.filter(id=self.user.id).update(
            status=status,
            last_seen=timezone.now()
        )
    
    @database_sync_to_async
    def update_activity(self):
        User.objects.filter(id=self.user.id).update(last_seen=timezone.now())
```

**Update routing:**

**File:** `connectflow/routing.py`

```python
from django.urls import path
from apps.accounts.consumers import NotificationConsumer, PresenceConsumer
from apps.chat_channels.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/presence/', PresenceConsumer.as_asgi()),  # ← ADD THIS
    path('ws/chat/<uuid:channel_id>/', ChatConsumer.as_asgi()),
]
```

**Add to base template:**

**File:** `templates/base.html`

```html
<script>
    // Global presence WebSocket - stays connected across all pages
    let presenceSocket = null;
    
    function connectPresence() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        presenceSocket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/presence/`);
        
        presenceSocket.onopen = () => {
            console.log('✅ Presence connected');
            
            // Send heartbeat every 30 seconds
            setInterval(() => {
                if (presenceSocket.readyState === WebSocket.OPEN) {
                    presenceSocket.send(JSON.stringify({ type: 'heartbeat' }));
                }
            }, 30000);
        };
        
        presenceSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            
            if (data.type === 'presence') {
                // Update all status indicators on page
                updateUserStatus(data.user_id, data.status);
            }
        };
        
        presenceSocket.onclose = () => {
            console.log('❌ Presence disconnected - reconnecting...');
            setTimeout(connectPresence, 3000);
        };
    }
    
    function updateUserStatus(userId, status) {
        const dots = document.querySelectorAll(`[data-user-id="${userId}"] .status-dot`);
        dots.forEach(dot => {
            dot.className = dot.className.replace(/bg-(green|gray)-\d+/, 
                status === 'ONLINE' ? 'bg-green-500' : 'bg-gray-300');
        });
    }
    
    // Connect on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', connectPresence);
    } else {
        connectPresence();
    }
</script>
```

---

### Fix #2: Update Status on Login/Logout ⭐ CRITICAL

**File:** `apps/accounts/views.py`

```python
from django.utils import timezone

class LoginView(View):
    def post(self, request):
        # ... existing auth code ...
        
        if user:
            # Set user ONLINE on login
            user.status = User.Status.ONLINE
            user.last_seen = timezone.now()
            user.save(update_fields=['status', 'last_seen'])
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return JsonResponse({'status': 'ok'})

class LogoutView(View):
    def get(self, request):
        user = request.user
        
        # Set user OFFLINE on logout
        if user.is_authenticated:
            user.status = User.Status.OFFLINE
            user.last_seen = timezone.now()
            user.save(update_fields=['status', 'last_seen'])
        
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        return redirect('accounts:login')
```

**Also update API login/logout:**

**File:** `apps/accounts/api_views.py`

```python
from django.utils import timezone

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login(request):
    user = authenticate(request, username=email, password=password)
    
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=401)
    
    # Set ONLINE status
    user.status = User.Status.ONLINE
    user.last_seen = timezone.now()
    user.save(update_fields=['status', 'last_seen'])
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_logout(request):
    # Set OFFLINE status
    request.user.status = User.Status.OFFLINE
    request.user.last_seen = timezone.now()
    request.user.save(update_fields=['status', 'last_seen'])
    
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({'message': 'Logged out successfully'})
```

---

### Fix #3: Automatic Idle/Away Status ⭐ RECOMMENDED

**Add to PresenceConsumer:**

```python
class PresenceConsumer(AsyncWebsocketConsumer):
    # ... existing code ...
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        
        if data.get('type') == 'heartbeat':
            await self.update_activity()
            await self.send(text_data=json.dumps({'type': 'pong'}))
        
        elif data.get('type') == 'status_change':
            # Manual status change (BUSY, AWAY, ONLINE)
            new_status = data.get('status')
            if new_status in ['ONLINE', 'AWAY', 'BUSY']:
                await self.set_status(new_status)
                await self.channel_layer.group_send(
                    self.org_group,
                    {
                        'type': 'user_status_update',
                        'user_id': self.user.id,
                        'status': new_status
                    }
                )
```

**Frontend idle detection:**

```javascript
let idleTimeout, awayTimeout;
let currentStatus = 'ONLINE';

function resetIdleTimer() {
    clearTimeout(idleTimeout);
    clearTimeout(awayTimeout);
    
    if (currentStatus !== 'ONLINE') {
        setStatus('ONLINE');
    }
    
    // Set to AWAY after 5 minutes of inactivity
    idleTimeout = setTimeout(() => {
        setStatus('AWAY');
    }, 5 * 60 * 1000);
    
    // Set to OFFLINE after 30 minutes of inactivity
    awayTimeout = setTimeout(() => {
        setStatus('OFFLINE');
    }, 30 * 60 * 1000);
}

function setStatus(status) {
    currentStatus = status;
    if (presenceSocket && presenceSocket.readyState === WebSocket.OPEN) {
        presenceSocket.send(JSON.stringify({
            type: 'status_change',
            status: status
        }));
    }
}

// Detect user activity
['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, resetIdleTimer);
});

// Start idle timer on page load
resetIdleTimer();
```

---

### Fix #4: Cleanup Stale Online Status ⭐ OPTIONAL

**Management command to reset stale statuses:**

**File:** `apps/accounts/management/commands/cleanup_stale_status.py`

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User

class Command(BaseCommand):
    help = 'Reset status to OFFLINE for users who haven\'t been seen in 30+ minutes'

    def handle(self, *args, **options):
        cutoff_time = timezone.now() - timedelta(minutes=30)
        
        stale_users = User.objects.filter(
            status='ONLINE',
            last_seen__lt=cutoff_time
        )
        
        count = stale_users.update(status=User.Status.OFFLINE)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Reset {count} stale ONLINE statuses to OFFLINE')
        )
```

**Add to cron or periodic task:**
```bash
# Run every 10 minutes
*/10 * * * * python /path/to/manage.py cleanup_stale_status
```

---

## 📊 Implementation Priority

### Phase 1: CRITICAL (Do Now)
1. ✅ Add status updates to login/logout views
2. ✅ Create global PresenceConsumer
3. ✅ Add presence WebSocket to base template

### Phase 2: HIGH (This Week)
4. ✅ Implement idle/away detection
5. ✅ Organization-wide status broadcasting

### Phase 3: NICE-TO-HAVE (Later)
6. ✅ Stale status cleanup command
7. ✅ Manual status setting (Busy, Away)
8. ✅ "Last seen" relative time display

---

## 🧪 Testing Checklist

After implementing fixes:

- [ ] Login → Status shows ONLINE immediately
- [ ] Logout → Status shows OFFLINE immediately
- [ ] Open dashboard → Status stays ONLINE (without opening chat)
- [ ] Idle for 5+ min → Status changes to AWAY
- [ ] Resume activity → Status changes back to ONLINE
- [ ] Close browser → Status changes to OFFLINE
- [ ] Multiple tabs → Status persists across tabs
- [ ] Server restart → Stale statuses get cleaned up
- [ ] Other users see real-time status changes
- [ ] Status indicator updates without page refresh

---

## 📝 Summary

**Current State:** 🟡 Partially Working
- ✅ Status works when connected to chat channels
- ❌ Status doesn't work during general browsing
- ❌ Login/logout don't update status
- ❌ No idle detection
- ❌ No global presence tracking

**After Fixes:** 🟢 Fully Functional
- ✅ Real-time presence tracking everywhere
- ✅ Automatic status updates
- ✅ Idle/away detection
- ✅ Organization-wide broadcasting
- ✅ Persistent across page navigation

---

**Next Steps:** Implement Phase 1 fixes immediately for production deployment.
