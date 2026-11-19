"""Build the Iowa county table for the wiki from Iowa SOS source files only
(population from Census V2025). Ballots denominator (locked Iowa formula).

Sources (all in ../sources):
  gov22.txt (pdftotext of ia2022_govcanvsummary.pdf)  2022 official state canvass, governor
  ia2022_turnout.txt (pdftotext of ia2022_turnout.pdf) 2022 official ballots cast by county
  gov18.txt / ia2018_turnout.txt                      2018 official (control cycle)
  enr2026_v387276/detailtxt/detail.txt + json_status.json   2026 ENR EID 127077 (UNOFFICIAL)
  state_of_iowa_monthly_voter_registration_totals_by_county_1013_rows.csv  SOS Data Hub (Nov 1)
  co-est2025-alldata.csv                              Census Vintage 2025 population
"""
import csv, json, re, os, statistics as st
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
S = os.path.join(ROOT, 'sources'); OUT = os.path.join(ROOT, 'data')
ENR = os.path.join(S, 'enr2026_v387276')
NUM = re.compile(r'^[\d,]+$')

def vr(date):
    out = {}
    for r in csv.DictReader(open(os.path.join(S, 'state_of_iowa_monthly_voter_registration_totals_by_county_1013_rows.csv'))):
        if r['report_date'] == date:
            g = lambda k: int(r[k]) if r[k].strip() else 0
            out[r['county']] = dict(dem=g('dem_active') + g('dem_inactive'), tot=g('grand_total'))
    assert len(out) == 99, (date, len(out))
    return out

COUNTIES = sorted(vr('2022-11-01'))

def canvass(path, ncols):
    """Parse governor canvass text: returns {county: total-row values}."""
    rows = {}; cur = None; pend = None; state = None
    for line in open(path):
        toks = line.split()
        if not toks: continue
        n = 0
        while n < len(toks) and NUM.match(toks[-1 - n]): n += 1
        lab = ' '.join(toks[:len(toks) - n]).replace('Election', '').replace('Day', '').strip()
        if n == ncols:
            vals = [int(t.replace(',', '')) for t in toks[-ncols:]]
            if lab == 'Absentee': rows[cur]['abs'] = vals
            elif lab == 'Total':
                if cur in rows and 'tot' not in rows[cur]: rows[cur]['tot'] = vals
                else: state = vals
            elif lab in COUNTIES or lab == 'TOTAL': cur = lab; rows[cur] = {'ed': vals}
            elif lab == '': pend = vals
            else: raise SystemExit('unknown label %r' % lab)
        elif n == 0 and lab in COUNTIES:
            cur = lab; rows[cur] = {'ed': pend}; pend = None
    if 'TOTAL' in rows and 'tot' in rows['TOTAL']: state = rows['TOTAL']['tot']
    for c in COUNTIES:
        r = rows[c]; assert [a + b for a, b in zip(r['ed'], r['abs'])] == r['tot'], c
    return {c: rows[c]['tot'] for c in COUNTIES}, state

def turnout(path):
    t = {}
    for line in open(path):
        m = re.match(r"^\s*([A-Z][A-Za-z' ]+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d.]+)%", line)
        if m and m.group(1).strip() in COUNTIES + ['Total']:
            t[m.group(1).strip()] = int(m.group(4).replace(',', ''))
    return t

# ---- 2022 official
g22, g22_state = canvass(os.path.join(S, 'gov22.txt'), 7)      # REP, DEM, LIB, WI, UNDER, OVER, TOTAL
b22 = turnout(os.path.join(S, 'ia2022_turnout.txt'))
# ---- 2018 official (control)
g18, g18_state = canvass(os.path.join(S, 'gov18.txt'), 8)      # REP, DEM, LIB, CWP, WI, UNDER, OVER, TOTAL
b18 = turnout(os.path.join(S, 'ia2018_turnout.txt'))
# ---- 2026 ENR (unofficial)
L = open(os.path.join(ENR, 'detailtxt', 'detail.txt')).read().replace('\r', '').split('\n')
i = [k for k, l in enumerate(L) if l.startswith('County') and 'Ballots Cast' in l][0]
b26 = {}
for l in L[i + 1:]:
    m = re.match(r"^(.+?)\s{2,}(\d+)\s+(\d+)\s+([\d.]+)%", l)
    if not m: break
    b26[m.group(1).strip().rstrip(':')] = int(m.group(3))
