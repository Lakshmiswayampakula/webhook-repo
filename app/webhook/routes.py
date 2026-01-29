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

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    if not data or not event_type:
        return jsonify({"error": "Missing data or event type"}), 400

    try:
        github_event = event_type.lower()
        action = None
        event = {
            "request_id": None,
            "author": None,
            "action": None,
            "from_branch": None,
            "to_branch": None,
            "timestamp": format_timestamp(datetime.utcnow())
        }

        if github_event == "push":
            # Handle PUSH event
            action = "PUSH"
            event["request_id"] = data.get("after") or data.get("head_commit", {}).get("id", "")
            # Try to get author from commits first, then pusher
            commits = data.get("commits", [])
            if commits and len(commits) > 0:
                event["author"] = commits[0].get("author", {}).get("name") or commits[0].get("author", {}).get("username")
            if not event["author"]:
                event["author"] = data.get("pusher", {}).get("name") or data.get("pusher", {}).get("login")
            # Extract branch name from ref (e.g., refs/heads/main -> main)
            ref = data.get("ref", "")
            event["to_branch"] = ref.split("/")[-1] if ref else ""

        elif github_event == "pull_request":
            pr = data.get("pull_request", {})
            pr_action = data.get("action", "").lower()
            is_merged = pr.get("merged", False)
            
            # Check if this is a merge (closed + merged) or a pull request (opened)
            if pr_action == "closed" and is_merged:
                action = "MERGE"
            elif pr_action == "opened" or pr_action == "synchronize":
                action = "PULL_REQUEST"
            else:
                # For other PR actions, we might still want to store as PULL_REQUEST
                action = "PULL_REQUEST"
            
            event["action"] = action
            event["request_id"] = str(data.get("number", ""))  # PR ID
            event["author"] = data.get("sender", {}).get("login") or pr.get("user", {}).get("login")
            event["from_branch"] = pr.get("head", {}).get("ref", "")
            event["to_branch"] = pr.get("base", {}).get("ref", "")

        else:
            return jsonify({"message": f"Unhandled event type: {github_event}"}), 400

        # Only store if we have a valid action
        if action and event["request_id"] and event["author"]:
            mongo.db.events.insert_one(event)
            return jsonify({"message": "Event stored successfully", "event": event}), 200
        else:
            return jsonify({"error": "Missing required fields", "event": event}), 400

    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
