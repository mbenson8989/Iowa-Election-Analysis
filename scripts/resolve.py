"""Turn a base county table (raw counts only) into every number the wiki cites.
Used by build_wiki.py (base from build_data.py) and by verify_wiki.py (base from an
independent re-parse of the SOS source files). Derived metrics are computed here from raw counts."""
import numpy as np, pandas as pd
from scipy import stats

def derive(b):
    d = b.copy()
    for y in ('18', '22', '26'):
        d['S' + y] = 100 * d['D' + y] / d['ballots' + y]
        d['R' + y] = 100 * d['demreg' + y] / d['totreg' + y]
        d['G' + y] = d['S' + y] - d['R' + y]
    d['dG'] = d.G26 - d.G22
    d['reg_share_change'] = d.R26 - d.R22
    d['reg_share_loss'] = d.R22 - d.R26
    d['residual'] = d.dG - d.reg_share_loss
    d['residual_votes'] = d.D26 - d.S22 / 100 * d.ballots26
    d['gap_votes'] = d.D26 - d.D22 * d.demreg26 / d.demreg22
    d['demreg_change'] = d.demreg26 - d.demreg22
    d['demreg_pct_change'] = 100 * d.demreg_change / d.demreg22
    d['D_change'] = d.D26 - d.D22
    d['ballots_change'] = d.ballots26 - d.ballots22
    d['Rep_change'] = d.Rep26 - d.Rep22
    d['dG_1822'] = d.G22 - d.G18
    d['residual_1822'] = d.S22 - d.S18
    if 'gv22' in d:   # governor-race-total denominator (labeled comparison only)
        d['gv_dG'] = (100 * d.D26 / d.gv26 - d.R26) - (100 * d.D22 / d.gv22 - d.R22)
    return d.sort_values('population', ascending=False).reset_index(drop=True)

def pooled(d):
    t = {k: d[k].sum() for k in ['population', 'D18', 'ballots18', 'demreg18', 'totreg18', 'D22', 'Rep22', 'ballots22', 'demreg22', 'totreg22', 'D26', 'Rep26', 'ballots26', 'demreg26', 'totreg26']}
    t = pd.DataFrame([t]); t['county'] = 'pooled'
    r = derive(t).iloc[0].to_dict()
    N = r['ballots26']; p = r['S26'] / 100; s0 = r['reg_share_loss'] / 100
    for k, add in (('0', 0), ('1', .01), ('2', .02)):
        s = s0 + add; r['offset_flips_' + k] = s * N; r['offset_additions_' + k] = s * N / (1 - p + s)
    r['gain_over_2022_share'] = r['residual'] / 100 * N
    r['turnout_part'] = r['D_change'] - r['gain_over_2022_share']
    r['D_gain_pct'] = 100 * r['D_change'] / r['D22']
    r['ballots_change_pct'] = 100 * r['ballots_change'] / r['ballots22']
    r['demreg_pct_change'] = 100 * r['demreg_change'] / r['demreg22']
    r['ratio_low'] = r['gain_over_2022_share'] / r['offset_additions_2']
    r['ratio_high'] = r['gain_over_2022_share'] / r['offset_flips_0']
    r['residual_votes_sum'] = d.residual_votes.sum()
    r['gap_votes_sum'] = d.gap_votes.sum()
    r['n'] = len(d)
    return r

