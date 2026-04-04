#!/usr/bin/env python3
"""
Create thumbnail grid of slides from a PPTX.
Usage: python scripts/thumbnail.py input.pptx [output_prefix]
"""
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: thumbnail.py <input.pptx> [output_prefix]", file=sys.stderr)
        sys.exit(1)

    print("Thumbnail generation requires python-pptx and Pillow.", file=sys.stderr)
    print("Install: pip install python-pptx Pillow", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
