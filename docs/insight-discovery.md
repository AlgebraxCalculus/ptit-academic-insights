# Insight Discovery — PTIT Academic Insights

**Phase:** 2 — Statistical exploration & insight selection
**Date:** 2026-09-11
**Input:** `data/DS-SV-DK-DATN-D22-KY-THUAT.xlsx` · `docs/data-audit.md` (Phase 1 source of truth)
**Analytical dataset:** 905 rows in-scope, 903 với CPA khả dụng
**Status:** Chưa xây frontend. Tài liệu này quyết định *nội dung* sẽ được trình bày ở phase sau.

---

## 0. Điểm cập nhật so với Phase 1

| Hạng mục | Phase 1 (audit) | Phase 2 (đã xác nhận) |
|---|---|---|
| Ý nghĩa `E22*` | **UNCONFIRMED** — 87% sinh viên mang mã ngành không phải CNTT | ✅ **Đã xác nhận: E22 = hệ CNTT chất lượng cao (CLC)** theo quy ước nhà trường |
| Nhãn nhóm | Dùng nhãn trung tính `D22*` / `E22*` | Dùng `CNTT` (D22CNPM + D22HTTT) và `CNTT CLC` (E22*) |

Một điểm từ Phase 1 **vẫn giữ nguyên giá trị** và trở thành đầu vào phân tích quan trọng: trong 215 sinh viên CLC, chỉ 29 mang mã ngành tuyển sinh CNTT (`DCCN`). Phần lớn là `DCVT` (96), `DCDT` (50), `DCAT` (34). Việc E22 **là** hệ CNTT CLC không làm mất đi sự thật rằng **thành phần đầu vào của nhóm này khác hẳn nhóm CNTT chuẩn** — đây là confound trung tâm của mọi so sánh hai chương trình (xem CORE-2, SUP-2, SUP-3).

Toàn bộ cleaning rules A1–A4, B1, C1–C7, D1–D4, E1–E5 của Phase 1 đã được implement và áp dụng. Assertion `0 ≤ CPA ≤ 4` pass.

---

## 1. Statistical overview

### 1.1 Tổng thể CPA (in-scope, n = 903)

| Metric | Giá trị |
|---|---:|
| N rows in-scope | 905 |
| N có CPA | **903** (thiếu 2) |
| Mean | **2.7915** |
| 95% CI của mean (bootstrap, 10k) | [2.7631, 2.8201] |
| Median | **2.7900** |
| 95% CI của median (bootstrap) | [2.7600, 2.8200] |
| Std. deviation (ddof=1) | **0.4322** |
| Variance | 0.1868 |
| Coefficient of variation | 0.1548 |
| Min / Max | **1.40 / 3.72** |
| Range | 2.32 |
| Q1 / Q2 / Q3 | 2.5200 / 2.7900 / 3.1100 |
| **IQR** | **0.5900** |
| MAD | 0.3000 |
| Skewness | −0.2391 |
| Excess kurtosis | −0.2606 |
| Sarle bimodality coefficient | 0.3859 (< 0.555 → **không** bimodal) |

**Percentiles**

| p1 | p5 | p10 | p20 | p25 | p30 | p40 | p50 | p60 | p70 | p75 | p80 | p90 | p95 | p99 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.73 | 2.01 | 2.23 | 2.44 | 2.52 | 2.58 | 2.67 | 2.79 | 2.90 | 3.05 | 3.11 | 3.19 | 3.34 | 3.49 | 3.64 |

**Normality:** Shapiro-Wilk W = 0.9915, p = 4.3×10⁻⁵ · D'Agostino K² = 11.53, p = 3.1×10⁻³ · Jarque-Bera p = 3.8×10⁻³.
→ Bác bỏ giả thuyết chuẩn về mặt thống kê, nhưng skew và kurtosis đều nhỏ. Phân phối **đơn đỉnh, gần đối xứng, đuôi hơi mỏng**. Với n = 903, test chuẩn nhạy với sai lệch rất nhỏ — không nên diễn giải p-value này là "phân phối bất thường".

### 1.2 Threshold proportions (thang phân loại 4.0)

| Xếp loại | Ngưỡng | n | % | 95% CI |
|---|---|---:|---:|---|
| Xuất sắc | ≥ 3.60 | 20 | 2.21% | [1.36%, 3.40%] |
| Giỏi | 3.20 – 3.59 | 157 | 17.39% | [14.97%, 20.02%] |
| Khá | 2.50 – 3.19 | 516 | 57.14% | [53.84%, 60.40%] |
| Trung bình | 2.00 – 2.49 | 169 | 18.72% | [16.22%, 21.42%] |
| Yếu | < 2.00 | 41 | 4.54% | [3.28%, 6.11%] |

Cumulative: ≥2.0 → 95.46% · ≥2.5 → 76.74% · ≥3.0 → 34.33% · ≥3.2 → 19.60% · ≥3.5 → 4.87% · ≥3.6 → 2.21%

### 1.3 Descriptives theo track (đơn vị phân tích thực chất)

| Track | Program | n rows | n CPA | mean | 95% CI | median | sd | IQR | min | max | skew |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| D22CNPM | CNTT | 362 | 362 | **3.0199** | [2.990, 3.049] | 3.030 | 0.2881 | 0.440 | 2.43 | 3.72 | +0.178 |
| D22HTTT | CNTT | 328 | 326 | **2.4847** | [2.441, 2.529] | 2.445 | 0.4042 | 0.480 | 1.65 | 3.69 | +0.357 |
| E22CNPM | CNTT CLC | 137 | 137 | **2.7560** | [2.697, 2.815] | 2.730 | 0.3504 | 0.460 | 1.40 | 3.67 | −0.541 |
| E22HTTT | CNTT CLC | 40 | 40 | **2.9172** | [2.788, 3.047] | 2.805 | 0.4173 | 0.725 | 2.18 | 3.70 | +0.363 |
| E22TTNT | CNTT CLC | 38 | 38 | **3.2429** | [3.140, 3.346] | 3.285 | 0.3228 | 0.500 | 2.57 | 3.71 | −0.469 |

### 1.4 Effect-size league table — cái gì thực sự giải thích CPA?

| Biến phân nhóm | k nhóm | η² (tỷ lệ phương sai CPA giải thích được) |
|---|---:|---:|
| `class_code` | 18 | **0.3522** |
| `track_label` | 5 | **0.3448** |
| `tttn_grade` | 9 | 0.2470 |
| `credits` (r², toàn bộ) | — | 0.2792 |
| `credits` (r², chỉ SV đủ đk) | — | 0.2034 |
| `eligible_for_thesis` | 2 | 0.1834 |
| `birthplace` (n ≥ 20) | 14 | 0.0699 |
| `admission_major_code` | 7 | 0.0294 |
| **`program` (CNTT vs CLC)** | 2 | **0.0109** |
| `is_off_cohort` | 2 | 0.0013 |

➡️ Đây là bảng quan trọng nhất của cả phase. **Chương trình đào tạo giải thích 1.1% phương sai CPA; track giải thích 34.5%** — gấp hơn 30 lần. Và `class_code` (18 nhóm) chỉ nhỉnh hơn `track_label` (5 nhóm) đúng 0.0074 → **lớp không thêm thông tin gì so với track**.

### 1.5 Các chiều KHÔNG hỗ trợ phân tích (kiểm chứng lại)

