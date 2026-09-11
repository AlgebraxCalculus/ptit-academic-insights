# Data Audit — PTIT Academic Insights

**Source file:** `data/DS-SV-DK-DATN-D22-KY-THUAT.xlsx`
**Audit date:** 2026-09-11
**Status:** Source of truth cho các phase tiếp theo. Mọi giả định phân tích phải đối chiếu với tài liệu này.

> **Nguyên tắc của bản audit này:** chỉ ghi nhận những gì có evidence trực tiếp trong file. Những chỗ ý nghĩa cột/mã lớp không xác định được từ dữ liệu sẽ được đánh dấu rõ là **UNCONFIRMED** thay vì suy đoán.

---

## 1. Dataset overview

### 1.1 File & workbook

| Thuộc tính | Giá trị |
|---|---|
| Định dạng | `.xlsx` (Office Open XML), 166,837 bytes |
| Số sheet | **1** |
| Tên sheet | `Data` (visible) |
| Sheet chứa dữ liệu chính | `Data` — đây là sheet duy nhất |
| Header | Dòng 1 |
| Số dòng dữ liệu | **2,023** (dòng 2 → 2024) |
| Số cột thực | **11** (A → K) |
| `max_column` báo cáo bởi Excel | 255 (IU) — cột L→IU rỗng hoàn toàn, là artifact của autofilter |
| Merged cells | `C1:D1` (header `Họ tên` trải trên 2 cột) |
| AutoFilter | `A1:IU2024` |
| Defined names / comments / macro | Không có |
| Sheet ẩn | Không có |

### 1.2 Workbook metadata (docProps)

| Field | Giá trị |
|---|---|
| `dc:creator` | `HangDT-GV` |
| `cp:lastModifiedBy` | `Tran Thanh Thuy D22CN05` |
| `dcterms:created` | 2026-09-09T07:47:27Z |
| `dcterms:modified` | 2026-09-11T02:11:03Z |
| Application | Microsoft Excel 16.03 |

⚠️ Metadata chứa **tên người thật** (`lastModifiedBy`). Nếu file gốc được commit hoặc phân phối, đây là một PII leak vector độc lập với nội dung bảng.

### 1.3 Bản chất của dataset — **quan trọng**

Tên file (`DS-SV-DK-DATN`) cùng với cột `Ghi chú` (chỉ 2 giá trị: `Làm ĐATN` / `Không đủ đk`) và cột `Số TCTL` cho thấy đây **không phải một roster sinh viên tổng quát**, mà là **danh sách xét đăng ký Đồ án tốt nghiệp** tại một thời điểm.

Hệ quả: dataset chỉ chứa những sinh viên **còn tồn tại trong hệ thống đến thời điểm xét ĐATN**. Sinh viên đã thôi học, bị buộc thôi học, bảo lưu dài hạn, hoặc chuyển trường **không xuất hiện**. Đây là **survivorship-filtered population**, không phải cohort đầy đủ.

### 1.4 Scope: file rộng hơn phạm vi đã khai báo

Brief nêu dataset chỉ gồm lớp `D22CNPM*`, `D22HTTT*`, `E22*`. **Thực tế file chứa 42 mã lớp thuộc nhiều ngành kỹ thuật khác nhau.**

| Nhóm lớp | Số SV | Trong scope? |
|---|---:|---|
| D22CNPM01–06 | 362 | ✅ |
| D22HTTT01–06 | 328 | ✅ |
| E22CNPM01–04 | 137 | ✅ |
| E22HTTT | 40 | ✅ |
| E22TTNT | 38 | ✅ |
| **Tổng in-scope** | **905** | |
| D22VTMD01–05 | 257 | ❌ |
| D22CQAT01–04-B | 214 | ❌ |
| D22CQKH01–02-B | 128 | ❌ |
| D22TKDPT1–2 | 116 | ❌ |
| D22DTVM01–02 | 86 | ❌ |
| D22VTHI01–02 | 82 | ❌ |
| D22PTDPT1–2 | 80 | ❌ |
| D22DTMT01–02 | 78 | ❌ |
| D22VTVT | 40 | ❌ |
| D22XLTH | 36 | ❌ |
| D23DTMT01 | 1 | ❌ |
| **Tổng out-of-scope** | **1,118** | |

➡️ **Phase tiếp theo bắt buộc phải áp dụng scope filter tường minh.** Không được dùng 2,023 dòng làm mẫu số.

---

## 2. Data dictionary

Đánh giá trên **toàn bộ 2,023 dòng**. Cột `In-scope missing` tính trên 905 dòng in-scope.

| # | Column (header gốc) | Type lưu trữ | Type logic | Ý nghĩa | Evidence | Missing (full) | In-scope missing | Unique (full) | Analytical role |
|---|---|---|---|---|---|---:|---:|---:|---|
| A | `TT` | `int` | Ordinal | Số thứ tự dòng | Chạy liên tục 1→2023, không trùng, không ngắt quãng | 0 | 0 | 2,023 | ❌ Drop — artifact của file, không mang thông tin |
| B | `Mã SV` | `str` | Nominal ID | **Student identifier** | Unique 100%; pattern `[A-Z]\d{2}DC[A-Z]{2}\d{3}` | 0 | 0 | 2,023 | 🔑 Primary key → **phải hash/pseudonymize** |
| C | `Họ tên` | `str` | Nominal | Họ + tên đệm | Header merged C1:D1 | 0 | 0 | 926 | 🚫 **PII — drop** |
| D | *(không có header)* | `str` | Nominal | Tên | Nửa phải của merge `C1:D1`; ô D1 rỗng | 0 | 0 | 261 | 🚫 **PII — drop** |
| E | `Ngày sinh` | `str` | Date | Ngày sinh, `DD/MM/YYYY` | 2,023/2,023 khớp pattern `99/99/9999` | 0 | 0 | 468 | 🚫 **Quasi-identifier — drop** (tối đa giữ `birth_year`) |
| F | `Nơi sinh` | `str` | Nominal | Tỉnh/thành hoặc quốc gia nơi sinh | 48 giá trị: 44 tỉnh VN + `Lào`, `Liên Bang Nga`, `CHLB Đức` | 0 | 0 | 48 | ⚠️ Optional dimension — small cells, cần suppression |
| G | `Mã lớp` | `str` | Nominal | **Class identifier** | 42 giá trị; pattern `[DE]\d{2}<CODE>[\d]{0,2}` | 0 | 0 | 42 | ✅ Class dimension + nguồn duy nhất suy ra program/track |
| H | `TTTN` | `str` | Ordinal | Điểm chữ của một học phần/hoạt động TTTN | 9 giá trị đúng thang điểm chữ PTIT: `A+ A B+ B C+ C D+ D F` | **119** | 53 | 9 | ⚠️ Secondary outcome — **nghĩa đầy đủ UNCONFIRMED** |
| I | `Số TCTL` | `int` | Ratio | Số tín chỉ tích lũy | Max 146 (= 1,295 SV đạt trần); tương quan mạnh với `Ghi chú` | 1 | 0 | 120 | ✅ Progress/completeness measure |
| J | `Điểm TBCTL` | **`str`** ⚠️ | Ratio | **CPA** — điểm trung bình chung tích lũy, thang 4 | Range 1.25–3.79, đúng 2 chữ số thập phân | 3 (chuỗi rỗng) | 2 | 219 | 🎯 **Primary outcome variable** |
| K | `Ghi chú` | `str` | Binary | Kết luận xét điều kiện ĐATN | Chỉ 2 giá trị: `Làm ĐATN` (1,878) / `Không đủ đk` (145) | 0 | 0 | 2 | ✅ Eligibility outcome |

