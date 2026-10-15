# JobShield

Công cụ hỗ trợ sinh viên nhận diện dấu hiệu đáng ngờ trong tin tuyển dụng tiếng Việt bằng phân loại văn bản có giải thích.

**Trạng thái:** Chuẩn bị đề tài và tài liệu tuần 1 (W01). Chưa có mô hình được huấn luyện, kết quả thực nghiệm hoặc demo hoạt động.

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
