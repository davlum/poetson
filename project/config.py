# project/config.py

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get("POETSON_SECRET_KEY", "")
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", "")
    UPLOAD_FOLDER = os.environ.get("POETSON_UPLOAD_FOLDER", "")
    ALLOWED_AUDIO_EXTENSIONS = set(['wv', 'wma', 'webm', 'wav', 'vox', 'tta', 'sln', 'raw',
    'ra','rm','opus','ogg','oga','mogg','nsf','msv','mpc','mp3','mmf','m4p','m4b','m4a','ivs','iklax','gsm','flac',
    'dvf','dss','dct','awb','au','ape','amr','aiff','act','aax','aac','aa','8svx','3gp',])
    ALLOWED_IMAGE_EXTENSIONS = set(['jpg', 'png'])
    # Max content length is ~ 200 mbs
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///postgres'

    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']

    # mail accounts
    MAIL_DEFAULT_SENDER = 'poetica.sonora.auto@gmail.com'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = False


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    DEBUG_TB_ENABLED = False