### 2.1 Mapping sang yêu cầu của brief

| Khái niệm brief yêu cầu | Có trong dataset? | Cột nguồn |
|---|---|---|
| Student identifier | ✅ Trực tiếp | `Mã SV` |
| Class | ✅ Trực tiếp | `Mã lớp` |
| **Major / Program** | ⚠️ **KHÔNG có cột nào** | Chỉ **derive được** từ `Mã lớp` + prefix `Mã SV` — xem §2.2 |
| **Cohort / Year** | ⚠️ Gần như hằng số | Derive từ 2 chữ số trong `Mã SV` (`B22…`) hoặc `Mã lớp` (`D22…`) |
| **CPA** | ✅ Trực tiếp | `Điểm TBCTL` |
| Metadata khác | ✅ | `Ngày sinh`, `Nơi sinh`, `TTTN`, `Số TCTL`, `Ghi chú` |

### 2.2 Cấu trúc mã — evidence

**Prefix `Mã SV`** (ký tự 1–7), toàn file:

| Prefix | n | Xuất hiện ở nhóm lớp |
|---|---:|---|
| `B22DCCN` | 714 | D22CNPM (360), D22HTTT (326), E22* (28) |
| `B22DCVT` | 474 | D22VTMD, D22VTHI, D22VTVT, E22* (96) |
| `B22DCDT` | 248 | D22DTMT, D22DTVM, D22XLTH, E22* (49) |
| `B22DCAT` | 247 | D22CQAT*, E22* (34) |
| `B22DCPT` | 193 | D22PTDPT*, D22TKDPT* |
| `B22DCKH` | 132 | D22CQKH*, E22* (4) |
| `B21DC*` | 11 | rải rác (khóa trước, học lại/chậm tiến độ) |
| `N22DC*` | 3 | mã 11 ký tự, kết thúc bằng `B` |
| `B23DCDT` | 1 | D23DTMT01 |

Quan sát: **prefix `Mã SV` ổn định theo ngành tuyển sinh; `Mã lớp` phản ánh lớp/chuyên ngành học tập.** Hai trục này **không trùng nhau** ở nhóm `E22`.

---

## 3. Data quality issues

### 🔴 CRITICAL

**C1 — Không tồn tại cột program/CLC. Phân nhóm "CNTT" vs "CNTT CLC" là một derived assumption, chưa được dữ liệu xác nhận.**
Không có cột nào trong 11 cột ghi chương trình đào tạo. Việc gán `E22* → CLC` hoàn toàn dựa vào quy ước bên ngoài file. **UNCONFIRMED.**

**C2 — Giả định "E22 = CNTT CLC" mâu thuẫn với cấu trúc `Mã SV` của chính nhóm E22.**
Trong 215 sinh viên lớp `E22*`, chỉ **28 (13.0%)** mang mã ngành CNTT (`B22DCCN`):

| `Mã SV` prefix | E22CNPM01 | E22CNPM02 | E22CNPM03 | E22CNPM04 | E22HTTT | E22TTNT | Tổng | % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `B22DCVT` | 15 | 16 | 11 | 22 | 20 | 12 | **96** | 44.7% |
| `B22DCDT` | 10 | 6 | 12 | 7 | 6 | 8 | **49** | 22.8% |
| `B22DCAT` | 2 | 7 | 7 | 2 | 6 | 10 | **34** | 15.8% |
| `B22DCCN` | 5 | 2 | 5 | 4 | 5 | 7 | **28** | 13.0% |
| `B22DCKH` | 0 | 0 | 0 | 0 | 3 | 1 | **4** | 1.9% |
| khác (`B21*`, `N22*`) | 2 | 1 | 1 | 0 | 0 | 0 | **4** | 1.9% |

➡️ `E22*` là các lớp **quy tụ sinh viên từ nhiều ngành tuyển sinh khác nhau** (VT, ĐT, ATTT, CNTT, KHMT). Gọi cả nhóm này là "CNTT CLC" là **không chính xác về mặt dữ liệu**. Bản chất thật của `E22` **UNCONFIRMED** — cần xác nhận từ phòng đào tạo trước khi đặt tên nhóm.

**C3 — `D22CNPM` và `D22HTTT` KHÔNG phải hai chương trình khác nhau, và khác biệt CPA giữa chúng gần như chắc chắn do selection.**
Cả **690/690** sinh viên hai nhóm này đều mang mã ngành CNTT (686 × `B22DCCN` + 4 × `B21DCCN`) → **cùng một ngành tuyển sinh**, chỉ khác lớp/chuyên ngành.

| Decile | D22CNPM (n=362) | D22HTTT (n=326) |
|---|---:|---:|
| min | **2.43** | 1.65 |
| p10 | 2.64 | 1.96 |
| p50 | 3.03 | 2.45 |
| p90 | 3.40 | 3.04 |
| max | 3.72 | 3.69 |

- CPA thấp nhất của toàn bộ CNPM là **2.43**; không một sinh viên CNPM nào dưới ngưỡng đó.
- Chỉ **1/362** sinh viên CNPM nằm dưới median của HTTT.
- Phân phối bị **truncate ở đuôi dưới** một cách sắc nét — dấu hiệu điển hình của **phân chuyên ngành theo xếp hạng CPA**.

➡️ Chênh lệch mean CPA (3.02 vs 2.49) **không được diễn giải là hiệu quả đào tạo**. Nếu chuyên ngành được phân theo CPA thì CPA là **biến đầu vào của việc phân nhóm**, và so sánh CPA giữa hai nhóm là **circular**.

