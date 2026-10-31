# JobShield

Công cụ hỗ trợ sinh viên nhận diện dấu hiệu đáng ngờ trong tin tuyển dụng tiếng Việt bằng phân loại văn bản có giải thích.

**Trạng thái:** Đã có bản Hello World W03 chạy local từ React qua ASP.NET Core đến FastAPI và trả kết quả về giao diện. Bộ xử lý hiện là baseline quy tắc; chưa fine-tune PhoBERT, chưa triển khai database hoặc có kết quả thực nghiệm mô hình.

## Chạy toàn bộ demo

Môi trường đã kiểm tra: **.NET SDK 10.0.302**, **Node.js 22.23.1 / npm 10.9.8**, **Python 3.14.2**, Windows PowerShell. Backend dùng `net10.0` và phiên bản C# mặc định của SDK, không cần cài package NuGet ngoài shared framework. React và Vite được ghim phiên bản trong `package.json`/`package-lock.json`.

Clone repo rồi chạy các lệnh sau từ gốc `JobShield`:

```powershell
git clone https://github.com/Kin2302/JobShield.git
cd JobShield
python -m venv services/ai/.venv
.\services\ai\.venv\Scripts\python.exe -m pip install -r services/ai/requirements.txt
dotnet build backend -c Release
npm --prefix frontend ci
npm --prefix frontend run build
powershell -NoProfile -File scripts/start-demo.ps1
```

