"""Render the Iowa wiki pages. Every number is a {{key|FMT}} placeholder resolved by resolve.py;
claims (page, key, format, text) and a placeholder-free skeleton are written for verify_wiki.py."""
import os, re, json, datetime, pandas as pd
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmt import FMTS
from resolve import make
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(os.path.dirname(ROOT), 'wiki')
J = json.load(open(os.path.join(ROOT, 'data', 'summary.json')))
base = pd.read_csv(os.path.join(ROOT, 'data', 'iowa_wiki_99_counties_by_population.csv')).rename(columns={'certified_2026': 'cert'})
val, d = make(base)
RAW = 'https://raw.githubusercontent.com/mbenson8989/Iowa-Election-Analysis/main/'
CEDAR = 'https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
NEWIKI = 'https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki'
BUILT = datetime.datetime.now().strftime('%b %d %Y %H:%M')
ENRUPD = J['enr_updated']
TOP5 = d.nlargest(5, 'dG').county.tolist(); FLOOR4 = d.nsmallest(4, 'R22').county.tolist()

DISC = ("> **\\*2026 figures are unofficial and not certified by the Iowa Secretary of State.** The State Canvass has not been completed. "
        "On the SOS results site (election 127077, last updated " + ENRUPD + "), {{n:certified|N}} of {{n:counties|N}} counties show certified county results; "
        "{{L:uncertified|L}} does not. Governor race unless a page says otherwise. Votes are votes for the Democratic candidate, not a count of registered "
        "Democrats who voted. Registration is the Iowa SOS Nov 1 report for each year (active + inactive). These pages measure a pattern; they make no claim about intent, fraud or cause.")

def img(file, alt, cap):
    return f"![{alt}]({RAW}{file})\n\n*{cap}*\n"

def row_six(c):
    k = f"c:{c}:"
    note = '†' if c == 'Dallas' else ''
    return (f"| {c}{note} | {{{{{k}population|I}}}} | {{{{{k}demreg22|I}}}} → {{{{{k}demreg26|I}}}} | {{{{{k}D22|I}}}} → {{{{{k}D26|I}}}} | "
            f"{{{{{k}ballots22|I}}}} → {{{{{k}ballots26|I}}}} | {{{{{k}residual|SF2}}}} | {{{{{k}reg_share_change|SF2}}}} | {{{{{k}dG|SF2}}}} | {{{{{k}residual_votes|SI}}}} |")

def grp_row(label, g):
    k = f"g:{g}:"
    return (f"| {label} | {{{{{k}n|N}}}} | {{{{{k}S22|P2}}}} → {{{{{k}S26|P2}}}}\\* | {{{{{k}R22|P2}}}} → {{{{{k}R26|P2}}}} | {{{{{k}residual|SF2}}}} | "
            f"{{{{{k}reg_share_change|SF2}}}} | {{{{{k}dG|SF2}}}} | {{{{gd:{g}:dG:median|SF2}}}} ({{{{gd:{g}:dG:min|SF2}}}} to {{{{gd:{g}:dG:max|SF2}}}}) | {{{{{k}residual_votes_sum|SI}}}} |")

def row_cf(c):
    k = f"c:{c}:"; grp = 'Ceiling' if c in TOP5 else 'Floor'
    return (f"| {c} | {grp} | {{{{{k}population|I}}}} | {{{{{k}G22|SF2}}}} | {{{{{k}G26|SF2}}}} | {{{{{k}dG|SF2}}}} | {{{{{k}R22|P1}}}} → {{{{{k}R26|P1}}}} | "
            f"{{{{{k}demreg22|I}}}} → {{{{{k}demreg26|I}}}} ({{{{{k}demreg_pct_change|SP1}}}}) | {{{{{k}D22|I}}}} → {{{{{k}D26|I}}}} | {{{{{k}residual_votes|SI}}}} |")

SIX = d.head(6).county.tolist()
CF = [c for c in d.county if c in TOP5 + FLOOR4]   # population order
EX = 'Dubuque'; e = f"c:{EX}:"

