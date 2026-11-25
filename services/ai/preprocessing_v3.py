"""Tiền xử lý dùng chung, chống học vẹt và tối ưu ngưỡng hai cổng cho JobShield v3."""

from __future__ import annotations

import random
import re
from typing import Any, Sequence

CODES: tuple[str, ...] = ("G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08")
VALID_TYPES: frozenset[str] = frozenset({"posting", "message", "unknown"})
VALID_SPEAKERS: frozenset[str] = frozenset({"recruiter", "applicant", "unknown"})
PLACEHOLDER_RE = re.compile(r"\[[A-Z0-9_]+\]")

_RAW_PLACEHOLDER_POOLS: dict[str, tuple[str, ...]] = {
    "[PHONE]": ("0912345678", "0987654321", "0389123456", "số điện thoại cá nhân"),
    "[URL]": ("https://tuyen-dung.example.vn", "đường dẫn đăng ký", "link trang web"),
    "[LINK]": ("đường dẫn riêng", "link biểu mẫu", "https://portal.example.com"),
    "[ZALO_URL]": ("link Zalo cá nhân", "nhóm Zalo tuyển dụng"),
    "[CONTACT]": ("Zalo cá nhân", "Telegram riêng", "liên hệ trực tiếp"),
    "[MONEY]": ("500.000đ", "300k", "2 triệu đồng", "1.500.000đ"),
    "[NUMBER]": ("500", "300", "24", "10"),
    "[BANK_ACCOUNT]": ("tài khoản ngân hàng cá nhân", "1903456789012", "số tài khoản nhận tiền"),
    "[ACCOUNT]": ("tài khoản ngân hàng", "tài khoản ví điện tử", "tài khoản cá nhân"),
    "[EMAIL]": ("hr@example.vn", "tuyendung@example.com"),
    "[ADDRESS]": ("Quận 1, TP.HCM", "Cầu Giấy, Hà Nội", "địa chỉ văn phòng"),
    "[NAME]": ("Minh", "Lan", "Hùng"),
    "[CODE]": ("849201", "123456"),
    "[REDACTED]": ("thông tin đã ẩn", "nội dung liên hệ"),
}


def _to_segmented_variant(text: str) -> str:
    if text.startswith("http") or text.isdigit() or "@" in text:
        return text
    return text.replace(" ", "_")


def normalize_sentences(
    row_or_sentences: dict[str, Any] | Sequence[dict[str, Any]],
    doc_type: str | None = None,
) -> list[dict[str, str]]:
    """Chuẩn hóa cả schema dataset v3 (`input.type` + `sentences`) lẫn runtime."""
    if isinstance(row_or_sentences, dict):
        inp = row_or_sentences.get("input", row_or_sentences)
        raw_sentences = inp["sentences"]
        resolved_doc_type = doc_type or inp.get("type", "unknown")
    else:
        raw_sentences = row_or_sentences
        resolved_doc_type = doc_type

    normalized: list[dict[str, str]] = []
    for sent in raw_sentences:
        s_type = sent.get("type") or resolved_doc_type or "unknown"
        speaker = sent.get("speaker") or "unknown"
        if s_type not in VALID_TYPES:
            raise ValueError(f"Kiểu nội dung không hợp lệ: {s_type!r}")
        if speaker not in VALID_SPEAKERS:
            raise ValueError(f"Vai người nói không hợp lệ: {speaker!r}")
        normalized.append(
            {
                "id": str(sent["id"]),
                "type": s_type,
                "speaker": speaker,
                "text": str(sent["text"]),
            }
        )
    return normalized


def augment_sentences(
    sentences: Sequence[dict[str, str]],
    rng: random.Random,
    enable: bool = True,
    prefix_dropout_p: float = 0.5,
    placeholder_sub_p: float = 0.7,
    word_segmented: bool = False,
) -> list[dict[str, str]]:
    """Chống học vẹt tiền tố (type/speaker) và placeholder chỉ khi huấn luyện."""
    if not enable:
        return [dict(s) for s in sentences]

    drop_channel = rng.random() < prefix_dropout_p

    def _replace_placeholder(match: re.Match[str]) -> str:
        token = match.group(0)
        if rng.random() >= placeholder_sub_p:
            return token
        pool = _RAW_PLACEHOLDER_POOLS.get(token, ("thông tin",))
        choice = rng.choice(pool)
        return _to_segmented_variant(choice) if word_segmented else choice

    augmented: list[dict[str, str]] = []
    for sent in sentences:
        s_type = "unknown" if drop_channel else sent["type"]
        speaker = "unknown" if rng.random() < prefix_dropout_p else sent["speaker"]
        text = PLACEHOLDER_RE.sub(_replace_placeholder, sent["text"])
        augmented.append(
            {
                "id": sent["id"],
                "type": s_type,
                "speaker": speaker,
                "text": text,
            }
        )
    return augmented


