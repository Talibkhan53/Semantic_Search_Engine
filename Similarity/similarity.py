import numpy as np 
class Similarity:
    def cosine_similarity(self,files_content,query_embed):
        result_score = {}
        for file_name,file_embedding in files_content.items():

            distance_from_origin_files_content = np.linalg.norm(file_embedding) 

            distance_from_origin_query = np.linalg.norm(query_embed) 

            distance_from_origin = distance_from_origin_query * distance_from_origin_files_content

            dot_product = np.dot(query_embed,file_embedding)

            angle = dot_product / distance_from_origin

            result_score[file_name] = angle

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


