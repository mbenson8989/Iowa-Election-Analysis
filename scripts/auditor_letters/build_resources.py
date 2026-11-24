import re, pandas as pd
W='/workspace/iowa-wiki/wiki-live/Resources.md'
t=open(W).read()
# split into sections at "## "
parts=re.split(r'(?m)^(?=## )',t)
head=parts[0]; secs={p.split('\n',1)[0][3:].strip():p for p in parts[1:]}
print(list(secs))
E=pd.read_csv('/workspace/iowa-wiki/repo-live/IA_99_County_Voting_Equipment_VerifiedVoting.csv',keep_default_na=False)
E=E.sort_values('population',ascending=False)
def rowf(r): return f"| {r.county} | {r.fips} | {r.population} | {r.marking_method_2026} | {r.election_day_tabulator_vendor_2026} | {r.election_day_tabulator_equipment_2026} | {r.mail_ballot_tabulator_equipment_2026} | {r.accessible_device_equipment_2026} | {r.paper_record_or_vvpat_2026} | {r.software_firmware_version_2026} | {r.notes} |"
# check old 25 rows match regenerated rows
old=[l for l in secs['Voting equipment by county'].split('\n') if l.startswith('| ') and not l.startswith('| County') and not l.startswith('| ---')]
new=[rowf(r) for r in E.itertuples()]
assert len(old)==25 and old==new[:25], 'old rows differ'
tbl_head="| County | FIPS | Population | Marking method | ED tabulator vendor | ED tabulator equipment | Absentee tabulator equipment | Accessible device | Paper record / VVPAT | Software/firmware | Notes | Source |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
full=[rowf(r)+f" [Verifier]({r.verified_voting_county_page_2026}) |" for r in E.itertuples()]
eq=secs['Voting equipment by county']
i=eq.index('### Largest counties'); j=eq.index('### Gaps')
eq=eq[:i]+"### All 99 counties, largest to smallest\n\n"+tbl_head+"\n"+"\n".join(full)+"\n\n"+eq[j:]
secs['Voting equipment by county']=eq

M=pd.read_csv('/workspace/iowa-auditor-letters/auditor_letter_merge_fields.csv')
sz={}
import os
for n in ['All_99_Counties']+[f'Congressional_District_{d}' for d in range(1,5)]:
    sz[n]=os.path.getsize(f'/workspace/iowa-auditor-letters/downloads/Iowa_Auditor_Letters_{n}.zip')/1e6
