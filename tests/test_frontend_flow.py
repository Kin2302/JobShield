"""Run with a local Vite server: python tests/test_frontend_flow.py -v.

Requires Playwright for Python and Chromium. Set JOBSHIELD_WEB_URL to run
against a different frontend or to include these browser tests in discovery.
The browser intercepts every /api request; no AI service or key is required.
"""
import os
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

if __name__ != "__main__" and not os.getenv("JOBSHIELD_WEB_URL"):
    raise unittest.SkipTest("Run directly or set JOBSHIELD_WEB_URL for frontend browser tests.")

from playwright.sync_api import expect, sync_playwright


class FrontendFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = sync_playwright().start()
        cls.addClassCleanup(cls.driver.stop)
        cls.browser = cls.driver.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1280, "height": 900})
        self.addCleanup(self.page.close)
        self.requests = []
        self.page.route("**/api/**", lambda route: self.requests.append(route))
        self.page.goto(os.getenv("JOBSHIELD_WEB_URL") or "http://127.0.0.1:5173")

    def button(self, name):
        return self.page.get_by_role("button", name=name, exact=True)

    def capture_home(self, filename):
        folder = os.getenv("JOBSHIELD_WEB_EVIDENCE")
        if folder:
            target = Path(folder)
            target.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=target / filename, full_page=True, animations="disabled")

    def submit(self, text, name="Kiểm tra"):
        before = len(self.requests)
        with self.page.expect_request("**/api/**"):
            self.button(name).click()
        expect(self.page.get_by_role("status", name="Đang kiểm tra nội dung…")).to_be_visible()
        self.assertEqual(len(self.requests), before + 1)
        route = self.requests[-1]
        self.assertEqual(urlparse(route.request.url).path, "/api/analyze")
        self.assertEqual(route.request.method, "POST")
        self.assertEqual(route.request.post_data_json, {"text": text})
        return route

    def test_sample_edit_highlight_and_select_findings(self):
        self.capture_home("desktop.png")
        samples = self.page.get_by_role("button", name=re.compile("^Rút ra:"))
        expect(samples).to_have_count(6)
        chat = self.page.get_by_role("button", name=re.compile("Rút ra:.*Quản lý Hương"))
        chat.click()
        self.button("← Trả về xấp hồ sơ").click()
        expect(chat).to_be_focused()
        chat.click()
        self.button("Dùng hồ sơ này").click()
        field = self.page.get_by_role("textbox")
        self.assertIn("Bên tuyển dụng: Em cần nộp phí", field.input_value())
        lines = ["📄 Hồ sơ.", "HR: Nộp tiền.", "Gửi mã OTP.", "HR: Nộp tiền."]
        text = "\n".join(lines)
        field.fill(text)
        sentences = []
        start = 0
        for index, line in enumerate(lines, 1):
            end = start + len(line.encode("utf-16-le")) // 2
            sentences.append({"id": f"c{index}", "text": line, "start": start, "end": end})
            start = end + 1
        route = self.submit(text)
        route.fulfill(json={
            "label": "suspicious", "sentences": sentences, "findings": [
                {"code": "G01", "evidenceSentenceIds": ["c4"]},
                {"code": "G04", "evidenceSentenceIds": ["c3"]},
            ],
            "explanations": {"G01": "Có yêu cầu nộp phí.", "G04": "Mã OTP là thông tin bí mật."},
            "cases": [{
                "id": "case-1", "title": "Thu phí và xin mã OTP", "summary": "Người tìm việc đã nộp phí.",
                "matchReasons": {"G01": "Cùng yêu cầu nộp phí.", "G04": "Cùng yêu cầu OTP."},
                "sourceUrl": "https://example.org/case",
            }],
            "possibleNextSteps": [
                {"id": "s1", "text": "Có thể yêu cầu chuyển thêm tiền.", "sourceUrl": "https://example.org/fee"},
                {"id": "s2", "text": "Có thể yêu cầu xác nhận giao dịch.", "sourceUrl": "https://example.org/otp"},
            ],
        })

        expect(self.page.get_by_text("Có dấu hiệu đáng ngờ", exact=True)).to_be_visible()
        document = self.page.locator(".dossier-original")
        mark = document.locator("mark")
        expect(mark).to_have_text([lines[3]])
        self.assertEqual(document.text_content(), text)
        self.assertEqual(mark.evaluate("el => el.previousSibling.textContent"), "\n".join(lines[:3]) + "\n")
        expect(self.page.get_by_text("Có yêu cầu nộp phí.", exact=True)).to_be_visible()
        self.page.get_by_role("button", name=re.compile("G04")).click()
        expect(mark).to_have_text([lines[2]])
        expect(self.page.get_by_role("blockquote")).to_have_text([lines[2]])
        expect(self.page.get_by_text("Mã OTP là thông tin bí mật.", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Có yêu cầu nộp phí.", exact=True)).to_be_hidden()
        for width, height in [(1280, 900), (375, 812)]:
            self.page.set_viewport_size({"width": width, "height": height})
            cases = self.page.get_by_role("region", name="Vụ việc có thật")
            expect(cases.get_by_role("article")).to_have_count(1)
            expect(cases.get_by_role("heading", name="Thu phí và xin mã OTP")).to_be_visible()
            expect(cases.get_by_text("Người tìm việc đã nộp phí.")).to_be_visible()
            expect(cases.get_by_role("listitem")).to_have_text(["G01 · Cùng yêu cầu nộp phí.", "G04 · Cùng yêu cầu OTP."])
            expect(cases.get_by_role("link")).to_have_attribute("href", "https://example.org/case")
            steps = self.page.get_by_role("region", name="Diễn biến giả định").get_by_role("listitem")
            expect(steps).to_have_count(2)
            for phrase, slug in [("chuyển thêm tiền", "fee"), ("xác nhận giao dịch", "otp")]:
                link = steps.filter(has_text=phrase).get_by_role("link")
                expect(link).to_be_visible()
                expect(link).to_have_attribute("href", f"https://example.org/{slug}")
            self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        self.assertEqual(len(self.requests), 1)

    def test_mobile_blank_retry_and_clean_result(self):
        self.page.set_viewport_size({"width": 375, "height": 812})
        self.capture_home("mobile.png")
        self.button("Bắt đầu kiểm tra").click()
        field = self.page.get_by_role("textbox")
        field.fill("   ")
        expect(self.button("Kiểm tra")).to_be_disabled()
        text = "Mời bạn tới phỏng vấn lúc 9 giờ."
        field.fill(text)
        self.submit(text).fulfill(status=502, json={"title": "Chưa thể phân tích"})
        expect(self.page.get_by_role("alert")).to_be_visible()
        expect(field).to_have_value(text)
        self.submit(text, "Thử lại").fulfill(json={
            "label": "not_detected", "findings": [],
            "sentences": [{"id": "c1", "start": 0, "end": len(text), "text": text}],
        })
        expect(self.page.get_by_text("Chưa phát hiện dấu hiệu", exact=True)).to_be_visible()
        self.assertEqual(self.page.locator(".dossier-original").text_content(), text)
        expect(self.page.locator(".dossier-original mark")).to_have_count(0)
        for title in ("Vụ việc có thật", "Diễn biến giả định"):
            expect(self.page.get_by_role("heading", name=title)).to_have_count(0)
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))
        self.button("Kiểm tra nội dung khác").click()
        expect(field).to_have_value("")
        self.assertEqual(len(self.requests), 2)

    def test_legacy_finding_without_catalog(self):
        self.button("Bắt đầu kiểm tra").click()
        text = "Gửi mã OTP."
        self.page.get_by_role("textbox").fill(text)
        self.submit(text).fulfill(json={
            "label": "suspicious", "findings": [{"code": "G04", "evidenceSentenceIds": ["c1"]}],
            "sentences": [{"id": "c1", "start": 0, "end": len(text), "text": text}],
        })
        expect(self.page.locator(".dossier-original mark")).to_have_text(text)
        expect(self.page.get_by_role("blockquote")).to_have_text(text)
        for title in ("Vụ việc có thật", "Diễn biến giả định"):
            expect(self.page.get_by_role("heading", name=title)).to_have_count(0)


if __name__ == "__main__":
    unittest.main()
