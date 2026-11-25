"""news-image-20261124 entry: deliver the 24 November 2026 front page.

The repository ships the finished picture as entry.png (a 1024x1024
PNG under the 1 MiB cap). When the grader runs this program it places
an exact copy at $MAKEFUN_OUTPUT_DIR/entry.png (or /output when the
variable is unset). The copy is checked before the program exits: the
first eight bytes must be the PNG signature, the file must stay within
the size cap, and its SHA-256 digest must equal the bundled original.
Any mismatch raises, so a damaged asset can never be judged silently.
Only the Python standard library is used and no network is touched.
"""

from hashlib import sha256
from os import environ
from pathlib import Path
from shutil import copyfile

SIGNATURE = bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A))
SIZE_LIMIT = 1024 * 1024


def _digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def _starts_as_png(path):
    with open(path, "rb") as stream:
        return stream.read(len(SIGNATURE)) == SIGNATURE


def _check_image(path):
    if not Path(path).is_file():
        raise FileNotFoundError("bundled picture not found: %s" % path)
    if not _starts_as_png(path):
        raise ValueError("bundled picture is not a PNG: %s" % path)
    if Path(path).stat().st_size > SIZE_LIMIT:
        raise ValueError("bundled picture is over 1 MiB: %s" % path)


def _deliver(source, destination_dir):
    _check_image(source)
    Path(destination_dir).mkdir(parents=True, exist_ok=True)
    destination = Path(destination_dir) / "entry.png"
    copyfile(source, destination)
    if not _starts_as_png(destination):
        raise ValueError("written copy lost its PNG signature")
    if _digest(destination) != _digest(source):
        raise ValueError("written copy does not match the bundled picture")
    return destination


if __name__ == "__main__":
    _deliver(
        Path(__file__).resolve().parent / "entry.png",
        environ.get("MAKEFUN_OUTPUT_DIR") or "/output",
    )
