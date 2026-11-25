# Đối chiếu trực tiếp PhoBERT v2 (cũ) vs PhoBERT v3 Type A (mới)

- Trong **30 mẫu `test` v2** giữ lại trong `test` v3, có **30/30** mẫu giữ nguyên nhãn tổng; PhoBERT v2 trên nhãn gốc v2 đạt `23/30` nhãn đúng (`missed=2`, `FA=5`).
- Lưu ý: PhoBERT v2 chỉ được huấn luyện trên **6 mã v2** (`A01, A02, A07, A09, C11, C12`), nên khi ánh xạ sang `G01`–`G08` sẽ bằng `0` ở `G03, G06, G07`.

## 1. Tổng hợp chất lượng trên các tập chuẩn v3

| Tập đánh giá | Chỉ số | PhoBERT v2 (cũ) | PhoBERT v3 Type A (mới) | Chênh lệch |
|---|---|---:|---:|---:|
| Test v3 đầy đủ (64 mẫu) | **F1 nhãn tổng** | 0.7606 | **0.8667** | +0.1061 |
| Test v3 đầy đủ (64 mẫu) | Precision | 0.7105 | **0.9630** | +0.2525 |
| Test v3 đầy đủ (64 mẫu) | Recall | 0.8182 | 0.7879 | -0.0303 |
| Test v3 đầy đủ (64 mẫu) | Báo nhầm (False Alarms) | 11 | **1** | -10 |
| Test v3 đầy đủ (64 mẫu) | Bỏ sót (Missed) | 6 | 7 | +1 |
| Test v3 đầy đủ (64 mẫu) | Exact Match | 23/64 | **30/64** | +7 |
| Test v3 đầy đủ (64 mẫu) | Evidence F1 (mã `G01`–`G08`) | 0.2951 | **0.2602** | -0.0349 |
| Tập con Test v2 (30 mẫu) | **F1 nhãn tổng** | 0.7879 | **0.8000** | +0.0121 |
| Tập con Test v2 (30 mẫu) | Precision | 0.7222 | **1.0000** | +0.2778 |
| Tập con Test v2 (30 mẫu) | Recall | 0.8667 | 0.6667 | -0.2000 |
| Tập con Test v2 (30 mẫu) | Báo nhầm (False Alarms) | 5 | **0** | -5 |
| Tập con Test v2 (30 mẫu) | Bỏ sót (Missed) | 2 | 5 | +3 |
| Tập con Test v2 (30 mẫu) | Exact Match | 13/30 | **15/30** | +2 |
| Tập con Test v2 (30 mẫu) | Evidence F1 (mã `G01`–`G08`) | 0.4368 | **0.3111** | -0.1257 |
| Negative Holdout (54 âm) | Báo nhầm (FPR) | 0/54 (0.0%) | **0/54 (0.0%)** | +0 |

## 2. Phân tách theo nguồn trên Test v3 (`64` mẫu)

| Nguồn (`origin`) | N | v2 F1 / Đúng nhãn | v3 Type A F1 / Đúng nhãn |
|---|---:|---:|---:|
| `hard_negative_real` | 31 | 0.0000 (20/31) | **0.0000 (30/31)** |
| `real` | 24 | 0.8837 (19/24) | **0.8293 (17/24)** |
| `real_quoted_excerpt` | 9 | 0.9412 (8/9) | **1.0000 (9/9)** |

## 3. Phân tách từng nhóm hành vi `G01`–`G08` trên Test v3 (`doc_f1` / `evidence_f1`)

| Mã nhóm | Số mẫu Test | v2 `doc_f1` / `ev_f1` | v3 Type A `doc_f1` / `ev_f1` |
|---|---:|---:|---:|
| `G01` | 13 | 0.47 / 0.28 | 0.31 / 0.20 |
| `G02` | 9 | 0.52 / 0.50 | 0.35 / 0.29 |
| `G03` | 2 | 0.00 / 0.00 | 0.40 / 0.33 |
| `G04` | 3 | 0.00 / 0.00 | 0.80 / 0.80 |
| `G05` | 2 | 0.00 / 0.00 | 0.40 / 0.33 |
| `G06` | 2 | 0.00 / 0.00 | 0.80 / 0.57 |
| `G07` | 3 | 0.00 / 0.00 | 0.00 / 0.00 |
| `G08` | 4 | 0.25 / 0.20 | 0.36 / 0.17 |

## 4. Hiệu năng CPU cục bộ (cùng 25 mẫu benchmark)

| Chỉ số CPU | PhoBERT v2 (cũ) | PhoBERT v3 Type A (mới) |
|---|---:|---:|
| Cold load (s) | 0.403 | 0.565 |
| VnCoreNLP load (s) | 0.178 | 0.271 |
| Peak RSS RAM (MB) | 904.4 | 959.2 |
| Latency p50 (ms) | 588.15 | 602.15 |
| Latency p95 (ms) | 1838.25 | 1925.41 |
| Tin sạch p50 (ms) | 736.09 | 764.84 |
| Tin nghi ngờ p50 (ms) | 255.06 | 274.00 |