| Chiều brief yêu cầu | Kết quả kiểm tra | Kết luận |
|---|---|---|
| **Cohort differences** | `intake_year`: 2022 → 899, 2021 → 6 | ❌ Không đủ biến thiên. η² = 0.0013 |
| **Trends over time** | Không có cột thời gian; dataset là snapshot một lần xét ĐATN | ❌ Không thể thực hiện |
| Gender | Không tồn tại trong dữ liệu | ❌ Không suy ra từ tên |
| Điểm đầu vào | Không tồn tại | ❌ Đây là biến kiểm soát then chốt bị thiếu |

Hai mục "Cohort differences" và "Trends over time" trong brief **không thể thực hiện** với dataset này. Đây là kết luận có bằng chứng, không phải bỏ sót.

---

## 2. Candidate insights (30)

| ID | Candidate insight |
|---|---|
| C01 | CPA toàn nhóm: mean 2.79, median 2.79, sd 0.43, IQR 0.59 — phân phối đơn đỉnh gần đối xứng |
| C02 | CPA thực tế chỉ trải 1.40–3.72; không ai đạt 4.0 và không ai dưới 1.40 |
| C03 | 76.7% đạt Khá trở lên (≥2.5); chỉ 19.6% đạt Giỏi trở lên (≥3.2); 2.2% Xuất sắc (≥3.6) |
| C04 | 4.54% dưới 2.00 (n=41) |
| C05 | Dù là hỗn hợp của hai track cách nhau rất xa, phân phối gộp **không** bimodal (BC=0.386, overlap 0.395) |
| C06 | CNTT CLC có mean CPA cao hơn CNTT: +0.106 (p=0.0067, d=0.246) |
| C07 | Program (CNTT vs CLC) chỉ giải thích **1.1%** phương sai CPA (η²=0.0109) |
| C08 | Track giải thích **34.5%** phương sai CPA (η²=0.3448) — gấp 31× program |
| C09 | Lớp không thêm thông tin so với track: η² 0.3522 vs 0.3448; KW trong mọi track đều p>0.18 |
| C10 | D22CNPM vs D22HTTT chênh 0.535 điểm, d=1.538 — effect size lớn nhất dataset |
| C11 | D22CNPM có min CPA 2.43, không một ai dưới ngưỡng; chỉ 1/362 dưới median HTTT → dấu hiệu phân track theo CPA |
| C12 | **Đảo dấu like-for-like:** CLC thấp hơn ở CNPM (−0.264) nhưng cao hơn ở HTTT (+0.433) |
| C13 | Mean CLC (2.872) nằm **giữa** HTTT (2.485) và CNPM (3.020) → so sánh gộp phụ thuộc hoàn toàn vào tỷ trọng track |
| C14 | Chênh lệch CLC–CNTT tập trung ở đuôi dưới: p10 +0.234, p20 +0.160, p50 chỉ +0.040 |
| C15 | CLC ít sinh viên <2.0 hơn (1.40% vs 5.52%) và nhiều ≥3.6 hơn (4.19% vs 1.60%) |
| C16 | E22TTNT có mean cao nhất toàn scope: 3.243 (n=38) |
| C17 | Trong nội bộ CLC, mã ngành tuyển sinh tạo khác biệt lớn: DCCN+DCAT 3.086 vs DCVT+DCDT 2.784 (d=0.824) |
| C18 | 87% sinh viên CLC mang mã ngành tuyển sinh không phải CNTT (VT 44.7%, ĐT 23.3%, ATTT 15.8%) |
| C19 | Tỷ lệ đủ điều kiện ĐATN: D22CNPM 99.45% vs D22HTTT 83.54% — risk ratio 29.8× |
| C20 | Tỷ lệ đủ điều kiện theo program **không** khác biệt có ý nghĩa (91.88% vs 93.95%, p=0.39) |
| C21 | Sinh viên không đủ đk có CPA thấp hơn hẳn: 2.138 vs 2.844 (d=1.806) |
| C22 | Nhưng 13.4% sinh viên không đủ đk có CPA ≥2.5, cao nhất 3.37 → điều kiện ĐATN **không** là hàm của CPA |
| C23 | 69.4% sinh viên đạt trần 146 tín chỉ; tương quan CPA–tín chỉ rho=0.621 |
| C24 | Tương quan CPA–tín chỉ vẫn mạnh khi chỉ xét SV đủ đk: rho=0.546 |
| C25 | Tỷ lệ chạm trần tín chỉ theo track: CNPM 93.1%, TTNT 84.2%, HTTT 48.5% |
| C26 | D22HTTT chiếm 36.2% cohort nhưng **92.5%** của decile thấp nhất |
| C27 | E22TTNT: 47.4% sinh viên nằm trong decile cao nhất, representation index 4.61 (n=38) |
| C28 | Gini của CPA rất thấp (0.0877) — CPA là thang bị nén, chênh lệch tuyệt đối nhỏ |
| C29 | TTTN tương quan trung bình với CPA (rho=0.416); tỷ lệ A+ gần như bằng nhau giữa 2 program (65.3% vs 66.8%) |
| C30 | Nơi sinh có liên hệ thống kê với CPA (Hà Nội 2.932 vs còn lại 2.739, p<0.001) nhưng η² chỉ 0.070 |

---

## 3. Scoring table

Thang 1–5. **Analytical value / Reliability / Public interest**: cao = tốt.
**Risk of misinterpretation**: cao = **nguy hiểm hơn** (5 = rất dễ bị hiểu sai thành causal claim).

