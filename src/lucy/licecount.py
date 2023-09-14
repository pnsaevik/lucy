"""
Functions for computing the number of lice released from farms
"""


import pandas as pd
import numpy as np
from . import schema


def fill_missing_lice(df: schema.Lice) -> schema.Lice:
    """
    Fill in missing lice counts

    This function reindexes the input dataframe so that there is one entry for
    each week and farm. Missing combinations of farms and weeks are added as new rows.
    Missing adult female lice counts are interpolated from existing ones, as long
    as the gaps less than 4 consecutive weeks. Otherwise, missing lice
    counts are assumed to be zero.

    The output dataframe has the same columns as the input dataframe, in addition
    to an extra column "missing" which indicates whether the adult female lice counts
    were missing from the raw data.

    :param df: Input dataframe
    :return: New dataframe
    """

    col_order = list(df.columns)

    # Find date range
    df = df.assign(date=pd.to_datetime(df.date))
    date_range = pd.date_range(df.date.min(), df.date.max(), freq='7D')
    date_df = pd.DataFrame(date_range, columns=['date'])

    # Create new index
    farms = df.farmid.drop_duplicates()
    new_index = pd.merge(right=date_df, left=farms, how='cross')
    new_index = new_index.set_index(["farmid", "date"]).index

    # Apply new index (i.e., add missing columns)
    df = df.set_index(["farmid", "date"])
    df = df.reindex(new_index)

    # Add column indicating which lice values are interpolated
    df["missing"] = np.isnan(df.naf.values)

    # Fill inn missing data
    chunks = []
    for farmid, group in df.groupby("farmid"):
        # Interpolate adult female lice values
        chunk = group.copy()
        chunk["naf"] = group.naf.interpolate()

        # Remove interpolation if many consecutive missing values
        missing = group.missing.values
        remove_interpolated = missing & (consecutive(missing) >= 4)
        chunk.loc[remove_interpolated, "naf"] = 0

        chunks.append(chunk)

    df = pd.concat(chunks)
    df = df.reset_index().loc[:, col_order + ["missing"]]
    df['date'] = df.date.values.astype('datetime64[D]').astype(str)
    return df


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
