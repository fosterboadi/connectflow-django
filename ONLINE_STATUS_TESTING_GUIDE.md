# Manual Testing Checklist for Online/Offline Status

Use this checklist to manually verify the online/offline status system works correctly.

---

## ✅ Pre-Test Setup

- [ ] Ensure Django server is running
- [ ] Ensure Redis is running (for WebSocket support)
- [ ] Have 2+ test user accounts ready
- [ ] Have 2 browsers or incognito windows open

---

## Test 1: Login Status Update

**Steps:**
1. Open browser console (F12)
2. Navigate to login page
3. Log in with test user

**Expected Results:**
- [ ] User status in database changes to `ONLINE`
- [ ] Console shows: "✅ Presence WebSocket connected"
- [ ] No console errors

**Verify:**
```bash
# Check in Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='testuser')
>>> print(user.status)  # Should show: ONLINE
```

---

## Test 2: Real-Time Status Display

**Steps:**
1. Login as User A in Browser 1
2. Login as User B in Browser 2
3. Navigate to Member Directory
4. Look for User A's profile picture

**Expected Results:**
- [ ] User A has green dot 🟢 next to avatar
- [ ] Status shows "Online"
- [ ] "Last seen" shows recent timestamp

**Pages to Check:**
- [ ] `/organizations/members/` - Member Directory
- [ ] `/chat/channels/` - Channel List
- [ ] `/accounts/profile/<id>/` - User Profile
- [ ] `/chat/channels/<id>/` - Channel Detail (member list)

---

## Test 3: Real-Time Status Updates (Multi-User)

**Steps:**
1. Browser 1: Login as User A, go to Member Directory
2. Browser 2: User B (already logged in) - observe
3. Browser 1: Logout User A

**Expected Results (in Browser 2):**
- [ ] User A's dot changes from green 🟢 to gray ⚪ (within 1-2 seconds)
- [ ] No page refresh needed
- [ ] Status text updates to "Offline"

**Reverse Test:**
1. Browser 1: Login as User A again
2. Browser 2: Observe User A's status

**Expected Results (in Browser 2):**
- [ ] User A's dot changes from gray ⚪ to green 🟢 (within 1-2 seconds)
- [ ] Status text updates to "Online"

---

## Test 4: Idle Detection (5 Minutes to AWAY)

**Steps:**
1. Login as test user
2. Go to Member Directory
3. **DO NOT** touch mouse/keyboard for 5 minutes
4. Watch your own status indicator (or have another user watch)

**Expected Results:**
- [ ] After 5 minutes of inactivity, dot changes to yellow 🟡
- [ ] Status changes to "Away"
- [ ] Console shows: "Status changed to: AWAY"

**Recovery Test:**
- [ ] Move mouse or press a key
- [ ] Dot changes back to green 🟢
- [ ] Status changes to "Online"

---

## Test 5: Extended Idle (30 Minutes to OFFLINE)

**Steps:**
1. Login as test user
2. **DO NOT** touch mouse/keyboard for 30 minutes
3. Watch status indicator

**Expected Results:**
- [ ] After 5 minutes: Status = AWAY 🟡
- [ ] After 30 minutes: Status = OFFLINE ⚪
- [ ] Console shows: "Status changed to: OFFLINE"

**Note:** You can temporarily reduce timeouts in `base.html` for faster testing:
```javascript
// Change from:
idleTimeout = setTimeout(() => setUserStatus('AWAY'), 5 * 60 * 1000);

// To (30 seconds for testing):
idleTimeout = setTimeout(() => setUserStatus('AWAY'), 30 * 1000);
```

---

## Test 6: Multi-Tab Behavior

**Steps:**
1. Login in Browser Tab 1
2. Open Tab 2 (same browser, same user)
3. Navigate to different pages in both tabs
4. Close Tab 1, keep Tab 2 open

**Expected Results:**
- [ ] Both tabs share same WebSocket connection
- [ ] Status remains ONLINE when any tab is active
- [ ] Activity in Tab 2 resets idle timer
- [ ] Closing one tab doesn't set status to OFFLINE
- [ ] Closing ALL tabs sets status to OFFLINE

---

## Test 7: Page Navigation (Persistence)

**Steps:**
1. Login as test user
2. Go to Dashboard (status should be ONLINE 🟢)
3. Navigate to Channel List
4. Navigate to Member Directory
5. Navigate to Profile Settings
6. Check console for WebSocket messages

**Expected Results:**
- [ ] WebSocket stays connected across page changes
- [ ] Console shows ongoing heartbeat messages every 30s
- [ ] No disconnection/reconnection on navigation
- [ ] Status remains ONLINE throughout

---

## Test 8: Logout Status Update

**Steps:**
1. Login as test user (status = ONLINE)
2. Click logout button
3. Check database or have another user verify

**Expected Results:**
- [ ] User status changes to OFFLINE immediately
- [ ] Other users see gray dot ⚪ in real-time
- [ ] Console shows WebSocket disconnect message