Mở **[JobShield local](http://127.0.0.1:5173)**. Script chạy ba dịch vụ nền và kiểm tra HTTP toàn luồng trước khi thông báo sẵn sàng. Những lần sau không cần cài lại; sau khi sửa code phải build lại phần tương ứng.

| Thành phần | Địa chỉ | Vai trò |
| --- | --- | --- |
| React / Vite preview | `http://127.0.0.1:5173` | Phục vụ bản frontend đã build; proxy `/api` sang ASP.NET Core. |
| ASP.NET Core | `http://127.0.0.1:5000/api/analyze` | Kiểm tra request và gọi FastAPI bằng named `HttpClient`. |
| FastAPI | `http://127.0.0.1:8001/analyze` | Chạy baseline; Swagger ở `/docs`. |

Luồng: **trình duyệt → Vite proxy → ASP.NET Core → FastAPI → ASP.NET Core → giao diện**. Proxy giữ request cùng origin với frontend; trình duyệt không gọi thẳng FastAPI. Vite preview phục vụ demo local, chưa phải phương án hosting production.

Dừng các dịch vụ do script khởi chạy:

```powershell
powershell -NoProfile -File scripts/stop-demo.ps1
```

Log và danh sách tiến trình nằm trong `tmp/hello-world/`, được loại khỏi Git. Nếu cổng 5000, 5173 hoặc 8001 đang dùng, script sẽ báo lỗi và giữ dịch vụ có sẵn. Nếu demo đã chạy thì mở trình duyệt, hoặc dừng bằng script trước khi khởi chạy lại.

### Kiểm tra và quay minh chứng

Sau khi bật demo, chạy từ gốc repo:

```powershell
# 10 ca HTTP qua frontend proxy va ca hai backend
.\services\ai\.venv\Scripts\python.exe -m pytest tests -q

# 20 ca API FastAPI
Push-Location services/ai
.\.venv\Scripts\python.exe -m pytest tests -q
Pop-Location
```

Đã kiểm tra 30 ca tự động, build cả backend/frontend và thao tác trên giao diện. Đã thử riêng các lỗi FastAPI mất kết nối (`503`), quá thời gian 10 giây (`504`), HTTP lỗi hoặc dữ liệu không hợp lệ (`502`). Lỗi không được biến thành kết quả “chưa phát hiện”. Backend trả `400` cho request rỗng/sai kiểu; FastAPI trả `422` khi được gọi trực tiếp với dữ liệu không hợp lệ.

Gợi ý video 30–60 giây:

1. Mở giao diện, chọn **Có yêu cầu phí** → **Phân tích nội dung**; chỉ đoạn trích khớp.
2. Chọn **Phủ định thu phí**, phân tích lại; kết quả chưa phát hiện theo quy tắc hiện có.
3. Chọn **Tin không khớp mẫu**, phân tích; nhắc đây là baseline hẹp, chưa phải mô hình đã huấn luyện.

**[Thư mục video minh chứng W03 trên Google Drive](https://drive.google.com/drive/folders/1GIJ9cVqN9fyTKCgzU2EjFt-gwvon8sb3?usp=sharing)** — người thực hiện sẽ upload video sau khi quay; repo chưa xác nhận video đã được tải lên hoặc quyền xem thư mục.

### Bản đồ code Hello World

| File | Trách nhiệm |
| --- | --- |
| [App.jsx](frontend/src/App.jsx) | Trạng thái ô nhập, gọi API bằng `fetch`, hiển thị chờ/kết quả/lỗi; xóa kết quả cũ khi thay đầu vào. |
| [styles.css](frontend/src/styles.css) | Bố cục hai cột, chuyển một cột trên màn hình hẹp; màu sắc và trạng thái focus. |
| [vite.config.js](frontend/vite.config.js) | Cổng frontend và proxy dùng khi phát triển hoặc preview bản build. |
| [Program.cs](backend/Program.cs) | Đăng ký `HttpClient`, endpoint `/api/analyze`, kiểm tra request/response và xử lý lỗi AI. |
| [AnalysisContracts.cs](backend/AnalysisContracts.cs) | Các record request/response và ánh xạ `baseline_version` từ JSON. |
| [appsettings.json](backend/appsettings.json) | URL FastAPI; có thể ghi đè bằng biến môi trường `AiService__BaseUrl`. |
| [main.py](services/ai/main.py), [baseline.py](services/ai/baseline.py) | API nhận diện và hai mẫu quy tắc được mô tả bên dưới. |
| [test_demo.py](tests/test_demo.py) | Kiểm tra bản build và request qua đủ các dịch vụ đang chạy. |
| [start-demo.ps1](scripts/start-demo.ps1), [stop-demo.ps1](scripts/stop-demo.ps1) | Chạy/dừng dịch vụ local, giữ log trong thư mục tạm. |

`useState` giữ trạng thái giao diện; `fetch` gửi JSON. ASP.NET Core dùng `async/await` khi chờ HTTP và truyền `CancellationToken` khi request bị hủy. DI cấp `IHttpClientFactory`; không thêm service layer cho một endpoint. Các record chỉ mô tả dữ liệu truyền qua API. Không lưu tin đã phân tích vào database, file hoặc browser storage.

## Chạy phần 1 — dịch vụ AI

Yêu cầu: Python 3.14 (phiên bản đã kiểm tra: 3.14.2). Các lệnh PowerShell dưới đây chạy từ gốc repo:

```powershell
cd services/ai
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

Không cần kích hoạt môi trường ảo; các lệnh gọi trực tiếp Python trong `.venv`.
Khi đã cài xong, lần sau chỉ cần chạy lệnh Uvicorn. Dừng bằng `Ctrl+C`.

Mở [Swagger UI](http://127.0.0.1:8001/docs), chọn `POST /analyze` → **Try it out**, gửi:

```json
{"text": "Em cần nộp phí hồ sơ trước khi nhận việc."}
```

Hoặc mở PowerShell thứ hai:

```powershell
$body = @{ text = 'Em cần nộp phí hồ sơ trước khi nhận việc.' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/analyze `
  -ContentType 'application/json; charset=utf-8' `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) | ConvertTo-Json -Depth 5
```

Kết quả:

```json
{
  "baseline_version": "rules-v0.1",
  "message": "Phát hiện dấu hiệu theo quy tắc hiện có.",
  "signals": [
    {
      "code": "UPFRONT_JOB_FEE",
      "name": "Yêu cầu phí trước khi nhận việc",
      "evidence": "nộp phí hồ sơ trước khi nhận việc"
    }
  ]
}
```

Đây là hợp đồng tối thiểu cho checkpoint baseline, chưa phải toàn bộ output AI đã thảo luận. `UPFRONT_JOB_FEE` là mã của quy tắc demo, chưa phải bộ nhãn nghiên cứu đã duyệt. Không trả điểm xác suất hoặc nhãn tổng quát từ mô hình vì chưa có mô hình phân loại.

### Phạm vi đã thống nhất

- Chỉ khớp hai cụm `nộp phí hồ sơ trước khi nhận việc` và `đóng phí hồ sơ trước khi nhận việc`, không phân biệt hoa/thường; các cụm có thể nằm trong một tin dài.
- Giữ nguyên chữ gốc trong `evidence`. Một lần khớp tạo một mục trong `signals`.
- Tách câu bằng dấu `.`, `!`, `?` hoặc xuống dòng; bỏ qua cả câu có từ `không`, bao gồm `không cần` và `không phải`. Phủ định ở câu khác không loại trừ câu đang xét.
- Không ghép các cụm từ qua nhiều câu. Dấu phẩy và dấu chấm phẩy chưa được dùng làm ranh giới câu.
- Không khớp thì trả `signals: []` và `Chưa phát hiện theo quy tắc hiện có.`; kết quả này không bảo đảm nội dung an toàn.
- Thiếu `text`, sai kiểu hoặc chỉ có khoảng trắng thì trả HTTP `422`.

Quy tắc còn có thể nhận sai câu hỏi/lời kể chứa nguyên mẫu hoặc bỏ sót câu có từ `không` nhưng vẫn yêu cầu đóng phí. Bản đầu chưa xử lý diễn đạt lại, nhiều khoảng trắng, Unicode tổ hợp hoặc ngữ cảnh phức tạp. Test kiểm chứng hành vi đã chốt, không phải đánh giá chất lượng trên dữ liệu thực tế. Dịch vụ không lưu nội dung phân tích vào database hoặc file.

### Đọc code theo thứ tự

| File | Trách nhiệm |
| --- | --- |
| [main.py](services/ai/main.py) | Định nghĩa request/response; kiểm tra `text`; khai báo `POST /analyze`; gọi baseline và đóng gói kết quả. |
| [baseline.py](services/ai/baseline.py) | Hàm `find_fee_evidence`: tách câu, loại trừ phủ định, tìm hai mẫu và trả đoạn trích nguyên văn. |
| [test_analyze.py](services/ai/tests/test_analyze.py) | Gửi request qua TestClient và kiểm tra hành vi API, không mock baseline. |
| [requirements.txt](services/ai/requirements.txt) | Cố định phiên bản thư viện trực tiếp đã dùng. |

Luồng: JSON → `AnalyzeRequest` → `analyze()` → `find_fee_evidence()` → danh sách `Signal` → `AnalyzeResponse` → JSON.

FastAPI khai báo API; Pydantic (dependency của FastAPI) kiểm tra dữ liệu và định nghĩa schema; Uvicorn chạy HTTP server. `re` là thư viện có sẵn của Python để tìm mẫu trong chuỗi. Pytest chạy test; HTTPX phục vụ TestClient theo [hướng dẫn FastAPI](https://fastapi.tiangolo.com/tutorial/testing/). TestClient chạy ứng dụng trong tiến trình test, không cần bật Uvicorn.

Chạy test từ `services/ai`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
.\.venv\Scripts\python.exe -m pip check
```

Bộ dependency hiện có cảnh báo từ Starlette rằng TestClient sẽ chuyển từ `httpx` sang `httpx2`; không tắt cảnh báo. Phiên bản đã ghim vẫn chạy test được. Khi nâng thư viện cần kiểm tra lại tương thích. Trong sandbox của Codex trên máy này, vòng lặp mạng của Python có thể bị treo; đã chạy test và HTTP smoke test ngoài sandbox để kiểm chứng, không thêm workaround vào code sản phẩm.

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

## Tiến độ W01

- Đã xác định vấn đề, CH1–CH2 và H1–H2 theo định hướng GVHD.
- Đã chuẩn bị bản nháp Chương 1 và nhật ký tuần, nhật ký AI ở bộ hồ sơ nộp học phần.
- Chưa triển khai mã nguồn ứng dụng, gán nhãn dữ liệu hoặc đánh giá mô hình.
- Chưa có demo hoạt động; sẽ cập nhật đường dẫn sau khi triển khai và kiểm tra.

## Sử dụng AI

Có sử dụng Codex để hỗ trợ làm rõ yêu cầu và soạn tài liệu ban đầu. Sinh viên cần kiểm tra, chỉnh sửa và khai báo các lượt sử dụng trong nhật ký AI. Các số đo, phỏng vấn và minh chứng chỉ được cập nhật khi đã thực hiện thực tế.
