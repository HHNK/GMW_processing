# filename: combine_results_ArtDiver_and_GTA
# author: Bart Kropf
# Python: 3.6.13
# use:  combines 
#           - gta result in BROLab format
#           - ArtDiver result in BROLab format
#       based on 
#           - unique identifier Putnaam_nr (Putnaam_filternummer)
# 
 
# %%
# import modules
from cmath import nan
import os
import pandas as pd

# %%
# read inputs
df_AD = pd.read_excel('../output/ArtDiver_result.xlsx', engine="openpyxl")
df_GTA = pd.read_excel('../output/GTA_result.xlsx', engine="openpyxl")

# %%
# append dataframes
df_GTA['Startdatum'] = df_GTA['Inrichtingsdatum'] # prepare Startdatum
df = df_GTA.append(df_AD, ignore_index=True)

# sort by Putnaam and Startdatum
df = df.sort_values(by=['Putnaam_nr', 'Startdatum'], ascending=[True, True])

# %%

# drop empty columns
df.dropna(how='all', axis=1, inplace=True)

# %%
# write combined result
df.to_excel('../output/GTA_ArtDiver_combined_result.xlsx', index=False) 

# TODO: higlight rows in excel to improve readability? maybe try this method with openpyxl: https://stackoverflow.com/questions/63010527/how-to-highlight-rows-based-on-content-in-excel-dataframe

# %%
