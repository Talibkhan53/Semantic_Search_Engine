import json
import numpy as np
from pathlib import Path


class VectorStore:

    def __init__(self, file_name="file_embed_data.json"):

        self.file_name = file_name

    # STORE EMBEDDINGS
    def store_file_vectors(self, file_embed, path):

        path = str(Path(path).resolve())

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

            data[str(index)] = {

                "path": path,

                "file_name": file_name,

                "file_embed": embedding.tolist()
                if isinstance(embedding, np.ndarray)
                else embedding

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

        path = str(Path(path).resolve())

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            return False

        for item in data.values():

            stored_path = str(
                Path(item["path"]).resolve()
            )

            if stored_path == path:

                return True

        return False
    # LOAD EMBEDDINGS
    def load_embeddings(self, path):

        path = str(Path(path).resolve())

        try:

            with open(self.file_name, "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):

            return {}

        embeddings = {}

        for item in data.values():

            stored_path = str(
                Path(item["path"]).resolve()
            )

            if stored_path == path:

                file_name = item["file_name"]

                embedding = np.array(
                    item["file_embed"]
                )

                embeddings[file_name] = embedding

        return embeddings