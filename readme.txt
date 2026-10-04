# Semantic Search Engine

A simple semantic search engine built with Python. It uses sentence embeddings and cosine similarity to find documents that are semantically related to a user's query.

The project was built to understand how semantic search works internally without using frameworks such as LangChain or external vector databases.

## Features

- Load text files from a directory
- Generate embeddings using Sentence Transformers
- Store embeddings locally in JSON
- Reuse existing embeddings
- Detect and update existing stored embeddings
- Convert user queries into embeddings
- Calculate cosine similarity
- Rank search results by similarity score
- Return relevant documents
- Modular project structure

## How It Works

The system follows this basic process:

1. Load documents from a directory.
2. Generate embeddings for the documents.
3. Store the embeddings in the local vector store.
4. Take the user's search query.
5. Generate an embedding for the query.
6. Compare the query embedding with stored document embeddings.
7. Calculate cosine similarity.
8. Sort the results based on similarity score.
9. Display the most relevant results.

## Project Structure

```text
Semantic_Search_Engine/
│
├── Data/
├── Embeddings/
├── Loader/
├── Result/
├── Search/
├── Similarity/
├── System/
├── VectorStore/
│
├── .gitignore
├── README.md
├── requirements.txt
└── execptions.py
```

## Technologies Used

- Python
- NumPy
- Sentence Transformers
- JSON
- Object-Oriented Programming

## Embedding Model

The project currently uses:

```text
all-MiniLM-L6-v2
```

The model converts documents and search queries into numerical vectors that can be compared based on their semantic meaning.

## Vector Store

The project uses a custom local vector store instead of an external vector database.

The vector store is responsible for:

- Storing document embeddings
- Storing file information
- Loading existing embeddings
- Reusing existing embeddings
- Updating embeddings when required

This was implemented to understand how a basic vector store works internally.

## Search

The search system uses cosine similarity to compare the query embedding with document embeddings.

A higher similarity score means that the document is more semantically related to the query.

Example:

```text
Query: What is Python?

python.txt    0.73
llm.txt       0.42
cat.txt       0.18
```

The results are sorted from highest to lowest similarity score.

## Installation

Clone the repository:

```bash
git clone https://github.com/Talibkhan53/Semantic_Search_Engine.git
```

Go to the project directory:

```bash
cd Semantic_Search_Engine
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

Run:

```bash
python System/system.py
```

Enter the path containing your text files and then enter your search query.

## Example

```text
Enter Path: D:\Projects\Semantic_Search_Engine\Data

Enter Your Question: What is Python?

Results:

python.txt
Score: 0.73

llm.txt
Score: 0.42

cat.txt
Score: 0.18
```

## What I Learned

While building this project, I worked with:

- Text processing
- Python modules and packages
- Object-oriented programming
- NumPy arrays
- Sentence embeddings
- Vector representations
- Cosine similarity
- Semantic search
- JSON data storage
- Incremental embedding updates
- Building a simple vector store from scratch

## Future Improvements

Some possible improvements are:

- Document chunking
- Chunk-level embeddings
- Support for more file formats
- Better indexing
- Search filters
- Hybrid keyword and semantic search
- Search evaluation
- Reranking
- LLM-based answers

## Project Status

The core semantic search system is implemented.

The project will continue to be improved by enhancing the existing components and gradually adding useful search capabilities.

## License

This project is created for learning and educational purposes.