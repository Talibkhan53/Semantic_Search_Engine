
from pathlib import Path
import logging

from Loader.loader import Loader
from Embeddings.embedding import Embedding
from Chunking.chunking import Chunking
from VectorStore.vector_store import VectorStore
from Search.semantic_search import SemanticSearch
from Result.display import Display

logger = logging.getLogger(__name__)


class SearchEngine:

    def __init__(self):
        self.loader = Loader()
        self.chunking = Chunking()
        self.embedding = Embedding()
        self.vector_store = VectorStore()
        self.semantic_search = SemanticSearch(
            self.vector_store
        )
        self.display = Display()

    def prepare_data(
        self, path: str | Path
    ) -> dict[str, list[str]]:

        directory = Path(path).expanduser().resolve()

        if not directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {directory}"
            )

        if not directory.is_dir():
            raise ValueError(
                f"Path must be a directory: {directory}"
            )

        current_files = {
            file.name: file
            for file in directory.iterdir()
            if (
                file.is_file()
                and file.suffix.lower() == ".txt"
                and not file.name.startswith(".")
            )
        }

        indexed_files = self.vector_store.get_indexed_files(
            str(directory)
        )

        # Remove records for files that no longer exist.
        deleted_files = (
            set(indexed_files) - set(current_files)
        )

        if deleted_files:
            self.vector_store.delete_files(
                str(directory),
                list(deleted_files),
            )

        files_to_index = []

        for file_name, file_path in current_files.items():
            stored_time = indexed_files.get(file_name)

            if (
                stored_time is None
                or file_path.stat().st_mtime != stored_time
            ):
                files_to_index.append(file_path)

        # Load, chunk, embed and store only changed files.
        for file_path in files_to_index:

            file_data = self.loader.file_loads(file_path)

            chunks = self.chunking.chunk_text(file_data)

            embeddings = self.embedding.embed_file(chunks)

            self.vector_store.store_file_chunks(
                chunks=chunks,
                embeddings=embeddings,
                directory=str(directory),
            )

            logger.info(
                "Indexed or updated %s",
                file_path.name,
            )

        if not current_files:
            logger.warning(
                "No .txt files found in %s",
                directory,
            )

        return {
            name: []
            for name in current_files
        }

    def search(
        self,
        path: str | Path,
        query: str,
        top_k: int = 3,
    ):

        directory = Path(path).expanduser().resolve()

        # Make sure new and modified files are indexed.
        self.prepare_data(directory)

        query_embedding = self.embedding.embed_query(query)

        results = self.semantic_search.search(
            query_embedding=query_embedding,
            top_k=top_k,
            directory=str(directory),
        )

        self.display.show_results(query, results)

        return results
