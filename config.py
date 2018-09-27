import logging


class Config(object):
    DEBUG = False
    TESTING = False
    LOGGING = logging.INFO
    DATABASE_NAME = "smol"
    DATABASE_USER = "smol"
    DATABASE_PASS = "smol"


class ProductionConfig(Config):
    DATABASE_PASS = "smolSmol"


class DevelopmentConfig(Config):
    DEBUG = True
    LOGGING = logging.DEBUG
