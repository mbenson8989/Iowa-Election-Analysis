"""Independent verification of every number in the Iowa wiki.
Re-parses the SOS source files with code separate from build_data.py:
  2022 D/R votes + ballots: the 99 official county ENR detail.xml files (Clarity, EID 115641 county sites),
      cross-checked against a fresh pdftotext of the 2022 State Canvass Summary and turnout PDFs
  2018: fresh pdftotext of the 2018 canvass + turnout PDFs
  2026: detail.txt read straight out of the ENR reports zip (v387276) + json/status.json
  Registration: Data Hub CSV (Nov 1), 2022 and 2018 cross-checked against the CoNov22 / CoNov18 SOS PDFs
  Population: Census V2025
Then recomputes each cited number (data/wiki_claims.json) and checks the published text, checks that every
number on each page is either a verified claim or an allow-listed constant, and checks image links."""
import os, re, io, csv, json, zipfile, subprocess, sys, glob, datetime, urllib.request
import xml.etree.ElementTree as ET
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fmt import FMTS
from resolve import make
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = os.path.join(ROOT, 'sources')
WIKI = os.path.join(os.path.dirname(ROOT), 'wiki')
LOG = []; P = F = 0
def check(name, ok, detail=''):
    global P, F
    P += bool(ok); F += (not ok)
    LOG.append(f"{'PASS' if ok else 'FAIL'}  {name}{'  ' + detail if detail else ''}")
def pdftext(f): return subprocess.run(['pdftotext', '-layout', os.path.join(S, f), '-'], capture_output=True, text=True).stdout
num = lambda t: int(t.replace(',', ''))

# ---------- registration (Data Hub)
REG = {}
for r in csv.DictReader(open(os.path.join(S, 'state_of_iowa_monthly_voter_registration_totals_by_county_1013_rows.csv'))):
    if r['report_date'] in ('2018-11-01', '2022-11-01', '2026-11-01'):
        v = lambda k: int(r[k] or 0)
        REG[(r['county'], r['report_date'][:4])] = (v('dem_active') + v('dem_inactive'), v('grand_total'), v('dem_active'), v('total_active'))
COUNTIES = sorted({c for c, y in REG if y == '2022'})
check('Data Hub: 99 counties for each of 2018/2022/2026', all(sum(1 for c, y in REG if y == yy) == 99 for yy in ('2018', '2022', '2026')))
# CoNov22 PDF: columns D,R,NP,O,TotalActive, D,R,NP,O,TotalInactive, Grand
t = pdftext('CoNov22.pdf'); bad = []
for c in COUNTIES:
    m = re.search(r'^\s*' + re.escape(c) + r'\s+((?:[\d,]+\s+){10}[\d,]+)\s*$', t, re.M)
    if not m: bad.append(c + ' missing'); continue
    x = [num(k) for k in m.group(1).split()]
    if (x[0] + x[5], x[10]) != REG[(c, '2022')][:2]: bad.append(c)
check('Registration 2022: Data Hub = SOS CoNov22.pdf (Dem active+inactive, grand total), 99 counties', not bad, str(bad[:5]))
t = pdftext('CoNov18.pdf'); bad = []
for c in COUNTIES:
    m = re.search(r'^\s*' + re.escape(c) + r'\s+((?:[\d,]+\s+){4,}[\d,]+)\s*$', t, re.M)
    if not m: bad.append(c + ' missing'); continue
    x = [num(k) for k in m.group(1).split()]
    if x[0] != REG[(c, '2018')][2]: bad.append(c)
check('Registration 2018: Data Hub Dem active = SOS CoNov18.pdf, 99 counties', not bad, str(bad[:5]))

# ---------- 2022 from county ENR XML (official)
E22 = {}
for f in glob.glob(os.path.join(S, 'enr2022_county', '*.zip')):
    z = zipfile.ZipFile(f); root = ET.fromstring(z.read('detail.xml'))
    reg = root.findtext('Region'); gov = [c for c in root.iter('Contest') if c.get('text').strip().startswith('Governor')]
    ch = {x.get('party'): int(x.get('totalVotes')) for x in gov[0].iter('Choice')}
    E22[reg] = dict(D=ch['DEM'], R=ch['REP'], ballots=int(root.find('VoterTurnout').get('ballotsCast')))
