"""Đánh giá thống nhất các mô hình JobShield v3 trên 4 lát cắt bắt buộc."""

from __future__ import annotations

import contextlib
import json
import sys
import zipfile
from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

AI_DIR = Path(__file__).resolve().parents[3] / "services" / "ai"
if str(AI_DIR) not in sys.path:
    sys.path.insert(0, str(AI_DIR))

from preprocessing_v3 import (
    CODES,
    decode_two_gate_predictions,
    encode_document_head_tail,
    encode_sentences,
    normalize_sentences,
)


class TwoHeadClassifier(torch.nn.Module):
    """Kiểu A: 1 encoder chung với 2 đầu ra (cổng câu + 8 mã G01-G08)."""

    def __init__(self, base_dir: Path, num_codes: int = 8):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_dir, local_files_only=True)
        hidden = self.encoder.config.hidden_size
        self.dropout = torch.nn.Dropout(0.1)
        self.gate_head = torch.nn.Linear(hidden, 1)
        self.code_head = torch.nn.Linear(hidden, num_codes)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0, :])
        return self.gate_head(pooled).squeeze(-1), self.code_head(pooled)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _verify_data_sha(data_dir: Path) -> None:
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    for name in ("validation.jsonl", "test.jsonl", "negative_holdout.jsonl", "provenance.jsonl"):
        digest = sha256((data_dir / name).read_bytes()).hexdigest()
        if manifest["sha256"][name] != digest:
            raise ValueError(f"SHA-256 không khớp cho {name}: {digest}")


def _extract_zips(models_dir: Path) -> None:
    for zpath in sorted(models_dir.glob("*.zip")):
        target = models_dir / zpath.stem.removesuffix("-result")
        if (target / "model_meta.json").exists():
            continue
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zpath) as zf:
            zf.extractall(target)


