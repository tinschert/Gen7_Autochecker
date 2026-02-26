# -*- coding: utf-8 -*-
# @file create_arxml.py
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


import xml.etree.ElementTree as ET
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
import os,sys
try:
    from Rbs_Scripts.create_autosar import generate_dbc_map, load_excel_sheet, get_node_name, create_excel_sheets, extractVariant
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from create_autosar import generate_dbc_map, load_excel_sheet, get_node_name, create_excel_sheets, extractVariant

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.getcwd() + r"\..\Control")
    from logging_config import logger
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching_arxml import *
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching_arxml import *

pd.set_option('mode.chained_assignment', None)
# column_names = ["Name", "group", "pdu", "Message", "Multiplexing/Group", "Startbit", "Length [Bit]", "Byte Order",
#                 "Value Type",
#                 "Factor", "Offset", "Minimum", "Maximum", "Unit", "Value Table", "Comment", "Message ID",
#                 "Cycle Time [ms]",
#                 "texttable", "texttable values", "max_value", "dlc", "variant", "Src IP", "Src IP", "Multi Dst IP",
#                 "Src Port",
#                 "Dst Port", "Vlan ID", "Src Mac", "Dst Mac"]


def get_arxml_list(path, excel_path):
    """
    

    Args:
      path: 
      excel_path: 

    Returns:

    """
    arxml_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for file in filenames:
            if ".arxml" in file:
                arxml_files.append(dirpath + "\\" + file)

    df_arxmlmapping = pd.read_excel(excel_path, "ArxmlMapping")  # create a df
    list_excel_arxml = [i for i in df_arxmlmapping["dbc_file_name"].tolist() if not (pd.isnull(i))]  # read dbc filenames from excel
    list_excel_arxml_index = [int(i) for i in df_arxmlmapping["dbc_file_name_index"].tolist() if not (pd.isnull(i))]  # read dbc file index from excel
    list_excel_arxml_path = [path+"\\"+file for file in list_excel_arxml]

    # checking if all files are present in dbc directory else raise error
    for file in list_excel_arxml_path:
        if file not in arxml_files:  # checking if files defined in excel sheet are present in DBC directory
            logger.error("arxml filenames or file order in excel and windows directory are different")
            raise Exception("Failed to create arxml")

    dict_arxml_files = dict(zip(list_excel_arxml_index,list_excel_arxml_path))

    if dict_arxml_files:
        logger.info(f"Found ARXML file/s --> {dict_arxml_files}")
        return dict_arxml_files
    else:
        logger.error(f"No ARXML files found in {path}")

