# GitHub Webhook Dashboard

A Flask app that receives GitHub webhook events (Push, Pull Request, Merge), stores them in MongoDB, and shows them on a real-time dashboard. I built this as the webhook receiver for the GitHub events flow.

## What’s in this repo

- **Webhook endpoint** – `POST /webhook/receiver` accepts GitHub webhooks and stores events.
- **Dashboard** – Web UI that lists recent events and auto-refreshes every 15 seconds.
- **API** – `GET /api/events` returns stored events as JSON.

## Requirements

- Python 3.8+
- MongoDB (e.g. MongoDB Atlas)
- Dependencies in `requirements.txt`

## How to run locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. MongoDB

Use a MongoDB Atlas cluster (or local MongoDB). **The connection string must be provided via environment variable**:

- Set the `MONGO_URI` environment variable (both locally and in production).

Database name used (suggested): `github_webhooks`. Collection: `events`.

### 3. Run the app

```bash
python run.py
```

App runs at `http://127.0.0.1:5000`.

### 4. Optional: test MongoDB connection

```bash
python test_connection.py
```

## How to use the dashboard

1. Open `http://127.0.0.1:5000` in a browser.
2. The page shows “Recent Events” and auto-refreshes every 15 seconds.
3. To see events, send webhooks to this app (e.g. from an “action” repo; see **GitHub webhook setup** below).

## GitHub webhook setup

To receive events from a GitHub repo:

1. In that repo: **Settings → Webhooks → Add webhook**.
2. **Payload URL:**  
   - Local: use a tunnel (e.g. ngrok: `ngrok http 5000`) and set URL to `https://<your-ngrok-host>/webhook/receiver`.  
   - Production: `https://<your-deployed-domain>/webhook/receiver`.
3. **Content type:** `application/json`.
4. **Events:** Choose “Let me select individual events” and enable **Pushes** and **Pull requests**.
5. Save the webhook.

## Deploying (e.g. Render)

1. Connect this repo to Render and create a Web Service.
2. **Build:** `pip install -r requirements.txt`
3. **Start:** `gunicorn run:app` (uses `run.py`; `gunicorn app:app` also works).
4. Set **Environment variable:** `MONGO_URI` = your MongoDB Atlas connection string (include database name in the URL, e.g. `github_webhooks`).
5. In MongoDB Atlas → Network Access, allow `0.0.0.0/0` (or Render’s IPs) so the app can connect.

After deploy, use the Render URL in the webhook Payload URL (e.g. `https://<your-service>.onrender.com/webhook/receiver`).

## API endpoints

| Method | Path               | Description                |
|--------|--------------------|----------------------------|
| GET    | `/`                | Dashboard UI               |
| POST   | `/webhook/receiver`| GitHub webhook receiver    |
| GET    | `/api/events`      | List events (JSON)         |
| GET    | `/api/health`      | Health check               |

## Event format (stored in MongoDB)

Each document has:

- `request_id` – Commit hash or PR number
- `author` – GitHub username
- `action` – `PUSH`, `PULL_REQUEST`, or `MERGE`
- `from_branch` / `to_branch` – Branch names (when applicable)
- `timestamp` – Formatted string (e.g. “1st April 2021 - 9:30 PM UTC”)

Messages shown on the dashboard:

- **Push:** `{author} pushed to {to_branch} on {timestamp}`
- **Pull request:** `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`
- **Merge:** `{author} merged branch {from_branch} to {to_branch} on {timestamp}`

## Project structure

```
webhook-repo/
├── app/
│   ├── __init__.py       # App factory, MongoDB config
│   ├── extensions.py     # Mongo instance
│   ├── webhook/routes.py # Webhook receiver
│   └── api/routes.py     # /api/events, /api/health
├── templates/
│   └── index.html        # Dashboard UI
├── app.py                # Gunicorn entry: app = create_app()
├── run.py                # Local dev server
├── requirements.txt
├── render.yaml            # Optional Render blueprint
└── test_connection.py     # Optional MongoDB test
```

## Troubleshooting

- **Dashboard shows “Connection Error” or no events:** Check `MONGO_URI` and MongoDB Atlas network access (e.g. `0.0.0.0/0`). Ensure the app can reach the cluster.
- **Webhook deliveries fail (e.g. 4xx/5xx):** The receiver is built to return 200 for valid GitHub deliveries (including ping). Check Render/server logs for exceptions.
- **Events not updating:** Dashboard polls every 15 seconds; new events appear after the next refresh.
