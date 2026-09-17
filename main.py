from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated

app = FastAPI()


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str


class Note(NoteCreate):
    id: int
    created_at: datetime
    updated_at: datetime


next_id: int = 1
notesDB: dict[int, Note] = {}


@app.post("/notes", response_model=Note, status_code=201)
async def create_note(note: NoteCreate):
    global next_id
    new_note = Note(
        id=next_id,
        title=note.title,
        content=note.content,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    notesDB[next_id] = new_note
    next_id += 1
    return new_note


@app.get("/notes", response_model=list[Note])
async def get_notes():
    return list(notesDB.values())


@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: Annotated[int, Path(ge=1)]):
    if note_id not in notesDB:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    return notesDB[note_id]


@app.put("/notes/{note_id}", response_model=Note)
async def edit_note(note_id: Annotated[int, Path(ge=1)], note: NoteCreate):
    if note_id not in notesDB:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    notesDB[note_id] = Note(
        id=notesDB[note_id].id,
        title=note.title,
        content=note.content,
        created_at=notesDB[note_id].created_at,
        updated_at=datetime.now(),
    )
    return notesDB[note_id]


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: Annotated[int, Path(ge=1)]):
    if note_id not in notesDB:
        raise HTTPException(
            status_code=404, detail=f"Заметка с {note_id} ID не найдена!"
        )
    del notesDB[note_id]
