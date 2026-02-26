# -*- coding: utf-8 -*-
# @file fdx_database_gen.py
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


import time
from openpyxl import load_workbook
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
import re
import os, sys
try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Rbs_Scripts")
from create_sysvar import define_classe_colIndex,generate_sysvar_header, generate_sysvar,generate_sysvar_footer, save_to_file


#allow longer names up to 100 characters
pd.options.display.max_colwidth = 100
pd.options.display.colheader_justify = 'left'

column_names = ["Name", "group","pdu","Message","Multiplexing/Group", "Value Type", "Initial Value", "Factor", "Offset", "Minimum",  "Maximum", "Unit", "texttable", "texttable values", "max_value", "sender", "direction", "texttable mapping", "conversion", "array name", "data_type"]

# read worksheet 'sheet_name' from workbook 'wb'
def generate_dataframe(df_FDX, sheet_name):
    """
    generate dataframe for sheet and put into global dataframe

    Args:
      df_FDX(dataframe): dataframe of excel sheet
      sheet_name(string): for which sheet dataframe to generate

    Returns:

    """
    global node, node_df, num_of_rows, sheet
    global signal_cloe
    global col_name, col_namespace, col_group, col_initial_value, col_factor, col_offset, col_minimum, col_maximum, col_unit, col_texttable, col_texttable_values, col_max_value, col_sender, col_direction, col_texttable_mapping, col_conversion, col_array_name, col_index
    sheet = sheet_name
    
    # node = ['/*@!Encoding:1252*/']
    # node.append(node_head)
    df_FDX.loc[-1] = list(df_FDX.columns)  # adding a row
    df_FDX.index = df_FDX.index + 1  # shifting index
    df_FDX = df_FDX.sort_index()
    df_FDX = df_FDX.replace(np.nan, '', regex=True)
    node_df = df_FDX.rename(columns={x: y for x, y in zip(df_FDX.columns, range(0, len(df_FDX.columns)))})

    # get column names
    col_names = list(node_df.iloc[0])
    # get column index
    try:
        col_index = [col_names.index(col) for col in column_names]
    except:
        logger.error("Column names in Excel are different from the Script:")
        logger.error(';'.join(column_names))
        return False
    [col_name, col_group, col_pdu, col_namespace, col_group, col_value_type, col_initial_value, col_factor, col_offset, col_minimum, col_maximum, col_unit, col_texttable, col_texttable_values, col_max_value, col_sender, col_direction, col_texttable_mapping, col_conversion, col_array_name, col_data_type] = col_index

    signal_cloe.extend(node_df[node_df[col_sender] == "Cloe"][col_name].tolist())
    num_of_rows = node_df.shape[0]
    logger.info(f"Signal count: {num_of_rows-1}")

def generate_onsysvarenum():
    """ it will filter out not empty texttable column
      and put cloe signal into datafame"""
    global sysvar_df
    message_count = 0
    enum_df = node_df
    enum_df = enum_df[(enum_df[col_texttable] != "")]
    num_of_rows_enum = enum_df.shape[0]
    for i in range(num_of_rows_enum):
        if (enum_df[col_sender].values[i] == "Cloe"):
            # generate sysvar
            add_sysvar_df = enum_df[col_index].iloc[[i]]
            add_sysvar_df.columns = [i for i in range(len(col_index))]
            sysvar_df = pd.concat([sysvar_df, add_sysvar_df])

    logger.info(f"enum int: generated with {str(message_count)} messages.")

def generate_onsysvardouble():
    """it will filter out not texttable  and put cloe signal into datafame """
    global sysvar_df
    message_count = 0
    sysvardouble_df = node_df
    sysvardouble_df = sysvardouble_df[(sysvardouble_df[col_texttable] != "texttable")]
    sysvardouble_df = sysvardouble_df[(sysvardouble_df[col_array_name] == "")]
    num_of_rows_double = sysvardouble_df.shape[0]
    for i in range(num_of_rows_double):
        if (sysvardouble_df[col_sender].values[i] == "Cloe"):
            # generate sysvar
            add_sysvar_df = sysvardouble_df[col_index].iloc[[i]]
            add_sysvar_df.columns = [i for i in range(len(col_index))]
            sysvar_df = pd.concat([sysvar_df, add_sysvar_df])

    logger.info(f"double signal : generated with {str(message_count)} messages.")

