#!/usr/bin/env python3
"""
LibreOffice headless wrapper for PDF conversion.
Usage: python scripts/office/soffice.py --headless --convert-to pdf input.pptx
"""
import sys

def main():
    print("soffice.py is a placeholder — LibreOffice soffice must be installed on the system.", file=sys.stderr)
    print("Install LibreOffice: https://www.libreoffice.org/download/", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
