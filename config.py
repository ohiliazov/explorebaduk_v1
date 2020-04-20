import os

APP_NAME = "explorebaduk"
APP_VERSION = "0.1.0"

# path to project root directory
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# ws game_server
SERVER_HOST = "localhost"
SERVER_PORT = 8080

# database
# MYSQL_DATABASE_URI = 'mysql:///username:password@host:port/database'
DATABASE_PATH = os.path.join(BASE_PATH, "explorebaduk.db")
# DATABASE_URI = "sqlite:///" + DATABASE_PATH
DATABASE_URI = "postgresql://ohili:ohili@localhost:5432/explorebaduk"
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENCODING = "utf8"

# test
TEST_SERVER_HOST = "localhost"
TEST_SERVER_PORT = 8083

TEST_DATABASE_PATH = os.path.join(BASE_PATH, "explorebaduk_test.db")
TEST_DATABASE_URI = "sqlite:///" + TEST_DATABASE_PATH