**C4 — CPA được lưu dưới dạng TEXT, không phải số.**
Cột J: 2,023/2,023 ô kiểu `str`. Đọc bằng bất kỳ loader nào không ép kiểu sẽ cho cột object, khiến mọi phép `mean`, `sort`, `>` sai âm thầm (sort theo lexicographic: `"3.10" < "3.9"`).

**C5 — 3 dòng có CPA là chuỗi rỗng `''` (không phải `NULL`).**

| `Mã SV` | `Mã lớp` | `Số TCTL` | `Ghi chú` |
|---|---|---:|---|
| `B22DCCN931` | D22HTTT01 | 0 | Không đủ đk |
| `B22DCCN031` | D22HTTT04 | 0 | Không đủ đk |
| `B22DCVT379` | D22VTVT | *(null)* | Không đủ đk |

2/3 dòng nằm trong scope. Missingness **không ngẫu nhiên** — cả 3 đều là `Không đủ đk` với 0 tín chỉ tích lũy.

**C6 — Selection bias cấu trúc (xem §1.3).**
Dataset là danh sách xét ĐATN, không phải cohort đầu vào. Sinh viên rời hệ thống trước thời điểm này bị loại khỏi mẫu. Mọi thống kê CPA đều là **conditional on survival**.

**C7 — 1 dòng có ngày sinh bất khả thi.**
`TT=2023`, `B23DCDT089`, lớp `D23DTMT01`, ngày sinh **`14/07/2025`** (tức 1 tuổi tại thời điểm file). Đây cũng là dòng cuối cùng của bảng và là **lớp D23 duy nhất** — có dấu hiệu là dòng được append thủ công. Out-of-scope, nhưng phải flag, **không xóa**.

---

### 🟡 WARNING

**W1 — `TTTN` thiếu 119 giá trị (5.9% full / 53 in-scope), missingness hoàn toàn có cấu trúc.**

| `TTTN` | Không đủ đk | Làm ĐATN |
|---|---:|---:|
| *(missing)* | **119** | 0 |
| `F` | **26** | 0 |
| `D+`→`A+` | 0 | **1,878** |

100% giá trị thiếu rơi vào nhóm `Không đủ đk`, và 100% nhóm `Làm ĐATN` có điểm ≥ `D+`. Đây là **structurally missing (MNAR)**, không phải lỗi nhập liệu. Tuyệt đối không impute.

**W2 — `Số TCTL` thiếu 1 giá trị** (`B22DCVT379`, out-of-scope, trùng với C5).

**W3 — Cohort gần như là hằng số → không dùng được làm analytical dimension.**

| Năm trong `Mã SV` | n (full) | n (in-scope) |
|---|---:|---:|
| 21 | 11 | 6 |
| 22 | 2,011 | 899 |
| 23 | 1 | 0 |

99.3% mẫu in-scope thuộc cùng một khóa (2022). **Không thể làm phân tích cohort/trend.**

**W4 — 11 sinh viên khóa trước (`B21DC*`) lẫn trong lớp D22/E22.**
Nhóm chậm tiến độ (học lại/kéo dài). Trong scope có 6. Là dữ liệu hợp lệ nhưng vi phạm giả định "một khóa đồng nhất".

**W5 — 3 `Mã SV` có độ dài 11 thay vì 10, prefix `N22`, hậu tố `B`.**

| `Mã SV` | `Mã lớp` | CPA | `Ghi chú` |
|---|---|---:|---|
| `N22DCVT043B` | D22VTMD01 | 2.21 | Làm ĐATN |
| `N22DCCI041B` | E22CNPM01 | 2.72 | Không đủ đk |
| `N22DCDK035B` | E22CNPM02 | 1.40 | Không đủ đk |

Prefix `N` và mã ngành `CI`/`DK` không xuất hiện ở bất kỳ đâu khác. Bản chất **UNCONFIRMED**. 2/3 nằm trong scope. **Giữ lại, gắn flag.**

**W6 — Header không đầy đủ do merged cell.**
`C1:D1` merge thành `Họ tên`; ô `D1` **rỗng**. Mọi header-based loader sẽ tạo tên cột kiểu `Unnamed: 3`. Phải hard-code schema thay vì đọc header.

**W7 — `Ghi chú` không phải hàm đơn giản của `Số TCTL`.**
261 sinh viên `Làm ĐATN` có `Số TCTL < 140` (thấp nhất 69), trong khi ngưỡng cao nhất của `Không đủ đk` là 140. Hai nhóm **chồng lấn** ở dải 69–140 → tiêu chí xét duyệt phụ thuộc yếu tố không có trong file. Không được reverse-engineer business rule từ dataset này.

**W8 — Ý nghĩa đầy đủ của `TTTN` chưa xác nhận.**
Header là chữ viết tắt không giải thích. Evidence duy nhất: thang điểm chữ 9 bậc và liên hệ chặt với điều kiện ĐATN. Ghi nhận là **UNCONFIRMED**; không đặt tên diễn giải trong schema sạch.

---

### 🟢 MINOR

| ID | Vấn đề | Chi tiết |
|---|---|---|
| M1 | Double space trong `Nơi sinh` | `Hà  Nội` (1 dòng) vs `Hà Nội` (488 dòng) |
| M2 | Đặt tên địa danh không nhất quán | `Hồ Chí Minh` (6) vs `TP. Hồ Chí Minh` (1) → cùng một tỉnh, đếm thành 2 |
| M3 | Trộn lẫn tỉnh VN và quốc gia trong cùng một cột | `Lào` (7), `Liên Bang Nga` (3), `CHLB Đức` (1) — cần cột `is_domestic` riêng nếu dùng |
| M4 | `number_format` không nhất quán trong cùng cột | Cột J có cả `General` và `#,##0.00`; cột H có `General`, `#,##0`, `0.00` — dấu hiệu file được ghép/paste từ nhiều nguồn |
| M5 | Ngày tháng là text, không phải Excel date serial | Format thống nhất `DD/MM/YYYY`, parse 2,023/2,023 thành công — nhất quán nhưng cần parse tường minh với `dayfirst=True` |
| M6 | Họ tên tách 2 cột không có header cột thứ hai | Cột C/D — sẽ drop nên tác động thấp |
| M7 | AutoFilter phủ tới cột `IU` (255 cột) | 244 cột rỗng; một số reader sẽ sinh cột `Unnamed: 11`…`Unnamed: 254` |
| M8 | 4 dòng rỗng cuối sheet (2025–2028) | Trailing blank rows, cần lọc |
| M9 | PII trong workbook metadata | `lastModifiedBy = Tran Thanh Thuy D22CN05` |

