import re

SECTION_RE = re.compile(r"^(\d+)\.\s+(?!\d).+")
UPDATED_RE = re.compile(r"^(Останнє оновлення|Последнее обновление):", re.IGNORECASE)


def parse_legal_document(body: str) -> dict:
    updated = ""
    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    for raw in body.strip().splitlines():
        line = raw.strip()
        if not line:
            continue
        if UPDATED_RE.match(line) and not items and current is None:
            updated = line
            continue
        if SECTION_RE.match(line):
            if current is not None:
                items.append(current)
            current = {"question": line, "answer": "", "is_email": False}
            continue
        if current is None:
            continue
        prev = str(current["answer"])
        current["answer"] = f"{prev}\n\n{line}" if prev else line

    if current is not None:
        items.append(current)
    return {"updated": updated, "items": items}
