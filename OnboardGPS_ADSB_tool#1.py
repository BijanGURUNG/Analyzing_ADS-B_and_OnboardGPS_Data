# -*- coding: utf-8 -*-
"""
File Name: ADSB_OnboardGPS_tool#1.py
Description: Parse the feature class files from Onboard GPS and ADS-B based on the registration or N-Number of the aircraft
Date created: 06/30/2024
"""

__author__ = "Bijan Gurung"
__version__ = "1.0"
__email__ = "bijangurung@ksu.edu"
__status__ = "Production"

# Import acrpy module and allow overwrites
import arcpy, os, datetime, pandas as pd, time, numpy as np
arcpy.env.overwriteOutput = True

# set the scratch folder as the workspace, so the original feature classes remain intact
# inWorkspace = "D:/DENA_ADS-B_OnBoard/DENA/OnboardGPS_TAT.gdb"
inWorkspace = arcpy.GetParameterAsText(0)               # gdb file
input_onboardGPS = arcpy.GetParameterAsText(1)          # JSON feature class from Onboard GPS 
input_park = arcpy.GetParameterAsText(2)                # park feature class file (used the dissolved one)
input_ADSB = arcpy.GetParameterAsText(3)                # ADS-B Merged Waypoints

# set the environment
arcpy.env.workspace = inWorkspace

# set local variable
input_park_Buff = input_park + "_buff10Miles"
outFc = input_onboardGPS + "_10Miles"

# Use try-except and execute GP tools
try: 
    if arcpy.CheckProduct("arcinfo") == "Available" or arcpy.CheckProduct("arcinfo") == "AlreadyInitialized":
        # generate a buffer of 10 Miles around the park
        arcpy.analysis.Buffer(input_park, input_park_Buff, "10 Miles")
        
        # Clip the input file or feature class by 10 mile buffer
        arcpy.analysis.Clip(input_onboardGPS, input_park_Buff, outFc)
        # arcpy.analysis.Clip("onboardGPS_TAT_JSONToFeature", os.path.join("D:/DENA_ADS-B_OnBoard/DENA/DENA.gdb", "Buffer_DENA_10Miles"), "onboardGPS_TAT_JSONToFeature_10Miles")

        # Onboard GPS file - use the one clipped by buffer 10 miles of the park
        # inFc = "D:/DENA_ADS-B_OnBoard/DENA/Onboard_K2A.gdb/onboardGPS_K2A_JSONToFeature_10Miles"

        # get the unique values of N-Number in GPS Onboard feature class
        with arcpy.da.SearchCursor(outFc, ["registration"]) as cursor:
            myValues = sorted({row[0] for row in cursor})

        # myValues
        # type(myValues)

        # print("The unique registration or N-Numbers are {0}".format(myValues))
        arcpy.AddMessage("The unique registration or N-Numbers are {0}".format(myValues))

        # get the unique of two values - departure_datetime and landing_datetime
        # with arcpy.da.SearchCursor(inFC, [["departure_datetime"], ["landing_datetime"]]) as cursor:
        #     myValues1 = sorted({(row[0], row[1]) for row in cursor})

        # get the unique of three values - departure_datetime, landing_datetime and registration (N-Number)
        with arcpy.da.SearchCursor(outFc, [["departure_datetime"], ["landing_datetime"], ["registration"]]) as cursor:
            myValues1 = sorted({(row[0], row[1], row[2]) for row in cursor})

        # myValues1
        # len(myValues1)
        # Note that the len of myValues1 is larger than the above len of myValues, because the two registration or flights could have simultaneous departure and landing time! Or one registration number have multiple departure and landing time.  
        # type(myValues1)

        arcpy.AddMessage("The total number of flights is {0}".format(len(myValues1)))
        
        # ADS-B file does not have N in front of their registration, so create a new field for N_Number
        arcpy.AddField_management(input_ADSB, "N_Number1", "TEXT")
        
        # Attach N to each N_NUMBER of ADS-B file, but there are <null> values in N_NUMBER, so apply if-else
        with arcpy.da.UpdateCursor(input_ADSB, ['N_NUMBER', 'N_Number1']) as cursor:
            for row in cursor:
                if row[0] != None:
                    row[1] = "N" + row[0]
                else:
                    row[1] = None
                cursor.updateRow(row)
                
        # apply loop to select feature classes of those N_Number from the ADS-B merged waypoints file
        for i in range(len(myValues)):
            where = '"N_Number1" = ' + "'" + myValues[i] + "'"
            arcpy.conversion.ExportFeatures(input_ADSB, input_ADSB + "_"+ myValues[i], where)
            
        # similarly, seperate the Onboard feature class based on their registration
        for i in range(len(myValues)):
            where = '"registration" = ' + "'" + myValues[i] + "'"
            arcpy.conversion.ExportFeatures(outFc, outFc + "_" + myValues[i], where)

    else:
        arcpy.AddWarning("Your ArcGIS licensing level isn't sufficient!")

except arcpy.ExecuteError:
    arcpy.AddError("A GP tool has encountered an error.")

finally:
    arcpy.AddMessage("Script ran to completion, Onboard GPS waypoints clipped within 10-mile boundary, aircraft registration or N-Numbers listed, total flights calculated in Onboard GPS feature class, feature classes generated based on the registration or N-Numbers.")