j = [k for k, l in enumerate(L) if 'Governor and Lt. Governor' in l][0]
hdr = L[j + 1]; assert 'Zach Lahn' in hdr and 'Rob Sand' in hdr and 'Write-in' in hdr
g26 = {}
for l in L[j + 3:]:
    if not l.strip(): break
    name = l[:30].strip().rstrip(':'); v = [int(x) for x in l[30:].split()]
    g26['TOTAL' if name == 'Totals' else name] = dict(R=v[3], D=v[6], WI=v[9], tot=v[10])
    if name == 'Totals': break
stat = json.load(open(os.path.join(ENR, 'json_status.json')))
cert = dict(zip(stat['P'], stat['C']))
settings = json.load(open(os.path.join(ENR, 'json_en_electionsettings.json')))
# ---- registration + population
r18, r22, r26 = vr('2018-11-01'), vr('2022-11-01'), vr('2026-11-01')
pop = {}
for r in csv.DictReader(open(os.path.join(S, 'co-est2025-alldata.csv'), encoding='latin-1')):
    if r['STATE'] == '19' and r['COUNTY'] != '000':
        pop[r['CTYNAME'].replace(' County', '')] = int(r['POPESTIMATE2025'])
assert set(pop) == set(COUNTIES) == set(g26) - {'TOTAL'} == set(b26) - {'Total'}

rows = []
for c in COUNTIES:
    d = dict(county=c, population=pop[c], certified_2026=bool(cert[c]),
             D18=g18[c][1], ballots18=b18[c], demreg18=r18[c]['dem'], totreg18=r18[c]['tot'],
             D22=g22[c][1], Rep22=g22[c][0], ballots22=b22[c], gov22_total=g22[c][6], gv22=sum(g22[c][:4]),
             demreg22=r22[c]['dem'], totreg22=r22[c]['tot'],
             D26=g26[c]['D'], Rep26=g26[c]['R'], WI26=g26[c]['WI'], gv26=g26[c]['tot'], ballots26=b26[c],
             demreg26=r26[c]['dem'], totreg26=r26[c]['tot'])
    rows.append(d)
df = pd.DataFrame(rows)
for y in ('18', '22', '26'):
    df['S' + y] = 100 * df['D' + y] / df['ballots' + y]            # Dem share of ballots
    df['R' + y] = 100 * df['demreg' + y] / df['totreg' + y]         # Dem registration share
    df['G' + y] = df['S' + y] - df['R' + y]
df['dG'] = df.G26 - df.G22
df['reg_share_change'] = df.R26 - df.R22                          # negative = share fell
df['reg_share_loss'] = -df.reg_share_change                       # expected loss subtracted in reverse step
df['residual'] = df.dG - df.reg_share_loss                        # = S26 - S22
df['residual_votes'] = df.D26 - df.S22 / 100 * df.ballots26       # implied extra votes (hypothesis)
df['gap_votes_ne_style'] = df.D26 - df.D22 * df.demreg26 / df.demreg22
df['demreg_change'] = df.demreg26 - df.demreg22
df['demreg_pct_change'] = 100 * df.demreg_change / df.demreg22
df['D_change'] = df.D26 - df.D22
df['ballots_change'] = df.ballots26 - df.ballots22
df['dG_1822'] = df.G22 - df.G18
df['residual_1822'] = df.S22 - df.S18
df['G_flip_neg_to_pos'] = (df.G22 < 0) & (df.G26 > 0)
df['ceiling_dG_gt15'] = df.dG > 15
df['pop_rank'] = df.population.rank(ascending=False).astype(int)
df = df.sort_values('population', ascending=False).reset_index(drop=True)

# floor/ceiling groups
top5 = df.nlargest(5, 'dG').county.tolist()
floor4 = df.nsmallest(4, 'R22').county.tolist()
df['group'] = np.where(df.county.isin(top5), 'ceiling_top5', np.where(df.county.isin(floor4), 'floor', ''))

# ---- statewide
T = {}
for y in ('18', '22', '26'):
    T['D' + y] = int(df['D' + y].sum()); T['ballots' + y] = int(df['ballots' + y].sum())
    T['demreg' + y] = int(df['demreg' + y].sum()); T['totreg' + y] = int(df['totreg' + y].sum())
    T['S' + y] = 100 * T['D' + y] / T['ballots' + y]; T['R' + y] = 100 * T['demreg' + y] / T['totreg' + y]
    T['G' + y] = T['S' + y] - T['R' + y]
