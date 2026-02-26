# -*- coding: utf-8 -*-
# @file create_arxml_v2.py
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
import os, sys
import time
import re
try:
    from Rbs_Scripts.create_autosar import generate_dbc_map, load_excel_sheet, get_node_name, create_excel_sheets, \
        extractVariant
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
    list_excel_arxml = [i for i in df_arxmlmapping["dbc_file_name"].tolist() if
                        not (pd.isnull(i))]  # read dbc filenames from excel
    list_excel_arxml_index = [int(i) for i in df_arxmlmapping["dbc_file_name_index"].tolist() if
                              not (pd.isnull(i))]  # read dbc file index from excel
    list_excel_arxml_path = [path + "\\" + file for file in list_excel_arxml]

    # checking if all files are present in dbc directory else raise error
    for file in list_excel_arxml_path:
        if file not in arxml_files:  # checking if files defined in excel sheet are present in DBC directory
            logger.error(f"arxml filenames or file order in excel and windows directory are different -> {file}")
            raise Exception("Failed to create arxml")

    dict_arxml_files = dict(zip(list_excel_arxml_index, list_excel_arxml_path))

    if dict_arxml_files:
        logger.info(f"Found ARXML file/s --> {dict_arxml_files}")
        return dict_arxml_files
    else:
        logger.error(f"No ARXML files found in {path}")

def attributes_data_to_dict(element):
    """
    

    Args:
      element: 

    Returns:

    """
    dictt={}
    try:
        key = element.tag.replace("{http://autosar.org/schema/r4.0}","")
        value = element.text.strip()
    except:
        return dictt
    
    if key and value!="":
        if "/" in value:
            value = value.split("/")[-1]
        dictt[key] = value
    
    for child_element in element:
        child_attributes = attributes_data_to_dict(child_element)
        dictt.update(child_attributes)
    return dictt


