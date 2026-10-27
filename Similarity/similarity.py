import numpy as np 
class Similarity:
    def cosine_similarity(self,file_content,query_embed):
        result_score = {}

        query_embed = np.asarray(query_embed,dtype=float)
        query_norm = np.linalg.norm(query_embed)

        if query_norm == 0:
            raise ValueError("Query embedding cannot be a zero vector.")

        for file_name , file_embedding in file_content.items():
            file_embedding = np.asarray(file_embedding,dtype=float)
            
            # No chunks or empty embeddings
            if file_embedding.size == 0:
                continue

            # A single embedding has shape (dimensions,).
            # Multiple chunk embeddings have shape (chunks, dimensions).
            if file_embedding.ndim == 1:
                file_embedding = file_embedding.reshape(1, -1)

            if file_embedding.ndim != 2:
                raise ValueError(
                    f"Invalid embedding dimensions for {file_name}"
                )
            norms = np.linalg.norm(file_embedding, axis=1)
            valid = norms > 0
            if not np.any(valid):
                continue
            scores = (
            file_embedding[valid] @ query_embed) / (norms[valid] * query_norm)

            # Keep the best matching chunk's score for this file
            result_score[file_name] = float(np.max(scores))
        return result_score

    def tradional_search(self,files_content,query):
        result = {}
        query_words = query.split()
        answer = []
        for file_name, file_content in files_content.items():
            exits_word = []
            score = 0
            file_words = file_content.split()
            for word in file_words:
                if word.lower() in query_words:
                    if word  in exits_word:
                        continue
                    score = score + 1
                    exits_word.append(word)

            result[file_name] = score
        return result


# s = Similarity() 

# files_content = {
#     "python.txt": ["python", "is", "a", "programming", "language"],
#     "numpy.txt": ["numpy", "is", "used", "for", "python", "arrays"],
#     "games.txt": ["games", "are", "fun"]
# }
# s.tradional_search(files_content,"What is Python")


