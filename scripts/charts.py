"""Charts for the Iowa wiki (ballots denominator). Reads data/iowa_wiki_99_counties_by_population.csv."""
import os, json, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, 'data', 'iowa_wiki_99_counties_by_population.csv'))
J = json.load(open(os.path.join(ROOT, 'data', 'summary.json')))
UNOFF = f"2026 figures UNOFFICIAL (Iowa SOS ENR EID 127077, v{J['enr_version']}, updated {J['enr_updated']}); † = county not yet certified on ENR ({', '.join(J['uncertified'])})."
SRC = ("Sources: Iowa SOS 2022 State Canvass Summary and turnout report; Iowa SOS ENR 2026 (unofficial); "
       "Iowa SOS voter registration via Iowa Data Hub, Nov 1 (active + inactive); Census V2025 population.")
DEF = "Dem share = Dem governor votes ÷ total ballots cast. G = Dem share − Dem registration share. ΔG = G 2026 − G 2022."
ORANGE, BLUE, GRAY, NAVY = '#E8771E', '#2F6DB5', '#9AA3AD', '#1B2A4A'
top5, floor4 = J['top5'], J['floor4']
lab = lambda c: c + ('†' if c in J['uncertified'] else '')
x = np.arange(len(df))

def foot(fig, extra=''):
    fig.text(0.01, 0.012, (extra + '\n' if extra else '') + DEF + '\n' + UNOFF + '\n' + SRC, fontsize=7.5, color='#444', va='bottom')

def xt(ax, d=df):
    ax.set_xticks(np.arange(len(d))); ax.set_xticklabels([lab(c) for c in d.county], rotation=90, fontsize=6.5)
    ax.set_xlim(-0.8, len(d) - 0.2)

def save(fig, name):
    fig.savefig(os.path.join(ROOT, name), dpi=150); plt.close(fig); print('wrote', name)

# 1. Delta-G by population
fig, ax = plt.subplots(figsize=(18, 8)); fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.99)
col = [ORANGE if c in top5 else BLUE if c in floor4 else GRAY for c in df.county]
ax.bar(x, df.dG, color=col, width=0.8)
ax.axhline(15, color='red', ls='--', lw=1.3, label='ΔG = 15')
ax.axhline(J['dG']['median'], color=NAVY, lw=1, label=f"median ΔG +{J['dG']['median']:.2f}*")
for i, r in df.iterrows():
    if r.county in top5 + floor4:
        ax.text(i, r.dG + 0.3, f"{r.county}\n{r.dG:+.2f}*", ha='center', fontsize=7, color=ORANGE if r.county in top5 else BLUE, fontweight='bold')
xt(ax); ax.set_ylabel('ΔG (percentage points)'); ax.set_ylim(0, 30)
ax.set_title(f"Iowa governor, ΔG 2022→2026* by county, largest to smallest population ({J['n_ceiling_gt15']} of 99 counties above 15)", fontsize=13, fontweight='bold')
from matplotlib.patches import Patch
h, l = ax.get_legend_handles_labels()
ax.legend(h + [Patch(color=ORANGE), Patch(color=BLUE), Patch(color=GRAY)], l + ['Ceiling: 5 largest ΔG', 'Floor: 4 lowest 2022 Dem registration share', 'Other counties'], loc='upper right', fontsize=8.5, ncol=2)
foot(fig, 'Iowa ΔG rose in all 99 counties; most clear 15 because the statewide swing was large and near-uniform, not because a separate group stands out.'); save(fig, 'IA_DeltaG_by_Population.png')

# 2. Residual bars by population
med = J['residual']['median']
fig, ax = plt.subplots(figsize=(18, 8)); fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.99)
ax.axhspan(med - 3, med + 3, color='#DCE8F5', label=f"median ±3 pts ({J['residual']['within3']} of 99)")
ax.bar(x, df.residual, color=[ORANGE if c in top5 else BLUE if c in floor4 else '#4A7BB7' for c in df.county], width=0.8)
ax.axhline(med, color=NAVY, lw=1.2, label=f'median residual +{med:.2f}*')
xt(ax); ax.set_ylabel('Residual (points) = ΔG − registration-share loss'); ax.set_ylim(0, 26)
ax.set_title('Iowa governor: per-county residual after subtracting the expected loss from Dem registration-share decline, 2022→2026*', fontsize=12.5, fontweight='bold')
ax.legend(loc='upper right', fontsize=9)
foot(fig, 'Residual = ΔG − (Dem registration share 2022 − 2026) = change in Dem share of ballots. Orange = ceiling 5, blue = floor 4.'); save(fig, 'IA_Residual_Bars_by_Population.png')

