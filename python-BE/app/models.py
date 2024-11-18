from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="documents")