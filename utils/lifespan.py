from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import init_db



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Closing DB Connection")