# 3. Strip chart: 2022-26 residual vs 2018-22 control residual, each centered on its own median
fig, axs = plt.subplots(2, 1, figsize=(16, 9), sharex=True); fig.subplots_adjust(bottom=0.17, top=0.9, left=0.06, right=0.99, hspace=0.25)
nine = J['ballots_fell_D_rose']
for ax, colname, key, title in [(axs[0], 'residual', 'residual', '2022→2026* residual (change in Dem share of ballots)'),
                                (axs[1], 'residual_1822', 'residual_1822', '2018→2022 control residual (same formula, official both years)')]:
    m = J[key]['median']; v = df[colname]
    ax.axhspan(m - 3, m + 3, color='#DCE8F5', label=f"median ±3 pts: {J[key]['within3']} of 99 counties")
    ax.axhline(m, color=NAVY, lw=1.2)
    c = [ORANGE if (k in nine and key == 'residual') else '#3E6A96' for k in df.county]
    ax.scatter(x, v, c=c, s=34, edgecolor='white', lw=0.6, zorder=3)
    for i, r in df.iterrows():
        if abs(r[colname] - m) > 5: ax.annotate(r.county, (i, r[colname]), textcoords='offset points', xytext=(0, -11 if r[colname] < m else 5), ha='center', fontsize=7.5)
    ax.set_title(f"{title}: median {m:+.2f}, SD {J[key]['sd']:.2f}", fontsize=11, loc='left')
    ax.set_ylim(m - 8, m + 8); ax.set_ylabel('points'); ax.legend(loc='upper right', fontsize=8.5)
axs[0].scatter([], [], c=ORANGE, label=f'Dem votes rose while total ballots fell ({len(nine)})'); axs[0].legend(loc='upper right', fontsize=8.5)
axs[1].set_xticks([0, 98]); axs[1].set_xticklabels(['Largest county (Polk)', 'Smallest county (Adams)']); axs[1].get_xticklabels()[0].set_ha('left'); axs[1].get_xticklabels()[1].set_ha('right'); axs[1].set_xlabel('All 99 counties, largest → smallest population')
fig.suptitle('Iowa residual strip chart: 2022→2026* vs the 2018→2022 control cycle', fontsize=13, fontweight='bold')
foot(fig, f"Spread is about the same in both cycles (SD {J['residual']['sd']:.2f} vs {J['residual_1822']['sd']:.2f}; Brown-Forsythe p = {J['bf_p_residual']:.2f}). Only the direction and size of the shift differ.")
save(fig, 'IA_Residual_Strip_2022_2026_vs_2018_2022_Control.png')

