
from Result.result import SearchResult
from VectorStore.vector_store import VectorStore


class SemanticSearch:

    def __init__(
        self,
        vector_store: VectorStore | None = None,
    ):
        self.vector_store = vector_store or VectorStore()

    def search(
        self,
        query_embedding,
        top_k: int = 3,
        directory: str | None = None,
    ):

        matches = self.vector_store.search_chunks(
            query_embedding=query_embedding,
            top_k=top_k,
            directory=directory,
        )

        return [
            SearchResult(
                file_name=match["metadata"]["file_name"],
                score=float(match["score"]),
                text=match["text"],
                chunk_index=int(
                    match["metadata"]["chunk_index"]
                ),
                distance=float(match["distance"]),
            )
            for match in matches
        ]