| ID | Insight (rút gọn) | Evidence | Metric | N | Anal. value | Reliab. | Public interest | Risk | Verdict |
|---|---|---|---|---:|:---:|:---:|:---:|:---:|---|
| C01 | Hình dạng phân phối CPA tổng thể | mean/median/sd/IQR/skew | mean 2.7915, sd 0.4322 | 903 | 3 | 5 | 4 | 1 | ✅ **CORE-4** |
| C02 | Range thực tế 1.40–3.72 | min/max | range 2.32 | 903 | 3 | 5 | 3 | 2 | ✅ CORE-4 (gộp) |
| C03 | Threshold proportions | binomial CI | 76.7% ≥2.5; 19.6% ≥3.2 | 903 | 4 | 5 | 5 | 2 | ✅ CORE-4 (gộp) |
| C04 | 4.54% dưới 2.00 | binomial CI | 41/903 | 903 | 3 | 5 | 4 | 3 | ✅ CORE-4 (gộp) |
| C05 | Hỗn hợp 2 track không lộ bimodal | Sarle BC, overlap coef | BC 0.386 | 903 | 5 | 4 | 2 | 1 | ✅ CORE-1 (gộp) |
| C06 | CLC mean > CNTT mean | Mann-Whitney, Welch | +0.106, p=0.0067, d=0.246 | 903 | 2 | 2 | 5 | **5** | ⚠️ CORE-2 (đảo khung) |
| C07 | Program giải thích 1.1% variance | η² | 0.0109 | 903 | 5 | 5 | 4 | 1 | ✅ **CORE-1** |
| C08 | Track giải thích 34.5% variance | η² | 0.3448 | 903 | 5 | 5 | 4 | 2 | ✅ **CORE-1** |
| C09 | Lớp ≡ track, không thêm thông tin | η², Kruskal-Wallis | 0.3522 vs 0.3448; p>0.18 | 903 | 5 | 5 | 3 | 1 | ✅ **CORE-8** |
| C10 | CNPM vs HTTT: effect lớn nhất | Cohen's d, Cliff's δ | d=1.538, δ=0.721 | 688 | 5 | 5 | 4 | **4** | ✅ **CORE-3** |
| C11 | Truncation ở CNPM → selection | min, overlap | min 2.43; 1/362 dưới median HTTT | 688 | 5 | 4 | 4 | 3 | ✅ **CORE-3** |
| C12 | Đảo dấu like-for-like | bootstrap CI, MW | −0.264 vs +0.433 | 865 | 5 | 4 | 5 | 2 | ✅ **CORE-2** |
| C13 | Mean CLC nằm giữa 2 track CNTT | weighted decomposition | break-even 0.724 | 903 | 5 | 5 | 4 | 2 | ✅ **CORE-2** |
| C14 | Chênh lệch tập trung ở đuôi dưới | decile diff | p10 +0.234, p50 +0.040 | 903 | 4 | 4 | 4 | 3 | ✅ **CORE-5** |
| C15 | CLC ít SV yếu hơn | band share, binomial | 1.40% vs 5.52% | 903 | 4 | 4 | 4 | 3 | ✅ **CORE-5** |
| C16 | E22TTNT mean cao nhất | mean + CI | 3.243, CI [3.140,3.346] | 38 | 3 | 2 | 5 | **5** | ⚠️ **SUP-1** (có rào) |
| C17 | Mã ngành tuyển sinh phân hoá CLC | Kruskal, Cohen's d | d=0.824, p<0.001 | 209 | 4 | 4 | 3 | 3 | ✅ **SUP-2** |
| C18 | 87% SV CLC không mang mã ngành CNTT | frequency | 186/215 | 215 | 5 | 5 | 3 | 2 | ✅ **SUP-3** |
| C19 | Tỷ lệ đủ đk CNPM vs HTTT | Fisher, risk ratio | 99.45% vs 83.54%, RR 29.8× | 690 | 5 | 5 | 5 | **4** | ✅ **CORE-6** |
| C20 | Đủ đk theo program: không khác biệt | chi², Fisher | p=0.39 | 905 | 3 | 5 | 3 | 1 | ✅ **SUP-4** |
| C21 | Không đủ đk ↔ CPA thấp | Cohen's d | 2.138 vs 2.844, d=1.806 | 903 | 3 | 5 | 3 | 2 | ✅ CORE-7 (gộp) |
| C22 | Nhưng đủ đk ≠ hàm của CPA | conditional freq | 13.4% ineligible ≥2.5 | 67 | 5 | 4 | 4 | 2 | ✅ **CORE-7** |
| C23 | 69.4% chạm trần 146 TC; rho=0.621 | Spearman | rho 0.621, p<10⁻⁹⁰ | 903 | 4 | 5 | 3 | **4** | ✅ **SUP-5** |
| C24 | Tương quan giữ nguyên trong nhóm đủ đk | Spearman | rho 0.546 | 836 | 4 | 5 | 2 | 3 | ✅ SUP-5 (gộp) |
| C25 | Tỷ lệ chạm trần theo track | proportion | 93.1% vs 48.5% | 905 | 4 | 5 | 3 | 3 | ✅ SUP-5 (gộp) |
| C26 | HTTT chiếm 92.5% decile thấp nhất | representation index | RI 2.55 | 903 | 4 | 5 | 4 | **4** | ✅ **SUP-6** |
| C27 | E22TTNT 47.4% ở top decile | representation index | RI 4.61 | 38 | 3 | 2 | 5 | **5** | ⚠️ SUP-1 (gộp) |
| C28 | Gini CPA rất thấp (0.0877) | Gini | 0.0877 | 903 | 4 | 5 | 2 | 2 | ✅ **SUP-7** |
| C29 | TTTN ~ CPA rho=0.416 | Spearman | rho 0.416 | 836 | 3 | 4 | 2 | 3 | ✅ **SUP-8** |
| C30 | Nơi sinh liên hệ với CPA | Kruskal, η² | η²=0.070, p<0.001 | 851 | 2 | 3 | 4 | **5** | ❌ **REJECT** |

---

## 4. Rejected insights

| ID | Insight | Lý do loại |
|---|---|---|
| **C30** | "Sinh viên sinh ở Hà Nội có CPA cao hơn (2.932 vs 2.739)" | **Cực kỳ dễ bị hiểu sai** thành phát biểu về năng lực theo vùng miền. η² chỉ 0.070. Nơi sinh gần như chắc chắn tương quan với điều kiện kinh tế - xã hội, chất lượng giáo dục phổ thông và cả việc chọn track — không có biến nào trong số đó có trong dataset. Public interest cao nhưng risk = 5 và analytical value = 2. Giữ lại làm **ghi chú kỹ thuật** (SUP-9) chứ không publish thành insight. |
| — | "Cohort differences" | Không thực hiện được: 899/905 cùng khóa 2022 (§1.5). |
| — | "Trends over time" | Không thực hiện được: dataset không có trục thời gian (§1.5). |
| — | "Chương trình CLC đào tạo tốt hơn / kém hơn" | **Causal claim** không được dataset hỗ trợ. Bị chặn bởi C12 (đảo dấu) và C07 (η²=0.011). Vi phạm quy tắc của brief. |
| — | "Ngành/track nào tốt nhất" | Causal claim. Bị chặn bởi C11 — CPA gần như chắc chắn là **tiêu chí phân track**, không phải kết quả của track. |
| — | "Phân phối CPA là bimodal" | **Kiểm tra và bác bỏ.** Sarle BC = 0.386 < 0.555; overlap coefficient giữa CNPM và HTTT = 0.395. Giả thuyết trực giác nhưng sai — đã loại nhờ tính toán. |
| — | "So sánh E22HTTT vs E22TTNT" | n = 40 và 38. Sau khi so sánh nhiều cặp, không có cặp nào sống sót hiệu chỉnh đa so sánh. |
| — | "Lớp X là lớp tốt nhất" | C09 bác bỏ: trong mọi track, Kruskal-Wallis giữa các lớp đều p > 0.18. Chênh lệch giữa các lớp cùng track (0.047–0.118) nhỏ hơn sai số. Đây là **noise, không phải signal**. |
| — | "Sinh viên tích lũy nhiều tín chỉ hơn thì CPA cao hơn" | Đúng về mặt tương quan (rho=0.621) nhưng **reverse-causality rõ ràng**: CPA thấp → trượt môn → ít tín chỉ tích lũy. Giữ lại dưới dạng mô tả cấu trúc (SUP-5), không dưới dạng quan hệ. |
| — | "Trường/khoa nào đào tạo tốt hơn" | Ngoài scope hoàn toàn — dataset chỉ có CNTT và CNTT CLC. |
| — | Off-cohort B21 (n=6), `N22*` (n=2), outlier riêng lẻ | Sample size quá nhỏ; ngoài ra là point-disclosure risk theo Phase 1 §7. |

---

## 5. Core insights (8)

---

### CORE-1 — Chương trình đào tạo gần như không giải thích được CPA; track mới là cấu trúc thật

