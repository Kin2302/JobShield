"""Huấn luyện baseline TF-IDF + Logistic Regression cho JobShield v3 (2 cổng)."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import make_pipeline

from preprocessing_v3 import CODES, optimize_two_gate_thresholds

SEED = 42


def _read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _doc_text(row: dict) -> str:
    return "\n".join(s["text"] for s in row["input"]["sentences"])


def run_tfidf_v3(data_dir: Path, output_dir: Path) -> None:
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    hashes = {
        name: sha256((data_dir / name).read_bytes()).hexdigest()
        for name in ("train.jsonl", "validation.jsonl")
    }
    for name, digest in hashes.items():
        if manifest["sha256"][name] != digest:
            raise ValueError(f"SHA-256 không khớp cho {name}: {digest}")

    train_rows = _read_jsonl(data_dir / "train.jsonl")
    val_rows = _read_jsonl(data_dir / "validation.jsonl")

    # Mô hình 1: Cổng cấp tài liệu (không ghép prefix type/speaker để tránh học tắt)
    gate_model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2, max_features=60000),
        LogisticRegression(max_iter=1000, class_weight="balanced", C=2.0, random_state=SEED),
    )
    gate_model.fit(
        [_doc_text(r) for r in train_rows],
        [1 if r["overall_label"] == "suspicious" else 0 for r in train_rows],
    )

    # Mô hình 2: Phân loại đa nhãn G01-G08 cấp câu
    sent_texts: list[str] = []
    sent_labels: list[list[int]] = []
    for row in train_rows:
        gold = {
            (f["code"], sid)
            for f in row["output"]["findings"]
            for sid in f["evidence_sentence_ids"]
        }
        for sent in row["input"]["sentences"]:
            sent_texts.append(sent["text"])
            sent_labels.append([1 if (code, sent["id"]) in gold else 0 for code in CODES])

    code_model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2, max_features=60000),
        OneVsRestClassifier(
            LogisticRegression(max_iter=1000, class_weight="balanced", C=2.0, random_state=SEED)
        ),
    )
    code_model.fit(sent_texts, np.asarray(sent_labels, dtype=np.int32))

    # Tối ưu ngưỡng trên validation
    val_gate_scores = gate_model.predict_proba([_doc_text(r) for r in val_rows])[:, 1].tolist()
    val_sent_scores_by_doc: list[list[list[float]]] = []
    for row in val_rows:
        probs = code_model.predict_proba([s["text"] for s in row["input"]["sentences"]])
        val_sent_scores_by_doc.append(probs.tolist())

    tuned = optimize_two_gate_thresholds(
        val_rows, val_gate_scores, val_sent_scores_by_doc, CODES, max_false_alarms=2
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    gate_path = output_dir / "gate_model.joblib"
    code_path = output_dir / "code_model.joblib"
    joblib.dump(gate_model, gate_path)
    joblib.dump(code_model, code_path)

    # Xác minh reload khớp dự đoán
    reloaded_gate = joblib.load(gate_path)
    reloaded_code = joblib.load(code_path)
    reloaded_gate_scores = reloaded_gate.predict_proba([_doc_text(r) for r in val_rows])[:, 1].tolist()
    np.testing.assert_allclose(reloaded_gate_scores, val_gate_scores, rtol=1e-12, atol=1e-12)
    for row, orig_scores in zip(val_rows, val_sent_scores_by_doc, strict=True):
        re_scores = reloaded_code.predict_proba([s["text"] for s in row["input"]["sentences"]])
        np.testing.assert_allclose(re_scores, orig_scores, rtol=1e-12, atol=1e-12)

    meta = {
        "model_name": "tfidf-v3",
        "model_type": "tfidf_v3",
        "architecture": "typeB",
        "dataset_version": "v3",
        "seed": SEED,
        "codes": list(CODES),
        "anti_shortcut": True,
        "train_samples": len(train_rows),
        "validation_samples": len(val_rows),
        "dataset_sha256": hashes,
        "scikit_learn_version": sklearn.__version__,
        "reload_verified": True,
    }
    (output_dir / "model_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "thresholds.json").write_text(
        json.dumps(
            {"tau_gate": tuned["tau_gate"], "code_thresholds": tuned["code_thresholds"]},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "validation.json").write_text(
        json.dumps({**meta, **tuned}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("TF-IDF v3 validation:", json.dumps(tuned["validation_summary"], ensure_ascii=False))


if __name__ == "__main__":
    parser = ArgumentParser(description="Huấn luyện baseline TF-IDF JobShield v3.")
    parser.add_argument("--data-dir", type=Path, default=Path(r"d:\DACN\data\v3"))
    parser.add_argument("--output-dir", type=Path, default=Path(r"d:\DACN\JobShield\models\v3\tfidf-v3"))
    args = parser.parse_args()
    run_tfidf_v3(args.data_dir, args.output_dir)
