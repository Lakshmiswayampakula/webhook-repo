# Setup Instructions

## Prerequisites
- Python 3.8+ (Anaconda Python 3.12.4 detected)
- MongoDB Atlas account (connection string provided)

## Installation Steps

### 1. Install Python Dependencies

Open a terminal/command prompt and run:

```bash
cd "c:\Users\laksh\OneDrive\Desktop\Assignment_Task\webhook-repo-master"
pip install -r requirements.txt
```

Or if using Anaconda Python:
```bash
C:\Users\laksh\anaconda3\python.exe -m pip install -r requirements.txt
```

If you encounter network issues, try:
```bash
pip install Flask flask-cors Flask-Login Flask-PyMongo pymongo==4.3.3 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

### 2. Verify MongoDB Connection

The MongoDB connection string is already configured in `app/__init__.py`:
```
mongodb+srv://lakshmidevi2116_db_user:z3E3v1Eo6wmkkcNk@cluster0.5msctw9.mongodb.net/github_webhooks?retryWrites=true&w=majority&appName=Cluster0
```

### 3. Run the Application

```bash
python run.py
```

Or with Anaconda Python:
```bash
C:\Users\laksh\anaconda3\python.exe run.py
```

The application will start on `http://127.0.0.1:5000`

### 4. Access the Dashboard

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 5. Webhook Endpoint

The webhook receiver endpoint is:
```
POST http://127.0.0.1:5000/webhook/receiver
```

## GitHub Webhook Configuration

### For action-repo:

1. Go to your GitHub repository settings
2. Navigate to Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: `https://your-domain.com/webhook/receiver` (or use ngrok for local testing)
   - **Content type**: `application/json`
   - **Events**: Select "Just the push event" and "Pull requests"
   - **Active**: ✅ Checked

### Local Testing with ngrok:

1. Install ngrok: https://ngrok.com/download
2. Run ngrok: `ngrok http 5000`
3. Use the ngrok URL (e.g., `https://abc123.ngrok.io/webhook/receiver`) as your webhook URL

## Testing the Application

1. **Push Event**: Make a commit and push to your action-repo
2. **Pull Request**: Create a pull request in your action-repo
3. **Merge Event**: Merge a pull request in your action-repo

All events will appear in the dashboard automatically (refreshes every 15 seconds).

## Troubleshooting

### If packages fail to install:
- Check your internet connection
- Try using a VPN if behind a corporate firewall
- Install packages one by one to identify which one fails
- Use conda: `conda install -c conda-forge flask flask-cors flask-pymongo pymongo`

### If MongoDB connection fails:
- Verify your MongoDB Atlas cluster is running
- Check if your IP is whitelisted in MongoDB Atlas
- Verify the connection string is correct

### If webhook doesn't receive events:
- Check GitHub webhook delivery logs
- Verify the webhook URL is accessible
- Check Flask application logs for errors
