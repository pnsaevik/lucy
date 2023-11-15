"""
Functions for interacting with the NorKyst ocean model
"""


import xarray as xr
import typing
import re
import numpy as np


OptionalDataset = typing.Union[xr.Dataset, None]


class NorKyst:
    def __init__(self):
        """
        An ocean model archive, created using the NorKyst system
        """


class NorKystDataset:
    def __init__(
            self, fname: str, dset: OptionalDataset = None
    ):
        """
        An ocean model dataset, created using the NorRoms system

        :param fname: File name of the dataset, must be formatted according to
        `meth:`lucy.norkyst.NorRomsDataset.file_name_pattern`.
        :param dset: If supplied, overrides the given file as the data source
        """
        self._fname = fname
        self._dset = dset
        self._dset_empty_at_init = (dset is None)
        self._start_date = None
        self._stop_date = None

    def close(self):
        """
        Closes the underlying data source
        """
        self._dset.close()

    def __enter__(self):
        if self._dset_empty_at_init:
            self._dset = xr.open_dataset(self._fname)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _getdates(self):
        # Try first his-pattern
        pat_his = re.compile(r'^.*(?P<start>\d{10})-(?P<stop>\d{10})$')
        m = pat_his.match(self._fname)
        if m:
            a = m.group('start')
            datestr = a[0:4] + '-' + a[4:6] + '-' + a[6:8] + 'T' + a[8:10]
            self._start_date = np.datetime64(datestr)
            a = m.group('stop')
            datestr = a[0:4] + '-' + a[4:6] + '-' + a[6:8] + 'T' + a[8:10]
            self._stop_date = np.datetime64(datestr)
            return

        # Next, try avg-pattern
        pat_avg = re.compile(r'^.*_(?P<date>\d{8})12$')
        m = pat_avg.match(self._fname)
        if m:
            a = m.group('date')
            datestr = a[0:4] + '-' + a[4:6] + '-' + a[6:8] + 'T12'
            self._start_date = np.datetime64(datestr)
            self._stop_date = self._start_date
            return

        # If all fails, raise error
        raise ValueError('Unknown date format in file name: ' + self._fname)

    @property
    def start_date(self):
        """
        Returns the start date (interpreted from file name)

        :return: A numpy datetime
        """
        if self._start_date is None:
            self._getdates()

        return self._start_date

    @property
    def stop_date(self):
        """
        Returns the stop date (interpreted from file name)

        :return: A numpy datetime
        """
        if self._stop_date is None:
            self._getdates()

        return self._stop_date
