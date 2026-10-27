from pathlib import Path
class Loader:

    SUPPORTED_EXTENSIONS = {".txt"}

    def file_loads(self, path: Path) -> dict[str, str]:
        path = Path(path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not path.is_file() and not path.is_dir():
            raise ValueError(f"Path is not a file or directory: {path}")

        if path.is_file():
            files = [path]
        else:
            files = sorted(
                item for item in path.iterdir()
                if (
                    item.is_file()
                    and not item.name.startswith(".")
                    and item.suffix.lower() in self.SUPPORTED_EXTENSIONS
                )
            )

        file_data = {}

        for file in files:
            if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            try:
                with file.open("r", encoding="utf-8-sig") as current_file:
                    content = current_file.read().strip()

                if content:
                    file_data[file.name] = content

            except UnicodeDecodeError as exc:
                raise ValueError(
                    f"File is not valid UTF-8 text: {file.name}"
                ) from exc

            except OSError as exc:
                raise OSError(
                    f"Could not read file: {file}"
                ) from exc

        return file_data
