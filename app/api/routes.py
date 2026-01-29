from flask import Blueprint, jsonify
from app.extensions import mongo

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/events', methods=['GET'])
def get_events():
    # Fetch events from MongoDB, sorted by timestamp descending
    # Get all events, not just last 10, so UI can show all
    events = list(mongo.db.events.find().sort('timestamp', -1))

    formatted = []
    for e in events:
        author = e.get("author", "Unknown")
        action = e.get("action", "")
        from_branch = e.get("from_branch", "")
        to_branch = e.get("to_branch", "")
        timestamp = e.get("timestamp", "")
        request_id = e.get("request_id", "")

        # Format message according to requirements
        if action == "PUSH":
            message = f'{author} pushed to {to_branch} on {timestamp}'
        elif action == "PULL_REQUEST":
            message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'
        elif action == "MERGE":
            message = f'{author} merged branch {from_branch} to {to_branch} on {timestamp}'
        else:
            message = f'{author} performed {action} on {timestamp}'

        formatted.append({
            "message": message,
            "timestamp": timestamp,
            "action": action,
            "author": author,
            "request_id": request_id,
            "from_branch": from_branch,
            "to_branch": to_branch
        })

    return jsonify(formatted)
