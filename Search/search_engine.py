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

        # Check whether path is already indexed
        if self.vector_store.path_exists(path):

            print("Path already indexed.")

            # Load existing embeddings
            return self.vector_store.load_embeddings(path)

        # Path does not exist
        print("Path not indexed.")
        print("Creating embeddings...")

        # Load files
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