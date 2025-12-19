"""
모델 정의:
    * id: Integer, PK
    * user_id: Integer, FK (User)
    * role: String ("user" | "assistant" | "system") - Enum 사용 권장
    * content: Text (메시지 내용)
    * created_at: DateTime (생성 시간)
    * is_deleted: Boolean (소프트 삭제용)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from enum import Enum

# class ChatRole(Enum) 일 때
#   print(ChatRole.USER == "user")  -> False
# class ChatRole(str, Enum):
#   print(ChatRole.USER == "user")  -> True
# Enum의 타입 안정성 + 문자열처럼 동작
class ChatRole(str, Enum):
    USER = "user",
    ASSISTANT = "assistant",
    SYSTEM = "system"
    
class ChatHistory(Base):
    __tablename__ = "chat_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False, comment="발신자 역할(user, assistant, system)")
    content = Column(Text, nullable=False, comment="메시지 내용")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    user = relationship("User", back_populates="chats")