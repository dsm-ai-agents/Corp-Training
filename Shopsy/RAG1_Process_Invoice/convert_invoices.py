# /// script
# requires-python = ">=3.10"
# dependencies = ["markitdown[pdf]"]
# ///
"""Convert invoice PDFs in INVOICES/ to Markdown with Microsoft MarkItDown.

Each PDF is written to converted/<name>.md. Only PDFs that convert
successfully (non-empty output) are moved to completed/; failures stay
in INVOICES/ so they can be retried.

Run with:  uv run convert_invoices.py
"""
import shutil
import sys
from pathlib import Path

from markitdown import MarkItDown

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "INVOICES"
CONVERTED = BASE / "converted"
COMPLETED = BASE / "completed"


def main() -> int:
    CONVERTED.mkdir(exist_ok=True)
    COMPLETED.mkdir(exist_ok=True)

    pdfs = sorted(SOURCE.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {SOURCE}")
        return 0

    md = MarkItDown()
    ok, failed = 0, []
    for pdf in pdfs:
        try:
            text = md.convert(str(pdf)).text_content
            if not text or not text.strip():
                raise ValueError("empty output")
            (CONVERTED / f"{pdf.stem}.md").write_text(text, encoding="utf-8")
            shutil.move(str(pdf), COMPLETED / pdf.name)
            ok += 1
            print(f"[ok]   {pdf.name}")
        except Exception as e:
            failed.append(pdf.name)
            print(f"[fail] {pdf.name}: {e}")

    print(f"\nConverted {ok}/{len(pdfs)}. Failed: {failed or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
