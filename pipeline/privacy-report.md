# Privacy gate report

- P1 PASS — fields exactly ['cpa', 'cr', 'el', 'major', 'track']
- P2 PASS — no forbidden field name pattern present
- P3 PASS — every published group has n >= 10
- P4 PASS — every group n < 20 has mean_cpa = null
- P5 PASS — no min/max at class level
- P6 PASS — 49.5% of rows unique on shipped fields (ceiling 55%)
- P7 PASS — no ineligible-by-class breakdown published
- P8 PASS — meta.json contains no paths or personal names
- P9 PASS — every published birthplace-band cell has n >= 10