---

### Không phải vấn đề (đã kiểm tra, sạch)

| Kiểm tra | Kết quả |
|---|---|
| Trùng `Mã SV` | **0** |
| Trùng (`Họ tên` + `Ngày sinh`) | **0** |
| `TT` trùng hoặc ngắt quãng | **0** (liên tục 1→2023) |
| Khoảng trắng đầu/cuối ở mọi cột text | **0** |
| CPA ngoài thang [0, 4] | **0** |
| CPA = 0 | **0** |
| CPA sai số chữ số thập phân | **0** (2,020/2,020 đều 2 chữ số) |
| `Ngày sinh` sai format | **0** |
| Ký tự lạ / encoding hỏng trong tiếng Việt | Không phát hiện |

---

## 4. CPA analysis

### 4.1 Scale & range

| Chỉ số | Toàn file (n=2,020) | In-scope (n=903) |
|---|---:|---:|
| Thang đo | **4.0** (suy ra từ range + không có giá trị >4) | 4.0 |
| Min | 1.25 | 1.40 |
| Max | 3.79 | 3.72 |
| Mean | 2.723 | 2.791 |
| Median | 2.73 | 2.79 |
| Std | 0.437 | 0.432 |
| Q1 / Q3 | 2.42 / 3.06 | — |
| Skewness | — | −0.24 |
| Excess kurtosis | — | −0.26 |

**Không quan sát thấy giá trị 4.00, cũng không có giá trị ≤ 1.24.** Điểm tối đa thực tế 3.79 — hợp lý với thang 4 nhưng cũng nhất quán với việc mẫu đã bị lọc.

### 4.2 Distribution (in-scope, n=903)

| Khoảng CPA | n | % |
|---|---:|---:|
| < 1.50 | 2 | 0.2% |
| 1.50 – 2.00 | 42 | 4.6% |
| 2.00 – 2.50 | 172 | 19.0% |
| 2.50 – 3.00 | 383 | 42.4% |
| 3.00 – 3.20 | 130 | 14.4% |
| 3.20 – 3.60 | 157 | 17.4% |
| 3.60 – 4.00 | 17 | 1.9% |

Phân phối gần đối xứng, hơi lệch trái, đơn đỉnh quanh 2.7–2.8.

### 4.3 Giá trị bất thường

Theo hàng rào IQR `[1.46, 4.02]` trên toàn file: **6 outlier, tất cả đều ở đuôi dưới, 0 ở đuôi trên.**

| `Mã SV` | `Mã lớp` | `Số TCTL` | CPA | `Ghi chú` | In-scope |
|---|---|---:|---:|---|---|
| `B22DCDT273` | D22XLTH | 8 | 1.25 | Không đủ đk | ❌ |
| `B22DCVT266` | D22VTVT | 16 | 1.38 | Không đủ đk | ❌ |
| `B22DCVT452` | D22VTVT | 5 | 1.40 | Không đủ đk | ❌ |
| `B22DCVT165` | D22VTHI02 | 10 | 1.40 | Không đủ đk | ❌ |
| `N22DCDK035B` | E22CNPM02 | 24 | 1.40 | Không đủ đk | ✅ |
| `B22DCVT140` | D22VTHI01 | 11 | 1.45 | Không đủ đk | ❌ |

➡️ **Cả 6 đều là `Không đủ đk` với `Số TCTL` rất thấp (5–24).** Đây là **outlier hợp lệ và giải thích được** — sinh viên gần như không tích lũy được tín chỉ. **KHÔNG loại bỏ.** Chúng phải được xử lý bằng cách phân tách nhóm `Không đủ đk`, không bằng cách trimming.

### 4.4 CPA theo lớp (in-scope)

`n` dưới đây là **số quan sát có CPA**, không phải số dòng. `D22HTTT01` có 55 dòng / 54 CPA; `D22HTTT04` có 54 dòng / 53 CPA. Mọi lớp khác: dòng = CPA.

| `Mã lớp` | n (CPA) | mean | std | min | median | max |
|---|---:|---:|---:|---:|---:|---:|
| D22CNPM01 | 59 | 3.008 | 0.265 | 2.55 | 2.950 | 3.68 |
| D22CNPM02 | 60 | 3.042 | 0.326 | 2.50 | 3.040 | 3.62 |
| D22CNPM03 | 60 | 2.978 | 0.314 | 2.47 | 2.985 | 3.67 |
| D22CNPM04 | 60 | 3.047 | 0.264 | 2.59 | 3.070 | 3.63 |
| D22CNPM05 | 62 | 2.963 | 0.279 | 2.43 | 2.980 | 3.72 |
| D22CNPM06 | 61 | 3.081 | 0.267 | 2.49 | 3.080 | 3.62 |
| D22HTTT01 | 54 | 2.433 | 0.473 | 1.66 | 2.360 | 3.44 |
| D22HTTT02 | 55 | 2.507 | 0.413 | 1.65 | 2.440 | 3.40 |
| D22HTTT03 | 55 | 2.523 | 0.374 | 1.67 | 2.520 | 3.34 |
| D22HTTT04 | 53 | 2.543 | 0.397 | 1.72 | 2.440 | 3.69 |
| D22HTTT05 | 53 | 2.436 | 0.408 | 1.71 | 2.450 | 3.41 |
| D22HTTT06 | 56 | 2.466 | 0.359 | 1.69 | 2.445 | 3.51 |
| E22CNPM01 | 34 | 2.741 | 0.283 | 1.99 | 2.680 | 3.48 |
| E22CNPM02 | 32 | 2.751 | 0.414 | 1.40 | 2.785 | 3.67 |
| E22CNPM03 | 36 | 2.788 | 0.318 | 2.31 | 2.715 | 3.43 |
| E22CNPM04 | 35 | 2.741 | 0.389 | 1.50 | 2.780 | 3.29 |
| E22HTTT | 40 | 2.917 | 0.417 | 2.18 | 2.805 | 3.70 |
| E22TTNT | 38 | 3.243 | 0.323 | 2.57 | 3.285 | 3.71 |

**Đáng chú ý:** trong cùng một `LopRoot`, mean CPA giữa các lớp đánh số rất đồng đều (CNPM: 2.963–3.081; HTTT: 2.433–2.543). Số hiệu lớp (`01`…`06`) **không** mã hóa thứ hạng. Nhưng khác biệt **giữa** các root thì rất lớn — củng cố C3.

`E22TTNT` (mean 3.243, cao nhất toàn scope) chỉ có **n=38** — sample nhỏ, không đủ để kết luận riêng.

