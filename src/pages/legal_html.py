"""Convert plain-text legal docs to simple HTML paragraphs for TinyMCE seed."""

from __future__ import annotations

import html

from src.pages.legal import SECTION_RE, UPDATED_RE


def plain_legal_to_html(body: str) -> tuple[str, str]:
    """Return (updated_label, html_body)."""
    updated = ""
    parts: list[str] = []
    current_heading = ""
    current_paras: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_paras
        if current_heading:
            parts.append(f"<h2>{html.escape(current_heading)}</h2>")
        for para in current_paras:
            parts.append(f"<p>{html.escape(para)}</p>")
        current_heading = ""
        current_paras = []

    for raw in body.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if UPDATED_RE.match(line) and not parts and not current_heading:
            updated = line
            continue
        if SECTION_RE.match(line):
            flush()
            current_heading = line
            continue
        current_paras.append(line)

    flush()
    return updated, "\n".join(parts)


def extract_updated_label(body: str) -> str:
    for raw in body.strip().splitlines():
        line = raw.strip()
        if UPDATED_RE.match(line):
            return line
        if line:
            break
    return ""
