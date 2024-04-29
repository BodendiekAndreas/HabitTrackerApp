from flask import Flask
from .config import config_by_name
from .extensions import db, migrate, login_manager
from datetime import datetime
from .models import Completion
import logging

from .routes.auth import auth_bp
from .routes.habit import habit_bp
from .routes.main import main_bp
from .routes.reminder import reminder_bp
from .routes.analytics import analytics_bp

flask_app = None


def create_app(config_name='default'):
    # The application factory function. This function creates and configures the Flask application object.
    # It then initializes all the extensions, registers all blueprints,
    # and returns the created Flask application object.
    global flask_app
    # Create a new Flask application object
    flask_app = Flask(__name__)
    # Load the configuration from the config dictionary
    flask_app.config.from_object(config_by_name[config_name])
    # Update additional Flask configurations
    flask_app.config.update(
        SERVER_NAME='127.0.0.1:5000',
        APPLICATION_ROOT='/',
        PREFERRED_URL_SCHEME='http'
    )

    # Initialize extensions
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    flask_app.logger.setLevel(logging.INFO)
    # Set the logging level to INFO

    # Register blueprints
    flask_app.register_blueprint(auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(habit_bp, url_prefix='/habits')
    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(reminder_bp, url_prefix='/reminders')
    flask_app.register_blueprint(analytics_bp, url_prefix='/analytics')

    # Register a context processor function that will return the current date and time.
    @flask_app.context_processor
    def inject_datetime():
        return {'datetime': datetime}

    # Register another context processor function that returns a function to get
    # the completion count of a habit
    @flask_app.context_processor
    def utility_processor():
        def get_completions_count(habit_id):
            return Completion.query.filter_by(habit_id=habit_id).count()

        return dict(get_completions_count=get_completions_count)

    return flask_app
    # Return the created Flask application object.
