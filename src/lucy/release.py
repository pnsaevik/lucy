"""
Functions for creating release files and similar resources for
particle tracking simulations
"""
import numpy as np
import pandas as pd


def create_licebiomass(df_biomass, df_lice):
    """
    Create LiceBiomass file format

    :return: A string with the file contents
    """

    df_biomass = df_biomass.rename(columns=dict(siteNr='farmid'))
    df_biomass = df_biomass.query('specieCode == "071101"')
    df_biomass['weight'] = df_biomass['avgWeight'] * df_biomass['numFish']
    date = df_biomass['endTime'].values
    date = date.astype('datetime64[s]') + np.timedelta64(2, 'h')  # To account for summertime
    df_biomass['date'] = date.astype('datetime64[D]').astype(str)

    df_lice['date'] = df_lice['date'].values.astype('datetime64[D]').astype(str)

    out_txt = ""
    df = pd.concat([df_biomass, df_lice])

    for farm_id, group in df.groupby('farmid'):
        lat = np.max(np.nan_to_num(group.Lat.values))
        lon = np.max(np.nan_to_num(group.Lon.values))
        out_txt += f'Fishfarm: {farm_id}  ({lat},{lon})\n'

        for i, row in group.sort_values('date').iterrows():
            datestr = row.date.replace('-', ' ')
            out_txt += f'{datestr}  '

            if np.isnan(row.numFish):
                fish_count = 'null'
            else:
                fish_count = f'{row.numFish:.0f}'
            out_txt += f'{fish_count}  '

            if np.isnan(row.weight):
                weight = 'null'
            else:
                weight = f'{row.weight:.4f}'
            out_txt += f'{weight} - '

            if np.isnan(row.temp):
                temp = 'null'
            else:
                temp = f'{row.temp:.2f}'

            if np.isnan(row.nch):
                nch = 'null'
            else:
                nch = f'{row.nch:.2f}'

            if np.isnan(row.npa):
                nmo = 'null'
            else:
                nmo = f'{row.npa:.2f}'

            if np.isnan(row.naf):
                naf = 'null'
            else:
                naf = f'{row.naf:.2f}'

            out_txt += f'{temp}  {nch} {nmo} {naf}\n'
        pass
    return out_txt