PAGES = {}
PAGES['Home'] = f"""# Iowa 2022 vs 2026 Governor Race: ΔG Method

**Version 1 (draft), built {BUILT} CST. Not yet published.**

{DISC}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki]({NEWIKI}), the origin of the ΔG method and the reverse step used here. This wiki applies the same arithmetic, unchanged, to all {{{{n:counties|N}}}} Iowa counties. Data: Iowa Secretary of State (SOS) 2022 State Canvass Summary and turnout report, the SOS election-results site for 2026, and SOS voter-registration counts published on the Iowa Data Hub; population from the Census Bureau. Compiled 19 Nov 2026.

## Pages

Start with the Cedar County audit in Nebraska. That is where the method began. The Iowa pages then build up from one county (Dubuque) to the six largest counties, to all {{{{n:counties|N}}}} counties, and to the formula.

1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Dubuque → the six largest counties → all {{{{n:counties|N}}}} counties, then solved backward for implied extra votes
3. [Locked Iowa Formula](Locked-Iowa-Formula): the equation, with a blank fill-in template
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom of ΔG
5. [Graphs](Graphs): slope chart, ΔG by population, stacked bars, paired bars, residual charts, scatter

## Statewide at a glance

| Measure | 2022 | 2026* | Change |
|---|---|---|---|
| Democratic registration (Nov 1, active + inactive) | {{{{g:all:demreg22|I}}}} | {{{{g:all:demreg26|I}}}} | {{{{g:all:demreg_change|SI}}}} ({{{{g:all:demreg_pct_change|SP1}}}}) |
| Democratic governor votes | {{{{g:all:D22|I}}}} | {{{{g:all:D26|I}}}}* | {{{{g:all:D_change|SI}}}}* ({{{{g:all:D_gain_pct|SP1}}}}) |
| Total ballots | {{{{g:all:ballots22|I}}}} | {{{{g:all:ballots26|I}}}}* | {{{{g:all:ballots_change|SI}}}}* ({{{{g:all:ballots_change_pct|SP1}}}}) |
| Democratic share of ballots (S) | {{{{g:all:S22|P2}}}} | {{{{g:all:S26|P2}}}}* | {{{{g:all:residual|SF2}}}} pts* |
| Democratic registration share (R) | {{{{g:all:R22|P2}}}} | {{{{g:all:R26|P2}}}} | {{{{g:all:reg_share_change|SF2}}}} pts |
| G = S − R | {{{{g:all:G22|SF2}}}} | {{{{g:all:G26|SF2}}}}* | ΔG {{{{g:all:dG|SF2}}}}* |

## County results in brief

- **ΔG rose in all {{{{st:dG:pos|N}}}} counties.** Median ΔG is {{{{st:dG:median|SF2}}}}\\* (about {{{{st:dG:median|SF1}}}}), with a range from {{{{st:dG:min|SF2}}}}\\* ({{{{L:bottom_dG|L}}}}) to {{{{st:dG:max|SF2}}}}\\* ({{{{L:top_dG|L}}}}). {{{{st:dG:within3|N}}}} of {{{{n:counties|N}}}} counties are within 3 points of the median.
- **Residual after the registration-loss step** (ΔG minus the registration-share decline): median {{{{st:residual:median|SF2}}}}\\*, positive in all {{{{st:residual:pos|N}}}} counties, {{{{st:residual:within3|N}}}} of {{{{n:counties|N}}}} within 3 points of the median.
- **Solved backward (hypothesis):** the residuals add up to {{{{g:all:residual_votes_sum|I}}}}\\* implied extra votes across the {{{{n:counties|N}}}} counties ({{{{g:all:gain_over_2022_share|I}}}}\\* on the pooled statewide numbers). These are the votes a hypothesis of added or switched votes would have to account for, not votes shown to be improper. See [Bottom-Up Reverse Math](Reverse-Math).
- **Ceiling and floor:** {{{{n:ceiling_gt15|N}}}} of {{{{n:counties|N}}}} counties have ΔG above 15. The top five are {{{{L:top5|L}}}}; the floor (most Republican baseline) is {{{{L:floor4|L}}}}. See [Floor and Ceiling Counties](Floor-and-Ceiling).

## Read this before using the numbers

- **The swing was large and close to uniform.** Iowa's counties moved together, so most of them clear the Nebraska ceiling test. The ceiling counties are the top of one continuous spread, not a separate group.
- **The 2018→2022 control cycle is just as tight.** The same formula run on 2018→2022 (official both years) gives a residual spread of SD {{{{st:residual_1822:sd|F2}}}}, against {{{{st:residual:sd|F2}}}}\\* for 2022→2026 (Brown-Forsythe p = {{{{n:bf_p_residual|F2}}}}). In that cycle G fell in all {{{{st:dG_1822:neg|N}}}} counties (median ΔG {{{{st:dG_1822:median|SF2}}}}). A uniform residual by itself is what an ordinary statewide swing looks like.
- **A residual is not evidence of altered votes.** Candidate choice, crossover voting by Republicans and no-party voters, turnout differences, and registration-list maintenance all move these numbers. The arithmetic cannot separate them.
- **2026 is unofficial.** Every 2026 figure is marked \\* and will be re-run after the State Canvass.

---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Locked Iowa Formula](Locked-Iowa-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Cedar County Audit (Nebraska)]({CEDAR})
"""

