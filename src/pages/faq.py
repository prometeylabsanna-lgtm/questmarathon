def parse_faq_items(body: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for chunk in body.strip().split("\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        question, _, rest = chunk.partition("\n")
        items.append(
            {
                "question": question.strip(),
                "answer": rest.strip(),
            }
        )
    return items
