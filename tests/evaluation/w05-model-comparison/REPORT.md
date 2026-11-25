# JobShield — So sánh TF-IDF và PhoBERT trên 24 tình huống

**Ngày chạy** 11/11/2026 · **Kho kịch bản** `w05.1` · **Codebook** `jobshield-v0.2`

## Kết quả nhãn tổng

| Mô hình | Phát hiện đúng | Bỏ sót | Cảnh báo nhầm | Đối chứng đúng | Tổng số ca đúng | F1 lớp đáng ngờ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TF-IDF + Logistic Regression | 0/15 | 15 | 0 | 9/9 | 9/24 (37,5%) | 0,0% |
| PhoBERT | 13/15 | 2 | 6 | 3/9 | 16/24 (66,7%) | 76,5% |

| Đầu vào | Số ca | TF-IDF đúng | PhoBERT đúng | Lỗi của PhoBERT |
| --- | ---: | ---: | ---: | --- |
| Tin tuyển dụng | 8 | 3 | 5 | Bỏ sót T01, T05. Cảnh báo nhầm T08. |
| Tin tuyển dụng + hội thoại | 8 | 3 | 6 | Cảnh báo nhầm M06, M08. |
| Hội thoại | 8 | 3 | 5 | Cảnh báo nhầm H06, H07, H08. |

TF-IDF trả `not_detected` cho cả 24 ca. PhoBERT trả `suspicious` cho 19 ca, gồm 13 ca đúng và 6 ca đối chứng. Hai mô hình trả khác nhau ở 19 ca. Trong nhóm hội thoại, PhoBERT cảnh báo cả 8 ca, gồm một cuộc trao đổi chỉ nói về lương và lịch thử việc (H07).

## Đối chiếu dấu hiệu và bằng chứng

Backend trả cùng mã và câu trích ở cả hai chế độ. Kết quả khớp toàn bộ đáp án ở **18/24 ca**, gồm 9 ca có bằng chứng và 9 ca đối chứng. Backend trả **12/18 đoạn bằng chứng kỳ vọng** và không trả thêm đoạn ngoài đáp án. Tất cả 12 đoạn trả về khớp nguyên văn và dẫn đúng nguồn tham chiếu của mã.

- **T02, T04, M04, H02** có yêu cầu trả tiền hoặc ứng tiền được diễn đạt khác với các mẫu mà quy tắc hiện nhận ra. Cả hai chế độ đều thiếu bằng chứng ở bốn ca này. PhoBERT vẫn gắn nhãn đáng ngờ.
- **M02, H04** cần nối nhiều lượt nói. M02 có điều kiện đóng tiền trong câu hỏi của ứng viên và lời xác nhận của nhà tuyển dụng. H04 tách yêu cầu ứng tiền và lời hứa hoàn trả sang các lượt khác nhau. PhoBERT gắn nhãn đáng ngờ cho cả hai, còn backend không trả đoạn trích.
- **T01, T05** cho thấy nhãn và bằng chứng có thể khác nhau. Cả hai mô hình trả `not_detected`, trong khi backend vẫn trả A01 ở T01 và cả A01/A02 ở T05.

## Cách chạy và phạm vi

24 ca được soạn mới để kiểm tra nội bộ, gồm 8 ca mỗi nhóm. Mỗi nhóm có 5 ca đáng ngờ theo codebook và 3 ca đối chứng. Đáp án được lưu trước khi chạy và các đầu vào không trùng nguyên văn với tập train nội bộ. Bộ ca là dữ liệu mô phỏng có chủ đích, chưa qua gán nhãn độc lập của người và chưa dùng để kết luận hiệu năng trên tin thật hay kiểm chứng H1.

Mỗi chế độ chạy 24 lượt `/api/prepare` và 24 lượt `/api/analyze`. Bước chuẩn bị dùng chế độ tách theo dòng, Groq tắt. Cả hai chế độ giữ đúng ranh giới của 24 đầu vào đã được soạn một đoạn mỗi dòng. Chế độ này gắn các dòng trong đầu vào nhiều dòng thành hội thoại với vai chưa rõ, kể cả ở nhóm chỉ có tin tuyển dụng. Khi phân tích, hai mô hình nhận cùng văn bản gốc và cùng ranh giới, vai đã xác nhận theo bộ ca. Cách chạy này đo nhãn mô hình và bằng chứng sau bước xác nhận.

