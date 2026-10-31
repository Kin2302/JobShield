from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from baseline import find_fee_evidence


class AnalyzeRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def reject_blank_text(cls, text: str) -> str:
        if not text.strip():
            raise ValueError("Nội dung không được để trống.")
        return text


class Signal(BaseModel):
    code: str
    name: str
    evidence: str


class AnalyzeResponse(BaseModel):
    baseline_version: str
    message: str
    signals: list[Signal]


app = FastAPI(title="JobShield AI — Hello World")


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    signals = [
        Signal(
            code="UPFRONT_JOB_FEE",
            name="Yêu cầu phí trước khi nhận việc",
            evidence=evidence,
        )
        for evidence in find_fee_evidence(request.text)
    ]
    return AnalyzeResponse(
        baseline_version="rules-v0.1",
        message=(
            "Phát hiện dấu hiệu theo quy tắc hiện có."
            if signals
            else "Chưa phát hiện theo quy tắc hiện có."
        ),
        signals=signals,
    )
