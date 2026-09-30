from Loader.loader import Loader
from Embeddings.embedding import Embedding
from VectorStore.vector_store import VectorStore
from Search.semantic_search import SemanticSearch
from Result.display import Display


class SearchEngine:

    def __init__(self):

        self.loader = Loader()

        self.embedding = Embedding()

        self.vector_store = VectorStore()

        self.semantic_search = SemanticSearch()

        self.display = Display()


    # Creating EMBEDDINGS

    def prepare_data(self, path):
        # Check Whether Path is Indexed
        if self.vector_store.path_exists(path):
            print("Path  already Indexed")

            changed_files = self.vector_store.get_changed_files(path)
            if not changed_files:
                # No Chnages in Files 
                print("No Changes In Files , Loading Previous Embeddings")
                return self.vector_store.load_embeddings(path)
            
            else:
                # File Data Has Changed
                print("Changes in File Data,Creating New Embeddings")

                embeddings = self.vector_store.load_embeddings(path)

                for file_path in changed_files:
                   file_data =  self.loader.file_loads(file_path)
                   new_embedding = self.embedding.embed_file(file_data)
                   embeddings.update(new_embedding)
                   self.vector_store.store_file_vectors(new_embedding,path)
            return embeddings
    # Path does not exist / is not indexed
        else:

            print("Path not indexed.")
            print("Creating embeddings...")

            # Load ALL files because this is the first indexing
            file_data = self.loader.file_loads(path)

            # Create embeddings
            embeddings = self.embedding.embed_file(
                file_data
            )

            # Store embeddings
            self.vector_store.store_file_vectors(
                embeddings,
                path
            )

            return embeddings


        
    # SEARCH
    def search(self, path, query, top_k=3):

        # Get embeddings
        embed_data = self.prepare_data(path)

        # Embed query
        query_embedding = self.embedding.embed_query(
            query
        )

        # Search
        results = self.semantic_search.search(
            embed_data,
            query_embedding,
            top_k
        )

        # Display
        self.display.show_results(
            query,
            results
        )

        return results