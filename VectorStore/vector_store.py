
from pathlib import Path
from typing import Any
import logging

import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent ChromaDB storage for document chunks."""

    def __init__(self, db_path: str = "chroma_data") -> None:
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="semantic_search",
            configuration={"hnsw": {"space": "cosine"}},
        )

    @staticmethod
    def _as_list(vector: Any) -> list[float]:
        if hasattr(vector, "tolist"):
            vector = vector.tolist()

        return [float(value) for value in vector]

    def get_indexed_files(self, directory: str) -> dict[str, float]:
        """Return indexed filenames and their modification times."""

        directory_path = str(Path(directory).expanduser().resolve())

        records = self.collection.get(
            where={"directory": directory_path},
            include=["metadatas"],
        )

        indexed: dict[str, float] = {}

        for metadata in records.get("metadatas") or []:
            if not metadata:
                continue

            name = metadata.get("file_name")
            file_time = metadata.get("file_time")

            if name is not None and file_time is not None:
                indexed[str(name)] = float(file_time)# type: ignore

        return indexed

    def path_exists(self, path: str) -> bool:
        return bool(self.get_indexed_files(path))

    def store_file_chunks(
        self,
        chunks: dict[str, list[str]],
        embeddings: dict[str, Any],
        directory: str,
    ) -> None:
        directory_path = Path(directory).expanduser().resolve()

        for file_name, file_chunks in chunks.items():

            if not file_chunks:
                self.delete_file_chunks(
                    str(directory_path), file_name
                )
                continue

            file_embeddings = embeddings.get(file_name)

            if file_embeddings is None:
                raise ValueError(
                    f"Embeddings missing for file: {file_name}"
                )

            if len(file_chunks) != len(file_embeddings):
                raise ValueError(
                    f"Chunk and embedding count mismatch for "
                    f"{file_name}: {len(file_chunks)} chunks, "
                    f"{len(file_embeddings)} embeddings"
                )

            file_path = (directory_path / file_name).resolve()

            if not file_path.is_file():
                raise FileNotFoundError(
                    f"Source file not found: {file_path}"
                )

            file_time = file_path.stat().st_mtime

            ids = [
                f"{file_path}::chunk_{i}"
                for i in range(len(file_chunks))
            ]

            metadatas = [
                {
                    "file_path": str(file_path),
                    "directory": str(directory_path),
                    "file_name": file_name,
                    "chunk_index": i,
                    "file_time": float(file_time),
                }
                for i in range(len(file_chunks))
            ]

            vectors = [
                self._as_list(vector)
                for vector in file_embeddings
            ]

            # Remove stale chunks when a file is re-indexed.
            self.delete_file_chunks(
                str(directory_path), file_name
            )

            self.collection.upsert(
                ids=ids,
                documents=file_chunks,
                embeddings=vectors,# type: ignore
                metadatas=metadatas,  # type: ignore
            )

            logger.info(
                "Indexed %d chunks from %s",
                len(file_chunks),
                file_name,
            )

    def delete_file_chunks(
        self,
        directory: str,
        file_name: str,
    ) -> None:
        directory_path = str(
            Path(directory).expanduser().resolve()
        )

        self.collection.delete(
            where={
                "$and": [
                    {"directory": directory_path},
                    {"file_name": file_name},
                ]
            }
        )

    def delete_files(
        self,
        directory: str,
        file_names: list[str],
    ) -> None:
        for file_name in set(file_names):
            self.delete_file_chunks(directory, file_name)

            logger.info(
                "Removed indexed chunks for deleted file %s",
                file_name,
            )

    def search_chunks(
        self,
        query_embedding: Any,
        top_k: int = 3,
        directory: str | None = None,
    ) -> list[dict[str, Any]]:

        if top_k <= 0:
            return []

        count = self.collection.count()

        if count == 0:
            return []

        query_args: dict[str, Any] = {
            "query_embeddings": [
                self._as_list(query_embedding)
            ],
            "n_results": min(top_k, count),
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if directory is not None:
            query_args["where"] = {
                "directory": str(
                    Path(directory).expanduser().resolve()
                )
            }

        results = self.collection.query(**query_args)

        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if documents is None or metadatas is None or distances is None:
            return []

        if not documents or not metadatas or not distances:
            return []

        if (
            documents[0] is None
            or metadatas[0] is None
            or distances[0] is None
        ):
            return []

        matches = []

        for document, metadata, distance in zip(
            documents[0],
            metadatas[0],
            distances[0],
        ):
            if (
                document is None
                or metadata is None
                or distance is None
            ):
                continue

            distance_value = float(distance)

            matches.append({
                "text": document,
                "metadata": metadata,
                "distance": distance_value,
                "score": 1.0 - distance_value,
            })

        return matches
