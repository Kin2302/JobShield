# So sánh PhoBERT v1 và v2 trên 30 mẫu nguồn thật

Ngày 18/11/2026, PhoBERT v2 nhận ra **5/15** mẫu đáng ngờ, thêm một mẫu so với v1. Hai bản đều báo nhầm **1/15** mẫu đối chứng. F1 lớp đáng ngờ tăng từ **40,00%** lên **47,62%**. [Dự đoán từng mẫu](results.json)

| Chỉ số | PhoBERT v1 | PhoBERT v2 |
| --- | ---: | ---: |
| Phát hiện đúng | 4/15 | 5/15 |
| Bỏ sót | 11/15 | 10/15 |
| Cảnh báo nhầm | 1/15 | 1/15 |
| Đối chứng đúng | 14/15 | 14/15 |
| Tổng số mẫu đúng | 18/30 | 19/30 |
| Precision lớp đáng ngờ | 80,00% | 83,33% |
| Recall lớp đáng ngờ | 26,67% | 33,33% |
| F1 lớp đáng ngờ | 40,00% | 47,62% |

## Các mẫu đổi nhãn

| Mẫu | Nhãn tham chiếu | v1 | v2 |
| --- | --- | --- | --- |
| `JS-TR024` có điều kiện đóng tiền để làm hồ sơ và hợp đồng | Đáng ngờ, A01 | Chưa phát hiện | Đáng ngờ |
| `JS-TR007` nói rõ người dạy không phải đóng phí nhận lớp trước | Chưa phát hiện | Đáng ngờ | Chưa phát hiện |
| `JS-TR021` nói rõ công ty không thu phí tuyển dụng | Chưa phát hiện | Chưa phát hiện | Đáng ngờ |

Trong các mẫu đáng ngờ, v1 và v2 lần lượt nhận ra **4/10** và **5/10** mẫu có mã tham chiếu A01. Cả hai bản bỏ sót cả **4 mẫu A02** và **1 mẫu A03**. Các mã trong bảng là nhãn tham chiếu của tập test. Đầu ra PhoBERT là nhãn của toàn đoạn trích. Tập test nhỏ và kết quả chỉ mô tả các đoạn trích đã lấy mẫu. [Thành phần và hồ sơ nguồn của tập test](../../../../data/v2/test-real/README.md)

## Cách chạy và xác minh

Hai checkpoint nhận cùng văn bản theo thứ tự đoạn gốc, cùng VnCoreNLP 1.2, OpenJDK 21, CPU và cấu hình tối đa 256 token của dịch vụ AI. Mỗi checkpoint chạy trong một tiến trình Python riêng. `TestClient` treo khi Python khởi tạo kết nối nội bộ trên Windows, nên lượt đo gọi trực tiếp `PhoBertClassifier.predict_label`, hàm phân loại của FastAPI. Kết quả xác minh nhãn mô hình. Luồng HTTP và giao diện cần lượt kiểm thử riêng.

Sau khi chạy, đã kiểm tra lại 60 dự đoán trên 30 ID, tính lại hai ma trận nhầm lẫn và F1 từ dự đoán từng mẫu, đối chiếu SHA-256 của tập test và hai tệp trọng số. Trọng số v1 khớp checkpoint trong kiểm thử W05. [Manifest tập test](../../../../data/v2/test-real/manifest.json) · [Kết quả W05](../w05-model-comparison/results.json)

Chạy lại từ thư mục gốc JobShield bằng môi trường Python đã dùng cho W05. Đặt `JAVA_HOME` thành thư mục OpenJDK 21 của máy chạy.

```powershell
$env:JAVA_HOME = 'C:\Program Files\Microsoft\jdk-21.0.13.21-hotspot'
$env:Path = (Join-Path $env:JAVA_HOME 'bin') + ';' + $env:Path
$env:HF_HUB_OFFLINE = '1'
$env:OMP_NUM_THREADS = '4'
.\tmp\w05-phobert\.venv\Scripts\python.exe -Bu -X utf8 .\tmp\phobert-v1-v2-real-test\run_eval.py
```