## Kết quả từng ca

Chữ đậm đánh dấu nhãn lệch kỳ vọng. Dấu ` / ` biểu thị xuống dòng trong đầu vào và câu trích. Cột bằng chứng trả về dùng chung cho hai chế độ. Vai người nói, offset, phản hồi gốc và link nguồn theo từng ca có trong [kết quả JSON](results.json). [Bộ 24 tình huống và đáp án](cases.json).

### Tin tuyển dụng

| Ca | Nội dung đưa vào | Nhãn kỳ vọng | TF-IDF | PhoBERT | Bằng chứng kỳ vọng | Bằng chứng trả về |
| --- | --- | --- | --- | --- | --- | --- |
| T01 | Tuyển sinh viên trực quầy mượn sách theo ca tối. / Ứng viên phải đóng phí xét hồ sơ 160.000 đồng để được xét tuyển. | Đáng ngờ | **Chưa phát hiện** | **Chưa phát hiện** | A01 · Ứng viên phải đóng phí xét hồ sơ 160.000 đồng để được xét tuyển. | A01 · Ứng viên phải đóng phí xét hồ sơ 160.000 đồng để được xét tuyển. |
| T02 | Cần người hỗ trợ quầy đổi vé trong hai ngày hội sách. / Muốn giữ được suất làm cuối tuần, người đăng ký gửi trước 240.000 đồng vào tài khoản phụ trách. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Muốn giữ được suất làm cuối tuần, người đăng ký gửi trước 240.000 đồng vào tài khoản phụ trách. | — |
| T03 | Tuyển cộng tác viên xử lý đơn nội thất trong ca chiều. / Ứng viên phải dùng tiền cá nhân để xử lý đơn và sẽ nhận lại vốn sau khi xác nhận giao hàng. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Ứng viên phải dùng tiền cá nhân để xử lý đơn và sẽ nhận lại vốn sau khi xác nhận giao hàng. | A02 · Ứng viên phải dùng tiền cá nhân để xử lý đơn và sẽ nhận lại vốn sau khi xác nhận giao hàng. |
| T04 | Tuyển cộng tác viên kiểm tra quy trình mua vé trực tuyến. / Mỗi lượt kiểm tra yêu cầu bạn lấy tiền túi thanh toán một vé, sau đó hệ thống hoàn lại đúng giá vé kèm 12% công. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Mỗi lượt kiểm tra yêu cầu bạn lấy tiền túi thanh toán một vé, sau đó hệ thống hoàn lại đúng giá vé kèm 12% công. | — |
| T05 | Tuyển cộng tác viên xử lý đơn thiết bị gia dụng. / Người đăng ký phải nộp phí đồng phục trước khi được xếp ca. / Ứng viên phải nạp tiền cá nhân để làm nhiệm vụ kiểm đơn rồi nhận lại vốn và hoa hồng. | Đáng ngờ | **Chưa phát hiện** | **Chưa phát hiện** | A01 · Người đăng ký phải nộp phí đồng phục trước khi được xếp ca. · A02 · Ứng viên phải nạp tiền cá nhân để làm nhiệm vụ kiểm đơn rồi nhận lại vốn và hoa hồng. | A01 · Người đăng ký phải nộp phí đồng phục trước khi được xếp ca. · A02 · Ứng viên phải nạp tiền cá nhân để làm nhiệm vụ kiểm đơn rồi nhận lại vốn và hoa hồng. |
| T06 | Tiệm bánh cần hai bạn phụ quầy từ 17 giờ đến 21 giờ, trả lương theo giờ. / Gửi lịch rảnh để cửa hàng hẹn phỏng vấn trực tiếp. | Chưa phát hiện | Chưa phát hiện | Chưa phát hiện | — | — |
| T07 | Tuyển nhân viên soạn hàng theo ca, lương 32.000 đồng mỗi giờ. / Không thu phí đồng phục hay phí xét hồ sơ khi tuyển dụng. | Chưa phát hiện | Chưa phát hiện | Chưa phát hiện | — | — |
| T08 | Tuyển nhân viên đi lấy hàng mẫu trong nội thành. / Công ty sẽ ứng tiền mua hàng mẫu, nhân viên giữ hóa đơn để quyết toán. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |

