import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_detects_fee_request_and_preserves_original_evidence():
    response = client.post(
        "/analyze",
        json={"text": "Tuyển nhân viên. Em cần NỘP PHÍ HỒ SƠ TRƯỚC KHI NHẬN VIỆC nhé."},
    )

    assert response.status_code == 200
    assert response.json() == {
        "baseline_version": "rules-v0.1",
        "message": "Phát hiện dấu hiệu theo quy tắc hiện có.",
        "signals": [
            {
                "code": "UPFRONT_JOB_FEE",
                "name": "Yêu cầu phí trước khi nhận việc",
                "evidence": "NỘP PHÍ HỒ SƠ TRƯỚC KHI NHẬN VIỆC",
            }
        ],
    }


def test_detects_second_agreed_phrase():
    response = client.post(
        "/analyze", json={"text": "Bạn cần đóng phí hồ sơ trước khi nhận việc."}
    )

    assert response.status_code == 200
    assert response.json()["signals"][0]["evidence"] == (
        "đóng phí hồ sơ trước khi nhận việc"
    )


@pytest.mark.parametrize(
    "text",
    [
        "Tuyển nhân viên bán hàng, phỏng vấn trực tiếp.",
        "Không thu phí nhận việc.",
        "Không nộp phí hồ sơ trước khi nhận việc.",
        "KHÔNG CẦN ĐÓNG PHÍ HỒ SƠ TRƯỚC KHI NHẬN VIỆC.",
        "Bạn không phải nộp phí hồ sơ trước khi nhận việc.",
        "Họ hỏi tôi đã đóng phí chưa.",
        "Nộp phí hồ sơ. Trước khi nhận việc.",
        "Nộp phí hồ sơ\ntrước khi nhận việc.",
    ],
)
def test_returns_no_detection_for_negation_or_unsupported_text(text):
    response = client.post("/analyze", json={"text": text})

    assert response.status_code == 200
    assert response.json() == {
        "baseline_version": "rules-v0.1",
        "message": "Chưa phát hiện theo quy tắc hiện có.",
        "signals": [],
    }


@pytest.mark.parametrize("separator", [". ", "! ", "? ", "\n"])
def test_negation_in_another_sentence_does_not_hide_fee_request(separator):
    response = client.post(
        "/analyze",
        json={
            "text": "Không thu phí" + separator
            + "Nộp phí hồ sơ trước khi nhận việc."
        },
    )

    assert response.status_code == 200
    assert [signal["evidence"] for signal in response.json()["signals"]] == [
        "Nộp phí hồ sơ trước khi nhận việc"
    ]


@pytest.mark.parametrize("text", ["", "   ", "\r\n\t"])
def test_rejects_blank_text(text):
    response = client.post("/analyze", json={"text": text})

    assert response.status_code == 422


@pytest.mark.parametrize("body", [{}, {"text": None}, {"text": 123}])
def test_rejects_missing_or_non_string_text(body):
    response = client.post("/analyze", json=body)

    assert response.status_code == 422
