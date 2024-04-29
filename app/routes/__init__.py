from flask import Flask

# Import blueprints from their respective modules
from .main import main_bp
from .auth import auth_bp
from .habit import habit_bp
from .reminder import reminder_bp
from .analytics import analytics_bp


def init_app(app: Flask):
    """Initializes the application with different route handlers"""
    # Register the 'main' Blueprint
    if main_bp is not None:
        app.register_blueprint(main_bp)

    # Register the 'auth' Blueprint
    if auth_bp is not None:
        app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register the 'habit' Blueprint
    if habit_bp is not None:
        app.register_blueprint(habit_bp, url_prefix='/habits')

    # Register the 'reminder' Blueprint
    if reminder_bp is not None:
        app.register_blueprint(reminder_bp, url_prefix='/reminders')

    # Register the 'analytics' Blueprint
    if analytics_bp is not None:
        app.register_blueprint(analytics_bp, url_prefix='/analytics')
