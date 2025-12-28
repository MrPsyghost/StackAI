from flask import Flask
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'

    app.permanent_session_lifetime = timedelta(days=30)

    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    from .view import view
    app.register_blueprint(view)

    return app