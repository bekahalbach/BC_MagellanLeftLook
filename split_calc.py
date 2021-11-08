# -*- coding: utf-8 -*-
# code by Rebekah Albach
"""
BC Calculator using GDAL for subsetting 
"""

# importing dependencies 
import os 
import numpy as np 
import math 
from osgeo import gdal 

# correction angles
angles = [45.18,45.35,45.49,45.62,45.74,45.85,45.96,46,46,46,46,46,45.94,45.86,45.79,45.72,45.61,45.49,45.36,45.18,44.99,44.78,44.55,44.32,44.03,43.73,43.42,43.12,42.8,42.45,42.1,41.71,41.33,40.96,40.6,40.12,39.64,39.19,38.76,38.33,37.85,37.35,36.85,36.36,35.88,35.4,34.9,34.4,33.9,33.38,32.85,32.32,31.8,31.3,30.8,30.3,29.8,29.3,28.86,28.43,28,27.55,27.09,26.64,26.22,25.82,25.42,25.03,24.66,24.3,23.94,23.61,23.29,22.96,22.64,22.31,21.99,21.67,21.32,20.98,20.63,20.28,19.93,19.57,19.15,18.72,18.29,17.83,17.36,16.9,45,44.81,44.59,44.33,44.04,43.75,43.45,43.18,42.81,42.43,42.08,41.68,41.28,40.89,40.5,40.01,39.56,39.13,38.65,38.13,37.59,37.06,36.53,36.01,35.48,34.96,34.42,33.88,33.34,32.78,32.22,31.67,31.11,30.56,30.02,29.49,28.95,28.46,27.98,27.49,27.02,26.55,26.08,25.62,25.19,24.77,24.34,23.98,23.63,23.28,22.95,22.64,22.33,22.07,21.81,21.56,21.34,21.13,20.91,20.7,20.49,20.31,20.16,20.01,19.79,19.56,19.32,19.04,18.76,18.4,18.02,17.63,17.22,16.8,16.23,15.66,15.11,14.56]


# setting file location 
#os.chdir(r'Y:\bekah_data')

os.chdir(r'C:\Users\Student\Documents\DNcorrection_files') 

# hi

in_ras = gdal.Open('dn_clip2.tif')

# print(in_ras.GetGeoTransform())
# print(in_ras.RasterXSize)
# print(in_ras.GetMetadata())

in_band = in_ras.GetRasterBand(1)

# Size has to be capitalized 
xsize = in_band.XSize
ysize = in_band.YSize 
block_xsize,block_ysize = in_band.GetBlockSize() 
nodata = in_band.GetNoDataValue()


# getting bottom sizes of raster 
ulx, xres, xskew, uly, yskew, yres  = in_ras.GetGeoTransform()
lrx = ulx + (in_ras.RasterXSize * xres)
lry = uly + (in_ras.RasterYSize * yres)

# code to calculate the latitude in degrees based on meters 

# whole raster specific values for Magellan Left Look Equidistant Cylindrical (don't change)
top_meters = 8871191.6025
bottom_meters = -8449908.3975

total_rows = 230948 

top_degrees = 84
bottom_degrees = -80  
cell_size = 75 # in meters 

# calculating the top edge of raster in degrees 
"""
if uly > 0: 
    meters_ratio = uly/top_meters
    degrees = meters_ratio * top_degrees
    
else:
    meters_ratio = uly/bottom_meters
    degrees = meters_ratio * bottom_degrees

print(degrees)"""

out_ras = in_ras.GetDriver().Create('dn_clip2_BC_4.tif',xsize,ysize,1,gdal.GDT_Float32)
#gdal.Translate(out_ras,)
out_ras.SetProjection(in_ras.GetProjection())
out_ras.SetGeoTransform(in_ras.GetGeoTransform())
out_band = out_ras.GetRasterBand(1)

for x in range(0,xsize,block_xsize): 
    if x + block_xsize < xsize: 
        cols = block_xsize 
    else: 
        cols = xsize - x 
    for y in range(0, ysize, 1): 
        rows = 1 

            
        data = in_band.ReadAsArray(x, y, cols, rows)
        
        # for subset of the above raster, use the y index and cell size to calculate meters
        # y is y index
        y_meters_diff = y * cell_size 
        y_position = uly - y_meters_diff

        if uly > 0: 
            meters_ratio_y = y_position/top_meters
            degrees_y = meters_ratio_y * top_degrees
            
        else:
            meters_ratio_y = y_position/bottom_meters
            degrees_y = meters_ratio_y * bottom_degrees

        # get angle for susbet 
        if degrees_y < 0: 
            index = round(abs(degrees_y)+89)
            if index > 167: 
                index = 167
        else: 
            index = round(degrees_y)
            if index > 167: 
                index = 167
            
        a = angles[index]
        
        data = np.where(data == 0, 0, (10*np.log10((10**(0.1*(-20 + ((data - 1)/5))))*(0.0118*math.cos(math.radians(a+0.5)))/(math.sin(math.radians(a+0.5))+0.111*math.cos(math.radians(a+0.5)))**3)))
        
        # this reads and writes one block's worth of data (128 x 128 for my dataset)
        out_band.WriteArray(data,x,y)
        