> **Trong dataset này, việc một sinh viên thuộc CNTT hay CNTT CLC giải thích 1.1% phương sai CPA. Việc họ thuộc track nào giải thích 34.5% — gấp hơn 30 lần.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | η²(program) = **0.0109** · η²(track) = **0.3448** · η²(class) = 0.3522 · tỷ lệ = **31.6×** |
| **Calculation method** | One-way variance decomposition trên CPA: η² = SSB/(SSB+SSW), với SSB = Σ nᵢ(x̄ᵢ − x̄)², SSW = Σ Σ (x − x̄ᵢ)². Tính riêng cho từng biến phân nhóm. |
| **Source data** | `cpa` (từ `Điểm TBCTL`), `program` (derive từ `Mã lớp`[0]), `track_label` (derive từ `Mã lớp` bỏ hậu tố số) |
| **Sample size** | n = 903 (2 dòng thiếu CPA bị loại khỏi phép tính này) |
| **Caveat** | η² là thước đo **mô tả** mức độ phân tách nhóm, không phải hiệu ứng nhân quả. Con số 34.5% của track phần lớn phản ánh **cách sinh viên được phân vào track** (xem CORE-3), không phải tác động của track. Bổ sung: phân phối gộp **không** bimodal (Sarle BC = 0.386; overlap coefficient CNPM/HTTT = 0.395) — nghĩa là cấu trúc hai track **bị che khuất hoàn toàn** khi nhìn biểu đồ tổng, đây chính là lý do insight này quan trọng. |
| **Recommended visualization** | Horizontal bar chart xếp hạng η² của 8 biến (§1.4), trục x 0–0.40. Kèm một small-multiple: cùng một histogram CPA vẽ 2 lần — (a) tô màu theo program → gần như đồng nhất; (b) tô màu theo track → tách rõ. Đây là cặp hình thuyết phục nhất của cả dashboard. |

---

### CORE-2 — "CLC cao hơn CNTT" đảo dấu khi so sánh cùng chuyên ngành

> **So gộp: CLC cao hơn +0.106. So cùng chuyên ngành: CLC thấp hơn 0.264 ở CNPM, nhưng cao hơn 0.433 ở HTTT. Dấu của "chênh lệch CLC" phụ thuộc vào nhóm đối chứng được chọn.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | Gộp: CLC 2.8720 vs CNTT 2.7663 → **+0.1057**, 95% CI [+0.0436, +0.1688], Mann-Whitney p = 0.0067, d = 0.246<br>CNPM: E22CNPM 2.7560 vs D22CNPM 3.0199 → **−0.2639**, 95% CI [−0.3282, −0.1982], d = −0.861, p = 6.5×10⁻¹⁴<br>HTTT: E22HTTT 2.9173 vs D22HTTT 2.4847 → **+0.4325**, 95% CI [+0.2998, +0.5666], d = +1.066, p = 1.2×10⁻⁸ |
| **Calculation method** | Mann-Whitney U hai phía + Welch t-test; Cohen's d với pooled SD; 95% CI của hiệu trung bình bằng bootstrap 10,000 lần lặp (seed 42). Ghép cặp theo hậu tố tên track (`CNPM` ↔ `CNPM`, `HTTT` ↔ `HTTT`). |
| **Source data** | `cpa`, `program`, `track_label` |
| **Sample size** | Gộp: 688 CNTT / 215 CLC. Cặp CNPM: 362 / 137. Cặp HTTT: 326 / 40. |
| **Caveat** | ⚠️ `E22TTNT` (n=38) **không có track đối ứng** bên CNTT nên không ghép cặp được — 17.7% nhóm CLC nằm ngoài phép so sánh này. Cặp HTTT chỉ có n=40 phía CLC. Quan trọng nhất: **không** được đọc ngược thành "CLC dạy kém hơn ở CNPM". Cả hai chiều đều là chênh lệch mô tả giữa các nhóm có thành phần đầu vào khác nhau. Riêng con số gộp p = 0.0067 **không sống sót** hiệu chỉnh Bonferroni cho ~20 phép so sánh (ngưỡng 0.0025) — thêm một lý do không nên dựa vào nó. |
| **Recommended visualization** | Slope chart / dumbbell 2 dòng: dòng "CNPM" nối D22CNPM→E22CNPM (dốc xuống), dòng "HTTT" nối D22HTTT→E22HTTT (dốc lên), kèm error bar 95% CI. Đặt cạnh một thanh đơn "so gộp: +0.106" để người xem thấy ngay con số gộp che giấu điều gì. |

---

### CORE-3 — Khác biệt CPA lớn nhất trong dataset nằm giữa hai track của **cùng một** ngành, và có dấu hiệu rõ là do phân track

