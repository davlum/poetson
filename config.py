import os

#class Config(object):
DEBUG = True
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = os.environ.get("POETSON_SECRET_KEY", "")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql:///postgres'




#class ProductionConfig(Config):
#    DEBUG = False
#
#
#class StagingConfig(Config):
#    DEVELOPMENT = True
#    DEBUG = True
#
#
#class DevelopmentConfig(Config):
#    DEVELOPMENT = True
#    DEBUG = True
#
#
#class TestingConfig(Config):
#    TESTING = True
