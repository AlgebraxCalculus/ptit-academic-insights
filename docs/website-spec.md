# Website Content Specification — PTIT Academic Insights

**Phase:** 3 — Information architecture & content design
**Date:** 2026-09-11
**Inputs:** `docs/data-audit.md` (Phase 1) · `docs/insight-discovery.md` (Phase 2)
**Audience:** frontend developer + content reviewer
**Status:** Specification only. Chưa implement.

---

## 0. Product definition

### 0.1 Đây là gì

**Một public data story về kết quả học tập của 905 sinh viên CNTT khóa 2022 tại PTIT, tại thời điểm xét đồ án tốt nghiệp.**

Người đọc cuộn từ trên xuống và được dẫn qua một lập luận có thứ tự. Mỗi section trả lời đúng một câu hỏi và để lại đúng một ý. Phần tự khám phá nằm ở cuối, sau khi người đọc đã có đủ ngữ cảnh để không hiểu sai những gì họ lọc ra.

### 0.2 Đây KHÔNG phải là gì

| Không phải | Vì sao |
|---|---|
| Admin dashboard | Không có KPI tile grid, không có sidebar filter toàn cục, không có gauge/donut, không có badge "last updated", không có nút export |
| Bảng xếp hạng lớp | CORE-8: 18 lớp không phân biệt được về mặt thống kê trong cùng track (KW p = 0.19 / 0.55 / 0.95) |
| Công cụ tra cứu sinh viên | Privacy: mọi identifier đã bị hash/drop ở Phase 1 |
| Báo cáo đánh giá chất lượng đào tạo | Không có điều kiện identification nào cho suy luận nhân quả |

### 0.3 Narrative arc

