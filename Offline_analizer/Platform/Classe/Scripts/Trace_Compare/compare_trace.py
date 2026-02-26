# -*- coding: utf-8 -*-
# @file compare_trace.py
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


from asammdf import MDF
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import re
from collections import Counter
import os,sys
try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import filter_msg_pattern_list, filter_sig_pattern_list
    filter_list = filter_msg_pattern_list + filter_sig_pattern_list
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import filter_msg_pattern_list, filter_sig_pattern_list
    filter_list = filter_msg_pattern_list + filter_sig_pattern_list
except:
    # default list if script fails to extract list from pattern matching
    filter_list = ['.*_*AliveCounter.*', '.*BlockCounter|BlockCtr.*', '.*_*CheckSum.*', '.*_*CRC.*','.*_*(?:AliveCtr|AliveCnt).*','.*sync|Sync.*']

script_path = os.path.dirname(os.path.abspath(__file__))
excel_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'

hil_key_list = []  # **
common_sigs = []  # **
dict_enum_values = {}

def filterSignals(sig_list):
    """
    

    Args:
      sig_list: 

    Returns:

    """
    logger.info("Start Filtering...")
    if filter_list == []:
        return sig_list
    filtered_df = pd.DataFrame(sig_list, columns=["signals"])
    for pattern in filter_list:
        filtered_df = filtered_df[filtered_df["signals"].str.contains(pattern, regex=True) == False]

    filtered_sig_list = list(filtered_df["signals"].values)
    logger.info("Done Filtering")
    return filtered_sig_list

# def checkDisplayName(dis_name):
#     if dis_name != {} and "message_name" in dis_name.values():
#         try:
#             temp_dict = dict(zip(dis_name.values(), dis_name.keys()))
#             return temp_dict["message_name"]
#         except:
#             return False
#     return False

def processTexttable(value):
    """
    

    Args:
      value: 

    Returns:

    """
    dict_result={}
    temp = value.replace("LogicalValue:","").strip().split("\n")
    for i in temp:
        search_obj = re.search(r"^(\d*)\s*(.*)", i.strip())
        if search_obj!=None:
            dict_result[str(search_obj.group(1))]=str(search_obj.group(2)).strip()
    return dict_result

def extractEnumValues():
    """ """
    temp_dict={}
    df_sysvar = pd.read_excel(excel_path, sheet_name="SysVarDatabase", usecols=["Name","Message","texttable values"])
    df_sysvar = df_sysvar.fillna("")
    for i,row in df_sysvar.iterrows():
        if row["texttable values"].strip() != "":
            key = row["Message"].strip() + "::" + row["Name"].strip()
            if key not in temp_dict.keys():
                temp_dict[key] = processTexttable(row["texttable values"])
    return temp_dict

def extractFiles(hil_file, veh_file):
    """
    

    Args:
      hil_file: 
      veh_file: 

    Returns:

    """
    global hil_key_list, common_sigs, dict_enum_values

    dict_hil_data = {}
    dict_veh_data = {}
    logger.info("Start Importing Files...")
    mdf_hil = MDF(hil_file)
    mdf_vehicle = MDF(veh_file)
    logger.info("Done Importing Files")
    logger.info("Start Processing Files...")
    try:
        dict_enum_values = extractEnumValues()
    except:
        dict_enum_values = {}

    # HIL data
    for sig in mdf_hil.iter_channels():
        temp = sig.name.split("::")
        s_name = temp[-1]
        if "_rv" in s_name.lower():
            s_name = s_name[:-3]
        try:
            key = temp[-2] + "::" + s_name
        except IndexError as e:
            logger.error(f"HIL MF4 file is not signal logged -> {e}")
            raise Exception("HIL MF4 file is not signal logged -> {e}")

        if key not in dict_hil_data.keys():
            temp_hil_mdf = MDF()
            temp_hil_mdf.append(sig)
            dict_hil_data[key] = temp_hil_mdf.to_dataframe()
            temp_hil_mdf.close()

            #hil_key_list.append(key)
    hil_key_list = list(dict_hil_data.keys())
    hil_key_list = filterSignals(hil_key_list)

    # Hil_data_dict = {k:v for k,v in dict_hil_data.items() if k in hil_key_list}

    # VEH data
    for sig in mdf_vehicle.iter_channels():
        temp = sig.name.split("::")
        s_name = temp[-1]
        if "_rv" in s_name.lower():
            s_name = s_name[:-3]
        try:
            key = temp[-2] + "::" + s_name
        except IndexError as e:
            logger.error(f"VEH MF4 file is not signal logged -> {e}")
            raise Exception(f"VEH MF4 file is not signal logged -> {e}")

        if (key not in dict_veh_data.keys()) and (key in hil_key_list):
            temp_veh_mdf = MDF()
            temp_veh_mdf.append(sig)
            dict_veh_data[key] = temp_veh_mdf.to_dataframe()
            temp_veh_mdf.close()

    common_sigs = list(dict_veh_data.keys())
    logger.info("Done Processing Files")
    return dict_hil_data,dict_veh_data



def convertToPhysical(key,value):
    """
    

    Args:
      key: 
      value: 

    Returns:

    """
    try:
        phy_value_dict = dict_enum_values[key]

        if (type(value)!=list) and (str(int(value)) in phy_value_dict.keys()):
            return phy_value_dict[str(int(value))]
        elif type(value) == list and len(value)!=0:
            new_value_list = []
            for j in value:
                if str(int(j)) in phy_value_dict.keys():
                    new_value_list.append(phy_value_dict[str(int(j))])
                else:
                    return value
            return new_value_list
        return value
    except:
        return value

