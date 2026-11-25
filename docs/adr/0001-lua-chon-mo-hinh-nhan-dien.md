# ADR 001 — Lựa chọn mô hình nhận diện cho JobShield

## Trạng thái (Status)

Đã chấp nhận cho phiên bản v3 hiện hành (`phobert-v3-typeA`), cập nhật ngày 24/11/2026. TF-IDF + Logistic Regression (`tfidf-v3`) được giữ làm baseline đối chiếu theo đề cương.

## Bối cảnh (Context)

JobShield phân loại tin tuyển dụng và hội thoại tiếng Việt theo 8 nhóm hành vi lừa đảo lõi `G01`–`G08` ([Codebook v3](../../data/v3/CODEBOOK.md)) và phải trả về câu bằng chứng cụ thể. Tập dữ liệu v3 gồm `1.223` mẫu đã gán nhãn và kiểm tra đồng thuận liên người gán (`κ = 0,9883`).

### Các phương án cân nhắc

| Phương án | Cách áp dụng | Kết quả đánh giá trên cùng bộ Test v3 / Holdout | Ghi chú |
| --- | --- | --- | --- |
| **A — PhoBERT v3 Kiểu A (`phobert-v3-typeA`, 2 cổng chung encoder)** | 1 encoder `vinai/phobert-base` + 2 đầu ra (cổng tài liệu & 8 mã `G01`–`G08` theo câu), tối ưu ngưỡng trên validation | Test v3 `F1 = 0,8667` (`Recall = 0,8485`, `Precision = 0,8857`), Holdout báo động giả `0/54`, CPU `p50 = 602 ms` | Đạt cân bằng tốt nhất giữa độ chính xác, báo động giả và tốc độ CPU |
| **B — PhoBERT v3 Kiểu B (2 mô hình riêng)** | Tách riêng mô hình cổng tài liệu và mô hình trích bằng chứng | Đạt `F1` tương đương nhưng gấp đôi dung lượng checkpoint và chi phí nạp RAM | Không tối ưu cho triển khai Docker CPU |
| **C — XLM-RoBERTa base (`xlmr-v3`)** | Thay encoder đa ngôn ngữ | Chi phí bộ nhớ/suy luận cao hơn trên CPU | Không vượt trội rõ rệt so với PhoBERT tiếng Việt |
| **D — TF-IDF + Logistic Regression (`tfidf-v3`)** | Baseline theo đề cương | Giữ làm mốc so sánh cho câu hỏi nghiên cứu CH1/H1 | Yếu hơn với diễn đạt hội thoại biến thể |

Chi tiết so sánh và số liệu đo được ghi tại [Báo cáo so sánh v3](../../tests/evaluation/v3-model-comparison/REPORT.md).

## Quyết định (Decision)

Chốt sử dụng **`phobert-v3-typeA`** (dựa trên `vinai/phobert-base`, giấy phép MIT) làm mô hình nhận diện chính thức cho JobShield v3:

- Sử dụng bộ tách từ `VnCoreNLP` (`py-vncorenlp`) ở chế độ chỉ đọc và cắt cửa sổ ngữ cảnh cân bằng 256 token quanh câu đang xét.
- Áp dụng giải mã hai cổng (`tau_gate` và ngưỡng riêng từng mã `G01`–`G08` trong `thresholds.json`) để bảo toàn bất biến: `suspicious` khi và chỉ khi `findings` khác rỗng.
- Giữ `tfidf-v3` làm baseline kiểm chứng giả thuyết nghiên cứu H1.

## Hệ quả (Consequences)

- Checkpoint `models/v3/jobshield-phobert-v3-typeA/` và `models/vncorenlp/` được gắn dạng volume chỉ đọc vào container AI khi chạy Docker (không nhồi vào Git hoặc image).
- Giới hạn ngữ cảnh `256` token/câu đã được xử lý bằng cửa sổ trượt quanh câu đang xét; `Evidence F1` còn khiêm tốn (`0,2602`) được ghi nhận là giới hạn hiện tại cần theo dõi.
- Phải giữ thông báo bản quyền MIT của `vinai/phobert-base` khi phân phối.