### Tin tuyển dụng + hội thoại

| Ca | Nội dung đưa vào | Nhãn kỳ vọng | TF-IDF | PhoBERT | Bằng chứng kỳ vọng | Bằng chứng trả về |
| --- | --- | --- | --- | --- | --- | --- |
| M01 | Nhà in tuyển sinh viên sắp xếp đơn in buổi sáng. / Ứng viên: Em có thể bắt đầu thứ hai được không ạ? / Bên tuyển dụng: Em cần nộp phí hồ sơ 185.000 đồng trước khi được xếp ca. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Bên tuyển dụng: Em cần nộp phí hồ sơ 185.000 đồng trước khi được xếp ca. | A01 · Bên tuyển dụng: Em cần nộp phí hồ sơ 185.000 đồng trước khi được xếp ca. |
| M02 | Tuyển trợ lý gian hàng tại hội chợ cuối tuần. / Ứng viên: Em phải chuyển trước 220.000 đồng mới được giữ suất phụ gian hàng đúng không ạ? / Bên tuyển dụng: Đúng rồi, bên chị chỉ giữ suất khi nhận được khoản đó. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Ứng viên: Em phải chuyển trước 220.000 đồng mới được giữ suất phụ gian hàng đúng không ạ? / Bên tuyển dụng: Đúng rồi, bên chị chỉ giữ suất khi nhận được khoản đó. | — |
| M03 | Tuyển cộng tác viên đối chiếu đơn hàng đồ thể thao. / Ứng viên: Khi có đơn thì em thao tác thế nào? / Bên tuyển dụng: Em phải ứng tiền để hoàn thành đơn thử rồi nhận lại vốn và hoa hồng. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Bên tuyển dụng: Em phải ứng tiền để hoàn thành đơn thử rồi nhận lại vốn và hoa hồng. | A02 · Bên tuyển dụng: Em phải ứng tiền để hoàn thành đơn thử rồi nhận lại vốn và hoa hồng. |
| M04 | Tuyển cộng tác viên kiểm tra quy trình đặt món, làm theo lượt. / Bên tuyển dụng: Để thực hiện mỗi lượt thử, em dùng số dư ví cá nhân trả trước tiền món, bên chị chuyển lại toàn bộ tiền và phần công sau khi xong. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Bên tuyển dụng: Để thực hiện mỗi lượt thử, em dùng số dư ví cá nhân trả trước tiền món, bên chị chuyển lại toàn bộ tiền và phần công sau khi xong. | — |
| M05 | Tuyển người hỗ trợ gian hàng bán đồ thủ công trực tuyến. / Ứng viên phải nộp khoản phí xác nhận trước khi được xếp ca. / Ứng viên: Khi vào ca em làm phần nào? / Bên tuyển dụng: Em phải nạp tiền cá nhân để chốt đơn và sẽ nhận lại vốn sau mỗi nhiệm vụ. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Ứng viên phải nộp khoản phí xác nhận trước khi được xếp ca. · A02 · Bên tuyển dụng: Em phải nạp tiền cá nhân để chốt đơn và sẽ nhận lại vốn sau mỗi nhiệm vụ. | A01 · Ứng viên phải nộp khoản phí xác nhận trước khi được xếp ca. · A02 · Bên tuyển dụng: Em phải nạp tiền cá nhân để chốt đơn và sẽ nhận lại vốn sau mỗi nhiệm vụ. |
| M06 | Quán ăn tuyển người chuẩn bị bàn vào ca tối. / Ứng viên: Em phải nộp phí trước khi nhận việc không ạ? / Bên tuyển dụng: Không thu phí tuyển dụng, em chỉ cần mang CV đến buổi gặp. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |
| M07 | Tuyển sinh viên hỗ trợ nhập kho ba buổi mỗi tuần. / Bên tuyển dụng: Em chọn một trong hai ca sáng rồi gửi lịch rảnh nhé. / Ứng viên: Dạ em đăng ký ca sáng thứ tư. | Chưa phát hiện | Chưa phát hiện | Chưa phát hiện | — | — |
| M08 | Tuyển phụ việc trang trí sự kiện bán thời gian. / Ứng viên: Ai thanh toán vật tư cho buổi dựng gian hàng ạ? / Bên tuyển dụng: Công ty sẽ ứng tiền mua vật tư để em làm nhiệm vụ, em chỉ nộp hóa đơn sau buổi. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |

