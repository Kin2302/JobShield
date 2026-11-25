# Khảo sát cơ chế tuyển dụng để rà soát JobShield

Khảo sát ban đầu ngày 14/11/2026. Lượt đối chiếu các quy tắc đã duyệt ngày 20/11/2026 ở ngay dưới đây.

## Kiểm tra độ phủ trên các tình huống thực tế · 20/11/2026

**Kết quả.** Chín nhóm đang dùng giải thích được nhiều yêu cầu cụ thể, từ nộp tiền nhận lớp tới giao quyền sử dụng tài khoản và giữ giấy tờ để ngăn người lao động rời đi. Vẫn có những hành vi quan sát được mà chín nhóm chưa gọi tên, tiêu biểu là yêu cầu ứng viên nói sai sự thật với người thứ ba. Một số rủi ro khác chỉ lộ ra khi ứng viên đến gặp trực tiếp hoặc khi sản phẩm thử tuyển đã được sử dụng. Độ phủ của quy tắc và khả năng phát hiện từ một tin đăng là hai câu hỏi riêng.

### Phạm vi và cách đọc

Mốc đối chiếu là các **quy tắc mới được duyệt trong chat**, chưa ghi thành phiên bản codebook chính thức. Nhóm 10 về mạo danh được hoãn cho chức năng xác minh. Hai nhãn của sản phẩm vẫn là “có dấu hiệu đáng ngờ” và “chưa phát hiện dấu hiệu đáng ngờ”. Trường hợp chưa rõ chuyển người phụ trách dataset duyệt.

Lượt tìm bao gồm gia sư, dịch thuật và bán hàng part-time, thực tập, tuyển lập trình viên và việc đầu tiên sau tốt nghiệp tại Việt Nam. Truy vấn gồm cả mô tả trung tính như phí nhận lớp, đề bài thử tuyển và công việc chăm sóc khách hàng. Đã đọc nguồn tự đăng công khai trên Reddit và VOZ, bài chia sẻ lại trên LinkedIn, thông báo do trường/doanh nghiệp phát hành, lời kể do báo phỏng vấn và thông tin cơ quan tiếp nhận vụ việc. Với Facebook, có bài báo chụp tin tuyển hoặc phỏng vấn người đã liên hệ qua nền tảng. Lượt này chưa đọc trực tiếp được tập bài Facebook/Threads đủ dùng để đánh giá riêng từng nền tảng. Bài gia đình kể về khoản vay do người dùng nêu trong chat được loại khỏi tư liệu.

Các dòng dưới đây so sánh **cơ chế và thời điểm**, không dùng làm mẫu số để tính tỷ lệ bao phủ. Chủ đề VOZ đã có trong kho được ghi là đối chiếu lại. Thông báo chung, lời kể đã đăng lại và nhiều nguồn về cùng vụ không được tính thành các vụ độc lập. Chưa chạy mô hình trên các nguồn này.

### Đối chiếu từng nhóm

