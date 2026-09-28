from Similarity.similarity import Similarity
from Result.result import SearchResult


class SemanticSearch:

    def __init__(self):
        self.similarity = Similarity()

    def search(self, files_content, query_embed, top_k=3):

        scores = self.similarity.cosine_similarity(
            files_content,
            query_embed
        )

        ranked_scores = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for file_name, score in ranked_scores[:top_k]:

            results.append(
                SearchResult(
                    file_name=file_name,
                    score=float(score)
                )
            )

        return results