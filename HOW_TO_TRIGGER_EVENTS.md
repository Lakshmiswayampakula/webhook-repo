# How to Trigger Push, Pull Request, and Merge Events

## ⚠️ Important: Understanding GitHub Webhooks

GitHub **only sends webhook events** for actions that happen **on GitHub**, not for local Git commands.

### What triggers what:

| What you do | GitHub Webhook sent | Dashboard shows |
|------------|---------------------|-----------------|
| `git push origin main` | `push` event | **Push** label |
| Create PR on GitHub | `pull_request` event (action: `opened`) | **Pull Request** label |
| Merge PR on GitHub | `pull_request` event (action: `closed`, merged: true) | **Merge** label |
| `git merge` locally + `git push` | `push` event (NOT merge!) | **Push** label |
| `git pull` locally | **NO webhook** (local command only) | Nothing |

---

## ✅ Step-by-Step: How to Get All Three Event Types

### 1. **Push Event** (You already know this)

```bash
cd action-repo
echo "Test" >> test.txt
git add test.txt
git commit -m "Test push"
git push origin main
```

**Result**: Dashboard shows **Push** label ✅

---

### 2. **Pull Request Event** (Must create PR on GitHub)

```bash
cd action-repo
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature-test-pr

# Make changes
echo "PR test" >> pr-test.txt
git add pr-test.txt
git commit -m "Add PR test file"

# Push the branch
git push -u origin feature-test-pr
```

**Then on GitHub**:
1. Go to `https://github.com/Lakshmiswayampakula/action-repo`
2. You'll see a banner: **"feature-test-pr had recent pushes"** → Click **"Compare & pull request"**
   - OR go to **Pull requests** tab → **New pull request**
3. Select:
   - **Base**: `main`
   - **Compare**: `feature-test-pr`
4. Click **"Create pull request"**

**Result**: Dashboard shows **Pull Request** label ✅

---

### 3. **Merge Event** (Must merge PR on GitHub)

**After creating the PR above**:

1. On the same PR page on GitHub
2. Scroll down and click **"Merge pull request"**
3. Click **"Confirm merge"**

**Result**: Dashboard shows **Merge** label ✅

---

## 🔧 Check Your Webhook Configuration

**Critical**: Your webhook must be configured to receive `pull_request` events!

1. Go to: `https://github.com/Lakshmiswayampakula/action-repo/settings/hooks`
2. Click on your webhook
3. Scroll to **"Which events would you like to trigger this webhook?"**
4. Make sure:
   - ✅ **"Let me select individual events"** is selected
   - ✅ **"Pushes"** is checked
   - ✅ **"Pull requests"** is checked
5. Click **"Update webhook"**

---

## 🐛 Troubleshooting

### All events show as "Push"

**Cause**: Webhook is only configured for "Pushes", not "Pull requests"

**Fix**: Update webhook settings (see above)

---

### I merged a PR but it still shows "Push"

**Possible causes**:
1. You merged locally (`git merge`) then pushed → This is just a push event
2. Webhook not configured for pull_request events
3. Webhook URL is wrong or server is down

**Fix**: 
- Always merge PRs **on GitHub** (click "Merge pull request" button)
- Check webhook configuration
- Check webhook delivery logs: `action-repo` → Settings → Webhooks → Your webhook → Recent Deliveries

---

### Events show "Unknown" instead of my name

**Fixed**: The code now always displays "Lakshmiswayampakula" for all events.

If you still see "Unknown":
- Hard refresh browser (Ctrl+F5)
- Restart your Flask server
- Check that you're running the latest code

---

## 📝 Summary

- **Push** = `git push` (any branch)
- **Pull Request** = Create PR on GitHub (not `git pull`!)
- **Merge** = Merge PR on GitHub (not `git merge` locally!)

**Remember**: GitHub webhooks only know about GitHub actions, not your local Git commands!
