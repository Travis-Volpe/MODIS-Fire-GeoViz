################################################################################
# Author: Travis Volpe
#
# Date Created: 12/20/2018
#
# Name: Blue Raster Technical interview
#
# Description: The following scripts use ArcPy to convert tabular data into a
#               feature class and preform various spatial analyses
#
# Contents: Part 0: Setting up scripting environment
#           Part 1: Extracting & manipulating CSV data with ArcPy
#           Part 2: Grouping fires
#           Part 3: Selecting Highest Confidence fires
#           Part 4: Average Distance matrix
#           Part 5: Fires within 5km of Boarder
#
# Sources:
# http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-classes/
# https://firms.modaps.eosdis.nasa.gov/active_fire/c6/text/MODIS_C6_South_America_7d.csv
# https://geo.nyu.edu/catalog/stanford-vc965bq8111
#
################################################################################
# Part 0: Setting up scripting environment
# 0a download and configure Anaconda environment
# in ArcGIS import sys, numpy, matplotlib
# in anaconda command prompt
# conda create -n arc1061 python=2.7.10 numpy=1.9.2 matplotlib=1.4.3
# pyparsing xlrd xlwt pandas scipy ipython ipython-notebook ipython-qtconsole
#
# 0b allow ArcGIS and Anaconda to interact
# copy Desktop10.6.1.pth file into Ana env site-packages
# create conda pth file in py27/arcgis site-packages
################################################################################

# Part 1: Extracting & manipulating CSV data with ArcPy
#Import modules
import arcpy
import csv
import pandas as pd
from pandas import DataFrame as df

# Set directories & environment settings
arcpy.env.workspace = r"C:/SA_Fires"

arcpy.env.overwriteOutput = True

#Local Variables
# table="C:/SA_Fires/MODIS_C6_South_America_7d.csv"
# in_x_field="longitude"
# in_y_field="latitude"
# out_layer="MODIS_C6_South_America_7d_Layer"
# spatial_reference="{4326}"

# Method 1: MakeXYEventLayer & Feature to Point Tools
# ArcGIS Desktop
# MakeXYEventLayer_management (table, in_x_field, in_y_field, out_layer, {spatial_reference}, {in_z_field})
arcpy.MakeXYEventLayer_management(table="C:/SA_Fires/Tabular/MODIS_C6_South_America_7d.csv",
    in_x_field="longitude",
    in_y_field="latitude",
    out_layer="MODIS_C6_South_America_7d_Layer",
    spatial_reference="{4326}") # WKID for GCS_WGS_1984 ; 4674 - SIRGAS 2000

arcpy.FeatureToPoint_management(in_features="MODIS_C6_South_America_7d_Layer",
    out_feature_class="C:/SA_Fires/SHP/SA_Fires.shp",
    point_location="CENTROID")

# Method 2: Creating Points from lat/long data
xyPoints = open(r"C:/SA_Fires/Tabular/MODIS_C6_South_America_7d.csv")
emptyFC = "C:/SA_Fires/SHP/SA_Fires_Empty.shp"
spatialRef = arcpy.Describe(emptyFC).spatialReference

csvReader = csv.reader(xypoints)
header = csvReader.next()
latIndex = header.index("latitude")
lonIndex = header.index("longitude")

pointArray = arcpy.Array()

for row in csvReader:
    lat = row[latIndex]
    lon = row[lonIndex]

    point = arcpy.Point(lon, lat)
    pointArray.add(point)

with arcpy.da.InsertCursor(emptyFC, ("SHAPE@",)) as cursor:
    points = arcpy.Point(pointArray, spatialRef)
    cursor.insertRow((points,))

# Project in WGS 1984 Web Mercator Aux Sph? WKID 3857

# ArcPro

# Local Variables
# in_table = r"MODIS_C6_South_America_7d.csv"
# out_feature_class = "fire_points"
# x_coords = "longitude"
# y_coords = "latitude"

# arcpy.management.XYTablePoint(in_table, out_feature_class,
#                              x_coords, y_coords,
#                              arcpy.SpatialReference(4674, 31987))
################################################################################
# Part 2: Grouping Fires

# Method 1: Spatial Join
arcpy.SpatialJoin_analysis(target_features="SA_Fire_Pts",
    join_features="SouthAmerica",
    out_feature_class="C:/SA_Fires/SHP/SA_Fire_Pts_SJ.shp",
    join_operation="JOIN_ONE_TO_ONE",
    join_type="KEEP_ALL",
    field_mapping='[*]',
    match_option="WITHIN")

# Method 2: Split & re-merge
arcpy.AddField_management(in_table="SA_Fire_Pts",
    field_name="Location",
    field_type="TEXT",
    field_length="20",
    field_is_nullable="NULLABLE",
    field_is_required="NON_REQUIRED")

arcpy.Split_analysis(in_features="SA_Fire_Pts",
    split_features="SouthAmerica",
    split_field="Name",
    out_workspace="C:SA_Fires")

arcpy.CalculateField_management(in_table="VENEZUELA",
    field="Location",
    expression='"Venezuela"',
    expression_type="PYTHON")

