import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Boolean
from db.database import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                     default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(32), unique=True,
                                          nullable=False)
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 default=func.now(),
                                                 nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime,
                                                 server_default=func.now(),
                                                 onupdate=func.now())
    secret_key: Mapped[str] = mapped_column(String(128), nullable=False)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False,
                                              nullable=False)

    notes: Mapped[list["Note"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