def make(base):
    d = derive(base)
    six = d.head(6)
    groups = {'all': d, 'six': six, 'other93': d.iloc[6:], 'top5': d[d.county.isin(d.nlargest(5, 'dG').county)],
              'floor4': d[d.county.isin(d.nsmallest(4, 'R22').county)]}
    P = {g: pooled(x) for g, x in groups.items()}
    def dist(series, agg, dd=None):
        dd = d if dd is None else dd
        x = dd[series].astype(float).values; med = np.median(x)
        return dict(mean=x.mean(), median=med, sd=x.std(ddof=1), min=x.min(), max=x.max(),
                    within3=(abs(x - med) <= 3).sum(), pos=(x > 0).sum(), neg=(x < 0).sum(),
                    gt15=(x > 15).sum())[agg]
    names = lambda s: ', '.join(s)
    lr = stats.linregress(np.log10(d.population), d.dG)
    N = dict(
        counties=len(d), certified=int(d.cert.sum()), uncertified=int((~d.cert).sum()),
        ceiling_gt15=int((d.dG > 15).sum()), not_gt15=int((d.dG <= 15).sum()),
        jump14_regfell=int(((d.residual >= 14) & (d.reg_share_change < 0)).sum()),
        G22_neg=int((d.G22 < 0).sum()), G26_neg=int((d.G26 < 0).sum()),
        flip=int(((d.G22 < 0) & (d.G26 > 0)).sum()),
        top5_flip=int(((d.G22 < 0) & (d.G26 > 0) & d.county.isin(groups['top5'].county)).sum()),
        demreg_fell=int((d.demreg_change < 0).sum()), regshare_fell=int((d.reg_share_change < 0).sum()),
        D_rose=int((d.D_change > 0).sum()), ballots_fell_D_rose=int(((d.ballots_change < 0) & (d.D_change > 0)).sum()),
        r2_dG_log10pop=lr.rvalue ** 2, p_dG_log10pop=lr.pvalue,
        bf_p_residual=stats.levene(d.residual, d.residual_1822, center='median').pvalue,
        bf_p_dG=stats.levene(d.dG, d.dG_1822, center='median').pvalue,
        r2_resid_R22=stats.linregress(d.R22, d.residual).rvalue ** 2,
        six_below_median=int((six.dG < np.median(d.dG)).sum()),
        top5_demreg_fell=int((groups['top5'].demreg_change < 0).sum()),
        top5_demreg_pct_min=float(groups['top5'].demreg_pct_change.max()),
        top5_demreg_pct_max=float(groups['top5'].demreg_pct_change.min()),
        floor4_below_median=int((groups['floor4'].dG < np.median(d.dG)).sum()),
        floor4_min_pop=int(groups['floor4'].population.min()),
        gov22_eq_ballots=int((d.gov22_total == d.ballots22).sum()),
        gv_ceiling_gt15=int((d.gv_dG > 15).sum()),
        gv_vs_ballots_mean_diff=float((d.gv_dG - d.dG).mean()),
    )
    Lst = dict(
        top5=names(d.nlargest(5, 'dG').county), floor4=names(d.nsmallest(4, 'R22').county),
        lowest5_dG=names(d.nsmallest(5, 'dG').county), lowest5_residual=names(d.nsmallest(5, 'residual').county),
        not_gt15=names(d[d.dG <= 15].county), nonloss=names(d[d.demreg_change >= 0].county),
        D_fell=names(d[d.D_change < 0].county) or 'none',
        ballots_fell_D_rose=names(d[(d.ballots_change < 0) & (d.D_change > 0)].county),
        uncertified=names(d[~d.cert].county), six=names(six.county),
        flip=names(d[(d.G22 < 0) & (d.G26 > 0)].county),
        gv_top5=names(d.nlargest(5, 'gv_dG').county),
        top_dG=d.loc[d.dG.idxmax(), 'county'], bottom_dG=d.loc[d.dG.idxmin(), 'county'],
    )
    def val(key):
        kind, _, rest = key.partition(':')
        if kind == 'c':
            c, f = rest.split(':'); return d.loc[d.county == c, f].iloc[0]
        if kind == 'g':
            g, f = rest.split(':'); return P[g][f]
        if kind == 'st':
            s, a = rest.split(':'); return dist(s, a)
        if kind == 'gd':
            g, s_, a = rest.split(':'); return dist(s_, a, groups[g])
        if kind == 'n': return N[rest]
        if kind == 'L': return Lst[rest]
        raise KeyError(key)
    return val, d