# 4/5. Stacked share with registration-share loss
def stacked(d, name, order_label):
    fig, ax = plt.subplots(figsize=(18, 8.5)); fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.99)
    xx = np.arange(len(d))
    ax.bar(xx, d.S22, color=BLUE, width=0.8, label='2022 Dem share of ballots')
    ax.bar(xx, d.residual, bottom=d.S22, color=ORANGE, width=0.8, label='Gain in Dem share, 2022→2026* (total = 2026 share)')
    ax.bar(xx, -d.reg_share_loss, color=NAVY, width=0.8, label='Dem registration-share loss, 2022→2026 (points, below 0)')
    ax.axhline(0, color='black', lw=0.8)
    nlab = 0
    for i, (_, r) in enumerate(d.iterrows()):
        if r.county in top5 or r.county in floor4:
            nlab += 1
            ax.text(i, r.S26 + 0.8 + 6 * (nlab % 3), f"{r.county}\n+{r.residual:.1f}", ha='center', fontsize=6.8, color=ORANGE if r.county in top5 else BLUE, fontweight='bold')
    xt(ax, d); ax.set_ylabel('Percentage points'); ax.set_ylim(-10, 85)
    ax.set_title(f'Iowa governor: Dem vote-share gain (above 0) vs Dem registration-share loss (below 0), 2022→2026*, {order_label}', fontsize=12.5, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    foot(fig, 'Above zero: blue + orange = 2026 Dem share of ballots. Below zero: points of Dem registration share lost (active + inactive, Nov 1). Labels: ceiling (orange) and floor (blue) counties, gain in points.'); save(fig, name)
stacked(df, 'IA_Stacked_Share_Reg_Loss_by_Population.png', 'largest to smallest population')
stacked(df.sort_values('S22', ascending=False).reset_index(drop=True), 'IA_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png', 'sorted by 2022 Dem share (high → low)')

# 6. Paired bars
fig, ax = plt.subplots(figsize=(18, 8)); fig.subplots_adjust(bottom=0.25, top=0.9, left=0.05, right=0.99)
ax.bar(x - 0.2, df.S22, width=0.4, color=BLUE, label='2022 Dem share of ballots (official)')
ax.bar(x + 0.2, df.S26, width=0.4, color=ORANGE, label='2026 Dem share of ballots*')
xt(ax); ax.set_ylabel('Dem share of ballots (%)'); ax.set_ylim(0, 80)
ax.set_title(f"Iowa governor: Dem share of ballots, 2022 vs 2026*, by county (largest to smallest population). Rose in all 99; median gain +{J['residual']['median']:.1f} pts", fontsize=12.5, fontweight='bold')
ax.legend(loc='upper right', fontsize=9); foot(fig); save(fig, 'IA_Paired_Bars_Dem_Share_2022_2026.png')

# 7. Slope chart G22 -> G26
fig, ax = plt.subplots(figsize=(11, 11)); fig.subplots_adjust(bottom=0.13, top=0.93, left=0.1, right=0.72)
for _, r in df.iterrows():
    if r.county in top5 or r.county in floor4: continue
    ax.plot([0, 1], [r.G22, r.G26], color=GRAY, lw=0.8, alpha=0.6)
def lbl(r, color):
    ax.plot([0, 1], [r.G22, r.G26], color=color, lw=2.4, marker='o', ms=4)
    return (r.G26, f"{r.county}  {r.dG:+.2f}*", color)
labels = [lbl(r, ORANGE) for _, r in df[df.county.isin(top5)].iterrows()] + [lbl(r, BLUE) for _, r in df[df.county.isin(floor4)].iterrows()]
labels.sort(key=lambda t: t[0]); last = -1e9
for y, t, c in labels:
    yy = max(y, last + 1.3); last = yy
    ax.annotate(t, xy=(1, y), xytext=(1.05, yy), color=c, fontsize=9.5, fontweight='bold', va='center', arrowprops=dict(arrowstyle='-', color=c, lw=0.6), annotation_clip=False)
ax.axhline(0, color='black', lw=0.7)
ax.set_xticks([0, 1]); ax.set_xticklabels(['G 2022 (official)', 'G 2026*']); ax.set_xlim(-0.05, 1.0)
ax.set_ylabel('G = Dem share of ballots − Dem registration share (points)')
ax.set_title(f"Iowa county slope chart, G 2022 → G 2026*\nG rose in all 99; {J['n_flip']} counties flipped from negative to positive", fontsize=12.5, fontweight='bold')
ax.text(1.05, ax.get_ylim()[1], 'Orange: ceiling (5 largest ΔG)\nBlue: floor (4 lowest 2022\nDem registration share)\nGray: other 90 counties', fontsize=9, va='top', transform=ax.transData)
foot(fig); save(fig, 'IA_Slope_G2022_to_G2026.png')

# 8. Delta-G vs population scatter
fig, ax = plt.subplots(figsize=(12, 8)); fig.subplots_adjust(bottom=0.17, top=0.92, left=0.08, right=0.98)
lp = np.log10(df.population); lr = stats.linregress(lp, df.dG)
ax.scatter(df.population, df.dG, c=[ORANGE if c in top5 else BLUE if c in floor4 else '#5B7FA6' for c in df.county], s=40, edgecolor='white', zorder=3)
xs = np.linspace(lp.min(), lp.max(), 50); ax.plot(10 ** xs, lr.intercept + lr.slope * xs, color='red', lw=1.2, ls='--', label=f'fit on log10(population): R² = {lr.rvalue**2:.3f}, p = {lr.pvalue:.2f}')
ax.axhline(15, color='gray', ls=':', lw=1)
for _, r in df.iterrows():
    if r.county in top5 + floor4 + ['Polk', 'Linn', 'Scott', 'Johnson']:
        off = {'Chickasaw': (5, -11), 'Linn': (5, 5), 'Scott': (-50, -10)}.get(r.county, (5, 3))
        ax.annotate(f"{r.county} {r.dG:+.1f}", (r.population, r.dG), textcoords='offset points', xytext=off, fontsize=8)
ax.set_xscale('log'); ax.set_xlabel('2025 population (log scale)'); ax.set_ylabel('ΔG 2022→2026* (points)')
ax.set_title('Iowa: ΔG* vs county population, all 99 counties', fontsize=13, fontweight='bold'); ax.legend(fontsize=9)
foot(fig, 'County size explains almost none of the spread in ΔG.'); save(fig, 'IA_DeltaG_vs_Population_Scatter.png')
