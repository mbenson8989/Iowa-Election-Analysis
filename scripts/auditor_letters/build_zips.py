import pandas as pd, zipfile, os
os.chdir('/workspace/iowa-auditor-letters')
M=pd.read_csv('auditor_letter_merge_fields.csv')
def readme(label,counties):
    return f"""Iowa county auditor letters (DRAFT, for review before mailing)
Drafted for Morissa Benson, adapted from the Kansas county clerk letters (which follow her Nebraska 93-county cast-vote-record request letter, in the same tone and structure as the Texas clerk letters), rewritten for Iowa law.
In Iowa, the county auditor of each county is the county commissioner of elections (Iowa Code § 47.2(1)). One letter per county, addressed to that county's auditor, in PDF and Word (.docx).
Addressees and mailing addresses: Iowa Secretary of State, County Auditor List, https://sos.iowa.gov/elections/auditors/auditorslist.html, retrieved November 24, 2026 (America/Chicago). All 99 counties had a name and mailing address on that list.
Grouping: Iowa's four U.S. House (congressional) districts, using the county lists in the Iowa Secretary of State's 2026 general election results (results site version 387276). Each county appears under exactly one district there. The Iowa Secretary of State does not divide the state into election regions for county administration; this grouping is only for convenience.
2026 figures in the letters are UNOFFICIAL (Iowa SOS election-night results, version 387276, last updated Nov. 19, 2026, 11:01:36 AM CST; the state canvass is not complete; Van Buren County had not certified when the data was pulled). 2022 figures are the SOS official State Canvass and turnout report. Registration is the SOS Nov. 1 county report for each year (active + inactive).
The figures are offered as an observation and a hypothesis, not an allegation and not proof of fraud.
Date, signature, and sender blocks are blank on purpose. Confirm each addressee before sending. Nothing has been sent.

{label} ({len(counties)} counties): {', '.join(counties)}
"""
def mk(name,label,sub):
    cs=sorted(sub.county)
    with zipfile.ZipFile(f'downloads/{name}.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr(f'{name}/README.txt',readme(label,cs))
        for fn in sorted(sub.file):
            z.write(f'out/PDF/{fn}.pdf',f'{name}/PDF/{fn}.pdf'); z.write(f'out/Word/{fn}.docx',f'{name}/Word/{fn}.docx')
    print(name,len(cs),round(os.path.getsize(f'downloads/{name}.zip')/1e6,1))
mk('Iowa_Auditor_Letters_All_99_Counties','Counties in this file',M)
for d in [1,2,3,4]:
    mk(f'Iowa_Auditor_Letters_Congressional_District_{d}',f'Congressional District {d} counties in this file',M[M.district==d])
L=M.sort_values('population',ascending=False)[['county','district','population']].copy()
L['ZIP_file']=L.district.map(lambda d:f'Iowa_Auditor_Letters_Congressional_District_{d}.zip')
L['district']=L.district.map(lambda d:f'Congressional District {d}')
L.columns=['County','Congressional_District','Population_2025','ZIP_file']
L.to_csv('downloads/Iowa_County_to_District_Lookup.csv',index=False)
