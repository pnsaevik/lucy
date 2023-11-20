"""
Functions for converting ROMS output files to NorKyst output format

The main function ``main()`` copies variables from input netCDF3 or netCDF4 file to
output netCDF4 file, optionally converting datatypes and use linear packing.

Pål Næverlid Sævik <a5606@hi.no>
2021-03-01

Loosely based on a previous script by Bjørn Ådlandsvik and Jon Albretsen
"""

import sys
import netCDF4 as nc
import numpy as np
import logging
import typing
logger = logging.getLogger(__name__)


DEFAULT_PROTOCOL = """
varname     dtype   offset  scale
-----------------------------------
swrad       i2      0       0.1
shflux      i2      0       0.1
Uwind       i2      0       0.01
Vwind       i2      0       0.01
tisrf       i2      0       0.01
zeta        i2      0       0.01
aice        i2      0       0.001
hice        i2      0       0.001
hsno        i2      0       0.001
snow_thick  i2      0       0.001
uice        i2      0       0.001
vice        i2      0       0.001
ubar        i2      0       0.001
vbar        i2      0       0.001
sustr       i2      0       0.001
svstr       i2      0       0.001
bustr       i2      0       0.001
bvstr       i2      0       0.001
u           i2      0       0.001
v           i2      0       0.001
omega       i2      0       0.001
temp        i2      10      0.001
salt        i2      30      0.001
ssflux      i2      0       0.00001
w           i2      0       0.00001
AKt         f4      0       1
AKs         f4      0       1
Vtransform  i2
Vstretching i2
mask_rho    i1
mask_u      i1
mask_v      i1
ocean_time
theta_s
theta_b
Tcline
hc
s_rho
Cs_r
Cs_w
h
angle
pm
pn
lon_rho
lat_rho
lon_u
lat_u
lon_v
lat_v

"""


FILL_VALUES = dict(
    i1=-127,
    i2=-32767,
    i4=-2147483647,
    i8=-9223372036854775807,
    f4=-1e+37,
    f8=-1e+307,
)


ProtocolKeyword = typing.Literal["varname", "dtype", "offset", "scale"]
ProtocolType = typing.List[typing.Dict[ProtocolKeyword, typing.Union[float, str]]]


def main():
    import sys

    # Print help message when requested
    if len(sys.argv) < 3 or len(sys.argv) > 4 or '--help' in sys.argv:
        print(
            'Usage 1: roms2nc4int2 input_file output_file\n'
            '  Copies selected variables from `input_file` to `output_file`, using netCDF4\n'
            '  file format with zlib compression and linear packing compression.\n'
        )
        print(
            'Usage 2: roms2nc4int2 grid_file input_file output_file\n'
            '  Same as usage 1, but also copies grid georeferencing data from `grid_file`.'
        )
        return

    # Interpret command line arguments
    ofile = sys.argv[-1]
    ifile = sys.argv[-2]
    if len(sys.argv) > 3:
        gfile = sys.argv[-3]
    else:
        gfile = None

    input_dset = None
    output_dset = None
    grid_dset = None

    try:
        logger.info("Open input dataset: " + ifile)
        input_dset = nc.Dataset(ifile)
        input_dset.set_auto_maskandscale(False)

        logger.info("Open output dataset: " + ofile)
        output_dset = nc.Dataset(ofile, mode='w', format='NETCDF4_CLASSIC')
        output_dset.set_auto_maskandscale(False)

        # Process dataset
        process(input_dset, output_dset, read_csv(DEFAULT_PROTOCOL))

        if gfile:
            logger.info("Open grid dataset: " + gfile)
            grid_dset = nc.Dataset(gfile)
            grid_dset.set_auto_maskandscale(False)

            # Append georeferencing
            logger.info("Copy georeferencing information")
            add_georeference(grid_dset, output_dset)

    finally:
        # Close datasets silently
        for ff in [input_dset, output_dset, grid_dset]:
            if ff is not None:
                try:
                    ff.close()
                except IOError:
                    pass

    logger.info("Finished")


def read_csv(txt):
    """Converts csv-formatted text to list of dicts. Assumes first line are column
    headers. Ignores any line starting with non-letters. Accepts lines with fewer
    elements than column headers."""

    # Convert string to float if possible, otherwise return string verbatim
    def numconv(s):
        try:
            return float(s)
        except ValueError:
            return s

    import re
    lines = [ln for ln in re.split('[\r\n]', txt) if re.match('[a-zA-Z]', ln)]
    elements = [[numconv(e) for e in re.split('\\s+', ln.strip())] for ln in lines]
    colnames = elements[0]
    return [dict(zip(colnames, elm)) for elm in elements[1:]]


def process(dset_in: nc.Dataset, dset_out: nc.Dataset, protocol: ProtocolType):
    """
    Converts data according to the given protocol

    The data in the input dataset is loaded, converted and stored to the output dataset
    according to the given protocol. The protocol is a list of dicts, where each element
    has a required keyword ``varname`` and optional keywords ``dtype``, ``offset``,
    ``scale`` and ``unlimited``.

    The conversion process has the following properties:

    1.  Dataset attributes are copied verbatim, except ``history`` which is appended to.
        An additional attribute "institution" is added.

    2.  Variables which are not contained in ``protocol`` are dropped

    3.  Variable data are scaled and offsetted according to ``scale`` and ``offset``

    4.  Variable data are stored using ``dtype`` data type

    5.  The dimension ``ocean_time`` is set to be unlimited

    6.  All variable attributes are copied verbatim

    7.  Compression with zlib is applied to all variables with more than one dimension

    :param dset_in: Input dataset
    :param dset_out: Output dataset
    :param protocol: Conversion protocol
    """
    # Copy attributes
    logger.info("Copy dataset attributes")
    for attr in dset_in.ncattrs():
        dset_out.setncattr(attr, dset_in.getncattr(attr))

    # Add additional attributes
    dset_out.institution = "Institute of Marine Research"
    dset_out.history = append_history(dset_in)

    # Copy variables, coordinates and dimensions
    for p in protocol:
        copyvar(dset_in, dset_out, **p)


