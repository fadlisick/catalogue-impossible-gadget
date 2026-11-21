"""Self-Butter Toaster catalogue entry.

Reads the catalogue photograph assets/gadget.png next to this script,
checks it against the competition gate, and writes it out as entry.png
in the output directory the harness provides.
"""

import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
ASSET_NAME = "gadget.png"
OUTPUT_NAME = "entry.png"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def read_png_dimensions(data):
    """Return (width, height) from a PNG IHDR chunk, or None if malformed."""
    if len(data) < 33:
        return None
    if data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0:
        return None
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "assets", ASSET_NAME)

    try:
        with open(source_path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        fail(f"cannot read {source_path}: {exc}")

    if not data.startswith(PNG_MAGIC):
        fail(f"{ASSET_NAME} is not a PNG file")
    if len(data) > MAX_BYTES:
        fail(f"{ASSET_NAME} is {len(data)} bytes, over the {MAX_BYTES} limit")

    dimensions = read_png_dimensions(data)
    if dimensions is None:
        fail(f"{ASSET_NAME} has no readable IHDR chunk")
    width, height = dimensions
    if width > MAX_SIDE or height > MAX_SIDE:
        fail(f"{ASSET_NAME} is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} limit")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        fail(f"cannot create output directory {out_dir}: {exc}")

    out_path = os.path.join(out_dir, OUTPUT_NAME)
    try:
        with open(out_path, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        fail(f"cannot write {out_path}: {exc}")

    written = os.stat(out_path).st_size
    if written != len(data):
        fail(f"wrote {written} bytes but expected {len(data)}")

    # Only the file itself gets its mode set; the directory belongs to
    # the harness and may be owned by another user.
    os.chmod(out_path, 0o644)
    print(f"wrote {out_path}: {width}x{height}, {len(data)} bytes")


if __name__ == "__main__":
    main()