> **D22CNPM và D22HTTT đều là 100% sinh viên ngành CNTT, cùng khóa. Chênh lệch CPA giữa hai track là 0.535 điểm (d = 1.54) — lớn hơn mọi khác biệt khác trong dataset. Nhưng phân phối cho thấy đây gần như chắc chắn là hệ quả của cách phân track, không phải kết quả của việc học ở track đó.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | D22CNPM 3.0199 (n=362, sd 0.2881) vs D22HTTT 2.4847 (n=326, sd 0.4042) → chênh **+0.5352**<br>Cohen's d = **1.538** · Cliff's δ = 0.721 → P(CNPM > HTTT) = **0.860** · Mann-Whitney p = 5.1×10⁻⁶⁰<br>**Bằng chứng truncation:** min của CNPM = **2.43**; **0/362** sinh viên CNPM dưới ngưỡng đó; chỉ **1/362 (0.28%)** dưới median của HTTT; trong khi **52.5%** sinh viên HTTT nằm trên min của CNPM.<br>η²(track \| trong nội bộ CNTT) = **0.3717** |
| **Calculation method** | Cohen's d (pooled SD); Cliff's delta = (#{a>b} − #{a<b})/(nₐ·n_b); overlap coefficient qua histogram bin 0.05. Kiểm tra truncation bằng cách so min/median chéo giữa hai nhóm. |
| **Source data** | `cpa`, `track_label`, `admission_major_code` (xác nhận cả 690/690 đều là mã ngành CNTT: 686 × `B22DCCN` + 4 × `B21DCCN`) |
| **Sample size** | n = 688 có CPA (362 + 326) trên 690 dòng |
| **Caveat** | 🔴 **Đây là caveat quan trọng nhất của toàn dự án.** Việc đuôi dưới của CNPM bị cắt sắc ở 2.43 trong khi HTTT trải xuống 1.65 là dấu hiệu kinh điển của **phân chuyên ngành theo xếp hạng CPA**. Nếu đúng vậy thì CPA là **biến đầu vào** của việc phân track, và mọi so sánh CPA giữa hai track là **circular** — giải thích kết quả bằng chính thứ đã tạo ra nhóm. Cơ chế phân track **chưa được xác nhận** (câu hỏi mở #2 của Phase 1). Cho đến khi có xác nhận, insight này phải được trình bày như **một quan sát về cấu trúc dữ liệu**, tuyệt đối không như đánh giá hai chuyên ngành. |
| **Recommended visualization** | Overlapping density / ridgeline hai track trên cùng trục CPA, kẻ một đường dọc đứt tại 2.43 với annotation "không sinh viên CNPM nào dưới ngưỡng này". Hình này tự nó truyền tải bằng chứng selection mà không cần khẳng định nhân quả. |

---

### CORE-4 — Chân dung thống kê của CPA: tập trung dày ở dải Khá, đỉnh trên rất mỏng

> **Mean 2.79, median 2.79, sd 0.43. 76.7% đạt Khá trở lên, nhưng chỉ 19.6% đạt Giỏi trở lên và 2.2% Xuất sắc. Không sinh viên nào đạt 4.0; CPA cao nhất là 3.72.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | mean **2.7915** (95% CI [2.7631, 2.8201]) · median **2.7900** · sd **0.4322** · variance 0.1868 · Q1 2.52 / Q3 3.11 · **IQR 0.59** · min 1.40 / max 3.72 · skew −0.2391 · excess kurtosis −0.2606<br>Ngưỡng: ≥2.0 → 95.46% · ≥2.5 → **76.74%** · ≥3.0 → 34.33% · ≥3.2 → **19.60%** · ≥3.6 → **2.21%** (n=20) · <2.0 → **4.54%** (n=41) |
| **Calculation method** | Thống kê mô tả chuẩn (ddof=1). CI của mean/median bằng bootstrap 10,000 lần (seed 42). CI của tỷ lệ bằng binomial exact (Clopper-Pearson). Bands theo thang phân loại 4.0. |
| **Source data** | `cpa` |
| **Sample size** | n = 903 |
| **Caveat** | ⚠️ Con số này mô tả **sinh viên đã đi được đến bước xét ĐATN**, không phải toàn bộ khóa tuyển sinh 2022. Sinh viên thôi học/buộc thôi học không có trong dataset (Phase 1 §1.3), nên đuôi dưới bị cắt và **mọi giá trị trung bình đều lệch cao** so với cohort thật. Ngoài ra mean 2.79 là giá trị của một **hỗn hợp hai track rất khác nhau** — dùng nó làm "mức chuẩn" cho một sinh viên cụ thể là sai (xem CORE-1). |
| **Recommended visualization** | Histogram CPA bin 0.1 (dữ liệu bin đã có sẵn) chồng đường KDE, kèm marker dọc cho median và Q1/Q3. Bên cạnh: stacked bar 100% cho 5 band xếp loại, ghi rõ n từng band. |

---

### CORE-5 — Khác biệt của CLC nằm ở việc **ít sinh viên yếu**, không phải ở việc có nhiều sinh viên xuất sắc hơn

> **Chênh lệch CLC–CNTT là +0.234 ở phân vị 10, nhưng chỉ +0.040 ở trung vị và −0.010 ở đỉnh. Tỷ lệ dưới 2.0 là 1.40% ở CLC so với 5.52% ở CNTT.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | Chênh lệch theo decile (CLC − CNTT): p10 **+0.234** · p20 +0.160 · p30 +0.100 · p40 +0.070 · **p50 +0.040** · p60 +0.020 · p70 +0.058 · p80 +0.070 · p90 +0.146 · **p100 −0.010**<br>Band <2.00: CLC **1.40%** (3/215) vs CNTT **5.52%** (38/688)<br>Band ≥3.60: CLC 4.19% (9/215) vs CNTT 1.60% (11/688)<br>Bottom-decile rate: CLC **3.26%** vs CNTT **12.46%**<br>sd: CLC 0.4015 vs CNTT 0.4386 (Levene p = 0.0614) |
| **Calculation method** | Quantile-difference profile: tính cùng bộ decile cho từng nhóm rồi lấy hiệu. Band share bằng `pd.cut` với ngưỡng [0, 2.0, 2.5, 3.2, 3.6, 4.0]. Bottom decile = CPA ≤ p10 toàn nhóm (2.23). Levene test (center='median') cho đồng nhất phương sai. |
| **Source data** | `cpa`, `program` |
| **Sample size** | 688 CNTT / 215 CLC |
| **Caveat** | ⚠️ Insight này mô tả **hình dạng** của chênh lệch, và nó **chồng lấn với CORE-2**: một phần lớn hiệu ứng "ít sinh viên yếu" đến từ việc track HTTT chỉ chiếm **18.6%** nhóm CLC (40/215) nhưng **47.5%** nhóm CNTT (328/690) — mà HTTT là nơi tập trung đuôi dưới (SUP-6). Không được diễn giải là "CLC nâng đỡ sinh viên yếu tốt hơn". Levene p = 0.0614 nằm sát ngưỡng → khác biệt phương sai **không** đạt mức có ý nghĩa thông thường. Ở band ≥3.60 n chỉ là 9 và 11 → tỷ lệ 4.19% vs 1.60% có sai số rất rộng, không nên nhấn mạnh. |
| **Recommended visualization** | Quantile-difference plot: trục x là phân vị 0→100, trục y là hiệu CPA (CLC − CNTT), có đường zero. Hình này cho thấy ngay đường cong cao ở hai đầu và gần zero ở giữa. Kèm cặp box plot có notch. |

---

### CORE-6 — Tỷ lệ đủ điều kiện làm ĐATN chênh lệch giữa các track lớn hơn nhiều so với giữa hai chương trình

> **D22CNPM: 99.45% đủ điều kiện. D22HTTT: 83.54%. Nguy cơ không đủ điều kiện ở HTTT cao gấp 29.8 lần. Trong khi đó, chênh lệch giữa CNTT và CNTT CLC (91.88% vs 93.95%) không đạt ý nghĩa thống kê.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | D22CNPM **99.45%** (360/362, CI [98.02, 99.93]) · E22HTTT **100%** (40/40) · E22TTNT **100%** (38/38) · E22CNPM **90.51%** (124/137, CI [84.32, 94.85]) · D22HTTT **83.54%** (274/328, CI [79.07, 87.38])<br>χ² qua 5 track = 69.205, p = 3.3×10⁻¹⁴, **Cramér's V = 0.2765**<br>CNPM vs HTTT: chênh **+15.91 pp**, Fisher exact p = 1.8×10⁻¹⁶, **risk ratio (không đủ đk) = 29.8×**<br>Theo program: 91.88% vs 93.95%, χ² p = **0.3946**, Fisher p = 0.3782 → **không có ý nghĩa** |
| **Calculation method** | `eligible_for_thesis` = (`Ghi chú` == `Làm ĐATN`). Tỷ lệ kèm CI binomial exact. χ² test of independence; Fisher exact cho bảng 2×2; Cramér's V = √(χ²/n). Risk ratio = (1−p_HTTT)/(1−p_CNPM). |
| **Source data** | `ghi_chu` → `eligible_for_thesis`, `track_label`, `program` |
| **Sample size** | n = 905 (đầy đủ — cột này không có missing) |
| **Caveat** | ⚠️ Risk ratio 29.8× nghe rất lớn nhưng xuất phát từ **mẫu số cực nhỏ**: chỉ 2 sinh viên CNPM không đủ điều kiện. Với n=2, ước lượng này cực kỳ không ổn định — nên trình bày bằng **chênh lệch điểm phần trăm (15.91 pp)** thay vì risk ratio. E22HTTT và E22TTNT đạt 100% nhưng n chỉ 40 và 38, CI dưới lần lượt là 91.19% và 90.75% — **không** được nói "hoàn hảo". Và như CORE-3, sự khác biệt này rất có thể phản ánh cách phân track chứ không phải chất lượng track. |
| **Recommended visualization** | Horizontal bar chart tỷ lệ đủ điều kiện theo 5 track, có error bar CI 95%, trục x bắt đầu từ 75% (không từ 0 — nhưng phải ghi chú rõ trục bị cắt). Thêm một dòng đối chiếu "theo program: không khác biệt (p=0.39)" để chống lại khung so sánh sai. |

---

### CORE-7 — Điều kiện làm ĐATN không phải là hàm của CPA

> **Sinh viên không đủ điều kiện có CPA thấp hơn rõ rệt (2.14 vs 2.84). Nhưng 13.4% trong số họ có CPA ≥ 2.5, và người cao nhất đạt 3.37 — cao hơn 91.8% toàn bộ nhóm. Ngược lại, 125 sinh viên đủ điều kiện có số tín chỉ nằm trong đúng dải mà người khác bị loại.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | CPA: không đủ đk **2.1381** (n=67, sd 0.3916) vs đủ đk **2.8439** (n=836, sd 0.3907) → chênh 0.7058, **d = 1.806**, Mann-Whitney p = 4.9×10⁻²⁷<br>Nhưng: **9/67 (13.4%)** sinh viên không đủ đk có CPA ≥ 2.5 · **3/67** có CPA ≥ 3.0 · **max = 3.37**<br>Dải chồng lấn tín chỉ: đủ đk min = **69**, không đủ đk max = **140**. Trong dải 69–140 có **154** sinh viên: **125 đủ điều kiện, 29 không**.<br>η²(eligibility) trên CPA = 0.1834 |
| **Calculation method** | So sánh CPA hai nhóm bằng Mann-Whitney + Cohen's d. Xác định dải chồng lấn bằng min(credits \| eligible) và max(credits \| ineligible), rồi đếm cả hai nhóm trong dải đó. |
| **Source data** | `cpa`, `credits` (từ `Số TCTL`), `eligible_for_thesis` |
| **Sample size** | 903 cho phần CPA (67 ineligible có CPA, 2 thiếu); 905 cho phần tín chỉ |
| **Caveat** | ⚠️ Insight này nói về **giới hạn của dữ liệu**, không phải về sinh viên. Kết luận đúng là: **tiêu chí xét ĐATN phụ thuộc vào yếu tố không có trong dataset** (nhiều khả năng là các điều kiện học phần cụ thể, chứng chỉ, hoặc quy định riêng). **Không được reverse-engineer quy tắc xét duyệt** từ dữ liệu này (Phase 1, W7). Cũng không được kết luận việc xét duyệt "thiếu nhất quán" — chúng ta chỉ đơn giản không quan sát được biến quyết định. Nhóm ineligible n=67 nhỏ và nhạy cảm về privacy: **không** breakdown theo lớp. |
| **Recommended visualization** | Scatter plot CPA (y) × tín chỉ tích lũy (x), màu theo trạng thái đủ/không đủ điều kiện, có jitter nhẹ. Highlight vùng chữ nhật 69–140 tín chỉ để lộ vùng chồng lấn. Đây là hình duy nhất trong bộ nên dùng scatter cấp cá nhân — và vì thế cần bỏ mọi tooltip định danh. |

---

### CORE-8 — Lớp không phải là đơn vị phân tích có ý nghĩa; track mới là

> **18 lớp trông như 18 nhóm khác nhau, nhưng trong cùng một track thì các lớp không phân biệt được về mặt thống kê. Chênh lệch mean giữa các lớp cùng track chỉ 0.047–0.118, và Kruskal-Wallis cho p > 0.18 ở cả ba track có nhiều lớp.**

| Mục | Nội dung |
|---|---|
| **Exact metric** | η²(class, k=18) = **0.3522** vs η²(track, k=5) = **0.3448** → thêm 13 nhóm chỉ tăng **0.0074**<br>Kruskal-Wallis trong nội bộ track: D22CNPM (k=6) H=7.454 **p=0.1890** · D22HTTT (k=6) H=3.996 **p=0.5499** · E22CNPM (k=4) H=0.366 **p=0.9473**<br>Biên độ mean giữa các lớp cùng track: D22CNPM 2.963–3.082 (**0.118**) · D22HTTT 2.433–2.543 (**0.110**) · E22CNPM 2.741–2.788 (**0.047**)<br>Để so sánh, biên độ giữa các track: **0.810** (2.433 → 3.243) |
| **Calculation method** | Kruskal-Wallis H test giữa các `class_code` trong từng `track_label`. η² so sánh giữa hai cách phân nhóm lồng nhau. SE của mean từng lớp = sd/√n để dựng CI 95%. |
| **Source data** | `cpa`, `class_code`, `track_label` |
| **Sample size** | 903 tổng; mỗi lớp n = 32–62 |
| **Caveat** | ⚠️ "Không phân biệt được về mặt thống kê" ≠ "hoàn toàn giống nhau". Với n ≈ 55/lớp, power để phát hiện khác biệt nhỏ là thấp — đây là bằng chứng **thiếu bằng chứng về khác biệt**, không phải bằng chứng về sự đồng nhất. Tuy vậy kết luận thực hành vẫn vững: **không nên xếp hạng lớp**, vì chênh lệch quan sát được nhỏ hơn sai số và sẽ bị người đọc hiểu thành "lớp này giỏi hơn lớp kia". `E22HTTT` và `E22TTNT` mỗi track chỉ có 1 lớp nên không kiểm định được. |
| **Recommended visualization** | Caterpillar plot: 18 lớp trên trục y sắp theo mean, chấm mean + thanh CI 95%, tô màu theo track. Người xem sẽ thấy các CI trong cùng một track chồng lên nhau gần như hoàn toàn, còn giữa các track thì tách rời. **Cố ý không** làm bảng xếp hạng lớp. |

---

## 6. Supporting insights (10)

| ID | Insight | Metric | N | Caveat bắt buộc đi kèm |
|---|---|---|---:|---|
| **SUP-1** | E22TTNT là track có CPA cao nhất trong dataset, và tập trung ở nhóm đầu | mean **3.2429** (CI [3.140, 3.346]); **47.4%** nằm trong decile cao nhất, representation index **4.61**; 0 sinh viên ở decile thấp nhất | **38** | 🔴 n = 38, một lớp duy nhất, không có track đối ứng bên CNTT. Không so sánh với bất kỳ track nào khác. Không suy ra điều gì về ngành TTNT nói chung. Đây là quan sát về **một lớp cụ thể của một khóa**. |
| **SUP-2** | Trong nội bộ CLC, mã ngành tuyển sinh phân hoá CPA mạnh hơn cả track | DCCN 3.114 (n=29) · DCKH 3.110 (n=4) · DCAT 3.062 (n=34) · DCDT 2.800 (n=50) · DCVT 2.776 (n=96). Nhóm IT-family (DCCN+DCAT) **3.086** vs Telecom/Electronics (DCVT+DCDT) **2.784**, chênh 0.302, **d = 0.824**, Kruskal p = 2×10⁻⁵ | 209 | Mã ngành tuyển sinh phản ánh điểm đầu vào và lựa chọn ban đầu — không quan sát được trong dataset. Đây là **bằng chứng về khác biệt thành phần đầu vào**, không phải về đào tạo. DCKH n=4, DCCI/DCDK n=1 → loại khỏi mọi so sánh. |
| **SUP-3** | Nhóm CNTT CLC có thành phần đầu vào rất khác nhóm CNTT chuẩn | **186/215 (86.5%)** sinh viên CLC mang mã ngành tuyển sinh không phải CNTT: DCVT 96 (44.7%), DCDT 50 (23.3%), DCAT 34 (15.8%). Nhóm CNTT chuẩn: **690/690 (100%)** mang mã ngành CNTT | 905 | Đây là **fact về cấu trúc dữ liệu**, độ tin cậy tuyệt đối. Là lý do nền tảng khiến CORE-2 xảy ra. Cần trình bày **trước** bất kỳ so sánh hai chương trình nào. |
| **SUP-4** | Tỷ lệ đủ điều kiện ĐATN **không** khác biệt giữa hai chương trình | CNTT 91.88% (634/690) vs CLC 93.95% (202/215); χ² p = **0.3946**, Fisher p = 0.3782 | 905 | Một **null result** có giá trị: nó chặn trước diễn giải sai "CLC có tỷ lệ tốt nghiệp cao hơn". Trình bày như bằng chứng về sự *không* khác biệt, kèm ghi chú về power. |
| **SUP-5** | Cấu trúc trần tín chỉ: phần lớn sinh viên chạm trần 146, phần còn lại phân tán rộng | **69.4%** (628/905) đạt đúng 146 TC; 78.0% ≥143. Spearman CPA–tín chỉ **rho = 0.621** (p < 10⁻⁹⁰); chỉ trong nhóm đủ đk rho = 0.546. Tỷ lệ chạm trần theo track: CNPM **93.1%**, TTNT 84.2%, E22HTTT 57.5%, E22CNPM 56.2%, HTTT **48.5%** | 905 | 🔴 **Reverse causality rõ ràng** — CPA thấp dẫn tới trượt môn dẫn tới ít tín chỉ. Tuyệt đối không trình bày như "tích lũy nhiều tín chỉ giúp CPA cao". Diễn giải đúng: hai biến này đo **cùng một hiện tượng tiến độ học tập** từ hai góc. |
| **SUP-6** | Nhóm CPA thấp nhất tập trung áp đảo ở một track | D22HTTT chiếm **36.2%** cohort nhưng **92.5%** của decile thấp nhất (86/93); representation index **2.55**. D22CNPM chiếm 40.0% cohort nhưng **0%** decile thấp nhất | 903 | Đọc cùng CORE-3: nếu track được phân theo CPA thì đây là **hệ quả cơ học của cách phân nhóm**, không phải phát hiện về sinh viên HTTT. Rủi ro stigma cao → cần đặt cạnh CORE-3 trong cùng một khung, không tách rời. |
| **SUP-7** | CPA là thang bị nén — chênh lệch tuyệt đối nhỏ nhưng thứ hạng thay đổi nhiều | **Gini = 0.0877** toàn nhóm (CNPM 0.0546 · TTNT 0.0558 · E22CNPM 0.0693 · E22HTTT 0.0794 · HTTT 0.0910). Decile cao nhất giữ 12.35% tổng "khối lượng CPA", decile thấp nhất 7.37% (chuẩn bình đẳng = 10%) | 903 | Gini vốn dùng cho biến có zero tự nhiên (thu nhập); với CPA nó chỉ có ý nghĩa **so sánh tương đối giữa các nhóm**, không phải giá trị tuyệt đối. Ích lợi chính: nhắc người đọc rằng chênh lệch 0.1 điểm CPA là **nhỏ về mặt thang đo** nhưng có thể lớn về thứ hạng. |
| **SUP-8** | Điểm TTTN tương quan trung bình với CPA và gần như bằng nhau giữa hai chương trình | Spearman rho = **0.416** (n=836, p<10⁻⁴). CPA trung bình theo bậc: A+ 2.957 (n=549) · A 2.707 (n=104) · B+ 2.700 (n=103) · B 2.486 (n=49) · D 2.176 (n=12). Tỷ lệ A+: CNTT **65.3%** vs CLC **66.8%** | 836 | ⚠️ Ý nghĩa đầy đủ của `TTTN` vẫn **UNCONFIRMED** (Phase 1, W8) — chỉ mô tả là "một điểm chữ liên quan điều kiện ĐATN". 53 giá trị thiếu là **MNAR** (100% rơi vào nhóm không đủ đk) nên phân tích chỉ chạy trên nhóm đủ đk. Bậc B (n=49) có mean thấp hơn cả C+ (n=6) → thang không đơn điệu hoàn hảo, không dùng làm biến thứ bậc chặt. |
| **SUP-9** | Dữ liệu có liên hệ giữa nơi sinh và CPA, nhưng **không đủ điều kiện để publish** | Hà Nội 2.932 (n=245) vs còn lại 2.739 (n=658), Mann-Whitney p < 0.001; Kruskal qua 14 tỉnh n≥20: H=52.06, p<0.001; nhưng **η² chỉ 0.070** | 851 | 🔴 **Đã REJECT khỏi output công khai** (§4). Ghi lại ở đây để phase sau không "phát hiện lại" và vô tình publish. Lý do: risk of misinterpretation = 5 (dễ thành phát biểu về vùng miền), confounder không quan sát được, và 15 tỉnh có n < 10 tạo small-cell disclosure risk. |
| **SUP-10** | Hai chiều phân tích mà brief yêu cầu **không tồn tại** trong dataset | `intake_year`: 2022 → 899, 2021 → 6 (η² = 0.0013). Không có cột thời gian nào. Chỉ 2 outlier theo hàng rào IQR (cả hai đều là sinh viên không đủ đk với 24 và 6 tín chỉ — hợp lệ và giải thích được, **không loại bỏ**) | 905 | Cần nêu rõ ràng trong sản phẩm cuối để người xem không kỳ vọng có biểu đồ xu hướng. Việc **không có** trend là một thông tin, không phải một thiếu sót cần che giấu. |

**Cập nhật về SUP-9 (sau launch):** chủ dữ liệu yêu cầu bổ sung lại insight nơi sinh, lần này ở dạng khác với candidate C30 ban đầu — thay vì một con số mean gộp ("Hà Nội cao hơn"), hiển thị **count và tỷ trọng-trong-chính-tỉnh** theo 3 dải CPA (coarsen từ `CLASSIFICATION_BANDS`: Dưới trung bình / Khá / Giỏi trở lên — 5 dải gốc để lại 0-1 tỉnh đạt ngưỡng riêng mỗi dải). Cách trình bày này buộc người đọc thấy đồng thời "tỉnh nào đông nhất" (phần lớn do quy mô tổng thể — Hà Nội đông nhất dataset) và "tỉnh nào có tỷ trọng cao/thấp bất thường trong tỉnh mình" (Hà Nội 29.5% ở dải cao nhất so với 8–16% của Thanh Hóa/Nghệ An/Nam Định) — đúng phần thiếu sót khiến C30 bị reject. Ngưỡng suppression giữ nguyên hai lớp: tỉnh phải có ≥20 sinh viên toàn dữ liệu (`MIN_GROUP_SIZE_FOR_MEAN`) mới được liệt kê, và ≥10 trong chính dải đó (`MIN_GROUP_SIZE`) mới hiện riêng — còn lại gộp "Khác". Rủi ro hiểu sai (confounder kinh tế-xã hội không quan sát được) **vẫn còn nguyên** và được nêu ở caveat critical của section — quyết định publish là của chủ dữ liệu, không phải kết luận rằng rủi ro đã biến mất. Xem `pipeline/s4_metrics.py::compute_birthplace_bands`, `site/src/sections/06b-Birthplace.astro`.

---

## 7. Statistical caveats

### 7.1 Giới hạn về thiết kế nghiên cứu

1. **Không có bất kỳ điều kiện nào cho suy luận nhân quả.** Observational, cross-sectional, một khóa, một thời điểm. Không randomization, không baseline, không biến công cụ, không thiết kế trước-sau. Mọi phát biểu phải ở dạng *"trong dataset này, nhóm A có median CPA cao hơn nhóm B"*.
2. **Selection into track là confounder trung tâm.** Bằng chứng truncation ở CORE-3 cho thấy CPA rất có thể là **tiêu chí phân track**. Khi đó, so sánh CPA giữa các track là circular. Cơ chế phân track chưa được xác nhận → đây là ẩn số lớn nhất còn lại.
3. **Selection into program cũng là confounder.** SUP-3: 86.5% sinh viên CLC đến từ mã ngành tuyển sinh khác. Hai nhóm khác nhau ở đầu vào trước khi khác nhau ở bất cứ điều gì khác.
4. **Survivorship filtering.** Dataset là danh sách xét ĐATN, không phải cohort tuyển sinh. Sinh viên thôi học không xuất hiện → đuôi dưới bị cắt, mọi mean lệch cao. Không biết được tỷ lệ rời bỏ theo track — nếu HTTT có tỷ lệ rời bỏ cao hơn thì khoảng cách thật giữa các track còn **lớn hơn** con số quan sát được.
5. **Simpson's paradox đã được xác nhận là hiện hữu**, không phải rủi ro lý thuyết: CORE-2 cho thấy dấu của so sánh đảo chiều khi phân tầng. Mọi so sánh gộp trong dự án này phải được kiểm tra lại theo tầng track trước khi công bố.

### 7.2 Giới hạn về suy luận thống kê

6. **Multiple comparisons.** Phase này chạy khoảng 20 kiểm định. Với Bonferroni α = 0.05/20 = 0.0025: các kết quả **sống sót** gồm CNPM vs HTTT (p=5×10⁻⁶⁰), like-for-like cả hai cặp (p=6.5×10⁻¹⁴ và 1.2×10⁻⁸), eligibility theo track (p=3.3×10⁻¹⁴), CPA theo eligibility (p=4.9×10⁻²⁷), CLC theo mã ngành (p=2×10⁻⁵). Kết quả **không sống sót**: so sánh gộp CLC vs CNTT (p=0.0067) và Levene về phương sai (p=0.0614). Đây là lý do bổ sung để không đặt so sánh gộp làm headline.
7. **Ecological fallacy.** Mọi thống kê ở mức track/lớp mô tả **nhóm**, không phải cá nhân. Với Cliff's δ = 0.721 ở cặp CNPM/HTTT, vẫn có 14% cặp ngẫu nhiên mà sinh viên HTTT có CPA cao hơn sinh viên CNPM.
8. **Sample size không đồng đều.** E22HTTT (n=40) và E22TTNT (n=38) nhỏ hơn D22CNPM (n=362) gần 10 lần. CI của hai nhóm nhỏ rộng gấp ~3 lần. Mọi biểu đồ **phải hiển thị n** và **phải hiển thị CI**.
9. **Power thấp cho hiệu ứng nhỏ.** Các null result (CORE-8, SUP-4) là "không tìm thấy bằng chứng về khác biệt", không phải "chứng minh không có khác biệt".
10. **η² là mô tả, không phải phân rã nhân quả.** η²(track) = 0.345 nói rằng track *phân tách* dữ liệu tốt, không nói track *gây ra* CPA.

### 7.3 Giới hạn về dữ liệu

11. **CPA làm tròn 2 chữ số thập phân** → có ties, ảnh hưởng nhẹ tới các thống kê thứ hạng. Không đáng kể ở n=903.
12. **2 giá trị CPA thiếu là MNAR** (cả hai đều `Không đủ đk`, 0 tín chỉ). Đã loại khỏi phép tính CPA nhưng **giữ** trong dataset. n khác nhau theo metric: 905 (class, eligibility) / 903 (CPA) / 836 (TTTN).
13. **53 giá trị TTTN thiếu là MNAR** — 100% thuộc nhóm không đủ điều kiện. Không impute.
14. **Ý nghĩa `TTTN` chưa xác nhận** (Phase 1, W8) → SUP-8 phải kèm rào.
15. **Cơ chế phân track chưa xác nhận** (Phase 1, câu hỏi mở #2) → chặn CORE-3 và CORE-6 khỏi mọi diễn giải mạnh hơn mô tả.
16. **`N22DC*B` (n=2) và `B21DC*` (n=6)** giữ trong dataset với flag, loại khỏi mọi so sánh nhóm.

### 7.4 Giới hạn về phạm vi và quyền riêng tư

17. **Không generalize ra ngoài CNTT và CNTT CLC.** Dataset gốc chứa 1,118 dòng thuộc các ngành khác đã bị filter khỏi scope. Không kết luận về toàn bộ PTIT, toàn bộ khối kỹ thuật, hay bất kỳ ngành nào khác.
18. **Không generalize ra ngoài khóa 2022.** Một cohort duy nhất, không có cơ sở để nói về khóa trước hay khóa sau.
19. **Không breakdown nhóm không đủ điều kiện (n=69) theo lớp.** Trung bình ~4 người/lớp → point disclosure. Áp dụng ngưỡng suppression n < 10 của Phase 1 (F4).
20. **Không hiển thị min/max CPA ở mức lớp**, không tạo bảng xếp hạng lớp hay xếp hạng cá nhân. CORE-8 vừa là insight vừa là lý do kỹ thuật để không làm điều này.

---

## 8. Điều gì chuyển sang phase sau

**Đã chốt để trình bày:** 8 core + 10 supporting insights ở trên, mỗi cái kèm metric chính xác, n, caveat và gợi ý visualization.

**Nguyên tắc trình bày bắt buộc:**
- Mọi biểu đồ so sánh nhóm phải hiển thị **n** và **khoảng tin cậy**.
- Mọi so sánh CNTT vs CLC phải đặt cạnh phiên bản phân tầng theo track (CORE-2), không được đứng một mình.
- Không có bảng xếp hạng lớp, không có xếp hạng cá nhân, không có min/max cấp lớp.
- Ngôn ngữ mô tả: *"nhóm A có median CPA cao hơn trong dataset này"* — không bao giờ *"tốt hơn"*, *"dạy tốt hơn"*, *"chất lượng cao hơn"*.

**Vẫn chờ xác nhận từ phòng đào tạo** (kế thừa Phase 1 §11, nay còn 3 câu):
1. Cơ chế phân sinh viên vào `D22CNPM` vs `D22HTTT` — **chặn** diễn giải CORE-3 và CORE-6.
2. `TTTN` là viết tắt của gì — **chặn** đặt tên chính thức cho SUP-8.
3. Diện sinh viên của 3 mã `N22DC*B` — ảnh hưởng nhỏ (n=2 in-scope).

---

## Phụ lục — Tái lập

```
Loader:      cleaning rules A1-A4, B1, C1-C7, D1, E1-E4 của docs/data-audit.md
Scope:       ^(D22CNPM|D22HTTT|E22) trên cột Mã lớp  ->  905 rows
Program map: class_prefix 'E' -> CNTT CLC ; 'D' -> CNTT   (xác nhận bởi quy ước nhà trường)
Assertion:   0 <= CPA <= 4  (pass)
Bootstrap:   10,000 resamples, numpy default_rng(seed=42)
Môi trường:  Python 3.13.2 · pandas 3.0.1 · numpy 2.4.2 · scipy 1.17.1 · openpyxl 3.1.5
Ngày:        2026-09-11
```
