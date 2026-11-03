
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

project = Path(__file__).resolve().parent
output = project.parent / "SearchEngine_Source.zip"

excluded_dirs = {
    ".venv",
    "venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "chroma_db",
}

excluded_files = {
    ".env",
}

with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for path in project.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(project)

        if any(part in excluded_dirs for part in relative.parts):
            continue

        if path.name in excluded_files or path.suffix == ".pyc":
            continue

        if path.resolve() == output.resolve():
            continue

        if path.name == "make_zip.py":
            continue

        archive.write(path, relative.as_posix())

print(f"ZIP created: {output}")
print(f"ZIP size: {output.stat().st_size / (1024 * 1024):.2f} MB")