class LoadedModel:
    """Wrapper thống nhất suy luận cho TF-IDF, Kiểu A và Kiểu B."""

    def __init__(self, model_dir: Path, segmenter_provider: Any):
        self.model_dir = model_dir
        self.meta = json.loads((model_dir / "model_meta.json").read_text(encoding="utf-8"))
        self.thresholds = json.loads((model_dir / "thresholds.json").read_text(encoding="utf-8"))
        self.codes = tuple(self.meta.get("codes", CODES))
        self.model_type = self.meta["model_type"]
        self.max_length = int(self.meta.get("max_length", 256))
        self.needs_wseg = bool(self.meta.get("word_segmentation", False))
        self.segmenter = segmenter_provider() if self.needs_wseg else None

        if self.model_type == "tfidf_v3":
            self.gate_model = joblib.load(model_dir / "gate_model.joblib")
            self.code_model = joblib.load(model_dir / "code_model.joblib")
        elif self.model_type == "transformer_typeA":
            ckpt = model_dir / "checkpoint"
            self.tokenizer = AutoTokenizer.from_pretrained(ckpt, local_files_only=True)
            self.model = TwoHeadClassifier(ckpt / "base_model", num_codes=len(self.codes))
            heads = torch.load(ckpt / "two_head_weights.pt", map_location="cpu", weights_only=True)
            self.model.gate_head.load_state_dict(heads["gate_head"])
            self.model.code_head.load_state_dict(heads["code_head"])
            self.model.eval()
        elif self.model_type == "transformer_typeB":
            gate_dir = model_dir / "gate_checkpoint"
            code_dir = model_dir / "code_checkpoint"
            self.gate_tokenizer = AutoTokenizer.from_pretrained(gate_dir, local_files_only=True)
            self.code_tokenizer = AutoTokenizer.from_pretrained(code_dir, local_files_only=True)
            self.gate_model = AutoModelForSequenceClassification.from_pretrained(gate_dir, local_files_only=True).eval()
            self.code_model = AutoModelForSequenceClassification.from_pretrained(code_dir, local_files_only=True).eval()
        else:
            raise ValueError(f"Không hỗ trợ model_type: {self.model_type}")

    @torch.inference_mode()
    def predict_row(self, row: dict[str, Any], force_run_code_model: bool = True) -> dict[str, Any]:
        sentences = normalize_sentences(row)
        sids = [s["id"] for s in sentences]
        tau_gate = float(self.thresholds["tau_gate"])
        code_thresholds = self.thresholds["code_thresholds"]

        if self.model_type == "tfidf_v3":
            doc_text = "\n".join(s["text"] for s in sentences)
            doc_gate = float(self.gate_model.predict_proba([doc_text])[0, 1])
            if not force_run_code_model and doc_gate < tau_gate:
                return {"label": "not_detected", "findings": [], "doc_gate_score": doc_gate}
            sent_scores = self.code_model.predict_proba([s["text"] for s in sentences]).tolist()
        elif self.model_type == "transformer_typeA":
            feats = encode_sentences(sentences, self.tokenizer, self.max_length, self.segmenter)
            gate_scores: list[float] = []
            sent_scores = []
            for start in range(0, len(feats), 16):
                batch = self.tokenizer.pad(feats[start : start + 16], padding=True, return_tensors="pt")
                g_logits, c_logits = self.model(batch["input_ids"], batch["attention_mask"])
                gate_scores.extend(torch.sigmoid(g_logits).tolist())
                sent_scores.extend(torch.sigmoid(c_logits).tolist())
            doc_gate = max(gate_scores) if gate_scores else 0.0
        else:  # transformer_typeB
            doc_feat = encode_document_head_tail(sentences, self.gate_tokenizer, self.max_length, self.segmenter)
            g_inp = self.gate_tokenizer.pad([doc_feat], padding=True, return_tensors="pt")
            g_logit = self.gate_model(**g_inp).logits.squeeze(-1)
            doc_gate = float(torch.sigmoid(g_logit).item())
            if not force_run_code_model and doc_gate < tau_gate:
                return {"label": "not_detected", "findings": [], "doc_gate_score": doc_gate}
            feats = encode_sentences(sentences, self.code_tokenizer, self.max_length, self.segmenter)
            sent_scores = []
            for start in range(0, len(feats), 16):
                batch = self.code_tokenizer.pad(feats[start : start + 16], padding=True, return_tensors="pt")
                logits = self.code_model(**batch).logits
                sent_scores.extend(torch.sigmoid(logits).tolist())

        res = decode_two_gate_predictions(doc_gate, sids, sent_scores, self.codes, tau_gate, code_thresholds)
        res["doc_gate_score"] = doc_gate
        return res


def _f1(tp: int, fp: int, fn: int) -> float:
    d = 2 * tp + fp + fn
    return round((2.0 * tp / d) if d > 0 else 0.0, 4)


