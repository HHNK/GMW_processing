# filename: convert_ArtDiver_wells_to_BROLab
# author: Bart Kropf
# Python: 3.6.13
# use:  converts 
#           - ArtDiver export_wells.csv
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
# open ArtDiver export_wells
df_wells = pd.read_csv('../input/ArtDiver_export_wells.csv', sep=';')


# %%
# combine ArtDiver wells with BROLabs sheet
df = pd.concat([df_wells,df_puttenlijst])

# %%
# calculate BROLab fields
df['Positie bovenkantbuis (m+NAP)'] = df['MEETPUNT']
df['Filterlengte (meters)'] = df['BK_FILT'] - df['OK_FILT']
df['Putnaam'] = df['PUTCODE']
df['Filternummer'] = df['FILTNR'] 
df['Inrichtingsdatum'] =  pd.to_datetime(df["START"], format="%d-%m-%Y %H:%M:%S")
df['X-coordinaat(RD)'] = df['X']
df['Y-coordinaat(RD)'] = df['Y']
df['Maaiveldpositie (m+NAP)'] = df['MAAIVELD']
df['Lengte stijgbuisdeel (meters)'] = df['MEETPUNT'] - df['BK_FILT']
df["Startdatum"] = pd.to_datetime(df["START"], format="%d-%m-%Y %H:%M:%S")
df["Einddatum"] = pd.to_datetime(df["EIND"], format="%d-%m-%Y %H:%M:%S")


# %%
#update ArtDiver Putnaam (PUTCODE) and Filternummer with costum made d_pb_mapper.
# Putnaam must be equal to GTA Putnaam (BOREHOLEIDENT)
d_pb_mapper = {
    "PB_1_001_04P001442_F-2": ["PB_1_001_04P001442",3],
    "PB_1_001_04P001442_F-374": ["PB_1_001_04P001442",1],
    "PB_1_002_04P001442_F-2": ["PB_1_002_04P001442",3],
    "PB_1_002_04P001442_F-375": ["PB_1_002_04P001442",1],
    "PB_1_003_04P001442_F-2": ["PB_1_003_04P001442",3],
    "PB_1_003_04P001442_F-337": ["PB_1_003_04P001442",1],
    "PB_1_004_04P001442-01_F-204": ["PB_1_004_04P001442-01",1],
    "PB_1_004_04P001442-01_F-2": ["PB_1_004_04P001442-01",3],
    "PB_1_005_04P001442-01_F-2": ["PB_1_005_04P001442-01",3],
    "PB_1_005_04P001442-01_F-264": ["PB_1_005_04P001442-01",1],
    "PB_2_001_04P001442_F-209": ["PB_2_001_04P001442",1],
    "PB_2_001_04P001442_F-2": ["PB_2_001_04P001442",3],
    "PB_2_002_04P001442_F-2": ["PB_2_002_04P001442",3],
    "PB_2_002_04P001442_F-297": ["PB_2_002_04P001442",1],
    "PB_2_003_04P001442-01_F-206": ["PB_2_003_04P001442-01",1],
    "PB_2_003_04P001442-01_F-2": ["PB_2_003_04P001442-01",3],
    "PB_6_001_04P001442-01_F-875": ["PB_6_001_04P001442-01",2],
}

for key, value in d_pb_mapper.items():
    putnaam, filternummer = value
    df.loc[df['PUTCODE'] == key, "Filternummer"] = filternummer
    df.loc[df['PUTCODE'] == key, "Putnaam"] = putnaam

# combine Putnaam and Filternummer to unique identifier Putnaam_nr
df['Putnaam_nr'] = df['Putnaam'] + "_" + df['Filternummer'].apply(lambda x:int(x)).astype(str)

df = df.sort_values(by=['Putnaam', 'BK_FILT', 'Startdatum'], ascending=[True, False, True])

# %%
# write result to excel
additional_fields = ['Startdatum','Einddatum','PUTCODE','Putnaam_nr']
with pd.ExcelWriter(
    '../output/ArtDiver_result.xlsx',
    date_format="YYYY-MM-DD",
    datetime_format="YYYY-MM-DD"
) as writer:
    df.to_excel(writer,
        columns=list(df_puttenlijst.columns)+additional_fields, 
        index=False)



# %%
