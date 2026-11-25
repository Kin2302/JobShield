# Báo cáo so sánh mô hình JobShield v3

## 1. Tổng hợp trên tập Test v3 (64 mẫu), Test v2 subset (30 mẫu) và Negative Holdout (55 mẫu)

| Mô hình | Kiến trúc | Test v3 F1 | Precision | Recall | Missed | FA (Test) | Exact Match | Evidence F1 | Test v2 (30) F1 / Exact | Holdout Neg FA (54) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `phobert-v3-typeA` | typeA | 0.8667 | 0.9630 | 0.7879 | 7 | 1 | 30/64 | 0.2602 | 0.8000 / 15/30 | 0/54 (0.0%) |
| `phobert-v3-typeA-no-antishortcut` | typeA | 0.7857 | 0.9565 | 0.6667 | 11 | 1 | 30/64 | 0.1983 | 0.6364 / 15/30 | 1/54 (1.8%) |
| `phobert-v3-typeB` | typeB | 0.8571 | 0.9000 | 0.8182 | 6 | 3 | 30/64 | 0.2857 | 0.8571 / 16/30 | 0/54 (0.0%) |
| `xlmr-v3-typeA` | typeA | 0.7576 | 0.7576 | 0.7576 | 8 | 8 | 26/64 | 0.1341 | 0.7429 / 11/30 | 1/54 (1.8%) |
| `xlmr-v3-typeB` | typeB | 0.7586 | 0.8800 | 0.6667 | 11 | 3 | 28/64 | 0.3667 | 0.6364 / 15/30 | 0/54 (0.0%) |
| `tfidf-v3` | typeB | 0.8136 | 0.9231 | 0.7273 | 9 | 2 | 37/64 | 0.5667 | 0.8462 / 20/30 | 1/54 (1.8%) |

## 2. Phân tách theo nguồn trên Test v3 (`real` vs `real_quoted_excerpt` vs `hard_negative_real`)

### `phobert-v3-typeA`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 1 | 0 | 30 | 0.0000 | 30/31 |
| `real` | 24 | 17 | 0 | 7 | 0 | 0.8293 | 0/24 |
| `real_quoted_excerpt` | 9 | 9 | 0 | 0 | 0 | 1.0000 | 0/9 |

### `phobert-v3-typeA-no-antishortcut`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 1 | 0 | 30 | 0.0000 | 30/31 |
| `real` | 24 | 16 | 0 | 8 | 0 | 0.8000 | 0/24 |
| `real_quoted_excerpt` | 9 | 6 | 0 | 3 | 0 | 0.8000 | 0/9 |

### `phobert-v3-typeB`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 3 | 0 | 28 | 0.0000 | 28/31 |
| `real` | 24 | 19 | 0 | 5 | 0 | 0.8837 | 2/24 |
| `real_quoted_excerpt` | 9 | 8 | 0 | 1 | 0 | 0.9412 | 0/9 |

### `xlmr-v3-typeA`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 8 | 0 | 23 | 0.0000 | 23/31 |
| `real` | 24 | 20 | 0 | 4 | 0 | 0.9091 | 3/24 |
| `real_quoted_excerpt` | 9 | 5 | 0 | 4 | 0 | 0.7143 | 0/9 |

### `xlmr-v3-typeB`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 3 | 0 | 28 | 0.0000 | 28/31 |
| `real` | 24 | 14 | 0 | 10 | 0 | 0.7368 | 0/24 |
| `real_quoted_excerpt` | 9 | 8 | 0 | 1 | 0 | 0.9412 | 0/9 |

### `tfidf-v3`
| Nguồn (`origin`) | N | TP | FP | FN | TN | F1 | Exact Match |
|---|---:|---:|---:|---:|---:|---:|---:|
| `hard_negative_real` | 31 | 0 | 2 | 0 | 29 | 0.0000 | 29/31 |
| `real` | 24 | 19 | 0 | 5 | 0 | 0.8837 | 7/24 |
| `real_quoted_excerpt` | 9 | 5 | 0 | 4 | 0 | 0.7143 | 1/9 |

## 3. Benchmark hiệu năng CPU cục bộ

| Mô hình | Cold load (s) | VnCoreNLP (s) | Peak RSS (MB) | Latency p50 (ms) | Latency p95 (ms) | Clean p50 (ms) | Suspicious p50 (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `phobert-v3-typeA` | 0.56 | 0.27 | 959.2 | 602.15 | 1925.41 | 764.84 | 274.00 |
| `phobert-v3-typeA-no-antishortcut` | 0.54 | 0.23 | 957.6 | 558.08 | 1815.28 | 741.03 | 244.86 |
| `phobert-v3-typeB` | 0.58 | 0.21 | 1262.2 | 182.80 | 1022.12 | 160.83 | 318.43 |
| `xlmr-v3-typeA` | 0.61 | 0.00 | 1125.4 | 551.71 | 2165.63 | 786.70 | 268.36 |
| `xlmr-v3-typeB` | 1.06 | 0.00 | 1661.7 | 174.23 | 868.14 | 153.43 | 309.96 |
| `tfidf-v3` | 0.22 | 0.00 | 375.8 | 1.70 | 3.03 | 0.89 | 2.19 |

