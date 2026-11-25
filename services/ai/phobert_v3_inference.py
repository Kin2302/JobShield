"""Suy luận hai cổng cho mô hình PhoBERT v3 Kiểu A."""

from __future__ import annotations

import json
from contextlib import chdir
from pathlib import Path
from threading import Lock
from typing import Any

import py_vncorenlp
import torch
from transformers import AutoModel, AutoTokenizer

from preprocessing_v3 import (
    CODES,
    decode_two_gate_predictions,
    encode_sentences,
    normalize_sentences,
)


class TwoHeadClassifier(torch.nn.Module):
    """Kiểu A: 1 encoder chung với 2 đầu ra (cổng câu + 8 mã G01-G08)."""

    def __init__(self, base_dir: Path, num_codes: int = 8) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base_dir, local_files_only=True)
        hidden = self.encoder.config.hidden_size
        self.dropout = torch.nn.Dropout(0.1)
        self.gate_head = torch.nn.Linear(hidden, 1)
        self.code_head = torch.nn.Linear(hidden, num_codes)

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.dropout(out.last_hidden_state[:, 0, :])
        return self.gate_head(pooled).squeeze(-1), self.code_head(pooled)


class PhoBertV3TypeAClassifier:
    """Bộ phân loại JobShield v3 (PhoBERT Kiểu A + ngưỡng hai cổng)."""

    BATCH_SIZE = 16

    def __init__(self, model_dir: Path, segmenter_dir: Path) -> None:
        model_dir = model_dir.resolve()
        segmenter_dir = segmenter_dir.resolve()

        meta = json.loads((model_dir / "model_meta.json").read_text(encoding="utf-8"))
        thresholds = json.loads((model_dir / "thresholds.json").read_text(encoding="utf-8"))

        self.model_name: str = meta.get("model_name", model_dir.name)
        self.codes: tuple[str, ...] = tuple(meta.get("codes", CODES))
        self.max_length: int = int(meta.get("max_length", 256))
        self.tau_gate: float = float(thresholds["tau_gate"])
        self.code_thresholds: dict[str, float] = {
            str(k): float(v) for k, v in thresholds["code_thresholds"].items()
        }

        ckpt = model_dir / "checkpoint"
        self.tokenizer = AutoTokenizer.from_pretrained(ckpt, local_files_only=True)
        self.model = TwoHeadClassifier(ckpt / "base_model", num_codes=len(self.codes))
        heads = torch.load(
            ckpt / "two_head_weights.pt", map_location="cpu", weights_only=True
        )
        self.model.gate_head.load_state_dict(heads["gate_head"])
        self.model.code_head.load_state_dict(heads["code_head"])
        self.model.eval()

        # VnCoreNLP thay đổi thư mục làm việc khi khởi tạo.
        with chdir(segmenter_dir):
            self.segmenter = py_vncorenlp.VnCoreNLP(
                annotators=["wseg"], save_dir=str(segmenter_dir)
            )
        self.segmenter_lock = Lock()

    @torch.inference_mode()
    def predict(self, sentences: list[dict[str, Any]]) -> dict[str, Any]:
        if not sentences:
            raise ValueError("Danh sách câu không được để trống.")

        normalized = normalize_sentences(sentences)
        sids = [s["id"] for s in normalized]

        with self.segmenter_lock:
            features = encode_sentences(
                normalized, self.tokenizer, self.max_length, self.segmenter
            )

        gate_scores: list[float] = []
        sent_scores: list[list[float]] = []
        for start in range(0, len(features), self.BATCH_SIZE):
            batch = self.tokenizer.pad(
                features[start : start + self.BATCH_SIZE],
                padding=True,
                return_tensors="pt",
            )
            g_logits, c_logits = self.model(
                batch["input_ids"], batch["attention_mask"]
            )
            gate_scores.extend(torch.sigmoid(g_logits).tolist())
            sent_scores.extend(torch.sigmoid(c_logits).tolist())

        doc_gate = max(gate_scores) if gate_scores else 0.0
        return decode_two_gate_predictions(
            doc_gate,
            sids,
            sent_scores,
            self.codes,
            self.tau_gate,
            self.code_thresholds,
        )
