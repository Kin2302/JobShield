"""Kiểm tra HTTP toàn luồng v3. Chạy scripts/start-demo.ps1 trước khi chạy test."""

import httpx
import pytest


BASE_URL = "http://127.0.0.1:5173"
AI_URL = "http://127.0.0.1:8001"
V3_CODES = {"G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08"}


def test_frontend_is_served_from_build():
    response = httpx.get(BASE_URL)
    assert response.status_code == 200
    assert '<html lang="vi">' in response.text
    assert "/assets/" in response.text


def test_ai_health_reports_phobert_v3_typeA():
    response = httpx.get(f"{AI_URL}/health", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "phobert-v3-typeA"


def test_ai_service_direct_v3_contract():
    payload = {
        "sentences": [
            {
                "id": "c1",
                "type": "message",
                "speaker": "recruiter",
                "text": "HR: Em chuyển trước 500.000đ tiền phí nhận lớp gia sư nhé.",
            }
        ]
    }
    response = httpx.post(f"{AI_URL}/analyze", json=payload, timeout=15)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "suspicious"
    assert len(data["findings"]) > 0
    assert {f["code"] for f in data["findings"]} <= V3_CODES


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   "}, {}, {"text": None}, {"text": 123}])
def test_backend_rejects_invalid_input(body):
    response = httpx.post(f"{BASE_URL}/api/analyze", json=body, timeout=10)
    assert response.status_code == 400


@pytest.mark.parametrize("text", [
    "HR: Em cần nộp phí hồ sơ 500.000đ trước khi nhận việc.",
    "HR: Em ứng trước 300k thanh toán đơn hàng giúp shop, hệ thống hoàn gốc và cộng 10% hoa hồng.",
])
def test_end_to_end_suspicious_cases_return_v3_catalog_and_valid_offsets(text):
    response = httpx.post(f"{BASE_URL}/api/analyze", json={"text": text}, timeout=30)
    assert response.status_code == 200
    data = response.json()

    assert data["label"] == "suspicious"
    assert data["splitSource"] in {"groq", "local"}
    assert data["catalogVersion"] == "2.0"

    utf16 = text.encode("utf-16-le")
    sent_ids = set()
    prev_end = 0
    for sent in data["sentences"]:
        assert sent["start"] >= prev_end
        assert sent["end"] > sent["start"]
        sliced = utf16[sent["start"] * 2 : sent["end"] * 2].decode("utf-16-le")
        assert sliced == sent["text"]
        sent_ids.add(sent["id"])
        prev_end = sent["end"]

    codes = {f["code"] for f in data["findings"]}
    assert len(codes) > 0
    assert codes <= V3_CODES
    for finding in data["findings"]:
        assert len(finding["evidenceSentenceIds"]) > 0
        assert set(finding["evidenceSentenceIds"]) <= sent_ids
        assert finding["code"] in data["explanations"]
    assert len(data["cases"]) > 0


def test_end_to_end_clean_posting_returns_not_detected():
    text = (
        "Tuyển nhân viên kế toán làm việc tại văn phòng Quận 7, TP.HCM.\n"
        "Mức lương 12-15 triệu/tháng, đóng BHXH đầy đủ.\n"
        "Ứng viên không phải nộp bất kỳ khoản phí nào. Gửi CV về hr@anphat.vn."
    )
    response = httpx.post(f"{BASE_URL}/api/analyze", json={"text": text}, timeout=30)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "not_detected"
    assert data["findings"] == []
    assert data["splitSource"] in {"groq", "local"}
    assert len(data["sentences"]) >= 1
