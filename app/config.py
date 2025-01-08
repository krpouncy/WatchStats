# app/config.py

class DefaultConfig:
    DEBUG = True
    TESTING = False


class TestingConfig(DefaultConfig):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for tests
