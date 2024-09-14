from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Define SQLAlchemy Base
Base = declarative_base()

# Define the 'conversations' table
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Define the relationship to the Messages model
    messages = relationship("Messages", back_populates="conversation", cascade="all, delete-orphan")

class Messages(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    data = Column(String)

    conversation = relationship("Conversation", back_populates="messages")