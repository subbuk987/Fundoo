from typing import List
from uuid import UUID

from sqlalchemy.orm import Session
from models.note import Note
from models.label import Label
from schema.note_schema import NoteCreate
from models.user import User


class NoteQueries:

    @staticmethod
    def get_or_create_label(db: Session, label_name: str) -> Label:
        label = db.query(Label).filter_by(name=label_name.strip()).first()
        if label:
            return label
        new_label = Label(name=label_name.strip())
        db.add(new_label)
        db.commit()
        db.refresh(new_label)
        return new_label

    @staticmethod
    def get_all_labels(db: Session) -> list[Label]:
        return db.query(Label).all()

    @staticmethod
    def create_note(db: Session, user: User, note_data: NoteCreate) -> Note:
        labels = [NoteQueries.get_or_create_label(db, name) for name in
                  note_data.labels]

        note = Note(
            title=note_data.title,
            content=note_data.content,
            user_id=user.id,
            labels=labels
        )

        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_user_notes(db: Session, user: User) -> List[Note]:
        return db.query(Note).filter(Note.user_id == user.id).all()

    @staticmethod
    def get_note_by_id(db: Session, note_id: UUID, user: User) -> Note | None:
        return db.query(Note).filter(Note.id == note_id,
                                     Note.user_id == user.id).first()

    @staticmethod
    def delete_note(db: Session, note: Note):
        db.delete(note)
        db.commit()

    @staticmethod
    def update_note(db: Session, note: Note, note_data: NoteCreate):
        note.title = note_data.title
        note.content = note_data.content
        note.labels = [NoteQueries.get_or_create_label(db, name) for name in
                       note_data.labels]
        db.commit()
        db.refresh(note)
        return note
