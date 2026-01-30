"""
Gunicorn entrypoint (alternative to run:app).

Use either:  gunicorn run:app   or   gunicorn app:app
Both expose the same Flask app via create_app().
"""

from app import create_app

app = create_app()