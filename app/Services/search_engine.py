import hashlib
import logging

from app.Chunking.chunking import Chunker
from app.Embeddings.embedding import Embedder
from app.schema import (
    DeleteOut,
    DocumentIn,
    DocumentInfo,
    DocumentOut,
    SearchHit,
    SearchRequest,
    SearchResponse,
)
from app.VectorStore.vector_store import VectorStore

logger = logging.getLogger(__name__)

# When grouping by document we over-fetch so enough distinct documents remain.
_GROUP_OVERFETCH = 3
_MAX_FETCH = 100


class SearchEngine:
    """Coordinates chunking, embedding and storage."""

    def __init__(
        self,
        chunker: Chunker,
        embedder: Embedder,
        store: VectorStore,
    ) -> None:
        self.chunker = chunker
        self.embedder = embedder
        self.store = store

    #documents
    def index_document(self, doc: DocumentIn) -> DocumentOut:
        content_hash = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
        existing = self.store.get_document_info(doc.document_id)

        if existing and existing["content_hash"] == content_hash:
            return DocumentOut(
                document_id=doc.document_id,
                file_name=existing["file_name"] or doc.file_name,
                chunks=existing["chunks"],
                status="unchanged",
            )

        chunks = self.chunker.chunk_text(doc.text)

        if not chunks:
            raise ValueError("Document produced no chunks")

        vectors = self.embedder.embed_documents(chunks)

        self.store.upsert_document(
            document_id=doc.document_id,
            file_name=doc.file_name,
            chunks=chunks,
            vectors=vectors,
            content_hash=content_hash,
            user_id=doc.user_id,
        )

        return DocumentOut(
            document_id=doc.document_id,
            file_name=doc.file_name,
            chunks=len(chunks),
            status="updated" if existing else "indexed",
        )

    def get_document(self, document_id: str) -> DocumentInfo | None:
        info = self.store.get_document_info(document_id)

        if info is None:
            return None

        return DocumentInfo(
            document_id=info["document_id"],
            file_name=info["file_name"],
            chunks=info["chunks"],
            user_id=info["user_id"],
        )

    def delete_document(self, document_id: str) -> DeleteOut:
        return DeleteOut(
            document_id=document_id,
            deleted_chunks=self.store.delete_document(document_id),
        )

    # ---------- search ----------

    def search(self, request: SearchRequest) -> SearchResponse:
        fetch = request.top_k

        if request.group_by_document:
            fetch = min(request.top_k * _GROUP_OVERFETCH, _MAX_FETCH)

        query_vector = self.embedder.embed_query(request.query)

        matches = self.store.search(
            query_vector=query_vector, #ignore # type: ignore
            n_results=fetch,
            document_ids=request.document_ids,
            user_id=request.user_id,
        )

        matches = [m for m in matches if m["score"] >= request.min_score]

        if request.group_by_document:
            best: dict[str, dict] = {}

            for match in matches:  # already sorted best-first
                best.setdefault(match["document_id"], match)

            matches = list(best.values())

        matches = matches[: request.top_k]

        return SearchResponse(
            query=request.query,
            count=len(matches),
            results=[SearchHit(**m) for m in matches],
        )

    #health

    def stats(self) -> dict:
        return {
            "model": self.embedder.model_name,
            "chunks": self.store.count(),
        }