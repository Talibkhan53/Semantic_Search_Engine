import logging
from typing import Any

import chromadb

logger = logging.getLogger(__name__)


class VectorStore:
    """Persistent ChromaDB storage for document chunks, keyed by document_id."""

    def __init__(self, db_path: str, collection_name: str = "documents") -> None:
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
        )

    #helpers 
    @staticmethod
    def _build_filter(
        document_ids: list[str] | None,
        user_id: str | None,
    ) -> dict[str, Any] | None:
        clauses: list[dict[str, Any]] = []

        if document_ids:
            clauses.append({"document_id": {"$in": document_ids}})

        if user_id:
            clauses.append({"user_id": user_id})

        if not clauses:
            return None

        return clauses[0] if len(clauses) == 1 else {"$and": clauses}

    # ---------- documents ----------

    def get_document_info(self, document_id: str) -> dict[str, Any] | None:
        """Return chunk count, file name and content hash, or None if absent."""
        records = self.collection.get(
            where={"document_id": document_id},
            include=["metadatas"],
        )
        metadatas = records.get("metadatas") or []

        if not metadatas:
            return None

        first = metadatas[0] or {}
        return {
            "document_id": document_id,
            "file_name": first.get("file_name"),
            "content_hash": first.get("content_hash"),
            "user_id": first.get("user_id") or None,
            "chunks": len(metadatas),
        }

    def delete_document(self, document_id: str) -> int:
        """Delete all chunks of a document. Returns how many were removed."""
        existing = self.collection.get(where={"document_id": document_id})
        ids = existing.get("ids") or []

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)

    def upsert_document(
        self,
        document_id: str,
        file_name: str,
        chunks: list[str],
        vectors: list[list[float]],
        content_hash: str,
        user_id: str | None = None,
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError(
                f"Chunk/vector count mismatch: {len(chunks)} vs {len(vectors)}"
            )

        # Remove old chunks first so a shorter new version leaves nothing stale.
        self.delete_document(document_id)

        if not chunks:
            return

        self.collection.upsert(
            ids=[f"{document_id}::{i}" for i in range(len(chunks))],
            documents=chunks,
            embeddings=vectors,  # type: ignore[arg-type]
            metadatas=[
                {
                    "document_id": document_id,
                    "file_name": file_name,
                    "chunk_index": i,
                    "content_hash": content_hash,
                    "user_id": user_id or "",
                }
                for i in range(len(chunks))
            ],  # type: ignore[arg-type]
        )
        logger.info("Indexed %d chunks for document %s", len(chunks), document_id)

    # ---------- search ----------

    def search(
        self,
        query_vector: list[float],
        n_results: int,
        document_ids: list[str] | None = None,
        user_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if n_results <= 0 or self.collection.count() == 0:
            return []

        args: dict[str, Any] = {
            "query_embeddings": [query_vector],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        where = self._build_filter(document_ids, user_id)

        if where is not None:
            args["where"] = where

        result = self.collection.query(**args)

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        matches: list[dict[str, Any]] = []

        for text, meta, distance in zip(documents, metadatas, distances):
            if text is None or meta is None or distance is None:
                continue

            matches.append(
                {
                    "document_id": meta["document_id"],
                    "file_name": meta["file_name"],
                    "chunk_index": int(meta["chunk_index"]),  # type: ignore[arg-type]
                    "text": text,
                    "score": 1.0 - float(distance),
                }
            )

        return matches

    #health

    def count(self) -> int:
        return self.collection.count()