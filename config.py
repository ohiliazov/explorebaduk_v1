class BaseConfig:
    SQLALCHEMY_URL = None
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENCODING = 'utf8'
    WEBSOCKET_PORT = None


class DevConfig(BaseConfig):
    SQLALCHEMY_URL = 'mysql://root@localhost/explorebaduk_dev'
    WEBSOCKET_PORT = 8080


class TestConfig(BaseConfig):
    SQLALCHEMY_URL = 'mysql://root@localhost/explorebaduk_test'
    WEBSOCKET_PORT = 8081


class ProdConfig(BaseConfig):
    SQLALCHEMY_URL = 'mysql://root@localhost/explorebaduk'
    SQLALCHEMY_ECHO = False
    WEBSOCKET_PORT = 8000