def most_repeated(value_list):
    """
    

    Args:
      value_list: 

    Returns:

    """
    if len(value_list)==0:
        return "-"
    cut_off_percent = int(len(value_list)*0.4)
    countr = Counter(value_list)
    result = countr.most_common(2)
    #if (result[0][1] == result[1][1])  -> to check if count is same for 2 values
    if (result[0][1] >= cut_off_percent):
        try:
            return result[0][0].decode()
        except:
            return result[0][0]
    else:
        return list(set(value_list))



def extract_value(df):
    """
    

    Args:
      df: 

    Returns:

    """
    if len(df) == 0:
        return "-"
    values = set(df.iloc[:, 0])
    length = len(values)
    if length == 1:
        try:
            return list(values)[0].decode()
        except:
            return list(values)[0]
    else:
        return most_repeated(list(df.iloc[:, 0]))


def processOrValues(hil_value,veh_value):  #handle "||" cases
    hil_value = str(hil_value).split("II")
    veh_value = str(veh_value).split("II")
    temp = [i.strip() for i in hil_value if i.strip() in veh_value]

    if len(set(temp)) == 1:
    """
    

    Args:
      hil_value: 
      veh_value):  #handle "||" caseshil_value:  (Default value = str(hil_value).split("II")veh_value = str(veh_value).split("II")temp = [i.strip() for i in hil_value if i.strip() in veh_value]if len(set(temp))

    Returns:

    """
        return True
    return False

def compareTrace(dict_hil_data, dict_veh_data, interval):
    """
    

    Args:
      dict_hil_data: 
      dict_veh_data: 
      interval: 

    Returns:

    """
    logger.info("Start Comparing...")
    final_List = []

    count = 0

    for key in common_sigs:
        temp = key.split("::")
        if len(temp) == 2:
            s_name = temp[-1]
            m_name = temp[-2]
        elif len(temp) == 1:
            s_name = temp[0]
            m_name = ""
        if "_rv" in s_name.lower():
            s_name = s_name[:-3]
        result_row_values = [m_name, s_name]
        count += 1
        df_hil = dict_hil_data[key]
        df_veh = dict_veh_data[key]

        df_hil_interval = df_hil[interval[0]:interval[1]]
        df_veh_interval = df_veh[interval[0]:interval[1]]

        hil_value = extract_value(df_hil_interval)
        veh_value = extract_value(df_veh_interval)


        if key in dict_enum_values.keys():
            hil_value = convertToPhysical(key,hil_value)
            veh_value = convertToPhysical(key,veh_value)

        result_row_values.append(hil_value)
        result_row_values.append(veh_value)

        if str(hil_value).strip().endswith(".0"):
            hil_value = str(hil_value).strip().replace(".0","").lower()
        if str(veh_value).strip().endswith(".0"):
            veh_value = str(veh_value).strip().replace(".0","").lower()

        if (type(hil_value) == str) or (type(hil_value)==str):
            hil_value = str(hil_value).replace(" ","").lower()
            veh_value = str(veh_value).replace(" ", "").lower()

        if hil_value == veh_value:
            result = "No Diff"
        elif hil_value == "-" or veh_value == "-":
            result = "empty"
        elif ("II" in str(hil_value)) or ("II" in str(veh_value)):
            result = "No Diff" if processOrValues(str(hil_value), str(veh_value)) else "Diff"
        elif type(hil_value) == type(veh_value) and type(hil_value) != list and hil_value != veh_value:
            result = "Diff"
        elif type(hil_value) != list and type(veh_value) != list:
            result = "Diff"
        else:
            result = "many values found"

        result_row_values.append(result)
        final_List.append(result_row_values)

    logger.info("Done Comparing")
    df = pd.DataFrame(final_List, columns=["Message", "Signal", "HIL_Trace", "Vehicle_Trace", "Result"])
    file_name = "Tool_results\\"+"Compare_Result_"+str(interval[0])+"_"+str(interval[1])+".xlsx"
    df.to_excel(file_name, index=False)
    logger.info(f"Result excel saved -> {file_name}")
    return file_name

def manualCompare(dict_hil_data, dict_veh_data,msg_name,sig_name):
    """
    

    Args:
      dict_hil_data: 
      dict_veh_data: 
      msg_name: 
      sig_name: 

    Returns:

    """
    logger.info(f"-----Start Manual compare-----")
    #print(dict_veh_data.keys())
    key=msg_name+"::"+sig_name
    #print(key)
    if (key in dict_veh_data.keys()) and (key in dict_hil_data.keys()):
        hil=pd.DataFrame(dict_hil_data[key])
        hil = hil.reset_index(level=0)
        hil.columns = ['HIL_TimeStamp',"HIl_Value"]
        #print(hil)
        veh=pd.DataFrame(dict_veh_data[key])
        veh = veh.reset_index(level=0)
        veh.columns = ['VEH_TimeStamp',"VEH_Value"]
        #temp_df=pd.concat([hil,veh],ignore_index=True,axis=1)
        temp_df = hil
        temp_df["VEH_TimeStamp"] = veh["VEH_TimeStamp"]
        temp_df["VEH_Value"] = veh["VEH_Value"]
        temp_df.fillna("")
        file_name = "Manual_results\\"+msg_name+"_"+sig_name+".xlsx"
        temp_df.to_excel(file_name,index=False)
        logger.info(f"Result excel saved -> {file_name}")
        return file_name

    else:
        if (key not in dict_veh_data.keys()):
            logger.error("Message::Signal not found in VEH trace file")
        else:
            logger.error("Message::Signal not found in HIL trace file")

