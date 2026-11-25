from contextlib import chdir
from importlib import import_module
from pathlib import Path
from threading import Lock

import py_vncorenlp
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# Dùng đúng hàm mã hóa được xuất cùng checkpoint v2.
encode_document = import_module(
    "jobshield-phobert-v2-result.preprocessing"
).encode_document


class PhoBertV2Classifier:
    THRESHOLD = 0.45
    BATCH_SIZE = 8

    def __init__(self, checkpoint: Path, segmenter_dir: Path):
        checkpoint = checkpoint.resolve()
        segmenter_dir = segmenter_dir.resolve()

        self.tokenizer = AutoTokenizer.from_pretrained(
            checkpoint, local_files_only=True
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            checkpoint, local_files_only=True
        ).eval()

        # VnCoreNLP thay đổi thư mục làm việc khi khởi tạo.
        with chdir(segmenter_dir):
            self.segmenter = py_vncorenlp.VnCoreNLP(
                annotators=["wseg"], save_dir=str(segmenter_dir)
            )
        self.segmenter_lock = Lock()

    @torch.inference_mode()
    def predict(self, sentences: list[dict[str, str]]) -> dict:
        if not sentences:
            raise ValueError("Danh sách câu không được để trống.")

        with self.segmenter_lock:
            features = encode_document(sentences, self.segmenter, self.tokenizer)

        evidence_by_code: dict[str, list[str]] = {}

        for start in range(0, len(features), self.BATCH_SIZE):
            batch = features[start : start + self.BATCH_SIZE]
            inputs = self.tokenizer.pad(batch, padding=True, return_tensors="pt")
            scores = self.model(**inputs).logits.sigmoid()

            for offset, sentence_scores in enumerate(scores.tolist()):
                sentence_id = sentences[start + offset]["id"]

                for label_id, score in enumerate(sentence_scores):
                    if score >= self.THRESHOLD:
                        code = self.model.config.id2label[label_id]
                        evidence_by_code.setdefault(code, []).append(sentence_id)

        findings = [
            {"code": code, "evidence_sentence_ids": sentence_ids}
            for code, sentence_ids in sorted(evidence_by_code.items())
        ]

        return {
            "label": "suspicious" if findings else "not_detected",
            "findings": findings,
        }
