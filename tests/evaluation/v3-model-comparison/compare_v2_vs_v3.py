"""Đo đối chiếu trực tiếp PhoBERT v2 (cũ) vs PhoBERT v3 Type A (mới) trên cùng tập test và CPU."""

from __future__ import annotations

import contextlib
import importlib.util
import json
import subprocess
import sys
import time
from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any

import psutil
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

EVAL_DIR = Path(__file__).resolve().parent
AI_DIR = Path(__file__).resolve().parents[3] / "services" / "ai"
for p in (EVAL_DIR, AI_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from benchmark_v3_cpu import _latency_stats, _select_benchmark_samples
from evaluate_v3_models import LoadedModel, _read_jsonl, score_slice
from preprocessing_v3 import CODES, normalize_sentences

V2_TO_V3_CODE: dict[str, str] = {
    "A01": "G01",
    "A04": "G01",
    "A02": "G02",
    "A03": "G02",
    "A05": "G03",
    "A06": "G03",
    "A07": "G04",
    "A16": "G04",
    "A08": "G05",
    "A09": "G05",
    "A10": "G05",
    "A11": "G06",
    "A12": "G07",
    "A13": "G07",
    "A14": "G07",
    "C11": "G08",
    "C12": "G08",
}


class PhoBertV2MappedModel:
    """Nạp PhoBERT v2 và ánh xạ mã A01..C12 sang G01..G08 theo Codebook v3 §2."""

    def __init__(self, v2_dir: Path, segmenter_provider: Any):
        self.v2_dir = v2_dir
        val_meta = json.loads((v2_dir / "validation.json").read_text(encoding="utf-8"))
        self.threshold = float(val_meta["selected"]["threshold"])

        spec = importlib.util.spec_from_file_location("v2_preproc", v2_dir / "preprocessing.py")
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.encode_document = mod.encode_document

        ckpt = v2_dir / "checkpoint"
        self.tokenizer = AutoTokenizer.from_pretrained(ckpt, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(ckpt, local_files_only=True).eval()
        self.segmenter = segmenter_provider()

    @torch.inference_mode()
    def predict_row(self, row: dict[str, Any]) -> dict[str, Any]:
        sentences = normalize_sentences(row)
        features = self.encode_document(sentences, self.segmenter, self.tokenizer)
        ev_by_v3_code: dict[str, set[str]] = {}
        for start in range(0, len(features), 8):
            batch = features[start : start + 8]
            inputs = self.tokenizer.pad(batch, padding=True, return_tensors="pt")
            scores = self.model(**inputs).logits.sigmoid().tolist()
            for offset, s_scores in enumerate(scores):
                sid = sentences[start + offset]["id"]
                for label_id, score in enumerate(s_scores):
                    if score >= self.threshold:
                        v2_code = self.model.config.id2label[label_id]
                        v3_code = V2_TO_V3_CODE.get(v2_code, v2_code)
                        ev_by_v3_code.setdefault(v3_code, set()).add(sid)

        order = {s["id"]: i for i, s in enumerate(sentences)}
        findings = [
            {"code": code, "evidence_sentence_ids": sorted(sids, key=lambda x: order[x])}
            for code, sids in sorted(ev_by_v3_code.items())
        ]
        return {"label": "suspicious" if findings else "not_detected", "findings": findings}


def benchmark_v2_cpu(v2_dir: Path, data_dir: Path, vncorenlp_dir: Path) -> dict[str, Any]:
    proc = psutil.Process()
    samples = _select_benchmark_samples(data_dir)
    vncore_time = {"sec": 0.0}

    def get_seg() -> Any:
        import py_vncorenlp

        t0 = time.perf_counter()
        with contextlib.chdir(vncorenlp_dir):
            seg = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=str(vncorenlp_dir.resolve()))
        vncore_time["sec"] = time.perf_counter() - t0
        return seg

    t_load0 = time.perf_counter()
    model = PhoBertV2MappedModel(v2_dir, get_seg)
    cold_load_sec = time.perf_counter() - t_load0
    _ = model.predict_row(samples[0])

    all_ms: list[float] = []
    by_len: dict[str, list[float]] = {"short": [], "medium": [], "long": []}
    by_label: dict[str, list[float]] = {"not_detected": [], "suspicious": []}
    peak_rss = proc.memory_info().rss

    for row in samples:
        t0 = time.perf_counter()
        _ = model.predict_row(row)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        all_ms.append(dt_ms)
        n_sents = len(row["input"]["sentences"])
        l_bin = "short" if n_sents <= 3 else ("medium" if n_sents <= 7 else "long")
        by_len[l_bin].append(dt_ms)
        by_label[row["overall_label"]].append(dt_ms)
        peak_rss = max(peak_rss, proc.memory_info().rss)

    return {
        "model_name": "phobert-v2",
        "cold_load_sec": round(cold_load_sec, 3),
        "vncorenlp_load_sec": round(vncore_time["sec"], 3),
        "peak_rss_mb": round(peak_rss / (1024 * 1024), 1),
        "overall": _latency_stats(all_ms),
        "by_length": {k: _latency_stats(v) for k, v in by_len.items()},
        "by_label": {k: _latency_stats(v) for k, v in by_label.items()},
    }


def _verify_v3_sha(data_dir: Path) -> None:
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    for name in ("test.jsonl", "negative_holdout.jsonl", "provenance.jsonl"):
        digest = sha256((data_dir / name).read_bytes()).hexdigest()
        if manifest["sha256"][name] != digest:
            raise ValueError(f"SHA-256 không khớp cho {name}")


def run_comparison(
    v3_data_dir: Path,
    v2_data_dir: Path,
    v2_model_dir: Path,
    v3_model_dir: Path,
    vncorenlp_dir: Path,
    output_dir: Path,
) -> None:
    _verify_v3_sha(v3_data_dir)
    test_rows = _read_jsonl(v3_data_dir / "test.jsonl")
    holdout_rows = _read_jsonl(v3_data_dir / "negative_holdout.jsonl")
    prov = {r["sample_id"]: r for r in _read_jsonl(v3_data_dir / "provenance.jsonl")}
    v2_subset_rows = [r for r in test_rows if prov[r["sample_id"]].get("v2_test_subset")]
    v2_raw_test = {r["sample_id"]: r for r in _read_jsonl(v2_data_dir / "test.jsonl")}

    label_same = sum(1 for r in v2_subset_rows if r["overall_label"] == v2_raw_test[r["sample_id"]]["overall_label"])

    by_origin: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in test_rows:
        by_origin[prov[r["sample_id"]]["origin"]].append(r)
    holdout_neg = [r for r in holdout_rows if r["overall_label"] == "not_detected"]
    holdout_pos = [r for r in holdout_rows if r["overall_label"] == "suspicious"]

    seg_cache: dict[str, Any] = {}

    def get_segmenter() -> Any:
        if "wseg" not in seg_cache:
            import py_vncorenlp

            with contextlib.chdir(vncorenlp_dir):
                seg_cache["wseg"] = py_vncorenlp.VnCoreNLP(
                    annotators=["wseg"], save_dir=str(vncorenlp_dir.resolve())
                )
        return seg_cache["wseg"]

    v2_model = PhoBertV2MappedModel(v2_model_dir, get_segmenter)
    v3_model = LoadedModel(v3_model_dir, get_segmenter)

    eval_rows = test_rows + holdout_rows
    v2_preds = {r["sample_id"]: v2_model.predict_row(r) for r in eval_rows}
    v3_preds = {r["sample_id"]: v3_model.predict_row(r, force_run_code_model=False) for r in eval_rows}

    # Benchmark CPU cô lập cho v2 (v3 đã có trong cpu_benchmark.json)
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--benchmark-v2",
        "--v3-data-dir",
        str(v3_data_dir),
        "--v2-model-dir",
        str(v2_model_dir),
        "--vncorenlp-dir",
        str(vncorenlp_dir),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    v2_cpu = json.loads([ln for ln in completed.stdout.splitlines() if ln.strip().startswith("{")][-1])
    v3_cpu = json.loads((output_dir / "cpu_benchmark.json").read_text(encoding="utf-8"))["phobert-v3-typeA"]

    def summarize(preds: dict[str, dict[str, Any]]) -> dict[str, Any]:
        neg_fa = sum(1 for r in holdout_neg if preds[r["sample_id"]]["label"] == "suspicious")
        pos_hit = sum(1 for r in holdout_pos if preds[r["sample_id"]]["label"] == "suspicious")
        return {
            "test_v3_full": score_slice(test_rows, preds),
            "test_v2_subset_on_v3_truth": score_slice(v2_subset_rows, preds),
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

    # Đối chiếu thêm v2 trên đúng nhãn gốc data/v2/test.jsonl (30 mẫu)
    v2_on_v2_truth_correct = sum(
        1 for sid, r in v2_raw_test.items() if v2_preds[sid]["label"] == r["overall_label"]
    )
    v2_on_v2_truth_fa = sum(
        1
        for sid, r in v2_raw_test.items()
        if r["overall_label"] == "not_detected" and v2_preds[sid]["label"] == "suspicious"
    )
    v2_on_v2_truth_fn = sum(
        1
        for sid, r in v2_raw_test.items()
        if r["overall_label"] == "suspicious" and v2_preds[sid]["label"] == "not_detected"
    )

    payload = {
        "v2_vs_v3_subset_label_agreement": {"same": label_same, "total": len(v2_subset_rows)},
        "phobert_v2_on_original_v2_test_30": {
            "label_correct": v2_on_v2_truth_correct,
            "missed": v2_on_v2_truth_fn,
            "false_alarms": v2_on_v2_truth_fa,
        },
        "models": {
            "phobert-v2": {**summarize(v2_preds), "cpu": v2_cpu},
            "phobert-v3-typeA": {**summarize(v3_preds), "cpu": v3_cpu},
        },
    }
    (output_dir / "v2_vs_v3_comparison.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    m2, m3 = payload["models"]["phobert-v2"], payload["models"]["phobert-v3-typeA"]
    lines = [
        "# Đối chiếu trực tiếp PhoBERT v2 (cũ) vs PhoBERT v3 Type A (mới)",
        "",
        f"- Trong **30 mẫu `test` v2** giữ lại trong `test` v3, có **{label_same}/30** mẫu giữ nguyên nhãn tổng; PhoBERT v2 trên nhãn gốc v2 đạt `{v2_on_v2_truth_correct}/30` nhãn đúng (`missed={v2_on_v2_truth_fn}`, `FA={v2_on_v2_truth_fa}`).",
        "- Lưu ý: PhoBERT v2 chỉ được huấn luyện trên **6 mã v2** (`A01, A02, A07, A09, C11, C12`), nên khi ánh xạ sang `G01`–`G08` sẽ bằng `0` ở `G03, G06, G07`.",
        "",
        "## 1. Tổng hợp chất lượng trên các tập chuẩn v3",
        "",
        "| Tập đánh giá | Chỉ số | PhoBERT v2 (cũ) | PhoBERT v3 Type A (mới) | Chênh lệch |",
        "|---|---|---:|---:|---:|",
    ]
    for title, key in [("Test v3 đầy đủ (64 mẫu)", "test_v3_full"), ("Tập con Test v2 (30 mẫu)", "test_v2_subset_on_v3_truth")]:
        s2, s3 = m2[key], m3[key]
        lines.extend([
            f"| {title} | **F1 nhãn tổng** | {s2['f1']:.4f} | **{s3['f1']:.4f}** | {s3['f1'] - s2['f1']:+.4f} |",
            f"| {title} | Precision | {s2['precision']:.4f} | **{s3['precision']:.4f}** | {s3['precision'] - s2['precision']:+.4f} |",
            f"| {title} | Recall | {s2['recall']:.4f} | {s3['recall']:.4f} | {s3['recall'] - s2['recall']:+.4f} |",
            f"| {title} | Báo nhầm (False Alarms) | {s2['false_alarms']} | **{s3['false_alarms']}** | {s3['false_alarms'] - s2['false_alarms']:+d} |",
            f"| {title} | Bỏ sót (Missed) | {s2['missed']} | {s3['missed']} | {s3['missed'] - s2['missed']:+d} |",
            f"| {title} | Exact Match | {s2['exact_match']}/{s2['n']} | **{s3['exact_match']}/{s3['n']}** | {s3['exact_match'] - s2['exact_match']:+d} |",
            f"| {title} | Evidence F1 (mã `G01`–`G08`) | {s2['evidence_f1']:.4f} | **{s3['evidence_f1']:.4f}** | {s3['evidence_f1'] - s2['evidence_f1']:+.4f} |",
        ])
    nh2, nh3 = m2["negative_holdout"], m3["negative_holdout"]
    lines.append(
        f"| Negative Holdout (54 âm) | Báo nhầm (FPR) | {nh2['neg_false_alarms']}/54 ({nh2['neg_fpr']:.1%}) | **{nh3['neg_false_alarms']}/54 ({nh3['neg_fpr']:.1%})** | {nh3['neg_false_alarms'] - nh2['neg_false_alarms']:+d} |"
    )

    lines.extend([
        "",
        "## 2. Phân tách theo nguồn trên Test v3 (`64` mẫu)",
        "",
        "| Nguồn (`origin`) | N | v2 F1 / Đúng nhãn | v3 Type A F1 / Đúng nhãn |",
        "|---|---:|---:|---:|",
    ])
    for orig in sorted(by_origin):
        o2, o3 = m2["test_by_origin"][orig], m3["test_by_origin"][orig]
        c2 = o2["tp"] + o2["tn"]
        c3 = o3["tp"] + o3["tn"]
        lines.append(f"| `{orig}` | {o2['n']} | {o2['f1']:.4f} ({c2}/{o2['n']}) | **{o3['f1']:.4f} ({c3}/{o3['n']})** |")

    lines.extend([
        "",
        "## 3. Phân tách từng nhóm hành vi `G01`–`G08` trên Test v3 (`doc_f1` / `evidence_f1`)",
        "",
        "| Mã nhóm | Số mẫu Test | v2 `doc_f1` / `ev_f1` | v3 Type A `doc_f1` / `ev_f1` |",
        "|---|---:|---:|---:|",
    ])
    for code in CODES:
        p2, p3 = m2["test_v3_full"]["per_code"][code], m3["test_v3_full"]["per_code"][code]
        lines.append(f"| `{code}` | {p3['support_docs']} | {p2['doc_f1']:.2f} / {p2['evidence_f1']:.2f} | {p3['doc_f1']:.2f} / {p3['evidence_f1']:.2f} |")

    c2, c3 = m2["cpu"], m3["cpu"]
    lines.extend([
        "",
        "## 4. Hiệu năng CPU cục bộ (cùng 25 mẫu benchmark)",
        "",
        "| Chỉ số CPU | PhoBERT v2 (cũ) | PhoBERT v3 Type A (mới) |",
        "|---|---:|---:|",
        f"| Cold load (s) | {c2['cold_load_sec']:.3f} | {c3['cold_load_sec']:.3f} |",
        f"| VnCoreNLP load (s) | {c2['vncorenlp_load_sec']:.3f} | {c3['vncorenlp_load_sec']:.3f} |",
        f"| Peak RSS RAM (MB) | {c2['peak_rss_mb']:.1f} | {c3['peak_rss_mb']:.1f} |",
        f"| Latency p50 (ms) | {c2['overall']['p50_ms']:.2f} | {c3['overall']['p50_ms']:.2f} |",
        f"| Latency p95 (ms) | {c2['overall']['p95_ms']:.2f} | {c3['overall']['p95_ms']:.2f} |",
        f"| Tin sạch p50 (ms) | {c2['by_label']['not_detected']['p50_ms']:.2f} | {c3['by_label']['not_detected']['p50_ms']:.2f} |",
        f"| Tin nghi ngờ p50 (ms) | {c2['by_label']['suspicious']['p50_ms']:.2f} | {c3['by_label']['suspicious']['p50_ms']:.2f} |",
    ])

    (output_dir / "V2_VS_V3_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = ArgumentParser(description="Đối chiếu PhoBERT v2 vs PhoBERT v3 Type A.")
    parser.add_argument("--v3-data-dir", type=Path, default=Path(r"d:\DACN\data\v3"))
    parser.add_argument("--v2-data-dir", type=Path, default=Path(r"d:\DACN\data\v2"))
    parser.add_argument("--v2-model-dir", type=Path, default=Path(r"d:\DACN\JobShield\services\ai\jobshield-phobert-v2-result"))
    parser.add_argument("--v3-model-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\v3\jobshield-phobert-v3-typeA"))
    parser.add_argument("--vncorenlp-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\vncorenlp"))
    parser.add_argument("--output-dir", type=Path, default=EVAL_DIR)
    parser.add_argument("--benchmark-v2", action="store_true")
    args = parser.parse_args()

    if args.benchmark_v2:
        print(json.dumps(benchmark_v2_cpu(args.v2_model_dir, args.v3_data_dir, args.vncorenlp_dir), ensure_ascii=False))
    else:
        run_comparison(
            args.v3_data_dir, args.v2_data_dir, args.v2_model_dir, args.v3_model_dir, args.vncorenlp_dir, args.output_dir
        )
        print("Done ->", args.output_dir / "V2_VS_V3_REPORT.md")
