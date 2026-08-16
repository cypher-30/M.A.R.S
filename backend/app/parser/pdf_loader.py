"""Turn a quarterly report PDF into text the extractor can work with.

Two paths:
  1. Native text layer (most bank filings) -> pypdf, cheap and exact.
  2. Scanned pages with no text layer -> flag for manual entry rather than
     guessing. Silent bad numbers are worse than a gap.
"""
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

MIN_CHARS_PER_PAGE = 200


@dataclass
class LoadedDocument:
    path: Path
    pages: list[str]
    has_text_layer: bool

    @property
    def text(self) -> str:
        return "\n\n".join(self.pages)


def load_pdf(path: str | Path) -> LoadedDocument:
    path = Path(path)
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    avg_chars = sum(len(p) for p in pages) / max(len(pages), 1)
    return LoadedDocument(path=path, pages=pages, has_text_layer=avg_chars >= MIN_CHARS_PER_PAGE)


def select_relevant_pages(doc: LoadedDocument, keywords: list[str]) -> list[str]:
    """Cut the document down before sending it to a model — cheaper and more accurate."""
    lowered = [k.lower() for k in keywords]
    return [p for p in doc.pages if any(k in p.lower() for k in lowered)]
