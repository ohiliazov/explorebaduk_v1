import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from explorebaduk.database.base import BaseModel


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    token_id = Column(Integer, primary_key=True, name="SignIn_Token_ID")
    user_id = Column(Integer, ForeignKey("users.User_ID"))
    token = Column(String(64))
    expired_at = Column(DateTime)

    player = relationship("PlayerModel", back_populates="tokens")

    @property
    def is_active(self):
        return datetime.datetime.utcnow() < self.expired_at
