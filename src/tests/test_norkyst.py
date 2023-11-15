from lucy import norkyst
import xarray as xr
import numpy as np


class Test_NorKystDataset_start_date:
    def test_can_interpret_his_file_name(self):
        dset = xr.Dataset()
        fname = "my_norkyst.nc4_2021020304-2025060708"
        nrdset = norkyst.NorKystDataset(fname, dset)
        assert nrdset.start_date == np.datetime64('2021-02-03 04:00')

    def test_can_interpret_avg_file_name(self):
        dset = xr.Dataset()
        fname = "my_norkyst.nc4_2021020312"
        nrdset = norkyst.NorKystDataset(fname, dset)
        assert nrdset.start_date == np.datetime64('2021-02-03 12:00')


class Test_NorKystDataset_stop_date:
    def test_can_interpret_his_file_name(self):
        dset = xr.Dataset()
        fname = "my_norkyst.nc4_2021020304-2025060708"
        nrdset = norkyst.NorKystDataset(fname, dset)
        assert nrdset.stop_date == np.datetime64('2025-06-07 08:00')

    def test_can_interpret_avg_file_name(self):
        dset = xr.Dataset()
        fname = "my_norkyst.nc4_2021020312"
        nrdset = norkyst.NorKystDataset(fname, dset)
        assert nrdset.stop_date == np.datetime64('2021-02-03 12:00')
