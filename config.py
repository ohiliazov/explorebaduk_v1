class BaseConfig:
    DATABASE_URI = None
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENCODING = 'utf8'
    WEBSOCKET_PORT = None


class DevConfig(BaseConfig):
    DATABASE_URI = 'sqlite:///explorebaduk.db'
    WEBSOCKET_PORT = 8080


class TestConfig(BaseConfig):
    DATABASE_URI = 'sqlite:///explorebaduk.db'
    WEBSOCKET_PORT = 8081


class ProdConfig(BaseConfig):
    DATABASE_URI = 'mysql://root@localhost/explorebaduk'
    SQLALCHEMY_ECHO = False
    WEBSOCKET_PORT = 8000
