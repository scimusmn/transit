"""
Recipes for GDAL Geo Tif conversion
"""

from fabric.api import local
import glob


def srs_wgs84_to_google(source):
    """Convert a WGS84 GeoTif file to a Google Mercator GeoTif """

    # Add the google mercator EPSG number to the filename
    target = filename_flag(source, '3785')

    # Use gdal to convert the file
    cmd = 'gdalwarp -s_srs EPSG:4269 -t_srs EPSG:3785 -r bilinear %s %s' % (
        source, target)
    local(cmd)
    return target


def slope(source):
    """Convert a GeoTif to a slope GeoTif"""

    target = filename_flag(source, 'slope')
    cmd = 'gdaldem slope %s %s' % (source, target)
    local(cmd)
    return target


def hillshade(source):
    """Convert a GeoTif to a hillshade GeoTif"""

    target = filename_flag(source, 'hillshade')
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
