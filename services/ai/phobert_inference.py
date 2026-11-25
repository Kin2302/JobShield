import logging
from contextlib import chdir
from pathlib import Path
from threading import Lock

import py_vncorenlp
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from train_phobert import LABEL_TO_ID, MAX_TOKENS


class PhoBertClassifier:
    def __init__(self, checkpoint: Path, segmenter_dir: Path):
        checkpoint = checkpoint.resolve()
        segmenter_dir = segmenter_dir.resolve()
        if not (checkpoint / "model.safetensors").is_file():
            raise FileNotFoundError(f"PhoBERT weights not found in {checkpoint}")
        for name in (
            "VnCoreNLP-1.2.jar",
            "models/wordsegmenter/vi-vocab",
            "models/wordsegmenter/wordsegmenter.rdr",
        ):
            if not (segmenter_dir / name).is_file():
                raise FileNotFoundError(f"VnCoreNLP file not found: {segmenter_dir / name}")

        self.tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            checkpoint, local_files_only=True
        ).eval()
        if self.model.config.id2label != {index: label for label, index in LABEL_TO_ID.items()}:
            raise ValueError("PhoBERT checkpoint has an unexpected label mapping.")

        # The wrapper changes the process working directory during initialization.
        with chdir(segmenter_dir):
            self.segmenter = py_vncorenlp.VnCoreNLP(
                annotators=["wseg"], save_dir=str(segmenter_dir)
            )
        self.segmenter_lock = Lock()
        logging.getLogger("uvicorn.error").info("Loaded PhoBERT checkpoint: %s", checkpoint)

    def predict_label(self, text: str) -> str:
        # FastAPI may call the same Java segmenter from multiple worker threads.
        with self.segmenter_lock:
            segmented = " ".join(self.segmenter.word_segment(text))
        token_ids = self.tokenizer.encode(
            segmented, add_special_tokens=False, verbose=False
        )
        inputs = self.tokenizer.prepare_for_model(
            token_ids,
            max_length=MAX_TOKENS,
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
            prepend_batch_axis=True,
        )
        with torch.inference_mode():
            label_id = self.model(**inputs).logits.argmax(dim=-1).item()
        return self.model.config.id2label[label_id]
