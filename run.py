import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Only enable debug mode in development (when FLASK_ENV=development)
    # Never use debug=True in production!
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    
    app.run(debug=debug_mode, host=host, port=port)