check('2022 county ENR XML: 99 county files', sorted(E22) == COUNTIES)
# fresh pdftotext of canvass: county -> Total row (REP, DEM, LIB, WI, UNDER, OVER, TOTAL)
def canvass_totals(fname, ncol):
    out = {}; cur = None
    for line in pdftext(fname).split('\n'):
        for c in COUNTIES:
            if re.match(r'^\s*' + re.escape(c) + r'(?:\s{2,}(?:Election\s+)?[\d,]|\s*$)', line): cur = c   # not "Page 1 of 13"
        m = re.match(r'^\s*Total\s+((?:[\d,]+\s+){%d}[\d,]+)\s*$' % (ncol - 1), line)
        if m and cur and cur not in out: out[cur] = [num(k) for k in m.group(1).split()]
    return out
C22 = canvass_totals('ia2022_govcanvsummary.pdf', 7)
check('2022 canvass PDF (fresh pdftotext): 99 county Total rows', len(C22) == 99)
T22 = {}
for line in pdftext('ia2022_turnout.pdf').split('\n'):
    m = re.match(r"^\s*([A-Z][A-Za-z' ]+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s", line)
    if m and m.group(1).strip() in COUNTIES: T22[m.group(1).strip()] = num(m.group(4))
check('2022 turnout PDF: 99 counties', len(T22) == 99)
mm = [c for c in COUNTIES if not (E22[c]['D'] == C22[c][1] and E22[c]['R'] == C22[c][0])]
check('2022 Dem/Rep governor votes: county ENR XML = State Canvass PDF, 99 counties', not mm, str(mm[:5]))
mm = [c for c in COUNTIES if T22[c] != C22[c][6]]
check('2022 ballots: SOS turnout PDF = canvass governor total incl. under/over, 99 counties', not mm, str(mm[:5]))
mm = [f"{c}: ENR XML {E22[c]['ballots']:,} vs canvass/turnout {T22[c]:,}" for c in COUNTIES if E22[c]['ballots'] != T22[c]]
LOG.append('NOTE  2022 ballots, county ENR XML snapshot (Nov 2022) vs official SOS turnout report: ' + ('; '.join(mm) if mm else 'identical in all 99') + '. The wiki uses the official SOS turnout report / State Canvass.')
# ---------- 2018 (fresh pdftotext)
C18 = canvass_totals('ia2018_govcanvsummary.pdf', 8)
T18 = {}
for line in pdftext('ia2018_turnout.pdf').split('\n'):
    m = re.match(r"^\s*([A-Z][A-Za-z' ]+?)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s", line)
    if m and m.group(1).strip() in COUNTIES: T18[m.group(1).strip()] = num(m.group(4))
check('2018 canvass + turnout PDFs: 99 counties each', len(C18) == 99 and len(T18) == 99)
mm = [c for c in COUNTIES if T18[c] != C18[c][7]]
check('2018 ballots: turnout PDF = canvass governor total incl. under/over, 99 counties', not mm, str(mm[:5]))
# ---------- 2026 ENR (unofficial)
ENR = os.path.join(S, 'enr2026_v387276')
txt = zipfile.ZipFile(os.path.join(ENR, 'reports_detailtxt.zip')).read('detail.txt').decode('utf-8', 'replace').replace('\r', '')
lines = txt.split('\n'); B26 = {}; G26 = {}
k = next(i for i, l in enumerate(lines) if 'Ballots Cast' in l)
for l in lines[k + 1:]:
    p = re.split(r'\s{2,}', l.strip())
    if len(p) < 3: break
    B26[p[0].rstrip(':')] = int(p[2])
k = next(i for i, l in enumerate(lines) if l.strip().startswith('Governor and Lt. Governor'))
for l in lines[k + 3:]:
    p = re.split(r'\s{2,}', l.strip())
    if len(p) < 12: break
    G26[p[0].rstrip(':')] = dict(R=int(p[4]), D=int(p[7]), WI=int(p[10]), tot=int(p[11]))
    if p[0].startswith('Totals'): break
check('2026 ENR: 99 counties + totals parsed (turnout and governor)', set(B26) - {'Total'} == set(COUNTIES) == set(G26) - {'Totals'})
check('2026 ENR: county sums equal ENR statewide totals (D, R, ballots)',
      sum(G26[c]['D'] for c in COUNTIES) == G26['Totals']['D'] and sum(G26[c]['R'] for c in COUNTIES) == G26['Totals']['R'] and sum(B26[c] for c in COUNTIES) == B26['Total'])