**Verify in Database:**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='testuser')
>>> print(user.status)  # Should show: OFFLINE
```

---

## Test 9: Stale Status Cleanup

**Steps:**
1. Manually set a user's status to ONLINE with old timestamp:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> User = get_user_model()
>>> user = User.objects.first()
>>> user.status = 'ONLINE'
>>> User.objects.filter(id=user.id).update(
...     status='ONLINE',
...     last_seen=timezone.now() - timedelta(minutes=35)
... )
>>> exit()
```

2. Run cleanup command:
```bash
python manage.py cleanup_stale_status
```

**Expected Results:**
- [ ] Command shows: "✓ Reset X stale ONLINE statuses to OFFLINE"
- [ ] User status is now OFFLINE in database
- [ ] Other users see gray dot if viewing that user

---

## Test 10: WebSocket Reconnection

**Steps:**
1. Login as test user
2. Open browser console
3. Check Network tab, find WebSocket connection
4. Close/disconnect WebSocket manually or restart Django server
5. Wait and observe console

**Expected Results:**
- [ ] Console shows: "❌ Presence disconnected - reconnecting in 3s..."
- [ ] After 3 seconds: "✅ Presence WebSocket connected"
- [ ] Status remains ONLINE (or returns to ONLINE)
- [ ] No manual intervention needed

---

## Test 11: Status Indicators in Different Areas

Visit each page and verify status indicator appears:

### Channel Detail Page
- [ ] Navigate to a channel with multiple members
- [ ] Each member shows status dot (green/yellow/gray/red)
- [ ] Dots update in real-time when users log in/out

### Channel List Page
- [ ] Navigate to `/chat/channels/`
- [ ] Channel preview shows member avatars
- [ ] Each avatar has status dot
- [ ] Dots match actual user status

### Member Directory
- [ ] Navigate to `/organizations/members/`
- [ ] Large status dot on each member's profile picture
- [ ] Green = Online, Yellow = Away, Gray = Offline
- [ ] "Last seen" timestamp displayed for offline users

### User Profile Page
- [ ] Navigate to a user's profile
- [ ] Status dot on profile avatar
- [ ] Status text displayed (Online/Offline/Away/Busy)
- [ ] Updates in real-time if user logs in/out

---

## Test 12: Console Debugging

**Steps:**
1. Login and open browser console
2. Look for presence-related messages

**Expected Console Output:**
```
Connecting to presence WebSocket: ws://localhost:8000/ws/presence/
✅ Presence WebSocket connected
```

**Every 30 seconds:**
```
(Heartbeat sent - no visible log, but network tab shows frames)
```

**When user activity detected:**
```
Status changed to: ONLINE
```

**When idle for 5 minutes:**
```
Status changed to: AWAY
```

**When idle for 30 minutes:**
```
Status changed to: OFFLINE
```

---

## 🐛 Common Issues & Solutions

### Issue: WebSocket won't connect
**Solution:**
- Check if Redis is running
- Verify Daphne/ASGI server is running
- Check for firewall blocking WebSocket ports

### Issue: Status doesn't update in real-time
**Solution:**
- Check browser console for errors
- Verify Channel Layer configuration in settings
- Ensure multiple users are in same organization

### Issue: Status stuck on ONLINE
**Solution:**
- Run: `python manage.py cleanup_stale_status`
- Check if WebSocket disconnected properly
- Verify logout view updates status

### Issue: Idle detection not working
**Solution:**
- Check browser console for JavaScript errors
- Verify `base.html` includes idle detection code
- Test with shorter timeouts (30s instead of 5min)

---

## ✅ Success Criteria

All tests should pass with these results:

- ✅ Login sets status to ONLINE
- ✅ Logout sets status to OFFLINE
- ✅ Idle for 5 min sets status to AWAY
- ✅ Idle for 30 min sets status to OFFLINE
- ✅ Activity brings user back to ONLINE
- ✅ Status updates in real-time across all users
- ✅ Status indicators shown in all key pages
- ✅ WebSocket reconnects automatically on disconnect
- ✅ Cleanup command resets stale statuses
- ✅ Multi-tab usage works correctly

---

## 📊 Visual Status Reference

| Status | Color | Dot | When |
|--------|-------|-----|------|
| ONLINE | Green 🟢 | `bg-green-500` | User is active |
| AWAY | Yellow 🟡 | `bg-yellow-500` | Idle for 5+ min |
| BUSY | Red 🔴 | `bg-red-500` | Manually set (future) |
| OFFLINE | Gray ⚪ | `bg-gray-300` | Logged out or idle 30+ min |

---

## 🎯 Quick Test Script

For rapid testing, use this sequence:

1. **30 seconds:** Login → Verify green dot
2. **30 seconds:** Have friend verify they see you online
3. **5 minutes:** Go idle → Verify yellow dot
4. **10 seconds:** Move mouse → Verify back to green
5. **10 seconds:** Logout → Verify gray dot
6. **DONE:** All core features tested in ~6 minutes

---

**Happy Testing! 🚀**

If all tests pass, the online/offline status system is working perfectly!