def generate_mapping(sysvar_df):
    """
    it will take data from sheet and create system variable for each message
    

    Args:
      sysvar_df(dataframe): dataframe of Fdx_sheet

    Returns:

    """
    # get column index
    try:
        col_name = column_names.index("Name")
        col_namespace = column_names.index("Message")
        col_group = column_names.index("Multiplexing/Group")
        col_value_type = column_names.index("Value Type")
        col_unit = column_names.index("Unit")
        col_texttable = column_names.index("texttable")
        col_direction = column_names.index("direction")
        col_data_type = column_names.index("data_type")
    except:
        logger.error("Column names in Excel are different from the Script:")
        logger.error(';'.join(column_names))
        return False

    xml = ['<?xml version="1.0" encoding="iso-8859-1"?>']
    xml.append('<canoefdxdescription version="1.0">')
    #print('\n'.join(xml))
    group_ids = list(set(sysvar_df[col_group].values))
    group_ids.remove("Multiplexing/Group")

    for item in group_ids:
        item_xml = []
        #item_xml.append('    <identifier>EasyDataRead</identifier>')

        sub_sysvar_df = sysvar_df[sysvar_df[col_group] == item]
        size_sum = 0
        offset = 0
        for i in range(sub_sysvar_df.shape[0]):
            signal_name = sub_sysvar_df[col_name].iloc[i]
            namespace = sub_sysvar_df[col_namespace].iloc[i]
            value = "raw"
            size = 8
            unit = sub_sysvar_df[col_unit].iloc[i]
            texttable = sub_sysvar_df[col_texttable].iloc[i]
            data_type = sub_sysvar_df[col_data_type].iloc[i]
            value_type = "int64" 
            if data_type == "int" or data_type == "int enum":
                value_type = "uint64" if sub_sysvar_df[col_value_type].iloc[i] == "Unsigned" else "int64"
            else:
                if data_type == "bool":
                    value_type = "uint32"
                else:
                    value_type = "double"
            #print(signal_name, namespace, value, value_type, size, unit)
            identifier = re.split("FDX_in_|FDX_out_", namespace)[-1]
            item_xml.append('    <item offset="{0}" size="{1}" type="{2}">'.format(str(offset), str(size), value_type))
            item_xml.append('      <identifier>{}</identifier>'.format(signal_name))
            item_xml.append('      <sysvar name="{0}" namespace="{1}" unit="{2}" value="{3}" />'.format(signal_name, namespace, unit, value))
            item_xml.append('    </item>')
            offset += size
            size_sum += size
        xml.append('  <datagroup groupID="{0}" size="{1}">'.format(str(item), str(size_sum)))
        xml.append(f'    <identifier>{identifier}</identifier>')
        xml.extend(item_xml)
        xml.append('  </datagroup>')
        #print('  <datagroup groupID="{0}" size="{1}">'.format(str(group_id), str(size_sum)))
        #print('\n'.join(item_xml))
        #print('  </datagroup>')
    xml.append('</canoefdxdescription>')
    return xml

def generate_fdx_init(sysvar_df):
    """
    
   it will create cin  file for  fdx_in_cus with set of 25 messages
    Args:
      sysvar_df(dataframe): dataframe of Fdx_in_cus_sheet

    Returns:

    """
    # get column index
    try:
        col_name = column_names.index("Name")
        col_namespace = column_names.index("Message")
    except:
        logger.error("Column names in Excel are different from the Script:")
        logger.error(';'.join(column_names))
        return False

    head = '''/*@!Encoding:1252*/
/**
 * @file signal.can
 * @author Rafael Herrera - ECU initialization file
 * @date 20.10.2021
 * @brief contains code that initialize the ECU or ECUs of the HIL
*/
includes
{
}

variables
{
} 

void init_fdx()
{
  if(init_count == 1)
  {'''

    item_xml = []
    xml = [head]
    flag_count = 1
    signal_batch = 25

    for i in range(1, sysvar_df.shape[0]):

        signal_name = sysvar_df[col_name].values[i]
        namespace = sysvar_df[col_namespace].values[i]

        if "FDX_in_HIL_mode" in signal_name:
            continue
        else:
            item_xml.append(f'  @{namespace}::{signal_name} = 0;')
        # case new set of 25 signals
        if i % signal_batch == 0:
            # except for the first signal
            if i != 0:
                item_xml.append('  }')
            ini_count = i // signal_batch + 1
            item_xml.append(f'  if(init_count == {ini_count})')
            item_xml.append('  {')

    item_xml.append('  if (prestart_mode==0) init_count = 0;')
    flag_count += 1
    item_xml.append('  initFlag = {0};'.format(flag_count))
    item_xml.append('  }')
    item_xml.append('  init_count++;')
    item_xml.append('}')
    xml.extend(item_xml)

    return xml
    
    # used_triggers_df = pd.read_excel(open('../FDX/FDX_Database.xlsx', 'rb'), sheet_name='fdx_in')
    # list_of_used_triggers = used_triggers_df.values.tolist()
    # list_of_all_triggers  = sysvar_df.values.tolist()
    # for el in list_of_used_triggers:
    #     signal_name = el[0]
    #     for el_all_triggers in list_of_all_triggers:
    #         if (el_all_triggers[0].find(signal_name)>=0):
    #             signal_name=el_all_triggers[0]
    #             namespace=el_all_triggers[1]
    #             item_xml.append(f'  @{namespace}::{signal_name} = 0;')
    

