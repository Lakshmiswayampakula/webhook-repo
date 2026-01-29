# GitHub Webhook Receiver - Assignment Solution

A Flask-based webhook receiver that processes GitHub webhook events (Push, Pull Request, Merge) and displays them in a real-time dashboard.

## 🚀 Features

- ✅ **GitHub Webhook Integration**: Receives and processes Push, Pull Request, and Merge events
- ✅ **MongoDB Storage**: Stores webhook events with proper schema
- ✅ **Real-time Dashboard**: Beautiful UI that auto-refreshes every 15 seconds
- ✅ **Event Formatting**: Displays events in the required format:
  - Push: `{author} pushed to {branch} on {timestamp}`
  - Pull Request: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`
  - Merge: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`
- ✅ **Timestamp Formatting**: Custom format matching requirements (e.g., "1st April 2021 - 9:30 PM UTC")

## 📋 Requirements

- Python 3.8+
- MongoDB Atlas account (connection string configured)
- Flask and dependencies (see requirements.txt)

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using Anaconda:
```bash
C:\Users\laksh\anaconda3\python.exe -m pip install -r requirements.txt
```

### 2. Verify Setup (Optional)

Run the test script to verify everything is configured correctly:

```bash
python test_connection.py
```

### 3. Run the Application

```bash
python run.py
```

The application will start on `http://127.0.0.1:5000`

### 4. Access the Dashboard

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 🔗 API Endpoints

- `GET /` - Main dashboard UI
- `POST /webhook/receiver` - GitHub webhook endpoint
- `GET /api/events` - JSON API for latest events

## 📊 MongoDB Schema

```javascript
{
    "_id": ObjectId,
    "request_id": "string",      // Commit hash or PR ID
    "author": "string",          // GitHub username
    "action": "string",          // PUSH, PULL_REQUEST, or MERGE
    "from_branch": "string",     // Source branch
    "to_branch": "string",       // Target branch
    "timestamp": "string"         // Formatted UTC timestamp
}
```

## 🔧 GitHub Webhook Configuration

### For action-repo:

1. Go to your GitHub repository settings
2. Navigate to **Settings → Webhooks → Add webhook**
3. Configure:
   - **Payload URL**: `https://your-domain.com/webhook/receiver` (or use ngrok for local testing)
   - **Content type**: `application/json`
   - **Events**: Select "Just the push event" and "Pull requests"
   - **Active**: ✅ Checked

### Local Testing with ngrok:

1. Install ngrok: https://ngrok.com/download
2. Run ngrok: `ngrok http 5000`
3. Use the ngrok URL (e.g., `https://abc123.ngrok.io/webhook/receiver`) as your webhook URL

## 🧪 Testing

1. **Push Event**: Make a commit and push to your action-repo
2. **Pull Request**: Create a pull request in your action-repo
3. **Merge Event**: Merge a pull request in your action-repo

All events will appear in the dashboard automatically (refreshes every 15 seconds).

## 📁 Project Structure

```
webhook-repo-master/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── extensions.py        # MongoDB extension
│   ├── webhook/
│   │   └── routes.py        # Webhook receiver endpoint
│   └── api/
│       └── routes.py        # API endpoints
├── templates/
│   └── index.html          # Dashboard UI
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── test_connection.py      # Connection test script
└── README.md              # This file
```

## 🎯 Assignment Requirements Completed

- ✅ Flask webhook receiver implemented
- ✅ MongoDB integration with proper schema
- ✅ Support for PUSH, PULL_REQUEST, and MERGE events
- ✅ Real-time UI with 15-second polling
- ✅ Proper timestamp formatting
- ✅ Clean, modern UI design
- ✅ Error handling and validation

## 🚨 Troubleshooting

See `SETUP.md` for detailed troubleshooting guide.

## 📝 Notes

- MongoDB connection string is configured in `app/__init__.py`
- The UI automatically polls `/api/events` every 15 seconds
- Webhook events are stored immediately upon receipt
- Timestamps are formatted in UTC timezone
