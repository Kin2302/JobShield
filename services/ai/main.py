import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field, field_validator

from phobert_v3_inference import PhoBertV3TypeAClassifier

_parents = Path(__file__).resolve().parents
REPO_ROOT = _parents[2] if len(_parents) > 2 else Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = REPO_ROOT / "models" / "v3" / "jobshield-phobert-v3-typeA"
DEFAULT_VNCORENLP_DIR = REPO_ROOT / "models" / "vncorenlp"


class Sentence(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    type: Literal["posting", "message", "unknown"]
    speaker: Literal["applicant", "recruiter", "unknown"]
    text: str = Field(min_length=1, max_length=2000)

    @field_validator("id", "text")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("Nội dung chứa ký tự không hợp lệ.")
        if not value.strip():
            raise ValueError("ID và nội dung câu phải có giá trị.")
        return value


class AnalyzeRequest(BaseModel):
    sentences: list[Sentence] = Field(min_length=1, max_length=150)

    @field_validator("sentences")
    @classmethod
    def reject_duplicate_ids(cls, sentences: list[Sentence]) -> list[Sentence]:
        if len({sentence.id for sentence in sentences}) != len(sentences):
            raise ValueError("ID câu bị trùng.")
        return sentences


class Finding(BaseModel):
    code: str
    evidence_sentence_ids: list[str]


class AnalyzeResponse(BaseModel):
    label: Literal["suspicious", "not_detected"]
    findings: list[Finding]


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_dir = Path(os.environ.get("JOBSHIELD_MODEL_DIR", DEFAULT_MODEL_DIR))
    segmenter_dir = Path(os.environ.get("JOBSHIELD_VNCORENLP_DIR", DEFAULT_VNCORENLP_DIR))
    app.state.classifier = PhoBertV3TypeAClassifier(
        model_dir=model_dir,
        segmenter_dir=segmenter_dir,
    )
    yield


app = FastAPI(title="JobShield AI", lifespan=lifespan)


@app.get("/health")
def health(request: Request):
    model_name = getattr(request.app.state.classifier, "model_name", "phobert-v3-typeA")
    return {"status": "ok", "model": model_name}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(body: AnalyzeRequest, request: Request):
    sentences = [sentence.model_dump() for sentence in body.sentences]
    return request.app.state.classifier.predict(sentences)
