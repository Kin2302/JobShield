import json
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
from random import Random


def agreed_label(annotation: dict) -> str | None:
    first = annotation.get("A") or {}
    second = annotation.get("B") or {}

    if first.get("selection") != "candidate" or second.get("selection") != "candidate":
        return None

    label = first.get("overall_label_proposal")
    if label in {"suspicious", "not_detected"} and label == second.get("overall_label_proposal"):
        return label

    return None


def load_samples(data_dir: Path) -> list[dict]:
    def read_rows(filename: str) -> list[dict]:
        with (data_dir / filename).open(encoding="utf-8") as file:
            return [json.loads(line) for line in file]

    inputs = {row["sample_id"]: row for row in read_rows("inputs.jsonl")}
    provenance = {row["sample_id"]: row for row in read_rows("provenance.jsonl")}

    samples = []
    for annotation in read_rows("annotations.jsonl"):
        label = agreed_label(annotation)
        if label is None:
            continue

        sample_id = annotation["sample_id"]
        source = provenance[sample_id]
        segments = inputs[sample_id]["segments"]
        samples.append({
            "sample_id": sample_id,
            "text": "\n".join(segment["text"] for segment in segments),
            "label": label,
            "group_id": source["split_group_id"],
            "train_only": source.get("split_constraint") == "train_only",
        })

    return samples


def split_samples(
    samples: list[dict], data_dir: Path
) -> tuple[list[dict], list[dict]]:
    with (data_dir / "provenance.jsonl").open(encoding="utf-8") as file:
        provenance = {
            row["sample_id"]: row
            for row in map(json.loads, file)
        }

    parents = {
        row["split_group_id"]: row["split_group_id"]
        for row in provenance.values()
    }

    def root(group_id: str) -> str:
        while parents[group_id] != group_id:
            parents[group_id] = parents[parents[group_id]]
            group_id = parents[group_id]
        return group_id

    with (data_dir / "review-queue.jsonl").open(encoding="utf-8") as file:
        for row in map(json.loads, file):
            group_id = provenance[row["sample_id"]]["split_group_id"]
            for neighbor in row.get("similar_inputs", []):
                other_group = provenance[neighbor["sample_id"]]["split_group_id"]
                parents[root(other_group)] = root(group_id)

    train_only_groups = {
        root(row["split_group_id"])
        for row in provenance.values()
        if row.get("split_constraint") == "train_only"
    }
    eligible_groups = sorted(
        {root(sample["group_id"]) for sample in samples} - train_only_groups
    )
    if len(eligible_groups) < 2:
        raise ValueError("Cần ít nhất hai nhóm đủ điều kiện để chia tập.")

    holdout_count = max(1, round(len(eligible_groups) * 0.2))
    holdout_groups = set(Random(42).sample(eligible_groups, holdout_count))

    train, holdout = [], []
    for sample in samples:
        target = holdout if root(sample["group_id"]) in holdout_groups else train
        target.append(sample)

    return train, holdout


def load_packaged_samples(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [
            {
                "sample_id": row["sample_id"],
                "text": "\n".join(segment["text"] for segment in row["segments"]),
                "label": row["label"],
            }
            for row in map(json.loads, file)
        ]


def run_baseline(
    data_dir: Path, output_dir: Path, training_package: bool = False
) -> None:
    import joblib
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix
    from sklearn.pipeline import make_pipeline

    if training_package:
        manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
        hashes = {
            filename: sha256((data_dir / filename).read_bytes()).hexdigest()
            for filename in ("train.jsonl", "negative_holdout.jsonl", "provenance.jsonl")
        }
        if any(manifest["output_sha256"][name] != digest for name, digest in hashes.items()):
            raise ValueError("Tệp dữ liệu không khớp SHA-256 trong manifest.")
        train = load_packaged_samples(data_dir / "train.jsonl")
        holdout = load_packaged_samples(data_dir / "negative_holdout.jsonl")
        if not holdout or {sample["label"] for sample in holdout} != {"not_detected"}:
            raise ValueError("Tập đối chứng phải có mẫu và chỉ chứa nhãn not_detected.")
    else:
        train, holdout = split_samples(load_samples(data_dir), data_dir)
    train_texts = [sample["text"] for sample in train]
    train_labels = [sample["label"] for sample in train]
    holdout_texts = [sample["text"] for sample in holdout]
    holdout_labels = [sample["label"] for sample in holdout]

    model = make_pipeline(
        TfidfVectorizer(analyzer="char", ngram_range=(3, 5)),
        LogisticRegression(),
    )
    model.fit(train_texts, train_labels)
    predictions = model.predict(holdout_texts)

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.joblib"
    joblib.dump(model, model_path)
    reloaded = joblib.load(model_path)
    if reloaded.predict(holdout_texts).tolist() != predictions.tolist():
        raise RuntimeError("Dự đoán thay đổi sau khi nạp lại model.")

    with (data_dir / "provenance.jsonl").open(encoding="utf-8") as file:
        origins = {
            row["sample_id"]: row["origin"]
            for row in map(json.loads, file)
        }

    def summarize(samples: list[dict]) -> dict:
        return {
            "count": len(samples),
            "labels": dict(Counter(sample["label"] for sample in samples)),
            "origins": dict(Counter(origins[sample["sample_id"]] for sample in samples)),
        }

    labels = ["not_detected", "suspicious"]
    report = {
        "purpose": "pipeline_smoke_test",
        "scikit_learn_version": sklearn.__version__,
        "train": summarize(train),
        "holdout": summarize(holdout),
        "confusion_matrix_label_order": labels,
        "confusion_matrix": confusion_matrix(
            holdout_labels, predictions, labels=labels
        ).tolist(),
        "reload_predictions_match": True,
    }
    if training_package:
        false_positives = report["confusion_matrix"][0][1]
        report.update(
            purpose="internal_negative_holdout",
            dataset_sha256=hashes,
            false_positives=false_positives,
            false_positive_rate=false_positives / len(holdout),
        )
    (output_dir / "report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = ArgumentParser(description="Chạy thử baseline TF-IDF offline.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--training-package", action="store_true")
    args = parser.parse_args()
    run_baseline(args.data_dir, args.output_dir, args.training_package)
