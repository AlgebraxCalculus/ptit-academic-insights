# Technical Architecture — PTIT Academic Insights

**Phase:** 4 — Technical architecture
**Date:** 2026-09-11
**Inputs:** `docs/data-audit.md` · `docs/insight-discovery.md` · `docs/website-spec.md`
**Status:** Specification only. Chưa implement.

---

## 0. Architecture decision summary

| Quyết định | Chọn | Vì sao |
|---|---|---|
| Kiến trúc tổng thể | **Static site + build-time data pipeline** | Dataset là **một file Excel bất biến, 905 dòng**. Không có write path, không có auth, không có realtime. Backend hoặc database sẽ là chi phí thuần túy không đổi lấy được gì |
| Backend | **Không có** | Xem trên |
| Database | **Không có** | 905 dòng × 5 trường = 2.2 KB sau nén. Nhỏ hơn logo trang |
| Framework | **Astro 5** (static output) | Zero JS mặc định; chỉ hydrate đúng những chart cần tương tác (islands). Phù hợp chính xác với một trang chủ yếu là văn bản + vài chart tương tác |
| Ngôn ngữ frontend | **TypeScript** | Schema dữ liệu sinh từ pipeline; type mismatch phải fail lúc build, không phải lúc chạy |
| Chart library | **D3 (modules) + SVG tự vẽ**, không dùng chart lib đóng gói | 16 chart trong spec thì 6 cái (slope + CI, quantile-difference, ridgeline, caterpillar, η² bar có highlight, small-multiple toggle) không có sẵn trong bất kỳ chart lib nào. Ép chúng vào Chart.js/Recharts sẽ tốn công hơn là vẽ trực tiếp |
| Data processing | **Python 3.13 + pandas + scipy** | Đúng stack đã dùng ở Phase 1–2. Mọi con số trong hai tài liệu kia sinh ra từ đây; đổi stack là tự tạo rủi ro lệch số |
| Deployment | **Cloudflare Pages** (thay thế: GitHub Pages) | Static hosting + CDN toàn cầu + Brotli + preview per-PR, miễn phí. Không cần compute |
| Row-level data lên client | **Có, nhưng đã rút gọn trường** — xem §9.2 | Cần cho Explore và scatter V-07b. Nhưng bộ trường trong `website-spec.md` **phải bị thu hẹp**, lý do đo được ở §9.2 |

### 0.1 Thay đổi bắt buộc so với `website-spec.md`

Đo k-anonymity trên đúng bộ trường mà spec đề xuất gửi xuống client cho ra kết quả không chấp nhận được. **Ba điều chỉnh sau là bắt buộc**, chi tiết và số liệu ở §9.2:

| # | Spec Phase 3 nói | Kiến trúc này quyết định | Lý do |
|---|---|---|---|
| 1 | `students_clean.json` gồm cả `class_code` và `tttn_grade` | **Bỏ `class_code` và `tttn_grade` khỏi payload row-level** | Kèm `class_code`, **85.1%** số dòng trở thành duy nhất → suy ngược ra được ai không đủ điều kiện tốt nghiệp. Bỏ đi còn **49.5%** |
| 2 | Explore cho "chọn một lớp để highlight overlay lên phân phối" | **Overlay bằng marker mean ± CI từ aggregate**, không phải điểm cá nhân của lớp | Giữ nguyên ý đồ ("lớp tôi nằm đâu") mà không cần gửi class-level rows |
| 3 | Section 05c caterpillar 18 lớp | Giữ nguyên — nhưng đọc từ `aggregates.json` | 18 lớp đều có n ≥ 32, an toàn ở mức tổng hợp |

---

## 1. Architecture diagram

