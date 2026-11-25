import json
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path

from train_tfidf import load_packaged_samples

MODEL_ID = "vinai/phobert-base"
LABEL_TO_ID = {"not_detected": 0, "suspicious": 1}
MAX_TOKENS = 256
SEED = 42
EPOCHS = 3
BATCH_SIZE = 8
LEARNING_RATE = 2e-5


def load_training_data(data_dir, smoke_test):
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    expected_counts = manifest["split_counts"]
    split_names = ["train", "negative_holdout"]
    if "validation" in expected_counts:
        split_names.append("validation")
    filenames = {split: f"{split}.jsonl" for split in split_names}
    expected = manifest["output_sha256"]
    hashes = {
        name: sha256((data_dir / name).read_bytes()).hexdigest()
        for name in filenames.values()
    }
    if any(expected[name] != digest for name, digest in hashes.items()):
        raise ValueError("Training files do not match the manifest SHA-256.")

    samples = {
        split: load_packaged_samples(data_dir / name)
        for split, name in filenames.items()
    }
    counts = {
        split: dict(Counter(row["label"] for row in rows))
        for split, rows in samples.items()
    }
    if (
        set(counts["train"]) != set(LABEL_TO_ID)
        or set(counts["negative_holdout"]) != {"not_detected"}
        or ("validation" in counts and set(counts["validation"]) != set(LABEL_TO_ID))
        or counts != expected_counts
    ):
        raise ValueError("Unexpected label counts for this training run.")

    if "validation" not in counts and not smoke_test and counts != {
        "train": {"not_detected": 548, "suspicious": 141},
        "negative_holdout": {"not_detected": 55},
    }:
        raise ValueError("Unexpected label counts for this training run.")

    sample_ids = [row["sample_id"] for rows in samples.values() for row in rows]
    if len(set(sample_ids)) != len(sample_ids):
        raise ValueError("Sample IDs must be unique and disjoint across splits.")
    return samples, hashes, counts


def summarize_validation(samples, predictions):
    suspicious = LABEL_TO_ID["suspicious"]
    not_detected = LABEL_TO_ID["not_detected"]
    pairs = Counter(
        (LABEL_TO_ID[sample["label"]], prediction)
        for sample, prediction in zip(samples, predictions, strict=True)
    )
    true_positives = pairs[suspicious, suspicious]
    false_positives = pairs[not_detected, suspicious]
    false_negatives = pairs[suspicious, not_detected]
    f1_denominator = 2 * true_positives + false_positives + false_negatives
    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_negatives": pairs[not_detected, not_detected],
        "suspicious_f1": 2 * true_positives / f1_denominator,
    }


def encode_samples(samples, segmenter, tokenizer):
    encoded = []
    truncated_count = 0
    special_tokens = tokenizer.num_special_tokens_to_add()
    for sample in samples:
        text = " ".join(segmenter.word_segment(sample["text"]))
        token_ids = tokenizer.encode(text, add_special_tokens=False, verbose=False)
        if len(token_ids) + special_tokens > MAX_TOKENS:
            truncated_count += 1
        item = tokenizer.prepare_for_model(
            token_ids, max_length=MAX_TOKENS, truncation=True,
            return_attention_mask=True,
        )
        item["labels"] = LABEL_TO_ID[sample["label"]]
        encoded.append(dict(item))
    return encoded, truncated_count


def run(data_dir, output_dir, segmenter_dir, smoke_test):
    import py_vncorenlp
    import torch
    import transformers
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    samples, hashes, counts = load_training_data(data_dir, smoke_test)
    train, holdout = samples["train"], samples["negative_holdout"]
    if not torch.cuda.is_available():
        raise RuntimeError("Select a GPU runtime in Colab before running this script.")

    segmenter_dir.mkdir(parents=True, exist_ok=True)
    py_vncorenlp.download_model(save_dir=str(segmenter_dir))
    segmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=str(segmenter_dir))
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    train_features, train_truncated = encode_samples(train, segmenter, tokenizer)
    holdout_features, holdout_truncated = encode_samples(holdout, segmenter, tokenizer)

    set_seed(SEED)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID,
        label2id=LABEL_TO_ID,
        id2label={index: label for label, index in LABEL_TO_ID.items()},
    )
    args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=EPOCHS,
        max_steps=2 if smoke_test else -1,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        seed=SEED,
        save_strategy="no",
        report_to="none",
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_features,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer),
    )
    result = trainer.train()
    original = trainer.predict(holdout_features).predictions.argmax(axis=-1).tolist()

    checkpoint = output_dir / "checkpoint"
    trainer.save_model(str(checkpoint))
    del trainer, model
    torch.cuda.empty_cache()
    restored_tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True)
    restored_features, _ = encode_samples(holdout, segmenter, restored_tokenizer)
    restored_model = AutoModelForSequenceClassification.from_pretrained(
        checkpoint, local_files_only=True
    )
    predictor = Trainer(
        model=restored_model,
        args=args,
        processing_class=restored_tokenizer,
        data_collator=DataCollatorWithPadding(restored_tokenizer),
    )
    restored = predictor.predict(restored_features).predictions.argmax(axis=-1).tolist()
    if original != restored:
        raise RuntimeError("Predicted labels changed after reloading the checkpoint.")

    false_positives = restored.count(LABEL_TO_ID["suspicious"])
    report = {
        "purpose": "pipeline_smoke_test" if smoke_test else "internal_negative_holdout",
        "model": MODEL_ID,
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "gpu": torch.cuda.get_device_name(),
        "training": {
            "seed": SEED,
            "epochs": result.metrics["epoch"],
            "steps": result.global_step,
            "learning_rate": LEARNING_RATE,
            "batch_size": BATCH_SIZE,
            "max_tokens": MAX_TOKENS,
        },
        "dataset_sha256": hashes,
        "split_counts": counts,
        "truncated_samples": {"train": train_truncated, "negative_holdout": holdout_truncated},
        "reload_predictions_match": True,
        "false_positives": false_positives,
        "false_positive_rate": false_positives / len(holdout),
        "holdout_predictions": [
            {"sample_id": row["sample_id"], "label": restored_model.config.id2label[label]}
            for row, label in zip(holdout, restored, strict=True)
        ],
    }
    if "validation" in samples:
        validation = samples["validation"]
        validation_features, validation_truncated = encode_samples(validation, segmenter, restored_tokenizer)
        predictions = predictor.predict(validation_features).predictions.argmax(axis=-1).tolist()
        report["validation_metrics"] = summarize_validation(validation, predictions)
        report["truncated_samples"]["validation"] = validation_truncated
        if not smoke_test:
            report["purpose"] = "internal_validation_and_negative_holdout"

    report_path = output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    parser = ArgumentParser(description="Fine-tune PhoBERT for JobShield on a GPU.")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--segmenter-dir", type=Path, required=True)
    parser.add_argument("--smoke-test", action="store_true")
    options = parser.parse_args()
    run(
        options.data_dir.resolve(),
        options.output_dir.resolve(),
        options.segmenter_dir.resolve(),
        options.smoke_test,
    )
