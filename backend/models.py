from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from backend.database import SourceBase, EvalBase, HitlEvalBase, ConfigBase
import uuid
import datetime

# --- Source Models (Read Only) ---

class Chat(SourceBase):
    __tablename__ = 'chat'
    __table_args__ = {'schema': 'chats'}

    id = Column(Integer, primary_key=True)
    displayName = Column(String)
    msg_metadata = Column("metadata", JSONB)
    closedAt = Column(DateTime)
    updatedAt = Column(DateTime)
    createdAt = Column(DateTime)
    assignedToId = Column(UUID(as_uuid=True))
    customerId = Column(UUID(as_uuid=True))

    # messages = relationship("Message", back_populates="chat")

class Message(SourceBase):
    __tablename__ = 'message'
    __table_args__ = {'schema': 'chats'}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatId = Column(Integer) # ForeignKey('chats.chat.id') but we might not want to enforce it if strict consistency isn't guaranteed
    text = Column(String)
    createdAt = Column(DateTime)
    author = Column(JSON)
    attachmentId = Column(UUID(as_uuid=True)) # Added for image resolution
    
    # chat = relationship("Chat", back_populates="messages")

class Account(SourceBase):
    __tablename__ = 'account'
    __table_args__ = {'schema': 'core'}

    id = Column(UUID(as_uuid=True), primary_key=True)
    pushName = Column(String)

class Attachment(SourceBase):
    __tablename__ = 'attachment'
    __table_args__ = {'schema': 'core'}

    id = Column(UUID(as_uuid=True), primary_key=True)
    path = Column(String)
    mimetype = Column(String)
    # Add other fields if needed, but path is critical



# --- Evaluation Models (Write) ---

class Evaluation(EvalBase):
    __tablename__ = 'evaluations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, nullable=False) # Maps to Chat.id
    score = Column(String, nullable=False) # horrible, bad, neutral, good, great
    reason = Column(String(500), nullable=False)
    improvement = Column(String(800), nullable=False)
    key_messages = Column(JSON, nullable=True) # List of message indices/IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class HitlEvaluation(HitlEvalBase):
    __tablename__ = 'hitl_evaluations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, nullable=False) # Maps to Chat.id
    score = Column(String, nullable=False) # horrible, bad, neutral, good, great
    reason = Column(String(500), nullable=False)
    improvement = Column(String(800), nullable=False)
    key_messages = Column(JSON, nullable=True) # List of message indices/IDs
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class User(EvalBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)

# --- Configuration Models (Isolated) ---

class SystemPrompt(ConfigBase):
    __tablename__ = 'system_prompts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False) # Encrypted
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Manual(ConfigBase):
    __tablename__ = 'manuals'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False) # Encrypted
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ActiveConfig(ConfigBase):
    __tablename__ = 'active_config'
    id = Column(Integer, primary_key=True) # Singleton, always 1
    active_prompt_id = Column(Integer, ForeignKey('system_prompts.id'), nullable=True)
    active_manual_id = Column(Integer, ForeignKey('manuals.id'), nullable=True)
