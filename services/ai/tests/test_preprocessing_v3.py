import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from preprocessing_v3 import (
    CODES,
    augment_sentences,
    decode_two_gate_predictions,
    encode_document_head_tail,
    encode_sentences,
    normalize_sentences,
    optimize_two_gate_thresholds,
)


class _DummyTokenizer:
    sep_token_id = 2
    cls_token_id = 0

    def encode(self, text: str, add_special_tokens: bool = False, verbose: bool = False) -> list[int]:
        ids = [100 + (abs(hash(tok)) % 900) for tok in text.split()]
        return self.build_inputs_with_special_tokens(ids) if add_special_tokens else ids

    def build_inputs_with_special_tokens(self, token_ids: list[int]) -> list[int]:
        return [self.cls_token_id, *token_ids, self.sep_token_id]


def test_normalize_supports_v3_and_runtime_schemas():
    v3_row = {
        "sample_id": "S1",
        "input": {
            "type": "posting",
            "sentences": [
                {"id": "c1", "speaker": "recruiter", "text": "Tuyển CTV."},
                {"id": "c2", "speaker": "unknown", "text": "Đóng cọc 500k."},
            ],
        },
    }
    norm_v3 = normalize_sentences(v3_row)
    assert [s["type"] for s in norm_v3] == ["posting", "posting"]

    runtime = [{"id": "c1", "type": "message", "speaker": "applicant", "text": "Dạ."}]
    assert normalize_sentences(runtime) == runtime


def test_encode_sentences_respects_budget_and_centers_focus():
    tok = _DummyTokenizer()
    sentences = [
        {
            "id": f"c{i}",
            "type": "message",
            "speaker": "recruiter",
            "text": " ".join(f"w{i}_{j}" for j in range(30)),
        }
        for i in range(1, 25)
    ]
    for max_len in (256, 512):
        feats = encode_sentences(sentences, tok, max_length=max_len)
        assert len(feats) == len(sentences)
        assert all(len(f["input_ids"]) <= max_len for f in feats)
        # Câu giữa phải được bao quanh bởi 2 dấu sep_token_id
        mid_ids = feats[12]["input_ids"]
        assert mid_ids.count(tok.sep_token_id) >= 3


def test_encode_document_head_tail_truncates_cleanly():
    tok = _DummyTokenizer()
    sentences = [
        {"id": f"c{i}", "type": "posting", "speaker": "unknown", "text": " ".join(["word"] * 40)}
        for i in range(20)
    ]
    feat_256 = encode_document_head_tail(sentences, tok, max_length=256)
    feat_512 = encode_document_head_tail(sentences, tok, max_length=512)
    assert len(feat_256["input_ids"]) <= 256
    assert len(feat_512["input_ids"]) <= 512
    assert feat_256["input_ids"][0] == tok.cls_token_id
    assert feat_256["input_ids"][-1] == tok.sep_token_id


def test_augment_sentences_disabled_is_identity_and_enabled_mutates_safely():
    original = [
        {"id": "c1", "type": "message", "speaker": "recruiter", "text": "Liên hệ [PHONE] gửi [MONEY]."}
    ]
    disabled = augment_sentences(original, random.Random(42), enable=False)
    assert disabled == original
    assert disabled is not original

    aug_plain = augment_sentences(
        original, random.Random(1), enable=True, prefix_dropout_p=1.0, placeholder_sub_p=1.0
    )
    assert aug_plain[0]["type"] == "unknown"
    assert aug_plain[0]["speaker"] == "unknown"
    assert "[PHONE]" not in aug_plain[0]["text"]
    assert "[MONEY]" not in aug_plain[0]["text"]
    assert original[0]["type"] == "message"

    aug_seg = augment_sentences(
        [{"id": "c1", "type": "posting", "speaker": "recruiter", "text": "Nhắn [CONTACT]"}],
        random.Random(2),
        enable=True,
        prefix_dropout_p=0.0,
        placeholder_sub_p=1.0,
        word_segmented=True,
    )
    assert "[" not in aug_seg[0]["text"]
    assert "_" in aug_seg[0]["text"]


def test_decode_two_gate_consistency_invariant():
    thresholds = {c: 0.5 for c in CODES}
    # Không qua cổng -> luôn not_detected & findings rỗng
    out_clean = decode_two_gate_predictions(0.3, ["c1"], [[0.9] * 8], CODES, 0.5, thresholds)
    assert out_clean == {"label": "not_detected", "findings": []}

    # Qua cổng nhưng chưa câu nào vượt tau_c -> lấy cặp cao nhất
    out_fallback = decode_two_gate_predictions(
        0.8, ["c1", "c2"], [[0.1] * 8, [0.2, 0.45, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]], CODES, 0.5, thresholds
    )
    assert out_fallback == {
        "label": "suspicious",
        "findings": [{"code": "G02", "evidence_sentence_ids": ["c2"]}],
    }


def test_optimize_two_gate_thresholds_respects_false_alarm_cap():
    val_rows = [
        {
            "sample_id": "P1",
            "overall_label": "suspicious",
            "input": {"type": "message", "sentences": [{"id": "c1", "speaker": "recruiter", "text": "p1"}]},
            "output": {"findings": [{"code": "G01", "evidence_sentence_ids": ["c1"]}]},
        },
        {
            "sample_id": "N1",
            "overall_label": "not_detected",
            "input": {"type": "posting", "sentences": [{"id": "c1", "speaker": "unknown", "text": "n1"}]},
            "output": {"findings": []},
        },
        {
            "sample_id": "N2",
            "overall_label": "not_detected",
            "input": {"type": "posting", "sentences": [{"id": "c1", "speaker": "unknown", "text": "n2"}]},
            "output": {"findings": []},
        },
    ]
    gate_scores = [0.85, 0.40, 0.20]
    sent_scores = [
        [[0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        [[0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
        [[0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    ]
    res = optimize_two_gate_thresholds(val_rows, gate_scores, sent_scores, CODES, max_false_alarms=0)
    assert res["validation_summary"]["fp"] == 0
    assert res["validation_summary"]["tp"] == 1
    assert 0.40 < res["tau_gate"] <= 0.85
