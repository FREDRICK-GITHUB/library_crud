from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'FDERTYHTJ8yuikoyTRHY^&975657898ik9jhg'

    return app