def _segment_texts(
    sentences: Sequence[dict[str, str]],
    segmenter: Any | None = None,
    presegmented_texts: Sequence[str] | None = None,
) -> list[str]:
    if presegmented_texts is not None:
        if len(presegmented_texts) != len(sentences):
            raise ValueError("presegmented_texts phải khớp số lượng câu.")
        return list(presegmented_texts)
    if segmenter is not None:
        return [" ".join(segmenter.word_segment(s["text"])) for s in sentences]
    return [s["text"] for s in sentences]


def encode_sentences(
    sentences: Sequence[dict[str, str]],
    tokenizer: Any,
    max_length: int = 256,
    segmenter: Any | None = None,
    presegmented_texts: Sequence[str] | None = None,
) -> list[dict[str, list[int]]]:
    """Mã hóa từng câu với cửa sổ ngữ cảnh cân bằng quanh câu đang xét."""
    texts = _segment_texts(sentences, segmenter, presegmented_texts)
    parts: list[list[int]] = []
    for sent, text in zip(sentences, texts, strict=True):
        prefix = f"{sent['type']} {sent['speaker']}: "
        parts.append(tokenizer.encode(prefix + text, add_special_tokens=False, verbose=False))

    sep = [tokenizer.sep_token_id]
    special_overhead = len(tokenizer.build_inputs_with_special_tokens([]))
    inner_budget = max_length - special_overhead - 2  # trừ 2 sep bao quanh focus
    if inner_budget <= 0:
        raise ValueError(f"max_length={max_length} quá nhỏ so với special tokens.")

    stream: list[int] = []
    starts: list[int] = []
    for part in parts:
        starts.append(len(stream))
        stream.extend(part + sep)

    features: list[dict[str, list[int]]] = []
    for start, part in zip(starts, parts, strict=True):
        focus = part[:inner_budget]
        available = inner_budget - len(focus)
        after = start + len(part) + 1
        left = min(start, available // 2)
        right = min(len(stream) - after, available - left)
        left = min(start, available - right)
        tokens = stream[start - left : start] + sep + focus + sep + stream[after : after + right]
        input_ids = tokenizer.build_inputs_with_special_tokens(tokens)
        assert len(input_ids) <= max_length, f"Vượt max_length: {len(input_ids)} > {max_length}"
        features.append({"input_ids": input_ids})
    return features


def encode_document_head_tail(
    sentences: Sequence[dict[str, str]],
    tokenizer: Any,
    max_length: int = 256,
    segmenter: Any | None = None,
    presegmented_texts: Sequence[str] | None = None,
) -> dict[str, list[int]]:
    """Mã hóa cả tài liệu trong 1 lượt cho Mô hình 1 (Cổng Kiểu B), cắt head+tail nếu dài."""
    texts = _segment_texts(sentences, segmenter, presegmented_texts)
    sep_id = tokenizer.sep_token_id
    special_overhead = len(tokenizer.build_inputs_with_special_tokens([]))
    inner_budget = max_length - special_overhead
    if inner_budget <= 2:
        raise ValueError(f"max_length={max_length} quá nhỏ so với special tokens.")

    stream: list[int] = []
    for idx, (sent, text) in enumerate(zip(sentences, texts, strict=True)):
        if idx > 0:
            stream.append(sep_id)
        prefix = f"{sent['type']} {sent['speaker']}: "
        stream.extend(tokenizer.encode(prefix + text, add_special_tokens=False, verbose=False))

    if len(stream) > inner_budget:
        head_len = inner_budget // 2
        tail_len = inner_budget - head_len - 1
        stream = stream[:head_len] + [sep_id] + (stream[-tail_len:] if tail_len > 0 else [])

    input_ids = tokenizer.build_inputs_with_special_tokens(stream)
    assert len(input_ids) <= max_length, f"Vượt max_length: {len(input_ids)} > {max_length}"
    return {"input_ids": input_ids}


def decode_two_gate_predictions(
    doc_gate_score: float,
    sentence_ids: Sequence[str],
    sentence_code_scores: Sequence[Sequence[float]],
    codes: Sequence[str],
    tau_gate: float,
    code_thresholds: dict[str, float],
) -> dict[str, Any]:
    """Giải mã hai cổng bảo toàn bất biến: suspicious <=> findings khác rỗng."""
    if doc_gate_score < tau_gate:
        return {"label": "not_detected", "findings": []}

    evidence_by_code: dict[str, list[str]] = {}
    best_pair: tuple[float, str, str] | None = None

    for sid, scores in zip(sentence_ids, sentence_code_scores, strict=True):
        for code, score in zip(codes, scores, strict=True):
            val = float(score)
            if best_pair is None or val > best_pair[0]:
                best_pair = (val, code, sid)
            if val >= code_thresholds[code]:
                evidence_by_code.setdefault(code, []).append(sid)

    if not evidence_by_code and best_pair is not None:
        _, best_code, best_sid = best_pair
        evidence_by_code[best_code] = [best_sid]

    findings = [
        {"code": code, "evidence_sentence_ids": sids}
        for code, sids in sorted(evidence_by_code.items())
    ]
    return {
        "label": "suspicious" if findings else "not_detected",
        "findings": findings,
    }


def _f1(tp: int, fp: int, fn: int) -> float:
    denom = 2 * tp + fp + fn
    return (2.0 * tp / denom) if denom > 0 else 0.0


def optimize_two_gate_thresholds(
    val_rows: Sequence[dict[str, Any]],
    doc_gate_scores: Sequence[float],
    sent_code_scores_by_doc: Sequence[Sequence[Sequence[float]]],
    codes: Sequence[str] = CODES,
    max_false_alarms: int = 2,
) -> dict[str, Any]:
    """Tối ưu ngưỡng cổng và ngưỡng từng mã G01-G08 chỉ trên tập validation."""
    truth_pos = {r["sample_id"] for r in val_rows if r["overall_label"] == "suspicious"}
    gold_pairs = {
        (r["sample_id"], f["code"], sid)
        for r in val_rows
        for f in r["output"]["findings"]
        for sid in f["evidence_sentence_ids"]
    }

    best_gate: dict[str, Any] | None = None
    best_fallback: dict[str, Any] | None = None
    for step in range(5, 96, 2):
        tau = round(step / 100.0, 2)
        pred_pos = {
            r["sample_id"]
            for r, g_score in zip(val_rows, doc_gate_scores, strict=True)
            if g_score >= tau
        }
        tp = len(pred_pos & truth_pos)
        fp = len(pred_pos - truth_pos)
        fn = len(truth_pos - pred_pos)
        recall = tp / max(1, len(truth_pos))
        precision = tp / max(1, tp + fp)
        f1 = _f1(tp, fp, fn)
        cand = {
            "tau_gate": tau,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
        if fp <= max_false_alarms:
            key = (f1, recall, -fp, -abs(tau - 0.5))
            if best_gate is None or key > best_gate["_key"]:
                best_gate = {**cand, "_key": key}
        fb_key = (-fp, f1, recall, -abs(tau - 0.5))
        if best_fallback is None or fb_key > best_fallback["_key"]:
            best_fallback = {**cand, "_key": fb_key}

    chosen_gate = best_gate if best_gate is not None else best_fallback
    assert chosen_gate is not None
    tau_gate = float(chosen_gate["tau_gate"])

    # Tối ưu riêng ngưỡng từng mã trên các tài liệu đã qua cổng trên validation
    code_thresholds: dict[str, float] = {}
    for code_idx, code in enumerate(codes):
        gold_c = {item for item in gold_pairs if item[1] == code}
        best_c_key: tuple[float, float, float] | None = None
        best_tau_c = 0.5
        for step in range(15, 91, 5):
            tau_c = round(step / 100.0, 2)
            pred_c: set[tuple[str, str, str]] = set()
            for row, g_score, s_scores in zip(
                val_rows, doc_gate_scores, sent_code_scores_by_doc, strict=True
            ):
                if g_score < tau_gate:
                    continue
                for sent, scores in zip(row["input"]["sentences"], s_scores, strict=True):
                    if float(scores[code_idx]) >= tau_c:
                        pred_c.add((row["sample_id"], code, sent["id"]))
            tp = len(pred_c & gold_c)
            fp = len(pred_c - gold_c)
            fn = len(gold_c - pred_c)
            c_f1 = _f1(tp, fp, fn)
            key = (c_f1, -abs(tau_c - 0.5), -fp)
            if best_c_key is None or key > best_c_key:
                best_c_key = key
                best_tau_c = tau_c
        code_thresholds[code] = best_tau_c

    # Tính tóm tắt cuối cùng sau khi ghép 2 cổng trên validation
    pred_pairs: set[tuple[str, str, str]] = set()
    pred_docs: set[str] = set()
    exact_correct = 0
    for row, g_score, s_scores in zip(
        val_rows, doc_gate_scores, sent_code_scores_by_doc, strict=True
    ):
        sids = [s["id"] for s in row["input"]["sentences"]]
        out = decode_two_gate_predictions(
            g_score, sids, s_scores, codes, tau_gate, code_thresholds
        )
        sid_codes = {(f["code"], sid) for f in out["findings"] for sid in f["evidence_sentence_ids"]}
        gold_doc_pairs = {
            (f["code"], sid) for f in row["output"]["findings"] for sid in f["evidence_sentence_ids"]
        }
        if out["label"] == "suspicious":
            pred_docs.add(row["sample_id"])
            for c, sid in sid_codes:
                pred_pairs.add((row["sample_id"], c, sid))
        if out["label"] == row["overall_label"] and sid_codes == gold_doc_pairs:
            exact_correct += 1

    tp_ev = len(pred_pairs & gold_pairs)
    fp_ev = len(pred_pairs - gold_pairs)
    fn_ev = len(gold_pairs - pred_pairs)
    chosen_gate.pop("_key", None)

    return {
        "tau_gate": tau_gate,
        "code_thresholds": code_thresholds,
        "validation_summary": {
            **chosen_gate,
            "n": len(val_rows),
            "label_correct": len(val_rows) - len(pred_docs ^ truth_pos),
            "exact_correct": exact_correct,
            "evidence_f1": round(_f1(tp_ev, fp_ev, fn_ev), 4),
            "max_false_alarms_policy": max_false_alarms,
        },
    }