def parse_autosar(arxml_path):
    """
    

    Args:
      arxml_path: 

    Returns:

    """
    logger.info(f"Start extracting data from {arxml_path}")
    
    try:
        tree = ET.parse(arxml_path)
        root = tree.getroot()
        ns = "{http://autosar.org/schema/r4.0}"
    except Exception as e:
        logger.error(f"Failed parsing {arxml_path}. Reason --> {e}")
        raise e
    
    try:
        ''' Extract [Name] [pdu] [Byte Order] [Startbit] [Cycle Times] [PDU Groups]'''
        pdus = []
        signals = []
        pdus_count = []
        byte_order = []
        start_bit = []
        cycle_times = []
        pdu_groups = []
        for elem in tree.iter(tag=f"{ns}I-SIGNAL-I-PDU"):
            pdus_count.append(elem)
            sig_extract = elem.findall(signals_path)
            for sig in sig_extract:
                pdus.append(elem.find(f'{ns}SHORT-NAME').text)
                pdu_group = elem.find(pdu_group_path)
                if pdu_group is not None:
                    pdu_groups.append(pdu_group.text.split("/")[-1])
                else:
                    pdu_groups.append(None)
                cycle_time = elem.find(cycle_time_path)
                if cycle_time is not None:
                    cycle_times.append(float(cycle_time.text)*1000)
                else:
                    cycle_times.append(0)
                signal = sig.find(f'{ns}I-SIGNAL-REF')
                if signal is not None:
                    signals.append(signal.text.split("/")[-1])
                    order = sig.find(byte_order_path)
                    if order is not None:
                        if order.text == "MOST-SIGNIFICANT-BYTE-LAST":
                            byte_order.append("Intel")
                        elif order.text == "MOST-SIGNIFICANT-BYTE-FIRST":
                            byte_order.append("Motorola")
                        else:
                            byte_order.append(order.text)
                    else:
                        byte_order.append(None)
                    start_bit.append(int(sig.find(start_bit_path).text))
    
        logger.info(f"Found {len(pdus_count)} PDUs")
        logger.info(f"Found {len(signals)} signals")
        logger.info(f"Found {len(byte_order)} byte orders")
        logger.info(f"Found {len(start_bit)} start bits")

        ''' Extract [Frame] '''
        frames = []

        can_frames_objects = root.findall(f'.//{ns}CAN-FRAME')
        for current_pdu in pdus:
            for frame_obj in can_frames_objects:
                frame = frame_obj.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}SHORT-NAME').text
                if current_pdu == frame:
                    frames.append(frame_obj.find(f'{ns}SHORT-NAME').text)
                    break

        ''' Extract [Frame ID] '''
        message_ids = []

        can_frames_objects = root.findall(f'.//{ns}CAN-FRAME-TRIGGERING')
        for current_frame in frames:
            for frame_obj in can_frames_objects:
                frame = frame_obj.find(f'{ns}SHORT-NAME').text
                if current_frame in frame:
                    message_id = frame_obj.find(f'{ns}IDENTIFIER').text
                    base16INT = int(message_id)
                    hex_value = hex(base16INT)
                    message_ids.append(hex_value.upper())
                    break

        ''' Extract [Initial Value] [Length] and system signal reference'''
        initial_values = []
        signals_length = []
        sys_sig = []
        base_types = []
        node = root.findall(f'.//{ns}I-SIGNAL')
        for sig in signals:
            for elem in node:
                if sig == elem.find(f'{ns}SHORT-NAME').text:
                    init = elem.find(f"{ns}INIT-VALUE/{ns}NUMERICAL-VALUE-SPECIFICATION/{ns}VALUE")
                    if init is not None:
                        # Workaround for IPCSYS_FMEM_HARDDSBL
                        if init.text == "IPCSYS_FMEM_HARDDSBL":
                            init = 0
                            initial_values.append(init)
                        else:
                            initial_values.append(float(init.text))
                    else:
                        initial_values.append(None)
                    length = elem.find(f"{ns}LENGTH")
                    if length is not None:
                        signals_length.append(int(length.text))
                    else:
                        signals_length.append(None)
                    base_type = elem.find(base_type_path)
                    if base_type is not None:
                        if "uint" in base_type.text:
                            base_types.append("Unsigned")
                        else:
                            base_types.append("Update to new base types")
                    else:
                        base_types.append(None)
                    sys_signal = elem.find(f"{ns}SYSTEM-SIGNAL-REF")
                    if sys_signal is not None:
                        sys_sig.append(sys_signal.text.split("/")[-1])
                    else:
                        sys_sig.append(None)
        logger.info(f"Found {len(initial_values)} initial values")
        logger.info(f"Found {len(signals_length)} signal lengths")
        logger.info(f"Found {len(sys_sig)} signal references")
    
    
        ''' Get comment , Computational method and Data method'''
        node = root.findall(f'.//{ns}SYSTEM-SIGNAL')
        comments = []
        sig_to_compu = {}
        sig_to_data = {}
        for signal in sys_sig:
            for sig in node:
                name = sig.find(f'{ns}SHORT-NAME').text
                if signal == name:
                    comment = sig.find(f'{ns}DESC/{ns}L-2')
                    if comment is not None:
                        comments.append(comment.text)
                    else:
                        comments.append(None)
                    compu_method = sig.find(compu_methods_path)
                    if compu_method is not None:
                        sig_to_compu[signal] = compu_method.text.split("/")[-1]
                    else:
                        sig_to_compu[signal] = None
                    data_method = sig.find(data_methods_path)
                    if data_method is not None:
                        sig_to_data[signal] = data_method.text.split("/")[-1]
                    else:
                        sig_to_data[signal] = None
        logger.info(f"Found {len(comments)} comments")
    
    
        ''' Get texttable'''
        signal_category = []
        factors = []
        offsets = []
        texttable_values = []
        compu_data_type = root.findall(f'.//{ns}COMPU-METHOD')
        for cmp_method in sig_to_compu.values():
            if cmp_method is None:
                signal_category.append(cmp_method)
                factors.append(1)
                offsets.append(0)
                texttable_values.append(None)
            else:
                for sig in compu_data_type:
                    name = sig.find(f'{ns}SHORT-NAME').text
                    if cmp_method == name:
                        category = sig.find(f'{ns}CATEGORY').text
                        if category.startswith("TEXTTABLE"):
                            signal_category.append(category.lower())
                            factors.append(1)
                            offsets.append(0)
                            enum = sig.findall(enums_path)
                            enum_entries = []
                            for texttable_entry in enum:
                                enum_entries.append("LogicalValue: " + texttable_entry.find(f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(f'{ns}COMPU-CONST/{ns}VT').text)
                            texttable_values.append("\n".join(enum_entries))
                        elif category.startswith(("SCALE_LINEAR_AND_TEXTTABLE", "LINEAR")):
                            signal_category.append(None)
                            try:
                                factors.append(float(sig.find(factors_path_type_1).text))
                                offsets.append(float(sig.find(offsets_path_type_1).text))
                                texttable_values.append(None)
                            except:
                                factors.append(float(sig.find(factors_path_type_2).text))
                                offsets.append(float(sig.find(offsets_path_type_2).text))
                                texttable_values.append(None)
                        else:
                            signal_category.append(None)
                            factors.append(None)
                            offsets.append(None)
                            texttable_values.append(None)
    
        logger.info(f"Found {len(signal_category)} textables")
    
        ''' Get minimum and maximum'''
        list_minimums = []
        list_maximums = []
        data_constr = root.findall(f'.//{ns}COMPU-METHOD')
        for data in sig_to_compu.values():
            if data is None:
                list_minimums.append(data)
                list_maximums.append(data)
            else:
                for sig in data_constr:
                    name = sig.find(f'{ns}SHORT-NAME').text
                    if data == name:
                        category_ = sig.find(f'{ns}CATEGORY').text
                        if not category_.startswith("TEXTTABLE"):
                            min_ = sig.find(min_value_path)
                            max_ = sig.find(max_value_path)
                            if min_ is not None and max_ is not None:
                                list_minimums.append(float(min_.text))
                                list_maximums.append(float(max_.text))
                                break
                            else:
                                list_minimums.append(None)
                                list_maximums.append(None)
                                break
                        else:
                            min_texttable = sig.find(texttabble_min_value_path)
                            texttable_min = int(min_texttable.text,0)
                            max_values_texttable_signal = sig.findall(texttabble_max_value_path)
                            max_val_enum = max_values_texttable_signal[-1]
                            max_ = max_val_enum.find(f'{ns}UPPER-LIMIT')
                            texttable_max = int(max_.text,0)
                            if texttable_min > texttable_max:
                                list_minimums.append(texttable_max)
                                list_maximums.append(texttable_min)
                            else:
                                list_minimums.append(texttable_min)
                                list_maximums.append(texttable_max)


        logger.info(f"Found {len(list_minimums)} minimum values")
        logger.info(f"Found {len(list_maximums)} maximum values")
    
        #return list(zip(signals, pdu_groups, pdus, start_bit, signals_length, byte_order, base_types, initial_values, factors, offsets, list_minimums, list_maximums, comments,cycle_times, signal_category, texttable_values))
        return list(
            zip(signals, pdus, frames,start_bit, signals_length, byte_order, initial_values,  factors,
                offsets, list_minimums, list_maximums, message_ids, cycle_times, signal_category, texttable_values))
    except Exception as e:
        logger.error(f"Failed to extract data from {arxml_path}. Reason --> {e}")
        raise e


def create_nodes(signals_full_data, arxml_path, excel_node, direction):
    """
    

    Args:
      signals_full_data: 
      arxml_path: 
      excel_node: 
      direction: 

    Returns:

    """

    if direction.lower() == "tx":
        dir_string = "_out"
    elif direction.lower() == "rx":
        dir_string = "_in"
    else:
        raise "Unknown signal direction"

    try:
        tree = ET.parse(arxml_path)
        root = tree.getroot()
        ns = "{http://autosar.org/schema/r4.0}"
    except Exception as e:
        logger.error(f"Failed parsing {arxml_path}. Reason --> {e}")
        raise e

    ''' Separate nodes'''
    nodes = root.findall(f'.//{ns}I-SIGNAL-TRIGGERING')
    dbc_node = []
    for signals in signals_full_data:
        signal = signals[0]
        for node in nodes:
            related_node = node.find(f'{ns}I-SIGNAL-PORT-REFS/{ns}I-SIGNAL-PORT-REF').text
            signal_identification = node.find(f'{ns}I-SIGNAL-REF').text.split("/")[-1]
            if signal == signal_identification and excel_node[0] in related_node and dir_string in related_node:
                dbc_node.append(signals)
    return dbc_node

    #logger.info(f"Found {len(comments)} comments")



def create_dataframe(data, variant_dict):
    """
    

    Args:
      data: 
      variant_dict: 

    Returns:

    """
    try:
        ''' Create the dataframe'''
        # df = pd.DataFrame(data,
        #                   columns=['Name', 'group', 'Message', 'Startbit', 'Length [Bit]', 'Byte Order', 'Value Type',
        #                            'Initial Value', 'Factor','Offset','Minimum', 'Maximum', 'Comment',
        #                            'Cycle Time [ms]', 'texttable', 'texttable values'])

        df = pd.DataFrame(data,
                          columns=['Name', 'pdu', 'Message','Startbit','Length [Bit]', 'Byte Order', "Initial Value",
                                   'Factor', 'Offset', 'Minimum',
                                   'Maximum', 'Message ID', 'Cycle Time [ms]', 'texttable', 'texttable values'])
    
        #columns_to_add = {"group": 1}
        columns_to_add = {"group": 1, "Multiplexing/Group": 4, 'Value Type': 8, 'Unit': 14, 'Value Table': 15, 'Comment': 16,
                          "max_value": 21, "dlc": 22, "variant": 23, "Src IP": 24, "Dst IP": 25, "Multi Dst IP": 26, "Src Port": 27, "Dst Port": 28,
                          "Vlan ID": 29, "Src Mac": 30, "Dst Mac": 31}
        for key, value in columns_to_add.items():
            df.insert(value, key, np.nan)

        #fill variants
        for i,row in df.iterrows():
            #fill variant column
            if row['pdu'] in variant_dict["a_variant"]:
                df["variant"][i] = "a_variant"
            elif row['pdu'] in variant_dict["b_variant"]:
                df["variant"][i] = "b_variant"
            else:
                df["variant"][i] = "Common"

            #fill max_value column
            df["max_value"][i] = (2 ** (int(df["Length [Bit]"][i])))-1

        logger.info("Filled variant, max_value columns")

        return df
    except Exception as e:
        logger.error(f"Failed to create dataframe --> {e}")
        raise e


def write_to_excel(df,sheet):
    """
    

    Args:
      df: 
      sheet: 

    Returns:

    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    try:
        ''' Writing the excel'''
        with pd.ExcelWriter(script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer,index=False, sheet_name=sheet)
            logger.info(f"Created sheet --> {sheet}")
        logger.info('DataFrame is written to Excel File successfully.')
    except Exception as e:
        logger.info(f"Failed to write dataframe to excel --> {e}")
        raise e

def create_arxml_main(arxmls_path):
    """
    

    Args:
      arxmls_path: 

    Returns:

    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    excel_path = script_path+r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'
    arxml_map = generate_dbc_map(excel_path,"ArxmlMapping")
    variant_dict = extractVariant(excel_path,"ArxmlMapping")
    wb, sheet_list, autosar_directory = load_excel_sheet()
    list_node, dict_node, dict_ecu_name, tx_messages, block_messages, direction = get_node_name(wb, "ArxmlMapping", True)
    arxmls = get_arxml_list(arxmls_path, excel_path)
    for _map in arxml_map:
        arxml_index = _map[1]
        sheet_index = _map[0]
        data = parse_autosar(arxmls[arxml_index])
        specific_node_data = create_nodes(data,arxmls[arxml_index],dict_ecu_name[list_node[sheet_index]], direction[sheet_index])
        df_to_write = create_dataframe(specific_node_data,variant_dict)
        write_to_excel(df_to_write,list_node[sheet_index])

def external_call():
    """ """
    try:
        logger.info("###### START 'Create Autosar ARXML' DEBUG INFORMATION ######")
        script_path = os.path.dirname(os.path.abspath(__file__))
        arxml_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Database\DBC'
        create_arxml_main(arxml_path)
        logger.info("###### END 'Create Autosar ARXML' DEBUG INFORMATION ######")
        logger.info('-' * 80)
    except Exception as exp:
        logger.error(f"Failed to create arxml: {exp}")
        raise Exception(exp)

if __name__ == "__main__":
    external_call()


# ''' Get value type'''
# signal_value_types = []
# node_data_type = root.findall(f'.//{ns}IMPLEMENTATION-DATA-TYPE')
# for data_method in sig_to_data.values():
#     if data_method is None:
#         signal_value_types.append(data_method)
#     else:
#         for sig in node_data_type:
#             name = sig.find(f'{ns}SHORT-NAME').text
#             if data_method in name:
#                 data_type = sig.find(
#                     f'{ns}SW-DATA-DEF-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}IMPLEMENTATION-DATA-TYPE-REF').text
#                 if data_type is not None:
#                     signal_value_types.append(data_type)
# value_type = []
# for string in signal_value_types:
#     if string is None:
#         value_type.append(string)
#     elif "uint" in string:
#         value_type.append("Unsigned")