R='https://raw.githubusercontent.com/mbenson8989/Iowa-Election-Analysis/main/downloads/'
cdl='\n'.join(f"| Congressional District {d} | {(M.district==d).sum()} | {', '.join(sorted(M[M.district==d].county))} |" for d in range(1,5))
dl='\n'.join(f"- [Download Congressional District {d} county auditor letters (ZIP, {(M.district==d).sum()} counties, {sz[f'Congressional_District_{d}']:.1f} MB)]({R}Iowa_Auditor_Letters_Congressional_District_{d}.zip)" for d in range(1,5))
secs['County auditor letters']=f"""## County auditor letters

One letter for each of Iowa's 99 counties, addressed to that county's auditor, in both PDF and Word. In Iowa, "the county auditor of each county is designated as the county commissioner of elections" (Iowa Code § 47.2(1)), so the county auditor is the election official in every county. Each ZIP has a `PDF` folder and a `Word` folder. Pick your district, or download everything at once.

- **[Download all 99 Iowa county auditor letters (ZIP, 99 counties, {sz['All_99_Counties']:.1f} MB)]({R}Iowa_Auditor_Letters_All_99_Counties.zip)**

By congressional district:

{dl}

Not sure which district your county is in? [Download the county-to-district lookup (CSV)]({R}Iowa_County_to_District_Lookup.csv), or use the table below.

**How the counties are grouped.** The Iowa Secretary of State does not divide the state into election regions; each county auditor runs the county's elections. So these files use Iowa's four U.S. House (congressional) districts, which cover all 99 counties exactly once. The county lists come from the Iowa Secretary of State's own 2026 general election results (results site version 387276), where each county appears under exactly one U.S. Representative race. The grouping is only for convenience. It has nothing to do with how the letters or the analysis were built.

**What each letter contains.** The letters follow Morissa's Nebraska 93-county cast-vote-record request letter, in the same tone and structure as the Texas and Kansas clerk letters, rewritten for Iowa law: the county's own 2022 and 2026\\* figures for registered Democrats (active and inactive), Democratic governor votes and total ballots cast, offered as an observation and a hypothesis, not an allegation; federal litigation context (no standing claimed); a request under Iowa Code chapter 22 for existing records only (any cast vote record or results export that exists, noting the Secretary of State's statement that a cast vote record "is not generated" in Iowa; the § 50.24(3) canvass summary report by precinct; the § 50.14 printed results; the § 52.35 equipment test statement and certificate; any § 50.51 post-election audit report; and hash-verification records); a request to keep those records for the full twenty-two months under § 50.19(2) and 52 U.S.C. § 20701; a request, not a demand, that the county consider asking the Secretary of State to extend post-election audit coverage (under § 50.51 the Secretary of State chooses the audited precincts, and § 50.12 keeps sealed ballots closed except for a recount, contest, audit, or destruction); and blank date, signature, and sender lines. Addressees and mailing addresses come from the [Iowa Secretary of State's County Auditor List](https://sos.iowa.gov/elections/auditors/auditorslist.html), retrieved November 24, 2026. All 99 counties had a name and mailing address on that list, so no addressee is a placeholder. Every quotation of Iowa Code was checked word for word against the Iowa Code 2026 on legis.iowa.gov, and every county's figures in every PDF were checked against the 99-county data. Please confirm each addressee against the county's own website before sending, because officials change. Nothing has been mailed or emailed.

| District | Counties | County list |
|---|---|---|
{cdl}

"""
ac=secs['County-level results']
ac=ac.replace("- A 99-county PDF and a page explaining its columns are being reviewed and will be added here once approved.\n",
"- [Iowa County PDF Information](https://github.com/mbenson8989/Iowa-Election-Analysis/wiki/Iowa-County-PDF-Information): what each column of the county PDF means\n- [Download the 99-county PDF](https://raw.githubusercontent.com/mbenson8989/Iowa-Election-Analysis/main/Iowa_99_County_Democratic_Registration_and_Vote_Change.pdf): registered Democrats, Democratic governor votes, and total ballots for every county, 2022 vs 2026\\*, with changes and statewide totals\n")
assert 'Iowa-County-PDF-Information' in ac
secs['County-level results']=ac
sos=secs['Iowa Secretary of State data sources']
sos=sos.replace("\nCounty populations","- **County auditors:** [SOS County Auditor List](https://sos.iowa.gov/elections/auditors/auditorslist.html), used for the auditor-letter addressees\n\nCounty populations",1)
assert 'County Auditor List' in sos; secs['Iowa Secretary of State data sources']=sos