def parse_autosar(arxml_path, channels):
    """
    

    Args:
      arxml_path: 
      channels: 

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

    frames_raw = []
    pdus_raw = []
    pdu_type_dict = {}

    can_frames_objects = root.findall(f'.//{ns}CAN-FRAME')
    for frame_obj in can_frames_objects:
        frame_name = frame_obj.find(f'{ns}SHORT-NAME').text
        dest_type = frame_obj.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PDU-REF').attrib["DEST"]
        if dest_type == "I-SIGNAL-I-PDU":
            pdu_ref = frame_obj.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PDU-REF').text.split("/")[-1]
            frames_raw.append(frame_name)
            pdus_raw.append(pdu_ref)
            pdu_type_dict.update({pdu_ref: dest_type})
        elif dest_type == "SECURED-I-PDU":
            pdu_ref = frame_obj.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PDU-REF').text.split("/")[-1].rsplit("_",maxsplit=1)[0]
            pdu_type_dict.update({pdu_ref: dest_type})
            frames_raw.append(frame_name)
            pdus_raw.append(pdu_ref)
        elif dest_type == "N-PDU":
            pdu_ref = frame_obj.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PDU-REF').text.split("/")[-1]
            pdu_type_dict.update({pdu_ref: dest_type})
            frames_raw.append(frame_name)
            pdus_raw.append(pdu_ref)


    logger.info(f"Found {len(frames_raw)} Frames")
    logger.info(f"Found {len(pdus_raw)} I-SIGNAL-I-PDU(s)")


    #extract TRANSFORMATION-TECHNOLOGYS info into dict
    transformation_technology_data = {}
    transformation_techs = root.findall(f'.//{ns}TRANSFORMATION-TECHNOLOGYS')
    for tt in transformation_techs:
        tt_data = attributes_data_to_dict(tt)
        if all(tag in tt_data.keys() for tag in ['SHORT-NAME','DATA-ID-MODE']):
            tt_name = tt_data["SHORT-NAME"]
            if tt_name not in transformation_technology_data:
                transformation_technology_data[tt_name] = tt_data["DATA-ID-MODE"]


    ''' Extract [Name] [pdu] [Byte Order] [Startbit] [Cycle Times] [PDU Groups]'''
    pdus_new = []
    frames_new = []
    signals = []
    byte_order = []
    start_bit = []
    cycle_times = []
    pdu_groups = []
    can_nodes = []
    pdu_type = []
    end_to_end_protection = []
    Block_size=[]
    Address_formate=[]
    Padding_active=[]
    STMin=[]
    MAXFC_wait=[]

    for index, pdu in enumerate(pdus_raw):
        for elem in tree.iter(tag=f"{ns}I-SIGNAL-I-PDU"):
            if elem.find(f'{ns}SHORT-NAME').text == pdu:
                sig_extract = elem.findall(signals_path)
                for sig in sig_extract:
                    signal = sig.find(f'{ns}I-SIGNAL-REF')
                    if signal is not None:
                        for _elem in tree.iter(tag=f"{ns}PDU-TRIGGERING"):
                            if pdu == _elem.find(f'{ns}I-PDU-REF').text.split("/")[-1]:
                                _node = _elem.find(f"{ns}I-SIGNAL-TRIGGERINGS/{ns}I-SIGNAL-TRIGGERING-REF-CONDITIONAL/{ns}I-SIGNAL-TRIGGERING-REF")
                                    # signal_list = _sig.findall(f"{ns}I-SIGNAL-TRIGGERING-REF")
                                    # for _signal in signal_list:
                                    #     s = _signal.text.split("/")[-1]
                                    #     if "ST" in s:
                                    #         sig_to_compare = s.split("_", maxsplit=1)[1]
                                    #     elif "RXX" in s:
                                    #         sig_to_compare = s.split("_", maxsplit=1)[1]
                                    #     else:
                                    #         temp_list = s.split("_")
                                    #         sig_to_compare = temp_list.sort()
                                    #         if temp_list[-1] == temp_list[-2]:
                                    #             temp_list.pop()
                                    #         sig_to_compare = "_".join(temp_list)
                                    #     sorted_signal = signal.text.split("/")[-1].split("_").sort()
                                    #
                                    #     if sig_to_compare == signal.text.split("/")[-1]:
                                for channel in channels:
                                    if channel in _node.text.split("/"):
                                        can_nodes.append(channel)
                                        break
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
                                pdus_new.append(elem.find(f'{ns}SHORT-NAME').text)
                                pdu_type.append(pdu_type_dict[elem.find(f'{ns}SHORT-NAME').text])
                                frames_new.append(frames_raw[index])

                                # Section Get PDU GROUP #
                                group_found = False
                                pdu_groups_arxml = root.findall(f'.//{ns}I-SIGNAL-GROUP')
                                for pdu_group in pdu_groups_arxml:
                                    pdu_group_content = pdu_group.findall(f"{ns}I-SIGNAL-REFS/{ns}I-SIGNAL-REF")
                                    
                                    end_to_end_transformation_data = attributes_data_to_dict(pdu_group)
                                    end_to_end_transformation_present = all(tag in end_to_end_transformation_data.keys() for tag in ['TRANSFORMER-REF','DATA-ID'])
                                    
                                    end_to_end = None
                                    if end_to_end_transformation_present:
                                        if end_to_end_transformation_data['TRANSFORMER-REF'] in transformation_technology_data:
                                            end_to_end = end_to_end_transformation_data['TRANSFORMER-REF'] + "/" + transformation_technology_data[end_to_end_transformation_data['TRANSFORMER-REF']] + "/" + end_to_end_transformation_data['DATA-ID']
                                        
                                    for sig_group in pdu_group_content:
                                        if signal.text.split("/")[-1] == sig_group.text.split("/")[-1]:
                                            pdu_groups.append(pdu_group.find(f"{ns}SHORT-NAME").text)
                                            group_found = True
                                            if end_to_end_transformation_present:
                                                end_to_end_protection.append(end_to_end)
                                            else:
                                                end_to_end_protection.append(None)
                                            break
                                if group_found is False:
                                    pdu_groups.append(None)
                                    end_to_end_protection.append(None)

                                # END Section PDU GROUP #
                                cycle_time = elem.find(cycle_time_path)
                                if cycle_time is not None:
                                    cycle_times.append(float(cycle_time.text) * 1000)
                                else:
                                    cycle_times.append(0)
                                Block_size.append(None)
                                Padding_active.append(None)
                                Address_formate.append(None)
                                MAXFC_wait.append(None)
                                STMin.append(None)

        for elem in tree.iter(tag=f"{ns}N-PDU"):
            if elem.find(f'{ns}SHORT-NAME').text == pdu and re.search(r'NPdu|nPdu|NPDU', pdu):
                if "FC" not in elem.find(f'{ns}SHORT-NAME').text:
                    for sigelem in tree.iter(tag=f"{ns}I-SIGNAL-I-PDU"):
                        if sigelem.find(f'{ns}SHORT-NAME').text in "_".join(elem.find(f'{ns}SHORT-NAME').text.split("_")[0:2]):
                            sig_extract = sigelem.findall(signals_path)
                            for sig in sig_extract:
                                signal = sig.find(f'{ns}I-SIGNAL-REF')
                                if signal is not None:
                                    for _elem in tree.iter(tag=f"{ns}PDU-TRIGGERING"):
                                        if _elem.find(f'{ns}I-PDU-REF').text.split("/")[-1] in sigelem.find(f'{ns}SHORT-NAME').text:
                                            for _sig in _elem.find(f"{ns}I-SIGNAL-TRIGGERINGS"):
                                                signal_list = _sig.findall(f"{ns}I-SIGNAL-TRIGGERING-REF")   
                                                for _signal in signal_list:
                                                    s = _signal.text.split("/")[-1]
                                                    if "ST" in s:
                                                        sig_to_compare = s.split("_", maxsplit=1)[1]
                                                    elif "RXX" in s:
                                                        sig_to_compare=s.split("_", maxsplit=1)[1]
                                                    else:
                                                        temp_list = s.split("_", maxsplit=2)
                                                        sig_to_compare = temp_list[0] + "_" + temp_list[1]
                                                    if "_".join(elem.find(f'{ns}SHORT-NAME').text.split("_")[0:2]) == sig_to_compare:    #skip signal same as pdu name 
                                                        break;
                                                    if sig_to_compare == signal.text.split("/")[-1]:
                                                        can_nodes.append(_signal.text.split("/")[4])
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
                                                        pdus_new.append(sigelem.find(f'{ns}SHORT-NAME').text)
                                                        pdu_type.append("I-SIGNAL-I-PDU")
                                                        frames_new.append(frames_raw[index])
                                                        pdu_group = elem.find(pdu_group_path)
                                                        # Section Get PDU GROUP #
                                                        group_found = False
                                                        pdu_groups_arxml = root.findall(f'.//{ns}I-SIGNAL-GROUP')
                                                        for pdu_group in pdu_groups_arxml:
                                                            pdu_group_content = pdu_group.findall(f"{ns}I-SIGNAL-REFS/{ns}I-SIGNAL-REF")
                                                            
                                                            end_to_end_transformation_data = attributes_data_to_dict(pdu_group)
                                                            end_to_end_transformation_present = all(tag in end_to_end_transformation_data.keys() for tag in ['TRANSFORMER-REF','DATA-ID'])
                                                            
                                                            end_to_end = None
                                                            if end_to_end_transformation_present:
                                                                if end_to_end_transformation_data['TRANSFORMER-REF'] in transformation_technology_data:
                                                                    end_to_end = end_to_end_transformation_data['TRANSFORMER-REF'] + "/" + transformation_technology_data[end_to_end_transformation_data['TRANSFORMER-REF']] + "/" + end_to_end_transformation_data['DATA-ID']
                                                                
                                                            for sig_group in pdu_group_content:
                                                                if signal.text.split("/")[-1] == sig_group.text.split("/")[-1]:
                                                                    pdu_groups.append(pdu_group.find(f"{ns}SHORT-NAME").text)
                                                                    group_found = True
                                                                    if end_to_end_transformation_present:
                                                                        end_to_end_protection.append(end_to_end)
                                                                    else:
                                                                        end_to_end_protection.append(None)
                                                                    break
                                                        if group_found is False:
                                                            pdu_groups.append(None)
                                                            end_to_end_protection.append(None)
                                                        cycle_time = sigelem.find(cycle_time_path)
                                                        if cycle_time is not None:
                                                            cycle_times.append(float(cycle_time.text) * 1000)
                                                        else:
                                                            cycle_times.append(0)	
                                                        Block_size.append(None)
                                                        Padding_active.append(None)
                                                        Address_formate.append(None)
                                                        MAXFC_wait.append(None)
                                                        STMin.append(None)
                            break;
                    
                pdus_new.append(elem.find(f'{ns}SHORT-NAME').text)
                pdu_type.append(pdu_type_dict[elem.find(f'{ns}SHORT-NAME').text])
                frames_new.append(frames_raw[index])
                cycle_times.append(0)
                signals.append(elem.find(f'{ns}SHORT-NAME').text)
                pdu_group = elem.find(pdu_group_path)
                pdu_groups.append(None)
                end_to_end_protection.append(None)
                for elem0 in tree.iter(tag=f"{ns}CAN-FRAME-TRIGGERING"):
                    if "_" in elem0.find(f'{ns}SHORT-NAME').text:
                        if "Tp" in pdu:
                            pdu_cmp=pdu.replace("_Tp","")
                        else:
                            pdu_cmp=pdu
                        if elem0.find(f'{ns}SHORT-NAME').text.split("_",1)[1] == pdu_cmp:
                            node_name = elem0.find(f"{ns}PDU-TRIGGERINGS/{ns}PDU-TRIGGERING-REF-CONDITIONAL/{ns}PDU-TRIGGERING-REF").text.split("/")[-2]
                            can_nodes.append(node_name)

                for elem1 in tree.iter(tag=f"{ns}CAN-FRAME"):
                    if elem1.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PDU-REF').text.split("/")[-1] == pdu:
                        order = elem1.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}PACKING-BYTE-ORDER')
                        if order is not None:
                            if order.text == "MOST-SIGNIFICANT-BYTE-LAST":
                                byte_order.append("Intel")
                            elif order.text == "MOST-SIGNIFICANT-BYTE-FIRST":
                                byte_order.append("Motorola")
                            else:
                                byte_order.append(order.text)
                        else:
                            byte_order.append(None)
                        start_bit.append(elem1.find(f'{ns}PDU-TO-FRAME-MAPPINGS/{ns}PDU-TO-FRAME-MAPPING/{ns}START-POSITION').text)
                        break
                for elem2 in root.findall(f'.//{ns}CAN-TP-CONFIG//{ns}TP-CONNECTIONS//{ns}CAN-TP-CONNECTION'):
                    if pdu in elem2.find(f'{ns}DATA-PDU-REF').text.split("/")[-1]:
                        if elem2.find(f'{ns}MAX-BLOCK-SIZE') is not None:
                            Block_size.append(elem2.find(f'{ns}MAX-BLOCK-SIZE').text)
                        else:
                            Block_size.append(None)
                        if elem2.find(f'{ns}ADDRESSING-FORMAT') is not None:
                            Address_formate.append(elem2.find(f'{ns}ADDRESSING-FORMAT').text)
                        else:
                            Address_formate.append(None)
                        if elem2.find(f'{ns}PADDING-ACTIVATION') is not None:
                            Padding_active.append(elem2.find(f'{ns}PADDING-ACTIVATION').text)
                        else:
                            Padding_active.append(None)
                        break
                    elif elem2.find(f'{ns}FLOW-CONTROL-PDU-REF')is not None:
                        if pdu in elem2.find(f'{ns}FLOW-CONTROL-PDU-REF').text.split("/")[-1]:
                            if elem2.find(f'{ns}MAX-BLOCK-SIZE') is not None:
                                Block_size.append(elem2.find(f'{ns}MAX-BLOCK-SIZE').text)
                            else:
                                Block_size.append(None)
                            if elem2.find(f'{ns}ADDRESSING-FORMAT') is not None:
                                Address_formate.append(elem2.find(f'{ns}ADDRESSING-FORMAT').text)
                            else:
                                Address_formate.append(None)
                            if elem2.find(f'{ns}PADDING-ACTIVATION') is not None:
                                Padding_active.append(elem2.find(f'{ns}PADDING-ACTIVATION').text)
                            else:
                                Padding_active.append(None)
                            break
                if "FC" in pdu:
                    for elem3 in root.findall(f'.//{ns}CAN-TP-CONFIG//{ns}TP-NODES//{ns}CAN-TP-NODE'):
                            if  "Toliman" in elem3.find(f'{ns}SHORT-NAME').text:
                                str_name="_".join(elem3.find(f'{ns}SHORT-NAME').text.split("_")[1:3])
                                if str_name in pdu:
                                    MAXFC_wait.append(elem3.find(f'{ns}MAX-FC-WAIT').text)
                                    STMin.append(elem3.find(f'{ns}ST-MIN').text)
                else:
                    STMin.append(None)
                    MAXFC_wait.append(None)
                       

                
    logger.info(f"Found {len(signals)} signals")
    logger.info(f"Found {len(byte_order)} byte orders")
    logger.info(f"Found {len(start_bit)} start bits")
    logger.info(f"Found {len(end_to_end_protection)} end_to_end_protection")

    transmission_dir_pointer = []
    message_ids = []


    frames = root.findall(f'.//{ns}CAN-FRAME-TRIGGERING')
    for frame_ in frames_new:
        for frame_obj in frames:
            if frame_ in frame_obj.find(f'{ns}FRAME-REF').text.split("/")[-1]:
                port_ref = frame_obj.find(f'{ns}FRAME-PORT-REFS/{ns}FRAME-PORT-REF').text.split("/")[-1]
                transmission_dir_pointer.append(port_ref)
                message_id = frame_obj.find(f'{ns}IDENTIFIER').text
                base16INT = int(message_id)
                hex_value = hex(base16INT)
                message_ids.append(hex_value.upper())

    try:

        ''' Extract [Initial Value] [Length] and system signal reference'''
        initial_values = []
        signals_length = []
        sys_sig = []
        base_types = []
        CANTP_protocol=[]
        node = root.findall(f'.//{ns}I-SIGNAL')
        for sig in signals:
            Sig_found=False
            for elem in node:
                if sig == elem.find(f'{ns}SHORT-NAME').text:
                    CANTP_protocol.append("No")
                    Sig_found=True
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
            
            if Sig_found==False:
                for elem in tree.iter(tag=f"{ns}N-PDU"):
                    if elem.find(f'{ns}SHORT-NAME').text == sig:
                        CANTP_protocol.append("Yes")
                        initial_values.append(None)
                        signals_length.append(elem.find(f'{ns}LENGTH').text)
                        base_types.append(None)
                        sys_sig.append(sig)
        
        logger.info(f"Found {len(initial_values)} initial values")
        logger.info(f"Found {len(signals_length)} signal lengths")
        logger.info(f"Found {len(sys_sig)} signal references")

        ''' Get comment , Computational method and Data method'''
        node = root.findall(f'.//{ns}I-SIGNAL')
        comments = []
        sig_to_compu = {}
        sig_to_data = {}
        for signal in sys_sig:
            syssig_flag=False
            for sig in node:
                #name = sig.find(f'{ns}SHORT-NAME').text
                name = sig.find(f'{ns}SYSTEM-SIGNAL-REF').text.split("/")[-1]
                if signal == name:
                    syssig_flag=True
                    comment = sig.find(f'{ns}DESC/{ns}L-2')
                    if comment is not None:
                        comments.append(comment.text)
                    else:
                        comments.append(None)
                    compu_method = sig.find(compu_methods_path)
                    if compu_method is not None:
                        sig_to_compu[signal] = compu_method.text.split("/")[-1]
                    else:
                        sys_sig_node = root.findall(f'.//{ns}SYSTEM-SIGNAL')
                        for sig in sys_sig_node:
                            name = sig.find(f'{ns}SHORT-NAME').text
                            if signal == name:
                                compu_method = sig.find(compu_methods_path_sys)
                                if compu_method is not None:
                                    sig_to_compu[signal] = compu_method.text.split("/")[-1]
                                else:
                                    sig_to_compu[signal] = None
                                break
                    data_method = sig.find(data_methods_path)
                    if data_method is not None:
                        sig_to_data[signal] = data_method.text.split("/")[-1]
                    else:
                        sig_to_data[signal] = None
            if syssig_flag==False:
                for elem in tree.iter(tag=f"{ns}N-PDU"):
                    if elem.find(f'{ns}SHORT-NAME').text == signal:
                        sig_to_compu[signal] = None
                        sig_to_data[signal] = None
                        comment = elem.find(f'{ns}LENGTH')
                        if comment is not None:
                            comments.append(comment.text)
                        else:
                            comments.append(None)    
        logger.info(f"Found {len(comments)} comments")

        ''' Get texttable'''
        dict_scale_linera_textable_data = {}
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
                                enum_entries.append("LogicalValue: " + texttable_entry.find(
                                    f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                                    f'{ns}COMPU-CONST/{ns}VT').text)
                            texttable_values.append("\n".join(enum_entries))
                        elif "SCALE_LINEAR_AND_TEXTTABLE" in category:
                            enum = sig.findall(enums_path)
                            linear = []
                            is_textable = True
                            for entry in enum:
                                if (name in entry.find(f'{ns}SHORT-LABEL').text) or ("CompuMethod_" in entry.find(f'{ns}SHORT-LABEL').text):
                                    is_textable = False
                                    linear = entry
                                    break
                            if is_textable:
                                signal_category.append(category.lower())
                                factors.append(1)
                                offsets.append(0)
                                enum_entries = []
                                enum_keys = []
                                for texttable_entry in enum:
                                    enum_entries.append("LogicalValue: " + texttable_entry.find(
                                        f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                                        f'{ns}COMPU-CONST/{ns}VT').text)
                                    enum_keys.append(int(texttable_entry.find(f'{ns}LOWER-LIMIT').text))
                                texttable_values.append("\n".join(enum_entries))
                                if name not in dict_scale_linera_textable_data.keys():
                                    dict_scale_linera_textable_data[name] = {"min":min(enum_keys), "max":max(enum_keys)}
                            else:
                                signal_category.append(category.lower())
                                try:
                                    factors.append(float(sig.find(factors_path_type_1).text))
                                    offsets.append(float(sig.find(offsets_path_type_1).text))
                                except:
                                    factors.append(float(sig.find(factors_path_type_2).text))
                                    offsets.append(float(sig.find(offsets_path_type_2).text))
                                enum = sig.findall(enums_path)
                                enum_entries = []
                                for texttable_entry in enum:
                                    is_valid_symbol = texttable_entry.find(f'{ns}SYMBOL')
                                    if is_valid_symbol is not None:
                                        enum_entries.append("LogicalValue: " + texttable_entry.find(
                                            f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                                            f'{ns}COMPU-CONST/{ns}VT').text)
                                texttable_values.append("\n".join(enum_entries))

                                if name not in dict_scale_linera_textable_data.keys():
                                    dict_scale_linera_textable_data[name] = {"min":int(linear.find(f'{ns}LOWER-LIMIT').text,0),"max":int(linear.find(f'{ns}UPPER-LIMIT').text, 0)}
                        elif category.startswith(("SCALE_LINEAR", "LINEAR")):
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
            if data in dict_scale_linera_textable_data.keys():
                list_minimums.append(dict_scale_linera_textable_data[data]["min"])
                list_maximums.append(dict_scale_linera_textable_data[data]["max"])
                continue
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
                            texttable_min = int(min_texttable.text, 0)
                            max_values_texttable_signal = sig.findall(texttabble_max_value_path)
                            max_val_enum = max_values_texttable_signal[-1]
                            max_ = max_val_enum.find(f'{ns}UPPER-LIMIT')
                            texttable_max = int(max_.text, 0)
                            if texttable_min > texttable_max:
                                list_minimums.append(texttable_max)
                                list_maximums.append(texttable_min)
                            else:
                                list_minimums.append(texttable_min)
                                list_maximums.append(texttable_max)

        logger.info(f"Found {len(list_minimums)} minimum values")
        logger.info(f"Found {len(list_maximums)} maximum values")

        directions = []
        ports = root.findall(f'.//{ns}FRAME-PORT')
        for transmission in transmission_dir_pointer:
            for port in ports:
                if transmission == port.find(f'{ns}SHORT-NAME').text:
                    directions.append(port.find(f'{ns}COMMUNICATION-DIRECTION').text)

        # can_nodes = []
        # nodes = root.findall(f'.//{ns}I-SIGNAL-TRIGGERING-REF')
        # for sig in signals:
        #     for node in nodes:
        #         if sig == node.text.split("/")[-1].split("_")[-1]:
        #             can_nodes.append(node.text.split("/")[3])
        return list(zip(signals, pdus_new, pdu_type, frames_new, pdu_groups, start_bit, signals_length, byte_order, initial_values, factors,
                offsets, list_minimums, list_maximums, message_ids, cycle_times, signal_category, texttable_values, end_to_end_protection,
                Block_size,Address_formate,Padding_active,STMin,MAXFC_wait,directions,can_nodes))
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
        dir_string = "OUT"
    elif direction.lower() == "rx":
        dir_string = "IN"
    else:
        raise "Unknown signal direction"

    # try:
    #     tree = ET.parse(arxml_path)
    #     root = tree.getroot()
    #     ns = "{http://autosar.org/schema/r4.0}"
    # except Exception as e:
    #     logger.error(f"Failed parsing {arxml_path}. Reason --> {e}")
    #     raise e

    # can_nodes = []
    # nodes = root.findall(f'.//{ns}CAN-FRAME-TRIGGERING')
    # for sig in signals_full_data:
    #     for node in nodes:
    #         sig_to_pdu = node.findall(f"{ns}I-SIGNAL-I-PDUS/{ns}I-SIGNAL-I-PDU-REF-CONDITIONAL/{ns}I-SIGNAL-I-PDU-REF")
    #         for el in sig_to_pdu:
    #             if sig[1] == el.text.split("/")[-1] and sig[-1] in node.find(f'{ns}SHORT-NAME').text and sig[
    #                 -2] == node.find(f'{ns}COMMUNICATION-DIRECTION').text:
    #                 can_nodes.append(sig)

    # can_nodes = []
    # nodes = root.findall(f'.//{ns}I-SIGNAL-I-PDU-GROUP')
    # for sig in signals_full_data:
    #     for node in nodes:
    #         sig_to_pdu = node.findall(f"{ns}I-SIGNAL-I-PDUS/{ns}I-SIGNAL-I-PDU-REF-CONDITIONAL/{ns}I-SIGNAL-I-PDU-REF")
    #         for el in sig_to_pdu:
    #             if sig[1] == el.text.split("/")[-1] and sig[-1] in node.find(f'{ns}SHORT-NAME').text and sig[-2] == node.find(f'{ns}COMMUNICATION-DIRECTION').text:
    #                 can_nodes.append(sig)
    # return can_nodes


    ''' Separate nodes'''
    dbc_node = []
    for signal in signals_full_data:
        if signal[-2] == dir_string and signal[-1] == excel_node[0]:
            dbc_node.append(signal)
    return dbc_node

    # logger.info(f"Found {len(comments)} comments")


def create_dataframe(data, variant_dict):
    """
    

    Args:
      data: 
      variant_dict: 

    Returns:

    """
    try:
        data_for_excel = []
        for elem in data: # remove last two elements which are not needed for the DataFrame
            normalized = elem[:-2]
            data_for_excel.append(normalized)

        ''' Create the dataframe'''

        df = pd.DataFrame(data_for_excel,
                          columns=['Name', 'pdu', "PDU Type", 'Message', "Multiplexing/Group", 'Startbit', 'Length [Bit]', 'Byte Order', "Initial Value",
                                   'Factor', 'Offset', 'Minimum',
                                   'Maximum', 'Message ID', 'Cycle Time [ms]', 'texttable', 'texttable values', 'EndToEndProtection', 'Block_size','Address_formate','Padding_active','STMin','MAXFC_wait'])
        
        # columns_to_add = {"group": 1}
        columns_to_add = {"group": 1, 'Value Type': 9, 'Unit': 15, 'Value Table': 16,
                          'Comment': 17,
                          "max_value": 23, "dlc": 24, "variant": 25}
        for key, value in columns_to_add.items():
            df.insert(value, key, np.nan)

        # fill variants
        for i, row in df.iterrows():
            # fill variant column
            if row['pdu'] in variant_dict["a_variant"]:
                df["variant"][i] = "a_variant"
            elif row['pdu'] in variant_dict["b_variant"]:
                df["variant"][i] = "b_variant"
            else:
                df["variant"][i] = "Common"

            # fill max_value column
            df["max_value"][i] = (2 ** (int(df["Length [Bit]"][i]))) - 1

        logger.info("Filled variant, max_value columns")

        return df
    except Exception as e:
        logger.error(f"Failed to create dataframe --> {e}")
        raise e


def write_to_excel(sheets_dict):
    """
    

    Args:
      sheets_dict: 

    Returns:

    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    try:
        ''' Writing the excel'''
        logger.info("Opening Autosar_Gen_Database.xlsx for writing...")
        with pd.ExcelWriter(script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx',
                            engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for sheet, value in sheets_dict.items():
                value.to_excel(writer, index=False, sheet_name=sheet)
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
    sheets_to_write = {}
    start_time = time.time()
    script_path = os.path.dirname(os.path.abspath(__file__))
    excel_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'
    arxml_map = generate_dbc_map(excel_path, "ArxmlMapping")
    variant_dict = extractVariant(excel_path, "ArxmlMapping")
    wb, sheet_list, autosar_directory = load_excel_sheet()
    list_node, dict_node, dict_ecu_name, tx_messages, block_messages, direction = get_node_name(wb, "ArxmlMapping", True)
    arxmls = get_arxml_list(arxmls_path, excel_path)
    for _map in arxml_map:
        arxml_index = _map[1]
        sheet_index = _map[0]
        channels = dict_ecu_name.values()
        channels_reduced = list(set([item for sublist in channels for item in sublist]))
        data = parse_autosar(arxmls[arxml_index], channels_reduced)
        specific_node_data = create_nodes(data, arxmls[arxml_index], dict_ecu_name[list_node[sheet_index]],
                                          direction[sheet_index])
        df_to_write = create_dataframe(specific_node_data, variant_dict)
        sheets_to_write[list_node[sheet_index]] = df_to_write
    write_to_excel(sheets_to_write)
    logger.info(f"Arxml(s) parsed for {time.time() - start_time} seconds")

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
