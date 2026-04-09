from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from categorize import categorize
from models import Base, Todo

DATABASE_URL = "sqlite+aiosqlite:///./todos.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


class AddTodoRequest(BaseModel):
    title: str


class TodoResponse(BaseModel):
    id: int
    title: str
    category: str
    done: bool


@app.post("/api/add_todo", response_model=TodoResponse)
async def add_todo(req: AddTodoRequest):
    category = await categorize(req.title)
    todo = Todo(title=req.title, category=category, done=False)
    async with async_session() as session:
        session.add(todo)
        await session.commit()
        await session.refresh(todo)
        return TodoResponse(id=todo.id, title=todo.title, category=todo.category, done=todo.done)


@app.get("/api/get_todos", response_model=list[TodoResponse])
async def get_todos():
    async with async_session() as session:
        result = await session.execute(select(Todo))
        todos = result.scalars().all()
        return [TodoResponse(id=t.id, title=t.title, category=t.category, done=t.done) for t in todos]


# Serve built React frontend
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(FRONTEND_DIR / "index.html")
