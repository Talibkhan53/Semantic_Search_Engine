# Semantic Search Engine

A Python-based semantic search engine that finds text files related to a user's query by comparing sentence embeddings. The project began as a custom implementation of the semantic-search pipeline and now exposes its core functionality through a FastAPI web API.

## Features

- Load `.txt` files from a directory
- Split document text into chunks
- Generate text embeddings with Sentence Transformers
- Persist embeddings and file metadata in a local JSON-based vector store
- Reuse existing embeddings and refresh the index when files change
- Detect newly added and deleted files
- Compare query embeddings with document embeddings using cosine similarity
- Rank results and return the most relevant files
- Expose health, document-loading, and search endpoints through FastAPI
- Keep the code separated into loader, chunking, embedding, storage, search, and API modules

## How It Works

1. The loader reads supported text files from the selected directory.
2. The chunking component splits each document into smaller text segments.
3. The embedding model converts each chunk into a numerical vector.
4. The vector store saves the vectors and associated file metadata locally.
5. A search query is converted into an embedding using the same model.
6. The search component compares the query embedding with stored chunk embeddings using cosine similarity.
7. Results are ranked and returned to the caller.

When a directory is indexed again, the service checks for changed, new, and deleted files so it can update the stored data rather than always rebuilding the whole index.

## Tech Stack

- **Python** — application logic
- **FastAPI** — HTTP API
- **Uvicorn** — ASGI server for running the API
- **Sentence Transformers** — text embedding model
- **NumPy** — numerical operations
- **JSON** — current local persistence format
- **Pydantic** — request-body validation

## Embedding Model

The project uses `all-MiniLM-L6-v2` through Sentence Transformers. It maps text to dense numerical vectors so semantically related text can have similar vector representations.

## Project Structure

```text
Search Engine/
├── api/
│   └── routes/
│       ├── dependencies.py   # Shared SearchEngine instance
│       ├── documents.py      # Document indexing endpoint
│       ├── health.py         # Health endpoint
│       └── search.py         # Search endpoint and request validation
├── Chunking/                 # Text chunking
├── Data/                     # Example .txt documents
├── Embeddings/               # Sentence embedding generation
├── Loader/                   # Text-file loading
├── Result/                   # Search-result display and result model
├── Search/                   # Semantic search orchestration
├── Services/                 # SearchEngine workflow
├── Similarity/               # Similarity calculation
├── System/                   # Original command-line entry point
├── VectorStore/              # JSON-based vector persistence
├── main.py                   # FastAPI application entry point
└── requirements.txt
```

## Installation

Use Python 3.10 or later in a virtual environment. From the project directory, create and activate the environment on Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the API and semantic-search dependencies:

```bash
python -m pip install fastapi "uvicorn[standard]" numpy sentence-transformers
```

> The first run of Sentence Transformers may download the embedding model, so an internet connection may be required initially.

## Run the API

From the project root—the directory containing `main.py`—run:

```bash
python -m uvicorn main:app --reload
```

The local API will be available at `http://127.0.0.1:8000`.

### Interactive API documentation

Open `http://127.0.0.1:8000/docs` to try the endpoints using Swagger UI.

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check that the API is running. |
| `POST` | `/load?path=...` | Index or refresh `.txt` files in a directory. |
| `POST` | `/search` | Search a directory and return ranked results. |

#### 1. Health check

```http
GET /health
```

Example response:

```json
{
  "Status": "Healthy"
}
```

#### 2. Load documents

Send the directory path as a query parameter. For example, when running locally on Windows:

```http
POST /load?path=D%3A%5CProjects%5CSemantic_Search_Engine%5CData
```

Use your own absolute directory path. The directory must exist and contain at least one `.txt` file.

A successful response reports the indexing status, directory, number of indexed file entries, and file names.

#### 3. Search documents

Send a JSON request body to `POST /search`:

```json
{
  "path": "D:\\Projects\\Semantic_Search_Engine\\Data",
  "query": "What is Python?",
  "top_k": 3
}
```

Fields:

- `path` — directory containing the `.txt` files
- `query` — search text; must contain at least three non-whitespace characters
- `top_k` — number of results requested, from `1` to `20` (defaults to `3`)

The response contains the normalized query, result count, and ranked results with file names and similarity scores. The search workflow also prepares or refreshes the index as needed, so calling `/load` first is not strictly required for a search.

## Run the Original CLI

The original command-line workflow is also available:

```bash
python System/system.py
```

Follow the prompts to enter a directory path and a search query.

## Current Storage Design

The current vector store is a custom JSON-based implementation. It stores embeddings and file metadata locally and is useful for learning how indexing and persistence work. It is not a dedicated vector database; moving the persistence and similarity-search layer to ChromaDB is a planned improvement.

## Current Limitations

- Input documents are currently limited to `.txt` files.
- The JSON file is a simple local store and may become inefficient as the collection grows.
- Search scores measure vector similarity; they are not a guarantee that a result answers the query correctly.
- The API currently accepts a local filesystem path, so it is intended for trusted local use. A public deployment should not expose arbitrary server paths without access controls and stricter path restrictions.
- Automated API tests and deployment configuration are still to be added.

## Roadmap

- Complete API smoke tests and error-case tests
- Keep dependency declarations clean and reproducible
- Replace JSON-based vector persistence with ChromaDB
- Preserve file metadata and incremental indexing during the storage migration
- Add automated tests for loading, updates, deletion, and search
- Deploy the API with appropriate path restrictions and configuration

## What This Project Demonstrates

- Python modular design and object-oriented programming
- Text preprocessing and chunking
- Dense vector embeddings
- Cosine similarity and ranking
- Incremental indexing and local persistence
- Request validation and error handling with FastAPI and Pydantic
- Separating API routes from the underlying search-engine workflow

## License

Created for learning and educational purposes.