arcpy.CalculateField_management(in_table="ARGENTINA",
    field="Location",
    expression='"Argentina"',
    expression_type="PYTHON")

arcpy.CalculateField_management(in_table="BRAZIL",
    field="Location",
    expression='"Brazil"',
    expression_type="PYTHON")

# ecetera for remaining countries BOLIVIA, CHILE, COLOMBIA ECUADOR GUYANA PARAGUAY
# PERU URUGUAY

arcpy.Merge_management(inputs="ALL_COUNTRIES",
    output="C:/SA_Fires/SHP/SA_Fires_by_Country.shp",
    field_mappings='[*]')

# export shapefile as csv file
createCSV('[*]', 'SA_Fires_by_Country.csv', 'wb')

# Method 3: use search cursor to sort rows by country NAME

fc = "C:/SA_Fires/SHP/SA_Fire_Pts_SJ.shp"
fields = ['NAME']

for row in arcpy.da.SearchCursor(
        fc, fields, sql_clause=(None, 'ORDER BY Name')):
    print('{0}'.format(row[0]))

#with arcpy.da.SearchCursor('fc', [fields], "") as cursor:
#    for row in cursor:
#        print('{NAME} has {} fires'.format(row[], row[])

################################################################################
#Part 3: Highest Confidence fire in each country with a fire
# heighest confidence value = 100?
# Just select all fires where c = 100?

# Method 1: Select all Fires WHERE c >= 100
arcpy.Select_analysis(in_features="SA_Fires_by_Country",
    out_feature_class="C:/SA_Fires/SHP/High_Confidence_Fires.shp",
    where_clause='"confidence" =100')

headers = "[*]"
csvname = "High_Confidence_Fires.csv"
createCSV(headers, csvname, 'wb')

# Method 2: Export re-merged fc as CSV file, find max and write to new file

# def max(arr):
#    max_ = arr[0]
#    for item in arr:
#        if item > max_:
#            max_ = item
#    return max_

df = pd.read_csv('SA_Fires_by_Country.csv')
max_conf = df['confidence'].max()
writer = pd.ExcelWriter(r"C:SA_Fires/Tabular/Highest_Confidence_fires.xlsx")
max_conf.to_excel(writer)
writer.save()

# Method 3: Data cursors
fc = "C:/SA_Fires/SHP/SA_Fire_Pts_SJ.shp"
fields = ['Name', 'confidence']

for row in arcpy.da.SearchCursor(fc, fields, sql_clause=('Select a Country', 'Top 1')):
    print('{0}, {1}'.format(row[0], row[1]))

################################################################################
#Part 4: For each fire find the average distance to all other fires

#Method 1 use point distance analyses
arcpy.PointDistance_analysis(in_features="SA_Fire_Pts",
    near_features="SA_Fire_Pts",
    out_table="C:/SA_Fires/Tabular/SA_Fire_Pts_PointDistance", # CHANGE
    search_radius="")

# Create pivot table if singular value wanted
PtDist_a = "SA_Fire_Pts_PointDistance"
Pivot_table = "C:SA_Fires/Tabular/PtDist_Pivot.csv"

arcpy.PivotTable_management(PtDist_a, "INPUT_FID", "DISTANCE", Pivot_table)

#Method 2: Use Numpy to calculate a distance matrix


################################################################################
# Part 5: Find Fires that are within 5km of a border (near analysis and search or buffer and select)
# NA than select feature where NDist <= 5km
# Near_analysis (in_features, near_features, {search_radius}, {location}, {angle}, {method})

arcpy.PolygonToLine_management(in_features="SouthAmerica",
    out_feature_class="C:SA_Fires/SHP/South_America_Line.shp",
    neighbor_option="IDENTIFY_NEIGHBORS")

arcpy.Near_analysis(in_features="SA_Fire_Pts",
    near_features="South_America_Line",
    search_radius="5 Kilometers",
    location="NO_LOCATION",
    angle="NO_ANGLE",
    method="PLANAR")

arcpy.Select_analysis(in_features="SA_Fire_Pts",
    out_feature_class="C:SA_Fires/SHP/Fires_win_5km.shp",
    where_clause='"NEAR_DIST" >= 0')

# Method 2
# Buffer country boundries by 5km then select features within

arcpy.Buffer_analysis(in_features="South_America_Line",
    out_feature_class="C:SA_Fires/SHP/South_America_Line_Buf5km.shp",
    buffer_distance_or_field="5 Kilometers",
    line_side="FULL",
    line_end_type="ROUND",
    dissolve_option="NONE",
    dissolve_field="",
    method="PLANAR")

arcpy.SelectLayerByLocation_management(in_layer="SA_Fire_Pts",
    overlap_type="WITHIN",
    select_features="South_America_Line_Buf5km",
    search_distance="0 Meters",
    selection_type="NEW_SELECTION",
    invert_spatial_relationship="NOT_INVERT")



#Additional Ideas
#Space_time series analysis
#Web Scrapping for new fires
#Upload to AGOL automatically?
# stats on fires by the date/ season?
# fires near population centers?
