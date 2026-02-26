# -*- coding: utf-8 -*-
# @file Generate_Triggers_XLS_table.py
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


import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
#import easygui
import simplejson
from openpyxl import load_workbook
import sys, os
from win32com.client import Dispatch
import pythoncom


#Jason_file1 = r'..\..\Database\data_dump.json'
#Jason_file1 = easygui.fileopenbox("Select the .json (json_dump file from controller binding team) : ")
from Control.logging_config import logger

to_excel_list = []
to_excel_list.clear()

def Read_Jason_File(path):
    """
    

    Args:
      path: 

    Returns:

    """
    f1 = open(path, "r")
    read_json_dict=simplejson.load(f1)
    f1.close()
    return read_json_dict

def Save_To_Excel(path_to_FDX):
    """
    

    Args:
      path_to_FDX: 

    Returns:

    """
    # save to EXCEL
    triggers_names = pd.DataFrame(to_excel_list,
                                  columns=[
    "Name",\
    "group",\
    "pdu",\
    "Message",\
    "Multiplexing/Group",\
    "Startbit",\
    "Length [Bit]",\
    "Byte Order",\
    "Value Type",\
    "Initial Value",\
    "Factor",\
    "Offset",\
    "Minimum",\
    "Maximum",\
    "Unit",\
    "Value Table",\
    "Comment",\
    "Message ID",\
    "Cycle Time [ms]",\
    "texttable",\
    "texttable values",\
    "max_value",\
    "dlc",\
    "variant",\
    "sender",\
    "direction",\
    "texttable mapping",\
    "conversion",\
    "array name",\
    "data_type"])

    #filename = r'..\..\..\..\CustomerPrj\FDX\FDX_Database.xlsx'

    with pd.ExcelWriter(path_to_FDX, mode='a',if_sheet_exists="replace",engine='openpyxl') as writer:
        triggers_names.to_excel(writer, sheet_name='fdxTriggersDatabase', index=False)

    try:
        pythoncom.CoInitialize()
        xlApp = Dispatch("Excel.Application")
        xlApp.Visible = False
        xlBook = xlApp.Workbooks.Open(path_to_FDX)
        xlBook.Save()
        xlBook.Close()
        xlApp.Quit()
        logger.info(f"You changes have been successfully saved into {path_to_FDX}.")
    except Exception as exp:
        logger.error(f"Failed to save Excel: {exp}")
        logger.error(f"Please open {path_to_FDX} with Excel and save it manually.")

def Reduce_Triggers_List_Name(orig_name):
    """
    

    Args:
      orig_name: 

    Returns:

    """
    temp_str=orig_name
    #remove prefixes
    temp_str = temp_str.replace("m_data_m_Lss_m_impl_m_data_","")
    temp_str = temp_str.replace("m_data_m_LongComfDriverInputProvider_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_LksCondition_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_Lks_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_Hf_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_Common_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_Alc_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_AccStateMachine_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_Aeb_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_data_m_AccControlUnit_m_impl_m_data_", "")
    temp_str = temp_str.replace("m_mapInfo_", "")
    temp_str = temp_str.replace("m_radarObjects_", "")
    temp_str = temp_str.replace("m_videoLines_", "")
    temp_str = temp_str.replace("m_vehicleInfo_", "")
    temp_str = temp_str.replace("__m_value", "")
    temp_str = temp_str.replace("_m_value", "")
    return temp_str

