# -*- coding: utf-8 -*-
# @file create_gw.py
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


from openpyxl import load_workbook
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
import os, sys

try:
    sys.path.append(os.getcwd() + r"\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import *
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import *

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger

try:
    from Rbs_Scripts.create_nodes import extractHilCtrl, getCopyRights
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from create_nodes import extractHilCtrl, getCopyRights

#allow longer names up to 100 characters
pd.options.display.max_colwidth = 100
pd.options.display.colheader_justify = 'left'

column_names = ['Name','group','PDU', 'PDU Type','Message','Multiplexing/Group','Startbit','Length [Bit]','Byte Order','Value Type','Initial Value','Factor','Offset','Minimum','Maximum','Unit','Value Table','Comment','Message ID','Cycle Time [ms]','texttable','texttable values', 'EndToEndProtection', 'max_value', 'dlc', 'variant',"Block_size", "Address_formate","Padding_active", "STMin","MAXFC_wait", 'sender', 'gw', 'node_entity', 'network_type', 'input_file', "dbc_file_index", "network_name",'a_variant_veh_0','a_variant_veh_1','b_variant_veh_0','b_variant_veh_1']
sort_by_column_names =['Message','Name']
gw_header = '''
includes
{
}

variables {
 
} 


on start
{

}

on stopMeasurement
{

}
'''
def generate_gw(ws1, file_path):
    """
    generate gateway main function

    Args:
      ws1 (worksheet): worksheet of sysvar database sheet
      file_path (str): path to save .can file

    """
    node = []
    node.append(gw_header)
    node.extend(generate_sysvarmapping(ws1))
    # Open and save node .can file
    file = (file_path + r'/Sysvarmapping.can')
    copyrights = getCopyRights(file)
    with open(file, 'w') as outfile:
        if copyrights:
            outfile.write(copyrights)
        else:
            outfile.write('/*@!Encoding:1252*/')
        outfile.write("\n".join(str(item) for item in node))
    logger.info(f"{file} updated successfully")

def getColNamespace(entity):
    """
    takes entity name as input and return column index

    Args:
      entity (str): entity name msg/pdu/grp

    Returns:
        int: index of column
    """
    if "message" in entity:
        return col_msg
    elif "pdu" in entity:
        return col_pdu
    elif "group" in entity:
        return col_group
    else:
        return col_msg

def generate_sysvarmapping(ws1):
    """
    this function generates the gateway mapping

    Args:
      ws1 (worksheet): worksheet of sysvardatabase sheet

    Returns:
        list: file content
    """
    global col_pdu, col_msg, col_group
    node = []
    #ws1 = wb[sheet_name]
    # create the different dataframes
    node_df = pd.DataFrame(ws1.values)
    node_df = node_df.replace(np.nan, '', regex=True)

    # get column names
    col_names = list(node_df.iloc[0])
    try:
        col_name = col_names.index("Signal")
        col_pdu = col_names.index("PDU")
        col_group = col_names.index("Signal_Group")
        col_msg = col_names.index("Message")
        col_gw = col_names.index("gw")
        #col_bus_type = col_names.index("bus_type")
        #col_input_file = col_names.index("input_file")
        col_entity = col_names.index("node_entity")
        col_network_name = col_names.index("network_name")
    except:
        logger.error("Column names not found in Excel. Please check it in Autosar_Gen_Database.xlsx")
        return False
    unique_entity = list(node_df[col_entity].loc[1:].unique())
    split_dfs = []
    for entity in unique_entity:
        col_namespace = getColNamespace(entity)
        filtered_df = node_df[node_df[col_entity] == entity]
        filtered_df = filtered_df[filtered_df[col_namespace].str.contains(diag_msg_pattern, regex=True)==False]#Filter out Diag
        filtered_df = filtered_df[filtered_df[col_namespace].str.contains(flt_evt_msg_pattern, regex=True)==False]#Filter out FLT_EVT
        filtered_df = filtered_df[filtered_df[col_namespace].str.contains(stbm_msg_pattern, regex=True)==False]#Filter out STBM
        split_dfs.append(filtered_df)
    node_df = pd.concat(split_dfs,axis=0)

    # gw filter
    node_df = node_df[node_df[col_gw] != ''].iloc[1:]
    logger.info(f"Signal count: {node_df.shape[0]}")

    if len(node_df)!=0:
        node_df=df_sort_asc(node_df,column_names,sort_by_column_names)#Sort in ascending df by column names

    # Create initialization of timers and node variables
    message_count = 0
    if(pd.isna(node_df[col_gw].max())):
        gw_max=0
    else:
        gw_max = int(node_df[col_gw].max())
    for i in range(1, gw_max+1):
        network_name = node_df[node_df[col_gw] == i][col_network_name].values[0]
        entity = node_df[node_df[col_gw] == i][col_entity].values[0]
        col_namespace = getColNamespace(entity)
        namespace = node_df[node_df[col_gw] == i][col_namespace].values[0]
        signal_name = node_df[node_df[col_gw] == i][col_name].values[0]
        logger.info(f"{i}{namespace}{signal_name}")
        gw_df = node_df[node_df[col_gw].between(i, i+1, inclusive='neither')]
        #print(gw_df)
        for j in range(gw_df.shape[0]):
            namespace_gw = gw_df[col_namespace].values[j]
            signal_name_gw = gw_df[col_name].values[j]
            #print(namespace_gw, signal_name_gw)
            node.append('')
            node.append('on signal {2}::{0}::{1}'.format(namespace, signal_name,network_name))
            node.append('{')
            node.append('  ${2}::{0}::{1} = @this;'.format(namespace_gw, signal_name_gw, network_name))
            node.append('}')
            message_count += 1 
    logger.info(f"viodstart: generated with {str(message_count)} messages.")
    return node


def external_call():
    """ external call funct used by jenkins """
    try:
        script_path = os.path.dirname(os.path.abspath(__file__))
        logger.info("###### START 'Create SysVarMapping' DEBUG INFORMATION ######")
        autosar_path = script_path +  r'/../../../../CustomerPrj/Restbus/Autosar_Gen_Database.xlsx'
        wb = load_workbook(autosar_path, data_only=True)
        sys_sheet = "SysVarDatabase"
    
        generate_gw(wb[sys_sheet], script_path + r"/../../../../CustomerPrj/Restbus/Nodes")
        logger.info("###### END 'Create SysVarMapping' DEBUG INFORMATION ######")
        logger.info('-' * 80)
    except Exception as exp:
        logger.error(f"Create SysVarMapping execution failed --> {exp}")
        raise Exception(exp)
    logger.info("###### END 'Create SysVarMapping' DEBUG INFORMATION ######")
    logger.info('-' * 80)
    
    
if __name__ == "__main__":
    external_call()
    
