"""
Recipes for GDAL Geo Tif conversion
"""

from fabric.api import local
import glob

def hillshade(source):
    """Convert a GeoTif to a hillshade GeoTif"""

    # Append an identifier to the filename
    target = filename_flag(source, 'hillshade')

    # Use gdal to convert the file
    cmd = 'gdaldem hillshade -compute_edges -co compress=lzw %s %s' % (
        source, target)
    local(cmd)
    return target


def filename_flag(filename, flag):
    filename_parts = filename.split('.')
    output = ''
    count = len(filename_parts)
    for part in filename_parts:
        if count == 1:
            output = output + '-' + flag + '.'
        count = count - 1

        output = output + part

    return str(output)
