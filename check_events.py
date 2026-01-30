"""
Diagnostic script to check what's actually stored in MongoDB.
Run this to see what action values your events have.
"""
from app import create_app
from app.extensions import mongo

def check_events():
    """Check all events in MongoDB and show their action values."""
    app = create_app()
    
    with app.app_context():
        try:
            events = list(mongo.db.events.find().sort('_id', -1).limit(10))
            
            print(f"\nFound {len(events)} recent events:\n")
            print("-" * 80)
            
            for i, e in enumerate(events, 1):
                action = e.get("action", "MISSING")
                author = e.get("author", "MISSING")
                from_branch = e.get("from_branch", "")
                to_branch = e.get("to_branch", "")
                timestamp = e.get("timestamp", "MISSING")
                
                print(f"\nEvent {i}:")
                print(f"  Action: {action}")
                print(f"  Author: {author}")
                print(f"  From Branch: {from_branch}")
                print(f"  To Branch: {to_branch}")
                print(f"  Timestamp: {timestamp[:50]}..." if len(timestamp) > 50 else f"  Timestamp: {timestamp}")
                print("-" * 80)
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_events()
