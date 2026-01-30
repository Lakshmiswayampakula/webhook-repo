import os

from flask import Flask, render_template
from app.webhook.routes import webhook
from .extensions import mongo
from app.api.routes import api

# Try to import CORS, make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False


def create_app():
    """Flask application factory."""

    # Resolve templates directory (project_root/templates/index.html)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(project_root, "templates")

    app = Flask(__name__, template_folder=templates_dir)

    # MongoDB configuration
    # MUST be set via MONGO_URI environment variable in production
    # For local development, create a .env file (see .env.example)
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        raise ValueError(
            "MONGO_URI environment variable is required. "
            "Set it in your environment or create a .env file for local development."
        )
    app.config["MONGO_URI"] = mongo_uri

    # Allow cross-origin requests (if CORS is available)
    if CORS_AVAILABLE:
        CORS(app)
    else:
        # Manual CORS headers if flask-cors is not available
        @app.after_request
        def after_request(response):
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
            )
            return response

    # Initialize Mongo with app
    mongo.init_app(app)

    # registering all the blueprints
    app.register_blueprint(webhook)
    app.register_blueprint(api)

    # Route to serve the UI
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
