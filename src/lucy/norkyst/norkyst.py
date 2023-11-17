"""
Functions for interacting with the NorKyst ocean model
"""
import contextlib
from . import numerics
import xarray as xr
import typing
import re
import numpy as np


OptionalDataset = typing.Union[xr.Dataset, None]


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
        self._dset_init = dset
        self._start_date = None
        self._stop_date = None

    @property
    def fname(self):
        """
        File name of dataset
        """
        return self._fname

    @contextlib.contextmanager
    def open(self) -> xr.Dataset:
        """
        Open the underlying data source
        """
        if self._dset_init is not None:
            yield self._dset_init

        else:
            dset = xr.open_dataset(self._fname)
            try:
                yield dset
            finally:
                dset.close()

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


class NorKystDataseries:
    def __init__(self, dsets: typing.Iterable[NorKystDataset]):
        """
        An ocean model archive, created using the NorKyst system

        :param dsets: An iterable of datasets in the database
        """
        self._dsets = list(dsets)
        self._grid_dset = self._dsets[0]
        self._time_index = None

    @staticmethod
    def from_pattern(pattern: str):
        """
        Initialize a database object from file name pattern. It is
        assumed that the files are ordered by time if they are sorted
        by alphabetic ordering of the file names.

        :param pattern: A file name glob pattern
        :return: An initialized database
        """
        import glob
        filenames = sorted(glob.glob(pattern))
        return NorKystDataseries.from_filenames(filenames)

    @staticmethod
    def from_filenames(filenames: typing.Iterable[str]):
        """
        Initialize a database object from file names. It is
        assumed that the files are ordered by time.

        :param filenames: File names
        :return: An initialized database
        """
        dsets = [NorKystDataset(fname) for fname in filenames]
        db = NorKystDataseries(dsets)
        return db

    def subset(self, start, stop) -> "NorKystDataseries":
        """
        Extract a subset of the data series

        :param start: numpy-compatible start date
        :param stop: numpy-compatible stop date
        :return: A subset of the data series
        """

        idx_start, _ = self._find_dataset_index_from_time(start)
        _, idx_stop = self._find_dataset_index_from_time(stop)

        ds_new = NorKystDataseries(self._dsets[idx_start:idx_stop])
        if self._time_index is not None:
            ds_new._time_index = self._time_index[idx_start:idx_stop]

        return ds_new

    @property
    def datasets(self) -> typing.List[NorKystDataset]:
        """
        The datasets that are contained in this data series
        """
        return self._dsets

    def _create_time_index(self):
        self._time_index = [(d.start_date, d.stop_date) for d in self._dsets]

    def select_time(self, time) -> (NorKystDataset, NorKystDataset):
        """
        Return the datasets corresponding to a specific time

        The function always returns a tuple of two datasets, the 'lower' and 'upper'
        dataset. If the given time is fully contained within a single dataset, this
        dataset is used as both 'lower' and 'upper' dataset. If the given time falls
        between two datasets, one will be the 'lower' and the other will be the 'upper'
        dataset.

        If the given time is outside the dataseries interval, an error is raised.

        :param time: A numpy-compatible datetime
        :return: A tuple (lower, upper) containing the datasets
        """

        dset_index_lower, dset_index_upper = self._find_dataset_index_from_time(time)

        lower = self._dsets[dset_index_lower]
        upper = self._dsets[dset_index_upper]
        return lower, upper

    def _find_dataset_index_from_time(self, time):
        nptime = np.datetime64(time)
        if (nptime < self._dsets[0].start_date) or (self._dsets[-1].stop_date < nptime):
            raise ValueError(f'Time value outside range: {nptime}')

        if self._time_index is None:
            self._create_time_index()

        start_times, stop_times = np.asarray(self._time_index).T
        dset_index_lower = np.searchsorted(start_times, nptime, side='right') - 1
        dset_index_upper = np.searchsorted(stop_times, nptime, side='left')
        return dset_index_lower, dset_index_upper

    def xy(self, lat, lon):
        """
        Find xy coordinates from latitude, longitude

        :param lat: Latitude coordinate
        :param lon: Longitude coordinate
        :return: A tuple (x, y) of internal coordinate values
        """

        with self._grid_dset.open() as dset:
            lat_rho = dset.lat_rho.values
            lon_rho = dset.lon_rho.values
        y, x = numerics.bilin_inv(lat, lon, lat_rho, lon_rho)
        return x, y


def extract_profile(files, start, stop, lat, lon, az) -> xr.Dataset:
    """
    Load profile data

    The function finds the grid point closest to the given lat/lon coordinates
    and extracts profile information from this grid point. The otuput dataset
    contains 'dens', 'salt', 'temp' at the grid point, and interpolated values
    for 'u', 'v'. Velocities at land points are set to zero.

    Velocities are rotated according to the given azimuthal orientation. The
    direction is given in clockwise degrees relative to north. That is, 0
    means north and 90 means east. Only the u direction is given, the v
    direction is always equal to the u direction minus 90 degrees.

    :param files: Either a list of files or a file name glob pattern
    :param start: numpy-compatible start date
    :param stop: numpy-compatible stop date
    :param lat: Latitude of profile position
    :param lon: Longitude of profile position
    :param az: Azimuthal orientation of u velocity (0 is north, 90 is east)
    :return: Profile data
    """

    if isinstance(files, str):
        ds = NorKystDataseries.from_pattern(files)
    else:
        ds = NorKystDataseries.from_filenames(files)

    ds_subset = ds.subset(start, stop)

    from .roms import load_location
    fnames = [d.fname for d in ds_subset.datasets]
    return load_location(fnames, lat, lon, az)
