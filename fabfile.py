"""
Recipes for GDAL GeoTIFF conversion
"""
from fabric.api import local, prompt, task
from fabric.utils import abort
from helper import check_true, header

import glob
import os


def shellquote(s):
    return '"' + s.replace("'", "'\\''") + '"'


def shellescapespace(s):
    """Sometimes we need spaces escaped for shell """
    return s.replace(" ", "\\ ")


@task
#def dem_dir(dir):
def dem_dir(dir, ramp_color='ramp_color.txt', ramp_slope='ramp_slope.txt'):
    """Generate hillshaded DEMs for an entire directory

    Arguments:
        dir: Path to the directory to be processed.
        ramp_color: Path to a text file of the ramp for topo coloring
        ramp_slope: Path to a text file of the ramp for slope shading
    """

    dir_esc = shellescapespace(dir)

    header('Cleaning up')
    delete_prompt = """
I plan on deleting all of these files in this dir:
    *-no_edges.tif
    *bak.tif
    *-3785.tif
    *-hillshade.tif
    *-slope.tif
    *-slopeshade.tif
    color.tif
    hillshades.tif
    slopes.tif

Proceed?
"""
    answer = check_true(prompt(delete_prompt))
    if answer is not True:
        abort('Taking that as a no. No files affected.')

    # Reset the directory
    local('rm -rf %s' % os.path.join(dir_esc, '*-no_edges.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*bak.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-3785.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-hillshade.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-slope.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-slopeshade.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, '*-color.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, 'color.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, 'hillshades.tif'))
    local('rm -rf %s' % os.path.join(dir_esc, 'slopes.tif'))

    filepath = os.path.join(dir, '*.tif')
    files = glob.glob(filepath)
    srs_3785_files = []
    hillshade_files = []
    slope_files = []
    color_files = []
    for file in files:
        print
        print header("Converting %s" % file)

        print "Converting DEM to Google Mercator"
        print
        srs_3785_file = srs_wgs84_to_google(shellquote(file))
        srs_3785_files.append(srs_3785_file)
        print "SRS 3785 file created %s" % srs_3785_file

        print
        print "Creating color relief GeoTIFF"
        print
        color_file = color(srs_3785_file, dir_esc + os.sep + ramp_color)
        color_files.append(color_file)
        print "*" * 50
        print "Color file created %s" % color_file
        print "*" * 50

        print
        print "Creating Hillshade GeoTIFF"
        print
        hillshade_file = hillshade(srs_3785_file)
        hillshade_files.append(hillshade_file)
        print "Hillshade file created %s" % hillshade_file

        print
        print "Creating Slope GeoTIFF"
        print
        slope_file = slope(srs_3785_file, dir_esc + os.sep + ramp_slope)
        slope_files.append(slope_file)
        print "Slope file created %s" % slope_file

    print header("Merging files")
    local('gdal_merge.py -o ' + dir_esc + os.sep + 'srs_3785.tif ' +
          ' '.join(srs_3785_files))
    local('gdal_merge.py -o ' + dir_esc + os.sep + 'hillshades.tif ' +
          ' '.join(hillshade_files))
    local('gdal_merge.py -o ' + dir_esc + os.sep + 'slopes.tif ' +
          ' '.join(slope_files))
    local('gdal_merge.py -o ' + dir_esc + os.sep + 'color.tif ' +
          ' '.join(color_files))


@task
def remove_border(source):
    """Remove single pixel border form the GeoTIFFs

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
    """Convert a WGS84 GeoTIFF file to a Google Mercator GeoTIFF """

    # Add the google mercator EPSG number to the filename
    target = filename_flag(source, '3785')

    # Use gdal to convert the file
    cmd = 'gdalwarp -s_srs EPSG:4269 -t_srs EPSG:3785 -r bilinear %s %s' % (
        source, target)
    local(cmd)
    return target


@task
def slope(source, ramp_slope):
    """Convert a GeoTIFF to a slope GeoTIFF"""

    slope_file = filename_flag(source, 'slope')
    cmd = 'gdaldem slope %s %s' % (source, slope_file)
    local(cmd)
    target = filename_flag(source, 'slopeshade')
    cmd = 'gdaldem color-relief -co compress=lzw %s %s %s' % (
        slope_file, ramp_slope, target)
    local(cmd)
    return target


@task
def hillshade(source):
    """Convert a GeoTIFF to a hillshade GeoTIFF"""

    target = filename_flag(source, 'hillshade')
    cmd = 'gdaldem hillshade -compute_edges -co compress=lzw %s %s' % (
        source, target)
    local(cmd)
    return target


@task
def color(source, ramp_color):
    """Generate a color-relief GeoTIFF """
    target = filename_flag(source, 'color')
    cmd = 'gdaldem color-relief %s %s %s' % (source, ramp_color, target)
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