```
┌─────────────────────────── BUILD TIME (offline, thủ công) ──────────────────────────┐
│                                                                                      │
│   data/raw/DS-SV-DK-DATN-D22-KY-THUAT.xlsx        ◄── .gitignore, KHÔNG commit       │
│                    │                                                                 │
│                    ▼                                                                 │
│        ┌───────────────────────┐                                                     │
│        │ 1. ingest + validate  │  schema check · assert 0<=CPA<=4 · row/col count    │
│        │    (pandera)          │  → FAIL BUILD nếu file lệch khỏi audit              │
│        └───────────┬───────────┘                                                     │
│                    ▼                                                                 │
│        ┌───────────────────────┐                                                     │
│        │ 2. clean              │  rules A1-A4, D1, E1-E4 của data-audit.md           │
│        └───────────┬───────────┘                                                     │
│                    ▼                                                                 │
│        ┌───────────────────────┐                                                     │
│        │ 3. scope + derive     │  rule B1 (905 rows) · C1-C7 derived fields          │
│        └───────────┬───────────┘                                                     │
│                    ▼                                                                 │
│         data/processed/students_clean.parquet    ◄── .gitignore (còn quasi-ID)       │
│                    │                                                                 │
│         ┌──────────┴──────────┐                                                      │
│         ▼                     ▼                                                      │
│  ┌─────────────┐      ┌─────────────────┐                                            │
│  │ 4. metrics  │      │ 5. privacy gate │  drop class_code + tttn · k-anon check     │
│  │  (scipy)    │      │                 │  · min group size 10 · FAIL nếu vi phạm    │
│  └──────┬──────┘      └────────┬────────┘                                            │
│         ▼                      ▼                                                      │
│  ┌─────────────────────────────────────┐                                             │
│  │ 6. emit + validate JSON (jsonschema)│                                             │
│  └──────────────────┬──────────────────┘                                             │
│                     ▼                                                                │
│   src/data/  aggregates.json · histograms.json · rows.json · meta.json               │
│                     │                          ◄── ĐƯỢC commit, đã ẩn danh           │
└─────────────────────┼────────────────────────────────────────────────────────────────┘
                      ▼
┌─────────────────── BUILD TIME (CI, tự động) ────────────────────────────────────────┐
│   Astro build  →  pre-render toàn bộ 1 trang HTML                                    │
│   · section 01-07, 09, 10 render sẵn thành HTML tĩnh (0 JS)                          │
│   · SVG chart tĩnh cũng render sẵn ở server                                          │
│   · chỉ 5 island được hydrate (xem §7.2)                                             │
└──────────────────────────────┬───────────────────────────────────────────────────────┘
                               ▼
┌─────────────────── RUNTIME (trình duyệt) ───────────────────────────────────────────┐
│   Cloudflare CDN  →  HTML tĩnh + ~2.2 KB rows.json (gzip) + ~35 KB JS islands        │
│   Không API call · không backend · không cookie · không analytics bên thứ ba         │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

**Đặc điểm quan trọng:** bước 1–6 chạy **thủ công trên máy người có quyền truy cập file gốc**, không chạy trong CI. File `.xlsx` không bao giờ rời khỏi máy đó. CI chỉ thấy các file JSON đã ẩn danh đã được commit.

---

## 2. Tech stack

### 2.1 Data pipeline

| Thành phần | Chọn | Phiên bản | Ghi chú |
|---|---|---|---|
| Ngôn ngữ | Python | 3.13.2 | Đã dùng ở Phase 1–2 |
| Đọc Excel | openpyxl | 3.1.5 | `data_only=True` |
| Xử lý | pandas | 3.0.1 | |
| Thống kê | scipy | 1.17.1 | Mann-Whitney, Kruskal, Fisher, χ², Levene |
| Số học | numpy | 2.4.2 | Bootstrap với `default_rng(42)` |
| Validation đầu vào | **pandera** | ≥0.20 | Schema contract cho DataFrame |
| Validation đầu ra | **jsonschema** | ≥4.23 | Kiểm JSON trước khi ghi |
| Lưu trung gian | pyarrow (parquet) | ≥17 | |
| Quản lý môi trường | **uv** | ≥0.5 | Lockfile, tái lập chính xác |
| Test | pytest | ≥8 | |
| Lint/format | ruff | ≥0.7 | |

### 2.2 Frontend

| Thành phần | Chọn | Ghi chú |
|---|---|---|
| Framework | **Astro 5**, `output: 'static'` | |
| UI island | **Preact** qua `@astrojs/preact` | 3 KB thay vì 45 KB của React; đủ cho 5 island |
| Ngôn ngữ | TypeScript, `strict: true` | |
| Chart | **d3-scale, d3-shape, d3-array, d3-axis** (chỉ module cần) | ~15 KB gzip. Không import `d3` trọn gói |
| Styling | **CSS thuần + custom properties** | Không cần Tailwind cho một trang; design token khai báo tường minh |
| Font | Được self-host, `font-display: swap` | Không gọi Google Fonts (privacy + latency) |
| Test unit | Vitest | Logic filter, format số |
| Test e2e | Playwright | Ngưỡng n<10, scroll reveal, responsive |
| Accessibility | axe-core trong CI | |

### 2.3 Những gì cố ý KHÔNG dùng

| Không dùng | Vì sao |
|---|---|
| React / Next.js | Không có route động, không có server component, không có data fetching. Next.js là bộ máy thừa cho một trang tĩnh |
| Chart.js / Recharts / Plotly / ECharts | 6/16 chart trong spec không tồn tại trong các thư viện này (slope+CI, quantile-difference, ridgeline, caterpillar không sort, η² highlight bar, small-multiple toggle). Plotly còn nặng ~1 MB |
| Tailwind | Một trang, một bảng màu. Utility class không đem lại gì ngoài build step |
| Database (bất kỳ) | 905 dòng, read-only, bất biến |
| API / serverless function | Không có gì để tính lúc chạy |
| CMS | Nội dung nằm trong `copy.json`, review qua PR |
| Google Analytics / bất kỳ tracker bên thứ ba nào | Đây là trang về dữ liệu sinh viên; gửi hành vi người đọc cho bên thứ ba là mâu thuẫn với chính lập trường của trang |

---

## 3. Folder structure

```
ptit-academic-insights/
├── data/
│   ├── raw/
│   │   └── DS-SV-DK-DATN-D22-KY-THUAT.xlsx     🚫 .gitignore — chứa PII
│   ├── interim/
│   │   └── students_clean.parquet              🚫 .gitignore — còn quasi-identifier
│   └── reference/
│       └── birthplace_mapping.csv              ✅ commit — bảng mapping có version (rule E2)
│
├── pipeline/
│   ├── pyproject.toml                          uv project, pinned deps
│   ├── uv.lock
│   ├── config.py                               hằng số: scope regex, ngưỡng, seed, đường dẫn
│   ├── schemas.py                              pandera schema cho raw + clean
│   ├── s1_ingest.py                            đọc xlsx → validate → DataFrame thô
│   ├── s2_clean.py                             rules A1-A4, D1, E1-E4
│   ├── s3_scope.py                             rule B1 + derived fields C1-C7
│   ├── s4_metrics.py                           mọi thống kê của insight-discovery.md
│   ├── s5_privacy.py                           privacy gate — xem §9.3
│   ├── s6_emit.py                              ghi JSON + validate bằng jsonschema
│   ├── run.py                                  orchestrator: chạy s1→s6, in báo cáo
│   ├── schema/                                 JSON Schema cho từng file output
│   │   ├── aggregates.schema.json
│   │   ├── histograms.schema.json
│   │   ├── rows.schema.json
│   │   └── meta.schema.json
│   └── tests/
│       ├── test_cleaning.py                    quy tắc cleaning giữ đúng hành vi
│       ├── test_metrics.py                     ⭐ so từng con số với insight-discovery.md
│       ├── test_privacy.py                     ⭐ k-anon, min group size, trường bị cấm
│       └── test_schema.py
│
├── site/
│   ├── package.json
│   ├── astro.config.mjs
│   ├── tsconfig.json
│   ├── public/
│   │   ├── fonts/
│   │   └── og-image.png
│   └── src/
│       ├── data/                               ✅ commit — output của pipeline
│       │   ├── aggregates.json
│       │   ├── histograms.json
│       │   ├── rows.json
│       │   ├── meta.json
│       │   └── copy.json                       toàn bộ text, tách khỏi code
│       ├── types/
│       │   └── data.d.ts                       ⭐ sinh tự động từ JSON Schema
│       ├── lib/
│       │   ├── format.ts                       quy tắc định dạng số của spec §4
│       │   ├── scales.ts                       thang màu, thang trục dùng chung
│       │   ├── stats.ts                        chỉ filter + đếm; KHÔNG tính lại thống kê
│       │   └── guards.ts                       ngưỡng chặn n<10
│       ├── components/
│       │   ├── charts/                         một file cho mỗi V-xx của spec §5.2
│       │   │   ├── DensityRidge.astro          V-00  static
│       │   │   ├── ScopeFunnel.astro           V-01  static
│       │   │   ├── BandBar.astro               V-02  static
│       │   │   ├── CpaHistogram.astro          V-03  static (+ toggle island)
│       │   │   ├── ProgramReveal.tsx           V-04a/b/c  🏝️ island
│       │   │   ├── EtaSquaredBar.astro         V-05a static
│       │   │   ├── ColorByToggle.tsx           V-05b 🏝️ island
│       │   │   ├── TrackRidgeline.astro        V-05c static
│       │   │   ├── ClassCaterpillar.astro      V-05d static (hover qua CSS + <title>)
│       │   │   ├── CompositionBars.astro       V-06a static
│       │   │   ├── MajorDotPlot.astro          V-06b static
│       │   │   ├── EligibilityBars.tsx         V-07a 🏝️ island (toggle)
│       │   │   └── CpaCreditScatter.tsx        V-07b 🏝️ island
│       │   ├── explore/
│       │   │   ├── ExplorePanel.tsx            V-08  🏝️ island
│       │   │   ├── FilterControls.tsx
│       │   │   └── SmallSampleGuard.tsx
│       │   └── layout/
│       │       ├── Section.astro
│       │       ├── Headline.astro
│       │       ├── Caveat.astro
│       │       └── SectionNav.astro
│       ├── sections/                           một file cho mỗi section của spec §2
│       │   ├── 00-hero.astro        ... 10-limits.astro
│       │   ├── 09-methodology.astro
│       │   └── 10-limits.astro
│       ├── styles/
│       │   ├── tokens.css                      màu, spacing, typography scale
│       │   └── global.css
│       └── pages/
│           └── index.astro                     một trang duy nhất
│
├── docs/
│   ├── data-audit.md                Phase 1
│   ├── insight-discovery.md         Phase 2
│   ├── website-spec.md              Phase 3
│   └── architecture.md              Phase 4 — tài liệu này
│
├── .github/workflows/
│   ├── ci.yml                       lint · test · build · axe · kiểm file bị cấm
│   └── deploy.yml                   deploy Cloudflare Pages khi merge vào main
├── .gitignore
└── README.md
```

**Vì sao tách `pipeline/` và `site/`:** hai runtime khác nhau (Python / Node), hai vòng đời khác nhau (pipeline chạy khi dữ liệu đổi — hiếm; site build mỗi lần đổi nội dung — thường xuyên), hai mức nhạy cảm khác nhau (pipeline chạm PII, site không bao giờ). Ranh giới giữa chúng chính là thư mục `site/src/data/` đã được ẩn danh.

---

## 4. Data pipeline

### 4.1 Tổng quan các bước

| Bước | Input | Output | Fail điều kiện |
|---|---|---|---|
| **S1 ingest** | `raw/*.xlsx` | DataFrame 2.023×11 | Sai số dòng/cột · thiếu header kỳ vọng · sheet ≠ `Data` |
| **S2 clean** | DF thô | DF đã sạch | Assertion `0 ≤ CPA ≤ 4` thất bại · parse ngày thất bại |
| **S3 scope+derive** | DF sạch | DF 905 dòng + 18 trường | Số dòng in-scope ≠ 905 · xuất hiện track lạ |
| **S4 metrics** | DF 905 | dict thống kê | Con số lệch khỏi giá trị chốt ở Phase 2 |
| **S5 privacy** | DF 905 + metrics | DF đã lược trường + báo cáo | Trường bị cấm còn sót · nhóm n<10 lọt ra · k-anon vượt ngưỡng |
| **S6 emit** | tất cả | 4 file JSON | jsonschema không hợp lệ |

### 4.2 S1 — Ingest & validation

Đọc `sheet="Data"`, `min_col=1, max_col=11`, bỏ dòng toàn null (rule A1, A2).

**Pandera schema cho dữ liệu thô** — mục đích là *phát hiện file gốc đã thay đổi*, không phải làm sạch:

| Kiểm tra | Giá trị kỳ vọng | Mức |
|---|---|---|
| Số sheet | 1, tên `Data` | 🔴 fail |
| Số dòng dữ liệu | 2.023 | 🟡 cảnh báo + yêu cầu xác nhận thủ công |
| Header dòng 1 (cột A–K) | khớp danh sách đã chốt ở audit §2 | 🔴 fail |
| `Mã SV` | không null, unique, khớp `^[A-Z]\d{2}DC[A-Z]{2,3}\d{3}B?$` | 🔴 fail |
| `Mã lớp` | không null, ⊆ 42 mã đã biết | 🟡 cảnh báo (mã mới → phải cập nhật scope) |
| `Điểm TBCTL` | chuỗi khớp `^\d\.\d{2}$` hoặc rỗng | 🔴 fail |
| `Ghi chú` | ⊆ {`Làm ĐATN`, `Không đủ đk`} | 🔴 fail |
| `Số TCTL` | int 0–146 hoặc null | 🔴 fail |

Lý do đặt gate cứng ở đây: toàn bộ `insight-discovery.md` giả định một hình dạng dữ liệu cụ thể. Nếu file gốc đổi, pipeline **phải dừng** thay vì âm thầm tạo ra con số mới mâu thuẫn với tài liệu.

### 4.3 S2 — Cleaning

Thực thi đúng các rule đã chốt ở `data-audit.md` §6, không thêm không bớt:

| Rule | Hành động |
|---|---|
| A3 | `Điểm TBCTL` → float, `errors='coerce'`, sau đó assert `0 ≤ CPA ≤ 4` |
| A4 | `Ngày sinh` parse `format='%d/%m/%Y'` tường minh |
| D1 | chuỗi rỗng `''` → `NA` ở mọi cột text |
| E1 | `Nơi sinh`: gộp khoảng trắng liên tiếp, trim |
| E2 | `Nơi sinh`: áp `reference/birthplace_mapping.csv` |
| E4 | `dob_implausible` = năm sinh ∉ [1990, 2010] — **gắn cờ, không sửa** |
| E5 | **không** winsorize/trim outlier CPA |
| D2, D3 | **không** impute `TTTN` và `CPA` |

### 4.4 S3 — Scope & derive

Rule B1: `ma_lop` khớp `^(D22CNPM|D22HTTT|E22)` → **905 dòng**, assert cứng.

Derived fields (C1–C7), khớp schema Phase 1 §10: `class_code`, `class_group`/`track_label`, `class_prefix`, `admission_major_code`, `intake_year`, `program`, `eligible_for_thesis`, `birth_year`, `birthplace`, `birthplace_is_domestic`, `is_off_cohort`, `id_format_anomaly`, `tttn_grade`, `tttn_missing`, `cpa_missing`, `dob_implausible`.

`program`: `class_prefix == 'E'` → `CNTT CLC`, ngược lại `CNTT` (theo quy ước nhà trường, xác nhận Phase 2 §0).

Ghi `data/interim/students_clean.parquet`. **File này vẫn chứa quasi-identifier (`birth_year`, `birthplace`, `student_key`) nên nằm trong `.gitignore`.**

### 4.5 S4 — Metrics

Tính toàn bộ con số xuất hiện trong `insight-discovery.md`. Nhóm theo section của website spec:

| Nhóm | Nội dung |
|---|---|
| `overall` | n, mean+CI, median+CI, sd, var, IQR, quartiles, 15 percentile, skew, kurtosis, Gini, Sarle BC |
| `bands` | 5 band xếp loại + CI binomial exact; 6 ngưỡng cumulative |
| `by_program` | descriptives × 2; Mann-Whitney, Welch, Cohen's d, Cliff's δ, Levene, KS, bootstrap CI hiệu; decile diff |
| `by_track` | descriptives × 5 + CI; Kruskal-Wallis |
| `by_class` | descriptives × 18 + CI (**chỉ aggregate**); KW trong từng track |
| `paired` | so sánh ghép cặp CNPM↔CNPM, HTTT↔HTTT; standardisation |
| `variance` | η² cho 9 biến |
| `eligibility` | tỷ lệ + CI theo track/program; χ², Fisher, Cramér's V; CPA theo eligibility; dải chồng lấn tín chỉ |
| `composition` | thành phần mã ngành × program; CPA theo mã ngành trong CLC (chỉ n ≥ 20) |
| `histograms` | bin 0.1 toàn nhóm; bin 0.2 theo program; bin 0.1 theo track |

Bootstrap: 10.000 lần, `numpy.random.default_rng(42)` — **seed cố định để build có tính tái lập bit-for-bit**.

> **Ràng buộc quan trọng:** frontend **không được tính lại** bất kỳ thống kê nào. Client chỉ được phép: lọc mảng, đếm, và bin lại histogram cho Explore. Mean/CI/p-value hiển thị ở Explore lấy từ công thức đơn giản (mean, sd, CI normal-approx) và **phải ghi rõ** là ước lượng nhanh, khác với con số bootstrap ở phần tĩnh.

### 4.6 S5 — Privacy gate

Xem §9.3. Bước này **có quyền làm fail build**.

### 4.7 S6 — Emit

Ghi 4 file vào `site/src/data/`, mỗi file validate bằng JSON Schema tương ứng trước khi ghi đĩa. Sinh `data.d.ts` từ schema để TypeScript và pipeline không bao giờ lệch nhau.

### 4.8 Chạy pipeline

```
uv run python pipeline/run.py --input data/raw/DS-SV-DK-DATN-D22-KY-THUAT.xlsx
```

In ra báo cáo: số dòng từng bước, kết quả validation, báo cáo privacy, diff so với JSON hiện có. Chỉ chạy khi dữ liệu nguồn thay đổi — **không** nằm trong CI.

---

## 5. Data schema

### 5.1 `meta.json`

```jsonc
{
  "generated_at": "2026-09-11T00:00:00Z",
  "pipeline_version": "1.0.0",
  "source_file_sha256": "…",           // truy vết, không lộ nội dung
  "source_rows_total": 2023,
  "scope_regex": "^(D22CNPM|D22HTTT|E22)",
  "n_in_scope": 905,
  "n_with_cpa": 903,
  "n_classes": 18, "n_tracks": 5, "n_programs": 2,
  "cohort": { "2022": 899, "2021": 6 },
  "min_group_size": 10,
  "bootstrap": { "iterations": 10000, "seed": 42 },
  "dictionaries": {
    "track":   ["D22CNPM","D22HTTT","E22CNPM","E22HTTT","E22TTNT"],
    "program": ["CNTT","CNTT CLC"],
    "major":   ["DCAT","DCCI","DCCN","DCDK","DCDT","DCKH","DCVT"]
  }
}
```

### 5.2 `rows.json` — row-level, columnar, integer-coded

**Chỉ 5 trường.** `class_code` và `tttn_grade` **đã bị loại** (§9.2).

```jsonc
{
  "n": 905,
  "encoding": "columnar-int",
  "fields": {
    "track":  { "type": "uint8",  "ref": "meta.dictionaries.track" },
    "major":  { "type": "uint8",  "ref": "meta.dictionaries.major" },
    "cpa":    { "type": "uint16", "scale": 100, "null": -1, "desc": "CPA × 100; 279 = 2.79" },
    "cr":     { "type": "uint8",  "null": -1,   "desc": "tín chỉ tích lũy, 0–146" },
    "el":     { "type": "uint8",  "desc": "1 = đủ điều kiện làm ĐATN" }
  },
  "track":  [0,0,0, …],   // 905 phần tử
  "major":  [2,2,2, …],
  "cpa":    [271,276,331, …],
  "cr":     [146,146,146, …],
  "el":     [1,1,1, …]
}
```

`program` **không lưu** — suy ra từ `track` (index 0–1 → CNTT, 2–4 → CNTT CLC), tránh trường dư thừa.

**Kích thước đo được: 12.3 KB raw · 2.2 KB gzip · ~1.8 KB brotli.**

### 5.3 `aggregates.json`

Mọi con số hiển thị ở section 02–07. Cấu trúc phẳng theo section để component tra cứu trực tiếp.

```jsonc
{
  "overall": {
    "n": 903, "mean": 2.7915, "mean_ci": [2.7631, 2.8201],
    "median": 2.79, "median_ci": [2.76, 2.82],
    "sd": 0.4322, "variance": 0.1868, "iqr": 0.59,
    "q1": 2.52, "q3": 3.11, "min": 1.40, "max": 3.72,
    "skew": -0.2391, "kurtosis": -0.2606, "gini": 0.0877, "sarle_bc": 0.3859,
    "percentiles": { "p1":1.73,"p5":2.01,"p10":2.23,"p25":2.52,"p50":2.79,
                     "p75":3.11,"p90":3.34,"p95":3.49,"p99":3.64 }
  },
  "bands": [
    { "label":"Xuất sắc","min":3.60,"max":4.00,"n":20,"pct":2.21,"ci":[1.36,3.40] }
    // … 4 band còn lại
  ],
  "by_track": [
    { "track":"D22CNPM","n_rows":362,"n_cpa":362,"mean":3.0199,"ci":[2.990,3.049],
      "median":3.030,"sd":0.2881,"q1":2.790,"q3":3.230,"min":2.43,"max":3.72,
      "eligible_n":360,"eligible_pct":99.45,"eligible_ci":[98.02,99.93],
      "credit_ceiling_pct":93.09 }
    // … 4 track còn lại
  ],
  "by_class": [
    { "class":"D22CNPM01","track":"D22CNPM","n":59,"mean":3.0081,"sd":0.2653,
      "se":0.0345,"ci":[2.940,3.076] }
    // … 17 lớp còn lại — KHÔNG có min/max (Phase 1 rule F4)
  ],
  "program_comparison": {
    "aggregate": { "cntt":{"n":688,"mean":2.7663}, "clc":{"n":215,"mean":2.8720},
                   "diff":0.1057,"ci":[0.0436,0.1688],"p_mw":0.0067,"cohens_d":0.246,
                   "survives_bonferroni":false },
    "paired": [
      { "pair":"CNPM","cntt":{"track":"D22CNPM","n":362,"mean":3.0199},
        "clc":{"track":"E22CNPM","n":137,"mean":2.7560},
        "diff":-0.2639,"ci":[-0.3282,-0.1982],"cohens_d":-0.861,"p_mw":6.5e-14,
        "survives_bonferroni":true },
      { "pair":"HTTT","cntt":{"track":"D22HTTT","n":326,"mean":2.4847},
        "clc":{"track":"E22HTTT","n":40,"mean":2.9173},
        "diff":0.4325,"ci":[0.2998,0.5666],"cohens_d":1.066,"p_mw":1.2e-8,
        "survives_bonferroni":true }
    ],
    "unpaired_note": { "track":"E22TTNT","n":38,"pct_of_clc":17.7 },
    "quantile_diff": [ {"q":10,"cntt":2.18,"clc":2.414,"diff":0.234}, … ],
    "band_share": { "cntt":{"<2.0":5.52,…}, "clc":{"<2.0":1.40,…} }
  },
  "variance_explained": [
    { "var":"class_code","k":18,"eta2":0.3522 },
    { "var":"track_label","k":5,"eta2":0.3448 },
    { "var":"program","k":2,"eta2":0.0109 }
    // … 6 biến còn lại
  ],
  "track_contrast": {
    "cnpm_vs_httt": { "diff":0.5352,"cohens_d":1.538,"cliffs_delta":0.721,
                      "p_superiority":0.860,"p_mw":5.1e-60,
                      "truncation":{"cnpm_min":2.43,"cnpm_below_min":0,
                                    "cnpm_below_httt_median":1,
                                    "httt_above_cnpm_min_pct":52.5},
                      "eta2_within_cntt":0.3717 },
    "class_homogeneity": [ {"track":"D22CNPM","k":6,"H":7.454,"p":0.1890,"mean_spread":0.118}, … ]
  },
  "eligibility": {
    "overall": {"n":905,"eligible":836,"pct":92.4},
    "by_program": {"cntt":{"n":690,"pct":91.88},"clc":{"n":215,"pct":93.95},
                   "chi2_p":0.3946,"significant":false},
    "by_track_chi2": {"chi2":69.205,"p":3.3e-14,"cramers_v":0.2765},
    "cpa_contrast": {"ineligible":{"n":67,"mean":2.1381},"eligible":{"n":836,"mean":2.8439},
                     "cohens_d":1.806},
    "cpa_not_determinant": {"ineligible_ge_2_5":9,"ineligible_ge_3_0":3,
                            "ineligible_max_cpa":3.37,"ineligible_max_pctile":91.8},
    "credit_overlap": {"lo":69,"hi":140,"n_in_band":154,"eligible":125,"ineligible":29}
  },
  "composition": {
    "by_program": [
      {"program":"CNTT","total":690,"majors":[{"major":"DCCN","n":690,"pct":100.0}]},
      {"program":"CNTT CLC","total":215,"non_cntt_n":186,"non_cntt_pct":86.5,
       "majors":[{"major":"DCVT","n":96,"pct":44.7,"mean_cpa":2.776},
                 {"major":"DCDT","n":50,"pct":23.3,"mean_cpa":2.800},
                 {"major":"DCAT","n":34,"pct":15.8,"mean_cpa":3.062},
                 {"major":"DCCN","n":29,"pct":13.5,"mean_cpa":3.114},
                 {"major":"DCKH","n":4,"pct":1.9,"mean_cpa":null},   // n<20 → null
                 {"major":"DCCI","n":1,"pct":0.5,"mean_cpa":null},
                 {"major":"DCDK","n":1,"pct":0.5,"mean_cpa":null}]}
    ],
    "it_vs_telecom": {"it":{"n":63,"mean":3.086},"telecom":{"n":146,"mean":2.784},
                      "diff":0.302,"cohens_d":0.824,"p":2e-5}
  }
}
```

**Quy ước:** bất kỳ nhóm nào `n < 20` thì `mean_cpa = null` (vẫn giữ `n` để tổng khớp 215) — thực thi ở S5, không phải ở frontend.

### 5.4 `histograms.json`

```jsonc
{
  "bin_width": 0.1, "domain": [1.3, 3.8],
  "edges": [1.3, 1.4, …, 3.8],
  "overall": [1,1,0,4,11,8,19,13,25,32,40,62,79,89,85,73,57,74,56,65,44,26,22,15,2],
  "by_program": { "CNTT": [...], "CNTT CLC": [...] },
  "by_track":   { "D22CNPM": [...], "D22HTTT": [...], "E22CNPM": [...],
                  "E22HTTT": [...], "E22TTNT": [...] },
  "kde": { "x": [...], "overall": [...], "by_track": {...} }   // đã tính sẵn, bandwidth Silverman
}
```

Bin đã chốt ở `insight-discovery.md` §O — frontend **dùng nguyên**, không tự bin lại (trừ Explore).

### 5.5 `copy.json`

Toàn bộ headline, deck, supporting copy, caveat, alt text, nhãn trục — tách khỏi code để reviewer nội dung duyệt qua PR mà không cần đọc TSX.

```jsonc
{
  "sections": {
    "04": {
      "headline": "Hệ chất lượng cao có CPA trung bình cao hơn 0.106 điểm — cho đến khi so cùng chuyên ngành",
      "deck": "…",
      "steps": [ {"body":"…"}, {"body":"…"}, {"body":"…"} ],
      "caveat": "…",
      "footnote": "…",
      "charts": { "V-04b": { "alt": "…", "axis_x":"…", "axis_y":"…" } }
    }
  }
}
```

---

## 6. Insight schema

Mỗi insight của Phase 2 được biểu diễn thành một object có cấu trúc, để component render **và** để test đối chiếu ngược lên `insight-discovery.md`.

```jsonc
{
  "id": "CORE-2",
  "rank": "core",                      // "core" | "supporting"
  "section": "04",
  "headline_key": "sections.04.headline",
  "claim": "Chênh lệch CPA giữa hai chương trình đảo dấu khi so sánh cùng chuyên ngành",
  "evidence": [
    { "metric":"mean_diff_aggregate","value":0.1057,"ci":[0.0436,0.1688],"n":903 },
    { "metric":"mean_diff_cnpm","value":-0.2639,"ci":[-0.3282,-0.1982],"n":499 },
    { "metric":"mean_diff_httt","value":0.4325,"ci":[0.2998,0.5666],"n":366 }
  ],
  "tests": [
    { "name":"mann_whitney","scope":"aggregate","p":0.0067,"survives_bonferroni":false },
    { "name":"mann_whitney","scope":"cnpm_pair","p":6.5e-14,"survives_bonferroni":true },
    { "name":"mann_whitney","scope":"httt_pair","p":1.2e-8,"survives_bonferroni":true }
  ],
  "effect_size": { "measure":"cohens_d","aggregate":0.246,"cnpm":-0.861,"httt":1.066 },
  "sample": { "cntt":688, "clc":215, "unpaired":{"track":"E22TTNT","n":38} },
  "caveat_key": "sections.04.caveat",
  "visualization": ["V-04a","V-04b","V-04c"],
  "causal_claim_allowed": false,
  "source_doc": "docs/insight-discovery.md#core-2"
}
```

**Trường `causal_claim_allowed`** áp dụng cho **mọi** insight và luôn là `false` trong dự án này. Nó tồn tại để một lint rule có thể quét `copy.json`: nếu copy của một section có insight `causal_claim_allowed: false` mà chứa từ trong danh sách cấm (`gây ra`, `dẫn tới`, `tốt hơn`, `dạy tốt hơn`, `chất lượng cao hơn`, `ảnh hưởng tới`, `chứng minh` — spec Phase 3 §4), **CI fail**. Đây là cách biến quy tắc ngôn ngữ thành ràng buộc thực thi được, thay vì một dòng ghi chú mà người ta sẽ quên.

---

## 7. Frontend architecture

### 7.1 Nguyên tắc render

Một trang duy nhất, pre-render toàn bộ. Mặc định **0 JavaScript**. Chart tĩnh render thành SVG ngay tại build time bằng d3-scale/d3-shape chạy trong Node — client nhận SVG đã hoàn chỉnh, không cần JS để thấy hình.

### 7.2 Islands (chỉ 5)

| Island | Section | Directive | Vì sao cần JS |
|---|---|---|---|
| `ProgramReveal` | 04 | `client:visible` | Scroll-triggered 3 bước |
| `ColorByToggle` | 05 | `client:visible` | Chuyển cách tô màu histogram |
| `EligibilityBars` | 07 | `client:visible` | Toggle track/program |
| `CpaCreditScatter` | 07 | `client:visible` | Hover tooltip trên 905 điểm |
| `ExplorePanel` | 08 | `client:idle` | Lọc tương tác |

`rows.json` **chỉ** được import bởi `CpaCreditScatter` và `ExplorePanel`. Astro tự code-split nên 2.2 KB đó không nằm trong bundle chính.

Section 01, 02, 03, 05b, 05c, 06, 09, 10 → **hoàn toàn không có JS**. Toggle ở section 03 ("hiện dải xếp loại") làm bằng CSS `:has()` + checkbox ẩn, không cần island.

### 7.3 Ranh giới tính toán

| Được phép ở client | Không được phép ở client |
|---|---|
| Lọc mảng theo predicate | Bootstrap, hypothesis test, tính p-value |
| Đếm, mean, sd, CI normal-approx cho nhóm đã lọc | Tính η², Cohen's d, Cliff's δ |
| Bin lại histogram cho Explore | Tính lại bất kỳ con số nào ở section 02–07 |
| Format số | Suy diễn nhãn xếp loại từ CPA (đã có trong aggregates) |

Explore hiển thị nhãn *"ước lượng nhanh"* cạnh mean/CI để phân biệt với con số bootstrap ở phần tĩnh.

### 7.4 State

Chỉ Explore có state, giữ trong URL query params (`?program=clc&track=E22TTNT&elig=1`) → chia sẻ được, back/forward hoạt động, không cần state library. Các island khác chỉ có local state tầm thường.

### 7.5 Accessibility

- Mọi chart là `<figure>` + `<figcaption>`; `role="img"` + `aria-label` mô tả **phát hiện**, không mô tả hình dạng.
- Mỗi chart kèm một `<table>` dữ liệu trong `<details>` đóng sẵn — screen reader và người muốn số thô đều dùng được.
- Màu không bao giờ là kênh thông tin duy nhất: kèm nhãn trực tiếp hoặc kiểu nét.
- Tương phản ≥ 4.5:1; kiểm bằng axe-core trong CI.
- Scroll reveal ở section 04: tôn trọng `prefers-reduced-motion` → hiện thẳng cả 3 bước.
- Toàn bộ Explore điều khiển được bằng bàn phím.

### 7.6 Responsive

Breakpoint 640px. Dưới ngưỡng: slope chart và caterpillar chuyển sang danh sách thanh ngang; section 04 từ scroll-reveal thành 3 card xếp dọc; SectionNav ẩn thành nút "Mục lục" nổi.

---

## 8. Deployment architecture

### 8.1 Môi trường

| Môi trường | Trigger | URL |
|---|---|---|
| Local | `npm run dev` | `localhost:4321` |
| Preview | mỗi PR | `<hash>.ptit-insights.pages.dev` |
| Production | merge vào `main` | domain chính thức |

### 8.2 CI (`ci.yml`) — chạy mọi PR

| Job | Nội dung | Fail = chặn merge |
|---|---|---|
| `forbidden-files` | Không có `.xlsx`, `.parquet`, `.csv` ngoài `data/reference/` trong diff | ✅ |
| `forbidden-fields` | `rows.json` không chứa `class`, `tttn`, `birth`, `name`, `id`, `ma_sv` | ✅ |
| `schema` | 4 file JSON hợp lệ theo JSON Schema | ✅ |
| `pipeline-tests` | pytest — gồm `test_metrics.py` đối chiếu Phase 2 | ✅ |
| `language-lint` | Quét `copy.json` bằng danh sách từ cấm (§6) | ✅ |
| `numbers-match` | Mọi số trong `copy.json` phải tồn tại trong `aggregates.json` | ✅ |
| `typecheck` + `lint` | tsc strict, ruff, eslint | ✅ |
| `build` | Astro build thành công | ✅ |
| `a11y` | axe-core trên trang đã build | ✅ |
| `e2e` | Playwright: ngưỡng n<10, reveal, responsive | ✅ |
| `budget` | Kiểm ngân sách hiệu năng (§10.1) | ✅ |

### 8.3 Deploy (`deploy.yml`)

Merge vào `main` → build → publish lên Cloudflare Pages. Không secret nào ngoài API token của Cloudflare. **Pipeline Python không chạy trong CI** — CI chỉ dùng JSON đã commit.

### 8.4 Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self';
                         img-src 'self' data:; font-src 'self'; connect-src 'none';
                         frame-ancestors 'none'; base-uri 'none'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: geolocation=(), camera=(), microphone=(), interest-cohort=()
Cache-Control: public, max-age=31536000, immutable      # asset có hash
Cache-Control: public, max-age=0, must-revalidate       # index.html
```

`connect-src 'none'` là một khẳng định có thể kiểm chứng: trang không gọi mạng sau khi tải xong.

### 8.5 Cập nhật khi dữ liệu đổi

```
1. Người có quyền chạy pipeline trên máy local, file .xlsx mới
2. Đọc báo cáo diff của pipeline
3. Nếu con số đổi → CẬP NHẬT docs/insight-discovery.md TRƯỚC
4. Commit JSON mới + tài liệu đã cập nhật trong CÙNG một PR
5. CI kiểm tra tính nhất quán; merge → deploy tự động
```

Bước 3 không thể bỏ qua: `test_metrics.py` đối chiếu JSON với tài liệu, nên tài liệu lệch sẽ làm fail build.

---

## 9. Privacy strategy

### 9.1 Bốn tầng phòng thủ

| Tầng | Cơ chế |
|---|---|
| 1. Nguồn | `.xlsx` và `.parquet` trong `.gitignore`; CI chặn nếu lọt vào diff |
| 2. Pipeline | Trường định danh bị drop ở S5; không có đường nào để chúng đến `site/` |
| 3. Artifact | `rows.json` chỉ 5 trường, đã kiểm k-anonymity |
| 4. Trình bày | Ngưỡng n<10, không ranking, tooltip hạn chế, `connect-src 'none'` |

### 9.2 ⚠️ Kết quả đo — vì sao phải thu hẹp payload

Đo trực tiếp trên 905 dòng, đếm tỷ lệ **dòng duy nhất** theo từng bộ trường:

| Bộ trường gửi xuống client | % dòng duy nhất | k nhỏ nhất |
|---|---:|---:|
| **Như `website-spec.md` viết** (`class_code` + `cpa` + `credits` + `elig` + `tttn` + `major`) | **85.1%** | 1 |
| Chỉ `class_code` + `cpa` | 63.3% | 1 |
| **Đề xuất** (`track` + `cpa` + `credits` + `elig` + `major`) | **49.5%** | 1 |
| `track` + `cpa` + `credits` + `elig` | 45.5% | 1 |
| `program` + `cpa` + `credits` + `elig` | 35.2% | 1 |

Mức tăng tính duy nhất khi thêm từng trường vào nền `track + cpa`:

| Thêm trường | % dòng duy nhất |
|---|---:|
| `+ class_code` | **63.3%** ⛔ |
| `+ tttn` | **46.3%** ⛔ |
| `+ credits` | 45.3% |
| `+ credit_bucket` | 39.8% |
| `+ admission_major` | 28.7% |
| `+ eligible` | 26.3% |

**Vì sao đây là vấn đề thật, không phải lo xa:** Phase 1 §7 đã xác định nhóm `Không đủ điều kiện` là dữ liệu nhạy cảm nhất trong dataset. Nếu gửi `class_code`, một người biết bạn học lớp nào và CPA khoảng bao nhiêu có thể khoanh vùng đúng dòng của bạn và đọc ra **trạng thái không đủ điều kiện tốt nghiệp**. Thêm nữa, **9 trên 11 lớp có dưới 10 sinh viên không đủ điều kiện** — đúng ngưỡng suppression mà Phase 1 rule F4 đặt ra. Gửi `class_code` xuống client là vô hiệu hóa chính quy tắc đó.

**Quyết định:**
- ⛔ **Bỏ `class_code`** khỏi `rows.json`. Dữ liệu cấp lớp chỉ tồn tại dưới dạng **aggregate 18 dòng** trong `aggregates.json`, mỗi dòng n ≥ 32 — an toàn.
- ⛔ **Bỏ `tttn_grade`** khỏi `rows.json`. Không filter nào ở Explore dùng nó, và Phase 2 đã cố ý không nâng SUP-8 thành chart.
- ✅ Explore vẫn cho chọn một lớp, nhưng overlay là **marker mean ± CI lấy từ `aggregates.json`**, không phải điểm cá nhân.

**Rủi ro tồn dư — ghi nhận tường minh:** bộ trường đề xuất vẫn có 49.5% dòng duy nhất. Người đã biết chính xác CPA (2 chữ số) và chuyên ngành của một sinh viên có thể suy ra số tín chỉ và trạng thái đủ điều kiện của người đó. Đánh giá: người đó **đã biết trường nhạy cảm nhất** (CPA) từ trước, nên mức lộ thêm là giới hạn. Nếu reviewer muốn siết thêm, đòn bẩy rẻ nhất là **bỏ `admission_major` khỏi Explore** → xuống 45.5%, đổi lại mất một bộ lọc. Đây là quyết định của người phụ trách dữ liệu, không phải của developer.

### 9.3 S5 privacy gate — kiểm tra tự động, fail build

| # | Kiểm tra | Ngưỡng |
|---|---|---|
| P1 | Danh sách trường được phép trong `rows.json` khớp chính xác `{track, major, cpa, cr, el}` | Bất kỳ trường lạ → fail |
| P2 | Không trường nào khớp regex `(?i)(name|ho_?ten|ma_?sv|student|birth|ngay_?sinh|noi_?sinh|email|id)` | fail |
| P3 | Mọi nhóm trong mọi aggregate có `n ≥ 10` | fail |
| P4 | Mọi nhóm có `n < 20` phải có `mean_cpa = null` | fail |
| P5 | Không aggregate nào chứa `min`/`max` ở cấp lớp | fail |
| P6 | k-anonymity của `rows.json` ≤ ngưỡng đã duyệt (50% dòng duy nhất) | vượt → fail |
| P7 | Không có breakdown nhóm ineligible theo lớp trong bất kỳ output nào | fail |
| P8 | `meta.json` không chứa đường dẫn tuyệt đối hay tên người | fail |

Báo cáo privacy in ra mỗi lần chạy pipeline và **được commit** thành `pipeline/privacy-report.md` để có audit trail.

### 9.4 Xử lý file gốc

| Việc | Quy định |
|---|---|
| Lưu trữ | Chỉ trên máy local của người được ủy quyền |
| Git | `.gitignore` + CI check chặn |
| Metadata | Strip `docProps` (chứa `HangDT-GV`, `Tran Thanh Thuy D22CN05`) khỏi mọi file phái sinh |
| Hash | `meta.json` chỉ lưu SHA-256 để truy vết phiên bản |
| Backup | Không sao chép lên cloud storage cá nhân |

---

## 10. Performance strategy

### 10.1 Ngân sách (CI thực thi, vượt = fail)

| Chỉ số | Ngân sách | Cơ sở |
|---|---|---|
| HTML (gzip) | ≤ 60 KB | Trang chủ yếu là văn bản + SVG inline |
| CSS (gzip) | ≤ 12 KB | CSS thuần, không framework |
| JS bundle chính (gzip) | ≤ 15 KB | Preact runtime + hydration |
| JS island tổng (gzip, lazy) | ≤ 35 KB | d3 modules + logic 5 island |
| `rows.json` (gzip) | ≤ 5 KB | **Đo được: 2.2 KB** |
| `aggregates.json` (gzip) | ≤ 15 KB | |
| Font | ≤ 40 KB | 1 family, 2 weight, subset Latin+Vietnamese |
| **Tổng first load (gzip)** | **≤ 130 KB** | |
| LCP (Slow 4G) | < 1.5 s | |
| CLS | < 0.05 | |
| TBT | < 100 ms | |
| Lighthouse Performance | ≥ 95 | |

### 10.2 Kỹ thuật

| Kỹ thuật | Chi tiết |
|---|---|
| Pre-render toàn bộ | Không có runtime data fetching; SVG tĩnh render sẵn tại build |
| Islands lazy | 4 island `client:visible`, Explore `client:idle` |
| Code splitting | `rows.json` chỉ nằm trong chunk của 2 island dùng nó |
| Integer coding | `rows.json` 12.3 KB thay vì 131 KB dạng object verbose (**giảm 91%**) |
| Brotli | Cloudflare tự động |
| Font | Self-host, `font-display: swap`, subset Vietnamese, preload 1 weight |
| Ảnh | Chỉ 1 ảnh OG; mọi biểu đồ là SVG |
| CLS | Mọi container chart có `aspect-ratio` cố định |
| Cache | Asset có hash → immutable 1 năm; `index.html` → revalidate |
| Không có | web font từ CDN, icon font, polyfill, analytics, cookie banner |

### 10.3 Vì sao SVG chứ không Canvas

Chart lớn nhất là scatter 905 điểm (V-07b). SVG xử lý 905 node thoải mái, đổi lại được: chọn text, hoạt động với screen reader, in ấn sắc nét, và không cần JS để hiển thị. Canvas chỉ đáng cân nhắc từ ~10.000 điểm trở lên.

---

## 11. Implementation checklist

Task theo thứ tự thực thi. `[P]` = có thể làm song song với task liền trước.

### Đợt 0 — Nền móng

| # | Task | Xong khi |
|---|---|---|
| 0.1 | Tạo cấu trúc thư mục `pipeline/` và `site/` | Khớp §3 |
| 0.2 | `.gitignore`: `data/raw/`, `data/interim/`, `*.xlsx`, `*.parquet` | `git status` sạch khi có file gốc |
| 0.3 | `uv init` trong `pipeline/`, pin pandas 3.0.1 / scipy 1.17.1 / numpy 2.4.2 / openpyxl 3.1.5 | `uv sync` tái lập được |
| 0.4 | `npm create astro`, bật TypeScript strict + Preact | `npm run build` chạy được |
| 0.5 | CI skeleton: lint, typecheck, build | PR đầu tiên xanh |
| 0.6 | CI job `forbidden-files` | Cố tình commit 1 `.xlsx` → CI đỏ |

### Đợt 1 — Pipeline (không có UI)

| # | Task | Xong khi |
|---|---|---|
| 1.1 | `config.py` — scope regex, ngưỡng, seed 42, đường dẫn | |
| 1.2 | `schemas.py` — pandera schema cho raw (§4.2) | |
| 1.3 | `s1_ingest.py` | Đọc ra đúng 2.023 dòng; sửa 1 ô sai kiểu → fail |
| 1.4 | `s2_clean.py` — rules A3, A4, D1, E1, E2, E4 | Assert `0≤CPA≤4` pass |
| 1.5 | `s3_scope.py` — rule B1 + 16 derived field | Đúng **905** dòng, 18 lớp, 5 track |
| 1.6 | `tests/test_cleaning.py` | 3 ô CPA rỗng → NA; 0 outlier bị xóa |
| 1.7 | `s4_metrics.py` nhóm `overall` + `bands` | mean = 2.7915, IQR = 0.59 |
| 1.8 | `s4_metrics.py` nhóm `by_track`, `by_class`, `variance` | η²(program) = 0.0109, η²(track) = 0.3448 |
| 1.9 | `s4_metrics.py` nhóm `program_comparison` + `paired` | diff = +0.1057 / −0.2639 / +0.4325 |
| 1.10 | `s4_metrics.py` nhóm `eligibility` + `composition` | 99.45% / 83.54%; 186/215 |
| 1.11 | `s4_metrics.py` histograms | Bin khớp `insight-discovery.md` §O |
| 1.12 | ⭐ `tests/test_metrics.py` — đối chiếu **từng** con số với Phase 2 | Mọi giá trị khớp đến chữ số cuối |
| 1.13 | `s5_privacy.py` — 8 kiểm tra P1–P8 | Cố tình thêm `class_code` → fail |
| 1.14 | ⭐ `tests/test_privacy.py` | k-anon ≤ 50%; trường cấm bị chặn |
| 1.15 | JSON Schema cho 4 file output | |
| 1.16 | `s6_emit.py` + sinh `data.d.ts` | 4 file JSON hợp lệ trong `site/src/data/` |
| 1.17 | `run.py` orchestrator + báo cáo diff | Một lệnh chạy hết S1→S6 |
| 1.18 | Chạy pipeline, commit JSON + `privacy-report.md` | `rows.json` gzip ≤ 5 KB |

### Đợt 2 — Khung site và các section không-JS

Theo build order của `website-spec.md` §6: **khung trung thực trước, so sánh sau.**

| # | Task | Xong khi |
|---|---|---|
| 2.1 | `tokens.css`, `global.css`, typography scale | |
| 2.2 | `Section.astro`, `Headline.astro`, `Caveat.astro` | |
| 2.3 | `format.ts` theo quy tắc số của spec §4 | Test: `2.79`, `+0.106`, `86.5% (186/215)` |
| 2.4 | `copy.json` — toàn bộ text của 11 section | |
| 2.5 | CI `language-lint` + `numbers-match` | Thêm "tốt hơn" vào copy → CI đỏ |
| 2.6 | **Section 01 Scope** + V-01 funnel | |
| 2.7 | **Section 02 Overview** + V-02 band bar | |
| 2.8 | **Section 03 Distribution** + V-03 histogram (toggle bằng CSS) | 0 JS |
| 2.9 | **Section 09 Methodology** — accordion 5 nhóm, `<details>` | 0 JS |
| 2.10 | **Section 10 Limits** | 0 JS |
| 2.11 | Milestone: deploy preview 5 section này | ✅ Điều kiện chặn của spec §6 được thỏa mãn |

### Đợt 3 — Lõi lập luận

| # | Task | Xong khi |
|---|---|---|
| 3.1 | Helper d3 render SVG tại build time | |
| 3.2 | V-04a bar 2 nhóm (tĩnh) | |
| 3.3 | `ProgramReveal.tsx` — V-04b slope chart + CI | Đúng 2 dòng, dốc ngược chiều |
| 3.4 | V-04c quantile-difference plot | Đường zero rõ |
| 3.5 | **Section 04** ghép 3 bước + `prefers-reduced-motion` | |
| 3.6 | V-05a η² bar chart | Highlight `track` và `program` |
| 3.7 | `ColorByToggle.tsx` — V-05b small-multiple | Toggle đổi cách tô màu |
| 3.8 | V-05c ridgeline + annotation tại 2.43 | Đường dọc có nhãn |
| 3.9 | V-05d caterpillar 18 lớp | **Không** sort theo mean; không min/max |
| 3.10 | **Section 05 + 05b + 05c** | |
| 3.11 | e2e: reveal, reduced-motion, không có sort control | |

### Đợt 4 — Chiều sâu

| # | Task | Xong khi |
|---|---|---|
| 4.1 | V-06a composition stacked bars | |
| 4.2 | V-06b dot plot, chỉ n ≥ 20 | DCKH/DCCI/DCDK không có chấm |
| 4.3 | **Section 06** | |
| 4.4 | `EligibilityBars.tsx` V-07a + nhãn trục cắt | |
| 4.5 | `CpaCreditScatter.tsx` V-07b | Tooltip **chỉ** cpa/credits/elig |
| 4.6 | Panel "vì sao không có xu hướng thời gian" | |
| 4.7 | **Section 07** | |
| 4.8 | e2e: tooltip không lộ trường nào khác | |

### Đợt 5 — Hero và Explore

| # | Task | Xong khi |
|---|---|---|
| 5.1 | **Section 00 Hero** + V-00 density ridge | 0 JS |
| 5.2 | `SmallSampleGuard.tsx` — ngưỡng n<10 | |
| 5.3 | `FilterControls.tsx` — 6 bộ lọc của spec §2/08 | Không có filter nơi sinh/năm sinh |
| 5.4 | Class overlay bằng marker aggregate | Không dùng row-level |
| 5.5 | `ExplorePanel.tsx` V-08 + nhãn "ước lượng nhanh" | |
| 5.6 | Đồng bộ state ↔ URL | Back/forward hoạt động |
| 5.7 | ⭐ e2e: lọc ra nhóm n<10 → chart bị ẩn | Bắt buộc pass |
| 5.8 | **Section 08** | |

### Đợt 6 — Hoàn thiện & phát hành

| # | Task | Xong khi |
|---|---|---|
| 6.1 | `SectionNav.astro` | |
| 6.2 | Responsive < 640px cho slope + caterpillar + section 04 | |
| 6.3 | Bảng dữ liệu trong `<details>` cho mọi chart | |
| 6.4 | Alt text mô tả **phát hiện** cho 16 chart | |
| 6.5 | axe-core trong CI, 0 violation | |
| 6.6 | CI performance budget (§10.1) | |
| 6.7 | Security headers (§8.4) | `connect-src 'none'` xác minh được |
| 6.8 | Lighthouse ≥ 95 cả 4 hạng mục | |
| 6.9 | `deploy.yml` → Cloudflare Pages | |
| 6.10 | README: cách chạy pipeline, cách cập nhật dữ liệu (§8.5) | |
| 6.11 | ⭐ Rà soát cuối: đối chiếu mọi con số trên site với `insight-discovery.md` | |
| 6.12 | ⭐ Rà soát privacy: mở DevTools → xác nhận không tải trường nào bị cấm | |

### Cổng chặn (không được bỏ qua)

| Cổng | Điều kiện |
|---|---|
| 🚧 Trước đợt 2 | `test_metrics.py` và `test_privacy.py` đều xanh |
| 🚧 Trước đợt 3 | Section 10 (Limits) đã live trên preview — spec §6 |
| 🚧 Trước đợt 5 | Ngưỡng n<10 có e2e test pass |
| 🚧 Trước production | Task 6.11 và 6.12 hoàn tất và có người thứ hai review |

---

## 12. Rủi ro và giảm thiểu

| Rủi ro | Khả năng | Tác động | Giảm thiểu |
|---|---|---|---|
| Số trên site lệch khỏi tài liệu | Trung bình | Cao — mất tính chính trực | `test_metrics.py` + CI `numbers-match`; tài liệu là chuẩn |
| Ai đó thêm `class_code` vào `rows.json` "cho tiện" | Trung bình | **Nghiêm trọng** — tính duy nhất nhảy lên 85.1% | P1/P2/P6 fail build; ghi rõ lý do ngay tại đây |
| File `.xlsx` bị commit nhầm | Thấp | **Nghiêm trọng** — lộ PII | `.gitignore` + CI `forbidden-files` |
| Copy trôi dần sang ngôn ngữ nhân quả | Cao | Cao | CI `language-lint` với danh sách từ cấm |
| Bundle phình theo thời gian | Trung bình | Trung bình | Performance budget fail build |
| File nguồn cập nhật, con số đổi | Thấp | Trung bình | Quy trình §8.5 buộc cập nhật tài liệu cùng PR |
| Explore bị dùng để đào dữ liệu | Trung bình | Trung bình | Ngưỡng n<10, caveat cố định, không có export |
| d3 tự vẽ tốn công hơn dự kiến | Trung bình | Thấp | 10/16 chart là tĩnh, đơn giản; chỉ 6 chart cần công thật sự |

---

## Phụ lục — Bảng quyết định nhanh

| Câu hỏi | Trả lời |
|---|---|
| Có cần backend không? | Không |
| Có cần database không? | Không |
| Có gửi dữ liệu cấp cá nhân xuống client không? | Có — 905 dòng, **5 trường**, không có `class_code`, không có `tttn` |
| Kích thước file đó? | 12.3 KB raw, **2.2 KB gzip** |
| Frontend có tính lại thống kê không? | Không, trừ mean/CI xấp xỉ trong Explore (có nhãn phân biệt) |
| Pipeline có chạy trong CI không? | Không — chạy thủ công trên máy có quyền truy cập file gốc |
| Site gọi API nào lúc chạy? | Không cái nào. `connect-src 'none'` |
| Cập nhật dữ liệu ra sao? | Chạy pipeline local → cập nhật tài liệu → commit JSON + docs cùng một PR |
```
