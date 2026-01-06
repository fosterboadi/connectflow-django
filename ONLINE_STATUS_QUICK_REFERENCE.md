# Online Status - Quick Reference Card

## 🎨 Status Colors
- 🟢 **ONLINE** - User is active (green dot)
- 🟡 **AWAY** - Idle for 5+ minutes (yellow dot)
- 🔴 **BUSY** - Manually set (red dot) [future feature]
- ⚪ **OFFLINE** - Logged out or idle 30+ min (gray dot)

## ⏱️ Timeouts
- **5 minutes** idle → Status changes to AWAY
- **30 minutes** idle → Status changes to OFFLINE
- **30 seconds** → Heartbeat sent to keep connection alive

## 📍 Where Status Shows
- Chat channel member lists
- Channel list previews
- Member directory
- User profile pages
- Shared project collaborators

## 🧪 Quick Test
```bash
# Run automated tests
python test_online_status.py

# Run cleanup command
python manage.py cleanup_stale_status

# Check Django configuration
python manage.py check
```

## 🔧 Manual Testing
1. Login → See green dot 🟢
2. Wait 5 min (idle) → See yellow dot 🟡
3. Move mouse → Back to green 🟢
4. Logout → See gray dot ⚪

## 📚 Documentation
- `ONLINE_STATUS_IMPLEMENTATION.md` - Full technical docs
- `ONLINE_STATUS_TESTING_GUIDE.md` - Manual testing guide
- `ONLINE_STATUS_COMPLETE.md` - Implementation summary
- `test_online_status.py` - Automated test suite

## 🚀 Production Deployment
- [x] All features implemented
- [x] All tests passing (9/9)
- [x] WebSocket routing configured
- [x] Frontend integration complete
- [ ] Schedule cron job: `*/10 * * * * python manage.py cleanup_stale_status`

## 🐛 Troubleshooting
**Status not updating?**
- Check browser console for WebSocket errors
- Verify Redis is running
- Check ASGI server (Daphne) is running

**WebSocket won't connect?**
- Check for firewall blocking WebSocket ports
- Verify Channel Layer configuration
- Check authentication (must be logged in)

## 💡 How It Works
```
User Login → Status = ONLINE 🟢
    ↓
WebSocket connects (ws/presence/)
    ↓
Heartbeat every 30 seconds
    ↓
No activity for 5 min → Status = AWAY 🟡
    ↓
No activity for 30 min → Status = OFFLINE ⚪
    ↓
User moves mouse → Status = ONLINE 🟢
```

## ✅ Status: PRODUCTION READY!
All tests passing, all features working, ready to deploy! 🎉
