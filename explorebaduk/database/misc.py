from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    Text,
    ForeignKey,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


from explorebaduk.database.base import BaseModel


class NotificationTypeModel(BaseModel):
    __tablename__ = "notification_types"

    notification_type_id = Column(Integer, name="Notification_Type_ID", primary_key=True)
    notification_type = Column(Integer, name="Notification_Type", nullable=False)


class NotificationModel(BaseModel):
    __tablename__ = "notifications"

    notification_id = Column(Integer, name="Notification_ID", primary_key=True)
    notification_type_id = Column(Integer, name="Notification_Type", nullable=False)

    sender = Column(Integer, name="Sender", nullable=False)
    receiver = Column(Integer, name="Receiver", nullable=False)
    added = Column(DateTime, name="Added", nullable=False)
    content = Column(Text, name="Content")
    status = Column(Integer, name="Status", nullable=False, default=0)


class FriendModel(BaseModel):
    __tablename__ = "friends"

    id = Column(Integer, name="ID", primary_key=True)
    user_id = Column(Integer, name="User_ID", nullable=False)
    friend_id = Column(Integer, name="Friend_ID", nullable=False)
    muted = Column(Boolean, name="Muted", default=False)
    blocked = Column(Boolean, name="Blocked", default=False)


class MessageModel(BaseModel):
    __tablename__ = "messages"

    message_id = Column(Integer, name="Message_ID", primary_key=True)
    message = Column(Text(collation="utf8mb4"), name="Message", nullable=False)
    sender = Column(Integer, name="Sender", nullable=False)
    receiver = Column(Integer, name="Receiver", nullable=False)
    sent = Column(Integer, name="Sent", nullable=False)


class SocialPostModel(BaseModel):
    __tablename__ = "social_posts"

    post_id = Column(Integer, name="Post_ID", primary_key=True)
    user_id = Column(Integer, name="User_ID", nullable=False)
    content = Column(Text(collation="utf8mb4"), name="Content", nullable=False)
    likes = Column(Integer, name="Likes", nullable=False, default=0)
    posted = Column(DateTime, name="Posted", nullable=False)


class SocialCommentModel(BaseModel):
    __tablename__ = "social_comments"

    comment_id = Column(Integer, name="Comment_ID", primary_key=True)
    content = Column(Text(collation="utf8mb4"), name="Content", nullable=False)
    posted = Column(DateTime, name="Posted", nullable=False)
    likes = Column(Integer, name="Likes", nullable=False, default=0)
    user_id = Column(Integer, name="User_ID", nullable=False)
    post_id = Column(Integer, name="Post_ID", nullable=False)


class SocialPostLikeModel(BaseModel):
    __tablename__ = "social_comments_likes"

    id = Column(Integer, name="ID", primary_key=True)
    post_id = Column(Integer, name="Post_ID", nullable=False)
    user_id = Column(Integer, name="User_ID", nullable=False)


class SocialCommentLikeModel(BaseModel):
    __tablename__ = "social_comments_likes"

    id = Column(Integer, name="ID", primary_key=True)
    comment_id = Column(Integer, name="Comment_ID", nullable=False)
    user_id = Column(Integer, name="User_ID", nullable=False)


class SubscriptionPlanModel(BaseModel):
    __tablename__ = "subscription_plans"

    id = Column(Integer, name="ID", primary_key=True)
    plan = Column(String(255), name="Plan", nullable=False)
    title = Column(String(255), name="Title", nullable=False)
    price = Column(Numeric(6, 2), name="Price", nullable=False)
    description = Column(Text, name="Description", nullable=False)


class TeacherBiographyModel(BaseModel):
    __tablename__ = "teachers_biographies"

    id = Column(Integer, name="ID", primary_key=True)
    teacher_id = Column(Integer, name="Teacher_ID", nullable=False)
    biography = Column(Text, name="Biography", nullable=False)


class TeacherPayPalModel(BaseModel):
    __tablename__ = "teachers_paypals"

    id = Column(Integer, name="ID", primary_key=True)
    teacher_id = Column(Integer, name="Teacher_ID", nullable=False)
    paypal = Column(String(255), name="PayPal", nullable=False)


class TeacherPlansModel(BaseModel):
    __tablename__ = "teachers_plans"

    id = Column(Integer, name="ID", primary_key=True)
    teacher_id = Column(Integer, name="Teacher_ID", nullable=False)
    plan = Column(String(255), name="Plan", nullable=False)
    price = Column(Numeric(6, 2), name="Price", nullable=False)


# TODO: add users table + update signin_token table