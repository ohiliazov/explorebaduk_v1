from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class TokenModel(BaseModel):
    __tablename__ = "signin_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    token = Column(String(64))
    expire = Column(DateTime)

    user = relationship("UserModel", back_populates="tokens")
