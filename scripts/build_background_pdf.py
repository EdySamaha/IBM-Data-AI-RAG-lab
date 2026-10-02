#!/usr/bin/env python3
"""
Build docs/cod_background.pdf from docs/cod_background.md.

The lab's semantic-search step reads this PDF with `pypdf`, so it must contain
real, extractable text. Two rendering paths:

  1. If `reportlab` is installed, use it (nicer typography).
     Install with:  pip install reportlab
  2. Otherwise fall back to a tiny built-in PDF writer (no dependencies) that
     lays out wrapped text with the standard Helvetica font.

Usage:
    python scripts/build_background_pdf.py
"""
from __future__ import annotations

import textwrap
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "docs" / "cod_background.md"
OUT = Path(__file__).resolve().parents[1] / "docs" / "cod_background.pdf"


def parse_markdown(md: str):
    """Return a list of (kind, text) blocks: kind in {title, heading, para}."""
    blocks = []
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("## "):
            blocks.append(("heading", line[3:].strip()))
        elif line.startswith("# "):
            blocks.append(("title", line[2:].strip()))
        else:
            blocks.append(("para", line.strip()))
    return blocks


# --------------------------------------------------------------------------- #
# Path 1: reportlab
# --------------------------------------------------------------------------- #
def build_with_reportlab(blocks) -> bool:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        return False

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("LabTitle", parent=styles["Title"], fontSize=20, spaceAfter=16)
    head_style = ParagraphStyle("LabHead", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("LabBody", parent=styles["BodyText"], fontSize=11, leading=16, spaceAfter=10)

    doc = SimpleDocTemplate(str(OUT), pagesize=letter,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch,
                            title="The Northern Cod Fishery: A Short Background")
    flow = []
    for kind, text in blocks:
        if kind == "title":
            flow.append(Paragraph(text, title_style))
        elif kind == "heading":
            flow.append(Paragraph(text, head_style))
        else:
            flow.append(Paragraph(text, body_style))
    flow.append(Spacer(1, 0.2 * inch))
    doc.build(flow)
    return True


# --------------------------------------------------------------------------- #
# Path 2: zero-dependency minimal PDF writer
# --------------------------------------------------------------------------- #
def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_minimal(blocks) -> None:
    # Letter page, 1-inch margins.
    page_w, page_h = 612, 792
    margin = 72
    top = page_h - margin
    bottom = margin
    wrap_at = 92  # characters per line at 11pt Helvetica within the text column

    # Turn blocks into (font_size, leading, text-line) instructions.
    lines = []  # list of (size, leading, space_before, text)
    for kind, text in blocks:
        if kind == "title":
            lines.append((18, 24, 6, text))
            lines.append((0, 8, 0, ""))  # gap
        elif kind == "heading":
            lines.append((14, 18, 10, text))
        else:
            for i, wrapped in enumerate(textwrap.wrap(text, wrap_at)):
                lines.append((11, 15, 6 if i == 0 else 0, wrapped))
            lines.append((0, 6, 0, ""))  # paragraph gap

    # Paginate into content streams.
    pages_content = []
    y = top
    cur = []

    def flush_page():
        nonlocal cur
        if cur:
            pages_content.append("\n".join(cur))
            cur = []

    for size, leading, space_before, text in lines:
        step = leading + space_before
        if y - step < bottom:
            flush_page()
            y = top
        y -= step
        if text:
            cur.append(f"BT /F1 {size} Tf 1 0 0 1 {margin} {y:.1f} Tm ({_esc(text)}) Tj ET")
    flush_page()
    if not pages_content:
        pages_content = [""]

    # Assemble PDF objects.
    objects = []  # raw body strings (without the "N 0 obj" wrapper)
    # 1 Catalog, 2 Pages, 3 Font, then per page: Page + Contents.
    n_pages = len(pages_content)
    font_obj = 3
    first_page_obj = 4
    page_obj_ids = [first_page_obj + 2 * i for i in range(n_pages)]
    content_obj_ids = [first_page_obj + 2 * i + 1 for i in range(n_pages)]

    kids = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    objects.append(("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"))
    objects.append((f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>\nendobj\n"))
    objects.append((f"{font_obj} 0 obj\n<< /Type /Font /Subtype /Type1 "
                    f"/BaseFont /Helvetica >>\nendobj\n"))
    for i in range(n_pages):
        pid, cid = page_obj_ids[i], content_obj_ids[i]
        objects.append((f"{pid} 0 obj\n<< /Type /Page /Parent 2 0 R "
                        f"/MediaBox [0 0 {page_w} {page_h}] "
                        f"/Resources << /Font << /F1 {font_obj} 0 R >> >> "
                        f"/Contents {cid} 0 R >>\nendobj\n"))
        stream = pages_content[i]
        objects.append((f"{cid} 0 obj\n<< /Length {len(stream.encode('latin-1', 'replace'))} >>\n"
                        f"stream\n{stream}\nendstream\nendobj\n"))

    # Write with a correct xref table.
    header = "%PDF-1.4\n"
    body = ""
    offsets = []
    pos = len(header)
    # objects are in id order 1..N already
    ordered = objects
    for obj in ordered:
        offsets.append(pos)
        body += obj
        pos += len(obj.encode("latin-1", "replace"))

    n_obj = len(ordered)
    xref_pos = len(header) + len(body.encode("latin-1", "replace"))
    xref = f"xref\n0 {n_obj + 1}\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n"
    trailer = (f"trailer\n<< /Size {n_obj + 1} /Root 1 0 R >>\n"
               f"startxref\n{xref_pos}\n%%EOF\n")

    OUT.write_bytes((header + body + xref + trailer).encode("latin-1", "replace"))


def main() -> None:
    md = SRC.read_text(encoding="utf-8")
    blocks = parse_markdown(md)
    if build_with_reportlab(blocks):
        print(f"Built {OUT} using reportlab.")
    else:
        build_minimal(blocks)
        print(f"Built {OUT} using the built-in minimal writer (reportlab not installed).")


if __name__ == "__main__":
    main()
