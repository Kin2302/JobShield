# ADR 003 — Quản lý và phát hành kho kịch bản

## Trạng thái (Status)

Đã chấp nhận và cập nhật cho kho v3 (`CatalogVersion = 2.0`) ngày 24/11/2026.

## Bối cảnh (Context)

JobShield cần ánh xạ các mã phát hiện `G01`–`G08` từ mô hình `phobert-v3-typeA` sang giải thích dễ hiểu cho sinh viên, bước kiểm tra tiếp theo và vụ việc tham chiếu có nguồn chính thống (HTTPS). Mã phiên bản kho giúp truy vết kết quả ứng với bản nội dung nào.

### Các phương án cân nhắc

| Phương án | Cách tổ chức | Ưu điểm | Hạn chế |
| --- | --- | --- | --- |
| A — Kho trong PostgreSQL | Lưu kịch bản và nguồn trong bảng quan hệ | Dễ sửa từng dòng qua giao diện quản trị | Phải vận hành thêm DB và migration không cần thiết cho 8 nhóm cố định |
| **B — Phát hành kho JSON có phiên bản nhúng cùng Backend** | Đóng gói `RecruitmentScenarios.json` làm Embedded Resource trong `JobShield.Infrastructure`, kiểm tra hợp lệ khi khởi động | Nạp vào bộ nhớ ngay khi khởi động, tốc độ tra cứu O(1), dễ kiểm soát phiên bản qua Git | Muốn cập nhật nội dung kho cần build lại container/backend |

## Quyết định (Decision)

Tiếp tục chọn **Phương án B** cho v3. Tệp [RecruitmentScenarios.json](../../backend/JobShield.Infrastructure/RecruitmentScenarios.json) được nâng cấp lên phiên bản **`2.0`** gồm:

- Đầy đủ **8 nhóm hành vi `G01`–`G08`** khớp với [Codebook v3](../../data/v3/CODEBOOK.md).
- **15 vụ việc tham chiếu** kèm đường dẫn nguồn HTTPS đã kiểm chứng.
- `ScenarioCatalogLoader` nạp và kiểm tra tính hợp lệ của toàn bộ 8 mã, đường dẫn HTTPS và cấu trúc JSON ngay khi Backend khởi động; mọi phản hồi `/api/analyze` đều trả kèm `catalogVersion`.

## Hệ quả (Consequences)

- Cập nhật kho kịch bản và huấn luyện mô hình AI vẫn tách biệt hoàn toàn: sửa giải thích/vụ việc không cần train lại PhoBERT.
- Nếu tệp JSON bị thiếu hoặc sai định dạng, Backend dừng ngay lúc khởi động và bị phát hiện sớm bởi `ScenarioCatalogTests` trong CI.
