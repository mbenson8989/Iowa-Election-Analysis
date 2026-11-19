# Iowa-Election-Analysis
Iowa 22-26, ΔG method from the Cedar County (Nebraska) audit, Residual Math, Locked Iowa Formula

Iowa governor race, 2022 vs 2026, all 99 counties. Same method as Morissa Benson's
[Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki), which began with the
[Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit).
The write-up is on this repo's **Wiki** tab (Home, Reverse-Math, Locked-Iowa-Formula, Floor-and-Ceiling, Graphs).

**2026 figures are unofficial** (Iowa SOS results site, election 127077). The State Canvass has not been completed.
These files measure a pattern; they make no claim about intent, fraud or cause. "Implied extra votes" are what a
hypothesis would have to account for, not votes shown to be improper.

## Formula (ballots denominator)
- S = Democratic governor votes ÷ total ballots cast × 100
- R = Democratic registered ÷ total registered (active + inactive, SOS Nov 1 report) × 100
- G = S − R; ΔG = G 2026 − G 2022
- Residual = ΔG − (R 2022 − R 2026) = S 2026 − S 2022
- Implied extra votes = D 2026 − (S 2022 ÷ 100) × ballots 2026

## Files
- `*.png` (repo root): the charts embedded in the wiki
- `data/iowa_wiki_99_counties_by_population.csv`: every county input and result, largest to smallest population
- `data/summary.json`, `data/wiki_claims.json`: statewide results and every number cited in the wiki
- `scripts/build_data.py` → `scripts/charts.py` → `scripts/build_wiki.py` → `scripts/verify_wiki.py`
- `VERIFY_LOG.txt`: independent re-parse of the source files and a pass/fail check of every number in the wiki
- `sources/`: the source files used (below)

## Sources
| Data | File in `sources/` | Origin | Status |
|---|---|---|---|
| 2022 governor by county | `ia2022_govcanvsummary.pdf`, `gov22.txt` | Iowa SOS 2022 State Canvass Summary, https://sos.iowa.gov/elections/pdf/2022/general/govcanvsummary.pdf (Wayback copy) | Official |
| 2022 ballots cast by county | `ia2022_turnout.pdf`, `.txt` | Iowa SOS 2022 turnout report, https://sos.iowa.gov/elections/pdf/2022/general/turnout.pdf (Wayback copy) | Official |
| 2022 county results (cross-check) | `enr2022_county/*.zip` | Iowa SOS results site, county pages for election 115641 | Official |
| 2026 governor and ballots by county | `enr2026_v387276/` | https://electionresults.iowa.gov/IA/127077/387276/reports/detailtxt.zip and json/status.json, downloaded Nov 19 2026 | **Unofficial**; 98 of 99 counties show certified county results (Van Buren does not) |
| Registration, Nov 1 of 2018, 2022, 2026 | `state_of_iowa_monthly_voter_registration_totals_by_county_1013_rows.csv`, `CoNov22.pdf`, `CoNov18.pdf` | Iowa SOS via the Iowa Data Hub (dataset 1013); SOS VR archive PDFs | Official |
| 2018 control cycle | `ia2018_govcanvsummary.pdf`, `ia2018_turnout.pdf` (+ `.txt`) | Iowa SOS 2018 canvass and turnout report (Wayback copies) | Official |
| Population | `co-est2025-alldata.csv` | U.S. Census Bureau Vintage 2025 county estimates | Official |

## Reproduce
```
pip install pandas numpy scipy matplotlib   # plus poppler-utils for pdftotext
python3 scripts/build_data.py && python3 scripts/charts.py && python3 scripts/build_wiki.py && python3 scripts/verify_wiki.py
```
`build_wiki.py` writes the wiki pages to `../wiki/`.
