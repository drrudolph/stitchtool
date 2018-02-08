#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:13:42 2018

@author: drr
"""

import argparse
import sys
import os
import subprocess
import pathlib
from pathlib import Path
from lxml import etree
import csv
import configparser
import numpy as np
import cv2

#######

def writetoxmlfile(tree, xmlfilename):
    '''write import file for terasticher in xml format'''
    xmltree = etree.ElementTree(TeraStitcher)
    xmltree.write(xmlfilename,
                #method = "html",
                pretty_print = True,
                encoding="utf-8", 
                xml_declaration = True )
                      #doctype='TeraStitcher SYSTEM "TeraStitcher.DTD" ')


def read_mdoc_file():
    mdocfilename = 'test-map.mrc-mod.mdoc'
    mdocpath = datadirpath.absolute().joinpath(mdocfilename)
    if mdocpath.is_file() == True:
        config = configparser.ConfigParser()
        with open(mdocpath, 'r') as mdocfile:
            for i in range(6):
                mdocfile.readline()
            try:
                config.read_file(mdocfile)
            except:
                sys.exit('error parsing mdoc file')
        for i in config.sections():
            coords = config[i]['PieceCoordinates']
            findex = i.split()[2]
            data = coords.split()
            images.append( {'filename':'test-map.00' + findex + '.tif',
                            'x':int(data[0]),
                            'y':int(data[1]),
                            'z':int(data[2])} )
    else:
        sys.exit(".mdoc file not found")


class tile:
    def __init__(self):
#        self.pos_x = -1
#        self.pos_y = -1
#        self.size_x = -1
#        self.size_y = -1
#        #self.
        pass


def create_TS_XML():
    #create XML structure
    TeraStitcher = etree.Element('TeraStitcher')
    TeraStitcher.set('volume_format', 'TiledXY|2Dseries')
    
    stacks_dir = etree.SubElement(TeraStitcher, 'stacks_dir')
    voxel_dims = etree.SubElement(TeraStitcher, 'voxel_dims')
    origin = etree.SubElement(TeraStitcher, 'origin')
    mechanical_displacements = etree.SubElement(TeraStitcher, 'mechanical_displacements')
    dimensions = etree.SubElement(TeraStitcher, 'dimensions')
    #stack_rows = etree.SubElement(TeraStitcher, 'stack_rows')
    #stack_columns = etree.SubElement(TeraStitcher, 'stack_columns')
    dir_name = etree.SubElement(TeraStitcher, 'dir_name')
    stacks = etree.SubElement(TeraStitcher, 'STACKS')
    
    stacks_dir.set('value', str(datadirpath))
    
    
    if args.msem:
        for image in images:
            stack = etree.SubElement(stacks, 'Stack')
            stack.set('DIR_NAME', 'datadirpath')
            stack.set('IMG_REGEX', '*.bmp')
    
    
    if args.mdoc:
        voxel_dims.set('V', '0.2')
        voxel_dims.set('H', '0.2')
        voxel_dims.set('D', '0.2')
    
        origin.set('V', '0.0')
        origin.set('H', '0.0')
        origin.set('D', '0.0')
    
        dimensions.set('stack_rows', '2')
        dimensions.set('stack_columns', '2')
        dimensions.set('stack_slices', '1')
        
        mechanical_displacements.set('V', '0.2')
        mechanical_displacements.set('H', '0.2')
    
        for image in images:
            stack = etree.SubElement(stacks, 'Stack')
            stack.set('ROW', str(image['x']))
            stack.set('COL', str(image['y']))
            stack.set('ABS_V', str(image['x']))
            stack.set('ABS_H', str(image['y']))
            stack.set('ABS_D', str(image['z']))
            stack.set('STITCHABLE', 'no')
            stack.set('DIR_NAME', '.')
            stack.set('IMG_REGEX', '.*\.tif')
            stack.set('Z_RANGES', "[0,1)")
            north_disp = etree.SubElement(stack, 'NORTH_displacements')
            north_disp = etree.SubElement(stack, 'EAST_displacements')
            north_disp = etree.SubElement(stack, 'SOUTH_displacements')
            north_disp = etree.SubElement(stack, 'WEST_displacements')
    
            stack.text = ''  # closing brackets
    
    writetoxmlfile(TeraStitcher, "xmltest.xml")
    
    #with open("xmltest.xml", 'w') as xmlfile:
    #    xmltree = etree.ElementTree(TeraStitcher)
    #    xmltree.write(xmlfilename, pretty_print = True, encoding="utf-8", xml_declaration = True)

###########################################################################
def read_coordinates_file(coordfilename):
    #coordfilename = 'full_image_coordinates.txt'
    #coordfilename = 'image_coordinates.txt'
    coordinates = []
    #coordinatepath = datadirpath.absolute().joinpath(coordfilename)
    if coordfilename.is_file() == True:
        with open(coordfilename, 'r') as coordinatefile:
            for line in coordinatefile:
                data = line.split()
                coordinates.append( {'filename':data[0],
                                'x':float(data[1]),
                                'y':float(data[2]),
                                'z':float(data[3])} )
    else:
        sys.exit("coordinate file not found")
    return(coordinates)


def create_unix_imgpath(filename, dirpath):
    '''create absolute image path from metadata and directory'''
#for i in imagelist:
#        i['filename']
    #relpath = Path(pathlib.PureWindowsPath(i['filename']).as_posix())
    relpath = Path(pathlib.PureWindowsPath(filename).as_posix())
    #relpath = Path(pathlib.PureWindowsPath(filename)
    relpath = Path(relpath)
    abspath = dirpath.absolute().joinpath(relpath)
    #print(abspath)
    return(abspath)
   

#def filter_images_external(imagelist, savedirpath, filtercmd):
#    for i in imagelist:
#       cmd = filtercmd + imagelist[]
#       subprocess.run(filtercmd)
    
    
def read_region_metadata(csvfilename):
    '''read region metadata from csv, return list of ordered dicts of fovs'''
    csvfilename = datadirpath.absolute().joinpath(csvfilename)
    with open(csvfilename, 'r', newline='') as csvfile:
        csvfile.readline() # skip first syntax line
        reader = csv.DictReader(csvfile, delimiter=';') 
        fovlist = []
        for row in reader:
            #print(row['Brightness'])
            fovlist.append(row)
        return(fovlist)

        
def show_msem_preview(imagelist):
    xmin = sys.maxsize
    xmax = -1
    ymin = sys.maxsize
    ymax = -1
    
    #TODO: get image size
    #test_tile = cv2.imread
    #tile_size_x = images[0].shape[0]
    #tile_size_y = images[0].shape[1]
    tile_size_y = 196
    tile_size_x = 170
    
    preview_map = np.zeros( (2 * tile_size_x, 2 * tile_size_y), dtype='uint8')
    #preview_map = np.zeros( (2 * tile_size_x, 2 * tile_size_y), dtype='uint8')
    tiles = []

    
    for i in imagelist:
        xmin = min(xmin, i['x'])
        xmax = max(xmax, i['x'])
        ymin = min(ymin, i['y'])
        ymax = max(ymax, i['y'])
    
    map_dim_x = int(np.ceil(xmax-xmin))
    map_dim_y = int(np.ceil(ymax-ymin))
    print(xmax, xmin, ymax, ymin)
    print(map_dim_x, map_dim_y)

    preview_map = np.zeros( (map_dim_x, map_dim_y), dtype='uint8')
    
    for i in imagelist:
        relpath = Path(pathlib.PureWindowsPath(i['filename']).as_posix())
        #relpath = Path(relpath.parent.name).joinpath(relpath.name)
        #relpath = Path(tile['filename']).name
        relpath = Path(relpath)
        abspath = datadirpath.absolute().joinpath(relpath)
        print(abspath)
        #current_tile = tile()
        #tile.pos_x = 
        preview_map[i['x']:i['x']+tile_size_x, i['y']:i['y']+tile_size_y] = i

        tiles.append( cv2.imread(str(abspath), 0) )
        #tile_size_x = tile.shape[0]
        #tile_size_y = tile.shape[1]
        
     
    #preview_map[0:tile_size_x,0:tile_size_y] = tile[0]
    #preview_map[1*tile_size_x:2*tile_size_x,0:tile_size_y] = tile[1]
    #preview_map[0:170,171:196] = tile[1]
    #preview_map[0:tile_size_x,1*tile_size_y:2*tile_size_y] = tile[2]
    #preview_map[1*tile_size_x:2*tile_size_x,1*tile_size_y:2*tile_size_y] = tile[3]


    #preview_map[0:tile_size_x,0:tile_size_y] = tile[0].re

    equalized = cv2.equalizeHist(preview_map)
    
    clahe = cv2.createCLAHE()
    equalized = clahe.apply(preview_map)
    
    cv2.namedWindow('preview', cv2.WINDOW_KEEPRATIO)
    #cv2.imshow(window, preview_map)        
    cv2.imshow('preview', equalized)
    cv2.resizeWindow('preview', 1024, 768)

    cv2.waitKey(0)       
    cv2.destroyAllWindows()

################
#main
################
    
parser = argparse.ArgumentParser()
#parser.add_argument("datadir", help="raw data directory")
parser.add_argument("outdir", help="output directory")
#parser.add_argument("--msem", help="data is in MultiSEM format", action='store_true')
parser.add_argument("--msem", help="MultiSEM image coordinates file")
parser.add_argument("--mdoc", help="data is in mdoc format (SerialEM)", action='store_true')
parser.add_argument("--pcmd", help="process command for each file")

args = parser.parse_args()


#sanity checks

if args.msem and args.mdoc:
    sys.exit("syntax error")
    
#if args.pmcd and not args.outdir:
#    sys.exit("no output directory specified")

#TODO: resolve homedir (~)
#datadirpath = Path(args.datadir).absolute()
if args.msem:
    if Path(args.msem).exists():
        datadirpath = Path(args.msem).parent.absolute()
    else: sys.exit("mSEM data file not found")
    outdirpath = Path(args.outdir).absolute()
    #print(datadirpath)

if datadirpath == outdirpath:
    #TODO allow/check
    sys.exit("output directory equal to input directory: will not overwrite input data")

if datadirpath.absolute().exists() == False:
    sys.exit("data dir not found")

if outdirpath.parent.absolute().exists() == False:
    sys.exit("cannot create output dir")


if args.msem:
    #images = []
    #TODO
    #fovlist = read_region_metadata('region_metadata.csv')
    
    #images = read_coordinates_file('full_image_coordinates.txt')
    images = read_coordinates_file(Path(args.msem))
    #images = read_coordinates_file('full_thumbnail_coordinates.txt')
    print("found", len(images), "images")
    #print(images[0]['Storage Path'])
    #show_msem_preview(images)
    if args.pcmd:
        
#        #find top for of dataset
#        toppath = datadirpath.absolute()
#        while not (toppath == toppath.anchor):
#            if sorted(toppath.glob('*.czi')):
#                break
#            else:
#                toppath = toppath.parent
#        reltoppath = datadirpath.relative_to(toppath.parent)
#        outdirpath = outdirpath.joinpath(reltoppath)
        
        outdirpath.mkdir(parents=True, exist_ok=True)
        for i in images:
            #relpath = Path(i['filename']).absolute().relative_to(datadirpath)
            infile = create_unix_imgpath(i['filename'], datadirpath)
            print("infile:",infile)
            outfile = create_unix_imgpath(i['filename'], outdirpath)
            print("outfile:",outfile)
            print(outdirpath, outfile)
#            cmd = args.pcmd + infile.as_posix() + outfile.as_posix()
            cmd = '{0} '"'{1}'"' '"'{2}'"' '.format(args.pcmd, infile.as_posix(), outfile.as_posix())
            #cmd = '{0} {1} '"'{2}'"' '"'{3}'"' '.format('/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/bin/python', args.pcmd, infile.as_posix(), outfile.as_posix())
#            command = ['/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/bin/python', args.pcmd, infile, outfile]
            command = [args.pcmd, infile.as_posix(), outfile.as_posix()]
            newenv = os.environ.copy()
            newenv['PATH'] = '/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/bin:/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/extlib/bin' + newenv['PATH']
            newenv['PYTHONPATH'] = '/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/lib:/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/bin'
            newenv['PYTHONHOME'] = '/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL'
            newenv['LD_LIBRARY_PATH'] = '/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL/lib'
            newenv['EMAN2DIR'] = '/cm/shared/apps/sphire/beta/dist-eman2-2017-10-01-EXPERIMENTAL'
            #print("processing", infile, "saving to", outfile)
#            proc = subprocess.run( [args.pcmd, infile.as_posix(), outfile.as_posix()], shell=True)
#            proc = subprocess.run( command, shell=True, env=newenv)
            #proc = subprocess.run( command, shell=True)
            print("command:", cmd)
            proc = subprocess.run(cmd, env=newenv, shell=True)

            proc.check_returncode()
            
if args.mdoc:
    read_mdoc_file()
    
