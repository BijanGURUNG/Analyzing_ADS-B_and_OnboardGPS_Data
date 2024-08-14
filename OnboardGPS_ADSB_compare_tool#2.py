# -*- coding: utf-8 -*-
"""
File Name: ADSB_OnboardGPS_tool#2.py
Description: Compare the overflights with same registration or N-Number from ADS-B and Onboard GPS feature classes and select the matching overflights from the ADS-B feature class
Date created: 07/03/2024
"""

__author__ = "Bijan Gurung"
__version__ = "1.0"
__email__ = "bijangurung@ksu.edu"
__status__ = "Production"

# Import acrpy module and allow overwrites
import arcpy, os, datetime, pandas as pd, time, numpy as np
arcpy.env.overwriteOutput = True

# # set the scratch folder as the workspace, so the original feature classes remain intact
# inWorkspace = "D:/DENA_ADS-B_OnBoard/DENA/Onboard_K2A.gdb"

# user-defined parameters
inWorkspace = arcpy.GetParameterAsText(0)               # gdb file containing the OnboardGPS and ADSB feature class files
inFc = arcpy.GetParameterAsText(1)                      # OnboardGPS feature class of a particular registration or N-Number obtained from tool#1
inFc1 = arcpy.GetParameterAsText(2)                     # ADS-B feature class of a particular registration or N-Number obtained from tool#1

# set the environment
arcpy.env.workspace = inWorkspace

# set local variables 
# inFc = "onboardGPS_K2A_JSONToFeature_10Miles_N1292F"
# Work with one particular N_Number or registration represented by one feature class

