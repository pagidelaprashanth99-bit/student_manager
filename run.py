from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Use PORT environment variable if available (for production), default to 5000 for local
    port = int(os.environ.get('PORT', 5000))
    # Only run in debug mode if not in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
