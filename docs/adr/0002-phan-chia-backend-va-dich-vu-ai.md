# ADR 002 — Phân chia backend chính và dịch vụ AI

## Trạng thái (Status)

Đã chấp nhận và cập nhật theo kiến trúc v3 + đóng gói Docker ngày 24/11/2026.

## Bối cảnh (Context)

JobShield cần tiếp nhận văn bản từ người dùng web, tách câu (tùy chọn dùng LLM hoặc cục bộ), bảo vệ dữ liệu cá nhân/tài nguyên, chạy mô hình PhoBERT bằng Python và trả về kết quả kèm giải thích kho kịch bản `G01`–`G08`.

### Các phương án cân nhắc

| Phương án | Cách tổ chức | Ưu điểm | Hạn chế |
| --- | --- | --- | --- |
| A — FastAPI cho toàn bộ backend | Python xử lý cả nghiệp vụ web và AI | Một dịch vụ duy nhất | Không đáp ứng định hướng phát triển backend bằng C# (.NET 10) |
| **B — React (Nginx) → ASP.NET Core (.NET 10) → FastAPI (`phobert-v3-typeA`)** | Tách rạch ròi giao diện tĩnh/reverse proxy, backend nghiệp vụ & bảo mật (C#), và dịch vụ suy luận AI (Python) | Tận dụng .NET 10 cho rate limit, kiểm soát đầu vào, kho kịch bản; giữ hệ sinh thái PyTorch/VnCoreNLP trong Python; dễ đóng gói thành 3 container tách mạng | Cần đồng bộ hợp đồng JSON và healthcheck giữa các dịch vụ |

## Quyết định (Decision)

Chọn **Phương án B** với luồng xử lý thống nhất qua `POST /api/analyze`:

1. **Cổng vào (`frontend` — React + Nginx):** Phục vụ giao diện tĩnh trên cổng `5173`, gắn HTTP Security Headers và chuyển tiếp `/api/*` tới `backend` trong mạng nội bộ Docker (không mở cổng `backend` hay `ai` ra máy ngoài).
2. **Backend ứng dụng (`backend` — ASP.NET Core .NET 10):**
   - Áp dụng **Rate Limiting** theo IP (mặc định `20 req/phút`, cấu hình qua biến môi trường), giới hạn body `32 KB` và độ dài `text ≤ 10.000` ký tự.
   - Che thông tin cá nhân cùng độ dài (`PiiRedactor`: SĐT, CCCD, email) và bọc `<user_text>...</user_text>` trước khi gọi Groq (`openai/gpt-oss-20b`, timeout 10s).
   - Hậu kiểm nguyên văn qua `SentencePreparation.Prepare`; nếu thiếu khóa Groq, quá thời gian, gặp lỗi hoặc đầu ra bị lệch/prompt injection, tự động chuyển về `LocalSentenceSplitter` cục bộ.
   - Đối chiếu kết quả `G01`–`G08` từ AI với `RecruitmentScenarios.json` (`CatalogVersion = 2.0`).
3. **Dịch vụ AI (`ai` — FastAPI + `phobert-v3-typeA`):** Ràng buộc Pydantic (`1–150` câu, `≤ 2.000` ký tự/câu), suy luận hoàn toàn cục bộ trên CPU và trả JSON `{ label, findings }`.

## Hệ quả (Consequences)

- Khóa bí mật `Groq__ApiKey` được truyền lúc chạy qua `.env` / biến môi trường hoặc User Secrets, không lưu trong mã nguồn hay Docker image.
- Khi dịch vụ Groq bên ngoài gặp sự cố hoặc bị tấn công prompt injection, luồng phân tích vẫn hoàn tất bằng `LocalSentenceSplitter` với tỉ lệ lỗi `5xx` bằng `0%`.
- Hợp đồng API giữa Backend và AI (`POST /analyze`, `GET /health`) được bảo vệ bằng kiểm thử tự động trong GitHub Actions CI.