PAGES['Reverse-Math'] = f"""# Bottom-Up Reverse Math

{DISC}

The same arithmetic at three levels, from one county up to the whole state, then solved backward for implied extra votes. Ballots denominator (Democratic governor votes ÷ total ballots cast). The method comes from the [Cedar County Audit]({CEDAR}) in Nebraska.

## Step 1: Dubuque County

| Step | Value |
|---|---|
| Democratic vote share | {{{{{e}S22|P2}}}} (2022) → {{{{{e}S26|P2}}}}* (2026): **{{{{{e}residual|SF2}}}} points*** |
| Democratic registration share | {{{{{e}R22|P2}}}} → {{{{{e}R26|P2}}}}: **{{{{{e}reg_share_change|SF2}}}} points** |
| ΔG = vote-share growth − registration-share change | {{{{{e}residual|F2}}}} − ({{{{{e}reg_share_change|F2}}}}) = **{{{{{e}dG|SF2}}}} points*** |
| Reverse step: ΔG − registration-share loss | {{{{{e}dG|F2}}}} − {{{{{e}reg_share_loss|F2}}}} = {{{{{e}residual|F2}}}} (the residual) |
| Implied extra votes | {{{{{e}D26|I}}}}* − {{{{{e}S22|P2}}}} × {{{{{e}ballots26|I}}}}* = **about {{{{{e}residual_votes|SI}}}}*** |
| Registration-scaled gap (the Nebraska wiki's "gap in votes" line, for comparison) | {{{{{e}D26|I}}}}* − {{{{{e}D22|I}}}} × ({{{{{e}demreg26|I}}}} ÷ {{{{{e}demreg22|I}}}}) = about {{{{{e}gap_votes|SI}}}}* |

## Step 2: the six largest counties

Largest to smallest population.

| County | Population | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026* | Ballots 2022 → 2026* | Vote-share growth* (pts) | Registration-share change (pts) | ΔG* (pts) | Implied extra votes* |
|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(row_six(c) for c in SIX) + f"""

ΔG is positive in all six ({{{{gd:six:dG:min|SF2}}}} to {{{{gd:six:dG:max|SF2}}}}\\*). {{{{n:six_below_median|N}}}} of the six largest counties are below the statewide median ΔG ({{{{st:dG:median|SF2}}}}\\*); Johnson is the lowest of the six.

† Dallas gained registered Democrats ({{{{c:Dallas:demreg22|I}}}} → {{{{c:Dallas:demreg26|I}}}}), so under the Nebraska rule it is a non-loss county and gets raw numbers only. Its residual is shown for completeness and is included in the statewide sums, because its registration *share* still fell ({{{{c:Dallas:reg_share_change|SF2}}}} points).

## Step 3: all {{{{n:counties|N}}}} counties

| Group | Counties | Dem vote share | Dem registration share | Vote-share growth* | Reg-share change | Pooled ΔG* | County median ΔG* (range) | Implied extra votes* |
|---|---|---|---|---|---|---|---|---|
{grp_row('Six largest counties', 'six')}
{grp_row('Other counties', 'other93')}
{grp_row('All Iowa counties', 'all')}

ΔG is positive in all {{{{st:dG:pos|N}}}} counties. The six largest counties moved a little less than the rest of the state (pooled ΔG {{{{g:six:dG|SF2}}}}\\* vs {{{{g:other93:dG|SF2}}}}\\*). County size explains almost none of the spread (R² = {{{{n:r2_dG_log10pop|F3}}}} against log population).

## Solving backward: implied extra votes (hypothesis)

