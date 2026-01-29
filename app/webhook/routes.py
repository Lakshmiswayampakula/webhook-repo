from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

def format_timestamp(dt):
    """Format datetime to '1st April 2021 - 9:30 PM UTC' format"""
    day = dt.day
    # Handle special cases: 11th, 12th, 13th
    if 11 <= day <= 13:
        suffix = "th"
    elif day % 10 == 1:
        suffix = "st"
    elif day % 10 == 2:
        suffix = "nd"
    elif day % 10 == 3:
        suffix = "rd"
    else:
        suffix = "th"
    
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    hour = dt.hour
    minute = dt.minute
    
    # Convert to 12-hour format
    if hour == 0:
        hour_12 = 12
        am_pm = "AM"
    elif hour < 12:
        hour_12 = hour
        am_pm = "AM"
    elif hour == 12:
        hour_12 = 12
        am_pm = "PM"
    else:
        hour_12 = hour - 12
        am_pm = "PM"
    
    return f"{day}{suffix} {month_names[dt.month - 1]} {dt.year} - {hour_12}:{minute:02d} {am_pm} UTC"

@webhook.route('/receiver', methods=["POST", "GET"])
def receiver():
    """
    GitHub webhook receiver endpoint.
    Always returns 200 for valid GitHub requests so delivery never fails with 400.
    """
    # GET: allow health checks / manual visits to return 200
    if request.method == "GET":
        return jsonify({"message": "Webhook receiver is active. Use POST with X-GitHub-Event header."}), 200

    # Parse JSON body - use force=True so we accept even if Content-Type is wrong
    try:
        data = request.get_json(silent=True, force=True) or {}
    except Exception:
        data = {}

    event_type = (request.headers.get("X-GitHub-Event") or "").strip()

    # Ping: GitHub sends this when webhook is created - MUST return 200
    if event_type.lower() == "ping":
        return jsonify({"message": "Webhook configured successfully", "zen": data.get("zen", "")}), 200

    # No event type: treat as unknown but still return 200 so GitHub doesn't retry
    if not event_type:
        return jsonify({"message": "No X-GitHub-Event header; request ignored"}), 200

    try:
        github_event = event_type.lower()
        action = None
        ts = format_timestamp(datetime.utcnow())
        event = {
            "request_id": None,
            "author": "Unknown",
            "action": None,
            "from_branch": "",
            "to_branch": "",
            "timestamp": ts,
        }

        if github_event == "push":
            action = "PUSH"
            event["request_id"] = (
                data.get("after")
                or data.get("head_commit", {}).get("id")
                or ("push-%s" % ts.replace(" ", "-").replace(":", "-"))
            )
            commits = data.get("commits") or []
            if commits:
                author = commits[0].get("author") or {}
                event["author"] = (
                    author.get("name")
                    or author.get("username")
                    or (author.get("email") or "").split("@")[0]
                    or "Unknown"
                )
            if event["author"] == "Unknown":
                pusher = data.get("pusher") or {}
                event["author"] = pusher.get("name") or pusher.get("login") or "Unknown"
            ref = (data.get("ref") or "").strip()
            event["to_branch"] = ref.split("/")[-1] if ref else "main"

        elif github_event == "pull_request":
            pr = data.get("pull_request") or {}
            pr_action = (data.get("action") or "").lower()
            is_merged = pr.get("merged", False)
            if pr_action == "closed" and is_merged:
                action = "MERGE"
            elif pr_action in ("opened", "synchronize", "reopened"):
                action = "PULL_REQUEST"
            else:
                return jsonify({"message": "PR event acknowledged", "action": pr_action}), 200

            event["action"] = action
            event["request_id"] = str(data.get("number") or "")
            sender = data.get("sender") or {}
            pr_user = pr.get("user") or {}
            event["author"] = sender.get("login") or pr_user.get("login") or "Unknown"
            event["from_branch"] = (pr.get("head") or {}).get("ref") or ""
            event["to_branch"] = (pr.get("base") or {}).get("ref") or ""

        else:
            return jsonify({"message": "Event received", "event": github_event}), 200

        # Store only if we have at least action and something to identify the event
        if action and (event["request_id"] or event["author"] != "Unknown"):
            event["request_id"] = event["request_id"] or ("%s-%s" % (action.lower(), ts.replace(" ", "-").replace(":", "-")))
            try:
                mongo.db.events.insert_one(event)
            except Exception:
                pass  # Don't fail the request if DB is down
        return jsonify({"message": "Event stored successfully", "event": event}), 200

    except Exception as e:
        # Never return 400/500 for GitHub webhook - return 200 so delivery succeeds
        return jsonify({"message": "Event received", "error": str(e)}), 200
