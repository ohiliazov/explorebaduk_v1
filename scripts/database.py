import argparse
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from explorebaduk.models import BaseModel
from explorebaduk.utils.database import (
    generate_blocked_users,
    generate_friends,
    generate_tokens,
    generate_users,
)


def populate_database_with_data(
    session,
    num_users: int = 100,
    num_friends: int = 20,
    num_blocked: int = 5,
):
    users = generate_users(session, num_users)
    generate_tokens(session, users)

    friends = generate_friends(session, users, num_friends)
    generate_blocked_users(session, users, num_blocked, friends)


def create_db(database_uri, clean: bool = False):
    engine = create_engine(database_uri)
    session = create_session(engine)

    if clean:
        BaseModel.metadata.drop_all(engine)
        BaseModel.metadata.create_all(engine)

    populate_database_with_data(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-uri",
        type=str,
        help="Database URI",
        default=os.getenv("DATABASE_URI"),
        nargs=1,
    )
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()
    create_db(args.database_uri, args.clean)
