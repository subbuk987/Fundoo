import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
from models.note_label import note_label_association


class Label(Base):
    __tablename__ = "labels"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                                     default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


    notes: Mapped[list["Note"]] = relationship(
        secondary=note_label_association,
        back_populates="labels",
        passive_deletes=True
    )
