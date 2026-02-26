# -*- coding: utf-8 -*-
# @file Update_FDX_in_Sheet.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import os, sys
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass

logger_path = os.path.abspath(os.path.join(os.getcwd(), r"..\..\Platform\Classe\Scripts\Control"))
sys.path.append(logger_path)
from logging_config import logger

list_found_triggers=[]

def Get_Linux_Username():
    """ """
    linux_username=""
    current_dir=os.getcwd()
    try:
        os.chdir(r"//wsl$/Ubuntu-18.04/home")
        obj_list = os.listdir(r"//wsl$/Ubuntu-18.04/home")
        list_dir = []
        list_files = []
        for elmnt in obj_list:
            if os.path.isdir(elmnt) == True:
                list_dir.append(elmnt)
            else:
                list_files.append(elmnt)
        linux_username = list_dir[0]
        os.chdir(current_dir)
    except Exception as e:
        logger.error(f"Failed to get Linux username: {e}")
    return linux_username
def Generate_List_Of_Files(folder):
    """
    

    Args:
      folder: 

    Returns:

    """

    listOfFile = os.listdir(folder)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(folder, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + Generate_List_Of_Files(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles
def Read_YML_File(path):
    """
    

    Args:
      path: 

    Returns:

    """
    list_rows_from_YML_file=[]
    list_rows_from_YML_file.clear()
    f1 = open(path, "r")
    for x in f1:
        list_rows_from_YML_file.append(x)
    f1.close()
    return list_rows_from_YML_file

def Identify_Already_Defined_Items(l1,l2):
    """
    

    Args:
      l1: 
      l2: 

    Returns:

    """
    already_defined_list=[]
    already_defined_list.clear()
    #print(l1[0])
    #print(l2[0])
    for el1 in l1:
        for el2 in l2:
            try:
                if (el1[0].find(el2[0])>=0):
                    already_defined_list.append(el2[0])
            except:
                pass
    return already_defined_list
def Process_XLS_Sheet(excel_filename):
    """
    

    Args:
      excel_filename: 

    Returns:

    """
    fdx_in_df=pd.read_excel(open(excel_filename, 'rb'), sheet_name='fdx_in')
    triggers_test_catalog_df = pd.read_excel(open(excel_filename, 'rb'), sheet_name='fdxTriggersTestCatalog')

    #convert dataframes to lists for easier C-like handling :)
    list_fdx_in=fdx_in_df.values.tolist()
    list_triggers_test_catalog = triggers_test_catalog_df.values.tolist()
    list_of_already_defined_items=Identify_Already_Defined_Items(list_fdx_in,list_triggers_test_catalog)

    for el_test_catalog in list_triggers_test_catalog:
        if (el_test_catalog[0] not in list_of_already_defined_items):
            list_fdx_in.append([el_test_catalog[0],"","","","","","","","","","","","","","","","","","","","","","","","","","",""])
            list_fdx_in.append(["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]) #empty row
        else:
            logger.info(f"!!!DUPLICATE ITEM = {el_test_catalog[0]}")
    #print(list_fdx_in)

    new_fdx_in = pd.DataFrame(list_fdx_in,
                                  columns=[
                                      "Name", \
                                      "Message", \
                                      "Multiplexing/Group", \
                                      "Startbit", \
                                      "Length [Bit]", \
                                      "Byte Order", \
                                      "Value Type", \
                                      "Initial Value", \
                                      "Factor", \
                                      "Offset", \
                                      "Minimum", \
                                      "Maximum", \
                                      "Unit", \
                                      "Value Table", \
                                      "Comment", \
                                      "Message ID", \
                                      "Cycle Time [ms]", \
                                      "texttable", \
                                      "texttable values", \
                                      "max_value", \
                                      "dlc", \
                                      "variant", \
                                      "sender", \
                                      "direction", \
                                      "texttable mapping", \
                                      "conversion", \
                                      "array name", \
                                      "data_type"])

    def color(row):
        """
        

        Args:
          row: 

        Returns:

        """
        if row.isnull().values.any() == True:
            return ['background-color: green'] * len(row)
        else:
            return ['background-color: red'] * len(row)
        return [''] * len(row)

    new_fdx_in=new_fdx_in.style.apply(color, axis=1)

    with pd.ExcelWriter(excel_filename, mode='a', if_sheet_exists="replace", engine='openpyxl') as writer:
        new_fdx_in.to_excel(writer, sheet_name='fdx_in', index=False)

#sample of triggers used in YML files
# triggers:
#   [
#   #############################  Environmental conditions #####################################################
#   # Ego vehicle driving with a velocity of 50kph
#   #############################  Ego Vehicle conditions #######################################################
#   # Precondition for Enabling AEB
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_isDriverSeatBeltPluggedIn": true}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_driverDoorStatus": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_mainSwitch": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_aebHmiSwitchStatus": true}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_ignitionState": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_prm_sr_TDaddyInterface_prm_sr_FctParam_sr_CCal_", "m_data__m_Lks__m_impl__m_data__m_lateralButtonEnabledConditionBypass": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_prm_sr_TDaddyInterface_prm_sr_FctParam_sr_CCal_", "m_data__m_Lks__m_impl__m_data__m_anyBoundariesReliableConditionBypass": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_prm_sr_TDaddyInterface_prm_sr_FctParam_sr_CCal_", "m_data__m_Lks__m_impl__m_data__m_bothBoundariesReliableConditionBypass": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_prm_sr_TDaddyInterface_prm_sr_FctParam_sr_CCal_", "m_data__m_Lks__m_impl__m_data__m_oneBoundaryReliableConditionBypass": 1}},
#     {"event": "time=0.00", "action": {"name": "default_controller/stimuli_Ods_sr_Fct_sr_PreProc", "m_vehicleInfo__m_driverActivityLateral__m_rateOfChangeOfSteeringWheelAngle__m_value": 200.0}}, #above threshold
#   #############################  Test Steps #######################################################
#
#
#     # Stop simulation
#     {"event": "time=6.0", "action": {"name": "stop"}}
#   ]

#global variables
def get_triggers():
    """ """
    linux_username=Get_Linux_Username()
    f_list=Generate_List_Of_Files(r"//wsl$/Ubuntu-18.04/home/"+linux_username+"/workspace/ods_cloe_tests/cloe_tests/")
    return f_list
    

def main_sequence(FDX_database):
    """
    

    Args:
      FDX_database: 

    Returns:

    """
    try:
        Process_XLS_Sheet(FDX_database)
        logger.info("FDX_in successfully updated")
        return True
    except Exception as e:
        logger.error(f"Failure reason {e}")
        return False

if __name__ == "__main__":
    main_sequence()