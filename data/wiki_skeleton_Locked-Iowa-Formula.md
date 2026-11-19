# Locked Iowa Formula

> **\*2026 figures are unofficial and not certified by the Iowa Secretary of State.** The State Canvass has not been completed. On the SOS results site (election 127077, last updated 11/19/2026 11:01:36 AM CST),  of  counties show certified county results;  does not. Governor race unless a page says otherwise. Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. Registration is the Iowa SOS Nov 1 report for each year (active + inactive). These pages measure a pattern; they make no claim about intent, fraud or cause.

## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ total ballots cast × 100
- **R** (Democratic registration share) = Democratic registered voters ÷ total registered voters (active + inactive, SOS Nov 1 report) × 100
- **G** = S − R
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (R2026 − R2022)
- **Reverse step (registration-loss subtraction):** residual = ΔG − (R2022 − R2026) = S2026 − S2022, the vote-share growth left after subtracting the expected loss from the registration-share decline
- **Solved backward, implied extra votes:** D2026 − (S2022 ÷ 100) × ballots2026
- **Registration-scaled gap** (the Nebraska wiki's "gap in votes" line, for comparison only): D2026 − D2022 × (RegDem2026 ÷ RegDem2022)

**Denominator.** Total ballots cast: the SOS 2022 turnout report and the "Ballots Cast" column on the 2026 SOS results site. In 2022, total ballots equal the governor-race total including undervotes and overvotes in  of  counties. The current Nebraska pages divide by total votes in the governor race instead. On Iowa's numbers that alternative raises county ΔG by  points on average; this wiki uses ballots throughout.

## Blank template

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | ______ | ______ |
| 2 | Total ballots cast | ______ | ______ |
| 3 | S = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters, active + inactive (Nov 1 SOS report) | ______ | ______ |
| 5 | Total registered voters, active + inactive (Nov 1 SOS report) | ______ | ______ |
| 6 | R = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | G = line 3 − line 6 | ______ | ______ |
| 8 | ΔG = G 2026 − G 2022 | | ______ |
| 9 | Registration-share change = R 2026 − R 2022 | | ______ |
| 10 | Did Democratic registration fall? (line 4: 2026 < 2022) | | Yes / No |
| 11 | If yes: residual = line 8 − \|line 9\| | | ______ |
| 12 | Implied extra votes = line 1 (2026) − line 3 (2022) ÷ 100 × line 2 (2026) | | ______ |
| 13 | Registration-scaled gap = line 1 (2026) − line 1 (2022) × (line 4 2026 ÷ line 4 2022) | | ______ |

## Rules for using this formula

1. **If a county lost Democratic registration, run the residual step.** Subtract the registration-share loss from ΔG (line 11) and solve backward for implied extra votes (line 12). In Iowa,  of  counties lost registered Democrats. The exception is  ( → ), a **non-loss county**: report its raw numbers. Its registration *share* still fell ( points), so its line 11 equals its vote-share growth.
2. **The starting point is different in every state. Don't assume Nebraska's numbers carry over.** Iowa's statewide ΔG was \* and its county median \*. Compare Iowa counties with Iowa's own range, not with Nebraska's.
3. **Always pull out the ceiling and floor counties.** In Iowa the ceiling county is  (\*) and the lowest ΔG is  (\*). No Iowa county has a negative ΔG. See [Floor and Ceiling Counties](Floor-and-Ceiling).

**Terms used in this wiki** (full definitions on [Floor and Ceiling Counties](Floor-and-Ceiling#terminology)):
- **Ceiling counties**: the five largest ΔG ().
- **Floor counties**: the most Republican baseline, the four lowest 2022 Democratic registration shares ().
- **Non-loss counties**: no Democratic registration loss (). Raw numbers only.

## Worked example: Dubuque

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes |  | * |
| 2 | Total ballots cast |  | * |
| 3 | S |  | * |
| 4 | Democratic registered |  |  |
| 5 | Total registered |  |  |
| 6 | R |  |  |
| 7 | G |  | * |
| 8 | ΔG | | * |
| 9 | Registration-share change | |  |
| 10 | Registration fell? | | Yes |
| 11 | Residual | | * |
| 12 | Implied extra votes | | * |
| 13 | Registration-scaled gap | | * |

---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) · [Home](Home)
