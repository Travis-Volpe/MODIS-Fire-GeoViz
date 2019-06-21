###
# DELETE
# The following script ...
#
# Use data cursors in the project:
# Data cursors are used to access data records contained within data tables,
#using a row by row iterative approach.
# The new data access model cursors can interact directly with the shape field,
#and when combined with ArcPy geometery objects
# can preform geospatial functions and replace the need to pass data to
# ArcToolbox tools.
#
# arcpy.da
#
# The data access cursors accept a number of required and optional parameters.
# The required parameters are the path to the feature class as a
# string and the fields to be returned. If all fields are required us ([*])
#
# Data access cursors and genometry objects are faster because the results of
# calculations do not need to be written to the disk at each step of analysis
################################################################################

###############################################################################
#
#
#
#
#
#
###############################################################################
# Step 0: Set up 'environment' - download anaconda/spyder
# 0a download and configure Anaconda environment
# in ArcGIS import sys, numpy, matplotlib
# in anaconda command prompt
# conda create -n arc1061 python=2.7.10 numpy=1.9.2 matplotlib=1.4.3 pyparsing xlrd xlwt pandas scipy ipython ipython-notebook ipython-qtconsole
#
# 0b allow ArcGIS and Anaconda to interact
# copy Desktop10.6.1.pth file into Ana env site-packages
#
#