def copyvar(dset_src, dset_dst, varname, dtype=None, offset=None, scale=None, **kwargs):
    if varname not in dset_src.variables:
        return None

    src = dset_src.variables[varname]
    src.set_auto_maskandscale(False)

    # Create dimensions
    for dimname in src.dimensions:
        if dimname not in dset_dst.dimensions:
            dimsize = dset_src.dimensions[dimname].size
            if dimname == 'ocean_time':
                dimsize = None
            logging.info("Create dimension " + dimname + "(" + str(dimsize) + ")")
            dset_dst.createDimension(dimname, dimsize)

    # Define fill value
    if scale is not None:
        kwargs['fill_value'] = FILL_VALUES[dtype]
    elif '_FillValue' in src.ncattrs():
        kwargs['fill_value'] = src.getncattr('_FillValue')

    # Use zlib compression unless the variable is one-dimensional
    if 'zlib' not in kwargs and len(src.shape) > 1:
        kwargs['zlib'] = True

    # Create variable
    logger.info("Copy variable " + varname + str(src.shape))
    dst = dset_dst.createVariable(
        varname, datatype=dtype or src.dtype, dimensions=src.dimensions, **kwargs)
    dst.set_auto_maskandscale(False)

    # Copy attributes
    for attr in src.ncattrs():
        if not attr.startswith('_'):
            dst.setncattr(attr, src.getncattr(attr))

    # If no conversion, copy values verbatim
    if dtype is None:
        dst[...] = src[...]

    # If conversion, do rescaling and fill missing values
    else:
        # Find missing values in original dataset
        if '_FillValue' in src.ncattrs():
            is_invalid = src[...] == src.getncattr('_FillValue')
        else:
            is_invalid = np.zeros(src.shape, dtype=bool)

        # Define new offset and scale
        offset_src = getattr(src, 'add_offset', 0)
        scale_src = getattr(src, 'scale_factor', 1)
        offset_dst = offset or 0
        scale_dst = scale or 1
        dst.add_offset = offset_dst
        dst.scale_factor = scale_dst

        # Define fill value in destination dataset
        if '_FillValue' in dst.ncattrs():
            fill_value = dst.getncattr('_FillValue')
        else:
            fill_value = None

        # Define overflow and underflow limits
        if dtype.startswith('i'):
            underflow = np.iinfo(dtype).min
            overflow = np.iinfo(dtype).max
        else:
            underflow = -np.inf
            overflow = np.inf

        # Copy with scaling, chunk-wise
        chunks = get_chunks(src)
        for chunk in chunks:
            values = src[chunk]*scale_src + offset_src
            with np.errstate(all='ignore'):
                transformed_values = (values - offset_dst) / scale_dst
                raw_values = transformed_values.astype(dtype)
            if raw_values.shape != () and fill_value is not None:
                raw_values[raw_values < underflow] = fill_value
                raw_values[raw_values > overflow] = fill_value
                raw_values[is_invalid[chunk]] = fill_value
            dst[chunk] = raw_values

        # Remove scale and offset attributes if redundant
        if scale_dst == 1 and offset_dst == 0:
            dst.delncattr('scale_factor')
            dst.delncattr('add_offset')

    return dst


def add_georeference(grid_dset, out_dset):
    # Find grid mapping variable
    grid_mapping_varname = None
    for varname in grid_dset.variables:
        if 'grid_mapping_name' in grid_dset.variables[varname].ncattrs():
            grid_mapping_varname = varname
            break

    # Find projection coordinate variables
    proj_vars = []
    pvar_std_names = ['projection_x_coordinate', 'projection_y_coordinate']
    for varname in grid_dset.variables:
        if getattr(grid_dset.variables[varname], 'standard_name', '') in pvar_std_names:
            proj_vars.append(varname)

    # Copy projection coordinate variables and grid mapping variable
    for varname in [grid_mapping_varname] + proj_vars:
        copyvar_verbatim(grid_dset.variables[varname], out_dset)

    # Add grid mapping reference to all variables using projection coordinates
    for varname in out_dset.variables:
        v = out_dset.variables[varname]
        if set.intersection(set(v.dimensions), set(proj_vars)):
            v.grid_mapping = grid_mapping_varname


def copyvar_verbatim(v, dset, **kwargs):
    new_v = dset.createVariable(v.name, v.dtype, v.dimensions, **kwargs)
    new_v[...] = v[...]
    for attr in v.ncattrs():
        if not attr.startswith('_'):
            new_v.setncattr(attr, v.getncattr(attr))
    return new_v


def append_history(dset):
    if 'history' in dset.ncattrs():
        history = dset.history + "\n"
    else:
        history = ""

    history += str(np.datetime64('now')) + ' - roms2nc4int2.py ' + " ".join(sys.argv[1:])
    return history


def get_chunks(var):
    if np.product(var.shape) < 1000*1000*50:
        return [...]
    else:
        return np.arange(var.shape[0])


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    main()
