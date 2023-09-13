"""
Functions for computing the number of lice released from farms
"""


import pandas as pd
import numpy as np
import datetime


def fill_missing_lice(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill in missing lice counts

    This function reindexes the input dataframe so that there is one entry for
    each week and farm. Missing combinations of farms and weeks are added as new rows.
    Missing lice counts are interpolated from existing ones, as long
    as the gaps are only 1 or 2 consecutive weeks. Otherwise, missing lice
    counts are assumed to be zero. Also, the data are extrapolated by two weeks.

    It is assumed that the input dataframe has columns named "Fastsittende lus",
    "Lus i bevegelige stadier", "Voksne hunnlus", "Lokalitetsnummer", "Uke", "År".

    :param df: Input dataframe
    :return: New dataframe
    """

    col_order = list(df.columns)

    # Find date range
    yw_min, yw_max = df[["År", "Uke"]].sort_values(["År", "Uke"]).iloc[[0, -1], :].values
    date_min = datetime.datetime.strptime(f'{yw_min[0]}-{yw_min[1]}-1', '%G-%V-%u')
    date_max = datetime.datetime.strptime(f'{yw_max[0]}-{yw_max[1]}-1', '%G-%V-%u')
    date_max = date_max + datetime.timedelta(days=14)  # Extrapolate two weeks
    date_range = pd.date_range(date_min, date_max, freq='7D')

    # Create new index
    farms = df[["Lokalitetsnummer"]].drop_duplicates()
    new_index = pd.merge(right=date_range.isocalendar(), left=farms, how='cross')
    new_index = new_index.rename(columns={'year': 'År', 'week': 'Uke'})
    new_index = new_index.set_index(["Lokalitetsnummer", "År", "Uke"]).index

    # Apply new index (i.e., add missing columns)
    df = df.set_index(["Lokalitetsnummer", "År", "Uke"])
    df = df.reindex(new_index)

    # Add column indicating that lice values are interpolated
    df["Interpolert"] = np.isnan(df["Voksne hunnlus"].values)

    # Fill inn missing data
    chunks = []
    interp_col = "Voksne hunnlus"
    for loknr, group in df.groupby("Lokalitetsnummer"):
        chunk = group.copy()
        chunk["Voksne hunnlus"] = group["Voksne hunnlus"].interpolate(limit=2)
        chunks.append(chunk)

    df = pd.concat(chunks)
    return df.reset_index().loc[:, col_order + ['Interpolert']]


def cleanup_temp():
    pass


def cleanup_numfish():
    pass


def merge_lice_fish():
    pass


def compute_nauplii():
    pass