def main_sequence(FDX_database,json_database):
    """
    

    Args:
      FDX_database: 
      json_database: 

    Returns:

    """
    try:
        json_dict1 = Read_Jason_File(json_database)

        #Add the json dump file provided by Controller Binding team
        for publishers_el_key,publishers_el_value in json_dict1["publishers"].items():
            #current_message=publishers_el_key
            current_group=publishers_el_value['group']
            signals_list=publishers_el_value['signals']
            for signals_el in signals_list:
                Direction=json_dict1["publishers"][publishers_el_key]["direction"]
                Name = "FDX_"+Direction+"_"+signals_el.replace("%%","__")#not sure if we have to do this (idea is names on cloe side have to be equal to canoe side)
                Name=Name.replace(".","__")#not sure if we have to do this (idea is names on cloe side have to be equal to canoe side)
                Name = Name.replace("[", "_")#not sure if we have to do this (idea is names on cloe side have to be equal to canoe side)
                Name = Name.replace("]", "_")#not sure if we have to do this (idea is names on cloe side have to be equal to canoe side)
                #Name=Reduce_Triggers_List_Name(Name) #not sure if we have to do this (idea is names on cloe side have to be equal to canoe side)
                Message="FDX_"+Direction+"_"+current_group          #+"(TestTrigger)"

                if 'fdx_groupid' in json_dict1["publishers"][publishers_el_key].keys():
                    Group_ID = json_dict1["publishers"][publishers_el_key]["fdx_groupid"]
                else:
                    logger.error(f"No such key for element : {json_dict1['publishers'][publishers_el_key]}")
                    print(f"No such key for element : ", json_dict1["publishers"][publishers_el_key])




                    #print(json_dict1["groups"][current_group]["signals"][signals_el]["compu_method"])
                Comp_Method=json_dict1["groups"][current_group]["signals"][signals_el]["compu_method"]
                Multiplexing_Group=Group_ID
                Startbit=""
                Length=json_dict1["groups"][current_group]["signals"][signals_el]["bit_size"]
                Byte_Order=""

                if (json_dict1["groups"][current_group]["signals"][signals_el]["signed"]==True):
                    Value_Type="Signed"
                else:
                    Value_Type = "Unsigned"
                Initial_Value=json_dict1["groups"][current_group]["signals"][signals_el]["initial_value"]

                try:
                    #for some computation methods it is a list, for some it is a single entry
                    #try to achieve the single entry first
                    Factor=json_dict1["compu_methods"][Comp_Method]["scale"]
                except:
                    #if it is a list take the first entry (we don't know which to use)
                    Factor = json_dict1["compu_methods"][Comp_Method][0]["scale"]
                try:
                    #for some computation methods it is a list, for some it is a single entry
                    #try to achieve the single entry first
                    Offset=json_dict1["compu_methods"][Comp_Method]["offset"]
                except:
                    #if it is a list take the first entry (we don't know which to use)
                    Offset = json_dict1["compu_methods"][Comp_Method][0]["offset"]

                try:
                    #for some computation methods it is a list, for some it is a single entry
                    #try to achieve the single entry first
                    Minimum=json_dict1["compu_methods"][Comp_Method]["lower_limit"]
                except:
                    #if it is a list take the first entry (we don't know which to use)
                    Minimum = json_dict1["compu_methods"][Comp_Method][0]["lower_limit"]

                try:
                    #for some computation methods it is a list, for some it is a single entry
                    #try to achieve the single entry first
                    Maximum=json_dict1["compu_methods"][Comp_Method]["upper_limit"]
                except:
                    #if it is a list take the first entry (we don't know which to use)
                    Maximum = json_dict1["compu_methods"][Comp_Method][0]["upper_limit"]

                group=""
                pdu=""
                Unit=""
                Value_Table=""
                Comment=""
                Message_ID=""
                Cycle_Time=""
                texttable=""
                texttable_values=""
                max_value=65535
                dlc=""
                variant=""
                datatype=json_dict1["groups"][current_group]["signals"][signals_el]["datatype"]
                array_size = json_dict1["groups"][current_group]["signals"][signals_el]["array_size"]
                if (datatype.find("float")>=0):
                    datatype="double"
                if (array_size==0):
                    to_excel_list.append([Name,group,pdu,Message,Multiplexing_Group,Startbit,Length,Byte_Order,Value_Type,Initial_Value,Factor,Offset,Minimum,Maximum,Unit,Value_Table,Comment,Message_ID,Cycle_Time,texttable,texttable_values,max_value,dlc,variant,"Cloe","","","","",datatype])
                else:
                    for p in range(array_size):
                        to_excel_list.append([Name+"__"+str(p),group,pdu,Message, Multiplexing_Group, Startbit, Length, Byte_Order, Value_Type, Initial_Value,Factor, Offset, Minimum, Maximum, Unit, Value_Table, Comment, Message_ID, Cycle_Time,texttable, texttable_values, max_value, dlc, variant, "Cloe", "", "", "", "", datatype])




        Save_To_Excel(FDX_database)
        to_excel_list.clear()
        logger.info("Successfully created fdxTriggersDatabase triggers")
        return True
    except Exception as e:
        logger.error(f"Failure reason {e}")
        return False




if __name__ == "__main__":
    main_sequence()