import re


def find_fee_evidence(text: str) -> list[str]:
    pattern = r"\b(?:nộp|đóng) phí hồ sơ trước khi nhận việc\b"
    evidence = []
    # Bản đầu coi dấu . ! ? và xuống dòng là ranh giới câu.
    for sentence in re.split(r"[.!?\r\n]+", text):
        if re.search(r"\bkhông\b", sentence, re.IGNORECASE):
            continue
        evidence.extend(
            match.group() for match in re.finditer(pattern, sentence, re.IGNORECASE)
        )
    return evidence
