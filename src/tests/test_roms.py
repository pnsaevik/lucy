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
        for varname in ['depth', 'u', 'v', 'salt', 'temp', 'dens']:
            df[varname] = df[varname].values.astype('f8').round(2)
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

    @pytest.fixture(scope='function')
    def dset_grid(self):
        with nc.Dataset(filename='dset_grid.nc', mode='w', diskless=True) as dset_grid:

            dset_grid.createDimension(dimname='x', size=2)
            dset_grid.createDimension(dimname='y', size=3)

            dset_grid.createVariable(varname='crs', datatype='i1', dimensions=())
            dset_grid.createVariable(varname='x', datatype='i1', dimensions='x')
            dset_grid.createVariable(varname='y', datatype='i1', dimensions='y')

            dset_grid.variables['crs'].grid_mapping_name = 'polar_stereographic'
            dset_grid.variables['x'].standard_name = 'projection_x_coordinate'
            dset_grid.variables['y'].standard_name = 'projection_y_coordinate'

            yield dset_grid

    def test_dataset_attributes_are_copied_verbatim(self, dset_in, dset_out):
        dset_in.setncattr(name="myatt", value="myval")
        roms2nc4int2.run(dset_in, dset_out, protocol=[])
        assert dset_out.getncattr('myatt') == "myval"

    def test_history_attribute_is_appended_to(self, dset_in, dset_out):
        dset_in.setncattr(name="history", value="Created by ROMS")
        roms2nc4int2.run(dset_in, dset_out, protocol=[])

        history_masked = re.sub(pattern="[0-9]", repl="0", string=dset_out.history)
        assert history_masked.startswith(
            'Created by ROMS\n'
            '0000-00-00T00:00:00 - roms0nc0int0.py'
        )

    def test_institution_attribute_is_added(self, dset_in, dset_out):
        roms2nc4int2.run(dset_in, dset_out, protocol=[])
        assert "institution" in dset_out.ncattrs()
        assert "history" in dset_out.ncattrs()

    def test_drops_variables_which_are_not_in_protocol(self, dset_in, dset_out):
        dset_in.createVariable(varname='myvar', datatype='i2')[:] = 0
        roms2nc4int2.run(dset_in, dset_out, protocol=[])
        assert "myvar" not in dset_out.variables

    def test_keeps_variables_that_are_in_protocol(self, dset_in, dset_out):
        key = 'varname'  # type: roms2nc4int2.ProtocolKeyword
        dset_in.createVariable(varname='myvar', datatype='i2')[:] = 0
        roms2nc4int2.run(dset_in, dset_out, protocol=[{key: 'myvar'}])
        assert "myvar" in dset_out.variables

    def test_variable_data_are_scaled_and_offsetted(self, dset_in, dset_out):
        protocol = [dict(varname='v', scale=0.5, offset=-1, dtype='f4')]

        dset_in.createDimension(dimname='d', size=5)
        dset_in.createVariable(varname='v', datatype='f4', dimensions='d')
        dset_in.variables['v'][:] = [.5, 1, 1.5, 2, 2.5]

        roms2nc4int2.run(dset_in, dset_out, protocol=protocol)  # type: ignore

        assert dset_out.variables['v'][:].tolist() == [3, 4, 5, 6, 7]
        assert dset_out.variables['v'].getncattr('scale_factor') == 0.5
        assert dset_out.variables['v'].getncattr('add_offset') == -1

    def test_nan_values_in_velocity_variables_are_set_to_zero(self, dset_in, dset_out):
        protocol = [
            dict(varname='u', dtype='i2'),
            dict(varname='v', dtype='i2'),
        ]

        dset_in.createDimension(dimname='d', size=3)
        dset_in.createVariable(varname='u', datatype='f4', dimensions='d', fill_value=1e37)
        dset_in.createVariable(varname='v', datatype='f4', dimensions='d', fill_value=1e37)
        dset_in.variables['u'].set_auto_maskandscale(False)
        dset_in.variables['v'].set_auto_maskandscale(False)
        dset_in.variables['u'][:] = [1, 2, 1e37]
        dset_in.variables['v'][:] = [4, 1e37, 6]

        roms2nc4int2.run(dset_in, dset_out, protocol)  # type: ignore

        assert dset_out.variables['u'][:].tolist() == [1, 2, 0]
        assert dset_out.variables['v'][:].tolist() == [4, 0, 6]

    def test_variable_data_are_stored_using_specified_data_type(self, dset_in, dset_out):
        protocol = [dict(varname='v', dtype='i2')]
        dset_in.createVariable(varname='v', datatype='f4')[:] = 5.9
        roms2nc4int2.run(dset_in, dset_out, protocol=protocol)  # type: ignore

        assert dset_out.variables['v'][:].tolist() == 5
        assert dset_out.variables['v'].dtype == np.dtype('int16')

    def test_adds_unlimited_property_to_ocean_time(self, dset_in, dset_out):
        protocol = [dict(varname='v')]
        dset_in.createDimension(dimname='ocean_time', size=2)
        dset_in.createDimension(dimname='d', size=3)
        dset_in.createVariable(varname='v', datatype='i2', dimensions=('ocean_time', 'd'))
        roms2nc4int2.run(dset_in, dset_out, protocol=protocol)  # type: ignore

        assert not dset_in.dimensions['ocean_time'].isunlimited()
        assert dset_out.dimensions['ocean_time'].isunlimited()

    def test_copies_variable_attributes_verbatim(self, dset_in, dset_out):
        key = 'varname'  # type: roms2nc4int2.ProtocolKeyword
        protocol = [{key: 'myvar'}]
        v = dset_in.createVariable(varname='myvar', datatype='i2')
        v.setncattr('myattr', 'myval')
        roms2nc4int2.run(dset_in, dset_out, protocol)
        assert dset_out.variables['myvar'].getncattr('myattr') == 'myval'

    def test_apply_zlib_compression_to_variables_with_more_than_one_dim(self, dset_in, dset_out):
        protocol = [dict(varname='a'), dict(varname='b')]
        dset_in.createDimension(dimname='d1', size=2)
        dset_in.createDimension(dimname='d2', size=3)
        dset_in.createVariable(varname='a', datatype='i2', dimensions=('d1', 'd2'))
        dset_in.createVariable(varname='b', datatype='i2', dimensions='d1')
        roms2nc4int2.run(dset_in, dset_out, protocol=protocol)  # type: ignore

        assert dset_out.variables['a'].filters()['zlib']
        assert not dset_out.variables['b'].filters()['zlib']

    def test_adds_georeferencing_information_if_grid_file_is_supplied(self, dset_in, dset_out, dset_grid):
        protocol = [dict(varname='a'), dict(varname='b')]
        dset_in.createDimension(dimname='x', size=2)
        dset_in.createDimension(dimname='y', size=3)
        dset_in.createVariable(varname='a', datatype='i2', dimensions=('x', 'y'))
        dset_in.createVariable(varname='b', datatype='i2', dimensions=())
        roms2nc4int2.run(dset_in, dset_out, protocol, dset_grid)  # type: ignore

        assert dset_out.variables['crs'].ncattrs() == dset_grid.variables['crs'].ncattrs()
        assert dset_out.variables['x'].ncattrs() == dset_grid.variables['x'].ncattrs()
        assert dset_out.variables['y'].ncattrs() == dset_grid.variables['y'].ncattrs()
        assert dset_out.variables['a'].getncattr('grid_mapping') == 'crs'
        assert 'grid_mapping' not in dset_out.variables['b'].ncattrs()
