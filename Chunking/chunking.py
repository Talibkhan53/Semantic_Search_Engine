
class Chunking:

    def __init__(
        self,
        chunk_size: int = 10,
        chunk_overlap: int = 5
    ):

        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive.")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "Chunk overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, file_content):

        all_chunks = {}

        # Process every file
        for file_name, file_data in file_content.items():

            # Split document into words
            words = file_data.split()

            # Store chunks for current file
            chunks = []

            # Calculate sliding window step
            step = self.chunk_size - self.chunk_overlap

            # Generate chunks
            for start in range(0, len(words), step):

                chunk_words = words[
                    start:start + self.chunk_size
                ]

                # Convert words back into text
                chunk = " ".join(chunk_words)

                chunks.append(chunk)

                # Stop after reaching document end
                if start + self.chunk_size >= len(words):
                    break

            # Store all chunks for current file
            all_chunks[file_name] = chunks

        return all_chunks
