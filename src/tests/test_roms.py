import netCDF4 as nc

from lucy.norkyst import roms, roms2nc4int2
import numpy as np
from pathlib import Path
import xarray as xr
import pytest
import re


FIXTURES_DIR = Path(__file__).parent.joinpath('fixtures')
FORCING_1 = str(FIXTURES_DIR / 'norfjords_160m_his.nc4_2015090701-2015090704')
FORCING_glob = str(FIXTURES_DIR / 'norfjords_160m_his.nc4_20150907*')


@pytest.fixture(scope='module')
def dset1():
    with xr.open_dataset(FORCING_1) as dset:
        yield dset


class Test_select_xy:
    def test_returns_single_point(self, dset1):
        ds = roms.select_xy(dset1, x=2, y=3)
        assert ds.temp.dims == ('ocean_time', 's_rho')

    def test_returns_correct_values(self, dset1):
        ds = roms.select_xy(dset1, x=2, y=3)
        assert 10.608 < float(ds.temp[0, 0]) < 10.610
        assert 0.018 < float(ds.u[0, 0]) < 0.020
        assert -0.044 < float(ds.v[0, 0]) < -0.042


class Test_compute_azimuthal_vel:
    def test_returns_correct_values(self):
        angle_xi = np.pi/3
        angle_vel = np.array(
            [0, np.pi/2, np.pi, 3*np.pi/2, 2*np.pi/6, 5*np.pi/6, 8*np.pi/6, 11*np.pi/6]
        )

        dset = xr.Dataset(
            data_vars=dict(
                u=xr.Variable('t', [30] * 8),
                v=xr.Variable('t', [40] * 8),
                angle=xr.Variable('t', [angle_xi] * 8, attrs={
                    'units': 'radians', 'long_name': 'angle between XI axis and EAST'
                }),
            )
        )
        vel = roms.compute_azimuthal_vel(dset, az=angle_vel)
        assert vel.values.round().astype('i4').tolist() == [46, 20, -46, -20, 40, -30, -40, 30]


class Test_open_location:
    def test_correct_profile_data(self):
        dset = roms.load_location(FORCING_glob, lat=59.03, lon=5.68, az=0)
        varnames = ['time', 'depth', 'u', 'v', 'salt', 'temp', 'dens']
        try:
            df = dset[varnames].to_dataframe()

        finally:
            dset.close()

        df = df.reset_index()
        df = df[varnames]
        txt = df.to_csv(index=False, float_format="%.02f", lineterminator='\n')

        fname = FIXTURES_DIR / 'profile.csv'
        with open(fname, encoding='utf-8') as fp:
            expected = fp.read()

        assert txt == expected


class Test_romsconv:
    @pytest.fixture(scope='function')
    def dset_in(self):
        with nc.Dataset(filename='dset_in.nc', mode='w', diskless=True) as dset_in:
            yield dset_in

    @pytest.fixture(scope='function')
    def dset_out(self):
        with nc.Dataset(filename='dset_out.nc', mode='w', diskless=True) as dset_out:
            yield dset_out

    def test_preserves_global_attributes(self, dset_in, dset_out):
        dset_in.setncattr(name="myatt", value="myval")
        roms2nc4int2.process(dset_in, dset_out, protocol=[])
        assert dset_out.getncattr('myatt') == "myval"

    def test_appends_extra_attributes(self, dset_in, dset_out):
        roms2nc4int2.process(dset_in, dset_out, protocol=[])
        assert "institution" in dset_out.ncattrs()
        assert "history" in dset_out.ncattrs()

    def test_appends_history(self, dset_in, dset_out):
        dset_in.setncattr(name="history", value="Created by ROMS")
        roms2nc4int2.process(dset_in, dset_out, protocol=[])

        history_masked = re.sub(pattern="[0-9]", repl="0", string=dset_out.history)
        assert history_masked == (
            'Created by ROMS\n'
            '0000-00-00T00:00:00 - roms0nc0int0.py test_roms.py::Test_romsconv'
        )

    def test_drops_variables_which_are_not_in_protocol(self, dset_in, dset_out):
        dset_in.createVariable(varname='myvar', datatype='i2')[:] = 0
        roms2nc4int2.process(dset_in, dset_out, protocol=[])
        assert "myvar" not in dset_out.variables

    def test_keeps_variables_that_are_in_protocol(self, dset_in, dset_out):
        protocol = [dict(varname='myvar')]
        dset_in.createVariable(varname='myvar', datatype='i2')[:] = 0
        roms2nc4int2.process(dset_in, dset_out, protocol)
        assert "myvar" in dset_out.variables

    def test_copies_variable_attributes(self, dset_in, dset_out):
        protocol = [dict(varname='myvar')]
        v = dset_in.createVariable(varname='myvar', datatype='i2')
        v.setncattr('myattr', 'myval')
        roms2nc4int2.process(dset_in, dset_out, protocol)
        assert dset_out.variables['myvar'].getncattr('myattr') == 'myval'
