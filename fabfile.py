"""
Recipes for GDAL Geo Tif conversion
"""

from fabric.api import local
import glob


def dem_dir(dir):
    """Generate hillshaded DEMs for an entire directory

    THIS IS A HACK
    really only works with fab dem_dir:''

    """

    local('rm -rf *-no_edges.tif')
    local('rm -rf *bak.tif')
    local('rm -rf *-3785.tif')
    local('rm -rf *-hillshade.tif')
    local('rm -rf *-slope.tif')
    filepath = dir + '*.tif'
    files = glob.glob(filepath)
    hillshade_files = []
    slope_files = []
    for file in files:
        print
        print """
===============================================================================
"""
        print "Converting %s" % file

        srs_3785_file = srs_wgs84_to_google(file)
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
