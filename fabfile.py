"""
Recipes for GDAL Geo Tiff conversion
"""
from fabric.api import local, prompt, task
from fabric.utils import abort
from helper import header, check_true
import glob
import os

def shellquote(s):
    return '"' + s.replace("'", "'\\''") + '"'


def shellescapespace(s):
    """Sometimes we need spaces escaped for shell """
    return s.replace(" ", "\\ ")


@task
def dem_dir(dir):
    """Generate hillshaded DEMs for an entire directory

    THIS IS A HACK
    really only works with fab dem_dir:''

    """
    dir_esc = shellescapespace(dir)

    header('Cleaning up')
    delete_prompt = """
I plan on deleting all of these files in this dir:
    *-no_edges.tif'
    *bak.tif'
    *-3785.tif'
    *-hillshade.tif'
    *-slope.tif'

Proceed?
"""
    answer = prompt(delete_prompt)
    if check_true(answer) is not True:
        abort()

    # Reset the directory
    local('rm -rf %s' % os.path.join(dir_esc, '*-no_edges.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*bak.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-3785.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-hillshade.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-slope.tif'))

    filepath = os.path.join(dir, '*.tif')
    files = glob.glob(filepath)
    hillshade_files = []
    slope_files = []
    for file in files:
        print
        print """
===============================================================================
"""
        print "Converting %s" % file

        srs_3785_file = srs_wgs84_to_google(shellquote(file))
        print "SRS 3785 file created %s" % srs_3785_file

        hillshade_file = hillshade(srs_3785_file)
        hillshade_files.append(hillshade_file)
        print "Hillshade file created %s" % hillshade_file

        slope_file = slope(srs_3785_file)
        slope_files.append(slope_file)
        print "Slope file created %s" % slope_file

        print """
===============================================================================
"""
    print "Merging files"
    local('gdal_merge.py -o hillshades.tif ' + ' '.join(hillshade_files))
    local('gdal_merge.py -o slopes.tif ' + ' '.join(slope_files))


@task
def remove_border(source):
    """Remove single pixel border form the GeoTifs

    These borders cause problems in transparency
    """
    target = filename_flag(source, 'no_edges')
    cmd = 'gdal_translate %s -co tfw=yes temporary.tif' % (source)
    local(cmd)
    cmd = 'gdal_translate temporary.tif %s' % (target)
    local(cmd)

    return target


@task
def srs_wgs84_to_google(source):
    """Convert a WGS84 GeoTif file to a Google Mercator GeoTif """

    # Add the google mercator EPSG number to the filename
    target = filename_flag(source, '3785')

    # Use gdal to convert the file
    cmd = 'gdalwarp -s_srs EPSG:4269 -t_srs EPSG:3785 -r bilinear %s %s' % (
        source, target)
    local(cmd)
    return target


@task
def slope(source):
    """Convert a GeoTif to a slope GeoTif"""

    target = filename_flag(source, 'slope')
    cmd = 'gdaldem slope %s %s' % (source, target)
    local(cmd)
    return target


@task
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
