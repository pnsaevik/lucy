from lucy.norkyst import roms2nc4int2
import netCDF4 as nc
import numpy as np


class Test_copyvar:
    def test_copies_variable_if_no_extra_params(self):
        dset_src = nc.Dataset('dset_src_1.nc', mode='r+', diskless=True)
        dset_dst = nc.Dataset('dset_dst_1.nc', mode='r+', diskless=True)

        varname = 'myvar'
        dset_src.createDimension(dimname='mydim', size=5)
        dset_src.createVariable(varname, datatype='i4', dimensions='mydim')
        dset_src[varname][:] = 23

        roms2nc4int2.copyvar(dset_src, dset_dst, varname)

        assert dset_dst[varname][:].tolist() == [23] * 5
        assert dset_dst[varname].dtype == np.dtype('i4')
        assert dset_dst[varname].dimensions == ('mydim', )

        dset_src.close()
        dset_dst.close()

    def test_can_convert_variables(self):
        dset_src = nc.Dataset('dset_src_2.nc', mode='r+', diskless=True)
        dset_dst = nc.Dataset('dset_dst_2.nc', mode='r+', diskless=True)

        varname = 'myvar'
        dset_src.createDimension(dimname='mydim', size=5)
        dset_src.createVariable(varname, datatype='f4', dimensions='mydim')
        dset_src[varname][:] = 1.23456789

        dtype = 'i2'
        offset = 0
        scale = 0.001

        roms2nc4int2.copyvar(dset_src, dset_dst, varname, dtype, offset, scale)

        dset_dst.set_auto_maskandscale(False)
        assert dset_dst[varname][:].tolist() == [1234] * 5
        assert dset_dst[varname].dtype == np.dtype(dtype)
        assert dset_dst[varname].dimensions == ('mydim', )

        dset_src.close()
        dset_dst.close()

    def test_can_convert_ln_variables(self):
        dset_src = nc.Dataset('dset_src_2.nc', mode='r+', diskless=True)
        dset_dst = nc.Dataset('dset_dst_2.nc', mode='r+', diskless=True)

        varname = 'myvar'
        varname_out = 'ln_myvar'
        dset_src.createDimension(dimname='mydim', size=4)
        dset_src.createVariable(varname, datatype='f4', dimensions='mydim')
        dset_src[varname][:] = [0, 1e-6, 1, 100]

        dtype = 'i2'
        offset = 0
        scale = 0.001

        roms2nc4int2.copyvar(dset_src, dset_dst, varname_out, dtype, offset, scale)

        dset_dst.set_auto_maskandscale(False)
        assert dset_dst[varname_out][:].tolist() == [-32767, -13815, 0, 4605]
        assert dset_dst[varname_out].dtype == np.dtype(dtype)
        assert dset_dst[varname_out].dimensions == ('mydim', )

        dset_src.close()
        dset_dst.close()

