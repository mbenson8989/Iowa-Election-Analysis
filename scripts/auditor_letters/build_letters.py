"""Iowa county auditor letters (99). Figures: repo data/iowa_wiki_99_counties_by_population.csv (built from raw Iowa SOS files).
Addressees: Iowa SOS County Auditor List https://sos.iowa.gov/elections/auditors/auditorslist.html (retrieved 2026-11-24 via WebFetch).
Equipment: IA_99_County_Voting_Equipment_VerifiedVoting.csv. Grouping: U.S. House districts as listed in Iowa SOS ENR v387276."""
import pandas as pd, csv, os, re, json
B='/workspace/iowa-auditor-letters/'
D=pd.read_csv('/workspace/iowa-wiki/repo-live/data/iowa_wiki_99_counties_by_population.csv').set_index('county')
E=pd.read_csv('/workspace/iowa-wiki/repo-live/IA_99_County_Voting_Equipment_VerifiedVoting.csv',keep_default_na=False).set_index('county')
A={r['county']:r for r in csv.DictReader(open(B+'auditors_parsed.csv'))}
FIX={'Greene':('114 N. Chestnut','Jefferson'),'Jefferson':('51 E. Briggs','Fairfield'),'Ringgold':('109 W. Madison','Mount Ayr'),
     'Taylor':('405 Jefferson','Bedford'),'Washington':('PO Box 889','Washington')}
for c,(s,ci) in FIX.items(): A[c]['street']=s; A[c]['city']=ci
for c,r in A.items(): assert r['mailing']==f"{r['street']} {r['city']} IA {r['zip']}", (c,r['mailing'])
CD=json.load(open(B+'county_to_cd.json'))
assert set(D.index)==set(A)==set(E.index)==set(CD) and len(D)==99
OUT=B+'md/'; os.makedirs(OUT,exist_ok=True)
def f(n): return f"{int(n):,}"
def ch(a,b,star=''):
    d=int(b)-int(a); p=100*d/int(a); s='+' if d>0 else ''
    return f"{f(a)} → {f(b)}{star} ({s}{d:,}{star}, {s}{p:.1f}%{star})".replace('+-','-').replace('(-','(−').replace(', -',', −')
