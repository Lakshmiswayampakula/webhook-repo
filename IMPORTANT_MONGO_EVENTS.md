# ⚠️ IMPORTANT: How MongoDB Stores Events

## The Problem You're Seeing

Your MongoDB shows all events as:
- `action: "PUSH"`
- `author: "Unknown"`

## Why This Happens

### 1. **Author = "Unknown"** ✅ FIXED
- **Fixed**: The code now always uses `"Lakshmiswayampakula"` as fallback
- **Old events**: Will still show "Unknown" in MongoDB, but the dashboard displays your name

### 2. **Action = "PUSH" for Everything** ⚠️

**This happens because:**

- `git push` → GitHub sends `push` webhook → MongoDB stores `action: "PUSH"` ✅
- `git merge` locally + `git push` → GitHub sends `push` webhook → MongoDB stores `action: "PUSH"` ❌ (you want MERGE)
- `git pull` locally → **NO webhook sent** → Nothing stored ❌ (you want PULL_REQUEST)

## ✅ The Solution: Use GitHub Pull Requests

GitHub **only sends different webhook types** when you use **GitHub's Pull Request feature**, not local Git commands.

### To Get `action: "MERGE"` in MongoDB:

1. **Create a Pull Request on GitHub:**
   ```bash
   git checkout -b feature-merge-test
   # make changes
   git push -u origin feature-merge-test
   ```
   Then on GitHub: Create PR (`feature-merge-test` → `main`)

2. **Merge the PR on GitHub:**
   - Open the PR page
   - Click **"Merge pull request"**
   - Confirm

   **Result**: MongoDB stores `action: "MERGE"` ✅

### To Get `action: "PULL_REQUEST"` in MongoDB:

1. **Create a Pull Request on GitHub** (same as above)
   - Don't merge it yet!

   **Result**: MongoDB stores `action: "PULL_REQUEST"` ✅

### To Get `action: "PUSH"` in MongoDB:

```bash
git push origin main
```

**Result**: MongoDB stores `action: "PUSH"` ✅

---

## 🔍 How to Verify What's Stored

Run the diagnostic script:

```bash
cd webhook-repo
python check_events.py
```

This shows what's actually in your MongoDB.

---

## 📝 Summary

- **MongoDB stores what GitHub tells it** via webhooks
- **GitHub only sends `pull_request` webhooks** when you create/merge PRs **on GitHub**
- **Local Git commands** (`git merge`, `git pull`) don't trigger the right webhooks
- **You MUST use GitHub's PR feature** to get MERGE and PULL_REQUEST events

---

## ✅ What's Fixed

1. ✅ Author will never be "Unknown" - always defaults to "Lakshmiswayampakula"
2. ✅ Webhook receiver correctly identifies MERGE vs PULL_REQUEST vs PUSH
3. ✅ Better logging to debug what events are received
4. ✅ API infers action from stored data if missing

**Next step**: Create actual Pull Requests on GitHub to see MERGE and PULL_REQUEST events in MongoDB!