def score_slice(rows: list[dict[str, Any]], preds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    truth_pos = {r["sample_id"] for r in rows if r["overall_label"] == "suspicious"}
    pred_pos = {r["sample_id"] for r in rows if preds[r["sample_id"]]["label"] == "suspicious"}
    tp = len(truth_pos & pred_pos)
    fp = len(pred_pos - truth_pos)
    fn = len(truth_pos - pred_pos)
    tn = len(rows) - tp - fp - fn

    gold_pairs = {
        (r["sample_id"], f["code"], sid)
        for r in rows
        for f in r["output"]["findings"]
        for sid in f["evidence_sentence_ids"]
    }
    pred_pairs = {
        (r["sample_id"], f["code"], sid)
        for r in rows
        for f in preds[r["sample_id"]]["findings"]
        for sid in f["evidence_sentence_ids"]
    }
    exact = 0
    for r in rows:
        sid = r["sample_id"]
        g = {(f["code"], x) for f in r["output"]["findings"] for x in f["evidence_sentence_ids"]}
        p = {(f["code"], x) for f in preds[sid]["findings"] for x in f["evidence_sentence_ids"]}
        if preds[sid]["label"] == r["overall_label"] and g == p:
            exact += 1

    per_code: dict[str, dict[str, Any]] = {}
    for code in CODES:
        g_docs = {r["sample_id"] for r in rows if any(f["code"] == code for f in r["output"]["findings"])}
        p_docs = {r["sample_id"] for r in rows if any(f["code"] == code for f in preds[r["sample_id"]]["findings"])}
        g_ev = {x for x in gold_pairs if x[1] == code}
        p_ev = {x for x in pred_pairs if x[1] == code}
        per_code[code] = {
            "support_docs": len(g_docs),
            "pred_docs": len(p_docs),
            "doc_tp": len(g_docs & p_docs),
            "doc_f1": _f1(len(g_docs & p_docs), len(p_docs - g_docs), len(g_docs - p_docs)),
            "evidence_f1": _f1(len(g_ev & p_ev), len(p_ev - g_ev), len(g_ev - p_ev)),
        }

    return {
        "n": len(rows),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(tp / max(1, tp + fp), 4),
        "recall": round(tp / max(1, tp + fn), 4),
        "f1": _f1(tp, fp, fn),
        "accuracy": round((tp + tn) / max(1, len(rows)), 4),
        "missed": fn,
        "false_alarms": fp,
        "exact_match": exact,
        "exact_match_rate": round(exact / max(1, len(rows)), 4),
        "evidence_f1": _f1(len(gold_pairs & pred_pairs), len(pred_pairs - gold_pairs), len(gold_pairs - pred_pairs)),
        "per_code": per_code,
    }


def evaluate_all(
    data_dir: Path,
    models_dir: Path,
    output_dir: Path,
    vncorenlp_dir: Path,
    extract_zips: bool = True,
) -> dict[str, Any]:
    _verify_data_sha(data_dir)
    if extract_zips:
        _extract_zips(models_dir)

    val_rows = _read_jsonl(data_dir / "validation.jsonl")
    test_rows = _read_jsonl(data_dir / "test.jsonl")
    holdout_rows = _read_jsonl(data_dir / "negative_holdout.jsonl")
    prov = {r["sample_id"]: r for r in _read_jsonl(data_dir / "provenance.jsonl")}

    v2_subset_rows = [r for r in test_rows if prov[r["sample_id"]].get("v2_test_subset")]
    by_origin: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in test_rows:
        by_origin[prov[r["sample_id"]]["origin"]].append(r)
    holdout_neg = [r for r in holdout_rows if r["overall_label"] == "not_detected"]
    holdout_pos = [r for r in holdout_rows if r["overall_label"] == "suspicious"]

    segmenter_cache: dict[str, Any] = {}

    def get_segmenter() -> Any:
        if "wseg" not in segmenter_cache:
            import py_vncorenlp

            with contextlib.chdir(vncorenlp_dir):
                segmenter_cache["wseg"] = py_vncorenlp.VnCoreNLP(
                    annotators=["wseg"], save_dir=str(vncorenlp_dir.resolve())
                )
        return segmenter_cache["wseg"]

    model_dirs = sorted(p.parent for p in models_dir.rglob("model_meta.json"))
    all_results: dict[str, Any] = {}
    for mdir in model_dirs:
        loaded = LoadedModel(mdir, get_segmenter)
        name = loaded.meta.get("model_name", mdir.name)
        all_rows = val_rows + test_rows + holdout_rows
        preds = {r["sample_id"]: loaded.predict_row(r, force_run_code_model=False) for r in all_rows}

        val_slice = score_slice(val_rows, preds)
        neg_fa = sum(1 for r in holdout_neg if preds[r["sample_id"]]["label"] == "suspicious")
        pos_hit = sum(1 for r in holdout_pos if preds[r["sample_id"]]["label"] == "suspicious")

        all_results[name] = {
            "meta": loaded.meta,
            "thresholds": loaded.thresholds,
            "validation_parity": val_slice,
            "test_v3_full": score_slice(test_rows, preds),
            "test_v2_subset": score_slice(v2_subset_rows, preds),
            "test_by_origin": {orig: score_slice(grp, preds) for orig, grp in sorted(by_origin.items())},
            "negative_holdout": {
                "total": len(holdout_rows),
                "neg_count": len(holdout_neg),
                "neg_false_alarms": neg_fa,
                "neg_fpr": round(neg_fa / max(1, len(holdout_neg)), 4),
                "pos_count": len(holdout_pos),
                "pos_detected": pos_hit,
            },
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "results.json").write_text(
        json.dumps(all_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    _write_report(output_dir, all_results)
    return all_results


def _write_report(output_dir: Path, all_results: dict[str, Any]) -> None:
    lines = [
        "# Báo cáo so sánh mô hình JobShield v3",
        "",
        "## 1. Tổng hợp trên tập Test v3 (64 mẫu), Test v2 subset (30 mẫu) và Negative Holdout (55 mẫu)",
        "",
        "| Mô hình | Kiến trúc | Test v3 F1 | Precision | Recall | Missed | FA (Test) | Exact Match | Evidence F1 | Test v2 (30) F1 / Exact | Holdout Neg FA (54) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, res in all_results.items():
        t3 = res["test_v3_full"]
        t2 = res["test_v2_subset"]
        nh = res["negative_holdout"]
        arch = res["meta"].get("architecture", "-")
        lines.append(
            f"| `{name}` | {arch} | {t3['f1']:.4f} | {t3['precision']:.4f} | {t3['recall']:.4f} | "
            f"{t3['missed']} | {t3['false_alarms']} | {t3['exact_match']}/{t3['n']} | {t3['evidence_f1']:.4f} | "
            f"{t2['f1']:.4f} / {t2['exact_match']}/{t2['n']} | {nh['neg_false_alarms']}/{nh['neg_count']} ({nh['neg_fpr']:.1%}) |"
        )

    lines.extend(["", "## 2. Phân tách theo nguồn trên Test v3 (`real` vs `real_quoted_excerpt` vs `hard_negative_real`)", ""])
    for name, res in all_results.items():
        lines.append(f"### `{name}`")
        lines.append("| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for orig, sl in res["test_by_origin"].items():
            lines.append(
                f"| `{orig}` | {sl['n']} | {sl['tp']} | {sl['fp']} | {sl['fn']} | {sl['tn']} | "
                f"{sl['f1']:.4f} | {sl['exact_match']}/{sl['n']} |"
            )
        lines.append("")

    cpu_path = output_dir / "cpu_benchmark.json"
    if cpu_path.exists():
        cpu = json.loads(cpu_path.read_text(encoding="utf-8"))
        lines.extend([
            "## 3. Benchmark hiệu năng CPU cục bộ",
            "",
            "| Mô hình | Cold load (s) | VnCoreNLP (s) | Peak RSS (MB) | Latency p50 (ms) | Latency p95 (ms) | Clean p50 (ms) | Suspicious p50 (ms) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for name, bm in cpu.items():
            ov = bm["overall"]
            lines.append(
                f"| `{name}` | {bm['cold_load_sec']:.2f} | {bm['vncorenlp_load_sec']:.2f} | "
                f"{bm['peak_rss_mb']:.1f} | {ov['p50_ms']:.2f} | {ov['p95_ms']:.2f} | "
                f"{bm['by_label']['not_detected']['p50_ms']:.2f} | {bm['by_label']['suspicious']['p50_ms']:.2f} |"
            )
        lines.append("")

    (output_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = ArgumentParser(description="Đánh giá các mô hình JobShield v3.")
    parser.add_argument("--data-dir", type=Path, default=Path(r"d:\DACN\data\v3"))
    parser.add_argument("--models-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\v3"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--vncorenlp-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\vncorenlp"))
    parser.add_argument("--no-extract-zips", action="store_true")
    args = parser.parse_args()
    res = evaluate_all(args.data_dir, args.models_dir, args.output_dir, args.vncorenlp_dir, not args.no_extract_zips)
    print(f"Đã đánh giá {len(res)} mô hình -> {args.output_dir / 'REPORT.md'}")