---

## 5. Sample size của từng group

### 5.1 In-scope, theo nhóm mã lớp

| Nhóm | n | CPA khả dụng | `Làm ĐATN` | `Không đủ đk` | `TTTN` missing |
|---|---:|---:|---:|---:|---:|
| `D22CNPM*` | 362 | 362 | — | — | — |
| `D22HTTT*` | 328 | 326 | — | — | — |
| **Tổng D22 (in-scope)** | **690** | **688** | 634 | 56 | 44 |
| `E22CNPM*` | 137 | 137 | — | — | — |
| `E22HTTT` | 40 | 40 | — | — | — |
| `E22TTNT` | 38 | 38 | — | — | — |
| **Tổng E22** | **215** | **215** | 202 | 13 | 9 |
| **TỔNG IN-SCOPE** | **905** | **903** | **836** | **69** | **53** |

### 5.2 In-scope, theo ngành tuyển sinh (prefix `Mã SV`)

| Prefix | trong lớp D22 | trong lớp E22 | Tổng |
|---|---:|---:|---:|
| `B22DCCN` | 686 | 28 | 714 |
| `B22DCVT` | 0 | 96 | 96 |
| `B22DCDT` | 0 | 49 | 49 |
| `B22DCAT` | 0 | 34 | 34 |
| `B22DCKH` | 0 | 4 | 4 |
| `B21DCCN` | 4 | 1 | 5 |
| `B21DCDT` | 0 | 1 | 1 |
| `N22DC*` | 0 | 2 | 2 |

Nếu gộp theo mã ngành 4 ký tự (`Mã SV`[3:7], bỏ qua năm/tiền tố): `DCCN` 719 · `DCVT` 96 · `DCDT` 50 · `DCAT` 34 · `DCKH` 4 · `DCCI` 1 · `DCDK` 1 — đây là dạng dùng cho field `admission_major_code` ở §10.

➡️ Nếu định nghĩa nhóm theo **ngành tuyển sinh** thay vì theo lớp, cấu trúc so sánh thay đổi hoàn toàn. Hai định nghĩa cho ra hai dataset khác nhau. **Phải chọn và ghi rõ một định nghĩa trước khi phân tích.**

---

## 6. Recommended cleaning rules

Mỗi rule kèm lý do. **Không rule nào xóa dữ liệu chỉ vì trông bất thường.**

### Nhóm A — Loading

| ID | Rule | Lý do |
|---|---|---|
| **A1** | Đọc sheet `Data`, `header=None`, `skiprows=1`, `usecols=A:K`, gán tên cột hard-code. | `C1:D1` merged khiến `D1` rỗng → header-based loader tạo `Unnamed: 3`; autofilter tới `IU` tạo 244 cột rác (W6, M7). |
| **A2** | Loại các dòng mà toàn bộ 11 cột đều null. | 4 trailing blank rows 2025–2028 (M8). Loại theo tiêu chí "all-null", không loại theo chỉ số dòng cứng. |
| **A3** | Ép `Điểm TBCTL` → `float` bằng `pd.to_numeric(errors='coerce')`, sau đó **assert** `0 ≤ CPA ≤ 4`. | Cột đang là text → mọi phép toán/sắp xếp sai âm thầm (C4). `assert` bắt lỗi sớm thay vì để lọt. |
| **A4** | Parse `Ngày sinh` bằng `format='%d/%m/%Y'` tường minh (không dựa vào inference). | Format nhất quán nhưng dd/mm dễ bị parser Mỹ hiểu ngược thành mm/dd (M5). |

### Nhóm B — Scope

| ID | Rule | Lý do |
|---|---|---|
| **B1** | Áp filter `Mã lớp` khớp `^(D22CNPM\|D22HTTT\|E22)` → **905 dòng**. Ghi lại số dòng trước/sau. | File chứa 1,118 dòng ngoài phạm vi dự án (§1.4). Không filter sẽ sai toàn bộ mẫu số. |
| **B2** | **Giữ nguyên** file gốc, không sửa tại chỗ. Mọi bước sinh ra artifact mới. | Reproducibility; file gốc là nguồn duy nhất, cần audit trail. |

### Nhóm C — Derived fields

| ID | Rule | Lý do |
|---|---|---|
| **C1** | Tạo `class_group` = `Mã lớp` bỏ hậu tố số (`D22CNPM01` → `D22CNPM`). | Cần một mức tổng hợp giữa lớp (18 giá trị, n nhỏ) và toàn bộ scope. |
| **C2** | Tạo `admission_major_code` = `Mã SV`[3:7] (`DCCN`, `DCVT`, …). | Là trục ngành tuyển sinh **độc lập** với lớp; bắt buộc để phát hiện confound ở nhóm E22 (C2). |
| **C3** | Tạo `class_prefix` = `Mã lớp`[0] (`D` / `E`) và `intake_year` = `Mã SV`[1:3]. | Tách hai chiều đang bị trộn trong một chuỗi. |
| **C4** | Tạo `track_label` với giá trị trung tính (`D22CNPM`, `D22HTTT`, `E22CNPM`, `E22HTTT`, `E22TTNT`) — **không** dùng nhãn "CLC" / "chuẩn" / "chất lượng cao". | Không có evidence trong file cho ánh xạ program (C1, C2). Nhãn trung tính giữ phân tích đúng ngay cả khi giả định sai. Có thể đổi nhãn sau khi phòng đào tạo xác nhận. |
| **C5** | Tạo `is_off_cohort` = `intake_year != '22'` (6 dòng in-scope). | Cho phép sensitivity analysis mà không loại bỏ dữ liệu (W4). |
| **C6** | Tạo `id_format_anomaly` = `len(Mã SV) != 10` (2 dòng in-scope). | Đánh dấu 3 mã `N22…B` chưa rõ bản chất (W5) — flag thay vì xóa. |
| **C7** | Tạo `eligible_for_thesis` = (`Ghi chú` == `Làm ĐATN`) → boolean. | Cột nhị phân sạch cho outcome thứ hai. |

### Nhóm D — Missing values