# Use try-except and execute GP tools
try: 
    if arcpy.CheckProduct("arcinfo") == "Available" or arcpy.CheckProduct("arcinfo") == "AlreadyInitialized":
             
        # Add a field "departure_datetime_1" for date in the OnboardGPS feature class
        arcpy.AddField_management(inFc, "departure_datetime_1", "Date")
        
        # Copy the text format in "departure_datetime" to the new field in date format 
        with arcpy.da.UpdateCursor(inFc, ['departure_datetime', 'departure_datetime_1']) as cursor:
            dt_format1 = "%Y-%m-%d %H:%M:%S"
            for row in cursor: 
                txt1 = row[0][0:10]
                txt2 = row[0][11:]
                row[1] = datetime.datetime.strptime(txt1 + " " + txt2, dt_format1)
                # row[1] = row[0]
                cursor.updateRow(row)
        
        # Add a field "landing_datetime" for date in the OnboardGPS feature class
        arcpy.AddField_management(inFc, "landing_datetime_1", "Date")
        
        # Copy the text in "landing_datetime" to date in "landing_datetime_1"
        with arcpy.da.UpdateCursor(inFc, ['landing_datetime', 'landing_datetime_1']) as cursor:
            dt_format1 = "%Y-%m-%d %H:%M:%S"
            for row in cursor: 
                txt1 = row[0][0:10]
                txt2 = row[0][11:]
                row[1] = datetime.datetime.strptime(txt1 + " " + txt2, dt_format1)
                # row[1] = row[0]
                cursor.updateRow(row)
        
        # Find the numbers and unique numbers of departure_datetime_1 and landing_datetime_1
        # inFc_1 = "onboardGPS_K2A_JSONToFeature_10Miles_N1292F"
        with arcpy.da.SearchCursor(inFc, [["departure_datetime_1"], ["landing_datetime_1"]]) as cursor:
            uniqDeptLand = sorted({(row[0], row[1]) for row in cursor})
        
        # len(uniqDeptLand)
        # uniqDeptLand[0]
        arcpy.AddMessage("The OnbooardGPS feature class has {0} overflights".format(len(uniqDeptLand)))
        
        with arcpy.da.SearchCursor(inFc, [["departure_datetime_1"], ["landing_datetime_1"]]) as cursor:
            DepartLand = [(row[0], row[1]) for row in cursor]
        
        # len(DepartLand)
        arcpy.AddMessage("The OnbooardGPS feature class has {0} waypoints".format(len(DepartLand)))
        # DepartLand[0:17]
        # DepartLand[-4]
        # DepartLand.count((datetime.datetime(2021, 5, 14, 13, 17, 45), datetime.datetime(2021, 5, 14, 14, 30, 30)))
        
        # DepartLand.count((datetime.datetime(2023, 2, 26, 10, 25, 30), datetime.datetime(2023, 2, 26, 10, 49, 15, 1)))
        
        # for i in DepartLand:
        #     for j in i:
        #         i.count(i[j])
        
        # type(DepartLand)
        # DepartLand[0]
        # DepartLand.count(DepartLand[0])
        
        # # See the frequency of each unique item in DepartLand, temporary object
        # for i in DepartLand:
        #     print(DepartLand.count(i[0:2]))
        #     # print(i)
        
        # Create a list of frequency of the values in "DepartLand" field
        freq = []
        for i in DepartLand:
            freq.append(DepartLand.count(i[0:2]))
            # print(DepartLand.count(i))
        # len(freq)
        # type(freq)
        # freq[0:17]
        # freq[-10:-1]
        
        # Add another field "freq1"
        arcpy.AddField_management(inFc, "freq", "SHORT")
        
        # Add the values from list "freq" to the feature class and its field "freq1"
        pointer = 0
        with arcpy.da.UpdateCursor(inFc, ["freq"]) as cursor:
            for row in cursor:
                row[0] = freq[pointer]
                pointer += 1
                cursor.updateRow(row)
        
        
        # Select the rows with frequency value > 2 and copy to new feature class
        # where = '"freq1" > ' + "'" + str(2) + "'"
        outFc = inFc + "_freq"
        expression = arcpy.AddFieldDelimiters(inFc, "freq") + " > 2"
        arcpy.conversion.ExportFeatures(inFc, outFc, expression)
        
        # Check the number of unique departure_datetime_1 and landing_datetime_1 in the new feature class of N2YV
        # inFc_1_freq = "onboardGPS_K2A_N1292F_freq"
        with arcpy.da.SearchCursor(outFc, [["departure_datetime_1"], ["landing_datetime_1"]]) as cursor:
            uniqDeptLand1 = sorted({(row[0], row[1]) for row in cursor})
        
        len(uniqDeptLand1)
        arcpy.AddMessage("The OnbooardGPS feature class has {0} overflights after removing overflights with less than 3 waypoints".format(len(uniqDeptLand1)))
        # uniqDeptLand1[0:17]
        # uniqDeptLand1[0][1]
        
        # # Work on the ADS-B file
        # inFc1 = "DENA_MergedWaypoints_N1292F"
        
        # # Check the format of Date in the OnboardGPS file for N2YV filtered by frequency
        # startDate = uniqDeptLand1[0][0]
        # endDate = uniqDeptLand1[0][1]
        
        # # Check to see the condition works or not
        # where = "TIME BETWEEN DATE '{}' AND DATE '{}'".format(startDate, endDate)
        # arcpy.conversion.ExportFeatures(inFc1, inFc1 + "_1", where)
        
        # len(uniqDeptLand1[0])
        
        # Apply loop to consider all the unique departure_datetime_1 and landing_datetime_1
        # Waypoints from the ADS-B file for N2YV are selected
        # Those selected waypoints were merged in ArcGIS Pro using GP tool
        for i in range(len(uniqDeptLand1)):
            where = "TIME BETWEEN DATE '{}' AND DATE '{}'".format(uniqDeptLand1[i][0], uniqDeptLand1[i][1])
            arcpy.conversion.ExportFeatures(inFc1, inFc1 + "_temp_"+ str(i), where)
        
        # Earlier, feature classes were merged using a GP tool
        # Now, we are using code
        pointList = []
        for fc in arcpy.ListFeatureClasses("*temp*"):
            pointList.append(fc)
        
        outFc1 = inFc1 + "_merge"
        arcpy.management.Merge(pointList, outFc1)
        
        # Check the number of flights in the merged ADS-B N2YV file
        # outFc_2_merge = "DENA_MergedWaypoints_N1292F_merge"
        with arcpy.da.SearchCursor(outFc1, ["flight_id"]) as cursor:
            uniqDeptLand2 = sorted({row[0] for row in cursor})
        
        # len(uniqDeptLand2)
        arcpy.AddMessage("The screened ADS-B feature class has {0} overflights".format(len(uniqDeptLand2)))
        # Delete the *temp* files
        delList = arcpy.ListFeatureClasses("*temp*")
        for i in delList:
            arcpy.management.Delete(i)
        
    else:
        arcpy.AddWarning("Your ArcGIS licensing level isn't sufficient!")

except arcpy.ExecuteError:
    arcpy.AddError("A GP tool has encountered an error.")

finally:
    arcpy.AddMessage("Script ran to completion, datetime fields created for departure time and landing time in OnboardGPS feature class, overflights with less than 3 waypoints removed from OnboardGPS feature class, departure time and landing time were applied to select the corresponding waypoints and overflights from ADS-B feature class, a new OnboardGPS feature class generated, and a new ADS-B feature class generated for visual comparison.")
        

# Note: After selecting the waypoints from the particular N-Number in ADS-B Merged Waypoints, use these same points (especially their date or day) to select the corresponding waypoints from Onboard GPS. Because, we do not need all of the waypoints shown in Onboard GPS.