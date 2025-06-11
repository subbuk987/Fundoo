from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from db.database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'

    id: Mapped[Integer] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True,
                                          nullable=False)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 default=func.now(),
                                                 nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.now())
