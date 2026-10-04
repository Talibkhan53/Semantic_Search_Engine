from Loader.loader import Loader
from Embeddings.embedding import Embedding
from VectorStore.vector_store import VectorStore
from Search.semantic_search import SemanticSearch
from Result.display import Display
from pathlib import Path

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


class SearchEngine:

    def __init__(self):

        self.loader = Loader()

        self.embedding = Embedding()

        self.vector_store = VectorStore()

        self.semantic_search = SemanticSearch()

        self.display = Display()

    # --------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------

    def prepare_data(self, path):

        print("Path:", path)

        # ==================================================
        # PATH ALREADY INDEXED
        # ==================================================

        if self.vector_store.path_exists(path):

            logging.info(
                "Path already indexed."
            )

            # --------------------------------------------------
            # 1. CHECK CHANGED FILES
            # --------------------------------------------------

            changed_files = (
                self.vector_store.get_changed_files(path)
            )

            if changed_files:

                logging.warning(
                    "Changes detected in files."
                )

                updated_embeddings = {}

                for file_path in changed_files:

                    print(
                        "Changed File:",
                        file_path
                    )

                    # Load changed file
                    file_data = (
                        self.loader.file_loads(
                            file_path
                        )
                    )

                    # Create new embedding
                    new_embedding = (
                        self.embedding.embed_file(
                            file_data
                        )
                    )

                    updated_embeddings.update(
                        new_embedding
                    )

                # UPDATE existing records
                self.vector_store.update_existing_embeddings(
                    path,
                    updated_embeddings
                )

            else:

                logging.info(
                    "No changes in existing files."
                )

            # --------------------------------------------------
            # 2. CHECK DELETED FILES
            # --------------------------------------------------

            deleted_files = (
                self.vector_store.get_deleted_files(
                    path
                )
            )

            if deleted_files:

                logging.warning(
                    f"Deleted files: {deleted_files}"
                )

                self.vector_store.delete_embeddings(
                    path,
                    deleted_files
                )

            else:

                logging.info(
                    "No deleted files."
                )

            # --------------------------------------------------
            # 3. CHECK NEW FILES
            # --------------------------------------------------

            new_files = (
                self.vector_store.get_new_files(
                    path
                )
            )

            if new_files:

                logging.info(
                    f"New files: {new_files}"
                )

                new_embeddings = {}

                for file_path in new_files:

                    print(
                        "New File:",
                        file_path
                    )

                    # Load new file
                    file_data = (
                        self.loader.file_loads(
                            Path(file_path)
                        )
                    )

                    # Create embedding
                    new_embedding = (
                        self.embedding.embed_file(
                            file_data
                        )
                    )

                    new_embeddings.update(
                        new_embedding
                    )

                # ADD new records
                self.vector_store.store_file_vectors(
                    new_embeddings,
                    path
                )

            else:

                logging.info(
                    "No new files."
                )

            # --------------------------------------------------
            # 4. LOAD CURRENT EMBEDDINGS
            # --------------------------------------------------

            logging.info(
                "Loading current embeddings."
            )

            return self.vector_store.load_embeddings(
                path
            )

        # ==================================================
        # PATH NOT INDEXED
        # ==================================================

        else:

            logging.warning(
                "Path not indexed."
            )

            logging.info(
                "Creating embeddings..."
            )

            # Load all files
            file_data = (
                self.loader.file_loads(
                    path
                )
            )

            # Create embeddings
            embeddings = (
                self.embedding.embed_file(
                    file_data
                )
            )

            # Store embeddings
            self.vector_store.store_file_vectors(
                embeddings,
                path
            )

            return embeddings

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(
        self,
        path,
        query,
        top_k=3
    ):

        # Get document embeddings
        embed_data = (
            self.prepare_data(
                path
            )
        )

        # Create query embedding
        query_embedding = (
            self.embedding.embed_query(
                query
            )
        )

        # Semantic search
        results = (
            self.semantic_search.search(
                embed_data,
                query_embedding,
                top_k
            )
        )

        # Display results
        self.display.show_results(
            query,
            results
        )

        return results