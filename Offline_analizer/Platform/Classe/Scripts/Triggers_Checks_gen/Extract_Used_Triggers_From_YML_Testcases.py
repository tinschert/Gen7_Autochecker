# -*- coding: utf-8 -*-
# @file Extract_Used_Triggers_From_YML_Testcases.py
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
import tkinter
from tkinter import filedialog

logger_path = os.path.abspath(os.path.join(os.getcwd(), r"..\..\Platform\Classe\Scripts\Control"))
sys.path.append(logger_path)
from logging_config import logger

list_found_triggers=[]

def Folder_Browser():
    """ """
    # initiate tinker and hide window
    main_win = tkinter.Tk()
    main_win.withdraw()

    main_win.lift()
    main_win.focus_force()

    # open file selector

    main_win.sourceFile = filedialog.askdirectory(parent=main_win, initialdir="/",
                                                     title='SELECT ODS CLOE TESTS FOLDER')
    # close window after selection
    main_win.destroy()
    folderPath = main_win.sourceFile
    return folderPath

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

def Save_To_Excel(excel_filename):
    """
    

    Args:
      excel_filename: 

    Returns:

    """
    # save to EXCEL
    # excel_filename = r'D:\ADAS_HIL\CustomerPrj\FDX\FDX_Database.xlsx'
    triggers_names = pd.DataFrame(list_found_triggers,columns=["Trigger Name", "Trigger NameSpace"])
    triggers_names=triggers_names.drop_duplicates()
    logger.info(f"Total number of used triggers found in YML files (UNIQUE) = {len(triggers_names)}")
    #writer = pd.ExcelWriter('FDX_Database_triggers_catalog_out2.xlsx', engine='xlsxwriter')
    #triggers_names.to_excel(writer, sheet_name='fdxTriggersTestCatalog')
    #writer.save()
    with pd.ExcelWriter(excel_filename, mode='a',if_sheet_exists="replace",engine='openpyxl') as writer:
        triggers_names.to_excel(writer, sheet_name='fdxTriggersTestCatalog', index=False)
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

    f_list_path = Folder_Browser()
    # Added if we press "cancel" on the tkinter folder browser, for error not to be raised
    if f_list_path == "":
        f_list = []
        return f_list
    else:
        f_list = Generate_List_Of_Files(f_list_path)
        return f_list

def main_sequence(FDX_database):
    """
    

    Args:
      FDX_database: 

    Returns:

    """
    # this parameter was added because we needed a third option in case we press the "Cancel" button on the tkinter folder browser
    main_seq_result = 0
    try:
        f_list = get_triggers()
        # Added if we press "cancel" on the tkinter folder browser, for error not to be raised
        if f_list == []:
            main_seq_result = 2
            return main_seq_result
        else:
            list_found_triggers.clear()
            for current_yml_file in f_list:
                logger.info(f"current_yml_file = {current_yml_file}")
                current_file_lines=Read_YML_File(current_yml_file)
                for line in current_file_lines:
                    if (line.find("#")>=0):
                        pass  #do nothing if line is commented out
                    else:
                        if (line.find('{"event": "')>=0):
                            idx_trigger_name_start=line.find('{"name":')+len('{"name":')+2
                            temp_str=line[idx_trigger_name_start:]
                            idx2=temp_str.find('",')
                            trigger_found_namespace=temp_str[:idx2]
                            trigger_found_name=temp_str[idx2+1:]
                            idx3=trigger_found_name.find('"')
                            trigger_found_name = trigger_found_name[idx3 + 1:]
                            idx4 = trigger_found_name.find('"')
                            trigger_found_name = trigger_found_name[:idx4]
                            trigger_found_name = trigger_found_name.replace("[","_")
                            trigger_found_name = trigger_found_name.replace("]","_")
                            trigger_found_name = trigger_found_name.replace(".","__")
                            #print("!!!DEBUG!!! trigger namespace = ",trigger_found_namespace)
                            #print("!!!DEBUG!!! trigger name      = ", trigger_found_name)
                            if (trigger_found_namespace.find('stop"}}')!=0):
                                if (trigger_found_name.find('action')!=0):
                                    if (trigger_found_namespace.find('default_controller/hmi') != 0):   #this is an obsolete namespace but still some .yml tests are not updated
                                        list_found_triggers.append([trigger_found_name,trigger_found_namespace])
            #for el in list_found_triggers:
            #    print("trigger name      = ",el[0])
            #    print("trigger namespace = ", el[1])
            logger.info(f"Total number of YML files processed                       = {len(f_list)}")
            logger.info(f"Total number of used triggers found in YML files          = {len(list_found_triggers)}")

            Save_To_Excel(FDX_database)
            main_seq_result = 1
            return main_seq_result
    except Exception as e:
        main_seq_result = 0
        logger.error(f"Failure reason {e}")
        return main_seq_result

if __name__ == "__main__":
    main_sequence()