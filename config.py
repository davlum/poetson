POSTGRES = {
    'user': 'davidlum',
    'pw': 'password',
    'db': 'myflaskapp',
    'host': 'localhost',
    'port': '5432',
}

#class Config(object):
DEBUG = True
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = 'this-really-needs-to-be-changed'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:\
    %(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES


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