st=D[['demreg22','demreg26','D22','D26','ballots22','ballots26']].sum()
SW=f"Statewide, registered Democrats changed {ch(st.demreg22,st.demreg26)} and Democratic votes for governor changed {ch(st.D22,st.D26,'*')}."
rows=[]
for c in D.index:
    a=D.loc[c]; o=A[c]; e=E.loc[c]
    dr=int(a.demreg26)-int(a.demreg22); dv=int(a.D26)-int(a.D22)
    if dr<0 and dv>0: pat='In this county, Democratic registration declined while Democratic votes for governor rose.'
    elif dr<0 and dv<0: pat='In this county, Democratic registration and Democratic votes for governor both declined.'
    elif dr>0 and dv>0: pat='In this county, Democratic registration and Democratic votes for governor both rose.'
    elif dr>0 and dv<0: pat='In this county, Democratic registration rose while Democratic votes for governor declined.'
    else: pat='In this county, at least one of these figures did not change.'
    cert=('' if a.certified_2026 else f" When these figures were retrieved, the Secretary of State's results site did not yet show {c} County's 2026 results as certified by the county.")
    md=f"""# {c.upper()} COUNTY — County auditor letter (records and audit request)

Date: ______________________

{o['name']}
County Auditor and Commissioner of Elections, {c} County
{o['street']}
{o['city']}, IA {o['zip']}

Re: November 3, 2026 general election — request under Iowa Code chapter 22 for existing election records, and request regarding post-election audit coverage, {c} County

Dear County Auditor {o['name']}:

I am writing as a member of the public concerning election records and the post-election audit for the November 3, 2026 general election in {c} County, where you serve as county commissioner of elections under Iowa Code § 47.2(1). Using Iowa Secretary of State figures for the governor race, I compared the 2022 and 2026 general elections in {c} County:

- Registered Democrats (active and inactive), Nov. 1, 2022 to Nov. 1, 2026: {ch(a.demreg22,a.demreg26)}
- Democratic votes for governor, 2022 to 2026: {ch(a.D22,a.D26,'*')}
- Total ballots cast, 2022 to 2026: {ch(a.ballots22,a.ballots26,'*')}

2022 votes are from the Secretary of State's official 2022 State Canvass summary, and 2022 ballots are from the Secretary of State's 2022 general election turnout report. *2026 figures are the Secretary of State's unofficial election-night results (results site version 387276, last updated Nov. 19, 2026, 11:01:36 AM CST) and are not final until the State Board of Canvassers completes the state canvass.{cert} Registration counts are the Secretary of State's county registration reports as of November 1 of each year and include active and inactive voters. These are votes for the Democratic candidate, not a count of registered Democrats who voted; that would require the voter-history file.

{pat} {SW} I offer these figures as an observation and a hypothesis, not an allegation. Candidate choice, turnout, and voters crossing party lines can all move them, and county totals alone cannot tell those causes apart. Records that show how ballots were counted, precinct by precinct and batch by batch, are the records that could.

**Federal litigation context.** Executive Order 14248 (Mar. 25, 2025) was challenged in *California v. Trump*, No. 1:25-cv-10810 (D. Mass.) (summary-judgment order June 24, 2026; judgment and permanent injunction July 13, 2026), and *LULAC v. Executive Office of the President*, No. 1:25-cv-0946 (D.D.C.) (permanent injunction as to Section 2(a), Oct. 31, 2025). This letter does not assert that Iowa was a plaintiff in either case, and it does not rely on that litigation for standing or for any new right to records. I mention it only as context: county records requests and the county's statutory duties stand independently, however the litigation resolves.

**Records request.** Under Iowa Code chapter 22 ("public records" includes "all records, documents, tape, or other information, stored or preserved in any medium, of or belonging to this state or any county," § 22.1(3)(a), and "[e]very person shall have the right to examine and copy a public record," § 22.2(1)), and in light of the preservation requirements of Iowa Code § 50.19(2) and 52 U.S.C. § 20701, I request copies of the following existing records for the November 3, 2026 general election:

- **Cast vote record or results export, if one exists:** The Secretary of State's "Election Security in Iowa" page states that "[i]n Iowa, a Cast Vote Record is not generated in the course of conducting an election." If the county's tabulation system nonetheless created or stores a cast vote record, ballot-image file, or electronic results file for this election, I request a copy in electronic form, including batch or precinct identifiers and all contests, with any information that could identify a voter removed. If no such record exists, please say so. Verified Voting lists the county's election-day tabulator as {e['election_day_tabulator_equipment_2026']}; please tell me if that has changed.
- **Canvass summary report:** the election canvass summary report certified by the board of supervisors under § 50.24(3), which includes the results, overvotes, and undervotes by precinct for each contest.
- **Printed results:** copies of the printed results of the voting equipment returned to the commissioner on election night under § 50.14.
- **Equipment test records:** the signed statement attesting to the pre-election test of the automatic tabulating equipment and the certificate signed by those present for the test, under § 52.35(2) and (4).
- **Post-election audit records:** if {c} County was selected for the post-election audit under § 50.51, the audit report provided to the county board of supervisors and transmitted to the state commissioner under § 50.51(3)(b), and the record of which precincts were selected.
- **Hash verification:** the hash values for the certified voting system version the county used, and any record of hash verification performed on that system, so they can be compared with the trusted build published for the certified version. If no such record exists, please say so.

**Preservation.** I respectfully ask that the county keep the paper ballots (§ 50.12), the memory devices and printed results (§ 50.14), the test ballots and counting programs (§ 52.35(3)), the precinct election registers and absentee ballot records (§ 50.19(2)), any post-election audit records (§ 50.51), and any cast vote records or ballot images that exist for this election for the full twenty-two-month period under § 50.19(2) and 52 U.S.C. § 20701.

**Audit coverage (a request, not a records demand).** Under § 50.51(2), the state commissioner of elections determines the number of counties and precincts to be audited and selects the precincts by lot, and under § 50.12 "[t]he sealed packages containing voted ballots shall be opened only for an official recount authorized by section 50.48, 50.49, or 50.50, for an election contest held pursuant to chapters 57 through 62, to conduct an audit pursuant to section 50.51, or to destroy the ballots pursuant to section 50.19." I am therefore not asking the county to open ballots outside those purposes, and I am not asking to inspect ballots myself. I ask instead that the county consider asking the Secretary of State, as state commissioner of elections, to extend post-election audit coverage in {c} County to precincts representing at least thirty to forty percent of the county's total ballots, prioritizing the precincts with the highest ballot volume, so the sample reflects where most voters actually cast ballots. This is a request, not a claim of statutory entitlement. If the county concludes it has no basis to make such a request, I ask that it say so in writing.

This request is limited to records that already exist. If any record is withheld in whole or in part, I ask that you tell me in writing which provision of law you rely on, whether the record exists, and release any portion that can reasonably be separated. If a record is held by another office or by a vendor, please tell me where; § 22.2(2) provides that "[a] government body shall not prevent the examination or copying of a public record by contracting with a nongovernment body to perform any of its duties or functions." I will pay reasonable expenses under § 22.3; please tell me the estimated cost before proceeding.

Please confirm the addressee and mailing address if your office's information has changed since the Secretary of State's County Auditor List was retrieved on November 24, 2026.

Thank you for your time and for the work your office does to conduct elections.

Signature: _______________________________________________

Printed name: _______________________________________________

Address: _______________________________________________

Phone / email: _______________________________________________
"""
    fn=f"{c.replace(' ','_').replace(chr(39),'')}_County_Auditor_Letter"
    open(OUT+fn+'.md','w').write(md)
    rows.append(dict(county=c,file=fn,district=CD[c],auditor=o['name'],street=o['street'],city=o['city'],zip=o['zip'],population=int(a.population),
        demreg22=int(a.demreg22),demreg26=int(a.demreg26),D22=int(a.D22),D26=int(a.D26),ballots22=int(a.ballots22),ballots26=int(a.ballots26),
        certified_2026=bool(a.certified_2026),ed_equipment=e['election_day_tabulator_equipment_2026']))
pd.DataFrame(rows).to_csv(B+'auditor_letter_merge_fields.csv',index=False)
print(len(rows), SW)
