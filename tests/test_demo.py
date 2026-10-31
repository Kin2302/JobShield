"""Kiểm tra HTTP toàn luồng. Chạy scripts/start-demo.ps1 trước khi chạy test."""

import httpx
import pytest


BASE_URL = "http://127.0.0.1:5173"


def test_frontend_is_served_from_build():
    response = httpx.get(BASE_URL)
    assert response.status_code == 200
    assert '<html lang="vi">' in response.text
    assert "/assets/" in response.text


@pytest.mark.parametrize(
    ("text", "expected_evidence"),
    [
        ("Em cần nộp phí hồ sơ trước khi nhận việc.", "nộp phí hồ sơ trước khi nhận việc"),
        ("ĐÓNG PHÍ HỒ SƠ TRƯỚC KHI NHẬN VIỆC.", "ĐÓNG PHÍ HỒ SƠ TRƯỚC KHI NHẬN VIỆC"),
        ("Không cần đóng phí hồ sơ trước khi nhận việc.", None),
        ("Tuyển nhân viên bán hàng, phỏng vấn trực tiếp.", None),
    ],
)
def test_analysis_through_frontend_proxy_and_both_backends(text, expected_evidence):
    response = httpx.post(BASE_URL + "/api/analyze", json={"text": text})
    assert response.status_code == 200
    result = response.json()
    assert result["baseline_version"] == "rules-v0.1"
    if expected_evidence:
        assert result["signals"] == [{
            "code": "UPFRONT_JOB_FEE",
            "name": "Yêu cầu phí trước khi nhận việc",
            "evidence": expected_evidence,
        }]
    else:
        assert result["signals"] == []
        assert result["message"] == "Chưa phát hiện theo quy tắc hiện có."


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   "}, {}, {"text": None}, {"text": 123}])
def test_backend_rejects_invalid_input(body):
    response = httpx.post(BASE_URL + "/api/analyze", json=body)
    assert response.status_code == 400
