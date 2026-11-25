import json
import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

import main


POSTING = {
    "id": "c1",
    "type": "posting",
    "speaker": "unknown",
    "text": "  Tuyển nhân viên bán thời gian.  ",
}

MESSAGE = {
    "id": "c2",
    "type": "message",
    "speaker": "recruiter",
    "text": "Nhà tuyển dụng: Em chuyển tiền cọc trước nhé.",
}

UNKNOWN_TYPE = {
    "id": "c3",
    "type": "unknown",
    "speaker": "unknown",
    "text": "Nộp phí hồ sơ 500.000đ để giữ suất.",
}


@pytest.fixture
def api(monkeypatch):
    classifier = Mock()
    classifier.model_name = "phobert-v3-typeA"
    load = Mock(return_value=classifier)
    monkeypatch.setattr(main, "PhoBertV3TypeAClassifier", load)
    monkeypatch.setenv("JOBSHIELD_MODEL_DIR", "test-model-dir")
    monkeypatch.setenv("JOBSHIELD_VNCORENLP_DIR", "test-segmenter")

    with TestClient(main.app) as client:
        yield client, classifier, load


def test_health_endpoint_reports_model_name(api):
    client, _, _ = api
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model": "phobert-v3-typeA"}


@pytest.mark.parametrize("prediction", [
    {"label": "not_detected", "findings": []},
    {
        "label": "suspicious",
        "findings": [{"code": "G01", "evidence_sentence_ids": ["c2"]}],
    },
])
def test_analyze_preserves_sentences_and_returns_findings(api, prediction):
    client, classifier, load = api
    classifier.predict.return_value = prediction
    sentences = [POSTING, MESSAGE, UNKNOWN_TYPE]

    for _ in range(2):
        response = client.post("/analyze", json={"sentences": sentences})
        assert response.status_code == 200
        assert response.json() == prediction

    load.assert_called_once()
    assert classifier.predict.call_count == 2
    classifier.predict.assert_called_with(sentences)


@pytest.mark.parametrize("body", [
    {"text": "Nội dung theo hợp đồng cũ."},
    {"sentences": []},
    {"sentences": [POSTING, POSTING]},
    {"sentences": [{**POSTING, "id": " "}]},
    {"sentences": [{**POSTING, "text": " "}]},
    {"sentences": [{**POSTING, "type": "sms"}]},
    {"sentences": [{**POSTING, "speaker": "sender"}]},
    {"sentences": [{"id": "c1", "text": "Thiếu loại và vai."}]},
    {"sentences": [{**POSTING, "text": "x" * 2001}]},
    {"sentences": [{**POSTING, "text": "Tin\x00ẩn"}]},
    {"sentences": [{**POSTING, "id": f"c{i}"} for i in range(151)]},
])
def test_invalid_request_stops_before_prediction(api, body):
    client, classifier, _ = api

    response = client.post("/analyze", json=body)

    assert response.status_code == 422
    classifier.predict.assert_not_called()


def test_phobert_v3_typeA_parity_with_evaluation_pipeline():
    repo_root = Path(__file__).resolve().parents[3]
    model_dir = repo_root / "models" / "v3" / "jobshield-phobert-v3-typeA"
    vncorenlp_dir = repo_root / "models" / "vncorenlp"
    test_jsonl = repo_root.parent / "data" / "v3" / "test.jsonl"
    if not (model_dir.exists() and vncorenlp_dir.exists() and test_jsonl.exists()):
        pytest.skip("Thiếu checkpoint v3, VnCoreNLP hoặc data/v3/test.jsonl.")

    if not os.environ.get("JAVA_HOME"):
        default_jdk = Path("C:/Program Files/Microsoft/jdk-21.0.13.21-hotspot")
        if default_jdk.exists():
            os.environ["JAVA_HOME"] = str(default_jdk)

    from phobert_v3_inference import PhoBertV3TypeAClassifier

    classifier = PhoBertV3TypeAClassifier(model_dir=model_dir, segmenter_dir=vncorenlp_dir)
    rows = [json.loads(line) for line in test_jsonl.read_text(encoding="utf-8").splitlines()][:6]

    for row in rows:
        doc_type = row["input"]["type"]
        sents = [
            {
                "id": s["id"],
                "type": doc_type,
                "speaker": s.get("speaker", "unknown"),
                "text": s["text"],
            }
            for s in row["input"]["sentences"]
        ]
        pred = classifier.predict(sents)
        assert pred["label"] in {"suspicious", "not_detected"}
        assert (pred["label"] == "suspicious") == (len(pred["findings"]) > 0)
        for finding in pred["findings"]:
            assert finding["code"] in {"G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08"}
            assert len(finding["evidence_sentence_ids"]) > 0
