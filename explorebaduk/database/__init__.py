from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import DATABASE_URI
from explorebaduk.database.base import BaseModel
from explorebaduk.database.token import TokenModel
from explorebaduk.database.user import UserModel
from explorebaduk.database.game import GameModel, GamePlayerModel


class DatabaseHandler:
    def __init__(self, database_uri: str):
        self.engine = create_engine(database_uri)
        self.session = Session(self.engine, autocommit=True)

    def get_by_id(self, model: BaseModel, key):
        return self.session.query(model).get(key)

    def query(self, model: BaseModel, **filters):
        query = self.session.query(model)

        if filters:
            query = query.filter_by(**filters)

        return query

    def fetch_one(self, model: BaseModel, **filters):
        return self.query(model, **filters).first()

    def save(self, instance: BaseModel):
        self.session.add(instance)
        self.session.flush()
        # try:
        #     self.session.commit()
        # except SQLAlchemyError:
        #     self.session.rollback()

    def delete(self, instance: BaseModel):
        self.session.delete(instance)
        self.session.flush()
        # try:
        #     self.session.commit()
        # except SQLAlchemyError:
        #     self.session.rollback()

    def select_token(self, token: str) -> TokenModel:
        return self.fetch_one(TokenModel, token=token)

    def select_user(self, user_id: int) -> UserModel:
        return self.get_by_id(UserModel, user_id)

    def select_game(self, game_id: int) -> GameModel:
        return self.get_by_id(GameModel, game_id)

    def insert_game(self, name, width, height, started_at, sgf) -> int:
        game_model = GameModel(name=name, width=width, height=height, started_at=started_at, sgf=sgf)
        self.save(game_model)
        return game_model.game_id

    def update_game(self, game_id) -> GameModel:
        # TODO: make actual update
        return self.select_game(game_id)

    def select_game_player(self) -> GamePlayerModel:
        pass

    def insert_game_player(self) -> GamePlayerModel:
        pass

    def update_game_player(self) -> GamePlayerModel:
        pass
