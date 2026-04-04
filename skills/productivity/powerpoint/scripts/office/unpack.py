#!/usr/bin/env python3
"""
Unpack a PPTX (zip) for direct XML editing.
Usage: python scripts/office/unpack.py input.pptx output_dir/
"""
import sys
import zipfile
import os
import shutil

def main():
    if len(sys.argv) < 3:
        print("Usage: unpack.py <input.pptx> <output_dir>", file=sys.stderr)
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2]

    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)

    with zipfile.ZipFile(src, 'r') as z:
        z.extractall(dst)

    print(f"Unpacked {src} -> {dst}")

if __name__ == "__main__":
    main()
