# JobShield

Công cụ hỗ trợ sinh viên nhận diện dấu hiệu đáng ngờ trong tin tuyển dụng tiếng Việt bằng phân loại văn bản có giải thích.

**Trạng thái** — Ứng dụng chạy toàn luồng **React → ASP.NET Core (.NET 10) → FastAPI (`phobert-v3-typeA`)** theo khung 8 nhóm hành vi lõi `G01`–`G08` ([Codebook v3](../data/v3/CODEBOOK.md)). ASP.NET Core hỗ trợ tách câu qua Groq (`openai/gpt-oss-20b`, timeout 10s) và tự động chuyển sang bộ tách câu dự phòng cục bộ (`LocalSentenceSplitter`) khi thiếu khóa, quá thời gian hoặc gặp giới hạn tốc độ; kết quả phân tích gắn giải thích và vụ việc tham chiếu từ [RecruitmentScenarios.json](backend/JobShield.Infrastructure/RecruitmentScenarios.json).

## Vấn đề đang theo dõi

- **Qwen gán vai người nói (`speaker`) lệch đáp án — đang mở, tạm hoãn.** Lượt đo trực tiếp với `qwen/qwen3.8-27b` sau khi thêm hai ví dụ vào prompt nhận được 15 phản hồi trên 30 mẫu. Cả 15 giữ nguyên văn và khớp ranh giới câu. Có 5 mẫu lệch vai: `JS-TR006`, `JS-TR008`, `JS-TR014`, `JS-TR024`, `JS-TR029`. Ví dụ, ở `JS-TR029` cả bốn câu đều được gán `unknown`, trong khi đáp án lần lượt là `recruiter`, `recruiter`, `applicant`, `recruiter`. Khi xử lý lại, đối chiếu quy ước tin đăng thiếu căn cứ nhận diện dùng `unknown` với nhãn trong [bộ 30 mẫu](backend/JobShield.Tests/Evaluation/Data/jobshield-test-30.jsonl). 15 yêu cầu gặp HTTP 429 được loại khỏi phép chấm vai.

## Phiên bản nghiên cứu

| Phiên bản | Dataset và codebook | PhoBERT |
| --- | --- | --- |
| v1 (trước đây là v3, codebook v0.3) | [Dataset](../data/v1/README.md) · [Codebook](../data/v1/CODEBOOK.md) | [Checkpoint theo câu](services/ai/phobert-v1/checkpoint/) · [Notebook Kaggle](services/ai/train_phobert_v1_kaggle.ipynb) · [Gói train/validation](../data/v1/jobshield-v1-train-val.zip) |
| v2 (trước đây là v4, codebook v0.4) | [Dataset](../data/v2/README.md) · [Codebook](../data/v2/CODEBOOK.md) | [Checkpoint theo câu](services/ai/jobshield-phobert-v2-result/checkpoint/) · [Notebook Colab](services/ai/train_phobert_v2_colab.ipynb) · [Kết quả validation](services/ai/jobshield-phobert-v2-result/validation.json) |
| **v3 (hiện hành, khung `G01`–`G08`)** | [Dataset](../data/v3/README.md) · [Codebook](../data/v3/CODEBOOK.md) | `phobert-v3-typeA` (`models/v3/jobshield-phobert-v3-typeA/`) · [Notebook Colab](services/ai/notebooks/train_phobert_v3_typeA_colab.ipynb) · [Báo cáo đánh giá](tests/evaluation/v3-model-comparison/REPORT.md) |

Minh chứng tuần đã chốt dùng tên tại thời điểm thực hiện. Checkpoint phân loại nhị phân trong hướng dẫn API bên dưới phục vụ chế độ demo riêng.

## Chạy ứng dụng JobShield v3 (`phobert-v3-typeA`)

### Cách 1 — Chạy bằng Docker Compose (khuyến nghị)

