
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def create_code_zip() -> None:
    source = Path(__file__).resolve().parent
    destination = source / f"{source.name}.zip"
    script = Path(__file__).resolve()

    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for path in source.rglob("*"):
            if not path.is_file():
                continue

            if "__pycache__" in path.parts:
                continue

            if path.suffix == ".pyc":
                continue

            if path.resolve() in (script, destination):
                continue

            archive.write(path, path.relative_to(source))

    print(f"ZIP created: {destination}")


if __name__ == "__main__":
    create_code_zip()
