# -*- coding: utf-8 -*-
# @file fdx_to_hil_specific_json.py
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


import json
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import re
import sys, os

from Control.logging_config import logger

def extract_data_from_FDX_platform_database(database):
    """
    Create Dataframe from fdx_in sheet

    Args:
      database: 

    Returns:

    """
    #excel_filename = r"..\..\Classe\Classe_Database.xlsx"
    with open(database, 'rb') as f:
        fdx_in_df=pd.read_excel(f, sheet_name='fdx_in_pf')
        fdx_in_df = fdx_in_df.drop(["group","pdu"], axis=1)
        fdx_in_df = fdx_in_df.dropna(subset = ["Name"]) # Remove missing values.
        #only_signals = fdx_in_df[["Name"]]
        fdx_out_df=pd.read_excel(f, sheet_name='fdx_out_pf')
        fdx_out_df = fdx_out_df.drop(["group", "pdu"], axis=1)
        fdx_out_df = fdx_out_df.dropna(subset = ["Name"]) # Remove missing values.
        fdx_concat = pd.concat([fdx_in_df, fdx_out_df]) # Concatenate fdx_in and fdx_out
        fdx_concat.sort_values(by=['Message']) # Sort values in Message column
        # p = fdx_concat.Message.unique()
        # grouped = fdx_concat.groupby(fdx_concat.Message)
        # new = grouped.get_group("FDX_in_HIL_specific_input_triggers")
    
    return fdx_concat

def extract_data_from_FDX_customer_database(database):
    """
    Create Dataframe from fdx_in sheet

    Args:
      database: 

    Returns:

    """
    with open(database, 'rb') as f:
        fdx_out_df=pd.read_excel(f, sheet_name='fdx_out_cus')
        fdx_out_df = fdx_out_df.drop(["group", "pdu"], axis=1)
        fdx_out_df = fdx_out_df.dropna(subset = ["Name"]) # Remove missing values.
        fdx_out_df.sort_values(by=['Message']) # Sort values in Message column

    return fdx_out_df

def filter_dataframe(dataframe):
    """
    

    Args:
      dataframe: 

    Returns:

    """
    dataframe = dataframe.values.tolist()
    fdx_all = []
    substring = "HIL_specific"
    for i in dataframe:
        if substring in i[1]:
            fdx_all.append(i)
    return fdx_all


def get_fdx_normalized(fdx_list,computation_only) -> list:
    """
    

    Args:
      fdx_list: 
      computation_only: 

    Returns:

    """
    normalized_data = []
    for i in fdx_list:
        if computation_only:
            i[0] = re.split("FDX_in_|FDX_out_|_[0-9]_",i[0])[-1]
        else:
            i[0] = re.split("FDX_in_|FDX_out_",i[0])[-1]
        i[1] = re.split("FDX_in_|FDX_out_",i[1])[-1]
        normalized_data.append(i)
        normalized_data.sort()
    return normalized_data

def remove_duplicates(normalized_list) -> list:
    """
    

    Args:
      normalized_list: 

    Returns:

    """
    duplicate = False
    fdx_no_dups = [normalized_list[0]]
    for i in normalized_list:
        for k in fdx_no_dups:
            if i[0] == k[0]:
                duplicate = True
            else:
                duplicate = False
        if not duplicate:
            fdx_no_dups.append(i)
    return fdx_no_dups

def get_unique_messages(dataframe):
    """
    

    Args:
      dataframe: 

    Returns:

    """
    messages_only = []
    for x in dataframe:
        x[1] = re.split("FDX_in_|FDX_out_",x[1])[-1]
        messages_only.append(x[1])
    return sorted(list(set(messages_only)))

def write_json(json_input,json_path):
    """
    

    Args:
      json_input: 
      json_path: 

    Returns:

    """
    write_obj = json.loads(json_input)
    with open(json_path, 'w') as f:
        json.dump(write_obj, f, indent=2, sort_keys=False)
    
        
def create_compu_method(hil_specific_all):
    """
    

    Args:
      hil_specific_all: 

    Returns:

    """
    filtered_data = filter_dataframe(hil_specific_all)
    fdx_signals = get_fdx_normalized(filtered_data,True)
    compu_methods = remove_duplicates(fdx_signals)
    compu_methods.sort(key= lambda compu_methods:compu_methods[1])

    """ Start the compu_method section """
    head_compu_method = ['{\n"compu_methods": {']
    compu_body = []
    for idx, data in enumerate(compu_methods):
        if idx == len(compu_methods) - 1:
            separator = ""
        else:
            separator = ","
        min_value = lambda sign : 0 if sign == "Unsigned" else -abs(int(data[19]))
        compu_methods_template = f"""
            "{data[0]}_COMPU_METHOD": [
              {{
                "label": "{data[14]}",
                "lower_limit": {min_value(data[6])},
                "lower_limit_closedinterval": true,
                "offset": 0,
                "scale": 1,
                "upper_limit": {int(data[19])},
                "upper_limit_closedinterval": true
              }}
            ]{separator}"""
        compu_body.append(compu_methods_template)

    head_compu_method.extend(compu_body)
    return head_compu_method


