"""
Descriptions of data formats used to communicate between tools in the package
"""


import pandas as pd


class Lice(pd.DataFrame):
    """
    A table of lice count data, with standardized column names.

    .. list-table::
        :header-rows: 1

        *   - Column
            - Type
            - Description
        *   - id
            - int
            - Index column
        *   - loknr
            - int
            - Fish farm identifier
        *   - date
            - str
            - Date of lice count, in ISO format. If the count date is
              uncertain, but the week is known, this field refers to
              Monday within the specified week.
        *   - temp
            - float
            - Temperature, in degrees Celcius
        *   - nch
            - float
            - Stationary lice per fish
        *   - npa
            - float
            - Mobile lice per fish
        *   - naf
            - float
            - Adult female lice per fish
        *   - missing
            - bool
            - True if lice data were missing from original dataset
    """
    def __init__(self):
        super().__init__()