Chuẩn bị sẵn Docker Desktop và thư mục `models/` (`models/vncorenlp/` và `models/v3/jobshield-phobert-v3-typeA/`). Tạo tệp `.env` từ `.env.example` nếu muốn cấu hình khóa Groq (tùy chọn — nếu để trống, Backend tự chuyển sang `LocalSentenceSplitter`):

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Mở [JobShield local](http://127.0.0.1:5173). Nginx chỉ mở duy nhất cổng `5173` ra máy host, gắn HTTP Security Headers và chuyển tiếp `/api/*` tới ASP.NET Core (`backend`) → FastAPI `phobert-v3-typeA` (`ai`) trong mạng nội bộ Docker (`models/` được gắn chỉ đọc). Dừng cụm dịch vụ bằng `docker compose down`.

### Cách 2 — Chạy trực tiếp trên máy (Dev)

Chuẩn bị sẵn JDK 21 (cho `VnCoreNLP`), `models/vncorenlp/` và checkpoint `models/v3/jobshield-phobert-v3-typeA/`. Khóa `Groq:ApiKey` trong User Secrets là tùy chọn (nếu thiếu hoặc lỗi, Backend tự chuyển sang `LocalSentenceSplitter`).

```powershell
dotnet build backend/JobShield.slnx -c Release
npm --prefix frontend ci
npm --prefix frontend run build
powershell -NoProfile -File scripts/start-demo.ps1
```

Mở [JobShield local](http://127.0.0.1:5173). Vite chuyển `POST /api/analyze` đến ASP.NET Core ở cổng 5000, tách câu qua Groq hoặc cục bộ, rồi gọi FastAPI `phobert-v3-typeA` ở cổng 8001 (`GET /health`, `POST /analyze`).

Kiểm thử toàn bộ và dừng dịch vụ:

```powershell
dotnet test backend/JobShield.slnx -c Release
Push-Location services/ai; .\.venv\Scripts\python.exe -m pytest tests -q; Pop-Location
.\services\ai\.venv\Scripts\python.exe -m pytest tests/test_demo.py -q
powershell -NoProfile -File scripts/stop-demo.ps1
```

Log của các dịch vụ khi chạy trực tiếp nằm trong `tmp/hello-world/`.

## Bảo mật, Yêu cầu phi chức năng (NFR) & CI

- **Bảo mật (4 lớp):**
  1. **Rate Limiting & Input Guard:** `POST /api/analyze` giới hạn `20 req/phút` theo IP (cấu hình qua `RateLimiting:PermitLimit`), body `≤ 32 KB`, `text ≤ 10.000` ký tự, chặn ký tự `\0`; FastAPI giới hạn `1–150` câu và `≤ 2.000` ký tự/câu.
  2. **Che PII & Quản lý Secrets:** `PiiRedactor` che SĐT, CCCD 12 số và email cùng độ dài trước khi gửi sang Groq; không ghi nội dung tin hay khóa vào log; khóa chỉ truyền qua `.env` / biến môi trường / User Secrets.
  3. **Chống Prompt Injection:** Bọc đầu vào bằng `<user_text>...</user_text>`, ép JSON Schema và hậu kiểm nguyên văn (`SentencePreparation.Prepare`); nếu đầu ra lệch, tự động fallback sang `LocalSentenceSplitter`.
  4. **HTTP Security Headers & Phân đoạn mạng:** Gắn `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy`; Docker chỉ mở cổng Frontend `5173`.
- **5 NFR mục tiêu:** Độ trễ CPU `p50 ≤ 800 ms`, `p95 ≤ 2.000 ms`; Test v3 `F1 ≥ 0,85`, `Recall ≥ 0,85`, Holdout báo động giả `≤ 5%`; Tỉ lệ lỗi `5xx = 0%`; Chi phí LLM `≤ $0,10 / 1.000` truy vấn (`$0` khi chạy cục bộ); RAM container AI `≤ 2,5 GB` và chặn `100%` request vi phạm giới hạn.
- **CI (GitHub Actions):** Workflow [.github/workflows/ci.yml](.github/workflows/ci.yml) tự chạy `dotnet test`, `pytest` và `npm run build` trên mỗi lần `push` / `pull_request`.

## Chuẩn bị nội dung với Groq

Lưu khóa Groq với tên `Groq:ApiKey` trong **.NET User Secrets** của `backend/JobShield.Api/JobShield.Api.csproj`. Trong Visual Studio, dùng **Manage User Secrets** trên project backend. Script demo và cấu hình chạy backend dùng môi trường `Development` để đọc User Secrets.

Chọn ô gửi nội dung tới Groq trên màn nhập khi dùng nội dung mô phỏng hoặc đã che thông tin. Agent gợi ý đoạn, loại nội dung và người nói. Người dùng xác nhận hoặc chỉnh lại trước khi phân tích. Khi thiếu khóa, Groq lỗi hoặc kết quả không khớp văn bản gốc, màn xác nhận dùng bản tách theo dòng.

Model mặc định là `openai/gpt-oss-20b`. Có thể cấu hình model khác hỗ trợ JSON Schema bằng biến môi trường `Groq__Model`.

## Thu phản hồi kết quả

Để hiện **Góp ý kết quả** dưới cây, tạo `frontend/.env.local` với cấu hình Google Form của dự án:

```dotenv
VITE_FEEDBACK_FORM_URL=https://docs.google.com/forms/d/e/1FAIpQLScgWnou80tFS7-RvhsjoS_fWp9rikE68QO-RJFGsgTLKDpk3g/viewform
VITE_FEEDBACK_LABEL_ENTRY=entry.1496633354
VITE_FEEDBACK_CODES_ENTRY=entry.1380967390
```

Khởi động lại Vite hoặc build lại frontend sau khi đổi cấu hình. Nếu thay Form, dùng chức năng **Mẫu điền sẵn** trong Google Forms để lấy URL người trả lời và hai mã `entry.*` tương ứng. Khi thiếu cấu hình hoặc URL sai, liên kết góp ý được ẩn.

Form mở ở tab mới với nhãn tổng và mã dấu hiệu đã điền sẵn. Người dùng tự gửi phản hồi vào Sheet liên kết. Các trường điền sẵn có thể chỉnh, nên dùng phản hồi để rà soát pilot.

## Chạy API với PhoBERT

Giải nén thư mục `checkpoint` từ tệp Colab. Chuẩn bị Java và bộ tách từ VnCoreNLP gồm `VnCoreNLP-1.2.jar` cùng hai tệp `vi-vocab`, `wordsegmenter.rdr` trong `models/wordsegmenter/`. Đặt `JAVA_HOME` tới thư mục Java dùng để chạy VnCoreNLP.

Từ gốc repo, cài `services/ai/requirements-phobert.txt` vào môi trường Python riêng. Ví dụ dưới đây dùng checkpoint và bộ tách từ đã chuẩn bị trong `tmp/w05-phobert`:

```powershell
$env:JOBSHIELD_MODEL_TYPE = 'phobert'
$env:JOBSHIELD_PHOBERT_CHECKPOINT = (Resolve-Path tmp/w05-phobert/checkpoint).Path
$env:JOBSHIELD_VNCORENLP_DIR = (Resolve-Path tmp/w05-phobert/vncorenlp).Path
.\tmp\w05-phobert\.venv\Scripts\python.exe -m uvicorn main:app --app-dir services/ai --host 127.0.0.1 --port 8001
```

Trong terminal thứ hai, chạy `dotnet run --project backend --launch-profile http` và gửi `POST /api/analyze` với JSON `{"text":"Nội dung cần phân tích"}`. Log FastAPI ghi đường dẫn checkpoint đã nạp. Chế độ mặc định của script demo phía trên là TF-IDF, dùng `JOBSHIELD_MODEL_PATH`.

## Đề tài

Xây dựng JobShield: công cụ nhận diện dấu hiệu lừa đảo trong tin tuyển dụng cho sinh viên dựa trên phân loại văn bản có giải thích.

Sinh viên thường phải tự nhận diện dấu hiệu đáng ngờ và đối chiếu nhiều nguồn khi tìm việc làm thêm hoặc thực tập. Đồ án dự kiến phân loại nội dung tin, chỉ ra dấu hiệu và đoạn bằng chứng để hỗ trợ sinh viên đánh giá. Nhãn “đáng ngờ” phản ánh tiêu chí nghiên cứu; nhãn “bình thường” không bảo đảm nhà tuyển dụng an toàn.

## Câu hỏi nghiên cứu và giả thuyết

- **CH1:** PhoBERT có nhận diện tin tuyển dụng đáng ngờ tốt hơn phương pháp từ khóa và TF-IDF trên tập kiểm thử giữ riêng không?
- **H1:** F1 của PhoBERT cao hơn baseline ít nhất 10 điểm phần trăm; recall lớp “đáng ngờ” đạt ít nhất 85%.
- **CH2:** Khi có danh sách dấu hiệu được giải thích, sinh viên có đánh giá đúng nhiều tin hơn và nhanh hơn không?
- **H2:** Tỷ lệ đánh giá đúng tăng ít nhất 15 điểm phần trăm so với tự kiểm tra; thời gian kiểm tra trung bình mỗi tin không tăng.

H1 và H2 là giả thuyết cần kiểm chứng, chưa phải kết quả đạt được. F1, precision và recall được báo cáo riêng để đánh giá chất lượng mô hình trong CH1.

## Bảng trước–sau

Đây là hai chỉ số đánh giá hiệu quả hỗ trợ người dùng cho CH2. Chưa thực hiện đo trước hoặc đo sau.

| Chỉ số | Cách đo | Trước | Sau | Ngày đo | Bằng chứng |
| --- | --- | --- | --- | --- | --- |
| Tỷ lệ đánh giá đúng (%) | Số nhận định đúng / tổng số tin đánh giá × 100. So sánh tự kiểm tra với dùng JobShield trên hai bộ 10 tin tương đương, có đáp án được duyệt. | Chưa đo. Dự kiến ghi nhận khi sinh viên tự kiểm tra tin. | | Trước: dự kiến 19–23/10/2026 (W2). Sau: dự kiến W8. | Chưa có. Sẽ lưu bộ tin, đáp án, phiếu đánh giá đã ẩn danh và bảng tính tổng hợp. |
| Thời gian kiểm tra trung bình (giây/tin) | Tổng thời gian hoàn thành / số tin. Bấm giờ theo cùng hướng dẫn, ghi nhận thời gian ở cả hai điều kiện. | Chưa đo. Dự kiến bấm giờ quá trình tự kiểm tra. | | Trước: dự kiến 19–23/10/2026 (W2). Sau: dự kiến W8. | Chưa có. Sẽ lưu phiếu thời gian đã ẩn danh và bảng tính tổng hợp. |

Hai bộ tin phải có tỷ lệ tin đáng ngờ và độ khó tương đương. Kiểm tra cả thời gian và độ đúng; cân nhắc ảnh hưởng của thứ tự thực hiện khi thiết kế pilot. Thông tin đơn vị pilot và lịch đo sẽ được cập nhật khi có xác nhận thực tế.

## Phạm vi dự kiến

- Xây dựng bảng tiêu chí dấu hiệu (codebook) từ nguồn chính thống trước khi gán nhãn.
- Chuẩn bị ít nhất 500 tin có nhãn; hai người gán độc lập trên ít nhất 20% dữ liệu và báo cáo Cohen’s kappa trước khi xử lý bất đồng.
- So sánh baseline từ khóa, TF-IDF kết hợp bộ phân loại và PhoBERT trên cùng tập kiểm thử giữ riêng. Dùng tập validation để chọn cấu hình và ngưỡng cảnh báo.
- Cung cấp dấu hiệu và đoạn bằng chứng; đánh giá mức trùng khớp với dấu hiệu do người gán nhãn chọn.
- Dự kiến xây dựng API FastAPI, giao diện React và kết nối Google Sheets để phối hợp pilot.
- Duy trì bộ eval phát triển ít nhất 30 tình huống, trong đó ít nhất 10 tình huống từ lỗi từng gặp, tách riêng với tập kiểm thử cuối cùng.

Pilot dự kiến với ít nhất 20 sinh viên trong 4–6 tuần; chưa có xác nhận của người đại diện. Phạm vi hiện tại không bao gồm tự động thu thập tin trên mạng xã hội, kết luận pháp lý về doanh nghiệp hoặc ứng dụng mobile.

## Đóng băng tính năng `v0.9`

Từ Tuần 7, sản phẩm chốt phạm vi và không bổ sung tính năng mới cho mốc `v0.9`:

1. **Phân tích tin tuyển dụng & hội thoại:** Toàn luồng React → ASP.NET Core (.NET 10) → FastAPI (`phobert-v3-typeA`), nhận diện 8 nhóm dấu hiệu `G01`–`G08` có câu bằng chứng (`<mark>`), giải thích và vụ việc tham chiếu (`RecruitmentScenarios.json`).
2. **Tách câu linh hoạt:** Hỗ trợ Groq (`openai/gpt-oss-20b`) và tự động chuyển sang bộ tách câu cục bộ (`LocalSentenceSplitter`) khi thiếu khóa, quá hạn hoặc lỗi kết nối.
3. **Trải nghiệm UX Thám tử Shield:** Giao diện 4 chặng kể chuyện, 4 biểu cảm dõi chuột, nút đáp nhanh theo ngữ cảnh, bấm ghim `G01`–`G08` cuộn tới câu bằng chứng và tùy chọn góp ý kết quả qua Google Form.
4. **4 lớp bảo mật:** Rate Limiting (`20 req/phút`) & Input Guard (`≤ 10.000` ký tự, chặn `\0`, body `≤ 32 KB`); che PII giữ độ dài (`PiiRedactor`) & quản lý bí mật ngoài repo; chống Prompt Injection (`<user_text>` + hậu kiểm nguyên văn + fallback); 5 HTTP Security Headers không trùng lặp & phân đoạn mạng Docker (chỉ mở cổng `5173`).
5. **Đóng gói & CI tự động:** Docker Compose 3 container (`ai`, `backend`, `frontend`) chạy demo cục bộ theo hướng dẫn phía trên, cùng GitHub Actions CI (`.github/workflows/ci.yml`) chạy `dotnet test`, `pytest` và `npm run build` trên mỗi lần đẩy mã.