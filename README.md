# clause-rag

A chat assistant that answers questions from the Clause shop handbook. You ask in a web chat, the API looks up the relevant passages in the handbook PDF, and a local model writes the answer. Each answer comes back with the pages it was based on.

Everything runs locally through Ollama, so there are no API keys and no usage costs.

![Architecture](docs/architecture.png)

## How it works

1. `ingestion.py` loads the handbook PDF, splits it into chunks, embeds them with `nomic-embed-text` and stores them in a local Qdrant collection.
2. The Next.js page sends the question to `POST /ask_query`.
3. `chat.py` embeds the question, pulls the closest chunks from Qdrant and drops anything below a similarity score of 0.35. If nothing is left, it replies that the handbook doesn't cover the topic and skips the model call.
4. Otherwise the chunks go to the chat model as context, and the answer is returned together with the source file, page and score of each chunk.

## Stack

- API: FastAPI, LangChain, Qdrant (local mode)
- Web: Next.js 16, plain CSS modules
- Models: Ollama (`gemma3:1b` for chat, `nomic-embed-text` for embeddings)
- Python packages managed with uv

## Project layout

```
api/
  app/
    main.py            FastAPI app, /ask_query endpoint
    cli.py             terminal chat
    core/config.py     settings
    services/
      ingestion.py     PDF -> chunks -> Qdrant
      chat.py          retrieval + answer
  data/                put the handbook PDF here
web/
  app/page.tsx         chat UI
```

## Setup

You need Python 3.13, uv, Node.js and Ollama.

Pull the models:

```bash
ollama pull gemma3:1b
ollama pull nomic-embed-text
```

Put the handbook at `api/data/shop_handbook.pdf`. The PDF isn't tracked in git.

Install the API dependencies:

```bash
cd api
uv sync
```

Index the handbook (run this once, and again whenever the PDF changes):

```bash
uv run python -c "from app.services.ingestion import ingest; print(ingest())"
```

Qdrant runs in local mode and only lets one process open `qdrant_data` at a time, so stop the server before ingesting.

## Running

API, from the `api` folder:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Web, in a second terminal:

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000. Swagger docs for the API are at http://localhost:8000/docs.

Run all commands from `api/`, because the PDF and Qdrant paths in the config are relative.

## API

`POST /ask_query`

```json
{ "question": "What is the return policy?" }
```

Response:

```json
{
  "answer": "...",
  "sources": [
    { "source": "data/shop_handbook.pdf", "page": 3, "score": 0.71 }
  ]
}
```

Page numbers are zero-based, the UI adds 1 when it shows them.

## Configuration

Settings live in `api/app/core/config.py` and can be overridden with environment variables prefixed with `RAG_`, either in the shell or in `api/.env`. See `api/env/.env.example`.

```
RAG_CHAT_MODEL=llama3.2:1b
RAG_CHUNK_SIZE=600
RAG_CHUNK_OVERLAP=100
```

Restart the server after changing them, the settings are cached.

## Notes

- The 0.35 score cutoff in `chat.py` is a starting value. Print the scores for a few good and bad questions and adjust it.
- Before deploying, move the API URL in `page.tsx` into an environment variable and add the deployed web address to the CORS list in `main.py`.
