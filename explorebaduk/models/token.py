import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String(64), name="Token")
    expired_at = Column(DateTime, name="Expire")

    user = relationship("UserModel", back_populates="tokens")

    @property
    def is_active(self):
        return datetime.datetime.utcnow() < self.expired_at
