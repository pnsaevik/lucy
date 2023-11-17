import pytest
from lucy import norkyst
import numpy as np
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent.joinpath('fixtures')
NORKYST_GLOB = str(FIXTURES_DIR / 'norfjords_160m_his.nc4_20150907*')


class Test_NorKystDataset_start_date:
    def test_can_interpret_his_file_name(self):
        fname = "my_norkyst.nc4_2021020304-2025060708"
        nrdset = norkyst.NorKystDataset(fname)
        assert nrdset.start_date == np.datetime64('2021-02-03 04:00')

    def test_can_interpret_avg_file_name(self):
        fname = "my_norkyst.nc4_2021020312"
        nrdset = norkyst.NorKystDataset(fname)
        assert nrdset.start_date == np.datetime64('2021-02-03 12:00')


class Test_NorKystDataset_stop_date:
    def test_can_interpret_his_file_name(self):
        fname = "my_norkyst.nc4_2021020304-2025060708"
        nrdset = norkyst.NorKystDataset(fname)
        assert nrdset.stop_date == np.datetime64('2025-06-07 08:00')

    def test_can_interpret_avg_file_name(self):
        fname = "my_norkyst.nc4_2021020312"
        nrdset = norkyst.NorKystDataset(fname)
        assert nrdset.stop_date == np.datetime64('2021-02-03 12:00')


class Test_NorKystDataseries_select_time:
    def test_raises_error_if_outside_range(self):
        fnames = ["my_norkyst.nc4_2021020304-2025060708"]
        ds = norkyst.NorKystDataseries.from_filenames(fnames)
        with pytest.raises(ValueError):
            ds.select_time("2019-01-01")
        with pytest.raises(ValueError):
            ds.select_time("2026-01-01")

    def test_returns_correct_internal_dataset(self):
        fnames = [
            "my_norkyst.nc4_2021020301-2021020400",
            "my_norkyst.nc4_2021020401-2021020500",
        ]
        ds = norkyst.NorKystDataseries.from_filenames(fnames)
        lower, upper = ds.select_time('2021-02-03 02:00')
        assert lower is upper
        assert lower.fname == fnames[0]

    def test_returns_correct_between_dataset(self):
        fnames = [
            "my_norkyst.nc4_2021020301-2021020400",
            "my_norkyst.nc4_2021020401-2021020500",
        ]
        ds = norkyst.NorKystDataseries.from_filenames(fnames)
        lower, upper = ds.select_time('2021-02-04 00:30')
        assert lower.fname == fnames[0]
        assert upper.fname == fnames[1]

    def test_returns_correct_lower_edge_dataset(self):
        fnames = [
            "my_norkyst.nc4_2021020301-2021020400",
            "my_norkyst.nc4_2021020401-2021020500",
        ]
        ds = norkyst.NorKystDataseries.from_filenames(fnames)
        lower, upper = ds.select_time('2021-02-03 01:00')
        assert lower.fname == fnames[0]
        assert upper.fname == fnames[0]
        assert lower is upper

    def test_returns_correct_upper_edge_dataset(self):
        fnames = [
            "my_norkyst.nc4_2021020301-2021020400",
            "my_norkyst.nc4_2021020401-2021020500",
        ]
        ds = norkyst.NorKystDataseries.from_filenames(fnames)
        lower, upper = ds.select_time('2021-02-04 00:00')
        assert lower.fname == fnames[0]
        assert upper.fname == fnames[0]
        assert lower is upper


class Test_NorKystDataseries_profile:
    def test_returns_xarray_dataset(self):
        ds = norkyst.NorKystDataseries.from_pattern(NORKYST_GLOB)
        result = ds.profile(
            start='2015-09-07T03',
            stop='2015-09-07T06',
            lon=5.27266,
            lat=60.46511,
            az=0,
        )
        assert set(result.data_vars) == {'u', 'v', 'dens', 'salt', 'temp'}
        assert result.temp.dims == ('time', 'depth')
        assert result.temp.shape == (4, 35)
