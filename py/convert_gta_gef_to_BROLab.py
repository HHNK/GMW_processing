# filename: convert_gta_gef_to_BROLab
# author: Bart Kropf
# Python: 3.6.13
# use:  combines 
#           - gta (manual) export of selected peilbuis with joined peilbuisput
#           - some additional gef attributes
#       into 
#           - BROLab import spreadsheet (result should be copy-pasted into original Puttenlijst)
# 
 
# %%
# import modules
from cmath import nan
from gef import GEF
import os, glob
import pandas as pd

# %%
# open BROLab sheet
df_puttenlijst = pd.read_excel('../input/BROLab_puttenlijst_v5_ori.xlsx', engine="openpyxl")
# drop rows
df_puttenlijst = df_puttenlijst.iloc[0:0]
# open GTA export sheet
df_export = pd.read_excel('../input/GTA_peilbuis_met_put_sel_HBPZ_all.xlsx', engine="openpyxl")

# %%
# combine export GTA with BROLabs sheet
df = pd.concat([df_export,df_puttenlijst])

# calculate BROLab fields
df['Positie bovenkantbuis (m+NAP)'] = df['GTA.GTA_PEILBUISGEGEVENS.BOVENKANT_PEILBUIS']
df['Zandvanglengte (meters)'] = df['GTA.GTA_PEILBUISGEGEVENS.LENGTE_ZANDVANG']
df['Filterlengte (meters)'] = df['GTA.GTA_PEILBUISGEGEVENS.LENGTE_FILTER']
df['Putnaam'] = df['GTA.GTA_PEILBUISPUT.BOREHOLEIDENT']
df['Inrichtingsdatum'] = df['GTA.GTA_PEILBUISPUT.DATUM_PLAATSING']
df['X-coordinaat(RD)'] = df['GTA.GTA_PEILBUISPUT.X_RD']
df['Y-coordinaat(RD)'] = df['GTA.GTA_PEILBUISPUT.Y_RD']
df['Maaiveldpositie (m+NAP)'] = df['GTA.GTA_PEILBUISPUT.MV_NAP']
df['Lengte stijgbuisdeel (meters)'] = df['GTA.GTA_PEILBUISGEGEVENS.LENGTE_PEILBUIS'] - df['GTA.GTA_PEILBUISGEGEVENS.LENGTE_FILTER']

# sort by Putnaam and bovenkant_filter
df = df.sort_values(by=['Putnaam', 'GTA.GTA_PEILBUISGEGEVENS.BOVENKANT_FILTER'], ascending=[True, False])
# %%
# calculate filternummer
i = 0
next_put = False
previous_Putnaam = ""
for index, row in df.iterrows():
    next_put = True if row['Putnaam'] != previous_Putnaam else False
    if not next_put:
        i += 1
    else:
        i = 1
    ## row['Filternummer'] = i   doesnt work, instead use df.loc[] for update
    df.loc[index,'Filternummer'] = i
    gefnaam = row['GTA.GTA_PEILBUISPUT.NAAM_PEILBUISPUTBESTAND'].split('.')[0]
    df.loc[index,'gefnaam_nr'] = "{}_{}".format(gefnaam,i)
    previous_Putnaam = row['Putnaam']

# %% 
# add additional info from GEF

df_gef = pd.DataFrame()
for filepath in glob.iglob('../input/GEF/*.gef'):
    
    gefnaam = os.path.basename(filepath).split(".")[0]
    print(gefnaam)

    gef = GEF()
    gef.read(filepath,None)

    
    for k in range(1,4): # for 3 filters max
        i = 26*k - 12   # lengte zandvang peilbuis #MEASUREMENTVAR = 26k-12
        j = 26*k - 9    # bovenkant filter         #MEASUREMENTVAR = 26k-9
        try:
            
            zandvanglengte, unit, description = gef.MEASURES.measurementsVar[i]
            print ("{} = {} in {}".format(description,zandvanglengte,unit))
            bov_f, unit, description = gef.MEASURES.measurementsVar[j]
            print ("{} = {} in {}".format(description,bov_f,unit))
            new_row = {
                "gefnaam": gefnaam,
                "Zandvanglengte (meters)": zandvanglengte,
                "bovenkant filter (gef)": float(bov_f),
                "peilbuis": description,
                }
            df_gef = df_gef.append(new_row, ignore_index=True)
        except KeyError:
            pass
        except Exception as e:
            print (e)
    
    # sort by Putnaam and bovenkant_filter
    df_gef = df_gef.sort_values(by=['gefnaam', 'bovenkant filter (gef)'], ascending=[True, True])

    # calculate filternummer
    i = 0
    next_put = False
    previous_Putnaam = ""
    for index, row in df_gef.iterrows():
        next_put = True if row['gefnaam'] != previous_Putnaam else False
        if not next_put:
            i += 1
        else:
            i = 1
        ## row['Filternummer'] = i   doesnt work, instead use df.loc[] for update
        df_gef.loc[index,'Filternummer (gef)'] = i
        df_gef.loc[index,'gefnaam_nr'] = "{}_{}".format(row['gefnaam'],i)
        previous_Putnaam = row['gefnaam']

# %%

df = pd.merge(df,df_gef, how="outer", left_on="gefnaam_nr", right_on="gefnaam_nr")


# %%
# calculate 'Zandvanglengte (meters)' en 'Voorzien van zandvang'
df['Zandvanglengte (meters)'] = df['Zandvanglengte (meters)_y']
df['Zandvanglengte (meters)'].fillna(0)
for index, row in df.iterrows():
    if float(row['Zandvanglengte (meters)']) > 0:
        value = "ja"
    else:
        value = "nee"
    print (value)
    df.loc[index,'Voorzien van zandvang'] = value

# %%
# add putnaam_nr
df['Putnaam_nr'] = df['Putnaam'] + "_" + df['Filternummer'].apply(lambda x:int(x)).astype(str)

# %%
# keep BROLab fields and additional fields
additional_fields = ['Putnaam_nr', 'gefnaam_nr', 'bovenkant filter (gef)', 'Filternummer (gef)', 'GTA.GTA_PEILBUISGEGEVENS.PEILBUISIDENT']
df.to_excel('../output/GTA_result.xlsx', columns=list(df_puttenlijst.columns)+additional_fields)


# # %%
# columns=list(df_puttenlijst.columns)+additional_fields
# # %%
# for column in columns:
#     if column not in df.columns:
#         print (column)
# # %%