st = json.load(open(os.path.join(ENR, 'json_status.json'))); cert = dict(zip(st['P'], st['C']))
es = json.load(open(os.path.join(ENR, 'json_en_electionsettings.json')))
check('2026 ENR still unofficial (final-upload flag false)', es['settings']['electiondetails']['chkisfinalupload'] is False, 'updated ' + es.get('websiteupdatedat', ''))
try:
    req = urllib.request.Request('https://electionresults.iowa.gov/IA/127077/current_ver.txt', headers={'User-Agent': 'Mozilla/5.0'})
    cur = urllib.request.urlopen(req, timeout=20).read().decode().strip()
    check('Live ENR version check: saved v387276 is current', cur == '387276', f'live current_ver = {cur} at {datetime.datetime.now():%Y-%m-%d %H:%M} CST')
except Exception as ex:
    LOG.append(f'NOTE  live ENR version check skipped ({ex})')
# ---------- population
POP = {}
for r in csv.DictReader(open(os.path.join(S, 'co-est2025-alldata.csv'), encoding='latin-1')):
    if r['STATE'] == '19' and r['COUNTY'] != '000': POP[r['CTYNAME'][:-7]] = int(r['POPESTIMATE2025'])
# ---------- independent base table
base = pd.DataFrame([dict(county=c, population=POP[c], cert=bool(cert[c]),
    D18=C18[c][1], ballots18=T18[c], demreg18=REG[(c, '2018')][0], totreg18=REG[(c, '2018')][1],
    D22=C22[c][1], Rep22=C22[c][0], ballots22=T22[c], gov22_total=C22[c][6], gv22=sum(C22[c][:4]),
    demreg22=REG[(c, '2022')][0], totreg22=REG[(c, '2022')][1],
    D26=G26[c]['D'], Rep26=G26[c]['R'], gv26=G26[c]['tot'], ballots26=B26[c],
    demreg26=REG[(c, '2026')][0], totreg26=REG[(c, '2026')][1]) for c in COUNTIES])
val, d = make(base)
# ---------- data CSV used for charts = independent recompute
csvd = pd.read_csv(os.path.join(ROOT, 'data', 'iowa_wiki_99_counties_by_population.csv'))
check('Chart/data CSV sorted by population, largest first', list(csvd.county) == list(d.county))
for col in ['population', 'D22', 'ballots22', 'demreg22', 'totreg22', 'D26', 'ballots26', 'demreg26', 'totreg26', 'D18', 'ballots18', 'S22', 'S26', 'R22', 'R26', 'G22', 'G26', 'dG', 'residual', 'residual_votes', 'dG_1822', 'residual_1822']:
    diff = (csvd[col].astype(float).values - d[col].astype(float).values); check(f'Data CSV column {col} matches independent recompute', np.abs(diff).max() < 1e-3, f'max diff {np.abs(diff).max():.2g}')
# ---------- literal statements in the page text and chart annotations
six = d.head(6)
check('Text: "Johnson is the lowest of the six" (largest counties, by ΔG)', six.loc[six.dG.idxmin(), 'county'] == 'Johnson')
fl = set(val('L:floor4').split(', ')); lo = set(val('L:lowest5_dG').split(', '))
check('Text: "Lyon and Sioux are on both lists" (floor by registration and lowest ΔG)', fl & lo == {'Lyon', 'Sioux'})
check('Text: Graphs captions name Crawford highest and Lyon lowest ΔG', val('L:top_dG') == 'Crawford' and val('L:bottom_dG') == 'Lyon')
check('Text: Dubuque "Registration fell? Yes"', d.loc[d.county == 'Dubuque', 'demreg_change'].iloc[0] < 0)
check('Text: "no Iowa county has a negative ΔG"', (d.dG > 0).all())
check('Text: residual step identity residual = S26 - S22 in all 99', np.allclose(d.residual, d.S26 - d.S22))
J = json.load(open(os.path.join(ROOT, 'data', 'summary.json')))
for k, v in [('n_ceiling_gt15', val('n:ceiling_gt15')), ('n_flip', val('n:flip')), ('top5', val('L:top5').split(', ')), ('floor4', val('L:floor4').split(', ')),
             ('uncertified', val('L:uncertified').split(', ')), ('ballots_fell_D_rose', val('L:ballots_fell_D_rose').split(', '))]:
    check(f'Chart annotations (summary.json) {k} = independent value', J[k] == v, f'{J[k]} vs {v}')
