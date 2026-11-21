"""Catalogue-photo entry: the self-buttering toaster.

Copies the bundled catalogue photograph to the grader's output
directory as ``entry.png``, after checking it against the gate:
a whole PNG, at most 1 MiB, at most 1024 by 1024 pixels.

Standard library only. No network access.
"""

import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ASSET_NAME = "gadget.png"


def die(message):
    """Print an error and exit non-zero."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def png_size(blob):
    """Return (width, height) read from the PNG IHDR chunk."""
    if len(blob) < 33:
        die("image is too short to contain a PNG header")
    if blob[:8] != PNG_SIGNATURE:
        die("asset does not start with the PNG signature")
    chunk_len, chunk_tag = struct.unpack(">I4s", blob[8:16])
    if chunk_tag != b"IHDR" or chunk_len != 13:
        die("first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(base, "assets", ASSET_NAME)
    if not os.path.isfile(asset_path):
        die(f"bundled image missing: {asset_path}")

    with open(asset_path, "rb") as source:
        blob = source.read()

    if len(blob) > MAX_BYTES:
        die(f"image is {len(blob)} bytes, over the {MAX_BYTES} byte cap")
    width, height = png_size(blob)
    if width > MAX_SIDE or height > MAX_SIDE:
        die(f"image is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} cap")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as target:
        target.write(blob)

    # Only the file we created gets a mode: the output directory
    # belongs to the harness, and chmod on it would raise, so the
    # directory is left exactly as the grader made it.
    os.chmod(out_path, 0o644)

    # Confirm the file on disk is exactly the image validated above.
    on_disk = os.path.getsize(out_path)
    if on_disk != len(blob):
        die(f"wrote {on_disk} bytes, expected {len(blob)}")

    print(f"wrote {out_path}: {width}x{height}, {len(blob)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
