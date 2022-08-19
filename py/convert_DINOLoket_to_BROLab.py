# filename: convert_DINOLoket_to_BROLab
# author: Bart Kropf
# Python: 3.6.13
# use:  converts 
#           - Dinoloket export files
#       into 
#           - BROLab import spreadsheet (result should be copy-pasted into original Puttenlijst)
# 
 
# %%
# import modules
from cmath import nan
import os, glob
import pandas as pd

# %%
# open BROLab sheet
df_puttenlijst = pd.read_excel('../input/BROLab_puttenlijst_v5_ori.xlsx', engine="openpyxl")
# drop rows
df_puttenlijst = df_puttenlijst.iloc[0:0]

# %%
# open Dinoloket exports
l_df = []
for filepath in glob.iglob('../input/download_van_dino_loket/Grondwaterstanden_Put/*_1.csv'):
    putnaam = os.path.basename(filepath).split("_1.csv")[0]
    print(putnaam)
    rows_to_keep = range(11,14)
    df_export = pd.read_csv(filepath, skiprows = lambda x: x not in rows_to_keep)
    l_df.append(df_export)


# %%
# combine list of DinoLoket fd's to BROLabs sheet
df = pd.concat(l_df)
df = pd.concat([df,df_puttenlijst])

# %%
df = df.sort_values(by=['Locatie', 'Bovenkant filter (cm t.o.v. NAP)', 'Startdatum'], ascending=[True, False, True])



# %%
# calculate BROLab fields
df['Positie bovenkantbuis (m+NAP)'] = df['Meetpunt (cm t.o.v. NAP)'] / 100
df['Filterlengte (meters)'] = (df['Bovenkant filter (cm t.o.v. NAP)'] - df['Onderkant filter (cm t.o.v. NAP)']) / 100 
df['Putnaam'] = df['Locatie']
df['Inrichtingsdatum'] = df['Startdatum']
df['X-coordinaat(RD)'] = df['X-coordinaat']
df['Y-coordinaat(RD)'] = df['Y-coordinaat']
df['Maaiveldpositie (m+NAP)'] = df['Maaiveld (cm t.o.v. NAP)'] / 100
df['Lengte stijgbuisdeel (meters)'] = (df['Meetpunt (cm t.o.v. NAP)'] - df['Bovenkant filter (cm t.o.v. NAP)']) / 100

# %%
with pd.ExcelWriter(
    '../output/Dino_result.xlsx',
    date_format="YYYY-MM-DD", 
    datetime_format="YYYY-MM-DD"
) as writer:
    df.to_excel(writer,
        columns=list(df_puttenlijst.columns)+['Startdatum','Einddatum'], 
        index=False)

