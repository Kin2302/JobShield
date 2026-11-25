"""Run against the local demo with: python tests/web_browser.py -v

Requires Playwright for Python and Chromium. JOBSHIELD_WEB_EVIDENCE optionally
records screenshots and observed results; JOBSHIELD_WEB_URL overrides the URL.
"""
import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import expect, sync_playwright


QUESTION = "Em có cần đóng phí không?"
REQUEST = "Em cần nộp phí hồ sơ trước khi nhận việc."
CHAT = QUESTION + "\n" + REQUEST
POST = "Phỏng vấn lúc 8 giờ. Mang theo CV."


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = sync_playwright().start()
        cls.addClassCleanup(cls.driver.stop)
        cls.browser = cls.driver.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1360, "height": 950}, reduced_motion="reduce")
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.page.goto(os.getenv("JOBSHIELD_WEB_URL", "http://127.0.0.1:5173"))

    def record(self, message, suffix=""):
        target = os.getenv("JOBSHIELD_WEB_EVIDENCE")
        if target:
            folder = Path(target)
            folder.mkdir(parents=True, exist_ok=True)
            case = "WEB-" + self._testMethodName.split("_")[1]
            self.page.screenshot(path=folder / (case + suffix + ".png"), full_page=True)
            with (folder / "observations.jsonl").open("a", encoding="utf8") as file:
                print(json.dumps(dict(case=case, time=datetime.now().astimezone().isoformat(),
                                      observed=message), ensure_ascii=False), file=file)
        print(message,flush=True)

    def button(self, name):
        return self.page.get_by_role("button", name=name, exact=True)

    def prepare(self, text):
        self.page.locator("#input").fill(text)
        self.button("Gửi để chuẩn bị").click()
        expect(self.part(1)).to_be_visible()

    def part(self, number):
        return self.page.get_by_label(f"Văn bản đoạn {number}", exact=True)

    def chat(self):
        self.prepare(CHAT)
        for i, role in enumerate(("Ứng viên", "Bên tuyển dụng"), 1):
            self.page.get_by_label(f"Loại nội dung đoạn {i}").select_option(label="Hội thoại")
            self.page.get_by_label(f"Vai đoạn {i}").select_option(label=role)

    def analyze(self):
        with self.page.expect_response(lambda r: r.url.endswith("/api/analyze") and r.request.method=="POST") as response:
            self.button("Xác nhận và phân tích").click()
        self.assertEqual(response.value.status,200)
        expect(self.page.get_by_role("heading",name="Kết quả kiểm tra")).to_be_visible()
        return response.value.json()

    def split(self):
        self.prepare(POST)
        editor = self.part(1)
        # Click at the visual boundary in the read-only text, as a user would.
        position = editor.evaluate("""async field => {
            await document.fonts.ready;
            const style = getComputedStyle(field);
            const canvas = document.createElement('canvas').getContext('2d');
            canvas.font = style.fontSize + ' ' + style.fontFamily;
            const prefix = field.value.slice(0, field.value.indexOf('Mang'));
            return {x: parseFloat(style.paddingLeft) + canvas.measureText(prefix).width,
                    y: parseFloat(style.paddingTop) + parseFloat(style.lineHeight) / 2};
        }""")
        editor.click(position=position)
        self.assertEqual(editor.evaluate("field => field.selectionStart"), POST.index("Mang"))
        self.button("Tách tại con trỏ").click()
        expect(self.part(2)).to_have_value("Mang theo CV.")

    def test_01_main_flow(self):
        self.chat()
        self.record("Đã xác nhận hai lượt nói và vai tương ứng.","-prepare")
        result = self.analyze()
        labels = {"suspicious":"Có dấu hiệu đáng ngờ","not_detected":"Chưa phát hiện dấu hiệu"}
        expect(self.page.locator(".tree-root")).to_have_text(labels[result["label"]])
        self.record("API trả HTTP 200. Web hiển thị nhãn “"+labels[result["label"]]+"”.")

    def test_02_blank(self):
        self.page.locator("#input").fill("   ")
        expect(self.button("Gửi để chuẩn bị")).to_be_disabled()
        self.record("Nút Gửi để chuẩn bị bị vô hiệu hóa khi nhập ba dấu cách.")

    def test_03_preserve_text(self):
        lines = ["💬 Chị gửi lịch.\n", "Dạ, em xác nhận."]
        self.prepare("".join(lines))
        for i, line in enumerate(lines,1):
            expect(self.part(i)).to_have_value(line)
        self.record("Hai đoạn giữ nguyên emoji, xuống dòng, dấu tiếng Việt và thứ tự.")

    def test_04_split(self):
        self.split()
        self.assertEqual(self.part(1).input_value()+self.part(2).input_value(),POST)
        self.record("Đoạn hai bắt đầu bằng “Mang”; hai đoạn ghép lại khớp văn bản gốc.")

    def test_05_merge(self):
        self.split()
        self.button("Gộp với đoạn sau").first.click()
        expect(self.part(2)).to_have_count(0)
        expect(self.part(1)).to_have_value(POST)
        self.record("Còn một đoạn và nội dung khớp nguyên văn trước khi tách.")

    def test_06_edit(self):
        self.prepare("Đặt cọc 200.000 đồng.")
        self.button("Sửa văn bản gốc").click()
        self.prepare("Đặt cọc 300.000 đồng.")
        expect(self.part(1)).to_have_value("Đặt cọc 300.000 đồng.")
        self.record("Đoạn xác nhận hiển thị 300.000 đồng sau khi sửa.")

    def test_07_quote(self):
        self.chat()
        result = self.analyze()
        self.assertEqual([(f["code"],f["quote"]) for f in result["findings"]],[("A01",REQUEST)])
        self.page.get_by_role("button",name="A01",exact=False).click()
        quotes = self.page.locator("blockquote:visible")
        expect(quotes).to_have_text([REQUEST])
        self.record("Web hiển thị đúng A01 và nguyên văn lời người tuyển. Câu hỏi không được đánh dấu.")

    def test_08_original(self):
        self.chat()
        self.analyze()
        self.button("Văn bản gốc").click()
        expect(self.page.locator("dialog[open] pre")).to_be_visible()
        self.assertEqual(self.page.locator("dialog[open] pre").text_content(),CHAT)
        self.record("Hộp Văn bản gốc hiển thị nguyên hai lượt lời đúng thứ tự.")

    def test_09_next(self):
        first = "Đặt cọc 300.000 đồng để giữ chỗ."
        second = "Phỏng vấn lúc 9 giờ sáng thứ Hai."
        self.prepare(first)
        self.analyze()
        self.button("Kiểm tra nội dung khác").click()
        expect(self.page.locator("#input")).to_have_value("")
        self.prepare(second)
        result = self.analyze()
        self.assertEqual(result["findings"],[])
        self.button("Văn bản gốc").click()
        self.assertEqual(self.page.locator("dialog[open] pre").text_content(),second)
        self.record("Lượt hai hiển thị đúng lịch phỏng vấn và không còn bằng chứng của tin thứ nhất.")

    def test_10_feedback(self):
        self.chat()
        result = self.analyze()
        link = self.page.get_by_role("link",name="Góp ý kết quả")
        expect(link).to_be_visible()
        url = urlparse(link.get_attribute("href"))
        self.assertEqual((url.scheme,url.hostname),("https","docs.google.com"))
        self.assertTrue(url.path.endswith("/viewform"))
        values = list(parse_qs(url.query).values())
        self.assertIn(["Đáng ngờ" if result["label"]=="suspicious" else "Chưa phát hiện"],values)
        self.assertIn(["A01"],values)
        with self.page.expect_popup() as opened:
            link.click()
        form = opened.value
        form.wait_for_load_state("domcontentloaded",timeout=30000)
        self.assertEqual(urlparse(form.url).hostname,"docs.google.com")
        expect(form.get_by_role("listitem").first).to_be_visible()
        self.page = form
        self.record("Bấm Góp ý kết quả mở được Google Forms có câu hỏi hiển thị; liên kết mang nhãn và mã A01.")


if __name__ == "__main__":
    unittest.main()
