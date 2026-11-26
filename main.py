#!/usr/bin/env python3
"""news-image-20261126: a one-image world atlas of Thursday 26 November 2026.

Copies the pre-rendered atlas image (entry.png, drawn by draw_globe.py at
build time) to $MAKEFUN_OUTPUT_DIR/entry.png (default /output). Pure
standard library: no Pillow, no fonts, no network, no randomness. The
grader runs this in a minimal image, so this file must never import
anything beyond the standard library and must never write into the
repository directory.
"""

import os
import shutil
import sys

MAX_BYTES = 1048576  # 1 MiB


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        fail("entry.png not found next to main.py: " + src)
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        fail("entry.png is %d bytes, over the %d byte limit" % (size, MAX_BYTES))
    with open(src, "rb") as f:
        magic = f.read(8)
    if magic != b"\x89PNG\r\n\x1a\n":
        fail("entry.png does not start with the PNG signature; refusing to copy")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, out_path)

    copied = os.path.getsize(out_path)
    if copied != size:
        fail("copied entry.png is %d bytes, expected %d" % (copied, size))
    print("copied entry.png (%d bytes) to %s" % (size, out_path))


if __name__ == "__main__":
    main()
