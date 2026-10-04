import json
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


class VectorStore:

    def __init__(self, file_name="file_embed_data.json"):

        self.file_name = file_name

    # STORE NEW EMBEDDINGS
    def store_file_vectors(self, file_embed, path):

        directory = Path(path).resolve()

        data = {}

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            data = {}

        # Find next index
        if data:

            index = max(
                map(int, data.keys())
            ) + 1

        else:

            index = 1

        # Store embeddings
        for file_name, embedding in file_embed.items():

            file_path = directory / file_name

            data[str(index)] = {

                "path": str(directory),

                "file_time": file_path.stat().st_mtime,

                "file_name": file_name,

                "file_embed": (
                    embedding.tolist()
                    if isinstance(embedding, np.ndarray)
                    else embedding
                )
            }

            index += 1

        with open(self.file_name, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )

        logging.info("Vectors stored successfully.")

    # CHECK PATH
    def path_exists(self, path):

        path = Path(path).resolve()

        print(f"Current Path: {path}")

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            logging.warning(
                "Vector store could not be loaded."
            )

            return False

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            logging.info(
                f"Stored Path: {stored_path}"
            )

            if stored_path == path:

                logging.info("Path Matched.")

                return True

        return False
    
    # LOAD EMBEDDINGS
    def load_embeddings(self, path):

        path = Path(path).resolve()

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            return {}

        embeddings = {}

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            if stored_path == path:

                file_name = item["file_name"]

                embedding = np.array(
                    item["file_embed"]
                )

                embeddings[file_name] = embedding

        return embeddings

    # GET CHANGED FILES
    def get_changed_files(self, path):

        changed_files = []

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            return changed_files

        directory = Path(path).resolve()

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            # Only check files belonging
            # to requested directory
            if stored_path != directory:
                continue

            file_path = directory / item["file_name"]

            # File was deleted
            if not file_path.exists():

                continue

            current_time = file_path.stat().st_mtime

            stored_time = item["file_time"]

            # File was modified
            if current_time != stored_time:

                changed_files.append(
                    str(file_path)
                )

        return changed_files

    # UPDATE EXISTING EMBEDDINGS
    def update_existing_embeddings(
        self,
        path,
        new_embeddings
    ):

        directory = Path(path).resolve()

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            logging.warning(
                "Error loading vector store."
            )

            return

        # Go through new embeddings
        for file_name, embedding in new_embeddings.items():

            file_path = directory / file_name

            if not file_path.exists():
                continue

            # Find existing record
            for item in data.values():

                stored_path = Path(
                    item["path"]
                ).resolve()

                if (
                    stored_path == directory
                    and item["file_name"] == file_name
                ):

                    # Update embedding
                    item["file_embed"] = (
                        embedding.tolist()
                        if isinstance(
                            embedding,
                            np.ndarray
                        )
                        else embedding
                    )

                    # IMPORTANT:
                    # Update modification time
                    item["file_time"] = (
                        file_path.stat().st_mtime
                    )

                    logging.info(
                        f"Embedding updated: {file_name}"
                    )

                    break

        # Save updated vector store
        with open(self.file_name, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )

        logging.info(
            "Existing embeddings updated successfully."
        )

    # GET DELETED FILES
    def get_deleted_files(self, path):

        deleted_files = []

        directory = Path(path).resolve()

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            return deleted_files

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            if stored_path != directory:
                continue

            file_path = directory / item["file_name"]

            if not file_path.exists():

                deleted_files.append(
                    item["file_name"]
                )

        return deleted_files

    # DELETE EMBEDDINGS

    def delete_embeddings(
        self,
        path,
        file_names
    ):

        directory = Path(path).resolve()

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            logging.warning(
                "Error loading vector store."
            )

            return

        deleted = []

        # list() is important because
        # we are deleting while iterating
        for key, item in list(data.items()):

            stored_path = Path(
                item["path"]
            ).resolve()

            if (
                stored_path == directory
                and item["file_name"] in file_names
            ):

                deleted.append(
                    item["file_name"]
                )

                del data[key]

        # Save only if something was deleted
        if deleted:

            with open(self.file_name, "w") as file:

                json.dump(
                    data,
                    file,
                    indent=4
                )

            for file_name in deleted:

                logging.info(
                    f"Embedding deleted: {file_name}"
                )

    # GET NEW FILES
    def get_new_files(self, path):

        directory = Path(path).resolve()

        new_files = []

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            # If vector store doesn't exist,
            # all files are new
            return [
                str(file)
                for file in directory.iterdir()
                if file.is_file()
            ]

        stored_files = set()

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            if stored_path == directory:

                stored_files.add(
                    item["file_name"]
                )

        if not directory.exists():
            return new_files

        for file in directory.iterdir():

            if (
                file.is_file()
                and file.name not in stored_files
            ):

                new_files.append(
                    str(file)
                )

        return new_files