# Khảo sát thị trường tuyển dụng 2025–2026 và khung 8 nhóm hành vi lõi JobShield (`G01`–`G08`)

**Ngày lập:** 24/11/2026  
**Phạm vi:** Phần 1 trong lộ trình nâng cấp Dataset & Lõi AI JobShield. Tài liệu kế thừa [khảo sát phủ nguồn 2026](codebook-coverage-2026.md) (`S01`–`S14`, `N01`–`N05`), đối chiếu [Dataset v2](../../../data/v2/README.md) và đề xuất khung nhãn chính thức cho [Codebook v3](../../../data/v3/CODEBOOK.md).

---

## 1. Mục tiêu và hiện trạng nền từ v2

### Mục tiêu
1. Cập nhật bức tranh thủ đoạn lừa đảo tuyển dụng nhắm vào sinh viên và người mới đi làm tại Việt Nam giai đoạn **2025–2026** từ nguồn công khai có kiểm chứng, tránh trùng lặp với 19 nguồn đã ghi ở bản khảo sát trước (`S01`–`S14`, `N01`–`N05`).
2. Gom 18 mã hoạt động rời rạc của [Codebook v2](../../../data/v2/CODEBOOK.md) về **8 nhóm hành vi lõi (`G01`–`G08`)** có ranh giới câu bằng chứng rõ ràng để lõi AI (PhoBERT / XLM-RoBERTa / TF-IDF) học ổn định ở quy mô ~1.000–1.400 mẫu, đồng thời đẩy phần phân nhánh chi tiết và kịch bản leo thang về kho JSON [RecruitmentScenarios.json](../../backend/JobShield.Infrastructure/RecruitmentScenarios.json).

### Hiện trạng dữ liệu & mô hình v2 (đã kiểm chứng)
Theo [Dataset v2](../../../data/v2/README.md) (715 mẫu) và [kết quả validation PhoBERT v2](../../services/ai/jobshield-phobert-v2-result/validation.json):
- **Phân bố nhãn cực lệch ở train (589 mẫu: 193 `suspicious`, 396 `not_detected`):** Chỉ **6/18 mã** có dữ liệu (`C11`: 125, `A02`: 64, `A01`: 42, `A07`: 7, `C12`: 5, `A09`: 1); **12 mã còn lại (`A03`–`A06`, `A08`, `A10`–`A16`) có 0 mẫu train**.
- **Tập đánh giá chưa phủ đều hành vi:** `validation` (41 mẫu: 23 dương / 18 âm) chỉ gồm `A01` (19), `A02` (1), `A03` (1), `C11` (1), `C12` (1); `test` (30 mẫu: 15 dương / 15 âm) chỉ gồm `A01` (10), `A02` (4), `A03` (1), `C11` (1); `negative_holdout` (55 mẫu) có 1 `C12` và 54 âm. Toàn bộ `data/v2/*.jsonl` chưa chuẩn hóa trường `input.type` (`posting` / `message`).
- **Hiệu năng mô hình v2:** Trên `validation`, checkpoint ngưỡng `0.45` đúng **40/41** nhãn tổng (`label_f1 = 0.979`) nhưng chỉ **17/41** khớp toàn bộ mã–câu (`evidence_f1 = 0.364`). Theo [STATUS.md](../../tools/data-collection/STATUS.md), trên `test` nguồn thật v2 phát hiện **12/15** mẫu dương nhưng **báo nhầm 9/15** mẫu âm.

> [!NOTE]
> Các con số trên phản ánh độ phủ của tập dữ liệu hiện có và kết quả thử nghiệm v2, **không** dùng làm tỷ lệ phổ biến của thủ đoạn ngoài thị trường.

---

## 2. Kết quả khảo sát cập nhật thị trường Việt Nam 2025–2026

Đợt tra cứu ngày 24/11/2026 bổ sung các nguồn công khai mới (không tính lại `S01`–`S14` và `N01`–`N05` trong [codebook-coverage-2026.md](codebook-coverage-2026.md)). Mỗi nguồn được phân rõ ngày công bố, cấp bằng chứng, kênh phát sinh (`posting` / `message`), hành vi quan sát được trên văn bản và giới hạn bằng chứng.

### 2.1. Mười nguồn trọng điểm đã trích xuất toàn văn (`M01`–`M10`)

