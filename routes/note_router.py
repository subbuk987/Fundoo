from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from db.database import get_db
from db.redis import cache_user_labels, cache_user_notes, get_cached_notes
from models.user import User
from queries.note_queries import NoteQueries
from schema.note_schema import (LabelRead, NoteCreate, NoteRead,
                                NoteSuccessResponse)

note_router = APIRouter(
    tags=["notes"],
)


@note_router.post("/", response_model=NoteSuccessResponse)
async def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    note = NoteQueries.create_note(db, current_user, note_data)
    # Update cache
    notes = NoteQueries.get_user_notes(db, current_user)
    labels = NoteQueries.get_all_labels(db)
    await cache_user_labels(
        current_user.username,
        [LabelRead.model_validate(l).model_dump() for l in labels],
    )
    await cache_user_notes(
        current_user.username, [NoteRead.model_validate(n).model_dump() for n in notes]
    )
    return NoteSuccessResponse(
        message="Note Created Successfully",
        payload=NoteRead.model_validate(note),
        status_code=status.HTTP_201_CREATED,
    )


@note_router.get("/", response_model=list[NoteRead])
async def get_notes(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    cached_notes = await get_cached_notes(current_user.username)
    if cached_notes:
        return [NoteRead(**n) for n in cached_notes]

    notes = NoteQueries.get_user_notes(db, current_user)
    return [NoteRead.model_validate(note) for note in notes]


@note_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    note = NoteQueries.get_note_by_id(db, note_id, current_user)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    NoteQueries.delete_note(db, note)
    # Update cache
    notes = NoteQueries.get_user_notes(db, current_user)
    labels = NoteQueries.get_all_labels(db)
    await cache_user_labels(
        current_user.username,
        [LabelRead.model_validate(l).model_dump() for l in labels],
    )
    await cache_user_notes(
        current_user.username, [NoteRead.model_validate(n).model_dump() for n in notes]
    )


@note_router.patch("/{note_id}", response_model=NoteSuccessResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    note = NoteQueries.get_note_by_id(db, note_id, current_user)

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    updated = NoteQueries.update_note(db, note, note_data)
    # Update cache
    notes = NoteQueries.get_user_notes(db, current_user)
    labels = NoteQueries.get_all_labels(db)
    await cache_user_labels(
        current_user.username,
        [LabelRead.model_validate(l).model_dump() for l in labels],
    )
    await cache_user_notes(
        current_user.username, [NoteRead.model_validate(n).model_dump() for n in notes]
    )
    return NoteSuccessResponse(
        message="Note Updated Successfully",
        payload=NoteRead.model_validate(updated),
        status_code=status.HTTP_200_OK,
    )