method="""## Where the method began: the Cedar County audit

The method was first worked out in Morissa Benson's [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) in her Nebraska Election Analysis wiki. This Iowa wiki applies the same approach using Iowa's own numbers only, all from the Iowa Secretary of State.

## The reverse-factoring method in brief

1. **Two shares per county, per year.** For each of the 99 counties, in 2022 and in 2026\\*, take (a) the Democratic share of all ballots cast (Democratic governor votes ÷ total ballots) and (b) **D**, the Democratic share of all registered voters (active plus inactive, SOS Nov 1 report). Iowa has party registration, so D is real registration, not a stand-in.
2. **The surplus, S.** S = (a) − D, in percentage points: the Democratic share of ballots minus the Democratic share of registration. The wiki's other pages call this G.
3. **The Iowa line.** Graph every county's surplus against its D and fit one straight line, Morissa's surplus form: **S = m × (D/100) + b**, where m is the multiplier and b is the offset in percentage points. Each state fits its own m and b from its own counties, weighted equally. Iowa's locked values for this line are still under review and will be posted on [Locked Iowa Formula](Locked-Iowa-Formula) once Morissa approves them. That page currently shows the ΔG form of the Iowa equation.
4. **Change and residuals.** ΔG is a county's surplus in 2026\\* minus its surplus in 2022. The residual is ΔG minus the drop in the county's Democratic registration share, the part of the change that registration alone does not explain. A county's residual against the line is its actual surplus minus the surplus the line predicts. See [Floor and Ceiling Counties](Floor-and-Ceiling) and [Bottom-Up Reverse Math](Reverse-Math).
5. **Checked against the source.** An independent verification script rebuilt the county figures from the raw SOS files and checked every number on the wiki pages: 491 checks passed, 0 failed ([VERIFY_LOG.txt](https://github.com/mbenson8989/Iowa-Election-Analysis/blob/main/VERIFY_LOG.txt)).

The [README](README) explains it all in plain language. This is an analytical model, with evidence for and against. It is a hypothesis, not proof of anything.

"""
law=secs['Iowa laws cited in the Attorney General letter']
law=law.replace('## Iowa laws cited in the Attorney General letter','## Iowa laws cited in the Attorney General and county auditor letters')
law=law.replace("| Iowa Code § 50.12 |","| Iowa Code § 22.3 | Supervision and fees: expenses for copies must be reasonable and \"communicated to the requester upon receipt of the request\" (§ 22.3(1)) (auditor letters) | [Iowa Code § 22.3](https://www.legis.iowa.gov/docs/code/22.3.pdf) |\n| Iowa Code § 47.2 | \"The county auditor of each county is designated as the county commissioner of elections\" (§ 47.2(1)) (auditor letters) | [Iowa Code § 47.2](https://www.legis.iowa.gov/docs/code/47.2.pdf) |\n| Iowa Code § 50.12 |",1)
law=law.replace("| Iowa Code § 50.51 |","| Iowa Code § 50.24 | County canvass by the board of supervisors; the election canvass summary report includes results, overvotes, and undervotes by precinct (§ 50.24(3)) (auditor letters) | [Iowa Code § 50.24](https://www.legis.iowa.gov/docs/code/50.24.pdf) |\n| Iowa Code § 50.51 |",1)
assert law.count('auditor letters)')==3
secs['Iowa laws cited in the Attorney General and county auditor letters']=law
fed=secs['Federal sources cited'].rstrip('\n')+"\n- Auditor letters, litigation context: *California v. Trump*, No. 1:25-cv-10810 (D. Mass.) [judgment and permanent injunction, July 13, 2026 (PDF)](https://storage.courtlistener.com/recap/gov.uscourts.mad.282905/gov.uscourts.mad.282905.194.0.pdf); *LULAC v. Executive Office of the President*, No. 1:25-cv-0946 (D.D.C.) [order of Oct. 31, 2025 (PDF)](https://storage.courtlistener.com/recap/gov.uscourts.dcd.279032/gov.uscourts.dcd.279032.217.0.pdf)\n\n"
secs['Federal sources cited']=fed
sub="""## Morissa Benson on Substack

- [Morissa Benson's Substack](https://moebenson.substack.com/) (home page, all posts)
- **Latest Substack: Article 4 / Guarantee Clause — [The Burden Just Flipped](https://moebenson.substack.com/p/the-burden-just-flipped)** (November 22, 2026). The piece is about Article IV, Section 4, the Guarantee Clause.
- [The Election Equation. And Plan](https://moebenson.substack.com/p/the-election-equation-and-plan) (November 21, 2026). The post now displays the title "The Numbers Don't Add up."
- [Who Holds The Keys](https://moebenson.substack.com/p/who-holds-the-keys) (November 18, 2026)
- [The Back Room](https://moebenson.substack.com/p/the-back-room) (November 13, 2026)

"""
order=['Letter to the Iowa Attorney General','County auditor letters','Iowa Secretary of State data sources','County-level results','Voting equipment by county',None,
 'Iowa laws cited in the Attorney General and county auditor letters','Federal sources cited','SUB','All Graphics Folder','Ten Iowa counties: the largest Democratic vote increases, 2022 to 2026','The Guarantee Clause']
out=head
for k in order:
    if k is None: out+=method
    elif k=='SUB': out+=sub
    else:
        s=secs[k]; out+=s if s.endswith('\n\n') or k=='The Guarantee Clause' else s.rstrip('\n')+'\n\n'
used=set(order)|{'Iowa laws cited in the Attorney General letter','Latest Substack: Article 4 / Guarantee Clause'}
assert set(secs)-used==set(), set(secs)-used
open('/workspace/iowa-auditor-letters/wiki/Resources.md','w').write(out)
print(len(out))