| ID | Rule | Lý do |
|---|---|---|
| **D1** | Chuẩn hóa chuỗi rỗng `''` → `NA` ở mọi cột text. | 3 ô CPA là `''` chứ không phải null (C5) — `''` sẽ lọt qua `isna()`. |
| **D2** | **Không impute** `TTTN`. Thêm cột `tttn_missing` (boolean). | Missingness là MNAR có cấu trúc: 100% giá trị thiếu nằm ở nhóm `Không đủ đk` (W1). Impute sẽ bịa ra dữ liệu và làm sai lệch mọi so sánh. |
| **D3** | **Không impute** CPA. Loại 2 dòng thiếu CPA **chỉ trong các phép tính riêng về CPA**, giữ lại trong dataset. | Missing CPA cũng không ngẫu nhiên (cả 2 đều `Không đủ đk`, 0 tín chỉ). Listwise deletion toàn cục sẽ âm thầm bỏ đúng nhóm yếu nhất. |
| **D4** | Ghi số quan sát khả dụng (`n`) **riêng cho từng metric**, không dùng một `n` chung. | `n` khác nhau: 905 (class), 903 (CPA), 852 (TTTN). Dùng chung một `n` sẽ sai. |

### Nhóm E — Chuẩn hóa & flag

| ID | Rule | Lý do |
|---|---|---|
| **E1** | `Nơi sinh`: collapse whitespace liên tiếp, trim. | `Hà  Nội` đang bị đếm tách khỏi `Hà Nội` (M1). Đây là chuẩn hóa **format**, không đổi giá trị. |
| **E2** | `Nơi sinh`: hợp nhất `TP. Hồ Chí Minh` → `Hồ Chí Minh` qua **bảng mapping tường minh, có version**. | Cùng một tỉnh bị đếm 2 lần (M2). Bảng mapping tường minh để review được, khác với fuzzy matching. |
| **E3** | Thêm `birthplace_is_domestic` (boolean); giữ nguyên giá trị gốc. | Cột đang trộn tỉnh VN và quốc gia (M3) — làm sai mọi phép tổng hợp theo địa lý. |
| **E4** | Thêm `dob_implausible` = `birth_year < 1990 or birth_year > 2010`. Bắt 1 dòng (`14/07/2025`). | C7 là lỗi nhập liệu gần như chắc chắn, nhưng không được **sửa** khi chưa có nguồn xác thực, cũng không được **xóa**. Flag là lựa chọn đúng. |
| **E5** | **Không** trim/winsorize CPA outlier. | Cả 6 outlier đều giải thích được bằng `Số TCTL` cực thấp + `Không đủ đk` (§4.3). Chúng là tín hiệu, không phải nhiễu. |

### Nhóm F — Privacy (bắt buộc trước khi public)

| ID | Rule | Lý do |
|---|---|---|
| **F1** | **Drop** `Họ tên` (cột C) và `Tên` (cột D). | Direct identifier. Không có mục đích phân tích nào cần tên. |
| **F2** | Thay `Mã SV` bằng `student_key` = HMAC-SHA256(`Mã SV`, salt bí mật), giữ 12 hex ký tự. Salt **không** commit. | `Mã SV` là mã công khai tra cứu được → hash trần (không salt) đảo ngược được bằng brute-force trên không gian mã rất nhỏ (~1,000 mã/ngành). |
| **F3** | **Drop** `Ngày sinh`. Nếu thật sự cần, chỉ giữ `birth_year`. | `Họ tên` + `Ngày sinh` định danh duy nhất **100%** (905/905). Ngay cả `Ngày sinh` + `Mã lớp` cũng đã unique **87.3%** — xem §7. |
| **F4** | Ở output công khai: suppress mọi cell có `n < 10`; không hiển thị min/max CPA ở mức lớp. | Min/max ở nhóm nhỏ là point disclosure — CPA thấp nhất của một lớp 34 người trỏ đích danh một cá nhân. |
| **F5** | Không publish bảng chéo `Nơi sinh` × `Mã lớp` ở dạng thô. | Có 10 tỉnh với ≤ 3 sinh viên in-scope; kết hợp với lớp cho ô n=1 (§7). |
| **F6** | Strip `docProps` (`creator`, `lastModifiedBy`) khỏi mọi file phái sinh; không commit `.xlsx` gốc vào repo public. | Metadata chứa tên thật (M9). `data/` hiện đang untracked — giữ nguyên và thêm vào `.gitignore`. |

---

## 7. Privacy / re-identification risk

Đo trên **905 dòng in-scope**.

| Quasi-identifier set | Số nhóm | Nhóm k=1 | % dòng bị định danh duy nhất | Mức rủi ro |
|---|---:|---:|---:|---|
| `Họ tên` + `Ngày sinh` | 905 | 905 | **100.0%** | 🔴 Critical |
| `Họ tên` | 859 | 823 | **90.9%** | 🔴 Critical |
| `Ngày sinh` + `Mã lớp` | 846 | 790 | **87.3%** | 🔴 Critical |
| `Ngày sinh` + `Nơi sinh` | 804 | 720 | **79.6%** | 🔴 Critical |
| `Ngày sinh` + `Nơi sinh` + `Mã lớp` | 897 | 889 | **98.2%** | 🔴 Critical |
| `Ngày sinh` | 369 | 136 | 15.0% | 🟡 High |
| `Mã lớp` + `Nơi sinh` | 308 | 126 | 13.9% | 🟡 High |

### Xếp hạng rủi ro theo cột

| Cột | Loại | Rủi ro | Xử lý bắt buộc |
|---|---|---|---|
| `Họ tên` + `Tên` | Direct identifier | 🔴 Critical | **Drop** |
| `Mã SV` | Direct identifier (tra cứu công khai được) | 🔴 Critical | **Salted HMAC** |
| `Ngày sinh` | Quasi-identifier mạnh nhất | 🔴 Critical | **Drop** (tối đa `birth_year`) |
| `Nơi sinh` | Quasi-identifier, đuôi thưa | 🟡 High | Giữ, nhưng **suppress cell nhỏ**; 10 tỉnh có n ≤ 3 |
| `Mã lớp` | Quasi-identifier yếu (n=32–62/lớp) | 🟡 Medium | Giữ; không hiển thị min/max ở mức lớp |
| `Điểm TBCTL` (CPA) | **Sensitive attribute** (dữ liệu học tập) | 🟡 Medium | Đây là thứ cần bảo vệ, không phải khóa để join |
| `Số TCTL`, `TTTN`, `Ghi chú` | Sensitive attribute | 🟢 Low riêng lẻ | Kết hợp `Ghi chú='Không đủ đk'` + `Số TCTL=0` + lớp → nhóm rất nhỏ, cần suppression |
| `TT` | — | 🟢 None | Drop |
| Workbook metadata | Direct identifier | 🟡 High | Strip |

