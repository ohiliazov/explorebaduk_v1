import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from explorebaduk.models.base import BaseModel


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    token_id = Column(Integer, primary_key=True, name="ID")
    user_id = Column(Integer, ForeignKey("users.User_ID"), name="User_ID")
    token = Column(String(64), name="Token")
    expired_at = Column(DateTime, name="Expire")

    user = relationship("UserModel", back_populates="tokens")

    @property
    def is_active(self):
        return datetime.datetime.utcnow() < self.expired_at
