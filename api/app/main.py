from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.chat import RAGService, Answer


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag = RAGService()
    yield
    app.state.rag.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


@app.post("/ask_query", response_model=Answer)
def ask_query(body: Query):
    try:
        return app.state.rag.ask(body.question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))