for k in ['median', 'sd', 'within3']:
    check(f'Chart annotations (summary.json) dG/residual/residual_1822 {k}', all(abs(J[s_][k] - val(f'st:{s_}:{k}')) < 1e-9 for s_ in ('dG', 'residual', 'residual_1822')))
check('Chart annotations: Brown-Forsythe p', abs(J['bf_p_residual'] - val('n:bf_p_residual')) < 1e-9)
# ---------- every wiki claim
claims = json.load(open(os.path.join(ROOT, 'data', 'wiki_claims.json')))
seen = set()
for c in claims:
    v = val(c['key']); text = v if c['fmt'] == 'L' else FMTS[c['fmt']](v)
    tag = (c['page'], c['key'], c['fmt'])
    if tag in seen: P_dup = True
    check(f"[{c['page']}] {c['key']} ({c['fmt']}) = {c['text']}", text == c['text'], '' if text == c['text'] else f'recomputed {text}')
    seen.add(tag)
# ---------- page integrity + number coverage
ALLOW = [r'https?://\S+', r'19 Nov 2026', r'Step \d', r'[A-Za-z]+(?:2018|2022|2026)\b', r'\(\S+\.png\)', r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M CST', r'[A-Z][a-z]{2} \d{1,2} \d{4}(?: \d{2}:\d{2})?',
         r'\b(?:2018|2022|2026)\b', r'\b(?:S|R|G|D)(?:2018|2022|2026)\b', r'election 127077', r'§ 49\.11', r'Nov 1\b', r'Nov 18\b', r'19 Nov 2026', r'^\d+\. ', r'^## \d+\. ', r'^\| \d+ \|',
         r'line \d+', r'± ?3', r'within 3 points', r'ΔG = 15', r'above 15', r'at or below 15', r'Dashed red line at 15', r'14 points or more', r'\b1-point\b', r'\b2-point\b', r'× 100', r'÷ 100', r'\(1 − p \+ s\)', r'CD3',
         r'five', r'\b5 largest\b', r'\b4 lowest\b', r'\bof 5\b', r'\bof 4\b', r'all 99 counties', r'All 99 counties', r'all six', r'Version 1', r'six']
claimed = {(c['page']) for c in claims}
for page in ['Home', 'Reverse-Math', 'Locked-Iowa-Formula', 'Floor-and-Ceiling', 'Graphs']:
    sk = open(os.path.join(ROOT, 'data', f'wiki_skeleton_{page}.md')).read(); out = open(os.path.join(WIKI, page + '.md')).read()
    texts = iter([c['text'] for c in claims if c['page'] == page])
    rebuilt = re.sub('\uE000', lambda m: next(texts), sk)
    check(f'[{page}] page text = skeleton + verified claims (no unverified edits)', rebuilt == out)
    stray = []
    for ln in sk.split('\n'):
        s = ln
        for a in ALLOW: s = re.sub(a, ' ', s, flags=re.M)
        stray += re.findall(r'\d[\d,.]*', s)
    # charts are referenced by 99-county captions; the literal 99 in captions is the county count (verified n:counties)
    check(f'[{page}] no unverified numbers outside claims/allow-list', not stray, str(stray[:10]))
    for f in re.findall(r'raw\.githubusercontent\.com/mbenson8989/Iowa-Election-Analysis/main/([\w.-]+)', out):
        check(f'[{page}] image exists in repo root: {f}', os.path.exists(os.path.join(ROOT, f)))
check('Literal "99" in captions equals verified county count', val('n:counties') == 99)
# ---------- summary
hdr = [f'Iowa wiki verification, run {datetime.datetime.now():%Y-%m-%d %H:%M} CST', f'PASS {P}  FAIL {F}  (claims checked: {len(claims)})', '']
open(os.path.join(ROOT, 'VERIFY_LOG.txt'), 'w').write('\n'.join(hdr + LOG) + '\n')
print('\n'.join(hdr)); [print(l) for l in LOG if not l.startswith('PASS')]
sys.exit(1 if F else 0)
