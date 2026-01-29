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
    """GitHub webhook receiver endpoint."""
    # Handle empty requests gracefully
    data = request.json or {}
    event_type = request.headers.get("X-GitHub-Event", "")

    # Handle GitHub ping event (sent when webhook is first created)
    if event_type.lower() == "ping":
        return jsonify({"message": "Webhook configured successfully", "zen": data.get("zen", "")}), 200

    # Validate we have required data for actual events
    if not event_type:
        return jsonify({"error": "Missing X-GitHub-Event header"}), 400

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
            # Get commit hash from 'after' field or head_commit
            event["request_id"] = data.get("after") or data.get("head_commit", {}).get("id", "")
            
            # Try to get author from commits first, then pusher
            commits = data.get("commits", [])
            if commits and len(commits) > 0:
                commit_author = commits[0].get("author", {})
                event["author"] = commit_author.get("name") or commit_author.get("username") or commit_author.get("email", "").split("@")[0]
            
            # Fallback to pusher if no author found
            if not event["author"]:
                pusher = data.get("pusher", {})
                event["author"] = pusher.get("name") or pusher.get("login") or "Unknown"
            
            # Extract branch name from ref (e.g., refs/heads/main -> main)
            ref = data.get("ref", "")
            event["to_branch"] = ref.split("/")[-1] if ref else "main"

        elif github_event == "pull_request":
            pr = data.get("pull_request", {})
            pr_action = data.get("action", "").lower()
            is_merged = pr.get("merged", False)
            
            # Check if this is a merge (closed + merged) or a pull request (opened)
            if pr_action == "closed" and is_merged:
                action = "MERGE"
            elif pr_action in ["opened", "synchronize", "reopened"]:
                action = "PULL_REQUEST"
            else:
                # For other PR actions, skip storing (like labeled, assigned, etc.)
                return jsonify({"message": f"PR action '{pr_action}' skipped"}), 200
            
            event["action"] = action
            event["request_id"] = str(data.get("number", ""))  # PR ID
            
            # Get author from sender or PR user
            sender = data.get("sender", {})
            pr_user = pr.get("user", {})
            event["author"] = sender.get("login") or pr_user.get("login") or "Unknown"
            
            event["from_branch"] = pr.get("head", {}).get("ref", "")
            event["to_branch"] = pr.get("base", {}).get("ref", "")

        else:
            # For other event types, return 200 but don't store
            return jsonify({"message": f"Event type '{github_event}' received but not processed"}), 200

        # Validate we have required fields before storing
        if not action:
            return jsonify({"error": "Could not determine action type"}), 400
        
        if not event["request_id"]:
            return jsonify({"error": "Missing request_id (commit hash or PR number)"}), 400
        
        if not event["author"] or event["author"] == "Unknown":
            return jsonify({"error": "Missing author information"}), 400

        # Store event in MongoDB
        mongo.db.events.insert_one(event)
        return jsonify({"message": "Event stored successfully", "event": event}), 200

    except Exception as e:
        import traceback
        # Log error but don't expose full traceback in production
        error_msg = str(e)
        return jsonify({"error": "Internal server error", "message": error_msg}), 500