| ID | Nguồn & ngày đăng | Cấp bằng chứng & kênh | Hành vi chính & điểm mới 2025–2026 | Giới hạn bằng chứng |
|---|---|---|---|---|
| **M01** | **Bộ Công an**, *Nâng cao cảnh giác trước 25 kịch bản lừa đảo trên không gian mạng năm 2026*, 08/09/2026 ([nguồn](https://bocongan.gov.vn/bai-viet/nang-cao-canh-giac-truoc-25-kich-ban-lua-dao-tren-khong-gian-mang-nam-2026-1788865614)) | Cảnh báo chính thức tổng hợp 5 nhóm / 25 kịch bản (`posting` & `message`) | Nhấn mạnh nhóm tuyển CTV/"việc nhẹ lương cao" cho rút tiền đầu rồi dụ nạp lớn; nhóm AI/Deepfake/DeepVoice giả danh; nhóm phát tán link/QR/app mã độc và phần mềm điều khiển từ xa. | Cảnh báo tổng hợp theo nhóm thủ đoạn, không kèm hội thoại nguyên văn từng ca. |
| **M02** | **VnEconomy**, *Cơ chế mới giúp "chặn" hành vi lừa đảo trong tuyển dụng lao động*, 10/09/2026 ([nguồn](https://vneconomy.vn/manh-tay-xu-ly-van-nan-lua-dao-tuyen-dung-viec-nhe-luong-cao.htm)) | Tin chính sách / pháp lý | Ghi nhận Nghị định 283/2026/NĐ-CP có hiệu lực từ 10/09/2026 quy định xử phạt vi phạm hành chính trong lĩnh vực lao động và đưa người lao động đi làm việc ở nước ngoài. | Tài liệu bối cảnh pháp lý, không cung cấp mẫu văn bản tuyển dụng để train. |
| **M03** | **Báo Lào Cai**, *Cảnh báo bẫy vay tiền khi sinh viên tìm việc gia sư trên Facebook*, 11/10/2026 ([nguồn](https://baolaocai.vn/canh-bao-bay-vay-tien-khi-sinh-vien-tim-viec-gia-su-tren-facebook-post911728.html)) | Tường thuật vụ việc cụ thể của nữ sinh năm 2 (Cầu Diễn, Hà Nội); hội nhóm Facebook → Messenger (`message`) | Tự xưng phụ huynh ở nước ngoài → xin STK trả trước nửa tháng lương → gửi ảnh chuyển khoản giả → hối thúc thao tác "xác nhận/khắc phục lỗi" 2 lần → phát sinh khoản vay ~55 triệu (lãi >30%/năm; gia đình tất toán 58.385.000 đ ngày 02/10 tới tài khoản hiển thị "VAY NHANH" ở MB và cá nhân). | Lời kể phụ huynh & ảnh biên lai sau sự việc; chưa công bố nguyên văn toàn bộ đoạn chat Messenger. |
| **M04** | **Tạp chí Luật sư Việt Nam**, *Cảnh báo sinh viên sập bẫy tuyển gia sư online, mắc nợ khoản vay lãi suất cao*, 14/10/2026 ([nguồn](https://lsvn.vn/canh-bao-sinh-vien-sap-bay-tuyen-gia-su-online-mac-no-khoan-vay-lai-suat-cao-a180702.html)) | Báo chí cảnh báo xu hướng (`posting` → `message`) | Xác nhận kịch bản giả danh tuyển gia sư trên hội nhóm Facebook dụ sinh viên cung cấp thông tin ngân hàng, chuyển tiền hoặc thực hiện thao tác đăng ký khoản vay tín dụng lãi cao dù không nhận được tiền công. | Bài cảnh báo theo phản ánh, thiếu trích đoạn hội thoại gốc từng lượt. |
| **M05** | **ĐH Ngoại ngữ – ĐHQGHN (ULIS)**, *Cảnh Báo Các Thủ Đoạn Lừa Đảo Nhắm Vào Sinh Viên*, 18/10/2026 ([nguồn](https://student.ulis.vnu.edu.vn/canh-bao-cac-thu-doan-lua-dao-nham-vao-sinh-vien-nhan-dien-de-tu-bao-ve-minh)) | Cảnh báo chính thức của trường ĐH (`message`) | Ghi nhận 2 chiêu nổi bật nhắm vào sinh viên: (i) yêu cầu **bật chia sẻ màn hình điện thoại** để dẫn dụ vay qua MoMo, Viettel Money, app ngân hàng (có ca SV bị vay & chuyển >71 triệu đồng); (ii) dùng cớ "xác minh danh tính" yêu cầu chụp ảnh cơ thể/nhạy cảm để khống chế. | Chuỗi hay mở đầu bằng mạo danh giao hàng/tài khoản "đăng ký người giao hàng" rồi mới nối sang chia sẻ màn hình & vay/ảnh nhạy cảm; không phải mẫu tin tuyển dụng ngay từ đầu. |
| **M06** | **Hệ thống Tiêm chủng VNVC**, *VNVC cảnh báo chiêu trò giả mạo tuyển dụng để lừa đảo chiếm đoạt tài sản*, 08/10/2026 ([nguồn](https://vnvc.vn/tin-tuc-hoat-dong/canh-bao-gia-mao-tuyen-dung-vnvc)) | Cảnh báo chính thức từ doanh nghiệp bị mạo danh (`posting` & `message`) | Liệt kê 6 thủ đoạn: chuyển khoản/OTP; thu phí xét tuyển/đào tạo/hồ sơ/đồng phục/ký hợp đồng; nhắn tin Facebook/Zalo/Telegram thu CCCD/STK/SĐT; gửi thư trúng tuyển giả; **yêu cầu cài đặt ứng dụng lạ** ("hệ thống tuyển dụng", "ứng dụng đào tạo", "phần mềm chấm công", "ứng dụng nhận việc") hoặc vào Telegram làm nhiệm vụ hoa hồng (được nêu là nhánh phát triển nhanh). | Thông báo phòng ngừa của doanh nghiệp, không công bố tin/chat gốc cụ thể của đối tượng. |
| **M07** | **Báo Sài Gòn Giải Phóng**, *Chiêu trò lừa đảo tuyển cộng tác viên gia công tại nhà*, 05/08/2026 ([nguồn](https://www.sggp.org.vn/chieu-tro-lua-dao-tuyen-cong-tac-vien-gia-cong-tai-nha-post865573.html)) | Tường thuật cảnh báo của Công an xã Vĩnh Lộc, TP.HCM (`posting` → `message`) | Tuyển CTV gia công (xâu vòng, tăm bông, dán phong bì, tranh đính đá) trên hội nhóm MXH để lừa tiền đặt cọc/ký quỹ giữ hàng hoặc dẫn sang làm nhiệm vụ trực tuyến. | Cảnh báo thủ đoạn kèm ảnh minh họa trên bài báo, chưa có bản chép text sạch từ nguồn gốc. |
| **M08** | **Thương hiệu & Công luận**, *Triệt phá đường dây mua bán gần 1.000 tài khoản ngân hàng, dùng phần mềm giả mạo sinh trắc học*, 26/06/2026 ([nguồn](https://thuonghieucongluan.com.vn/triet-pha-duong-day-mua-ban-gan-1-000-tai-khoan-ngan-hang-dung-phan-mem-gia-mao-sinh-trac-hoc-a324134.html)) | Tường thuật vụ án do Công an tỉnh Thanh Hóa triệt phá | Thuê/mua gần 1.000 tài khoản ngân hàng cho đánh bạc/rửa tiền; sử dụng phần mềm can thiệp thiết bị di động dựng video từ **ảnh khuôn mặt chụp sẵn** để vượt lớp xác thực sinh trắc học ngân hàng. | Tin điều tra tóm tắt cơ chế kỹ thuật, không có tin tuyển dụng gốc; bổ sung căn cứ trực tiếp cho rủi ro thu thập ảnh/video khuôn mặt. |
| **M09** | **Bộ Công an**, *Cảnh giác với thủ đoạn "mua bán người" núp bóng tuyển dụng việc làm*, 29/08/2026 ([nguồn](https://bocongan.gov.vn/bai-viet/canh-giac-voi-thu-doan-mua-ban-nguoi-nup-bong-tuyen-dung-viec-lam-1788002885)) | Cảnh báo chính thức mùa cuối năm (`posting` → `message`) | Tuyển "việc nhẹ lương cao, không cần bằng cấp" đưa sang nước ngoài trái phép, dẫn tới đòi giao hộ chiếu/CCCD, đặt cọc hoặc cưỡng bức lao động. | Cảnh báo tổng hợp, không có chat gốc. Tin tuyển "lương cao" đơn lẻ chưa đủ chứng minh cưỡng ép lao động ở giai đoạn đầu. |
| **M10** | **CareerLink**, *Nhận diện lừa đảo tuyển dụng qua deepfake: 9 dấu hiệu cần biết*, 04/08/2026 ([nguồn](https://www.careerlink.vn/cam-nang-viec-lam/goc-ky-nang/nhan-dien-lua-dao-tuyen-dung-qua-deepfake)) | Cẩm nang hướng dẫn từ nền tảng việc làm | Phỏng vấn video call dùng face swap thời gian thực để giả danh HR tập đoàn lớn; nhấn mạnh dấu hiệu chốt vẫn là đòi chuyển tiền, OTP hoặc ảnh CCCD. | Hướng dẫn nhận diện hình ảnh/video; lõi AI đọc văn bản không phát hiện được deepfake nếu hội thoại chưa xuất hiện yêu cầu hành vi rủi ro. |

### 2.2. Nguồn bổ trợ chỉ đọc được snippet hoặc dùng đối chiếu kênh (ghi rõ giới hạn)
- **Nguồn bị lỗi fetch/timeout khi trích xuất (chỉ ghi nhận ở mức snippet tìm kiếm, chưa tính là đã đọc toàn văn):**
  - **Công an tỉnh Đắk Lắk (30/05/2026):** Cảnh báo mua bán, cho thuê thông tin cá nhân (CCCD, SĐT, OTP) để đăng ký tài khoản thanh toán và đặt phòng trực tuyến ([link](https://congan.daklak.gov.vn/tin-moi/canh-bao-thu-doan-mua-ban-cho-thue-thong-tin-ca-nhan-de-dang-ky-tai-khoan-thanh-toan-va-dat-phong-truc-tuyen-phuc-vu-hoat-dong-lua-dao-11824.html)).
  - **Công an tỉnh Quảng Ninh (30/06/2026):** Cảnh báo giả danh doanh nghiệp/cơ quan nhà nước tuyển dụng trên mạng ([link](https://congan.quangninh.gov.vn/tin-antt-va-canh-bao-toi-pham/canh-bao-cac-hinh-thuc-lua-dao-trong-tuyen-dung-xin-viec-lam-51083.html)).
- **Nguồn bổ trợ về kênh mạng xã hội & CTV chốt đơn (snippet 2025–2026):**
  - Các bài cảnh báo của **Luật sư Việt Nam** (14/04/2025, [link](https://lsvn.vn/tiep-tuc-canh-giac-thu-doan-lua-dao-cong-tac-vien-chot-don-hang-online-a156328.html)), **Công an Hải Phòng** (21/05/2025, [link](https://congan.haiphong.gov.vn/Tin-An-ninh-trat-tu/Canh-bao-thu-doan-lua-dao-bang-hinh-thuc-tuyen-cong-tac-vien-xu-ly-don-hang-cho-cac-trang-thuong-mai-dien-tu-171717.html)), **Cổng TTĐT Hà Nội** (25/03/2025, [link](https://hanoi.gov.vn/infographics/canh-bao-thu-doan-lua-dao-lam-cong-tac-vien-chot-don-hang-online-4250325161216631.htm)) và **Gia Lai TV** (11/07/2026, [link](https://gialaitv.vn/vach-tran-manh-khoe-lua-dao-xuyen-quoc-gia-tuyen-cong-tac-vien-chot-don-ao)) cho thấy tin tuyển CTV chốt đơn/tăng tương tác tiếp tục xuất hiện trên **Facebook, TikTok, Zalo, Telegram**, thường gắn với việc cấp link/app mang tên sàn TMĐT và yêu cầu hoàn thành gói nhiệm vụ giá trị tăng dần.

### 2.3. Nhận định tổng hợp cho thiết kế nhãn
1. **Không xuất hiện nhóm hành vi hoàn toàn mới ngoài các trục cốt lõi đã khảo sát**, nhưng năm 2026 nổi bật 3 biến thể diễn đạt cần cập nhật ngay vào quy tắc và từ khóa:
   - **Bẫy vay ẩn dưới thao tác "sửa lỗi nhận lương / chia sẻ màn hình"** nhắm vào sinh viên tìm việc gia sư (`M03`, `M04`, `M05`).
   - **Cài ứng dụng lạ núp bóng "app tuyển dụng / đào tạo / chấm công / nhận việc"** và **bật chia sẻ màn hình điện thoại** (`M05`, `M06`) bên cạnh phần mềm điều khiển máy từ xa truyền thống.
   - **Thu thập ảnh/video khuôn mặt trước phỏng vấn** gắn với nguy cơ vượt xác thực sinh trắc học (`M08`, nối tiếp `S02`/`VTV` ở v2).
2. **Ranh giới thực tế của mô hình đọc văn bản:** Deepfake video (`M10`) và mạo danh logo/tên thương hiệu (`V01`) không thể phân định chỉ bằng văn bản tin đăng. Lõi AI tập trung bắt đúng **hành vi yêu cầu trong văn bản**; phần xác minh danh tính/liên kết giữ ở lớp xác minh ngoài.

---

## 3. Khung 8 nhóm hành vi lõi (`G01`–`G08`) & Bảng ánh xạ từ v2

### 3.1. Bảng ánh xạ đầy đủ từ 18 mã v2 sang khung v3

| Mã lõi (`code`) | `slug` | Tên nhóm hành vi lõi | Ánh xạ từ mã v2 | Hành vi cốt lõi trong phạm vi nhóm |
|---|---|---|---|---|
| **G01** | `upfront_fee` | Phí, cọc hoặc ký quỹ để nhận/giữ việc | `A01`, `A04` | Buộc nộp tiền trước (phí hồ sơ, giữ chỗ, đồng phục, nhận lớp gia sư, phí thực tập định kỳ, cọc vật tư gia công, hoặc ký quỹ/đầu tư tiền thật làm điều kiện qua vòng tuyển). |
| **G02** | `task_advance` | Ứng vốn làm nhiệm vụ hoặc nộp thêm để rút tiền | `A02`, `A03` | Yêu cầu ứng tiền cá nhân thanh toán đơn/nhiệm vụ kèm hứa hoàn gốc + hoa hồng; hoặc đòi nộp thêm khoản riêng (phí giải ngân, thuế, xác minh, sửa lỗi thao tác) mới cho rút số dư đã hứa. |
| **G03** | `loan_or_package` | Ép mua gói hàng hoặc đứng tên vay/tín dụng | `A05`, `A06` | Bắt mua gói sản phẩm/nhập hàng để nhận hoặc giữ vị trí; hoặc yêu cầu/dẫn dụ đứng tên đăng ký khoản vay qua app/tín dụng (kể cả dưới cớ nhận lương/khắc phục lỗi chuyển khoản). |
| **G04** | `credential_ekyc` | Đòi OTP, mật khẩu hoặc dữ liệu sinh trắc học (CCCD + khuôn mặt) | `A07`, `A16` | Đòi mật khẩu, mã OTP (trực tiếp hoặc qua biểu mẫu/link bên tuyển chỉ định); hoặc yêu cầu gửi tổ hợp CCCD và ảnh/video khuôn mặt vào tài khoản cá nhân trước phỏng vấn chính thức. |
| **G05** | `account_mule` | Mở, cho thuê, bàn giao tài khoản hoặc trung chuyển tiền hộ | `A08`, `A09`, `A10` | Lôi kéo mở/xác thực tài khoản ngân hàng/ví cho bên khác dùng, cho thuê/bàn giao quyền truy cập tài khoản đứng tên mình, hoặc nhận tiền bên thứ ba rồi chuyển tiếp theo chỉ dẫn. |
| **G06** | `device_control` | Cài app lạ, bật chia sẻ màn hình hoặc cấp quyền điều khiển thiết bị | `A11` *(mở rộng 2026)* | Yêu cầu tắt bảo vệ/antivirus để cài công cụ, cài app ngoài kho chính thống ("app tuyển dụng/chấm công/đào tạo"), bật chia sẻ màn hình khi thao tác tài chính, hoặc cấp quyền điều khiển từ xa (AnyDesk, UltraViewer, TeamViewer...). |
| **G07** | `coercion_extortion` | Cưỡng ép, giữ giấy tờ, đòi ảnh nhạy cảm hoặc đe dọa tống tiền | `A12`, `A13`, `A14` | Giữ giấy tờ/điện thoại để ràng buộc hoặc ép di chuyển/làm việc; đòi ảnh/video khỏa thân hay mang tính tình dục (kể cả dưới cớ khám sức khỏe/xác minh); hoặc đe dọa phát tán thông tin/hình ảnh riêng tư để ép làm theo. |
| **G08** | `early_task_lure` | Cảnh báo sớm: nhiệm vụ tương tác ảo hoặc lời mời việc online mơ hồ | `C11`, `C12` *(siết tiêu chí)* | Tuyển làm nhiệm vụ tương tác ảo (like, tim, follow, đánh giá sản phẩm/video nhận tiền theo lượt khi chưa có yêu cầu ứng vốn); hoặc tin việc online hội đủ **cả 3 điều kiện siết chặt** (mô tả mơ hồ thiếu đơn vị/cách tính công + hứa thu nhập bất thường/trả liền + kéo sang Zalo/Telegram/link cá nhân). |

### 3.2. Các hạng mục ngoài lõi AI đọc văn bản

| Mã v2 / Hiện tượng 2026 | Hướng xử lý trong v3 | Lý do & nơi lưu trữ |
|---|---|---|
| **`V01` (Mạo danh đơn vị) & Deepfake phỏng vấn (`M10`)** | Ngoài nhãn phân loại văn bản | Cần đối chiếu kênh chính thức của doanh nghiệp hoặc phân tích video/âm thanh; khi hội thoại có hành vi đòi tiền/OTP/app thì gán `G01`–`G07`. Lưu hướng dẫn nhận diện tại tài liệu & kho JSON. |
| **`V02` (Xác minh link/tệp độc hại)** | Ngoài nhãn phân loại văn bản | Chỉ riêng URL hoặc yêu cầu chạy bài test lập trình chưa chứng minh mã độc bằng văn bản; cần bước kiểm tra kỹ thuật riêng. |
| **`A15` (Ép ứng viên nói sai với người thứ ba)** | Đưa vào mục tham khảo / mở rộng tương lai | Có **0 mẫu** trong toàn bộ `data/v2` (715 mẫu), thiếu hội thoại gốc công khai để dựng Val/Test độc lập và dễ chồng lấn với kịch bản tư vấn bán hàng bình thường. Ghi nhận lại trong danh mục theo dõi nếu mở rộng ở v4. |

### 3.3. Tách lớp giữa Lõi AI và Kho kịch bản JSON
- **Lõi AI (`G01`–`G08`):** Chỉ chịu trách nhiệm nhận diện đúng nhóm hành vi lõi và trỏ chính xác ID câu bằng chứng (`evidence_sentence_ids`).
- **Kho kịch bản [RecruitmentScenarios.json](../../backend/JobShield.Infrastructure/RecruitmentScenarios.json) (cập nhật ở Phần 4):** Lưu phần giải thích chi tiết theo từng phân nhánh bên dưới mỗi nhóm `G01`–`G08` (ví dụ trong `G01` phân biệt phí nhận lớp gia sư, cọc vật tư gia công và ký quỹ vòng tuyển; trong `G02` nối chuỗi leo thang từ `G08 → G02`), kèm vụ việc tham chiếu có URL nguồn kiểm chứng (`M01`–`M10`, `S01`–`S14`, `N01`–`N05`) và `possibleNextSteps`.

---

## 4. Kế hoạch thu dữ liệu & cân bằng âm khó cho Phần 2

### 4.1. Nguồn kế thừa từ v2 và khoảng thiếu cần bù

| Nhóm | Số mẫu v2 ánh xạ được *(Train / Val / Test)* | Nguồn thật ưu tiên cho Val & Test (100% nguồn thật độc lập) | Phương án Train (mục tiêu ≥ 40–60 mẫu/nhóm) | Mẫu âm khó (Hard Negatives) ưu tiên cho nhóm |
|---|---:|---|---|---|
| **G01** | 42 / 19 / 10 | Tin gia sư thu phí, thực tập thu phí, cọc gia công tại nhà (SGGP/FB chụp nguyên tin), hồ sơ sơ tuyển ký quỹ giả | Kế thừa 42 mẫu `A01` + bổ sung biến thể cọc vật tư, phí giữ ca, ký quỹ vòng test (`A04`) | Lệ phí thi viên chức chính thức (`S11`), khóa học tự chọn không ép việc, tin ghi rõ "không thu phí/miễn cọc", phụ cấp do công ty ứng |
| **G02** | 64 / 2 / 5 | Hội thoại nhiều lượt ứng tiền thanh toán đơn và đoạn đòi phí giải ngân/thuế/sửa lỗi rút tiền từ báo chí, VOZ, cộng đồng chống lừa đảo | Kế thừa 64 `A02` + bổ sung đủ biến thể đòi nộp thêm rút tiền (`A03` cũ) ở `message` | JD vận hành sàn TMĐT / xử lý đơn hàng thật có lương cứng & KPI; hoa hồng bán hàng hợp pháp không phải ứng tiền cá nhân |
| **G03** | 0 / 0 / 0 | Vụ ép vay gia sư (Báo Lào Cai/LSVN), vụ sinh viên mua gói 11 triệu (Thanh Niên), vụ vay app thế chân (Nhân Dân) | Tự thu trích đoạn thật + mẫu mô phỏng bám sát `M03`, `M04`, `S05`, `S06` (đánh dấu `simulated_from_real`) | Chương trình vay ưu đãi sinh viên của ngân hàng/ĐH (`M` tra cứu ngân hàng), ưu đãi nhân viên tự nguyện, JD tư vấn tín dụng |
| **G04** | 7 / 0 / 0 | Tin/hội thoại đòi OTP, biểu mẫu đòi mật khẩu nhận lương (VTV), yêu cầu gửi CCCD + video mặt trước phỏng vấn | Kế thừa 7 `A07` + thu mới + mô phỏng bám vụ VTV & thu sinh trắc học (`M08`) | Yêu cầu gửi CV, STK nhận lương sau trúng tuyển, ảnh 3×4 làm thẻ, câu nhắc cảnh giác "không chia sẻ OTP" |
| **G05** | 1 / 0 / 0 | Tin rao thuê/mua tài khoản ngân hàng trên MXH/SMS, vụ lôi kéo mở tài khoản nhận chuyển tiền (`S04`, `S13`, `M08`) | Kế thừa 1 `A09` + trích đoạn thật từ bài rao thuê TK + mô phỏng bám hồ sơ điều tra | Hướng dẫn mở tài khoản trả lương đứng tên mình (tự giữ quyền dùng), JD kế toán/thu ngân xử lý giao dịch của công ty |
| **G06** | 0 / 0 / 0 | Cảnh báo cài app chấm công/tuyển dụng (`M06`), chia sẻ màn hình vay app (`M05`), bài test lập trình/RMM (`S08`, `S10`) | Trích đoạn thật (`posting` & `message`) + mô phỏng bám `M05`, `M06`, `S08`, `S10` | Phỏng vấn qua Zoom/Teams/Google Meet, cài Git/VS Code làm test dev bình thường, chia sẻ màn hình trình bày slide/code |
| **G07** | 0 / 0 / 0 | Trích đoạn lời kể/tin nhắn giữ CCCD/ép đi làm (`S12`, `M09`), khám sức khỏe đòi ảnh nhạy cảm/tống tiền (`S07`, `M05`) | Trích đoạn thật đủ căn cứ trực tiếp + mô phỏng bám `S07`, `S12`, `M05`, `M09` | Tin tuyển việc tỉnh khác có xe đón/chỗ ở hợp pháp, yêu cầu mang CCCD đối chiếu phỏng vấn, tuyển mẫu ảnh thời trang minh bạch |
| **G08** | 130 / 2 / 1 *(+1 ở holdout)* | Tin tuyển like/follow trả tiền và tin CTV chốt đơn/online mơ hồ từ tập nguồn thật mới | Kế thừa chọn lọc `C11`/`C12` sau khi rà lại đúng tiêu chí siết chặt ở Codebook v3 | JD Social Media Marketing đo lượt thích/tương tác; tin part-time/CTV bán hàng thật ghi rõ đầu việc, đơn giá và tên cửa hàng (dù có Zalo HR) |

### 4.2. Chỉ tiêu tổng thể chuyển tiếp sang Phần 2
- **Tổng quy mô mục tiêu:** ~1.000–1.400 mẫu, chuẩn hóa `input.type` chỉ gồm `posting` hoặc `message`.
- **Tập Train:** Nguồn thật + mẫu mô phỏng bám vụ việc (đạt ≥ 40–60 mẫu/nhóm cho đủ 8 nhóm `G01`–`G08`) + **250–350 mẫu âm khó** cân bằng giữa `posting` và `message`.
- **Tập Validation & Test:** **100% nguồn thật độc lập** (~60–80 mẫu mỗi tập), giữ tập con 30 mẫu `test` v2 cũ để đối chiếu trực tiếp trước/sau nâng cấp; không trùng `split_group_id` hay văn bản chuẩn hóa giữa các tập.
