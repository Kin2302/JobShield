"""Benchmark tốc độ CPU (cold load, latency p50/p95, peak RSS RAM) cho các mô hình v3."""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import numpy as np
import psutil

EVAL_DIR = Path(__file__).resolve().parent
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))

from evaluate_v3_models import LoadedModel, _read_jsonl, _write_report


def _select_benchmark_samples(data_dir: Path) -> list[dict[str, Any]]:
    test_rows = _read_jsonl(data_dir / "test.jsonl")
    holdout_rows = _read_jsonl(data_dir / "negative_holdout.jsonl")
    # Lấy 30 mẫu đại diện cân bằng ngắn (1-3), trung bình (4-7), dài (8+) và cả 2 nhãn
    pool = test_rows + holdout_rows
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in pool:
        n_sents = len(row["input"]["sentences"])
        length_bin = "short" if n_sents <= 3 else ("medium" if n_sents <= 7 else "long")
        key = (row["overall_label"], length_bin)
        buckets.setdefault(key, []).append(row)

    selected: list[dict[str, Any]] = []
    for key in sorted(buckets):
        selected.extend(buckets[key][:5])
    return selected[:30]


def _latency_stats(ms_list: list[float]) -> dict[str, float]:
    if not ms_list:
        return {"n": 0, "mean_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0}
    arr = np.asarray(ms_list, dtype=np.float64)
    return {
        "n": len(ms_list),
        "mean_ms": round(float(np.mean(arr)), 2),
        "p50_ms": round(float(np.percentile(arr, 50)), 2),
        "p95_ms": round(float(np.percentile(arr, 95)), 2),
    }


def benchmark_single_model(model_dir: Path, data_dir: Path, vncorenlp_dir: Path) -> dict[str, Any]:
    proc = psutil.Process()
    samples = _select_benchmark_samples(data_dir)
    vncore_time = {"sec": 0.0}

    def get_segmenter() -> Any:
        import py_vncorenlp

        t0 = time.perf_counter()
        with contextlib.chdir(vncorenlp_dir):
            seg = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=str(vncorenlp_dir.resolve()))
        vncore_time["sec"] = time.perf_counter() - t0
        return seg

    t_load0 = time.perf_counter()
    loaded = LoadedModel(model_dir, get_segmenter)
    cold_load_sec = time.perf_counter() - t_load0

    # 1 lượt warm-up ngoài phép đo chính
    _ = loaded.predict_row(samples[0], force_run_code_model=False)

    all_ms: list[float] = []
    by_len: dict[str, list[float]] = {"short": [], "medium": [], "long": []}
    by_label: dict[str, list[float]] = {"not_detected": [], "suspicious": []}
    peak_rss = proc.memory_info().rss

    for row in samples:
        t0 = time.perf_counter()
        _ = loaded.predict_row(row, force_run_code_model=False)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        all_ms.append(dt_ms)
        n_sents = len(row["input"]["sentences"])
        l_bin = "short" if n_sents <= 3 else ("medium" if n_sents <= 7 else "long")
        by_len[l_bin].append(dt_ms)
        by_label[row["overall_label"]].append(dt_ms)
        peak_rss = max(peak_rss, proc.memory_info().rss)

    return {
        "model_name": loaded.meta.get("model_name", model_dir.name),
        "model_type": loaded.model_type,
        "cold_load_sec": round(cold_load_sec, 3),
        "vncorenlp_load_sec": round(vncore_time["sec"], 3),
        "peak_rss_mb": round(peak_rss / (1024 * 1024), 1),
        "overall": _latency_stats(all_ms),
        "by_length": {k: _latency_stats(v) for k, v in by_len.items()},
        "by_label": {k: _latency_stats(v) for k, v in by_label.items()},
    }


def main() -> None:
    parser = ArgumentParser(description="Benchmark CPU cho các mô hình JobShield v3.")
    parser.add_argument("--data-dir", type=Path, default=Path(r"d:\DACN\data\v3"))
    parser.add_argument("--models-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\v3"))
    parser.add_argument("--output-dir", type=Path, default=EVAL_DIR)
    parser.add_argument("--vncorenlp-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\vncorenlp"))
    parser.add_argument("--single-model", type=Path, default=None)
    args = parser.parse_args()

    if args.single_model is not None:
        result = benchmark_single_model(args.single_model, args.data_dir, args.vncorenlp_dir)
        print(json.dumps(result, ensure_ascii=False))
        return

    model_dirs = sorted(p.parent for p in args.models_dir.rglob("model_meta.json"))
    all_benchmarks: dict[str, Any] = {}
    for mdir in model_dirs:
        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--single-model",
            str(mdir),
            "--data-dir",
            str(args.data_dir),
            "--vncorenlp-dir",
            str(args.vncorenlp_dir),
        ]
        completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Dòng cuối cùng là JSON kết quả
        last_line = [ln for ln in completed.stdout.splitlines() if ln.strip().startswith("{")][-1]
        bm = json.loads(last_line)
        all_benchmarks[bm["model_name"]] = bm
        print(
            f"[CPU] {bm['model_name']}: load={bm['cold_load_sec']}s, "
            f"p50={bm['overall']['p50_ms']}ms, p95={bm['overall']['p95_ms']}ms, "
            f"peak_rss={bm['peak_rss_mb']}MB"
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "cpu_benchmark.json").write_text(
        json.dumps(all_benchmarks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    results_file = args.output_dir / "results.json"
    if results_file.exists():
        _write_report(args.output_dir, json.loads(results_file.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main()
