import os

APP_NAME = 'explorebaduk'
APP_VERSION = '0.1.0'

# path to project root directory
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# ws game_server
SERVER_HOST = "localhost"
SERVER_PORT = 8080

# database
# MYSQL_DATABASE_URI = 'mysql:///username:password@host:port/database'
DATABASE_URI = 'sqlite:///' + os.path.join(BASE_PATH, 'explorebaduk.db')
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENCODING = 'utf8'
