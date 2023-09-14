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
    Missing adult female lice counts are interpolated from existing ones, as long
    as the gaps are only 1 or 2 consecutive weeks. Otherwise, missing lice
    counts are assumed to be zero.

    It is assumed that the input dataframe has columns named "Fastsittende lus",
    "Lus i bevegelige stadier", "Voksne hunnlus", "Lokalitetsnummer", "Uke", "År".

    The output dataframe has the same columns as the input dataframe, in addition
    to an extra column "Rådata mangler" which indicates whether the adult female lice counts
    were missing from the raw data.

    :param df: Input dataframe
    :return: New dataframe
    """

    adf_col = "Voksne hunnlus"
    col_order = list(df.columns)

    # Find date range
    yw_min, yw_max = df[["År", "Uke"]].sort_values(["År", "Uke"]).iloc[[0, -1], :].values
    date_min = datetime.datetime.strptime(f'{yw_min[0]}-{yw_min[1]}-1', '%G-%V-%u')
    date_max = datetime.datetime.strptime(f'{yw_max[0]}-{yw_max[1]}-1', '%G-%V-%u')
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
    df["Rådata mangler"] = np.isnan(df[adf_col].values)

    # Fill inn missing data
    chunks = []
    for loknr, group in df.groupby("Lokalitetsnummer"):
        # Interpolate adult female lice values
        chunk = group.copy()
        chunk[adf_col] = group[adf_col].interpolate()

        # Remove interpolation if three or more consecutive missing values
        missing = group["Rådata mangler"].values
        remove_interpolated = missing & (consecutive(missing) >= 3)
        chunk.loc[remove_interpolated, adf_col] = np.nan

        chunks.append(chunk)

    df = pd.concat(chunks)
    return df.reset_index().loc[:, col_order + ["Rådata mangler"]]


def consecutive(v):
    """
    Count the number of consecutive equal elements in the input array

    Example: consecutive([5, 5, 5, 1, 1, 3, 3, 1, 1, 1, 1]) returns
    [3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4]

    :param v: Input array of bools
    :return: An array of counts, of the same size as the input array
    """
    v = np.asarray(v)
    if len(v) == 0:
        return np.zeros((0, ), dtype=np.int64)

    breaks = v[:-1] != v[1:]
    group_num = np.concatenate([[0], np.cumsum(breaks)])
    _, unq_cnt = np.unique(group_num, return_counts=True)
    return np.repeat(unq_cnt, unq_cnt)


def cleanup_temp():
    pass


def cleanup_numfish():
    pass


def merge_lice_fish():
    pass


def compute_nauplii():
    pass
