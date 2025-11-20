from .session import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Message(db.Model):
    __tablename__ = "message"
    __table_args__ = {"schema": "chats"}

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    chatId = db.Column(db.Integer)
    text = db.Column(db.String)
    createdAt = db.Column(db.DateTime)
    author = db.Column(db.JSON)


    