⚠️ **Rủi ro đặc biệt:** tổ hợp `Ghi chú = 'Không đủ đk'` là nhóm chỉ 69 người in-scope, phân bố mỏng trên 18 lớp (trung bình ~4/lớp). Publish breakdown theo lớp cho nhóm này = công khai danh tính sinh viên trượt điều kiện tốt nghiệp. **Đây là thông tin nhạy cảm nhất trong toàn bộ dataset.**

---

## 8. Analytical dimensions available

### ✅ Thực sự tồn tại và dùng được

| Dimension | Nguồn | Cardinality (in-scope) | Sample size nhỏ nhất | Ghi chú |
|---|---|---:|---:|---|
| **Class** | `Mã lớp` (trực tiếp) | 18 | 32 (`E22CNPM02`) | Chiều đáng tin cậy nhất |
| **Class group / Track** | derive từ `Mã lớp` | 5 | 38 (`E22TTNT`) | Dùng nhãn trung tính |
| **Class prefix (D / E)** | derive từ `Mã lớp`[0] | 2 | 215 (E) | Nhị phân, n đủ lớn |
| **Admission major** | derive từ `Mã SV`[3:7] | 8 | 1 | Chỉ dùng được cho `DCCN`/`DCVT`/`DCDT`/`DCAT`; còn lại n < 5 |
| **CPA** | `Điểm TBCTL` | liên tục, n=903 | — | 🎯 Outcome chính |
| **Credits accumulated** | `Số TCTL` | 0–146, n=905 | — | Progress measure |
| **Thesis eligibility** | `Ghi chú` | 2 | 69 | Outcome nhị phân |
| **TTTN grade** | `TTTN` | 9 bậc, n=852 | 5 (`D+`) | Ordinal; ⚠️ nghĩa UNCONFIRMED |
| **Birthplace** | `Nơi sinh` | 36 in-scope (48 toàn file) | 1 | Chỉ dùng cho top ~10 tỉnh |

### ❌ KHÔNG tồn tại — đừng đưa vào thiết kế

| Dimension | Lý do |
|---|---|
| **Program / CLC flag** | Không có cột nào. Chỉ là derived assumption chưa xác nhận (C1, C2). |
| **Cohort / intake year** | 99.3% in-scope cùng khóa 2022 (W3). Không có biến thiên để phân tích. |
| **Time / trend / semester** | Dataset là snapshot một thời điểm. Không có trục thời gian. |
| **Gender** | Không có cột. **Không được suy ra từ tên tiếng Việt** — không đáng tin và tạo thêm rủi ro. |
| **GPA theo học kỳ, điểm môn học** | Chỉ có CPA tích lũy tổng hợp. |
| **Điểm đầu vào / điểm thi THPT** | Không có. Đây chính là biến kiểm soát then chốt bị thiếu (§9). |
| **Hoàn cảnh KT-XH, học phí, học bổng** | Không có. |
| **Kết quả ĐATN / tốt nghiệp** | Chỉ có *đăng ký*, chưa có kết quả. |
| **Giảng viên, môn học, khoa** | Không có. |

---

## 9. Data limitations — dataset này **KHÔNG** cho phép kết luận điều gì

### 9.1 Không cho phép suy luận nhân quả

1. **Không kết luận chương trình nào "tốt hơn" / "chất lượng cao hơn".** Đây là observational cross-sectional data, không có randomization, không có baseline đầu vào. Không có bất kỳ điều kiện identification nào được thỏa mãn.
2. **Không suy diễn từ tên chương trình.** Không được coi `E22` (hay bất kỳ nhãn "CLC" nào) là "better" hay "higher quality" chỉ vì tên gọi. Tên gọi không phải evidence.
3. **Không diễn giải chênh lệch `D22CNPM` vs `D22HTTT` là hiệu quả đào tạo.** Bằng chứng phân phối (§C3) cho thấy rất mạnh rằng CPA là **tiêu chí phân lớp**, không phải kết quả của lớp. Đây là reverse causality.
4. **Thiếu biến kiểm soát then chốt:** điểm đầu vào, năng lực nền, động lực, hoàn cảnh, lựa chọn cá nhân — tất cả đều không có trong dataset.

### 9.2 Không cho phép khái quát hóa

5. **Không đại diện cho toàn bộ sinh viên PTIT.** In-scope 905 người, chỉ thuộc CNTT/HTTT/E22 khóa 2022.
6. **Không đại diện cho toàn bộ khối kỹ thuật PTIT**, kể cả khi dùng cả 2,023 dòng — vẫn chỉ là một khóa, một thời điểm xét ĐATN.
7. **Không đại diện cho toàn bộ ngành đào tạo PTIT.**
8. **Không đại diện cho khóa 2022 đầy đủ** — do survivorship filtering (§1.3). Sinh viên bỏ học/buộc thôi học **không có mặt**, nên phân phối CPA bị **cắt đuôi dưới** một cách hệ thống. Mọi trung bình đều **lệch cao**.
9. **Không so sánh được theo thời gian.** Chỉ một cohort, một snapshot.

### 9.3 Không cho phép với nhóm nhỏ

10. **`E22HTTT` (n=40), `E22TTNT` (n=38)** — quá nhỏ cho subgroup inference đáng tin. `E22TTNT` có mean CPA cao nhất (3.243) nhưng **không được** trình bày như một phát hiện.
11. **Nhóm `Không đủ đk` (n=69 in-scope)** — quá nhỏ để breakdown theo lớp, và nhạy cảm về privacy.
12. **`Admission major` ngoài 4 mã lớn** — `B22DCKH` (n=4), `B21DC*` (n=6), `N22DC*` (n=2) không đủ để phân tích riêng.

### 9.4 Không cho phép vì ý nghĩa dữ liệu chưa xác nhận

13. **Không được gán nhãn "CNTT" / "CNTT CLC"** cho các nhóm cho đến khi phòng đào tạo xác nhận ánh xạ `Mã lớp` → chương trình. Bằng chứng hiện có **mâu thuẫn** với ánh xạ giả định (C2).
14. **Không diễn giải `TTTN`** vượt quá "một điểm chữ liên quan điều kiện ĐATN" (W8).
15. **Không reverse-engineer quy tắc xét `Làm ĐATN`** từ `Số TCTL` — hai nhóm chồng lấn ở dải 69–140 (W7).
16. **Không coi `Nơi sinh` là nơi cư trú hiện tại** — header ghi rõ "nơi sinh".

### 9.5 Điều dataset **CÓ** cho phép

