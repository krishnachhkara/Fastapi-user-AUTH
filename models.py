from sqlalchemy import String,Integer,DateTime,func
from .database import Base
from sqlalchemy.orm import mapped_column,Mapped
from datetime import datetime



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    email: Mapped[str] = mapped_column(String(255),nullable=False,unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column(String(255),nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now(),index=True)
    role: Mapped[str] = mapped_column(
        String(50),
        default="user",#so that every new user gets basic functionality
        nullable=False
    )