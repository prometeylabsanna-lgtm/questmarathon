def parse_faq_items(body: str) -> list[dict[str, str]]:
    items: list[dict[str, object]] = []
    for chunk in body.strip().split("\n\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        question, _, rest = chunk.partition("\n")
        answer = rest.strip()
        compact = answer.replace(" ", "")
        is_email = "@" in compact and "\n" not in answer and " " not in answer
        items.append(
            {
                "question": question.strip(),
                "answer": answer,
                "is_email": is_email,
            }
        )
    return items
