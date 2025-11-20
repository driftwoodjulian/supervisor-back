from .session import db
from sqlalchemy.dialects.postgresql import JSONB, UUID


class Chat(db.Model):
    __tablename__ = "chat"
    __table_args__ = {"schema": "chats"}

    id = db.Column(db.Integer, primary_key=True)  # <-- integer, not UUID
    displayName = db.Column(db.String, nullable=False)
    msg_metadata = db.Column("metadata", JSONB)   # map to metadata column
    closedAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime, nullable=False)
    assignedToId = db.Column(UUID(as_uuid=True))
    customerId = db.Column(UUID(as_uuid=True), nullable=False)
