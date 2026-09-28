# Semantic Search Engine

A lightweight semantic search engine built from scratch in Python using **Sentence Transformers and NumPy**.

The project takes a directory of text files, converts their contents into vector embeddings, stores those embeddings locally, and uses **cosine similarity** to find the documents most relevant to a user's query.

The project focuses on understanding the core concepts behind semantic search and vector-based retrieval rather than relying on frameworks such as LangChain or external vector databases.

## Features

* Load text files from a directory
* Generate semantic embeddings using `all-MiniLM-L6-v2`
* Store embeddings locally in JSON
* Store the source path and file name with each embedding
* Detect whether a directory has already been indexed
* Reuse previously generated embeddings
* Calculate cosine similarity using NumPy
* Rank search results by similarity score
* Return Top-K search results
* Use a structured `SearchResult` object
* Separate search logic from result display
* Modular architecture with separate components for loading, embedding, storage, similarity, and searching

## Architecture

```text
                         system.py
                             |
                             v
                       SearchEngine
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
       Loader            Embedding        VectorStore
                                               |
                                        path_exists()
                                               |
                                  +------------+------------+
                                  |                         |
                                YES                        NO
                                  |                         |
                                  v                         v
                          load_embeddings()             Loader
                                                            |
                                                            v
                                                        Embedding
                                                            |
                                                            v
                                                     store vectors
                                  |                         |
                                  +------------+------------+
                                               |
                                               v
                                       SemanticSearch
                                               |
                                               v
                                          Similarity
                                               |
                                               v
                                        SearchResult
                                               |
                                               v
                                            Display
```

## Project Structure

```text
Search Engine/
│
├── Data/
│   ├── cat.txt
│   ├── got.txt
│   ├── llm.txt
│   └── python.txt
│
├── Embeddings/
│   └── embedding.py
│
├── Loader/
│   └── loader.py
│
├── Result/
│   ├── display.py
│   └── result.py
│
├── Search/
│   ├── search_engine.py
│   └── semantic_search.py
│
├── Similarity/
│   └── similarity.py
│
├── System/
│   └── system.py
│
├── VectorStore/
│   └── vector_store.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## How It Works

### 1. User provides a directory

For example:

```text
D:\Projects\Search Engine\Data
```

The system checks whether this directory has already been indexed.

### 2. If the directory has not been indexed

The system:

```text
Directory
    ↓
Loader
    ↓
Text files
    ↓
Embedding Model
    ↓
Vector embeddings
    ↓
VectorStore
```

The embeddings are stored locally together with the original path and file name.

### 3. If the directory has already been indexed

The system loads the existing embeddings instead of generating them again.

```text
Directory
    ↓
VectorStore
    ↓
Existing embeddings
```

This avoids unnecessary embedding computation.

### 4. Query embedding

The user's query is passed through the same embedding model.

```text
"What is Python?"
        ↓
Embedding Model
        ↓
Query Vector
```

### 5. Similarity calculation

The query vector is compared with the stored document vectors using cosine similarity.

The basic formula is:

```text
                 A · B
cosine similarity = ---------
                   ||A|| ||B||
```

A higher value means the vectors point in a more similar direction.

### 6. Ranking

The similarity scores are sorted from highest to lowest.

Example:

```text
Rank    File                 Score
---------------------------------------
1       python.txt           0.73
2       llm.txt              0.42
3       cat.txt              0.18
```

Only the requested Top-K results are returned.

## Technologies

* **Python**
* **NumPy**
* **Sentence Transformers**
* **JSON**
* **Object-Oriented Programming**
* **Cosine Similarity**
* **Vector Embeddings**

## Installation

Clone the repository:

```bash
git clone <YOUR-REPOSITORY-URL>
```

Enter the project directory:

```bash
cd "Search Engine"
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

From the project root:

```bash
python System/system.py
```

Enter the directory containing your text files:

```text
Enter Path: D:\Projects\Search Engine\Data
```

Then enter a query:

```text
Enter Your Question: What is Python?
```

The system will return the most semantically similar documents.

## Example

```text
Enter Path: D:\Projects\Search Engine\Data
Enter Your Question: What is Python?

Path already indexed.

Query: What is Python?

Rank    File                Score
--------------------------------------
1       python.txt          0.73
2       llm.txt             0.42
3       cat.txt             0.18
```

The exact scores will vary depending on the contents of the documents and embedding model.

## Why This Project?

The purpose of this project is to understand the fundamental components behind semantic retrieval:

```text
Documents
   ↓
Embeddings
   ↓
Vector Storage
   ↓
Query Embedding
   ↓
Similarity Search
   ↓
Ranked Results
```

Rather than hiding these concepts behind a high-level framework, the project implements the retrieval pipeline directly.

## Future Improvements

Possible future improvements include:

* Text chunking
* Metadata for individual chunks
* Incremental indexing when files change
* Search evaluation and Top-1/Top-K accuracy
* Similarity score thresholds
* Batch embedding
* Better handling of different file types
* Persistent metadata management
* LLM-based answer generation using retrieved documents

## Current Limitations

* The current loader focuses on text files.
* Embeddings are stored in a JSON file rather than a dedicated vector database.
* The entire document is embedded as one vector.
* Changes inside already-indexed files are not currently detected automatically.
* Search results contain document-level similarity rather than chunk-level similarity.

## License

This project is provided for learning and educational purposes.