assert T['D22'] == g22_state[1] and T['ballots22'] == b22['Total'] == g22_state[6]
assert T['D26'] == g26['TOTAL']['D'] and T['ballots26'] == b26['Total']
T['Rep26'] = int(df.Rep26.sum()); T['Rep22'] = int(df.Rep22.sum()); T['Rep_change'] = T['Rep26'] - T['Rep22']
T['dG'] = T['G26'] - T['G22']; T['reg_share_loss'] = T['R22'] - T['R26']
T['share_gain'] = T['S26'] - T['S22']
T['D_gain'] = T['D26'] - T['D22']; T['D_gain_pct'] = 100 * T['D_gain'] / T['D22']
T['ballots_change'] = T['ballots26'] - T['ballots22']
T['gain_over_2022_share'] = T['share_gain'] / 100 * T['ballots26']
T['turnout_part'] = T['D_gain'] - T['gain_over_2022_share']
T['gap_votes_ne_style'] = T['D26'] - T['D22'] * T['demreg26'] / T['demreg22']
T['residual_votes_county_sum'] = float(df.residual_votes.sum())
N = T['ballots26']; p = T['S26'] / 100; s0 = T['reg_share_loss'] / 100
for k, add in (('0', 0), ('1', .01), ('2', .02)):
    s = s0 + add
    T['offset_flips_' + k] = s * N; T['offset_additions_' + k] = s * N / (1 - p + s)
T['ratio_low'] = T['gain_over_2022_share'] / T['offset_additions_2']
T['ratio_high'] = T['gain_over_2022_share'] / T['offset_flips_0']

def summ(x):
    x = np.asarray(x, float); med = np.median(x)
    return dict(mean=x.mean(), median=med, sd=x.std(ddof=1), min=x.min(), max=x.max(),
                within3=int((abs(x - med) <= 3).sum()), pos=int((x > 0).sum()), neg=int((x < 0).sum()))
D = dict(statewide=T, dG=summ(df.dG), residual=summ(df.residual), dG_1822=summ(df.dG_1822),
         residual_1822=summ(df.residual_1822), reg_share_loss=summ(df.reg_share_loss))
D['bf_p_residual'] = float(stats.levene(df.residual, df.residual_1822, center='median').pvalue)
D['bf_p_dG'] = float(stats.levene(df.dG, df.dG_1822, center='median').pvalue)
lr = stats.linregress(np.log10(df.population), df.dG); D['r2_dG_log10pop'] = lr.rvalue ** 2; D['p_dG_log10pop'] = lr.pvalue
D['n_ceiling_gt15'] = int(df.ceiling_dG_gt15.sum())
D['n_jump14_regfell'] = int(((df.residual >= 14) & (df.reg_share_change < 0)).sum())
D['n_flip'] = int(df.G_flip_neg_to_pos.sum()); D['n_G22_neg'] = int((df.G22 < 0).sum()); D['n_G26_neg'] = int((df.G26 < 0).sum())
D['n_demreg_fell'] = int((df.demreg_change < 0).sum()); D['n_regshare_fell'] = int((df.reg_share_change < 0).sum())
D['nonloss_counties'] = df.loc[df.demreg_change >= 0, 'county'].tolist()
D['regshare_rose_counties'] = df.loc[df.reg_share_change >= 0, 'county'].tolist()
D['D_fell_counties'] = df.loc[df.D_change < 0, 'county'].tolist()
D['ballots_fell_D_rose'] = df.loc[(df.ballots_change < 0) & (df.D_change > 0), 'county'].tolist()
D['top5'] = top5; D['floor4'] = floor4
D['lowest5_dG'] = df.nsmallest(5, 'dG').county.tolist()
D['lowest5_residual'] = df.nsmallest(5, 'residual').county.tolist()
D['uncertified'] = [c for c in COUNTIES if not cert[c]]
D['n_certified'] = int(sum(cert.values()))
D['enr_version'] = '387276'; D['enr_updated'] = settings.get('websiteupdatedat')
D['enr_final_flag'] = settings['settings']['electiondetails']['chkisfinalupload']
os.makedirs(OUT, exist_ok=True)
df.to_csv(os.path.join(OUT, 'iowa_wiki_99_counties_by_population.csv'), index=False, float_format='%.4f')
json.dump(D, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in D.items()}, indent=1, default=lambda o: round(float(o), 4)))
