from flask import Blueprint, jsonify
from datetime import datetime, timedelta
import re
from app.extensions import mongo

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Try to ping MongoDB
        mongo.db.command('ping')
        return jsonify({
            "status": "healthy",
            "mongodb": "connected"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "mongodb": "disconnected",
            "error": str(e)
        }), 503

# Max events to return (production-safe, avoids huge responses)
EVENTS_LIMIT = 100


def ensure_ist_in_timestamp(timestamp_str):
    """Ensure timestamp includes IST. If it doesn't, parse UTC time and add IST."""
    if not timestamp_str:
        return timestamp_str
    
    # Check if IST is already present
    if "(IST)" in timestamp_str or "IST)" in timestamp_str:
        return timestamp_str
    
    # Try to parse the UTC timestamp and add IST
    # Format: "30th January 2026 - 8:06 AM UTC"
    try:
        # Extract UTC time components using regex
        match = re.search(r'(\d{1,2})(?:st|nd|rd|th)\s+(\w+)\s+(\d{4})\s+-\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+UTC', timestamp_str)
        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            year = int(match.group(3))
            hour_12 = int(match.group(4))
            minute = int(match.group(5))
            am_pm = match.group(6)
            
            # Convert to 24-hour format
            if am_pm == "PM" and hour_12 != 12:
                hour_24 = hour_12 + 12
            elif am_pm == "AM" and hour_12 == 12:
                hour_24 = 0
            else:
                hour_24 = hour_12
            
            # Create UTC datetime
            month_map = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month = month_map.get(month_name, 1)
            utc_dt = datetime(year, month, day, hour_24, minute)
            
            # Convert to IST (UTC+5:30)
            ist_dt = utc_dt + timedelta(hours=5, minutes=30)
            
            # Format IST time
            ist_day = ist_dt.day
            if 11 <= ist_day <= 13:
                ist_suffix = "th"
            elif ist_day % 10 == 1:
                ist_suffix = "st"
            elif ist_day % 10 == 2:
                ist_suffix = "nd"
            elif ist_day % 10 == 3:
                ist_suffix = "rd"
            else:
                ist_suffix = "th"
            
            ist_hour = ist_dt.hour
            ist_minute = ist_dt.minute
            
            if ist_hour == 0:
                ist_hour_12 = 12
                ist_am_pm = "AM"
            elif ist_hour < 12:
                ist_hour_12 = ist_hour
                ist_am_pm = "AM"
            elif ist_hour == 12:
                ist_hour_12 = 12
                ist_am_pm = "PM"
            else:
                ist_hour_12 = ist_hour - 12
                ist_am_pm = "PM"
            
            ist_month_names = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
            
            ist_str = f"{ist_day}{ist_suffix} {ist_month_names[ist_dt.month - 1]} {ist_dt.year} - {ist_hour_12}:{ist_minute:02d} {ist_am_pm} IST"
            
            return f"{timestamp_str} ({ist_str})"
    except Exception:
        # If parsing fails, return original timestamp
        pass
    
    return timestamp_str


@api.route('/events', methods=['GET'])
def get_events():
    """Get all webhook events from MongoDB. Returns 200 with array, or 503 on DB failure."""
    try:
        # Sort by _id descending (newest first; _id is time-based)
        events = list(mongo.db.events.find().sort('_id', -1).limit(EVENTS_LIMIT))
    except Exception:
        # Return 503 so frontend keeps previous events and shows connection error (production-safe)
        return jsonify({"error": "Database unavailable", "events": []}), 503

    formatted = []
    for e in events:
        # Normalize author, and map "Unknown" to your GitHub name for display
        author_raw = e.get("author") or ""
        author = (author_raw or "").strip() or "Unknown"
        if author == "Unknown":
            author = "Lakshmiswayampakula"

        action = e.get("action") or ""
        from_branch = e.get("from_branch") or ""
        to_branch = e.get("to_branch") or ""
        timestamp = e.get("timestamp") or ""
        request_id = e.get("request_id") or ""
        
        # Ensure timestamp includes IST
        timestamp = ensure_ist_in_timestamp(timestamp)

        # Format messages consistently - all follow "pushed to main" style format
        if action == "PUSH":
            # Default to "main" if to_branch is empty
            branch = to_branch or "main"
            message = f'{author} pushed to {branch} on {timestamp}'
        elif action == "PULL_REQUEST":
            # Ensure we have branch info, default to "main" if missing
            from_br = from_branch or "feature"
            to_br = to_branch or "main"
            message = f'{author} submitted a pull request from {from_br} to {to_br} on {timestamp}'
        elif action == "MERGE":
            # Ensure we have branch info
            from_br = from_branch or "feature"
            to_br = to_branch or "main"
            message = f'{author} merged branch {from_br} to {to_br} on {timestamp}'
        else:
            # Treat any unknown/legacy action as a push-style event for consistent display
            branch = to_branch or "main"
            message = f'{author} pushed to {branch} on {timestamp}'

        formatted.append({
            "message": message,
            "timestamp": timestamp,
            "action": action,
            "author": author,
            "request_id": request_id,
            "from_branch": from_branch,
            "to_branch": to_branch,
        })

    return jsonify(formatted)
