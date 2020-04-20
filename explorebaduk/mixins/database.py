from explorebaduk.database import BaseModel, TokenModel, UserModel, GameModel, GamePlayerModel, db


class DatabaseMixin:
    db_model: BaseModel = None
    columns = []

    def create_model(self):
        self.model = None
        data = {col: getattr(self, col) for col in self.columns}
        self.model = self.db_model(**data)

    def save(self):
        if not self.model:
            self.create_model()
        db.save(self.model)

    def delete(self):
        if self.model:
            db.delete(self.model)
