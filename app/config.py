import os

# Basedir will be the absolute path to the directory the script is in.
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Base configuration class. Sets the SECRET KEY and SQLALCHEMY_DATABASE_URI variables.
    # SECRET_KEY is used to keep client-side sessions secure.
    # SQLALCHEMY_DATABASE_URI defines the database to connect to.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-long-and-secure-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    # Development configuration class.
    # Inherits from Config.
    # DEBUG is set to True.
    # SQLALCHEMY_ECHO is enabled to help with debugging by
    # logging all SQLAlchemy commands to the console.
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    # Testing configuration class.
    # Inherits from Config.
    # TESTING is set to True.
    # A separate test database is defined.
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    # Production configuration class.
    # Inherits from Config.
    # DEBUG is set to False for production.
    # A separate production database is defined.
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DATABASE_URI')

    # Mapping of configuration names to configuration classes.
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