### Hội thoại

| Ca | Nội dung đưa vào | Nhãn kỳ vọng | TF-IDF | PhoBERT | Bằng chứng kỳ vọng | Bằng chứng trả về |
| --- | --- | --- | --- | --- | --- | --- |
| H01 | Ứng viên: Em còn có thể đăng ký ca tối thứ sáu không ạ? / Bên tuyển dụng: Em phải đóng cọc 125.000 đồng để giữ chỗ ca tối thứ sáu. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Bên tuyển dụng: Em phải đóng cọc 125.000 đồng để giữ chỗ ca tối thứ sáu. | A01 · Bên tuyển dụng: Em phải đóng cọc 125.000 đồng để giữ chỗ ca tối thứ sáu. |
| H02 | Ứng viên: Bao giờ em được xếp lịch ở quầy thông tin ạ? / Bên tuyển dụng: Chị chỉ xếp lịch cho em sau khi em tự mua bộ nhận diện giá 275.000 đồng do bên chị bán. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Bên tuyển dụng: Chị chỉ xếp lịch cho em sau khi em tự mua bộ nhận diện giá 275.000 đồng do bên chị bán. | — |
| H03 | Ứng viên: Bước đầu ở ca trực đơn em cần làm gì? / Bên tuyển dụng: Em phải nạp tiền để xử lý đơn mỹ phẩm rồi nhận lại vốn và hoa hồng cuối ca. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Bên tuyển dụng: Em phải nạp tiền để xử lý đơn mỹ phẩm rồi nhận lại vốn và hoa hồng cuối ca. | A02 · Bên tuyển dụng: Em phải nạp tiền để xử lý đơn mỹ phẩm rồi nhận lại vốn và hoa hồng cuối ca. |
| H04 | Bên tuyển dụng: Em phải dùng tiền cá nhân để hoàn thành đơn nước hoa thử. / Ứng viên: Khoản em vừa phải bỏ ra thì sao ạ? / Bên tuyển dụng: Sau khi hoàn thành đơn đó, bên chị hoàn lại toàn bộ khoản em đã ứng và trả công. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A02 · Bên tuyển dụng: Em phải dùng tiền cá nhân để hoàn thành đơn nước hoa thử. / Ứng viên: Khoản em vừa phải bỏ ra thì sao ạ? / Bên tuyển dụng: Sau khi hoàn thành đơn đó, bên chị hoàn lại toàn bộ khoản em đã ứng và trả công. | — |
| H05 | Ứng viên: Chị gửi em điều kiện vào làm và cách nhận đơn được không ạ? / Bên tuyển dụng: Em phải đóng phí hồ sơ để được ký hợp đồng. / Bên tuyển dụng: Em phải ứng tiền cá nhân để xử lý đơn đầu tiên rồi nhận lại vốn và hoa hồng. | Đáng ngờ | **Chưa phát hiện** | Đáng ngờ | A01 · Bên tuyển dụng: Em phải đóng phí hồ sơ để được ký hợp đồng. · A02 · Bên tuyển dụng: Em phải ứng tiền cá nhân để xử lý đơn đầu tiên rồi nhận lại vốn và hoa hồng. | A01 · Bên tuyển dụng: Em phải đóng phí hồ sơ để được ký hợp đồng. · A02 · Bên tuyển dụng: Em phải ứng tiền cá nhân để xử lý đơn đầu tiên rồi nhận lại vốn và hoa hồng. |
| H06 | Ứng viên: Ở chỗ cũ em phải nộp phí để được nhận việc. / Bên tuyển dụng: Bên chị không thu phí khi tuyển, em chỉ cần gửi lịch rảnh. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |
| H07 | Bên tuyển dụng: Ca sáng được trả 38.000 đồng mỗi giờ, nhận lương vào cuối tuần. / Ứng viên: Dạ em đến thử ca sáng thứ bảy. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |
| H08 | Ứng viên: Em có cần tự trả tiền xe đến chỗ phỏng vấn không? / Bên tuyển dụng: Chi phí đi lại do em tự lo, công ty không thu phí hồ sơ. | Chưa phát hiện | Chưa phát hiện | **Đáng ngờ** | — | — |
