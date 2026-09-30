import json
import numpy as np
from pathlib import Path


class VectorStore:

    def __init__(self, file_name="file_embed_data.json"):

        self.file_name = file_name

    # STORE EMBEDDINGS
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

                # Directory containing the file
                "path": str(directory),

                # Modification time of the individual file
                "file_time": file_path.stat().st_mtime,

                # Name of the individual file
                "file_name": file_name,

                # Store embedding as a JSON-compatible list
                "file_embed": (
                    embedding.tolist()
                    if isinstance(embedding, np.ndarray)
                    else embedding
                )

            }

            index += 1

        # Save
        with open(self.file_name, "w") as file:

            json.dump(
                data,
                file,
                indent=4
            )

        print("Vectors stored successfully.")

    # CHECK PATH
    def path_exists(self, path):

        path = Path(path).resolve()

        print(f"Current Path: {path}")

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            print("Vector store could not be loaded.")

            return False

        for item in data.values():

            stored_path = Path(
                item["path"]
            ).resolve()

            print(f"Stored Path: {stored_path}")

            if stored_path == path:

                print("Path Matched.")

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

            file_path = directory / item["file_name"]

            # File was deleted
            if not file_path.exists():

                continue

            # Current modification time
            current_time = file_path.stat().st_mtime

            # Modification time stored with embedding
            stored_time = item["file_time"]

            # File has changed
            if current_time != stored_time:

                changed_files.append(
                    str(file_path)
                )

        return changed_files