def save_file(file_path):
    """
    saving .can file at file_path
    

    Args:
      file_path(str):file path name where file to save

    Returns:

    """
    # Open and save node .can file
    file = ('{0}/{1}.can'.format(file_path, sheet))
    with open(file, 'w') as outfile:
        outfile.write("\n".join(str(item) for item in node))
        outfile.close()
    logger.info(f"{file} updated successfully")


# main function to create nodes
def create_mapping_main_database(df_FDX, file_path):
    """
    it will create database as per fdxTriggersDatabase sheet and put
     into xml file for fdx  system variable and for Fdx_in_cus sheet it will create
     .cin file
    

    Args:
      df_FDX(dataframe): dataframe of Fdx_sheet
      file_path(str):file path name where can file to save

    Returns:

    """
    try:
        create_mapping_custom_sheet(df_FDX,"fdxTriggersDatabase")
        define_classe_colIndex(list(sysvar_df.iloc[0]))
        sysvar_xml = generate_sysvar_header()
        sysvar_xml.extend(generate_sysvar(sysvar_df, FDX=True))
        sysvar_xml.extend(generate_sysvar_footer())
        time.sleep(5)
        save_to_file(sysvar_xml, file_path+"/Databases", "FDX_Database")
        fdx_xml = generate_mapping(sysvar_df)
        time.sleep(5)
        save_to_file(fdx_xml, file_path+"/Databases", "FDX_Mapping")

        fdx_in_sheet_name = "fdx_in_cus"
        create_mapping_custom_sheet(df_FDX,fdx_in_sheet_name)
        fdx_init = generate_fdx_init(sysvar_df)
        save_to_file(fdx_init, file_path+"/Nodes", "fdx_init")
    except Exception as exp:
        logger.error(f"Failed to create sysvar&mapping: {exp}")
        return False
    return True

def create_mapping_custom_sheet(df_FDX, sheet_name):
    """
    it will create mapping dataframe for generate xml or cin file
    

    Args:
      df_FDX(dataframe): dataframe of Fdx_shee
      sheet_name(str): sheet name for mapping

    Returns:

    """
    global sysvar_df, signal_cloe
    sheet_list = list(df_FDX.keys())
    sysvar_df = pd.DataFrame([column_names])
    signal_cloe = ["Name"]
    if sheet_name in sheet_list:
        logger.info(f"++++++++++Creating mapping for: {sheet_name} ++++++++++")
        try:
            generate_dataframe(df_FDX[sheet_name], sheet_name)
            generate_onsysvardouble()
            generate_onsysvarenum()
            # save_file(file_path+"/Nodes")
        except Exception as exp:
            logger.error(f"Failed to create node for: {sheet_name}")
            logger.error(f"Error: {exp}")
            return False
    else:
        logger.error(f"Sheet {sheet_name} not found in FDX excel")
    try:
        index_list = []
        for i in range(sysvar_df.shape[0]):
            try:
                index_list.append(signal_cloe.index(sysvar_df.iloc[i][col_name]))
            except:
                logger.error(f"{sysvar_df.iloc[i][col_name]} signal is not found in sysvar_df.")
                raise Exception("Please check that 3 generate functions.")
        sysvar_df["Index"] = index_list
        sysvar_df = sysvar_df.sort_values("Index")
        
    except Exception as exp:
        logger.error(f"Failed to create sysvar&mapping: {exp}")
        return False


def external_call():
    """ """
    try:
        logger.info("###### START 'Update FDX Database' DEBUG INFORMATION ######")
        script_path = os.path.dirname(os.path.abspath(__file__))
        df_FDX = pd.read_excel(script_path + r'/../../../../CustomerPrj/FDX/FDX_Database.xlsx', sheet_name=None, dtype=object)
        create_mapping_main_database(df_FDX, script_path + r'/../../../../CustomerPrj/FDX/')
    except Exception as e:
        logger.error(f"Update Update FDX Database failed. Exception --> {e}")
    logger.info("###### END 'Update FDX Database' DEBUG INFORMATION ######")
    logger.info('-' * 80)


if __name__ == "__main__":
    external_call()