- Mô tả (descriptive) phân phối CPA trong nhóm sinh viên **đã đến được bước xét ĐATN**, khóa 2022, các lớp CNTT/HTTT/E22.
- So sánh **có mô tả, không nhân quả** giữa các lớp / class group, **kèm điều kiện rõ ràng** về selection.
- Mô tả mối liên hệ (association) giữa CPA, số tín chỉ tích lũy và điều kiện ĐATN.
- Mô tả cấu trúc cấu thành của các lớp E22 theo ngành tuyển sinh — bản thân đây là một phát hiện có giá trị.

---

## 10. Recommended cleaned schema

Analytical dataset: **`data/processed/students_clean.parquet`** — 905 dòng.

| # | Field | Type | Nullable | Nguồn | Mô tả |
|---|---|---|---|---|---|
| 1 | `student_key` | `string(12)` | ❌ | HMAC-SHA256(`Mã SV`, salt) | Pseudonymous PK. **Salt không commit.** |
| 2 | `class_code` | `category` | ❌ | `Mã lớp` | 18 giá trị in-scope |
| 3 | `class_group` | `category` | ❌ | derive | `D22CNPM` \| `D22HTTT` \| `E22CNPM` \| `E22HTTT` \| `E22TTNT` |
| 4 | `class_prefix` | `category` | ❌ | `Mã lớp`[0] | `D` \| `E` |
| 5 | `admission_major_code` | `category` | ❌ | `Mã SV`[3:7] | `DCCN` \| `DCVT` \| `DCDT` \| `DCAT` \| `DCKH` \| `DCCI` \| `DCDK` |
| 6 | `intake_year` | `int16` | ❌ | `Mã SV`[1:3] → 2000+ | 2021 \| 2022 |
| 7 | `cpa` | `float64` | ✅ (2) | `Điểm TBCTL` → numeric | Thang 4.0. Range in-scope 1.40–3.72 |
| 8 | `credits_accumulated` | `int16` | ❌ (0 missing in-scope) | `Số TCTL` | 0–146 |
| 9 | `tttn_grade` | `category` (ordered) | ✅ (53) | `TTTN` | `F < D < D+ < C < C+ < B < B+ < A < A+`. ⚠️ nghĩa UNCONFIRMED |
| 10 | `eligible_for_thesis` | `bool` | ❌ | `Ghi chú` == `Làm ĐATN` | 836 True / 69 False |
| 11 | `birthplace` | `category` | ❌ | `Nơi sinh` (đã chuẩn hóa E1+E2) | 36 giá trị in-scope |
| 12 | `birthplace_is_domestic` | `bool` | ❌ | derive | False cho `Lào` (7), `Liên Bang Nga` (2), `CHLB Đức` (1) |
| 13 | `birth_year` | `int16` | ❌ | `Ngày sinh` → year | **Chỉ giữ năm.** Không giữ ngày/tháng |
| 14 | `tttn_missing` | `bool` | ❌ | derive | Missingness là tín hiệu (D2), không phải lỗi |
| 15 | `cpa_missing` | `bool` | ❌ | derive | 2 dòng |
| 16 | `is_off_cohort` | `bool` | ❌ | `intake_year != 2022` | 6 dòng |
| 17 | `id_format_anomaly` | `bool` | ❌ | `len(Mã SV) != 10` | 2 dòng (`N22…B`) |
| 18 | `dob_implausible` | `bool` | ❌ | `birth_year ∉ [1990, 2010]` | 0 dòng in-scope |

### Bị loại có chủ đích

| Cột gốc | Lý do |
|---|---|
| `TT` | Row counter, không mang thông tin |
| `Họ tên` (C) | 🚫 PII — direct identifier |
| `Tên` (D) | 🚫 PII — direct identifier |
| `Ngày sinh` (đầy đủ) | 🚫 Quasi-identifier: 100% unique khi ghép với tên; 87.3% unique khi ghép với lớp. Chỉ giữ `birth_year` |
| `Mã SV` (raw) | 🚫 Thay bằng `student_key` |

### ❌ Field **không được** đưa vào schema

| Field bị cám dỗ thêm vào | Vì sao không |
|---|---|
| `program` / `is_clc` | Chưa có evidence (C1, C2). Chỉ thêm sau khi phòng đào tạo xác nhận, và phải kèm cột nguồn xác nhận. |
| `program_quality_tier` | Không đo được từ dataset này. Vi phạm §9.1. |
| `gender` | Không có trong dữ liệu; suy từ tên là không đáng tin và tăng rủi ro privacy. |
| `cpa_rank` / `percentile` | An toàn ở mức tổng thể, nhưng **không tạo rank trong lớp** — rank + lớp là point disclosure. |
| `cpa_band` cố định | Chỉ tạo ở tầng presentation, không lưu trong schema, để tránh khóa cứng một cách phân loại. |

### Artifact phụ trợ nên tạo

| File | Nội dung |
|---|---|
| `data/processed/scope_manifest.json` | Số dòng trước/sau filter, danh sách 42 mã lớp và mã nào in/out scope, timestamp, hash của file nguồn |
| `data/processed/group_sizes.csv` | Bảng §5 — mọi biểu đồ phải kèm `n` |
| `data/reference/birthplace_mapping.csv` | Bảng mapping E2, có version, review được |
| `.gitignore` | Thêm `data/raw/`, `data/*.xlsx` — file gốc chứa PII và metadata tên thật |

---

## 11. Câu hỏi cần xác nhận trước Phase tiếp theo

Bốn câu hỏi này **chặn** việc đặt tên nhóm và diễn giải kết quả:

1. **`E22*` thực chất là chương trình gì?** 87% sinh viên nhóm này mang mã ngành **không phải** CNTT (VT 44.7%, ĐT 22.8%, ATTT 15.8%). Ánh xạ `E22 → CNTT CLC` mâu thuẫn với dữ liệu.
2. **`D22CNPM` và `D22HTTT` được phân lớp theo cơ chế nào?** Nếu phân theo CPA/xếp hạng thì mọi so sánh CPA giữa hai nhóm là circular và phải bị loại khỏi scope phân tích.
3. **`TTTN` là viết tắt của gì?** Cần xác nhận để đặt tên field và diễn giải đúng.
4. **`N22DC*B` (3 mã, 11 ký tự) là diện sinh viên nào?**

---

## Phụ lục — Tái lập audit

```
File:        data/DS-SV-DK-DATN-D22-KY-THUAT.xlsx
Sheet:       Data
Rows:        2,023 data rows (Excel rows 2–2024)
Columns:     11 (A–K)
In-scope:    905 rows (regex ^(D22CNPM|D22HTTT|E22) trên cột Mã lớp)
Môi trường:  Python 3.13.2 · pandas 3.0.1 · openpyxl 3.1.5 · numpy 2.4.2
Audit date:  2026-09-11
```