| Nhóm | Tình huống và thời điểm có thể phát hiện | Kết quả đối chiếu |
|---|---|---|
| 1. Thu tiền trước | Tin tìm gia sư ghi hai buổi/tuần. Khi trao đổi, trung gian yêu cầu sinh viên chuyển 600.000 đồng mới giao lớp. Một sinh viên tự thuật trên Reddit cũng được đòi phí kích hoạt sau khi hỏi việc dịch thuật. [Sinh Viên Việt Nam – Tiền Phong](https://tienphong.vn/post-1603612.tpo) · [Bài tự thuật](https://www.reddit.com/r/vozforums/comments/1h4y1px/) | **Đã phủ** từ bước có điều kiện thu tiền. Đối chứng là chính sách của một bên môi giới công khai phương án thanh toán sau khi nhận lớp và thống nhất lịch. Cùng tên “phí nhận lớp” nhưng thời điểm khác. [Nội quy nhận lớp](https://daykemsupham.edu.vn/index.php/noiquynhanlop/) |
| 2. Ứng tiền làm nhiệm vụ | Trong một bài tự thuật, sau phần khảo sát có nhận tiền, người tìm việc bị yêu cầu chuyển tiền để tiếp tục rồi vay tiền khi không đáp ứng được khoản lớn. [Lời kể trên Reddit, 2023](https://www.reddit.com/r/vozforums/comments/17wg10i/) | **Đã phủ khi có yêu cầu dùng tiền cá nhân** và quan hệ với khoản được hứa trả. Đoạn chỉ xuất hiện lời mời làm nhiệm vụ tương tác trả tiền theo lượt là ranh giới riêng cần giữ từ trao đổi trước. Trong mẫu JS-SUP03-13 chưa xuất hiện yêu cầu ứng vốn. [Đầu vào đã lưu](../../../datasets/raw/jobshield-v03-initial/supplement-03/inputs.jsonl) |
| 3. Ký quỹ hoặc đầu tư để qua vòng tuyển | Vietcombank mô tả bài đánh giá về chứng chỉ quỹ dẫn tới bước yêu cầu ký quỹ. Một ứng viên trên VOZ kể đã trải qua vòng hỏi đáp trước khi phải chuyển tiền thật. [Thông báo của ngân hàng](https://www.vietcombank.com.vn/vi-VN/Trang-thong-tin-dien-tu/Articles/2026/09/16/20260914_MKTTT_Canh-bao-lua-dao-mao-danh-tuyen-dung-VCB) · [VOZ, chủ đề đã có trong kho](https://voz.vn/t/canh-bao-lua-dao-cu-nga-dau-cua-ke-that-nghiep.1196110/) | **Đã phủ** ở bước dùng tiền thật để qua vòng tuyển. Việc có phỏng vấn trên Teams, có bài khảo sát hoặc có sản phẩm tài chính trong đề chưa đủ để gán. |
| 4. Buộc mua gói hoặc vay | Phóng viên ghi nhận việc mua gói hàng để vào làm sau lời tuyển bán hàng. Trong một bài Reddit về việc bán cà phê, người kể được mời mua đồ uống và được giới thiệu thêm vị trí khác. [Thanh Niên](https://thanhnien.vn/da-cap-lua-dao-o-tphcm-cam-bay-sinh-vien-mua-nhap-hoc-185250907073814014.htm) · [Lời kể về buổi phỏng vấn](https://www.reddit.com/r/vozforums/comments/1rdao4v/) | **Đã phủ** nếu mua là điều kiện nhận hoặc giữ việc. Với lời mời mua đồ uống, chưa có chi tiết xác nhận tính bắt buộc. Cần ghi riêng việc mô tả công việc thay đổi. |
| 5. Dữ liệu và quyền đăng nhập | VTV ghi nhận phản ánh về tuyển CTV truyền thông. Sau khi ứng tuyển, có yêu cầu cung cấp nhiều ảnh mặt hoặc video khuôn mặt. Bài không xác nhận tất cả người nhận đều bị yêu cầu gửi kèm CCCD hay phát sinh thiệt hại. [VTV, 25/05/2026](https://vtv.vn/gia-tuyen-dung-bao-chi-de-thu-thap-du-lieu-khuon-mat-100260525103950021.htm) | **Đúng nhóm, ngưỡng còn hẹp.** Quy tắc OTP/mật khẩu hoặc tổ hợp CCCD + video + tài khoản cá nhân trước phỏng vấn không bao quát hết yêu cầu thu ảnh. Khi soạn quy tắc cần phân biệt ảnh chân dung/đoạn thử hình phù hợp với vị trí và yêu cầu định danh theo chỉ dẫn bất thường. Hiện các ca thiếu căn cứ vẫn chờ rà. |
| 6. Dùng tài khoản của ứng viên | Bộ Công an thuật lại vụ người tìm việc đăng ký tài khoản, giao quyền sử dụng và thông tin xác thực. [Thông tin vụ điều tra, 18/10/2026](https://www.mps.gov.vn/bai-viet/canh-giac-voi-chieu-tro-tuyen-dung-viec-nhe-luong-cao-de-thue-muon-tai-khoan-ngan-hang-1792292719) | **Đã phủ** khi có yêu cầu giao quyền dùng tài khoản hoặc dùng tài khoản cá nhân nhận và chuyển tiền hộ. Cho số tài khoản nhận lương chỉ xác định đích nhận tiền. |
| 7. Thiết bị và bài tuyển dụng | Nghiên cứu kỹ thuật ghi nhận ứng viên được yêu cầu chạy bài thực hành có chứa thành phần độc hại. Một lập trình viên tự thuật bằng tiếng Việt về bài test đáng ngờ mình đã dừng lại. [Microsoft, nghiên cứu quốc tế](https://www.microsoft.com/en-us/security/blog/2026/03/11/contagious-interview-malware-delivered-through-fake-developer-job-interviews/) · [Bài gốc trên Viblo](https://viblo.asia/p/suyt-bay-sach-data-vi-nhan-coding-test-luong-120hr-canh-bao-lua-dao-tuyen-dung-linkedin-13VM99vQVY7) | **Đúng nhóm, thiếu căn cứ ở tin đầu** nếu người tuyển chỉ yêu cầu chạy bài. Hai điều kiện đã duyệt là tắt bảo vệ và cấp quyền điều khiển từ xa. Kết quả phân tích kỹ thuật ở vụ khác không xác minh được tệp của người viết trên Viblo. |
| 8. Ảnh nhạy cảm và đe dọa | Tin tuyển công nhân nữ chuyển thành yêu cầu ảnh khỏa thân dưới lý do khám sức khỏe, sau đó mới có lời đe dọa. [Nguồn tường thuật lời trình báo](https://khoahocdoisong.vn/lua-dao-kham-suc-khoe-tuyen-dung-de-lay-anh-nhay-cam-khong-che-nan-nhan-post2148569086.html) | **Đã phủ** từ lúc xuất hiện yêu cầu gửi ảnh. Đe dọa là hành vi thứ hai. Nguồn từ 2024 giúp thử quy tắc nhưng chưa cho biết mức độ phổ biến năm 2026. |
| 9. Hạn chế tự do | Một thiếu niên tìm việc trên Facebook, được hứa việc nhẹ. Khi tới Hà Nội, em bị yêu cầu ký giấy không được đọc, bị giữ căn cước và điện thoại, không thể liên lạc hay tự rời xưởng. Công an cho biết đã tìm được em. [Bộ Công an, 03/07/2026](https://www.bocongan.gov.vn/bai-viet/phu-tho-kip-thoi-giai-cuu-nam-thanh-nien-nghi-bi-lua-dao-tuyen-dung-viec-nhe-luong-cao-qua-mang-xa-hoi-1783045468) | **Đã phủ ở giai đoạn bị kiểm soát.** Tin tuyển đầu chưa đủ. Nếu ứng viên thuật lại yêu cầu ký giấy không được đọc, có thể lưu đó là dấu hiệu cần rà riêng. Chưa biết nội dung giấy và chưa có căn cứ quy thành khoản vay. Đây là ví dụ về cơ chế, nhân vật không được xác nhận là sinh viên. |
| 10. Mạo danh | Trường ĐH Cần Thơ cảnh báo hình thức giả danh doanh nghiệp tuyển thực tập rồi thu các loại phí. Trên mẫu chỉ có chỉ dẫn nộp cọc, người đọc đã có thể xét nhóm 1 trước khi có kết quả xác minh danh tính. [Cảnh báo của trường](https://dpa.ctu.edu.vn/co-quan-an-toan/63-thong-tin-canh-giac.html) | **Hoãn theo phạm vi đã duyệt.** Lưu nguồn xác minh bên ngoài riêng. Chưa đưa mạo danh thành nhãn cho lõi AI chỉ đọc văn bản. |

**Một chỉnh sửa có căn cứ trực tiếp cho nhóm 5.** Trong vụ gia sư được VTV phỏng vấn, bên liên hệ xin số tài khoản với lý do hỗ trợ tiền đi lại, gửi ảnh chuyển tiền, rồi chỉ sang biểu mẫu nhận tiền yêu cầu tài khoản, mật khẩu và mã xác nhận. Đến khi biểu mẫu đòi bí mật đăng nhập, có thể mô tả chính xác điều ứng viên bị yêu cầu làm. Nên ghi rõ “giao bí mật qua biểu mẫu do bên tuyển chỉ định để nhận tiền” bên cạnh trường hợp đọc mật khẩu cho người tuyển. Phải có nội dung yêu cầu trên biểu mẫu hoặc lời thuật tương ứng trong đầu vào. Ca này là một nguồn VTV độc lập với ví dụ người dùng chia sẻ. [VTV, 22/06/2026](https://vtv.vn/bay-viec-lam-mua-he-gia-phu-huynh-thue-gia-su-lua-chiem-doat-hang-chuc-trieu-dong-100260622000817872.htm)

**Đối chứng về nền tảng.** Một freelancer kể với ZNews rằng mình nhận được dự án sáng tạo nội dung sau khi phỏng vấn qua một cơ hội trên Threads. Trong một cơ hội khác trên cùng nền tảng, người liên hệ yêu cầu nạp tiền để kích hoạt tài khoản làm việc. Nhóm 1 giải thích được khác biệt khi xét tới bước thu phí. Tên nền tảng và việc chuyển sang ứng dụng nhắn tin chưa đủ để phân hai trường hợp. [Phỏng vấn của ZNews, 02/03/2024](https://lifestyle.znews.vn/gen-z-gap-cu-lua-khi-tim-viec-tren-threads-post1462773.html)

### Những tình huống cần người phụ trách quyết định

| Vấn đề | Bằng chứng và mốc xuất hiện | Đề xuất cho bản codebook mới |
|---|---|---|
| Yêu cầu ứng viên đánh lừa người thứ ba | Một gia sư kể trung tâm hướng dẫn khai sai trường đang học với phụ huynh. Trong bối cảnh việc đầu tiên sau tốt nghiệp, một người được tuyển chăm sóc khách hàng kể về việc mời khách nhận voucher rồi hướng họ tới buổi giới thiệu đất. Độ rõ của trường hợp gia sư cao hơn vì người kể chỉ đích danh lời khai sai. [Dân trí, 16/12/2025](https://dantri.com.vn/giao-duc/sinh-vien-sap-bay-trung-tam-gia-su-cay-dang-mat-ca-thang-tien-tro-20251215234604338.htm) · [Quân đội nhân dân, 21/09/2026, đối chiếu qua bản được lập chỉ mục do trang gốc chuyển hướng](https://www.qdnd.vn/xa-hoi/cac-van-de/tu-nguoi-tim-viec-den-mat-xich-lua-dao-1057713) | **Ưu tiên thử một quy tắc mới** khi bên tuyển trực tiếp yêu cầu ứng viên nói sai một thông tin cụ thể với khách, phụ huynh hay người thứ ba. Phân biệt với việc nhân viên tư vấn mời khách hoặc nhà tuyển dụng tự mạo danh. Khả năng áp dụng mạnh nhất ở bước hướng dẫn công việc. |
| Thu tiền thực tập theo tháng | Tin tuyển thực tập AI đăng trên fanpage, được báo đăng lại kèm hình, nêu mức thu 3 triệu đồng/tháng và trường hợp miễn. Chưa rõ thời điểm thu lần đầu. Để đối chiếu, thông báo tuyển thực tập khác do ĐH Cần Thơ công bố ghi doanh nghiệp hỗ trợ sinh viên được chọn. [Bài có hình tin tuyển, 11/06/2025](https://tuoitre.vn/nld/tranh-cai-viec-cong-ty-tuyen-thuc-tap-sinh-khong-luong-con-thu-3-trieu-dong-thang-196250611091155779.htm) · [Thông báo tuyển thực tập, 06/08/2025](https://dsa.ctu.edu.vn/images/upload/vbanply/2025/Tuyendung/06-8-2025_Thong_bao_tuyen_chon_Thuc_tap_sinh_2025signed.pdf) | **Làm rõ nhóm 1.** Người duyệt quyết định có cảnh báo việc phải trả phí để tiếp tục thực tập khi chưa rõ ngày thu. Học phí đào tạo công khai, khoản hỗ trợ sinh viên và phí bắt buộc để có vị trí cần ví dụ riêng. |
| Khai thác bài làm thử | Nữ sinh năm hai kể đã nộp bài viết thử, nhận thông báo không đạt và sau đó thấy nội dung trên website. Một bài chia sẻ lại trên LinkedIn năm 2025 mô tả ứng viên từ chối làm kế hoạch quý dựa trên số liệu cửa hàng. Thảo luận trên VOZ cho thấy người đọc cũng có thể nghi ngờ chỉ vì đề dài. [Nhân Dân, 01/07/2022](https://nhandan.vn/can-trong-chieu-lua-tuyen-cong-tac-vien-post703461.html) · [Bài chia sẻ lại trên LinkedIn](https://vn.linkedin.com/posts/meet-evan93_c%C3%A2u-chuy%E1%BB%87n-mu%C3%B4n-th%C6%B0%E1%BB%9Fu-brand-m%C6%B0%E1%BB%A3n-danh-tuy%E1%BB%83n-activity-7337688533773504513-20_G) · [Thảo luận VOZ](https://voz.vn/t/cong-ty-cho-lam-test-nhieu-la-sai.897968/) | **Ngoài chín nhóm, còn thiếu căn cứ cảnh báo sớm.** Giữ phân biệt giữa giao bài, nộp bài và sử dụng sản phẩm. Cần đối chiếu bài gốc với bản xuất bản và thỏa thuận sử dụng. |
| Lấy tài sản vật lý tại buổi phỏng vấn | Báo Công an TP.HCM thuật lại việc người mới tốt nghiệp đi phỏng vấn, được một người tự xưng bảo vệ đề nghị giao xe để giữ, rồi mất xe. [Báo Công an TP.HCM, 12/11/2022](https://congan.com.vn/vu-an/canh-giac/cu-lua-ngoan-muc-cua-ga-bao-ve_139730.html) | **Ngoài chín nhóm.** Rủi ro liên quan đến việc giao tài sản tại hiện trường. Chưa có căn cứ để kết luận từ lời mời phỏng vấn, hay gán cho mọi yêu cầu gửi xe. Cần thêm vụ gần đây trước khi ưu tiên thành nhóm độc lập. |

**Thứ tự đề nghị.** Trước hết, thử quy tắc về yêu cầu nói sai với người thứ ba bằng các cặp tình huống rõ và dễ nhầm. Đồng thời, bổ sung ví dụ biên cho nhóm 1, 5 và 7. Quy tắc đã bàn trước đó về làm nhiệm vụ tương tác trả tiền theo lượt cần có vị trí riêng khi soạn bản mới để tránh ép vào nhóm 2 khi ứng viên chưa phải ứng tiền. Các trường hợp thu phí theo tháng, giao tài sản và bài làm bị dùng lại tiếp tục chờ người phụ trách quyết định. Không suy tỷ lệ phát hiện, tần suất thị trường hay hiệu năng của AI từ khảo sát này.

**Ranh giới sau tuyển dụng.** Sinh viên làm part-time tại cùng một chuỗi cà phê phản ánh ban đầu có nhận lương, về sau bị trả chậm hoặc chia nhỏ. Nguồn cho biết điều xảy ra trong quá trình làm việc. Chưa có bằng chứng về ý đồ gian dối trong tin tuyển đầu tiên. Nếu sau này mở rộng JobShield sang vi phạm quyền lợi lao động, nên xác định phạm vi và bằng chứng riêng cho trường hợp này. [Thanh Niên, 23/08/2024](https://thanhnien.vn/nhieu-sinh-vien-di-lam-them-ban-phe-o-tphcm-miet-mai-doi-luong-tui-em-phai-muon-tien-de-song-185240822172059467.htm)

## Khảo sát nền ngày 14/11/2026

Báo cáo này tổng hợp chọn lọc 14 nguồn để hỗ trợ xem xét CODEBOOK v0.3-DRAFT. Đây không phải tổng
quan hệ thống hay phép đo độ bao phủ thị trường. Nguồn cảnh báo, lời kể và bài báo không tự trở
thành hội thoại tuyển dụng dùng làm dữ liệu.

## Phạm vi và cách đọc

Khảo sát chọn nguồn theo ba hướng thu thập:

1. Cảnh báo/hướng dẫn từ cơ quan chức năng, tổ chức bị mạo danh và nền tảng tuyển dụng: S01–S04, S12–S14. S01 là hướng dẫn trực tiếp của nền tảng TopCV, không phải nguồn điều tra.
2. Tường thuật/điều tra có lời kể hoặc quan sát: S05–S07. Mức độ xác minh khác nhau; bài viết có thể trích cảnh báo cơ quan chức năng mà không kèm hồ sơ vụ việc.
3. Bài đăng cá nhân và nghiên cứu kỹ thuật: S08–S10. S08 là nghiên cứu chiến dịch quốc tế; không xác minh các ca riêng tại Việt Nam.

S11 là nguồn đối chứng về tuyển dụng chính thức có lệ phí. Mỗi mục ghi ngày đăng, ngày diễn biến khi
nguồn nêu, cấp bằng chứng, thông tin sinh viên và loại tư liệu gốc được công bố. “Có ảnh/tài liệu”
không đồng nghĩa có chuỗi chat đủ lượt và người nói. Nhận xét về chat gốc dựa trên phần văn bản đã
đọc; ảnh chụp chưa được tách lượt hoặc xác minh độc lập. Khảo sát này chưa thu được bộ hội thoại
gốc có đủ ngữ cảnh và điều kiện sử dụng để chuyển sang dataset.

Nguồn được mở toàn văn. Nguồn tư liệu xã hội ở đây là S09 (VOZ) và S10 (Viblo); không rà trực tiếp
các bài tuyển trên Facebook, TikTok hay Instagram, và không có căn cứ để nhận định mức độ bao phủ
các nền tảng đó. Trích xuất, quyền sử dụng, khử định danh, đối chiếu vụ trùng và gán nhãn dữ liệu
chưa được thực hiện.

## Danh mục nguồn

### Cảnh báo, hướng dẫn và thông tin cơ quan chức năng

**S01. TopCV, “Tìm việc an toàn cùng TopCV”.** [Nguồn](https://www.topcv.vn/tim-viec-an-toan), cập
nhật 10/2026; không nêu ngày vụ cụ thể. Trang TopCV tổng hợp các dấu hiệu về phí/đặt cọc, thu thập
dữ liệu cá nhân, nhiệm vụ trực tuyến, mạo danh, AI giả hình/giọng và tuyển việc nước ngoài. **Bằng chứng:** hướng dẫn
của nền tảng, không phải điều tra vụ riêng. Không xác nhận nạn nhân là sinh viên. Không có chat gốc;
có các thẻ hướng dẫn/minh họa.

**S02. ĐHQG Hà Nội, “Cảnh báo mạo danh ĐHQGHN để lừa đảo tuyển dụng”.**
[Nguồn](https://vnu.edu.vn/canh-bao-mao-danh-dhqghn-de-lua-dao-tuyen-dung-post38972.html),
25/12/2025; diễn biến “những ngày gần đây”. ĐHQGHN nói đã nhận phản ánh sinh viên về tài khoản
Instagram giả, sơ tuyển Zoom, biểu mẫu/link và tài khoản dự án; có dấu hiệu đòi phí hỗ trợ. **Bằng
chứng:** thông tin của đơn vị bị mạo danh, có phản ánh sinh viên nhưng không nêu ca cụ thể. Có ảnh
tài khoản/tin, không có chat đầy đủ. Sinh viên được xác nhận ở cấp phản ánh.

**S03. Vietcombank, “Cảnh báo thủ đoạn lừa đảo mạo danh Vietcombank tuyển dụng dự án an sinh xã
hội”.**
[Nguồn](https://www.vietcombank.com.vn/vi-VN/Trang-thong-tin-dien-tu/Articles/2025/08/20/20250819_NMH_Canh-bao-lua-dao-VCBxVietlott),
20/08/2025; không định ngày từng ca. Ngân hàng nêu mạo danh Vietcombank/Vietlott và dự án an sinh,
dùng quy trình tuyển giả; các dạng đã cảnh báo gồm phí, app/link, nhóm nhắn tin và nhiệm vụ hoa
hồng. **Bằng chứng:** cảnh báo của tổ chức bị mạo danh; không nêu nạn nhân cụ thể. Không xác nhận
sinh viên. Có ảnh/tài liệu minh họa, không có chat trọn vẹn.

**S04. Bộ Công an, “Cảnh báo thủ đoạn lôi kéo học sinh, sinh viên mở tài khoản ngân hàng tiếp tay
cho tội phạm”.**
[Nguồn](https://www.mps.gov.vn/bai-viet/hai-phong-canh-bao-thu-doan-loi-keo-hoc-sinh-sinh-vien-mo-tai-khoan-ngan-hang-tiep-tay-cho-toi-pham-1773113453),
10/03/2026; không nêu ngày ca riêng. Mô tả tin “việc nhẹ”, thuê tài khoản/nhận tiền hộ, sau đó yêu
cầu giao thẻ, thông tin đăng nhập, OTP hoặc SIM. **Bằng chứng:** cảnh báo chung của Bộ Công an,
không có hồ sơ vụ hay sinh viên cụ thể. Không có chat gốc; ảnh minh họa. Không dùng riêng nguồn này
để gán hành vi cho một người.

**S12. Bộ Công an, “Cảnh giác với ‘bẫy’ việc nhẹ lương cao”.**
[Nguồn](https://www.bocongan.gov.vn/bai-viet/cong-an-tinh-vinh-long-canh-giac-voi-bay-viec-nhe-luong-cao-1780907526),
08/06/2026; lời kể về tìm việc ngày 08/04/2025, bàn giao ba công dân giữa tháng 5/2026. Người lao
động nói được hứa lương/chỗ ở rồi bị đưa sang Campuchia; công an tiếp nhận sau khi phía Campuchia
trục xuất. **Bằng chứng:** thông tin cơ quan chức năng, có lời kể người trong cuộc và mốc bàn giao.
Không xác nhận họ là sinh viên. Không công bố chat gốc.

**S13. Bộ Công an, “Cảnh giác với chiêu trò tuyển dụng ‘việc nhẹ, lương cao’ để thuê, mượn tài khoản
ngân hàng”.**
[Nguồn](https://www.mps.gov.vn/bai-viet/canh-giac-voi-chieu-tro-tuyen-dung-viec-nhe-luong-cao-de-thue-muon-tai-khoan-ngan-hang-1792292719),
18/10/2026; sự việc bắt đầu khoảng giữa 2025, khởi tố được nêu ngày 16/10/2026. Bài thuật lại hai
người tìm việc qua mạng, sang Campuchia chuyển tiền, đăng ký tài khoản ngân hàng và giao đăng
nhập/OTP. **Bằng chứng:** thông tin điều tra, chưa phải phán quyết cuối cùng. Không xác nhận sinh
viên; không công bố chat gốc. Cùng chủ đề với S04 nhưng có vụ cụ thể.

**S14. NCSC đăng trên cổng Bộ KH&CN, “Cảnh giác với thủ đoạn lừa đảo tuyển cộng tác viên cho sàn
thương mại điện tử”.**
[Nguồn](https://mst.gov.vn/canh-giac-voi-thu-doan-lua-dao-tuyen-cong-tac-vien-cho-san-thuong-mai-dien-tu-197153805.htm),
05/06/2022; không nêu ngày ca riêng. NCSC tổng hợp phản ánh tuyển CTV xử lý đơn, yêu cầu trả tiền
hàng trước, ban đầu hoàn vốn/hoa hồng rồi tăng giá trị nhiệm vụ. **Bằng chứng:** cảnh báo tổng hợp,
không phải điều tra từng ca. Không xác nhận sinh viên. Không có chat gốc. Mô tả này không chứng minh
A02/A03/C04 trong một hội thoại cụ thể.

### Điều tra, tường thuật và lời kể người bị ảnh hưởng

**S05. Nhân Dân, “Sập bẫy mô hình lừa đảo: Người lao động lao đao (kỳ 1)”.**
[Nguồn](https://nhandan.vn/sap-bay-mo-hinh-lua-dao-nguoi-lao-dong-lao-dao-ky-1-post998767.html),
29/10/2026; nhân vật bắt đầu tìm việc cuối 06/2026, bài thuật khoảng ba tháng làm. Có ảnh tờ tuyển
350.000 đồng/ngày và lời kể của lao động 19 tuổi về vay qua ứng dụng, nộp tiền thế chân/mua hàng,
tham gia câu lạc bộ, nợ trên 200 triệu đồng và tuyển người mới. **Bằng chứng:** phóng viên điều tra,
ảnh tờ tuyển, lời kể trực tiếp. Người 19 tuổi, không xác nhận là sinh viên. Không có chat gốc.

**S06. Thanh Niên, “Đa cấp lừa đảo ở TP.HCM: Cạm bẫy sinh viên mùa nhập học”.**
[Nguồn](https://thanhnien.vn/da-cap-lua-dao-o-tphcm-cam-bay-sinh-vien-mua-nhap-hoc-185250907073814014.htm),
13/09/2025; lịch phỏng vấn nhân vật là 11/08/2025. Bài mô tả tuyển bán hàng rồi chuyển thành tư vấn,
buổi “làm giàu”, yêu cầu giữ kín và khoản 11 triệu đồng mua hàng để được nhận chính thức. Phóng viên
xuất hiện tại lần thu tiền, ghi nhận giấy mua hàng viết tay và lời đối thoại. **Bằng chứng:** tường
thuật/quan sát trực tiếp một phần diễn biến. Nhân vật là sinh viên. Không đăng chat gốc.

**S07. Khoa học & Đời sống, “Lừa đảo khám sức khỏe tuyển dụng để lấy ảnh nhạy cảm khống chế nạn nhân”.** [Nguồn](https://khoahocdoisong.vn/lua-dao-kham-suc-khoe-tuyen-dung-de-lay-anh-nhay-cam-khong-che-nan-nhan-post2148569086.html), 20/10/2024; người trình báo thấy tin tuyển hơn bốn tháng trước. Bài dẫn cảnh báo Quảng Ngãi và lời trình báo của chị T: tuyển công nhân nữ, yêu cầu CCCD, ảnh mặt và khỏa thân; sau đó đe dọa đăng tải nếu không làm theo. **Bằng chứng:** cảnh báo công an được báo chí thuật, lời trình báo và ảnh tin do nạn nhân cung cấp. Không xác nhận sinh viên; không có chat đầy đủ; không nêu đòi tiền cụ thể.

### Nguồn cá nhân và nghiên cứu kỹ thuật

**S08. Microsoft Security, “Contagious Interview: Malware delivered through fake developer job
interviews”.**
[Nguồn](https://www.microsoft.com/en-us/security/blog/2026/03/11/contagious-interview-malware-delivered-through-fake-developer-job-interviews/),
11/03/2026; chiến dịch được theo dõi từ ít nhất 12/2022. Microsoft mô tả giả tuyển lập trình viên,
bài đánh giá và dụ chạy package/lệnh độc hại. **Bằng chứng:** nghiên cứu threat intelligence quốc
tế, không phải vụ Việt Nam. Không xác nhận sinh viên hay công bố chat ứng viên. Nguồn này không xác
minh độc lập S10.

**S09. VOZ, “Đi xin việc mà còn bị lừa”.**
[Nguồn](https://voz.vn/t/di-xin-viec-ma-con-bi-lua.1186387/), chủ đề mở 20/12/2025; người viết tự
thuật sự việc 17–19/12/2025. Người viết thấy tin tuyển trên Facebook, điền form, nhận cuộc
gọi/email, làm bài trên web dự án; được chuyển 120.000 đồng, thấy số dư tăng và rút 328.000 đồng,
rồi nhận bảng margin. Ngày 21/12 chỉ là lịch hẹn dự kiến. **Bằng chứng:** lời tự đăng có ảnh chụp
chưa xác minh. Không nói là sinh viên; không thấy yêu cầu ứng tiền. Không gán A02/C04. Không có chat
đầy đủ.

**S10. Viblo, “Suýt Bay Sạch Data Vì Nhận ‘Coding Test’ Lương $120/hr”.**
[Nguồn](https://viblo.asia/p/suyt-bay-sach-data-vi-nhan-coding-test-luong-120hr-canh-bao-lua-dao-tuyen-dung-linkedin-13VM99vQVY7),
25/10/2025; ngày lời mời không nêu. Tác giả kể nhận lời mời LinkedIn, được giao repo và yêu cầu chạy
`npm install`/`npm run dev`; tác giả nói phát hiện package lạ rồi không chạy lệnh cài đặt. **Bằng
chứng:** bài cá nhân có phân tích kỹ thuật/ảnh minh họa, chưa xác minh độc lập package hay người
tuyển. Không xác nhận sinh viên. Ảnh offer/project, không có chat đầy đủ. Cài package không tự chứng
minh malware hay quyền truy cập.

### Đối chứng tuyển dụng chính thức

**S11. Trường Đại học Đồng Tháp, Thông báo tuyển dụng viên chức năm 2026, số 2519/TB-ĐHĐT.** [PDF
chính thức](https://www.dthu.edu.vn/mainpage/notice/1461.pdf), ký 05/05/2026; hạn hồ sơ 05/06, xét
tuyển dự kiến đến tháng 7. Văn bản nêu đầu mối, lịch và lệ phí theo Thông tư 92/2021/TT-BTC; mức thu
được thông báo sau khi tổng hợp hồ sơ đủ điều kiện. **Bằng chứng:** văn bản tuyển dụng chính thức,
không phải ca lừa đảo. Không xác nhận sinh viên. Là tài liệu gốc, không có chat. Có lệ phí chính
thức không làm mọi khoản phí khác trở nên an toàn.

## Bảng tổng hợp rủi ro để duyệt ngày 20/11/2026

Bảng đọc từ phía ứng viên. Mỗi dòng mô tả một rủi ro hoặc cách người tuyển dẫn ứng viên tới rủi ro đó. Một vụ có thể xuất hiện ở nhiều dòng. Nguồn gồm khảo sát S01–S14 ở trên, [sổ nguồn lô 12](../../../datasets/raw/jobshield-v03-initial/supplement-12/source-review.jsonl), [trích đoạn tuyển dụng lô 12](../../../datasets/raw/jobshield-v03-initial/supplement-12/README.md) và năm bài tra cứu bổ sung dưới đây. Đây là khảo sát chọn lọc phục vụ thiết kế. Số bài tìm được chưa cho phép ước tính mức độ phổ biến.

| Rủi ro | Giai đoạn và điều ứng viên có thể quan sát | Căn cứ và giới hạn khi đọc một mẫu |
|---|---|---|
| Mất tiền cọc để được nhận việc, nhận vật tư hoặc kích hoạt tài khoản | Lúc đăng ký hoặc trước khi giao việc, bên tuyển yêu cầu ứng viên chuyển một khoản tiền và nói rõ chuyển xong mới được bắt đầu. | N01 ghi nhận một học sinh trình báo ngay khi bị đòi cọc. N02 mô tả phí giữ chỗ và cọc vật tư. Cần ghi người nhận, mục đích và điều kiện thanh toán. S11 cung cấp đối chứng về lệ phí dự tuyển công khai. |
| Mất tiền khi ứng vốn làm nhiệm vụ hoặc đóng thêm để rút số dư | Khi giao việc, ứng viên được yêu cầu tự thanh toán đơn và được hứa hoàn gốc kèm hoa hồng. Yêu cầu nộp thêm có thể xuất hiện ở lượt sau. | N03, S14 mô tả diễn biến. Tin chỉ tuyển CTV chốt đơn chưa cho biết ai trả tiền. Muốn ghi nhận yêu cầu nộp thêm, cần trích đúng lượt có điều kiện rút tiền. |
| Mất tiền đầu tư dưới danh nghĩa thi tuyển | Ở vòng sàng lọc, ứng viên nhận đề bài đánh giá sản phẩm tài chính rồi được yêu cầu ký quỹ. | N04 mô tả một quy trình mạo danh ngân hàng. Một bài tập kiến thức về chứng chỉ quỹ tự nó chưa cho thấy ứng viên phải chuyển tiền. |
| Gánh nợ hoặc phải mua gói hàng để được làm việc | Khi phỏng vấn hoặc nhận việc, công việc ban đầu chuyển thành mua hàng, vào mạng lưới, tuyển thêm người hoặc đứng tên vay rồi giao tiền cho bên tuyển. | S05 có ảnh tờ tuyển và lời kể về khoản vay. S06 ghi nhận việc mua hàng ở giai đoạn sau. Đánh dấu riêng điều kiện mua hàng và việc đứng tên vay theo từng vụ. |
| Bị lấy dữ liệu nhận dạng hoặc quyền sử dụng tài khoản | Khi làm hồ sơ, ứng viên được yêu cầu cung cấp ảnh mặt, giấy tờ, OTP hoặc chuyển quyền đăng nhập. Cần ghi chính xác loại dữ liệu và ai sẽ sử dụng. | S02, S04, S13 và nguồn VTV ở lô 12. Yêu cầu quay mặt có thể xuất hiện sau poster. Mẫu chỉ có poster chưa đủ để xác định người đăng đã thu loại dữ liệu nào. |
| Bị lôi kéo cho thuê tài khoản hoặc trung chuyển tiền | Khi mô tả nhiệm vụ, bên tuyển yêu cầu mở hoặc giao tài khoản cho người khác dùng, hay nhận tiền rồi chuyển tiếp theo chỉ dẫn. | S04 là cảnh báo chung, S13 thuật lại vụ điều tra. Cần phân biệt cung cấp số tài khoản để nhận lương với giao quyền kiểm soát hoặc luân chuyển tiền của bên khác. |
| Mất dữ liệu hoặc quyền kiểm soát thiết bị khi làm bài tuyển dụng | Trong vòng kiểm tra, người tuyển gửi công cụ, ứng dụng hoặc bài thực hành cần chạy trên thiết bị cá nhân. | S08 có phân tích kỹ thuật về chiến dịch quốc tế. S10 là lời kể cá nhân. Văn bản có thể cho thấy yêu cầu cài đặt. Kết luận một tệp cụ thể có mã độc cần bằng chứng kỹ thuật gắn với tệp đó. |
| Bị ép cung cấp hình ảnh riêng tư, sau đó bị khống chế | Trong bước được gọi là khám sức khỏe, bên tuyển yêu cầu ảnh nhạy cảm. Một lời đe dọa công bố ảnh có thể xuất hiện sau khi ứng viên đã gửi. | S07 dẫn lời trình báo. Yêu cầu gửi ảnh và đe dọa phát tán là hai hành vi ở hai thời điểm. Chỉ ghi nhận đòi tiền nếu có bằng chứng riêng. |
| Bị đưa đến nơi làm việc khác và cưỡng ép lao động | Ban đầu có thể chỉ là lời mời làm một nghề cụ thể với mức lương hấp dẫn. Khi di chuyển hoặc đến nơi mới xuất hiện việc đổi địa điểm, cản trở rời đi hay ép làm công việc khác. | N05 thuật lại vụ giải cứu người được mời làm lơ xe. Gia đình nhận yêu cầu tiền chuộc sau đó. S12 ghi nhận một vụ khác. Lời hứa lương cao ở tin đầu chưa chứng minh cưỡng ép. |
| Bị đánh lừa về danh tính nhà tuyển dụng | Ngay ở tin đăng hoặc thư mời có thể thấy tên doanh nghiệp, logo hay văn bản có dấu. Ở vòng sau có thể xuất hiện chỉ dẫn trái quy trình đơn vị công bố. | N04 cho phép đối chiếu quy trình riêng của Vietcombank. Với hai JD mạo danh ở lô 12, cần nối bằng chứng bên ngoài với đúng poster hoặc tài khoản. Tên doanh nghiệp trong JD chỉ cho biết bên đăng tự xưng là ai. |

### Năm bài tra cứu bổ sung

- **N01 · Công an Hà Tĩnh.** Ngày 05/07/2025, Công an xã Lộc Hà tiếp nhận trình báo của học sinh vừa thi tốt nghiệp THPT. Lời mời làm nhiệm vụ có hoa hồng xuất hiện trước yêu cầu đặt cọc kích hoạt tài khoản. Vụ việc được ngăn chặn trước khi em mất tiền. [Tin về vụ việc](https://congan.hatinh.gov.vn/tin-tuc-su-kien/an-ninh-trat-tu/ngan-chan-kip-thoi-vu-viec-lua-dao-tuyen-dung-lam-nhiem-vu-online-1751712080.caht)
- **N02 · Công an Khánh Hòa.** Cảnh báo dịp Tết 2026 mô tả việc tuyển người đóng gói quà tại nhà rồi thu phí giữ chỗ hoặc tiền cọc vật tư. Bài cũng mô tả biến thể chuyển sang nhiệm vụ thanh toán đơn. Đây là cảnh báo theo thủ đoạn. [Bài cảnh báo đóng gói quà Tết](https://congan.khanhhoa.gov.vn/vi/canh-giac-thu-doan-lua-dao-tuyen-cong-tac-vien-dong-goi-qua-tet-cuoi-nam)
- **N03 · Công an Đồng Nai.** Cảnh báo tổng hợp mô tả bên tuyển giả mạo thương hiệu, hứa hoàn tiền cho đơn ứng viên tự thanh toán và tăng giá trị nhiệm vụ sau những đơn nhỏ. Nội dung cùng cơ chế với S14, được dùng để đối chiếu diễn biến. [Bài cảnh báo tuyển cộng tác viên](https://congan.dongnai.gov.vn/pages/newsdetail.aspx?CatId=109&NewsId=31803)
- **N04 · Vietcombank, tháng 09/2026.** Ngân hàng công bố quy trình bị mạo danh, gồm văn bản có dấu giả, mã dự tuyển và yêu cầu ký quỹ khi đánh giá sản phẩm tài chính. Đơn vị cũng nêu kênh nhận hồ sơ chính thức. Bài này và S03 đều do Vietcombank phát hành. [Thông báo của ngân hàng](https://www.vietcombank.com.vn/vi-VN/Trang-thong-tin-dien-tu/Articles/2026/09/16/20260914_MKTTT_Canh-bao-lua-dao-mao-danh-tuyen-dung-VCB)
- **N05 · Bộ Công an, vụ giải cứu tại Lâm Đồng.** Người tìm việc được giới thiệu việc lơ xe khoảng tháng 10/2025. Bài ghi nhận việc bị ép làm công việc lừa đảo ở Campuchia và cuộc gọi đòi tiền chuộc gia đình nhận ngày 21/12/2025. Đây là tường thuật sau giải cứu. [Thông tin vụ giải cứu](https://www.bocongan.gov.vn/bai-viet/ho-tro-giai-cuu-thanh-cong-nan-nhan-bi-lua-dua-sang-campuchia-1770107892)

### Từ nguồn vụ việc tới quy tắc gán nhãn

Trong lô 12, mẫu JS-SUP12-01 ghi yêu cầu chỉ cần biết đánh máy và hứa lương cơ bản 24 triệu đồng/tháng cùng hoa hồng. Người đọc có thể chỉ ra sự chênh lệch giữa yêu cầu và thu nhập được hứa. Muốn ghi thêm việc người lao động bị đưa qua biên giới hoặc bị giữ giấy tờ, phải tìm được bằng chứng về chính vụ đó, ở đúng giai đoạn. Tương tự, việc chuyển kênh liên hệ chỉ là một chi tiết cần đọc trong ngữ cảnh.

Khi duyệt từng dòng, nên đặt cạnh nhau một trích đoạn có dấu hiệu và một tình huống dễ nhầm, rồi xác định câu nào đủ để cảnh báo, câu nào chỉ gợi ý cần hỏi thêm và chi tiết nào cần đối chiếu bên ngoài. Kho hiện còn thiếu hội thoại nguyên văn cho một số hành vi phi tài chính. Những cảnh báo tổng hợp giúp xác định nội dung cần khảo sát tiếp, song chưa cung cấp đáp án theo câu cho các hội thoại đó.

## Ma trận cơ chế và mã cần đối chiếu

Ma trận chỉ nối cơ chế nguồn mô tả với mã có thể cần rà. Đây không phải nhãn cho nguồn hoặc mẫu. Mỗi
nhãn A chỉ được gán nếu nội dung mẫu có đủ hành vi, điều kiện và chủ thể theo codebook.

| Cơ chế nguồn mô tả | Nguồn | Mã v0.3 cần đối chiếu | Giới hạn |
|---|---|---|---|
| Phí/đặt cọc là điều kiện tuyển hoặc nhận việc; đối chứng phí tuyển chính thức | S01–S03, S05–S06, S11 | A01; C02 | S11 là đối chứng chính thức; chỉ có tên khoản phí không đủ xác định cơ chế. |
| Trả tiền làm nhiệm vụ, nhận hoàn vốn/hoa hồng; sau đó tăng giá trị | S03, S14 | A02–A03; C04 | Cảnh báo tổng hợp không đủ gán chuỗi nhiệm vụ; cần các lượt trả và yêu cầu nộp tiếp trong cùng nguồn mẫu. |
| Lời mời việc làm gắn mua hàng/gói, nâng vị trí hoặc tuyển người | S05–S06 | A06; C01–C03, C10 | A04 chỉ khi có yêu cầu đầu tư độc lập gắn tuyển dụng. S05/S06 cùng khoản mua hàng/gói và mạng lưới, nên không coi là ca A04 riêng. |
| Công việc dẫn tới đứng tên/làm thủ tục vay, chuyển tiền vay cho công ty | S05 | A05; C07–C08, C10 | Căn cứ xem xét mở A05 tới hành vi thực hiện/xác thực khoản vay gắn tuyển dụng/việc làm. Không suy khoản vay từ nhắc CCCD/OTP. |
| Tuyển dụng để mở/cho thuê tài khoản, giao thẻ, đăng nhập, OTP/SIM hoặc chuyển tiền | S04, S13 | A07–A10; C08; có thể C02/C06 | Phân biệt mở tài khoản cho bản thân với mở/giao quyền sử dụng cho bên khác; số tài khoản nhận lương không đồng nghĩa trung chuyển tiền. |
| Thu thập CCCD/ảnh mặt/dữ liệu; link, app hoặc yêu cầu chạy công cụ | S01–S03, S07–S10 | A07–A08, A11; C06, C08–C09 | Link/app/npm install chưa đủ gán A11. C09 ghi chỉ dẫn cài/chạy/cấp quyền. C06 gồm chỉ dẫn chuyển sang kênh trò chuyện hoặc website đăng ký; URL đơn lẻ chưa đủ. |
| Đổi điều kiện hoặc nhiệm vụ trong quá trình tìm việc | S05–S06 | C07 | Cần hai phát biểu về cùng cơ hội để đối chiếu; thay đổi công việc riêng lẻ không đủ A12. |
| Hạn chế rời đi/liên lạc hoặc cưỡng ép làm việc | S06, S12 | A12; C02–C03 | Cần hành vi kiểm soát cụ thể; đi làm nước ngoài riêng lẻ chưa đủ. S12 chưa xác nhận nhân vật là sinh viên. |
| Ép gửi ảnh/video khỏa thân hoặc hành vi tình dục | S07 | A13; C02, C08 | A13 chỉ cho ảnh/video khỏa thân hoặc hành vi tình dục theo định nghĩa; không áp cho mọi ảnh thân thể/khám sức khỏe. S07 không xác nhận sinh viên. |
| Đe dọa phát tán dữ liệu riêng tư để buộc làm theo | S07 | A14; C02, C08 | S07 nêu đe dọa phát tán để ép hành động, không nêu đòi tiền cụ thể. Không mã C03 nếu không có dấu hiệu cô lập/giữ bí mật. |
| Mạo danh đơn vị tuyển dụng, kể cả cách dùng hình/giọng giả | S01–S03 | V01; C06, C08 | S01 là cảnh báo chung, S02/S03 từ đơn vị bị mạo danh. V01 cần đối chiếu đúng tài khoản/tuyên bố; không suy mạo danh từ hình thức phỏng vấn hoặc tên nền tảng. |
| Liên kết/ứng dụng giả hoặc gây hại | S08, S10 | V02; C09 | S08 mô tả chiến dịch quốc tế; không xác minh project/package trong S10. S10 là bài tự đăng, tác giả không chạy lệnh cài đặt. V02 cần kiểm chứng riêng. |
| Thành công được kể như lời chứng thực trong lời mời việc | S03, S05–S06 | C10; C01–C03 | Ghi nhận lời chứng thực nếu xuất hiện trong đầu vào; không suy người làm chứng là đồng phạm hoặc lời kể chắc chắn giả. |

## Kết luận và giới hạn

Các nguồn củng cố việc giữ A01–A12 và xem xét A13/A14 cho ép ảnh/hành vi tình dục và đe dọa phát tán
dữ liệu riêng tư. S05 là căn cứ rõ để cân nhắc mở A05 tới việc hướng dẫn thực hiện khoản vay gắn với
tuyển dụng. A04 chưa có ca độc lập trong tập này; khoản mua hàng/gói ở S05/S06 được mô tả cùng cơ
chế tham gia/mạng lưới. C07–C10 là bối cảnh cần ghi đúng điều kiện và hành động thể hiện trong
chuỗi. Nguồn năm 2022 và 2024 bổ sung cơ chế đã được cảnh báo; không chứng minh tần suất hiện nay.

Mức chứng cứ trải từ hướng dẫn/cảnh báo tổng hợp đến điều tra báo chí, thông tin cơ quan chức năng
và lời kể tự đăng. Một số nguồn cùng cơ quan/chủ đề; chúng không phải các vụ độc lập. Nguồn không có
chat đầy đủ thì chỉ dùng làm căn cứ nghiên cứu. Mọi kết luận pháp lý, xác minh danh tính, doanh
nghiệp, tài khoản, khoản vay hay phần mềm cần nguồn riêng.

Chưa trích xuất hay chuyển thể nguồn thành dữ liệu, chưa kiểm tra quyền sử dụng/khử định danh, chưa
gán nhãn hoặc chia tập. Bước tiếp theo là đối chiếu dự thảo codebook với các ranh giới này rồi tìm
đầu vào gốc có đủ ngữ cảnh và quyền sử dụng.

## Liên kết với codebook

[Bản nháp CODEBOOK-v0.3-DRAFT.md](../../../data/v1/CODEBOOK.md) lưu
quy tắc nhãn; báo cáo này chỉ lưu căn cứ khảo sát, không phải dữ liệu gán nhãn.