Cấu trúc theo lối **"con số bạn tưởng → con số thật sự"**, vì đó chính là hình dạng của dữ liệu (CORE-2 là một Simpson's paradox đã được xác nhận).

```
Bối cảnh        →  Bức tranh chung  →  So sánh ai cũng muốn xem
(01 Scope)         (02-03)             (04 — và nó đảo dấu)
                                            ↓
Tự kiểm chứng   ←  Ngoài CPA        ←  Cấu trúc thật
(08 Explore)       (07 Eligibility)     (05 Track, 06 Composition)
                                            ↓
                                       Giới hạn & phương pháp
                                       (09-10)
```

**Điều chỉnh so với gợi ý trong brief:**

| Section gợi ý | Quyết định | Lý do |
|---|---|---|
| Hero | ✅ Giữ, tách thêm section Scope riêng | Scope disclaimer quá quan trọng để nhét vào hero |
| Overview | ✅ Giữ (02) | |
| Distribution | ✅ Giữ (03) | |
| Program comparison | ✅ Giữ (04) — nhưng thiết kế lại thành "reveal" | Con số gộp sai lệch; phải trình bày cả hai tầng |
| **Cohort patterns** | ❌ **Bỏ** — thay bằng 05 Track structure + panel giải thích | **Không thực hiện được:** 899/905 cùng khóa 2022, η² = 0.0013. Không có trục thời gian nào trong dataset |
| Insights | ❌ Bỏ như một section riêng | Insight nằm rải trong 02–07. Một section "Insights" tách rời sẽ lặp nội dung và tạo cảm giác dashboard |
| Explore | ✅ Giữ (08), đặt cuối | |
| Methodology | ✅ Giữ (09), tách thêm 10 "Những gì dataset không trả lời được" | Limitations xứng đáng có vị trí riêng, không chôn trong methodology |
| — | ➕ **Thêm 06 Composition** | SUP-3 là lời giải thích cho CORE-2; không có nó thì section 04 lơ lửng |
| — | ➕ **Thêm 07 Eligibility** | CORE-6 + CORE-7 là outcome thứ hai độc lập với CPA, và là phần "human" nhất của dataset |

---

## 1. Summary table

| # | Section | Question | Insight | Visualization | Interaction | Caveat |
|---|---|---|---|---|---|---|
| 00 | Hero | Tôi đang xem cái gì? | 905 sinh viên CNTT, 1 khóa, 2 chương trình, 1 thời điểm | Số lớn + sparkline mật độ CPA nền | Scroll cue | Không đại diện toàn PTIT |
| 01 | Scope | Dữ liệu này bao gồm và loại trừ ai? | Đây là danh sách xét ĐATN, không phải toàn khóa tuyển sinh | Sankey/funnel tĩnh 2.023 → 905 | Toggle "xem 42 lớp gốc" | Survivorship: SV thôi học không có mặt |
| 02 | Overview | Nhìn tổng thể thì kết quả ra sao? | 76.7% đạt Khá trở lên, 2.2% Xuất sắc | 5 band stacked bar 100% + 4 số dẫn | Hover band → n | Mean 2.79 là của một hỗn hợp 2 track |
| 03 | Distribution | CPA phân bố thế nào? | Nửa số SV nằm gọn trong 0.59 điểm; không ai đạt 4.0 | Histogram 0.1 + KDE, marker Q1/median/Q3 | Toggle overlay band xếp loại | Đuôi dưới bị cắt do survivorship |
| 04 | Program comparison | CLC có kết quả tốt hơn không? | Gộp: +0.106. Cùng chuyên ngành: **đảo dấu** (−0.264 / +0.433) | Bước 1 bar đơn → bước 2 slope chart 2 dòng + CI | Scroll-triggered reveal 2 bước | E22TTNT (17.7% CLC) không ghép cặp được |
| 05 | Track structure | Vậy cái gì thực sự phân hoá CPA? | Chương trình giải thích 1.1%; chuyên ngành 34.5% | η² bar chart + cặp histogram tô màu 2 cách | Toggle "tô theo chương trình / theo chuyên ngành" | η² là mô tả, không phải nhân quả |
| 05b | — trong 05 | Hai chuyên ngành cùng ngành khác nhau ra sao? | Chênh 0.535 (d=1.54); không SV CNPM nào dưới 2.43 | Ridgeline 2 track + đường dọc tại 2.43 | Hover → mật độ tại điểm | 🔴 Rất có thể là hệ quả của cách phân chuyên ngành |
| 05c | — trong 05 | Lớp nào tốt nhất? | Không lớp nào — trong cùng track không phân biệt được | Caterpillar 18 lớp + CI, tô theo track | Hover lớp → n, mean, CI | Cố ý **không** sắp xếp thành ranking |
| 06 | Composition | Ai đang ở trong mỗi chương trình? | 86.5% SV hệ CLC vào trường bằng mã ngành không phải CNTT | Stacked bar thành phần mã ngành, 2 chương trình | Hover segment → n, mean CPA | Mã ngành phản ánh đầu vào — biến không quan sát được |
| 07 | Eligibility | Ai đi được tới đồ án tốt nghiệp? | CNPM 99.4% vs HTTT 83.5%; nhưng CPA không quyết định điều đó | Bar tỷ lệ + CI; scatter CPA × tín chỉ | Toggle "theo chương trình / theo chuyên ngành" | Tiêu chí xét duyệt phụ thuộc biến không có trong dataset |
| 08 | Explore | Tôi tự kiểm chứng được không? | — (công cụ, không phải insight) | Histogram + summary card phản ứng theo filter | Filter: program, track, eligibility, credit bucket, CPA range | Chặn cứng n < 10; luôn hiện n và CI |
| 09 | Methodology | Con số này đến từ đâu? | — | Bảng data dictionary rút gọn + timeline xử lý | Accordion 5 nhóm | — |
| 10 | Limits | Dataset này KHÔNG nói được gì? | 6 nhóm kết luận bị chặn, kèm lý do | Danh sách có icon, không có chart | Không | Chính nó là caveat |

---

## 2. Section specifications

Mỗi section dưới đây gồm: **headline · deck · user question · insight (mã Phase 2) · metrics chính xác · visualization · supporting copy · interaction · caveat hiển thị**.

Copy viết sẵn bằng tiếng Việt. Dev copy nguyên văn, **không tự diễn đạt lại các con số**.

---

### 00 — Hero

**Headline**
> ## 905 sinh viên Công nghệ thông tin, một khóa, tại thời điểm xét đồ án tốt nghiệp

**Deck**
> Dữ liệu chính thức từ danh sách đăng ký đồ án tốt nghiệp khóa 2022 của Học viện Công nghệ Bưu chính Viễn thông. Hai chương trình: Công nghệ thông tin và Công nghệ thông tin chất lượng cao. Đây là những gì dữ liệu cho phép nói — và những gì nó không cho phép.

| Mục | Nội dung |
|---|---|
| **User question** | "Tôi đang xem cái gì, và có đáng tin không?" |
| **Metrics hiển thị** | `905` sinh viên · `18` lớp · `2` chương trình · `1` khóa tuyển sinh (2022) |
| **Visualization** | Không có chart thật. Nền là một **density ridge** của 903 giá trị CPA vẽ rất mảnh, độ mờ thấp — gợi hình dạng dữ liệu mà không yêu cầu đọc. Không trục, không nhãn, không tooltip. |
| **Supporting copy** | Một dòng dưới cùng: *"Cuộn xuống để bắt đầu. Khoảng 8 phút đọc."* |
| **Interaction** | Chỉ có scroll cue. Không CTA, không nút, không filter. |
| **Caveat hiển thị** | Ngay dưới deck, cỡ chữ nhỏ hơn: *"Dataset chỉ gồm sinh viên hai chương trình CNTT và CNTT chất lượng cao. Không đại diện cho toàn bộ sinh viên PTIT, khối kỹ thuật PTIT, hay bất kỳ ngành đào tạo nào khác."* |

**Ghi chú thiết kế:** hero **không** có KPI tiles. Bốn con số đặt thành một dòng chạy ngang, typographic, không khung viền, không icon.

---

### 01 — Scope

**Headline**
> ## Đây là danh sách xét đồ án tốt nghiệp — không phải toàn bộ khóa tuyển sinh

**Deck**
> Từ 2.023 sinh viên khối kỹ thuật trong file gốc, 905 người thuộc phạm vi phân tích này. Và ngay cả 905 người đó cũng đã là những người đi được đến bước xét đồ án.

| Mục | Nội dung |
|---|---|
| **User question** | "Dữ liệu này bao gồm ai, và quan trọng hơn — loại trừ ai?" |
| **Insight** | Phase 1 §1.3 (survivorship), §1.4 (scope filter) |
| **Metrics chính xác** | File gốc `2.023` dòng, `42` mã lớp → in-scope `905` dòng, `18` mã lớp, `5` chuyên ngành<br>Loại khỏi scope: `1.118` sinh viên thuộc VTMD, CQAT, CQKH, TKDPT, DTVM, VTHI, PTDPT, DTMT, VTVT, XLTH, D23DTMT<br>Trong scope: CNTT `690` (D22CNPM 362 + D22HTTT 328) · CNTT CLC `215` (E22CNPM 137 + E22HTTT 40 + E22TTNT 38) |
| **Visualization** | **Funnel ngang 2 bước, tĩnh.** Bước 1: thanh 2.023 chia thành 905 (đậm, có nhãn) + 1.118 (nhạt, gạch chéo). Bước 2: 905 tách thành 690 CNTT + 215 CNTT CLC. Không animation phức tạp — một fade-in khi vào viewport là đủ. |
| **Supporting copy** | *"Sinh viên đã thôi học, bị buộc thôi học, bảo lưu dài hạn hoặc chuyển trường không xuất hiện trong danh sách này. Điều đó có nghĩa là phân phối điểm bạn sắp thấy đã bị cắt mất phần đuôi dưới, và mọi giá trị trung bình đều cao hơn thực tế của cả khóa."*<br><br>*"Hệ chất lượng cao (mã lớp E22) được xác định theo quy ước của nhà trường."* |
| **Interaction** | Một link văn bản: *"Xem đầy đủ 42 mã lớp trong file gốc"* → mở panel liệt kê, đóng lại được. Mặc định đóng. |
| **Caveat hiển thị** | Callout box: *"Đây là một mẫu đã qua sàng lọc tự nhiên (survivorship-filtered), không phải một cohort đầy đủ. Mọi con số trong trang này mô tả nhóm sinh viên đã đi được đến bước xét đồ án tốt nghiệp."* |

---

### 02 — Overview

**Headline**
> ## Ba phần tư đạt loại Khá trở lên. Một trong 45 người đạt Xuất sắc.

**Deck**
> Điểm trung bình tích lũy của nhóm là 2.79 trên thang 4. Phần lớn sinh viên tập trung ở dải Khá, còn đỉnh trên rất mỏng.

| Mục | Nội dung |
|---|---|
| **User question** | "Nhìn tổng thể, kết quả học tập của nhóm này ra sao?" |
| **Insight** | CORE-4 |
| **Metrics chính xác** | mean `2.7915` (95% CI [2.7631, 2.8201]) · median `2.7900` · sd `0.4322`<br>Xuất sắc ≥3.60: `20` (**2.21%**, CI [1.36, 3.40]) · Giỏi 3.20–3.59: `157` (17.39%) · Khá 2.50–3.19: `516` (57.14%) · Trung bình 2.00–2.49: `169` (18.72%) · Yếu <2.00: `41` (4.54%)<br>Cumulative ≥2.5: **76.74%** · ≥3.2: 19.60%<br>Đủ điều kiện làm ĐATN: `836/905` = **92.4%** |
| **Visualization** | **Stacked bar 100% nằm ngang, 5 band**, mỗi band nhãn trực tiếp (n + %). Đây là chart chính. Trên nó là 3 con số dẫn dạng typographic (không tile): `2.79` mean · `76.7%` từ Khá trở lên · `2.2%` Xuất sắc. |
| **Supporting copy** | *"Trên thang 4.0, sinh viên có CPA cao nhất trong nhóm đạt 3.72. Không ai đạt 4.0. Ở đầu kia, người thấp nhất là 1.40."*<br><br>*"Con số 2.79 là trung bình của cả nhóm — nhưng như các phần sau sẽ cho thấy, nhóm này thực chất gồm những tập hợp con rất khác nhau, và 2.79 không mô tả đúng bất kỳ tập hợp con nào."* |
| **Interaction** | Hover từng band → tooltip: tên xếp loại, khoảng CPA, n, %, khoảng tin cậy 95%. |
| **Caveat hiển thị** | Footnote: *"n = 903. Hai sinh viên không có giá trị CPA trong dữ liệu gốc (cả hai đều thuộc nhóm không đủ điều kiện, 0 tín chỉ tích lũy) và được loại khỏi các phép tính về CPA nhưng vẫn giữ trong dataset."* |

---

### 03 — Distribution

**Headline**
> ## Một nửa số sinh viên nằm gọn trong khoảng 0.59 điểm

**Deck**
> Từ 2.52 đến 3.11. Phân phối CPA đơn đỉnh, gần đối xứng, và nén chặt hơn nhiều so với cảm giác thông thường về "khoảng cách học lực".

| Mục | Nội dung |
|---|---|
| **User question** | "CPA phân bố như thế nào? Khoảng cách giữa các sinh viên có lớn không?" |
| **Insight** | CORE-4 + SUP-7 |
| **Metrics chính xác** | Q1 `2.52` · median `2.79` · Q3 `3.11` · **IQR `0.59`** · MAD 0.30<br>min `1.40` · max `3.72` · range 2.32<br>skewness `−0.2391` · excess kurtosis `−0.2606` · Sarle BC 0.3859 (đơn đỉnh)<br>Percentiles: p10 `2.23` · p25 2.52 · p50 2.79 · p75 3.11 · p90 `3.34` · p99 3.64<br>Gini `0.0877`<br>Histogram bins 0.1 (đã tính sẵn, xem Phase 2 §O — dev dùng bộ số này, không tự bin lại) |
| **Visualization** | **Histogram bin 0.1 + đường KDE chồng lên.** Ba marker dọc: Q1, median, Q3, có nhãn giá trị. Vùng giữa Q1–Q3 tô nhạt để thể hiện IQR trực quan. Trục x từ 1.3 đến 3.8. |
| **Supporting copy** | *"Chênh lệch 0.1 điểm CPA nghe rất nhỏ, và về mặt thang đo thì đúng là nhỏ — hệ số Gini của CPA chỉ 0.0877, thấp hơn nhiều so với các biến như thu nhập. Nhưng vì phân phối nén chặt, 0.1 điểm vẫn có thể dịch chuyển một sinh viên qua vài chục bậc thứ hạng."*<br><br>*"Phân phối này bác bỏ giả thuyết bimodal: mặc dù nhóm gồm hai chuyên ngành có điểm trung bình cách nhau 0.54, biểu đồ gộp vẫn chỉ có một đỉnh (hệ số bimodality Sarle = 0.386, dưới ngưỡng 0.555). Đó chính là lý do phần tiếp theo quan trọng — cấu trúc thật bị che khuất hoàn toàn ở mức tổng."* |
| **Interaction** | Toggle "Hiện dải xếp loại" → phủ 5 vùng màu nhạt tương ứng 5 band. Mặc định tắt. |
| **Caveat hiển thị** | *"Đuôi dưới của phân phối này đã bị cắt: sinh viên rời hệ thống trước thời điểm xét đồ án không có trong dữ liệu. Phân phối thật của cả khóa tuyển sinh sẽ có đuôi dưới dài hơn và trung bình thấp hơn."* |

---

### 04 — Program comparison ⭐ section quan trọng nhất

**Headline**
> ## Hệ chất lượng cao có CPA trung bình cao hơn 0.106 điểm — cho đến khi so cùng chuyên ngành

**Deck**
> Khi tách theo chuyên ngành, dấu của chênh lệch đảo ngược. Đây không phải lỗi tính toán, mà là một đặc điểm thật của dữ liệu.

| Mục | Nội dung |
|---|---|
| **User question** | "Chương trình chất lượng cao có kết quả tốt hơn không?" |
| **Insight** | CORE-2 (+ CORE-5 ở cuối section) |
| **Metrics chính xác** | **Bước 1 — gộp:** CNTT CLC `2.8720` (n=215) vs CNTT `2.7663` (n=688) → **+0.1057**, 95% CI [+0.0436, +0.1688], Mann-Whitney p = 0.0067, Cohen's d = 0.246<br>**Bước 2 — cùng chuyên ngành:**<br>· CNPM: E22CNPM `2.7560` (n=137) vs D22CNPM `3.0199` (n=362) → **−0.2639**, CI [−0.3282, −0.1982], d = −0.861, p = 6.5×10⁻¹⁴<br>· HTTT: E22HTTT `2.9173` (n=40) vs D22HTTT `2.4847` (n=326) → **+0.4325**, CI [+0.2998, +0.5666], d = +1.066, p = 1.2×10⁻⁸<br>**Bước 3 — vì sao:** mean CLC 2.872 nằm giữa D22HTTT 2.485 và D22CNPM 3.020. Tỷ trọng CNPM trong CNTT = 0.526; ngưỡng hòa = **0.724**<br>**Đuôi phân phối (CORE-5):** chênh theo phân vị p10 `+0.234` · p50 `+0.040` · p90 +0.146 · p100 −0.010. Band <2.00: CLC **1.40%** vs CNTT **5.52%** |
| **Visualization** | **Ba bước, kích hoạt theo scroll — đây là trung tâm của cả trang.**<br>**Bước 1:** hai thanh ngang đơn giản, CNTT 2.766 và CLC 2.872, nhãn "+0.106". Cố tình trông như một kết luận hoàn chỉnh.<br>**Bước 2:** thanh tách đôi thành **slope chart 2 dòng** — dòng CNPM dốc **xuống** (3.020 → 2.756), dòng HTTT dốc **lên** (2.485 → 2.917). Mỗi đầu mút có error bar 95% CI và nhãn n.<br>**Bước 3:** **quantile-difference plot** — trục x là phân vị 0→100, trục y là hiệu CPA (CLC − CNTT), có đường zero. Đường cong cao ở hai đầu, gần zero ở giữa. |
| **Supporting copy** | Trước bước 2: *"Đây là con số thường được trích dẫn. Nó đúng về mặt số học. Nhưng nhóm CNTT không phải một khối đồng nhất — nó gồm hai chuyên ngành có kết quả rất khác nhau."*<br><br>Sau bước 2: *"Cùng tên chuyên ngành Công nghệ phần mềm, hệ chất lượng cao thấp hơn 0.264 điểm. Cùng tên chuyên ngành Hệ thống thông tin, hệ chất lượng cao cao hơn 0.433 điểm. Con số gộp +0.106 là kết quả của việc hai hiệu ứng ngược chiều triệt tiêu nhau theo tỷ trọng — không phải của một chênh lệch nhất quán."*<br><br>Sau bước 3: *"Chênh lệch giữa hai chương trình cũng không đều trên toàn phân phối. Ở phân vị 10, hệ chất lượng cao cao hơn 0.234 điểm; ở trung vị chỉ còn 0.040; ở đỉnh thì bằng nhau. Khác biệt nằm ở chỗ hệ chất lượng cao có ít sinh viên ở nhóm điểm thấp hơn (1.40% dưới 2.0, so với 5.52%) — chứ không phải có nhiều sinh viên xuất sắc hơn."* |
| **Interaction** | Scroll-triggered, 3 bước. Có nút "Xem lại từ đầu". **Không** cho phép nhảy thẳng tới bước 3 — thứ tự là nội dung. Trên mobile: 3 card xếp dọc, mỗi card một bước. |
| **Caveat hiển thị** | Callout, hiển thị cùng bước 2 và giữ nguyên đến hết section:<br>*"Không được đọc ngược thành 'hệ chất lượng cao dạy kém hơn ở chuyên ngành này, tốt hơn ở chuyên ngành kia'. Hai nhóm khác nhau về thành phần đầu vào trước khi khác nhau về bất cứ điều gì khác — xem phần tiếp theo."*<br><br>Footnote: *"Chuyên ngành E22TTNT (n=38) không có nhóm đối ứng bên hệ CNTT chuẩn nên không tham gia phép so sánh ghép cặp — tương đương 17.7% nhóm chất lượng cao nằm ngoài so sánh này. Riêng con số gộp +0.106 (p=0.0067) không vượt qua hiệu chỉnh đa so sánh Bonferroni; hai con số ghép cặp thì vượt."* |

---

### 05 — Track structure

**Headline**
> ## Chương trình đào tạo giải thích 1% khác biệt CPA. Chuyên ngành giải thích 34%.

**Deck**
> Nếu muốn biết vì sao hai sinh viên có CPA khác nhau, việc họ học hệ chuẩn hay chất lượng cao gần như không giúp gì. Việc họ ở chuyên ngành nào thì giúp rất nhiều.

| Mục | Nội dung |
|---|---|
| **User question** | "Vậy cái gì thực sự phân hoá kết quả học tập trong dữ liệu này?" |
| **Insight** | CORE-1 |
| **Metrics chính xác** | η²(`class_code`, k=18) `0.3522` · η²(`track`, k=5) **`0.3448`** · η²(`tttn_grade`) 0.2470 · r²(credits) 0.2792 · η²(`eligibility`) 0.1834 · η²(`birthplace` n≥20) 0.0699 · η²(`admission_major`) 0.0294 · **η²(`program`) `0.0109`** · η²(`is_off_cohort`) 0.0013<br>Tỷ lệ track/program = **31.6×** |
| **Visualization** | **Chart A — η² horizontal bar chart**, 9 biến sắp giảm dần, trục x 0–0.40. Thanh `track` và `program` highlight màu tương phản, các thanh còn lại xám.<br>**Chart B — cặp histogram small-multiple:** cùng một phân phối CPA vẽ 2 lần cạnh nhau. Trái: tô màu theo **chương trình** → hai màu trộn gần như đều nhau. Phải: tô màu theo **chuyên ngành** → các màu tách thành từng vùng rõ rệt. Đây là cặp hình thuyết phục nhất của cả trang. |
| **Supporting copy** | *"η² đo tỷ lệ phương sai CPA mà một cách phân nhóm giải thích được. Chia theo chương trình: 1.1%. Chia theo chuyên ngành: 34.5% — gấp hơn 31 lần."*<br><br>*"Điều này giải thích vì sao phần trước lại đảo dấu. Ranh giới thật trong dữ liệu không chạy giữa hai chương trình, mà chạy giữa các chuyên ngành. Khi gộp theo chương trình, ta đang trộn lẫn hai nhóm khác nhau rất xa và lấy trung bình của hỗn hợp đó."* |
| **Interaction** | Chart B có toggle "Tô màu theo: Chương trình / Chuyên ngành" — người dùng tự bấm để thấy sự khác biệt, thay vì chỉ được kể. |
| **Caveat hiển thị** | *"η² mô tả mức độ một cách phân nhóm tách được dữ liệu, không phải mức độ nhóm đó gây ra kết quả. Con số 34.5% phần lớn phản ánh cách sinh viên được phân vào chuyên ngành — xem ngay dưới."* |

---

### 05b — Bên trong một ngành

**Headline**
> ## Hai chuyên ngành của cùng một ngành cách nhau 0.54 điểm — và không một sinh viên CNPM nào dưới 2.43

**Deck**
> Cả 690 sinh viên hệ CNTT chuẩn đều vào trường bằng cùng một mã ngành. Nhưng phân phối điểm của hai chuyên ngành gần như không chồng lên nhau ở phần đuôi.

| Mục | Nội dung |
|---|---|
| **User question** | "Khác biệt giữa hai chuyên ngành lớn đến đâu, và nó đến từ đâu?" |
| **Insight** | CORE-3 |
| **Metrics chính xác** | D22CNPM `3.0199` (n=362, sd 0.2881) vs D22HTTT `2.4847` (n=326, sd 0.4042) → chênh **`0.5352`**<br>Cohen's d **`1.538`** · Cliff's δ 0.721 → P(CNPM > HTTT) = **0.860** · Mann-Whitney p = 5.1×10⁻⁶⁰<br>**Truncation:** min CNPM = **`2.43`** · `0/362` sinh viên CNPM dưới 2.43 · chỉ `1/362` (0.28%) dưới median HTTT · nhưng **52.5%** sinh viên HTTT nằm trên min của CNPM<br>Thành phần: `690/690` đều mã ngành CNTT (686 × B22DCCN + 4 × B21DCCN)<br>Bottom decile: D22HTTT chiếm 36.2% cohort nhưng **92.5%** decile thấp nhất (86/93); D22CNPM chiếm 40.0% nhưng **0%** |
| **Visualization** | **Ridgeline / overlapping density** hai chuyên ngành trên cùng trục CPA. Một **đường dọc đứt tại 2.43** với annotation trực tiếp trên chart: *"Không sinh viên CNPM nào dưới ngưỡng này"*. Hình này tự truyền tải bằng chứng mà không cần khẳng định nhân quả. |
| **Supporting copy** | *"Đuôi dưới của CNPM dừng đột ngột ở 2.43, trong khi HTTT trải xuống tới 1.65. Một phân phối bị cắt sắc như vậy thường là dấu hiệu của việc phân nhóm theo chính biến đang được đo."*<br><br>*"Nếu sinh viên được phân chuyên ngành dựa trên xếp hạng CPA, thì CPA là nguyên nhân của việc phân nhóm, chứ không phải kết quả của nó. Khi đó việc so sánh CPA giữa hai chuyên ngành trở thành vòng luẩn quẩn — giải thích kết quả bằng đúng thứ đã tạo ra nhóm."*<br><br>*"Cơ chế phân chuyên ngành hiện chưa được xác nhận. Cho đến khi có xác nhận từ nhà trường, đây phải được đọc như một quan sát về cấu trúc dữ liệu, không phải một đánh giá về hai chuyên ngành."* |
| **Interaction** | Hover trên ridgeline → hiện mật độ và số sinh viên trong bin tại vị trí đó, cho từng chuyên ngành. |
| **Caveat hiển thị** | 🔴 Callout nổi bật nhất trang: *"Đây là caveat quan trọng nhất của toàn bộ dự án. Chênh lệch này rất có thể là hệ quả của cách phân chuyên ngành, không phải của việc học ở chuyên ngành đó. Không được diễn giải thành đánh giá chất lượng hai chuyên ngành."* |

---

### 05c — Cấp lớp

**Headline**
> ## Không có lớp nào "tốt hơn" lớp nào — trong cùng chuyên ngành, 18 lớp không phân biệt được

**Deck**
> Chênh lệch điểm trung bình giữa các lớp cùng chuyên ngành chỉ 0.05–0.12, nhỏ hơn sai số. Giữa các chuyên ngành thì là 0.81.

| Mục | Nội dung |
|---|---|
| **User question** | "Lớp nào có kết quả tốt nhất?" — và câu trả lời là câu hỏi này không có nghĩa |
| **Insight** | CORE-8 |
| **Metrics chính xác** | Kruskal-Wallis trong từng chuyên ngành: D22CNPM (k=6) H=7.454 **p=0.1890** · D22HTTT (k=6) H=3.996 **p=0.5499** · E22CNPM (k=4) H=0.366 **p=0.9473**<br>Biên độ mean giữa các lớp cùng chuyên ngành: D22CNPM `0.118` (2.963–3.082) · D22HTTT `0.110` (2.433–2.543) · E22CNPM `0.047` (2.741–2.788)<br>Biên độ giữa các chuyên ngành: **`0.810`** (2.433 → 3.243)<br>η²(class) 0.3522 vs η²(track) 0.3448 → thêm 13 nhóm chỉ tăng **0.0074**<br>n mỗi lớp: 32–62 |
| **Visualization** | **Caterpillar plot:** 18 lớp trên trục y, chấm mean + thanh CI 95%, tô màu theo chuyên ngành. Sắp xếp **theo chuyên ngành rồi theo tên lớp** — **không** sắp theo mean. Người xem thấy các CI trong cùng chuyên ngành chồng lên nhau gần như hoàn toàn, còn giữa các chuyên ngành thì tách rời. |
| **Supporting copy** | *"Trong cả ba chuyên ngành có nhiều lớp, kiểm định Kruskal-Wallis đều không phát hiện khác biệt (p = 0.19, 0.55, 0.95). Thêm 13 nhóm lớp vào mô hình chỉ làm tăng khả năng giải thích thêm 0.7 điểm phần trăm."*<br><br>*"Vì lý do đó, trang này cố ý không xếp hạng lớp. Chênh lệch quan sát được giữa các lớp nhỏ hơn sai số đo, nhưng sẽ luôn bị đọc thành 'lớp này giỏi hơn lớp kia'."* |
| **Interaction** | Hover một lớp → n, mean, CI 95%, chuyên ngành. **Không** có sort control. **Không** hiển thị min/max cấp lớp (Phase 1, quy tắc F4). |
| **Caveat hiển thị** | *"'Không phân biệt được về mặt thống kê' không đồng nghĩa với 'giống hệt nhau'. Với khoảng 55 sinh viên mỗi lớp, khả năng phát hiện khác biệt nhỏ là thấp. Đây là bằng chứng về việc thiếu bằng chứng, không phải bằng chứng về sự đồng nhất."* |

---

### 06 — Composition

**Headline**
> ## 86% sinh viên hệ chất lượng cao không vào trường bằng mã ngành Công nghệ thông tin

**Deck**
> Hai chương trình khác nhau về thành phần đầu vào trước khi khác nhau về bất cứ điều gì khác. Đây là lời giải thích cho sự đảo dấu ở phần trước.

| Mục | Nội dung |
|---|---|
| **User question** | "Hai nhóm đang được so sánh có thực sự tương đương không?" |
| **Insight** | SUP-3 + SUP-2 |
| **Metrics chính xác** | CNTT CLC (n=215): mã ngành `DCVT` **96** (44.7%) · `DCDT` **50** (23.3%) · `DCAT` **34** (15.8%) · `DCCN` **29** (13.5%) · `DCKH` 4 · `DCCI` 1 · `DCDK` 1 → **186/215 = 86.5%** không phải mã ngành CNTT<br>CNTT chuẩn (n=690): **690/690 = 100%** mã ngành CNTT<br>CPA trong nội bộ CLC theo mã ngành: DCCN `3.114` (n=29) · DCAT `3.062` (n=34) · DCDT `2.800` (n=50) · DCVT `2.776` (n=96)<br>Nhóm IT (DCCN+DCAT) `3.086` (n=63) vs nhóm VT/ĐT (DCVT+DCDT) `2.784` (n=146) → chênh **0.302**, d = **0.824**, Kruskal p = 2×10⁻⁵ |
| **Visualization** | **Hai stacked bar ngang chồng nhau** (CNTT / CNTT CLC), mỗi bar chia theo mã ngành tuyển sinh. Bar CNTT là một khối đơn sắc; bar CLC chia thành 4 mảng lớn. Sự tương phản thị giác tự nói lên vấn đề.<br>Phía dưới: **dot plot** CPA trung bình theo mã ngành trong nội bộ CLC, có CI, chỉ hiện các nhóm n ≥ 20. |
| **Supporting copy** | *"Toàn bộ 690 sinh viên hệ CNTT chuẩn vào trường bằng mã ngành Công nghệ thông tin. Ở hệ chất lượng cao, chỉ 29 người như vậy — phần lớn còn lại đến từ Viễn thông (96), Điện tử (50) và An toàn thông tin (34)."*<br><br>*"Và mã ngành tuyển sinh vẫn tạo khác biệt bên trong hệ chất lượng cao: nhóm vào bằng mã CNTT hoặc An toàn thông tin có CPA trung bình 3.086, so với 2.784 ở nhóm vào bằng mã Viễn thông hoặc Điện tử — chênh 0.302 điểm."*<br><br>*"Mã ngành tuyển sinh phản ánh điểm đầu vào và lựa chọn ban đầu của sinh viên. Không biến nào trong số đó có mặt trong dataset này. Đó là biến kiểm soát then chốt bị thiếu."* |
| **Interaction** | Hover một mảng → mã ngành, tên đầy đủ, n, % trong chương trình, CPA trung bình (chỉ hiện nếu n ≥ 20; nếu nhỏ hơn ghi *"n quá nhỏ để hiển thị thống kê"*). |
| **Caveat hiển thị** | *"Các nhóm DCKH (n=4), DCCI (n=1), DCDK (n=1) quá nhỏ để phân tích và không được hiển thị thống kê riêng. Bảng thành phần vẫn tính đủ để tổng bằng 215."* |

---

### 07 — Eligibility

**Headline**
> ## 99.4% sinh viên CNPM đủ điều kiện làm đồ án. Ở HTTT là 83.5%.

**Deck**
> Nhưng CPA không phải thứ quyết định điều đó — 13% sinh viên không đủ điều kiện vẫn có CPA từ 2.5 trở lên, và người cao nhất trong nhóm đó đạt 3.37.

| Mục | Nội dung |
|---|---|
| **User question** | "Ai đi được tới đồ án tốt nghiệp, và điều gì quyết định?" |
| **Insight** | CORE-6 + CORE-7 |
| **Metrics chính xác** | **Theo chuyên ngành:** D22CNPM **99.45%** (360/362, CI [98.02, 99.93]) · E22HTTT 100% (40/40) · E22TTNT 100% (38/38) · E22CNPM 90.51% (124/137) · D22HTTT **83.54%** (274/328, CI [79.07, 87.38])<br>χ² qua 5 nhóm = 69.205, p = 3.3×10⁻¹⁴, Cramér's V = 0.2765 · CNPM vs HTTT chênh **15.91 pp**, Fisher p = 1.8×10⁻¹⁶<br>**Theo chương trình:** CNTT 91.88% vs CLC 93.95%, χ² p = **0.3946** → **không có khác biệt có ý nghĩa**<br>**CPA và điều kiện:** không đủ đk `2.1381` (n=67) vs đủ đk `2.8439` (n=836), d = 1.806<br>Nhưng `9/67` (**13.4%**) không đủ đk có CPA ≥ 2.5 · `3/67` có CPA ≥ 3.0 · max **`3.37`** (cao hơn 91.8% toàn nhóm)<br>**Tín chỉ:** đủ đk min = `69`, không đủ đk max = `140` → dải chồng lấn 69–140 có **154** sinh viên: **125 đủ điều kiện, 29 không**<br>69.4% đạt trần 146 TC; theo chuyên ngành: CNPM 93.1% · TTNT 84.2% · E22HTTT 57.5% · E22CNPM 56.2% · HTTT 48.5% |
| **Visualization** | **Chart A:** bar ngang tỷ lệ đủ điều kiện theo 5 chuyên ngành + error bar CI 95%. Trục x bắt đầu từ 75% với **nhãn cảnh báo trục bị cắt hiển thị rõ**. Bên cạnh là một thanh đối chiếu nhỏ "theo chương trình: 91.9% vs 94.0%, p = 0.39".<br>**Chart B:** **scatter CPA (y) × tín chỉ tích lũy (x)**, màu theo trạng thái đủ/không đủ điều kiện, jitter nhẹ. Highlight vùng chữ nhật 69–140 tín chỉ. Đây là chart cấp cá nhân duy nhất của cả trang. |
| **Supporting copy** | *"Chênh lệch giữa hai chuyên ngành là 15.91 điểm phần trăm. Giữa hai chương trình thì không có chênh lệch có ý nghĩa thống kê (p = 0.39) — thêm một lần nữa, ranh giới không nằm ở nơi người ta thường tìm."*<br><br>*"Sinh viên không đủ điều kiện có CPA thấp hơn rõ rệt. Nhưng quan hệ không phải một-một: trong dải 69 đến 140 tín chỉ tích lũy, có 125 sinh viên đủ điều kiện và 29 sinh viên không — cùng một khoảng tín chỉ, hai kết quả khác nhau."*<br><br>*"Điều đó có nghĩa là tiêu chí xét duyệt phụ thuộc vào những yếu tố không có trong dataset này. Chúng ta không quan sát được biến quyết định, nên không thể — và không nên — suy ngược ra quy tắc xét duyệt."* |
| **Interaction** | Chart A: toggle "Theo chuyên ngành / Theo chương trình".<br>Chart B: hover một điểm → **chỉ** CPA, số tín chỉ, trạng thái đủ điều kiện. **Tuyệt đối không** mã sinh viên, không mã lớp, không chuyên ngành (tổ hợp lớp + tín chỉ + CPA gần như định danh duy nhất). |
| **Caveat hiển thị** | *"Tỷ lệ 100% ở E22HTTT và E22TTNT dựa trên n = 40 và n = 38; cận dưới khoảng tin cậy 95% lần lượt là 91.2% và 90.8%. Không nên đọc là 'tuyệt đối'."*<br><br>*"Chỉ có 2 sinh viên CNPM không đủ điều kiện. Mọi tỷ số nguy cơ tính từ mẫu số này đều cực kỳ không ổn định — trang này trình bày chênh lệch điểm phần trăm thay vì tỷ số."*<br><br>*"Nhóm không đủ điều kiện chỉ có 69 người. Trang này không tách nhỏ nhóm đó theo lớp."* |

**Panel phụ trong section này — thay cho "Cohort patterns":**

> ### Vì sao không có biểu đồ xu hướng theo thời gian
> Dataset là một ảnh chụp tại một thời điểm xét đồ án, không có cột thời gian nào. Và 899 trong 905 sinh viên thuộc cùng khóa tuyển sinh 2022 — 6 người còn lại thuộc khóa 2021 (η² = 0.0013, quá nhỏ để phân tích). Vì vậy không thể so sánh giữa các khóa hay theo dõi diễn biến theo thời gian. Đây là kết luận có kiểm chứng, không phải một phần bị bỏ sót.

---

### 08 — Explore

**Headline**
> ## Tự kiểm chứng

**Deck**
> Mọi con số ở trên đều tính từ cùng một bộ 905 dòng. Lọc theo cách của bạn và xem phân phối thay đổi ra sao.

| Mục | Nội dung |
|---|---|
| **User question** | "Tôi có thể tự kiểm tra không, hoặc xem một lát cắt mà trang chưa trình bày?" |
| **Insight** | Không có — đây là công cụ. Giá trị của nó là **tính minh bạch**, không phải phát hiện mới. |
| **Filter cho phép** | `program` (CNTT / CNTT CLC / cả hai) · `track` (5 giá trị, multi-select) · `eligible_for_thesis` (đủ / không đủ / cả hai) · `credit_bucket` (146 / 143–145 / 131–142 / 101–130 / ≤100) · `cpa_range` (slider 1.4–3.8) · `admission_major_code` (chỉ các mã n ≥ 20: DCCN, DCVT, DCDT, DCAT) |
| **Filter KHÔNG cho phép** | ❌ `birthplace` (SUP-9 đã reject; 15 tỉnh có n < 10) · ❌ `birth_year` · ❌ tìm kiếm theo mã sinh viên · ❌ `class_code` như một filter **so sánh** (xem dưới) |
| **Xử lý `class_code`** | Cho phép **chọn một lớp** để highlight overlay lên phân phối của chuyên ngành chứa nó. **Không** cho chọn nhiều lớp cạnh nhau, **không** có bảng sắp xếp theo mean, **không** hiển thị min/max cấp lớp. Kèm dòng cố định: *"Các lớp trong cùng chuyên ngành không khác biệt có ý nghĩa thống kê (xem phần trên)."* |
| **Visualization** | Histogram CPA phản ứng theo filter (bin 0.1, trục x cố định 1.3–3.8 để so sánh được giữa các lần lọc) + một hàng summary: `n` · mean ± CI 95% · median · sd · IQR · % ≥ 2.5 · % đủ điều kiện. Phía sau hiện mờ phân phối của **toàn bộ 903** để làm mốc so sánh. |
| **Interaction bắt buộc** | 1. **Chặn cứng n < 10:** khi tổ hợp filter cho ra dưới 10 sinh viên → ẩn toàn bộ chart và số liệu, hiện: *"Chỉ có N sinh viên khớp bộ lọc này. Trang không hiển thị nhóm dưới 10 người để bảo vệ quyền riêng tư."*<br>2. **Luôn hiển thị `n`** cạnh mọi con số, không có ngoại lệ.<br>3. **Luôn hiển thị CI 95%** cho mean.<br>4. Cảnh báo mềm khi 10 ≤ n < 30: *"Cỡ mẫu nhỏ — khoảng tin cậy rộng."*<br>5. Nút "Đặt lại". Trạng thái filter phản ánh vào URL để chia sẻ được. |
| **Caveat hiển thị** | Cố định phía trên panel: *"Việc lọc ra một nhóm không biến nó thành một phát hiện. Bộ lọc càng nhiều điều kiện, khả năng bắt gặp một chênh lệch ngẫu nhiên càng cao. Mọi con số ở đây là mô tả của nhóm được lọc, không phải bằng chứng về nguyên nhân."* |

---

### 09 — Methodology

**Headline**
> ## Con số này đến từ đâu

Trình bày dạng **accordion 5 nhóm**, mặc định đóng hết. Không chart.

#### 9.1 Dataset & scope

| Mục | Nội dung |
|---|---|
| Nguồn | File Excel chính thức `DS-SV-DK-DATN-D22-KY-THUAT.xlsx`, một sheet `Data`, 2.023 dòng dữ liệu × 11 cột thực |
| Bản chất | Danh sách xét đăng ký đồ án tốt nghiệp khối kỹ thuật khóa D22 — không phải roster sinh viên tổng quát |
| Scope filter | Mã lớp khớp `^(D22CNPM\|D22HTTT\|E22)` → **905 dòng**, 18 lớp, 5 chuyên ngành |
| Ánh xạ chương trình | Mã lớp bắt đầu bằng `E` → **CNTT chất lượng cao**; bắt đầu bằng `D` → **CNTT**. Theo quy ước của nhà trường |
| Loại khỏi scope | 1.118 sinh viên thuộc 24 mã lớp của các ngành khác (Viễn thông, Điện tử, An toàn thông tin, Khoa học máy tính, Truyền thông đa phương tiện…) |

#### 9.2 Data cleaning

Liệt kê các quy tắc **thực sự ảnh hưởng tới con số hiển thị**, mỗi quy tắc một dòng, kèm lý do:

| Quy tắc | Lý do |
|---|---|
| CPA đọc từ text sang số, có assertion `0 ≤ CPA ≤ 4` | Cột gốc lưu toàn bộ dưới dạng chuỗi; nếu không ép kiểu, mọi phép trung bình và sắp xếp sẽ sai âm thầm |
| Chuỗi rỗng `''` → giá trị thiếu | 3 ô CPA trong file gốc là chuỗi rỗng, không phải null, nên lọt qua kiểm tra thiếu thông thường |
| **Không** điền khuyết CPA (2 dòng in-scope) | Cả 2 đều thuộc nhóm không đủ điều kiện với 0 tín chỉ — thiếu có cấu trúc, điền vào sẽ bịa dữ liệu |
| **Không** điền khuyết TTTN (53 dòng) | 100% giá trị thiếu nằm ở nhóm không đủ điều kiện — thiếu có cấu trúc |
| Chuẩn hóa khoảng trắng nơi sinh; gộp `TP. Hồ Chí Minh` → `Hồ Chí Minh` | `Hà  Nội` (hai dấu cách) đang bị đếm tách khỏi `Hà Nội` |
| **Không** loại bỏ giá trị ngoại lai | 2 outlier theo hàng rào IQR đều là sinh viên không đủ điều kiện với 24 và 6 tín chỉ — hợp lệ và giải thích được |
| Gắn cờ thay vì sửa/xóa dữ liệu bất thường | 6 sinh viên khóa 2021, 2 mã sinh viên sai định dạng — giữ nguyên, đánh dấu |
| Ngày sinh parse với định dạng `DD/MM/YYYY` tường minh | Tránh bị hiểu nhầm thành `MM/DD` |

#### 9.3 Metric definitions

| Metric | Định nghĩa hiển thị cho người đọc |
|---|---|
| **CPA** | Điểm trung bình chung tích lũy, thang 4.0. Trong dataset dao động 1.40–3.72. Cột gốc `Điểm TBCTL` |
| **Chuyên ngành (track)** | Suy ra từ mã lớp sau khi bỏ hậu tố số: `D22CNPM01` → `D22CNPM`. 5 giá trị |
| **Chương trình** | Suy ra từ ký tự đầu mã lớp: `E` → CNTT CLC, `D` → CNTT |
| **Mã ngành tuyển sinh** | 4 ký tự thứ 4–7 của mã sinh viên: `B22DCCN002` → `DCCN`. Khác với chuyên ngành |
| **Đủ điều kiện làm ĐATN** | Cột `Ghi chú` = `Làm ĐATN`. Giá trị còn lại là `Không đủ đk` |
| **Tín chỉ tích lũy** | Cột `Số TCTL`, 0–146. Trần chương trình là 146 |
| **η² (eta bình phương)** | Tỷ lệ phương sai CPA mà một cách phân nhóm giải thích được: SSB/(SSB+SSW). Từ 0 đến 1 |
| **Cohen's d** | Chênh lệch trung bình chia cho độ lệch chuẩn gộp. Quy ước: 0.2 nhỏ, 0.5 vừa, 0.8 lớn |
| **Cliff's δ** | Xác suất một sinh viên nhóm A cao hơn một sinh viên nhóm B, chuẩn hóa về [−1, 1] |
| **Khoảng tin cậy 95%** | Bootstrap 10.000 lần lặp cho trung bình/trung vị; Clopper-Pearson (binomial exact) cho tỷ lệ |

#### 9.4 Statistical methods

| Phép | Dùng ở đâu | Vì sao chọn |
|---|---|---|
| Mann-Whitney U | Mọi so sánh 2 nhóm về CPA | Không giả định phân phối chuẩn (Shapiro p = 4.3×10⁻⁵) |
| Welch t-test | Đối chiếu song song | Không giả định phương sai bằng nhau |
| Kruskal-Wallis | So sánh > 2 nhóm (lớp trong chuyên ngành, mã ngành trong CLC) | Phi tham số |
| Fisher exact / χ² | Tỷ lệ đủ điều kiện | Fisher cho bảng 2×2 có ô nhỏ |
| Bootstrap 10.000 lần, seed 42 | CI của trung bình, trung vị, hiệu trung bình | Không giả định phân phối |
| Hiệu chỉnh Bonferroni | Kiểm tra ~20 phép so sánh | Ngưỡng 0.0025. Nêu rõ kết quả nào vượt, kết quả nào không |

#### 9.5 Privacy

| Biện pháp | Chi tiết |
|---|---|
| Đã loại bỏ hoàn toàn | Họ tên, tên, ngày sinh đầy đủ, mã sinh viên gốc |
| Định danh giả | Mã sinh viên thay bằng HMAC-SHA256 có salt bí mật, giữ 12 ký tự hex. Salt không nằm trong mã nguồn |
| Chỉ giữ năm sinh | Họ tên + ngày sinh định danh duy nhất **100%** số dòng; ngày sinh + mã lớp định danh duy nhất **87.3%** |
| Ngưỡng chặn hiển thị | Mọi nhóm n < 10 bị ẩn, ở cả trang tĩnh lẫn phần Explore |
| Không hiển thị | Min/max CPA cấp lớp · xếp hạng lớp · xếp hạng cá nhân · breakdown nhóm không đủ điều kiện theo lớp |
| Biểu đồ cấp cá nhân duy nhất | Scatter ở section 07 — tooltip chỉ hiện CPA, tín chỉ, trạng thái. Không mã sinh viên, không lớp |
| Nơi sinh | Không dùng làm chiều phân tích công khai và không có trong bộ lọc |
| File gốc | Không commit vào repository công khai; metadata workbook (chứa tên thật người tạo/sửa) bị strip khỏi mọi file phái sinh |

---

### 10 — Những gì dataset này KHÔNG trả lời được

**Headline**
> ## Sáu câu hỏi trang này không trả lời — và vì sao

Danh sách, không chart. Mỗi mục: câu hỏi (in đậm) + lý do (một đoạn ngắn).

| # | Câu hỏi bị chặn | Lý do |
|---|---|---|
| 1 | **"Chương trình nào đào tạo tốt hơn?"** | Dữ liệu quan sát, một thời điểm, không có nhóm đối chứng, không có điểm đầu vào. Không thỏa mãn bất kỳ điều kiện nào cho suy luận nhân quả. Và như section 04 cho thấy, dấu của chênh lệch còn đảo khi đổi cách phân tầng. |
| 2 | **"Chuyên ngành nào tốt hơn?"** | Có bằng chứng mạnh rằng CPA là **tiêu chí phân chuyên ngành** chứ không phải kết quả của nó (đuôi dưới của CNPM cắt sắc tại 2.43). So sánh CPA giữa các chuyên ngành khi đó là vòng luẩn quẩn. |
| 3 | **"Sinh viên PTIT nói chung học thế nào?"** | Dataset chỉ gồm hai chương trình CNTT của một khóa. 1.118 sinh viên các ngành khác đã bị loại khỏi phạm vi. Không đại diện cho toàn trường, khối kỹ thuật, hay bất kỳ ngành nào khác. |
| 4 | **"Kết quả học tập thay đổi theo thời gian ra sao?"** | 899/905 sinh viên cùng khóa 2022; dataset không có trục thời gian. Không thể so sánh giữa các khóa. |
| 5 | **"Vì sao một số sinh viên không đủ điều kiện làm đồ án?"** | Trong cùng dải 69–140 tín chỉ có 125 người đủ điều kiện và 29 người không. Biến quyết định không có trong dataset. |
| 6 | **"Yếu tố nào ảnh hưởng đến CPA?"** | Điểm đầu vào, hoàn cảnh kinh tế - xã hội, giới tính, động lực, điểm từng học phần, giảng viên — không có biến nào trong dataset. Những gì quan sát được (tín chỉ tích lũy, điều kiện ĐATN, điểm TTTN) đều là **hệ quả** của kết quả học tập, không phải nguyên nhân. |

**Đóng lại bằng:**
> *"Ba câu hỏi vẫn đang chờ xác nhận từ nhà trường: cơ chế phân sinh viên vào hai chuyên ngành CNPM và HTTT; ý nghĩa đầy đủ của cột TTTN; và diện sinh viên của 2 mã sinh viên có định dạng khác biệt. Câu hỏi đầu tiên ảnh hưởng trực tiếp đến cách đọc phần 05."*

---

## 3. Headline registry

Mọi headline phải truy vết được về một con số đã tính. Dev **không** được sửa headline mà không sửa cả evidence tương ứng.

| Section | Headline | Con số nền | Nguồn |
|---|---|---|---|
| 00 | 905 sinh viên CNTT, một khóa, tại thời điểm xét đồ án tốt nghiệp | n = 905; 899/905 khóa 2022 | Audit §1.4 |
| 01 | Đây là danh sách xét đồ án tốt nghiệp — không phải toàn bộ khóa tuyển sinh | 2.023 → 905; tên file `DS-SV-DK-DATN` | Audit §1.3–1.4 |
| 02 | Ba phần tư đạt loại Khá trở lên. Một trong 45 người đạt Xuất sắc. | 76.74% ≥ 2.5; 20/903 = 2.21% ≈ 1/45.2 | CORE-4 |
| 03 | Một nửa số sinh viên nằm gọn trong khoảng 0.59 điểm | IQR = 0.59 (Q1 2.52, Q3 3.11) | CORE-4 |
| 04 | Hệ chất lượng cao có CPA trung bình cao hơn 0.106 điểm — cho đến khi so cùng chuyên ngành | +0.1057 gộp; −0.2639 / +0.4325 ghép cặp | CORE-2 |
| 05 | Chương trình đào tạo giải thích 1% khác biệt CPA. Chuyên ngành giải thích 34%. | η² 0.0109 vs 0.3448 | CORE-1 |
| 05b | Hai chuyên ngành của cùng một ngành cách nhau 0.54 điểm — và không một sinh viên CNPM nào dưới 2.43 | 0.5352; min = 2.43, 0/362 | CORE-3 |
| 05c | Không có lớp nào "tốt hơn" lớp nào — trong cùng chuyên ngành, 18 lớp không phân biệt được | KW p = 0.189 / 0.550 / 0.947 | CORE-8 |
| 06 | 86% sinh viên hệ chất lượng cao không vào trường bằng mã ngành Công nghệ thông tin | 186/215 = 86.5% | SUP-3 |
| 07 | 99.4% sinh viên CNPM đủ điều kiện làm đồ án. Ở HTTT là 83.5%. | 360/362; 274/328 | CORE-6 |
| 10 | Sáu câu hỏi trang này không trả lời — và vì sao | 6 mục, mỗi mục có evidence riêng | §4 Phase 2 |

**Headline bị cấm** (generic hoặc vượt quá evidence):

| ❌ Không dùng | ✅ Dùng thay |
|---|---|
| "CPA Distribution" | "Một nửa số sinh viên nằm gọn trong khoảng 0.59 điểm" |
| "Program Comparison" | "…cao hơn 0.106 điểm — cho đến khi so cùng chuyên ngành" |
| "Hệ chất lượng cao vượt trội" | "Hệ chất lượng cao có CPA trung bình cao hơn 0.106 điểm" |
| "Chuyên ngành CNPM đào tạo hiệu quả hơn" | "Hai chuyên ngành cách nhau 0.54 điểm — và không SV CNPM nào dưới 2.43" |
| "Class Performance Ranking" | "Không có lớp nào 'tốt hơn' lớp nào" |
| "Key Metrics" / "Insights" / "Data Explorer" | Tên mô tả nội dung thật của section |

---

## 4. Language rules

Áp dụng cho **toàn bộ** copy, tooltip, nhãn trục, alt text.

| Cấm | Cho phép |
|---|---|
| "tốt hơn", "kém hơn", "vượt trội", "yếu hơn" | "cao hơn / thấp hơn **trong dataset này**" |
| "dạy tốt hơn", "chất lượng đào tạo cao hơn" | "có điểm trung bình tích lũy cao hơn" |
| "chương trình X hiệu quả hơn" | "nhóm X có median CPA cao hơn nhóm Y" |
| "dẫn tới", "gây ra", "ảnh hưởng tới", "tác động" | "liên hệ với", "tương quan với", "đi kèm với" |
| "sinh viên giỏi / sinh viên yếu" | "sinh viên có CPA cao / thấp" |
| "chứng minh", "khẳng định" | "cho thấy", "phù hợp với", "gợi ý" |
| "sinh viên PTIT" (khi nói về dataset) | "sinh viên hai chương trình CNTT khóa 2022 trong dataset này" |

**Quy tắc trình bày số:**
- CPA luôn 2 chữ số thập phân (`2.79`), khớp độ chính xác dữ liệu gốc.
- Chênh lệch CPA 3 chữ số khi < 0.1 (`+0.040`), 3 chữ số nói chung để nhất quán (`+0.106`).
- Tỷ lệ 1 chữ số thập phân (`76.7%`); trong bảng chi tiết cho phép 2 (`76.74%`).
- p-value: `p < 0.001` khi rất nhỏ; ghi chính xác khi nằm giữa 0.001 và 0.1 (`p = 0.0067`).
- **Mọi tỷ lệ phải đi kèm mẫu số** ít nhất một lần: `86.5% (186/215)`.
- **Mọi giá trị trung bình nhóm phải đi kèm n.**

---

## 5. Design direction

### 5.1 Nguyên tắc chống-dashboard

| Làm | Không làm |
|---|---|
| Một cột nội dung hẹp (~680px), chart tràn rộng hơn khi cần | Grid nhiều panel cạnh nhau |
| Chart nằm **trong** mạch văn, mỗi chart một ý | Hàng KPI tile ở đầu trang |
| Nhiều khoảng trắng dọc giữa các section | Nhồi tối đa thông tin mỗi màn hình |
| Typography là yếu tố chính; headline lớn, deck rõ | Icon set, badge, gauge, donut, speedometer |
| Bảng màu giới hạn: 1 màu cho CNTT, 1 cho CLC, 5 sắc độ cho 5 chuyên ngành, xám cho nền | Bảng màu rực rỡ nhiều màu không mang nghĩa |
| Chú thích trực tiếp trên chart (direct labeling) | Legend tách rời buộc mắt di chuyển qua lại |
| Chỉ section 08 có control | Filter bar cố định toàn trang |

### 5.2 Chart inventory

| ID | Loại | Section | Ghi chú kỹ thuật |
|---|---|---|---|
| V-00 | Density ridge trang trí | 00 | Không tương tác, không trục |
| V-01 | Funnel 2 bước | 01 | Tĩnh |
| V-02 | Stacked bar 100%, 5 band | 02 | Direct label n + % |
| V-03 | Histogram bin 0.1 + KDE | 03 | Dùng bộ bin đã tính sẵn ở Phase 2 §O |
| V-04a | Bar 2 nhóm | 04 bước 1 | |
| V-04b | **Slope chart 2 dòng + CI** | 04 bước 2 | Chart quan trọng nhất trang |
| V-04c | Quantile-difference plot | 04 bước 3 | Trục y có đường zero |
| V-05a | η² horizontal bar, 9 biến | 05 | Highlight 2 thanh |
| V-05b | Cặp histogram small-multiple | 05 | Toggle cách tô màu |
| V-05c | Ridgeline 2 chuyên ngành | 05b | Đường dọc annotation tại 2.43 |
| V-05d | Caterpillar 18 lớp + CI | 05c | **Không** sort theo mean |
| V-06a | 2 stacked bar thành phần | 06 | |
| V-06b | Dot plot + CI, chỉ n ≥ 20 | 06 | |
| V-07a | Bar tỷ lệ + CI, trục cắt | 07 | Nhãn cảnh báo trục cắt |
| V-07b | Scatter CPA × tín chỉ | 07 | Chart cấp cá nhân duy nhất; tooltip hạn chế |
| V-08 | Histogram phản ứng theo filter | 08 | Trục x cố định; nền là phân phối tổng |

**Yêu cầu chung cho mọi chart:**
- Hiển thị `n` trên hoặc cạnh chart, không giấu trong tooltip.
- Mọi ước lượng trung bình/tỷ lệ có CI 95%.
- Trục y của biểu đồ cột **bắt đầu từ 0**, trừ V-07a (bắt buộc có nhãn cảnh báo).
- Alt text mô tả **phát hiện**, không mô tả hình dạng: *"Biểu đồ cho thấy chuyên ngành CNPM không có sinh viên nào dưới CPA 2.43"*, không phải *"Biểu đồ mật độ hai đường"*.
- Màu không được là kênh thông tin duy nhất — kèm nhãn hoặc kiểu nét.
- Responsive: dưới 640px, slope chart và caterpillar chuyển sang dạng danh sách có thanh ngang.

### 5.3 Điều hướng

Sidebar mảnh bên phải, chỉ tên section, highlight vị trí hiện tại. **Không** đánh số dạng "1/10", không progress bar dạng phần trăm. Trên mobile: ẩn, thay bằng nút "Mục lục" nổi.

---

## 6. Build order

Ưu tiên theo giá trị nội dung, không theo độ dễ:

| Đợt | Nội dung | Vì sao trước |
|---|---|---|
| 1 | Section 01, 02, 03 + 09, 10 | Khung trung thực phải có trước mọi so sánh. Không bao giờ deploy section 04 khi chưa có 10 |
| 2 | Section 04 + 05 (gồm 05b, 05c) | Lõi lập luận |
| 3 | Section 06, 07 | Chiều sâu |
| 4 | Section 00 hero + section 08 Explore | Hero cần biết trang hoàn chỉnh trông ra sao; Explore cần toàn bộ ngữ cảnh đã có mặt |

**Điều kiện chặn deploy:**
- ❌ Không deploy section 04 nếu section 10 chưa live.
- ❌ Không deploy section 08 nếu chưa có chặn cứng n < 10.
- ❌ Không deploy bất kỳ chart nào chưa hiển thị `n`.

---

## 7. Cần chuẩn bị cho phase sau

**Data artifact frontend sẽ tiêu thụ** (chưa build ở phase này):

| File | Nội dung |
|---|---|
| `students_clean.json` | 905 bản ghi đã ẩn danh, đúng schema Phase 1 §10 — cho section 08 và V-07b |
| `aggregates.json` | Toàn bộ con số đã tính sẵn của section 02–07, để trang tĩnh không phải tính lại và không thể lệch khỏi tài liệu này |
| `histogram_bins.json` | Bin 0.1 toàn nhóm + theo chương trình + theo chuyên ngành |
| `copy.json` | Toàn bộ headline, deck, supporting copy, caveat — tách khỏi code để review nội dung độc lập |

**Yêu cầu bắt buộc:** mọi con số hiển thị trên site phải khớp `docs/insight-discovery.md`. Nếu phát sinh chênh lệch, tài liệu Phase 2 là chuẩn — sửa code, không sửa tài liệu.

---

## Phụ lục — Truy vết section ↔ insight

| Section | Core/Supporting insight sử dụng |
|---|---|
| 01 | Audit §1.3, §1.4 |
| 02 | CORE-4 |
| 03 | CORE-4, SUP-7 |
| 04 | **CORE-2**, CORE-5 |
| 05 | **CORE-1** |
| 05b | **CORE-3**, SUP-6 |
| 05c | **CORE-8** |
| 06 | **SUP-3**, SUP-2 |
| 07 | **CORE-6**, **CORE-7**, SUP-4, SUP-5, SUP-10 |
| 08 | — (công cụ) |
| 09 | Audit §2, §5, §6, §7 · Phase 2 §7 |
| 10 | Phase 2 §4, §7 |

**Insight chưa dùng ở section nào:** SUP-1 (E22TTNT, n=38) và SUP-8 (TTTN, ý nghĩa chưa xác nhận) xuất hiện dưới dạng dữ liệu trong section 05c/08 nhưng **không** được nâng thành headline hay chart riêng — đúng như rào cản đã đặt ở Phase 2. SUP-9 (nơi sinh) bị loại hoàn toàn khỏi sản phẩm.
