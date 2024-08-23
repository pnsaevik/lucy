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

    # Include only salmonid species
    df2 = df_biomass.query('specieCode.str.startswith("071")').copy()

    # Add total weight, which is a summable quantity
    df2['weight'] = (df2['numFish'] * df2['avgWeight']).astype('int64')

    # Compute reference date
    period_month = df2['endTime'].str.slice(0, 7).values.astype('datetime64[M]')
    reference_month = period_month + np.timedelta64(1, 'M')
    df2['date'] = reference_month.astype('datetime64[D]').astype(str)

    # First aggregation: Sum over all cages in report
    df3 = df2.groupby([
        'siteNr', 'date', 'organization', 'mainOperator',
        'reportTime', 'reportReceipt'
    ])[['numFish', 'weight']].sum().reset_index()

    # If there are multiple reports, choose only the last one
    # At this point, the data frame is already sorted by reportTime
    df4 = df3.groupby([
        'siteNr', 'date', 'organization', 'mainOperator',
    ]).last().reset_index()

    # Second aggregation: Sum over all organizations in the same site
    df5 = df4.groupby(['siteNr', 'date'])[['numFish', 'weight']].sum().reset_index()

    # Remove all-null lines from lice dataset
    idx = np.isnan(df_lice['naf'].values)
    idx &= np.isnan(df_lice['temp'].values)
    df8 = df_lice.rename(columns={'farmid': 'siteNr'}).iloc[~idx].copy()

    # Append salmon lice dataset
    df9 = pd.concat([df5, df8])
    df9['datestr'] = df9['date'].values.astype('datetime64[D]').astype(str)

    # Sort by fish farm ID and date
    df6 = df9.sort_values(['siteNr', 'datestr'])

    # Prepare text file format
    df6['separator'] = '-'
    df6['avgWeight'] = np.round(df6['weight'].values / df6['numFish'].values, 4)
    df6['year'] = df6['datestr'].str.slice(0, 4)
    df6['month'] = df6['datestr'].str.slice(5, 7)
    df6['day'] = df6['datestr'].str.slice(8, 10)
    df7 = df6[[
        'siteNr', 'Lat', 'Lon', 'year', 'month', 'day', 'numFish',
        'avgWeight', 'separator', 'temp', 'nch', 'npa', 'naf',
    ]]

    # Write text file
    out_txt = ""
    for farm_id, group in df7.groupby('siteNr'):
        lat = np.max(np.nan_to_num(group.Lat.values))
        lon = np.max(np.nan_to_num(group.Lon.values))
        out_txt += f'Fishfarm: {farm_id}  ({lat},{lon})\n'
        out_txt += group.drop(
            columns=['siteNr', 'Lat', 'Lon'],
        ).to_csv(
            sep=' ',
            na_rep='null',
            lineterminator='\n',
            index=False,
            header=False,
        )
    return out_txt


def make_licebiomass(bw_user, bw_pass, fd_user, fd_pass, year, outfile):
    import lucy.data.barentswatch
    import lucy.data.fiskeridir

    print('Download lice data')
    lucy.data.barentswatch.create_token(bw_user, bw_pass)
    df_lice = lucy.data.barentswatch.lice(year)

    print('Download biomass data')
    df_biomass = lucy.data.fiskeridir.biomass(
        year=year, user=fd_user, passwd=fd_pass)

    print('Create licebiomass file')
    result_txt = create_licebiomass(df_biomass, df_lice)

    with open(outfile, 'w', newline='\n', encoding='utf-8') as fp:
        fp.write(result_txt)
