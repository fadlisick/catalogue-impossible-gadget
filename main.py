"""Self-Butter Toaster entry.

Reads the catalogue photograph bundled next to this file and writes it
to the grader output directory as entry.png, validating the gate caps
(PNG, at most 1,048,576 bytes, at most 1024x1024 px) before it exits.
Standard library only, no network.
"""

import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_png_dimensions(data):
    """Return (width, height) parsed from the PNG IHDR chunk."""
    if len(data) < 33:
        fail("image too short to hold a PNG IHDR chunk")
    if data[:8] != PNG_MAGIC:
        fail("asset is not a PNG file")
    length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or length != 13:
        fail("first PNG chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "assets", "gadget.png")
    if not os.path.isfile(source):
        fail(f"asset not found: {source}")

    with open(source, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        fail(f"image is {len(data)} bytes, over the {MAX_BYTES} cap")
    width, height = read_png_dimensions(data)
    if width > MAX_DIM or height > MAX_DIM:
        fail(f"image is {width}x{height}, over the {MAX_DIM}x{MAX_DIM} cap")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as handle:
        handle.write(data)
    # Only the output file gets a mode change, never the output dir:
    # the grader collects outputs as another user, so 0644 is required,
    # and the dir itself is harness-owned (chmod on it raises).
    os.chmod(out_path, 0o644)

    # Verify the file on disk is exactly what was validated above.
    written = os.path.getsize(out_path)
    if written != len(data):
        fail(f"wrote {written} bytes, expected {len(data)}")

    print(f"wrote {out_path}: {width}x{height}, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