def create_groups(hil_specific_all):
    """
    

    Args:
      hil_specific_all: 

    Returns:

    """
    filtered_data = filter_dataframe(hil_specific_all)
    fdx_datagroup = get_fdx_normalized(filtered_data,False)
    messages = get_unique_messages(fdx_datagroup)

    """ Start the groups section """
    head_groups = ['\n},\n"groups": {']
    groups = []
    for current_message in messages:
        groups_template = f"""
                    "{current_message}": {{
                        "connections": [
                            "g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_fct_mainproc_RunnableMainProc",
                            "m_portCustomerInput_in"
                        ],
              "signals": {{"""
        groups.append(groups_template)

        for fdx_row in fdx_datagroup:
            if fdx_row[1] == current_message:
                signed = lambda sign : "false" if sign == "Unsigned" else "true"
                data_type = lambda data : "float" if data == "double" else "int"
                sig_in_message = f"""
                    "{fdx_row[0]}": {{
                           "array_size": 0,
                           "bit_size": 64,
                           "bus_signal": "{fdx_row[0]}",
                          "compu_method": "{re.split("_[0-9]_",fdx_row[0])[-1]}_COMPU_METHOD",
                           "datatype": "{data_type(fdx_row[27])}",
                           "group": "{current_message}",
                          "initial_value": {int(fdx_row[7])},
                           "ros_msg_prefix": "",
                          "signed": {signed(fdx_row[6])}
                        }},"""
                groups.append(sig_in_message)
        if current_message == messages[-1]:
            separator = ""
        else:
            separator = ","
        groups[-1] = groups[-1].replace("},", "}")
        groups_tail = f' \n}},\n"states": []\n}}{separator}'
        groups.append(groups_tail)
    head_groups.extend(groups)
    return head_groups


def create_publishers(hil_specific_all):
    """
    

    Args:
      hil_specific_all: 

    Returns:

    """
    head_publishers = ['\n},\n"publishers": {']
    filtered_data = filter_dataframe(hil_specific_all)
    fdx_datagroup = get_fdx_normalized(filtered_data,False)
    messages = get_unique_messages(fdx_datagroup)

    """ Start the publishers section """
    all_publishers = []
    for current_message in messages:
        publishers_group = []
        sig_tag = []
        for fdx_row in fdx_datagroup:
            if fdx_row[1] == current_message and fdx_row[1] != "HIL_specific_input_triggers":
                #if fdx_row[16] == 1:
                    direction = lambda data : "out" if data == "out" else "in"
                    #sporadic = False
                    publishers_body = f"""
                    "{fdx_row[1]}": {{
                    "group": "{fdx_row[1]}",
                    "signals": [ """
                    sig_tag.append(f'\n"{fdx_row[0]}",')
                    if fdx_row[16] == 0:
                        sporadic = "true"
                    else:
                        sporadic = "false"
                    type_body = f'\n],\n"sporadic": {sporadic},\n"direction": "{direction(fdx_row[23])}"\n}},'
                    combined_signals = "".join(sig_tag)
                    publ = publishers_body + combined_signals + type_body

        publ = publ.replace(",\n]","\n]")
        publishers_group.append(publ)
        all_publishers.extend(publishers_group)

    sporadic_signals = []
    publishers_group_sporadic = []
    for current_message in messages:
        for fdx_row in fdx_datagroup:
            if fdx_row[1] == "HIL_specific_input_triggers":
                if fdx_row[16] == 0:
                    direction = lambda data : "out" if data == "out" else "in"
                    separator = lambda mess : "" if mess == messages[-1] else ","

                    publishers_body_sporadic = f"""
                    "{fdx_row[1]}_{fdx_row[0]}": {{
                    "group": "{fdx_row[1]}",
                    "signals": [
                        "{fdx_row[0]}"
                    ],
                    "sporadic": true,
                    "direction": "{direction(fdx_row[23])}"
                    }},"""
                    sporadic_signals.append(publishers_body_sporadic)
    publishers_group_sporadic.extend(sporadic_signals)
    all_publishers.extend(publishers_group_sporadic)
    head_publishers.extend(all_publishers)
    return head_publishers


def main_sequence(database_fdx, json_file):
    """
    

    Args:
      database_fdx: 
      json_file: 

    Returns:

    """
    try:
        hil_specific_classe = extract_data_from_FDX_platform_database(database_fdx)
        hil_specific_fdx = extract_data_from_FDX_customer_database(database_fdx)
        hil_specific_concat = pd.concat([hil_specific_classe, hil_specific_fdx]) 
        compu_methods = create_compu_method(hil_specific_concat)
        groups = create_groups(hil_specific_concat)
        publishers = create_publishers(hil_specific_concat)
        
        tail = '\n},\n"system_signals": {}\n}'
        compu_methods.extend(groups)
        compu_methods.extend(publishers)
        compu_methods.append(tail)
        json_string = "".join(compu_methods)
        json_string = json_string.replace('},\n},\n"system_signals": {}\n}','}\n},\n"system_signals": {}\n}')
        #print(json_string)
        write_json(json_string,json_file)
        logger.info("HIL_specific.json created succesfully")
        return True

    except Exception as e:
        logger.error(f"Failed due to : {e}")
        return False


if __name__ == "__main__":
    main_sequence()









