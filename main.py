import os
from website import create_app

app = create_app()


# only run if the file is run directly else do not run
if __name__ == "__main__":
    # Use environment variable to control debug mode (default: False for production)
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")

    app.run(debug=debug_mode, host=host, port=port)