For each county, implied extra votes = 2026 Democratic votes − (2022 Democratic share of ballots × 2026 ballots). That is how many more Democratic votes the county cast than it would have at its 2022 share on 2026 turnout.

| Measure | Votes |
|---|---|
| Sum of the {{{{n:counties|N}}}} county figures | {{{{g:all:residual_votes_sum|I}}}}* |
| Statewide, pooled: ({{{{g:all:S26|P2}}}} − {{{{g:all:S22|P2}}}}) × {{{{g:all:ballots26|I}}}} ballots | {{{{g:all:gain_over_2022_share|I}}}}* |
| Raw rise in Democratic votes | {{{{g:all:D_change|SI}}}}* = {{{{g:all:gain_over_2022_share|I}}}} share gain + {{{{g:all:turnout_part|I}}}} from more ballots at the 2022 share |
| Offset need for the {{{{g:all:reg_share_loss|F2}}}}-point registration-share decline: switched / added votes | {{{{g:all:offset_flips_0|I}}}} / {{{{g:all:offset_additions_0|I}}}} |
| Same, with a 1-point cushion | {{{{g:all:offset_flips_1|I}}}} / {{{{g:all:offset_additions_1|I}}}} |
| Same, with a 2-point cushion | {{{{g:all:offset_flips_2|I}}}} / {{{{g:all:offset_additions_2|I}}}} |

Offset need: switched votes = s × N; added votes = s × N ÷ (1 − p + s), where s is the registration-share decline (plus any cushion), N is 2026 ballots and p is the 2026 Democratic share of ballots. The pooled statewide figure, {{{{g:all:gain_over_2022_share|I}}}}\\*, is {{{{g:all:ratio_low|F2}}}} to {{{{g:all:ratio_high|F2}}}} times the offset need.

> **Hypothesis label.** Turning the residual into "implied extra votes" and calling them injected, switched or offset votes is a hypothesis the arithmetic cannot test. The same number reflects candidate choice, crossover voting, turnout changes and any other cause. Candidate votes are not turnout, and registered Democrats are not the only people who vote for Democrats.

## What the arithmetic cannot tell you

- **The control cycle looks the same.** Run on 2018→2022, the same residual has SD {{{{st:residual_1822:sd|F2}}}} (vs {{{{st:residual:sd|F2}}}}\\* now; Brown-Forsythe p = {{{{n:bf_p_residual|F2}}}}). A tight, near-uniform residual is what a statewide swing produces; in 2018→2022 it ran the other way, with G falling in all {{{{st:dG_1822:neg|N}}}} counties.
- **The swing was near-uniform.** {{{{st:residual:within3|N}}}} of {{{{n:counties|N}}}} county residuals are within 3 points of the median ({{{{st:residual:median|SF2}}}}\\*).
- **2026 is unofficial.** These totals come from the SOS results site and will be re-run after the State Canvass.

![Residual bars by population]({RAW}IA_Residual_Bars_by_Population.png)

*Residual (ΔG minus registration-share loss) for all {{{{n:counties|N}}}} counties, largest to smallest population.*

---
**Related:** [Locked Iowa Formula](Locked-Iowa-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Home](Home)
"""

PAGES['Locked-Iowa-Formula'] = f"""# Locked Iowa Formula

{DISC}

## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ total ballots cast × 100
- **R** (Democratic registration share) = Democratic registered voters ÷ total registered voters (active + inactive, SOS Nov 1 report) × 100
- **G** = S − R
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (R2026 − R2022)
- **Reverse step (registration-loss subtraction):** residual = ΔG − (R2022 − R2026) = S2026 − S2022, the vote-share growth left after subtracting the expected loss from the registration-share decline
- **Solved backward, implied extra votes:** D2026 − (S2022 ÷ 100) × ballots2026
- **Registration-scaled gap** (the Nebraska wiki's "gap in votes" line, for comparison only): D2026 − D2022 × (RegDem2026 ÷ RegDem2022)

**Denominator.** Total ballots cast: the SOS 2022 turnout report and the "Ballots Cast" column on the 2026 SOS results site. In 2022, total ballots equal the governor-race total including undervotes and overvotes in {{{{n:gov22_eq_ballots|N}}}} of {{{{n:counties|N}}}} counties. The current Nebraska pages divide by total votes in the governor race instead. On Iowa's numbers that alternative raises county ΔG by {{{{n:gv_vs_ballots_mean_diff|F2}}}} points on average; this wiki uses ballots throughout.

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
| 11 | If yes: residual = line 8 − \\|line 9\\| | | ______ |
| 12 | Implied extra votes = line 1 (2026) − line 3 (2022) ÷ 100 × line 2 (2026) | | ______ |
| 13 | Registration-scaled gap = line 1 (2026) − line 1 (2022) × (line 4 2026 ÷ line 4 2022) | | ______ |

## Rules for using this formula

1. **If a county lost Democratic registration, run the residual step.** Subtract the registration-share loss from ΔG (line 11) and solve backward for implied extra votes (line 12). In Iowa, {{{{n:demreg_fell|N}}}} of {{{{n:counties|N}}}} counties lost registered Democrats. The exception is {{{{L:nonloss|L}}}} ({{{{c:Dallas:demreg22|I}}}} → {{{{c:Dallas:demreg26|I}}}}), a **non-loss county**: report its raw numbers. Its registration *share* still fell ({{{{c:Dallas:reg_share_change|SF2}}}} points), so its line 11 equals its vote-share growth.
2. **The starting point is different in every state. Don't assume Nebraska's numbers carry over.** Iowa's statewide ΔG was {{{{g:all:dG|SF2}}}}\\* and its county median {{{{st:dG:median|SF2}}}}\\*. Compare Iowa counties with Iowa's own range, not with Nebraska's.
3. **Always pull out the ceiling and floor counties.** In Iowa the ceiling county is {{{{L:top_dG|L}}}} ({{{{c:Crawford:dG|SF2}}}}\\*) and the lowest ΔG is {{{{L:bottom_dG|L}}}} ({{{{c:Lyon:dG|SF2}}}}\\*). No Iowa county has a negative ΔG. See [Floor and Ceiling Counties](Floor-and-Ceiling).

**Terms used in this wiki** (full definitions on [Floor and Ceiling Counties](Floor-and-Ceiling#terminology)):
- **Ceiling counties**: the five largest ΔG ({{{{L:top5|L}}}}).
- **Floor counties**: the most Republican baseline, the four lowest 2022 Democratic registration shares ({{{{L:floor4|L}}}}).
- **Non-loss counties**: no Democratic registration loss ({{{{L:nonloss|L}}}}). Raw numbers only.

## Worked example: Dubuque

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | {{{{{e}D22|I}}}} | {{{{{e}D26|I}}}}* |
| 2 | Total ballots cast | {{{{{e}ballots22|I}}}} | {{{{{e}ballots26|I}}}}* |
| 3 | S | {{{{{e}S22|F2}}}} | {{{{{e}S26|F2}}}}* |
| 4 | Democratic registered | {{{{{e}demreg22|I}}}} | {{{{{e}demreg26|I}}}} |
| 5 | Total registered | {{{{{e}totreg22|I}}}} | {{{{{e}totreg26|I}}}} |
| 6 | R | {{{{{e}R22|F2}}}} | {{{{{e}R26|F2}}}} |
| 7 | G | {{{{{e}G22|SF2}}}} | {{{{{e}G26|SF2}}}}* |
| 8 | ΔG | | {{{{{e}dG|SF2}}}}* |
| 9 | Registration-share change | | {{{{{e}reg_share_change|SF2}}}} |
| 10 | Registration fell? | | Yes |
| 11 | Residual | | {{{{{e}residual|F2}}}}* |
| 12 | Implied extra votes | | {{{{{e}residual_votes|SI}}}}* |
| 13 | Registration-scaled gap | | {{{{{e}gap_votes|SI}}}}* |

---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Cedar County Audit (Nebraska)]({CEDAR}) · [Home](Home)
"""

PAGES['Floor-and-Ceiling'] = f"""# Floor and Ceiling Counties

{DISC}

## How to read floor and ceiling counties

Look for the pattern at both ends. The ceiling counties are the ones with the highest ΔG; in Iowa those are {{{{L:top5|L}}}}. The floor counties are the most Republican baseline counties, where there were the fewest Democrats to move.

- **The floor** by ΔG is the single county with the lowest ΔG in the state. In Iowa that's {{{{L:bottom_dG|L}}}}, at {{{{c:Lyon:dG|SF2}}}}\\*. Unlike Nebraska, no Iowa county has a negative ΔG, so the floor is the smallest rise, not a decline.
- **The ceiling** is the single county with the highest ΔG in the state. In Iowa that's {{{{L:top_dG|L}}}}, at {{{{c:Crawford:dG|SF2}}}}\\*.

Every state has its own floor and ceiling. Those two extremes set the range the rest of that state's counties fall within.

## Terminology

- **Ceiling counties** are residual counties with the largest positive ΔG: they lost registered Democrats and moved most. {{{{L:top5|L}}}}: """ + ', '.join(f"{c} {{{{c:{c}:dG|SF2}}}}\\*" for c in TOP5) + f""".
- **Floor counties** are the most Republican baseline: the four lowest 2022 Democratic registration shares. """ + ', '.join(f"{c} {{{{c:{c}:R22|P1}}}} (ΔG {{{{c:{c}:dG|SF2}}}}\\*)" for c in FLOOR4) + f""". Read by ΔG instead, the five lowest are {{{{L:lowest5_dG|L}}}}. Lyon and Sioux are on both lists.
- **Non-loss counties** had no Democratic registration loss. Raw numbers only, no residual step:
  - Dallas: registered Democrats {{{{c:Dallas:demreg22|I}}}} → {{{{c:Dallas:demreg26|I}}}}; Democratic governor votes {{{{c:Dallas:D22|I}}}} → {{{{c:Dallas:D26|I}}}}\\*.
- **Registration fell and votes fell too:** none in Iowa. Democratic governor votes rose in all {{{{n:D_rose|N}}}} counties.
- **Ballots fell, Democratic votes rose** ({{{{n:ballots_fell_D_rose|N}}}} counties): {{{{L:ballots_fell_D_rose|L}}}}. These are flagged for how their votes moved, not because their ΔG is unusual.

## Most Iowa counties clear the ceiling test

{{{{n:ceiling_gt15|N}}}} of {{{{n:counties|N}}}} counties have ΔG above 15, and {{{{n:jump14_regfell|N}}}} had a vote-share jump of 14 points or more while their registration share fell. That reflects the size of Iowa's statewide swing (median ΔG {{{{st:dG:median|SF2}}}}\\*), not a separate group of ceiling counties: the top five sit at the top of one continuous spread. Only {{{{n:not_gt15|N}}}} counties are at or below 15: {{{{L:not_gt15|L}}}}.

An earlier run (Nov 18) used the governor-race total as the denominator. On that basis {{{{n:gv_ceiling_gt15|N}}}} counties are above 15 and the top five are {{{{L:gv_top5|L}}}}. This page uses the locked ballots denominator.

## Ceiling and floor detail

Largest to smallest population.

| County | Group | Population | G 2022 | G 2026* | ΔG* | Dem reg share 2022 → 2026 | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026* | Implied extra votes* |
|---|---|---|---|---|---|---|---|---|---|
""" + '\n'.join(row_cf(c) for c in CF) + f"""

**Ceiling profile.**
- **Starting G:** {{{{n:top5_flip|N}}}} of 5 ceiling counties began 2022 with a negative G (Democratic vote share behind registration share) and turned positive in 2026. Statewide, {{{{n:flip|N}}}} counties flipped from negative to positive; the number of counties with a negative G in 2026 is {{{{n:G26_neg|N}}}}.
- **Registration decline:** Democratic registration fell in {{{{n:top5_demreg_fell|N}}}} of 5, by {{{{n:top5_demreg_pct_min|SP1}}}} to {{{{n:top5_demreg_pct_max|SP1}}}}.
- **Voting method:** all Iowa counties vote at precinct polling places plus absentee ballots. Iowa law does not allow vote centers in general elections ([Iowa Code § 49.11](https://www.legis.iowa.gov/docs/code/49.11.pdf)), so Iowa has no vote-center vs precinct or all-mail vs precinct contrast like Nebraska's.

**Floor profile.** The four floor counties are in the northwest corner of the state and have the lowest Democratic registration shares. All four rose, and {{{{n:floor4_below_median|N}}}} of 4 rose less than the statewide median ΔG.

Statewide, ΔG rose in {{{{st:dG:pos|N}}}} of {{{{n:counties|N}}}} counties (median about {{{{st:dG:median|SF1}}}}).

{img('IA_DeltaG_by_Population.png', 'Delta-G by population, ceiling and floor counties marked', 'All 99 counties, ΔG in population order. Orange: ceiling (5 largest ΔG). Blue: floor (4 lowest 2022 Democratic registration share). Dashed red line at ΔG = 15.')}
{img('IA_Slope_G2022_to_G2026.png', 'County slope chart, G 2022 to G 2026', 'Each line is one county, G 2022 to G 2026*. Ceiling counties in orange, floor counties in blue, labeled with ΔG.')}
---
**Related:** [Bottom-Up Reverse Math](Reverse-Math) · [Graphs](Graphs) · [Locked Iowa Formula](Locked-Iowa-Formula) · [Home](Home)
"""

PAGES['Graphs'] = f"""# Graphs

{DISC}

All charts use the ballots denominator and list counties largest to smallest population unless the title says otherwise.

## 1. County slope chart

{img('IA_Slope_G2022_to_G2026.png', 'County slope chart, G 2022 to G 2026', 'Each line is one county, G 2022 to G 2026*. G rose in all 99 counties. Orange: the five ceiling counties; blue: the four floor counties; each labeled with its ΔG*.')}
## 2. ΔG by population

{img('IA_DeltaG_by_Population.png', 'Delta-G for all 99 counties in population order, floor and ceiling marked', 'All 99 counties in population order. Ceiling: Crawford is the highest ΔG*. Floor by ΔG: Lyon is the lowest*. Dashed red line at 15.')}
## 3. Stacked share bars with registration loss

{img('IA_Stacked_Share_Reg_Loss_by_Population.png', 'Vote-share gain above the line, registration-share loss below, by population', 'Democratic vote-share gain (above the line: 2022 share plus 2022 to 2026 gain*) and registration-share loss (below the line), all 99 counties in population order.')}
{img('IA_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png', 'Vote-share gain above the line, registration-share loss below, sorted by 2022 Democratic share', 'The same bars sorted by 2022 Democratic share of ballots, highest to lowest.')}
## 4. Paired bars, 2022 vs 2026

{img('IA_Paired_Bars_Dem_Share_2022_2026.png', 'Democratic share of ballots 2022 vs 2026 by county', 'Democratic share of ballots, 2022 (blue) and 2026* (orange), all 99 counties in population order.')}
## 5. Residual charts

{img('IA_Residual_Bars_by_Population.png', 'Residual bars by population', 'Residual (ΔG minus registration-share loss) for all 99 counties. Shaded band: median ±3 points.')}
{img('IA_Residual_Strip_2022_2026_vs_2018_2022_Control.png', 'Residual strip chart, 2022 to 2026 vs the 2018 to 2022 control', 'Top: 2022 to 2026* residual. Bottom: the same formula on 2018 to 2022 (official both years). The spread is about the same in both cycles; only the direction and size of the shift differ. Orange: counties where Democratic votes rose while total ballots fell.')}
## 6. ΔG scatter (population)

{img('IA_DeltaG_vs_Population_Scatter.png', 'Delta-G versus population, all 99 counties', 'ΔG* against population (log scale) for all 99 counties. County size explains almost none of the spread.')}
---
**Related:** [Floor and Ceiling Counties](Floor-and-Ceiling) · [Bottom-Up Reverse Math](Reverse-Math) · [Locked Iowa Formula](Locked-Iowa-Formula) · [Home](Home)
"""

PH = re.compile(r'\{\{([^|}]+)\|([A-Z0-9]+)\}\}')
claims = []; os.makedirs(WIKI, exist_ok=True)
for name, tpl in PAGES.items():
    def sub(m):
        key, f = m.group(1), m.group(2)
        v = val(key); text = v if f == 'L' else FMTS[f](v)
        claims.append(dict(page=name, key=key, fmt=f, text=text, value=(v if isinstance(v, str) else float(v))))
        return text
    out = PH.sub(sub, tpl)
    assert '{{' not in out, name
    open(os.path.join(WIKI, name + '.md'), 'w').write(out)
    open(os.path.join(ROOT, 'data', 'wiki_skeleton_' + name + '.md'), 'w').write(PH.sub('\uE000', tpl))
json.dump(claims, open(os.path.join(ROOT, 'data', 'wiki_claims.json'), 'w'), indent=0)
print(len(claims), 'claims across', len(PAGES), 'pages')
