# -*- coding: utf-8 -*-
# @file create_arxml_eth.py
# @author ADAS_HIL_TEAM
# @date 12-05-2023

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

"""
extracts needed data from arxml for ethernet
"""

from copy import deepcopy

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
import traceback

try:
    from Rbs_Scripts.create_autosar import generate_dbc_map, load_excel_sheet, get_node_name, create_excel_sheets, \
        extractVariant
    from Rbs_Scripts.classicarxml_parser import ClassicArxmlParser
    from Rbs_Scripts.adaptive_arxml_parser import getAdaptiveSomeIpData
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from create_autosar import generate_dbc_map, load_excel_sheet, get_node_name, create_excel_sheets, extractVariant
    from classicarxml_parser import ClassicArxmlParser
    from adaptive_arxml_parser import getAdaptiveSomeIpData

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

eth_column_names = ('Service',
                    'Service Instance',
                    'Service ID',
                    'Major version',
                    'Minor version',
                    'Instance ID',
                    'Member Type',
                    'Event Group',
                    'Event_GroupId',
                    'Field Name',
                    'Member',
                    'Member ID',
                    'Field Type',
                    'Parameter',
                    'Parameter Type',
                    'No of Parameters',
                    'parameter_dtype_l1',
                    'parameter_dtype_l2',
                    'parameter_dtype_l3',
                    'parameter_dtype_l4',
                    'parameter_dtype_l5',
                    'Signal',
                    'No of Elements',
                    'Fire_and_forget',
                    "Signal_Group",
                    "PDU",
                    "PDU_Type",
                    "Payload_PDU_Type",
                    "Payload_PDU",
                    "Selector_Field_Signal",
                    "Startbit",
                    "PDU_Length [Byte]",
                    "Signal_Length [Bit]",
                    "Initial Value",
                    "max_value",
                    "Cycle Time [ms]",
                    "texttable",
                    "texttable values",
                    "Value Type",
                    "Comment",
                    "dlc",
                    "variant",
                    "Value Table",
                    "EndToEndProtection",
                    'Signal Data Type',
                    'Byte Order',
                    'Factor',
                    'Offset',
                    'Minimum',
                    'Maximum',
                    'Unit',
                    'IP_Address',
                    'UDP_Port',
                    'TCP_Port',
                    'TP_Protocol',
                    'VLAN_ID',
                    'VLAN_Name',
                    'SD Type',
                    "Network Protocol",
                    'Autosar Type')


def data_extractor(element):
    """
    Iterates an attribute object till it finds an end point and adds the found data to dict
    Args:
        element (object): xml element to iterate

    Returns:
        dict: {attribute_name: value}

    """
    dictt = {}
    try:
        key = element.tag.replace(ns, "")
        value = element.text.strip()
    except:
        return dictt

    if key and value != "":
        if "/" in value:
            value = value.split("/")[-1]
        dictt[key] = value

    for child_element in element:
        child_attributes = data_extractor(child_element)
        dictt.update(child_attributes)
    return dictt



def getSystemSignalRef(pdu_triggerings, normal_pdus_packages, signal_packages, required_pdu_triggering_name):
    """
    takes pdu triggering name as input and returns associated system signal name
    Args:
        pdu_triggerings (list): list of pdu triggerings
        normal_pdus_packages (list): list of normal pdu packages
        signal_packages (list): list of signal packages
        required_pdu_triggering_name (str): required pdu trigerring name

    Returns:
        str: system_signal_ref if found else None
    """
    for pdu_triggering in pdu_triggerings:
        if required_pdu_triggering_name == pdu_triggering.find(f'.//{ns}SHORT-NAME').text:
            #print(required_pdu_triggering_name)
            required_pdu_name = pdu_triggering.find(f'.//{ns}I-PDU-REF').text.split("/")[-1]
            for pdu in normal_pdus_packages:
                if required_pdu_name == pdu.find(f'.//{ns}SHORT-NAME').text:
                    #print(required_pdu_name)
                    required_isignal_name = pdu.find(f'.//{ns}I-SIGNAL-TO-PDU-MAPPINGS//{ns}I-SIGNAL-TO-I-PDU-MAPPING//{ns}I-SIGNAL-REF').text.split("/")[-1]
                    for isignal in signal_packages:
                        if required_isignal_name == isignal.find(f'.//{ns}SHORT-NAME').text:
                            #print(required_isignal_name)
                            system_signal_ref = isignal.find(f'.//{ns}SYSTEM-SIGNAL-REF')
                            if system_signal_ref is not None:
                                return system_signal_ref.text.split("/")[-1]
                            else:
                                return None
    return None



def getNameFromRef(ref):
    """
    splits by / and returns last element
    Args:
        ref (str): string to split

    Returns:
        ref value
    """
    return ref.split("/")[-1]


def calculateMethodID(header_id):
    """
    calculate method id from header id
    Args:
        header_id (int): header id

    Returns:
        int: method id

    """
    method_id_hex = str(hex(header_id))[-4:]
    return int(method_id_hex,16)

def calculateEventID(header_id):
    """
    calculate event id from header id
    Args:
        header_id (int): header id

    Returns:
        int: event id

    """
    event_id_hex = str(hex(header_id))[-3:]
    return int(event_id_hex,16)

def extract_digits(evgid):
    match = re.search(r'_(\d+)$', evgid)
    if match:
        return match.group(1)
    return None


primitive_data_compu_method_ref = f'{ns}SW-DATA-DEF-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}COMPU-METHOD-REF'

primitive_data_unit_ref = f'{ns}SW-DATA-DEF-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}UNIT-REF'

def getClassicSomeIpData(arxml_file_path, eth_nwt_name):
    """
    main function ,gets someip data from given arxml file in given node and network
    Args:
        arxml_file_path (str): arxml file path
        eth_nwt_name (str): eth nwt name to parse

    Returns:
        dict: excel rows for rbs and node sheet
    """

    datatype_tags = {'APPLICATION-RECORD-DATA-TYPE':'STRUCTURE', 'APPLICATION-PRIMITIVE-DATA-TYPE':'VALUE', 'APPLICATION-ARRAY-DATA-TYPE':'ARRAY'}

    def find_data_structure(dest, name):
        datatype_info = DICT_DATATYPE_DATA[dest][name].copy()
        if dest == 'APPLICATION-PRIMITIVE-DATA-TYPE':
            return datatype_info
        elif dest == 'APPLICATION-ARRAY-DATA-TYPE':
            # if datatype_info['elem_dtype'] == 'VALUE':
            #     datatype_info.update(DICT_DATATYPE_DATA[datatype_info['element_info']['DEST']][datatype_info['element_info']['text']])
            #     del datatype_info['element_info']
            #     return datatype_info
            # else:
            datatype_info['element_info'] = find_data_structure(datatype_info['element_info']['DEST'], datatype_info['element_info']['text'])
            return datatype_info
        elif dest == 'APPLICATION-RECORD-DATA-TYPE':
            structure_elements_list = []
            for struct_elem in DICT_DATATYPE_DATA[dest][name]:
                if struct_elem['elem_dtype'] == 'VALUE':
                    structure_elements_list.append(struct_elem)
                else:
                    temp = struct_elem.copy()
                    temp['element_info'] = find_data_structure(struct_elem['element_info']['DEST'], struct_elem['element_info']['text'])
                    structure_elements_list.append(temp)
            return structure_elements_list
        logger.warning(f"Unknown data structure -> {dest} -> {name}")
        return []
        
    def generate_namespace(data, prefix='', result=None):
        if result is None:
            result = {}
        if isinstance(data, dict):
            if 'elem_name' in data:
                
                namespace = f'{prefix}.{data["elem_name"]}' if prefix else data["elem_name"]
                if 'array_name' in data:
                    arr_size = data['array_max_size']
                    namespace = f'{prefix}.2D_ARRAY_[{arr_size}]' if prefix else f'2D_ARRAY_[{arr_size}]'
                    

                if data['elem_dtype'] == 'STRUCTURE':
                    generate_namespace(data['element_info'], namespace, result)
                elif data['elem_dtype'] == 'ARRAY':
                    arr_size = data['element_info']['array_max_size']
                    array_namespace = f'{namespace}[{arr_size}]'
                    if data['element_info']['elem_dtype'] == 'VALUE':
                        result[data['elem_name']] = {
                            'namespace': array_namespace,
                            'minimum': data['element_info']['element_info'].get('Minimum', None),
                            'maximum': data['element_info']['element_info'].get('Maximum', None),
                            'unit': data['element_info']['element_info'].get('unit', None),
                            'elem_base_type': data['element_info']['element_info'].get('elem_base_type', None)
                        }
                    else:
                        generate_namespace(data['element_info']['element_info'], array_namespace, result)
                elif data['elem_dtype'] == 'VALUE':
                    if data.get('array_name', None) is not None:
                        result[data['elem_name']] = {
                            'namespace': namespace,
                            'minimum': data['element_info'].get('Minimum', None),
                            'maximum': data['element_info'].get('Maximum', None),
                            'unit': data['element_info'].get('unit', None),
                            'elem_base_type': data['element_info'].get('elem_base_type', None)
                        }
                    else:
                        result[data['elem_name']] = {
                            'namespace': namespace,
                            'minimum': data.get('Minimum', None),
                            'maximum': data.get('Maximum', None),
                            'unit': data.get('unit', None),
                            'elem_base_type': data.get('elem_base_type', None)
                    }
            else:  # if the dictionary is a list of elements
                for item in data.values():
                    generate_namespace(item, prefix, result)
        elif isinstance(data, list):
            for element in data:
                generate_namespace(element, prefix, result)
        return result

    tree = ET.parse(arxml_file_path)
    root = tree.getroot()

    #mapping sheet
    eth_cluster_packages = root.findall(f'.//{ns}ETHERNET-CLUSTER')

    normal_pdus_packages = root.findall(f'.//{ns}I-SIGNAL-I-PDU') #--> i-signal-ref
    signal_packages = root.findall(f'.//{ns}I-SIGNAL')  #--> system signal
    pdu_triggerings = root.findall(f'.//{ns}PDU-TRIGGERING')  #--> i-signal-i-pdu-ref



    logger.info(f"-------------------Start Extraction -> cluster-{eth_nwt_name}----------------")


    datatype_mapping = {"APPLICATION-ARRAY-DATA-TYPE":"ARRAY",
                       "APPLICATION-RECORD-DATA-TYPE":"STRUCTURE",
                       "APPLICATION-PRIMITIVE-DATA-TYPE":"VALUE"}
    array_types = root.findall(f'.//{ns}APPLICATION-ARRAY-DATA-TYPE')
    structure_types = root.findall(f'.//{ns}APPLICATION-RECORD-DATA-TYPE')
    primitive_types = root.findall(f'.//{ns}APPLICATION-PRIMITIVE-DATA-TYPE')

    comput_methods = root.findall(f'.//{ns}COMPU-METHOD')

    base_types = root.findall(f'.//{ns}SW-BASE-TYPE')
    implementation_dtypes = root.findall(f'.//{ns}IMPLEMENTATION-DATA-TYPE')
    data_type_maps = root.findall(f'.//{ns}DATA-TYPE-MAP')
                              


    DICT_DATATYPE_DATA = {}

    #base types
    DICT_DATATYPE_DATA["SW-BASE-TYPE"] = {}
    for base_type in base_types:
        base_type_name = base_type.find(f'.//{ns}SHORT-NAME').text
        native_declaration = base_type.find(f'.//{ns}NATIVE-DECLARATION')
        if native_declaration is not None:
            native_declaration = native_declaration.text
            DICT_DATATYPE_DATA["SW-BASE-TYPE"][base_type_name] = native_declaration
        else:
            DICT_DATATYPE_DATA["SW-BASE-TYPE"][base_type_name] = base_type_name

    #implementation data types
    DICT_DATATYPE_DATA["IMPLEMENTATION-DATA-TYPE"] = {}
    for impl_type in implementation_dtypes:
        impl_type_name = impl_type.find(f'.//{ns}SHORT-NAME').text
        category = impl_type.find(f'.//{ns}CATEGORY').text
        if category == "VALUE":
            base_type_ref = impl_type.find(f'.//{ns}BASE-TYPE-REF')
            if base_type_ref is not None:
                base_type = base_type_ref.text.split("/")[-1]
                DICT_DATATYPE_DATA["IMPLEMENTATION-DATA-TYPE"][impl_type_name] = DICT_DATATYPE_DATA["SW-BASE-TYPE"].get(base_type, base_type)

    #data type maps
    DICT_DATATYPE_DATA["DATA-TYPE-MAP"] = {}
    for dtype_map in data_type_maps:
        application_dtype_ref = dtype_map.find(f'.//{ns}APPLICATION-DATA-TYPE-REF')
        implementation_dtype_ref = dtype_map.find(f'.//{ns}IMPLEMENTATION-DATA-TYPE-REF')
        if application_dtype_ref is not None and implementation_dtype_ref is not None:
            application_dtype = application_dtype_ref.text.split("/")[-1]
            implementation_dtype = implementation_dtype_ref.text.split("/")[-1]
            DICT_DATATYPE_DATA["DATA-TYPE-MAP"][application_dtype] = DICT_DATATYPE_DATA["IMPLEMENTATION-DATA-TYPE"].get(implementation_dtype, implementation_dtype) #gets the base type {app_dtype: base type}

    #comput_method
    DICT_DATATYPE_DATA["COMPU-METHOD"] = {}
    for com_method in comput_methods:
        compu_name = com_method.find(f'.//{ns}SHORT-NAME').text
        try:
            category = com_method.find(f'.//{ns}CATEGORY').text
            unit = com_method.find(f'.//{ns}UNIT-REF')
            if unit is not None:
                unit = unit.text.split("/")[-1].replace("NoUnit","")
            else:
                unit=""

            temp = {}
            temp["unit"] = unit
            temp["elem_dtype"] = "VALUE"
            if category == "LINEAR" or category == "SCALE_LINEAR":
                temp["Minimum"] = com_method.find(min_value_path).text
                temp["Maximum"] = com_method.find(max_value_path).text
                #factor offset
            elif category == "TEXTTABLE":
                com_scales = com_method.findall(f'.//{ns}COMPU-SCALE')
                t=[]
                texttable = ""
                for cs in com_scales:
                    key = cs.find(f'.//{ns}LOWER-LIMIT').text
                    t.append(int(key))
                    value = cs.find(f'.//{ns}SHORT-LABEL').text
                    texttable+=f"{key}: {value}\n"
                temp["Minimum"] = min(t)
                temp["Maximum"] = max(t)
            elif category=="IDENTICAL":
                #min max not present for identical type
                temp["Minimum"] = ""
                temp["Maximum"] = ""
            else:
                temp["Minimum"] = com_method.find(min_value_path).text
                temp["Maximum"] = com_method.find(max_value_path).text
            #print(temp)
            DICT_DATATYPE_DATA["COMPU-METHOD"][compu_name] = temp
        except Exception as e:
            #logger.warning(f"Error occurred while extracting Computation method info of -> {compu_name} -> {e}")
            continue

    logger.info(f"Found {len(DICT_DATATYPE_DATA['COMPU-METHOD'])} Computation definitions")

    #primitive datatype
    DICT_DATATYPE_DATA["APPLICATION-PRIMITIVE-DATA-TYPE"] = {}
    for pt in primitive_types:
        pt_name = pt.find(f'.//{ns}SHORT-NAME').text
        try:
            unit_ref = pt.find(primitive_data_unit_ref)
            if unit_ref is not None:
                unit = unit_ref.text.split("/")[-1]
            else:
                unit = None
            comu_method_ref = pt.find(primitive_data_compu_method_ref)
            if comu_method_ref is None:
                #logger.warning(f'COMPU-METHOD not defined for primitive datatype -> {pt_name}')
                DICT_DATATYPE_DATA["APPLICATION-PRIMITIVE-DATA-TYPE"][pt_name] = {'elem_dtype':'VALUE', 'unit': unit, 'elem_base_type': DICT_DATATYPE_DATA["DATA-TYPE-MAP"].get(pt_name, '')}
                #logger.warning(f'Computation method not found for {pt_name} APPLICATION-PRIMITIVE-DATA-TYPE')
            else:
                tag = comu_method_ref.get("DEST")
                name = comu_method_ref.text.split("/")[-1]
                try:
                    if unit is None:
                        unit=DICT_DATATYPE_DATA[tag][name].get('unit','')
                    temp = DICT_DATATYPE_DATA[tag][name].copy()
                    temp.update({'unit':unit, 'elem_base_type': DICT_DATATYPE_DATA["DATA-TYPE-MAP"].get(pt_name, '')})
                    
                    DICT_DATATYPE_DATA["APPLICATION-PRIMITIVE-DATA-TYPE"][pt_name] = temp
                except:
                    DICT_DATATYPE_DATA["APPLICATION-PRIMITIVE-DATA-TYPE"][pt_name] = {'elem_dtype':'VALUE', 'unit': unit, 'elem_base_type': DICT_DATATYPE_DATA["DATA-TYPE-MAP"].get(pt_name, '')}
                #logger.warning(f"error -> {tag}  -- {name}")

        except Exception as e:
            logger.warning(f"Error occurred while extracting primitive datatype info of -> {pt_name} -> {e}")
            continue
    logger.info(f"Found {len(DICT_DATATYPE_DATA['APPLICATION-PRIMITIVE-DATA-TYPE'])} primitive datatype")


    #struture datatype
    DICT_DATATYPE_DATA["APPLICATION-RECORD-DATA-TYPE"] = {}
    for struct in structure_types:
        stuct_name =struct.find(f'.//{ns}SHORT-NAME').text
        elements = struct.findall(f'.//{ns}APPLICATION-RECORD-ELEMENT')
        data = []
        for elem in elements:
            elem_dict ={}
            elem_dict["elem_name"] = elem.find(f'.//{ns}SHORT-NAME').text
            try:
                category = elem.find(f'.//{ns}CATEGORY').text
                ty_ref = elem.find(f'.//{ns}TYPE-TREF')
                ty_dest = ty_ref.get("DEST")
                ty_name = ty_ref.text.split("/")[-1]
                elem_dict["elem_dtype"] = datatype_mapping[ty_dest]
                if category != "VALUE":
                    elem_ref = {"DEST":ty_dest, "text":ty_name}
                    elem_dict["element_info"] = elem_ref
                else:
                    try:
                        elem_dict.update(DICT_DATATYPE_DATA[ty_dest][ty_name])
                    except:
                        pass
                data.append(elem_dict)
            except Exception as e:
                logger.warning(f"Error occurred while extracting structure info of -> {elem_dict['elem_name']} -> {e}")
                continue

        DICT_DATATYPE_DATA["APPLICATION-RECORD-DATA-TYPE"][stuct_name] = data

    logger.info(f"Found {len(DICT_DATATYPE_DATA['APPLICATION-RECORD-DATA-TYPE'])} Structure datatype")


    #Array datatype
    DICT_DATATYPE_DATA["APPLICATION-ARRAY-DATA-TYPE"] = {}
    for array in array_types:
        array_name = array.find(f'.//{ns}SHORT-NAME').text
        try:
            array_elem = array.find(f'.//{ns}ELEMENT')
            temp = {}
            temp["array_name"] = array_name
            temp["array_max_size"] = array_elem.find(f'.//{ns}MAX-NUMBER-OF-ELEMENTS').text
            elem_tref = array.find(f'.//{ns}TYPE-TREF')
            elem_type = elem_tref.get("DEST")
            elem_name = elem_tref.text.split("/")[-1]
            temp["elem_name"] = elem_name
            temp["elem_dtype"] = datatype_mapping[elem_type]

            temp["element_info"] = {"DEST":elem_type,"text":elem_name}

            DICT_DATATYPE_DATA["APPLICATION-ARRAY-DATA-TYPE"][array_name] = temp
        except Exception as e:
            logger.warning(f"Error occurred while extracting array info of -> {array_name} -> {e}")
            continue
    logger.info(f"Found {len(DICT_DATATYPE_DATA['APPLICATION-ARRAY-DATA-TYPE'])} Array datatype")



    """
    # #resync Structure datatype
    for struc_name, struct_data in DICT_DATATYPE_DATA["APPLICATION-RECORD-DATA-TYPE"].items():
        try:
            for i,elem in enumerate(struct_data):
                if "element_info" in elem.keys():
                    info = DICT_DATATYPE_DATA[elem["element_info"]["DEST"]].get(elem["element_info"]["text"], {})
                    if info:
                        elem["element_info"] = info
                        DICT_DATATYPE_DATA["APPLICATION-RECORD-DATA-TYPE"][struc_name][i] = elem
        except Exception as e:
            logger.warning(f"Error occurred while resyncing structure  -> {struc_name} -> {e}")
            continue

    logger.info("Resynced Structure Datatype")

    #resync array datatype
    for array, array_data in DICT_DATATYPE_DATA["APPLICATION-ARRAY-DATA-TYPE"].items():
        try:
            if 'DEST' in array_data["element_info"]:
                array_data["element_info"] = DICT_DATATYPE_DATA[array_data["element_info"]["DEST"]][array_data["element_info"]["text"]]
        except Exception as e:
            logger.warning(f"Error occurred while resyncing array  -> {array_name} -> {e}")
            continue
    logger.info("Resynced Array Datatype")
    """


    # # Interface Information Extract

    # In[7]:



    interfaces = {"CLIENT-SERVER-OPERATION": {},
                 "VARIABLE-DATA-PROTOTYPE": {},
                  "TRIGGER":{}
                  }

    CSIs = root.findall(f'.//{ns}CLIENT-SERVER-INTERFACE')
    SRIs = root.findall(f'.//{ns}SENDER-RECEIVER-INTERFACE')
    TIs = root.findall(f'.//{ns}TRIGGER-INTERFACE')

    for ti in TIs:
        ti_name = ti.find(f'.//{ns}SHORT-NAME').text
        triggers = ti.findall(f'.//{ns}TRIGGER')
        if triggers:
            interfaces["TRIGGER"][ti_name] = {}

        for trigger in triggers:
            trigger_info = {}
            trigger_name = trigger.find(f'.//{ns}SHORT-NAME').text
            trigger_info['Member_name'] = trigger_name
            trigger_info["Member_type"] = "trigger"
            trigger_info["Fire_and_forget"] = 'true'
            interfaces["TRIGGER"][ti_name][trigger_name] = trigger_info

    logger.info(f"Found {len(interfaces['TRIGGER'])} TRIGGER interface definitions")


    for csi in CSIs:
        csi_name = csi.find(f'.//{ns}SHORT-NAME').text
        operations = csi.findall(f'.//{ns}CLIENT-SERVER-OPERATION')
        if operations:
            interfaces["CLIENT-SERVER-OPERATION"][csi_name] = {}
        
        ops_info = []

        for operation in operations:
            operation_info = {}
            op_name = operation.find(f'.//{ns}SHORT-NAME').text
            try:
                operation_info["Member_name"] = op_name
                operation_info["Member_type"] = "method"
                operation_info_extract = data_extractor(operation)
                operation_info["fire_and_forget"] = operation_info_extract.get('FIRE-AND-FORGET', '')
                if operation_info["fire_and_forget"] in ['false', '0', 0, 'FALSE', 'False']:
                    operation_info["fire_and_forget"] = ''
                op_arguements = operation.findall(f'.//{ns}ARGUMENT-DATA-PROTOTYPE')
                op_arguements_list = []
                for arg in op_arguements:
                    arg_name = arg.find(f'.//{ns}SHORT-NAME').text
                    temp={}
                    temp["arg_name"] = arg_name
                    direction = arg.find(f'.//{ns}DIRECTION').text.upper()
                    dir_mapping = {"IN":"IN_PARAMETERS", "OUT":"RETURN_PARAMETERS","INOUT":"INOUT"}
                    #temp["direction"]="IN_PARAMETERS" if arg.find(f'.//{ns}DIRECTION').text.upper()=="IN" else "RETURN_PARAMETERS"

                    temp["direction"]=dir_mapping.get(direction,direction)

                    arg_type_ref = arg.find(f'.//{ns}TYPE-TREF')

                    arg_type = arg_type_ref.get("DEST")
                    arg_type_name = arg_type_ref.text.split("/")[-1]
                    temp["datatype"] = datatype_mapping[arg_type]
                    #temp={}
                    # try:
                    #     temp["arg_info"]=DICT_DATATYPE_DATA[arg_type][arg_type_name]
                    # except:
                    temp["arg_info"] = {"DEST":arg_type, "text":arg_type_name}
                    op_arguements_list.append(temp)
                operation_info["arguements"]=op_arguements_list

                interfaces["CLIENT-SERVER-OPERATION"][csi_name][op_name]=operation_info

            except Exception as e:
                logger.warning(f"Error occurred while extracting METHOD info of -> {op_name} -> {e}")
                continue
    logger.info(f"Found {len(interfaces['CLIENT-SERVER-OPERATION'])} METHOD interface definitions")


    #EVENTS
    for sri in SRIs:
        sri_name = sri.find(f'.//{ns}SHORT-NAME').text
        data_elemts = sri.findall(f'.//{ns}VARIABLE-DATA-PROTOTYPE')

        if data_elemts:
            interfaces["VARIABLE-DATA-PROTOTYPE"][sri_name] = {}

        for elem in data_elemts:
            elements_dict={}
            elem_name = elem.find(f'.//{ns}SHORT-NAME').text
            try:
                elements_dict["Member_name"] = elem_name
                elements_dict["Member_type"] = "event"
                elem_type_ref = elem.find(f'.//{ns}TYPE-TREF')
                elem_type = elem_type_ref.get("DEST")
                elem_type_name = elem_type_ref.text.split("/")[-1]
                elem_info = {}
                # try:
                #     elem_info = DICT_DATATYPE_DATA[elem_type][elem_type_name]
                # except:
                elem_info = {"DEST":elem_type, "text":elem_type_name}
                elements_dict["Member_info"] = elem_info

                interfaces["VARIABLE-DATA-PROTOTYPE"][sri_name][elem_name]=elements_dict
            except Exception as e:
                logger.warning(f"Error occurred while extracting EVENT variables info of -> {elem_name} -> {e}")
                continue
    logger.info(f"Found {len(interfaces['VARIABLE-DATA-PROTOTYPE'])} Event interface definitions")



    system_signal_group_dict = {}
    system_sig_groups = root.findall(f'.//{ns}SYSTEM-SIGNAL-GROUP')

    if system_sig_groups is not None:
        for sig_grp in system_sig_groups:
            sig_grp_name = sig_grp.find(f'.//{ns}SHORT-NAME').text
            try:
                sig_refs = sig_grp.findall(f'.//{ns}SYSTEM-SIGNAL-REF')
                if sig_refs is not None:
                    for sig_ref in sig_refs:
                        system_sig = sig_ref.text.split("/")[-1]
                        system_signal_group_dict[system_sig] = sig_grp_name
            except Exception as e:
                logger.warning(f"Error occurred while extracting system signal group info of -> {sig_grp_name} -> {e}")
                continue

    logger.info(f"Found {len(system_signal_group_dict)} system signal groups")


    # # DATA MAPPING Information Extract

    data_mapping = root.find(f'.//{ns}MAPPINGS//{ns}SYSTEM-MAPPING//{ns}DATA-MAPPINGS')

    DATA_MAPPING_DICT = {}

    if data_mapping is not None:
        #trigger to signal mapping
        tgg_2_signal_mappings = data_mapping.findall(f'.//{ns}TRIGGER-TO-SIGNAL-MAPPING')

        for tgg_sig_map in tgg_2_signal_mappings:
            try:
                mapp_info = data_extractor(tgg_sig_map)
                system_sig = mapp_info.get('SYSTEM-SIGNAL-REF', None)
                trigger_ref = tgg_sig_map.find(f'.//{ns}TARGET-TRIGGER-REF')
                if trigger_ref is None:
                    continue
                interface_name = trigger_ref.text.split('/')[-2]

                trigger_name = mapp_info.get('TARGET-TRIGGER-REF', None)
                if (system_sig is None) or (trigger_name is None):
                    continue

                trigger_info = interfaces["TRIGGER"].get(interface_name, {}).get(trigger_name, None)

                if trigger_info is None:
                    continue

                DATA_MAPPING_DICT[system_sig] = trigger_info
            except Exception as e:
                logger.warning(
                    f"Error occurred while extracting DATA-MAPPINGS info for system signals for CLIENT-SERVER-OPERATION-> {e}")
                continue


        #clint-server to signal
        cs_2_signal_mappings = data_mapping.findall(f'.//{ns}CLIENT-SERVER-TO-SIGNAL-MAPPING')

        for cs_sig_map in cs_2_signal_mappings:
            try:
                mapp_info = data_extractor(cs_sig_map)
                system_sig = mapp_info.get('CALL-SIGNAL-REF', None)
                target_operation_ref = cs_sig_map.find(f'.//{ns}TARGET-OPERATION-REF')
                if target_operation_ref is None:
                    continue
                interface_name = target_operation_ref.text.split('/')[-2]

                operation_name = mapp_info.get('TARGET-OPERATION-REF', None)
                if (system_sig is None) or (operation_name is None):
                    continue

                operation_info = interfaces["CLIENT-SERVER-OPERATION"].get(interface_name, {}).get(operation_name, None)

                if operation_info is None:
                    continue

                DATA_MAPPING_DICT[system_sig] = operation_info
            except Exception as e:
                logger.warning(f"Error occurred while extracting DATA-MAPPINGS info for system signals for CLIENT-SERVER-OPERATION-> {e}")
                continue

        #client-server to signal group
        cs_2_signalgrp_mappings = data_mapping.findall(f'.//{ns}CLIENT-SERVER-TO-SIGNAL-GROUP-MAPPING')

        for cs_siggrp_map in cs_2_signalgrp_mappings:
            try:
                mapp_info = data_extractor(cs_siggrp_map)
                system_siggrp = mapp_info.get('SIGNAL-GROUP-REF', None)

                target_operation_ref = cs_siggrp_map.find(f'.//{ns}TARGET-OPERATION-REF')
                if target_operation_ref is None:
                    continue
                interface_name = target_operation_ref.text.split('/')[-2]

                operation_name = mapp_info.get('TARGET-OPERATION-REF', None)
                if (system_siggrp is None) or (operation_name is None):
                    continue

                operation_info = interfaces["CLIENT-SERVER-OPERATION"].get(interface_name, {}).get(operation_name, None)

                if operation_info is None:
                    continue

                DATA_MAPPING_DICT[system_siggrp] = operation_info
            except Exception as e:
                logger.warning(f"Error occurred while extracting DATA-MAPPINGS info for system signal groups for CLIENT-SERVER-OPERATION-> {e}")
                continue

        #sender reciiver to signal mapping
        sr_2_signal_mappings = data_mapping.findall(f'.//{ns}SENDER-RECEIVER-TO-SIGNAL-MAPPING')

        for sr_sig_map in sr_2_signal_mappings:
            try:
                mapp_info = data_extractor(sr_sig_map)
                system_sig = mapp_info.get('SYSTEM-SIGNAL-REF', None)

                target_prototype_ref = sr_sig_map.find(f'.//{ns}TARGET-DATA-PROTOTYPE-REF')
                if target_prototype_ref is None:
                    continue
                interface_name = target_prototype_ref.text.split('/')[-2]

                event_name = mapp_info.get('TARGET-DATA-PROTOTYPE-REF', None)
                if (system_sig is None) or (event_name is None):
                    continue

                event_info = interfaces['VARIABLE-DATA-PROTOTYPE'].get(interface_name, {}).get(event_name, None)

                if event_info is None:
                    continue

                DATA_MAPPING_DICT[system_sig] = event_info
            except Exception as e:
                logger.warning(f"Error occurred while extracting DATA-MAPPINGS info of system signals for VARIABLE-DATA-PROTOTYPE-> {e}")
                continue


        #sender receiver to signal group mapping
        sr_2_signalgrp_mappings = data_mapping.findall(f'.//{ns}SENDER-RECEIVER-TO-SIGNAL-GROUP-MAPPING')

        for sr_siggrp_map in sr_2_signalgrp_mappings:
            try:
                mapp_info = data_extractor(sr_siggrp_map)
                system_sig_grp = mapp_info.get('SIGNAL-GROUP-REF', None)

                target_prototype_ref = sr_siggrp_map.find(f'.//{ns}TARGET-DATA-PROTOTYPE-REF')
                if target_prototype_ref is None:
                    continue
                interface_name = target_prototype_ref.text.split('/')[-2]

                event_name = mapp_info.get('TARGET-DATA-PROTOTYPE-REF', None)
                if (system_sig_grp is None) or (event_name is None):
                    continue

                event_info = interfaces['VARIABLE-DATA-PROTOTYPE'].get(interface_name, {}).get(event_name, None)

                if event_info is None:
                    continue

                DATA_MAPPING_DICT[system_sig_grp] = event_info
            except Exception as e:
                logger.warning(f"Error occurred while extracting DATA-MAPPINGS info of system signal groups for VARIABLE-DATA-PROTOTYPE-> {e}")
                continue

    logger.info(f"Found {len(DATA_MAPPING_DICT)} data mappings for system signals/grps, for METHOD and Event mapping to service.")


    #Get network endpoints
    network_endpoints_dict = {}
    eth_pythsical_channels = eth_cluster_packages[0].findall(f'.//{ns}ETHERNET-PHYSICAL-CHANNEL')
    for eth_phy_channel in eth_pythsical_channels:
        eth_phy_channel_name = eth_phy_channel.find(f'.//{ns}SHORT-NAME').text
        if eth_phy_channel_name not in network_endpoints_dict:
            network_endpoints_dict[eth_phy_channel_name] = {}
            network_endpoints = eth_phy_channel.findall(f'.//{ns}NETWORK-ENDPOINT')
            for network_endpoint in network_endpoints:
                try:
                    network_endpoint_name = network_endpoint.find(f'.//{ns}SHORT-NAME').text
                    if network_endpoint_name not in network_endpoints_dict[eth_phy_channel_name]:
                        network_endpoints_dict[eth_phy_channel_name][network_endpoint_name] = data_extractor(network_endpoint)
                except:
                    logger.warning(f"Error while extracting network endpoint info in channel {eth_phy_channel_name} -> {e}")
                    continue


    # ## Socket address provider names

    socket_address = eth_cluster_packages[0].findall(f'.//{ns}SOCKET-ADDRESS')
    provided_service_socket_address_list = []
    for sa in socket_address:
        sa_name = sa.find(f'.//{ns}SHORT-NAME').text
        try:
            provided_service_intances = sa.findall(f'.//{ns}APPLICATION-ENDPOINT//{ns}PROVIDED-SERVICE-INSTANCES//{ns}PROVIDED-SERVICE-INSTANCE')
            if provided_service_intances:
                provided_service_socket_address_list.append(sa_name)
        except Exception as e:
            logger.warning(f"Error occurred while extracting provided_service_intances info for socket_address- {sa_name}-> {e}")
            continue

    logger.info(f"Found {len(provided_service_socket_address_list)} Socket Adresses with provided services instance definition in cluster-{eth_nwt_name}")



    #------------------------------------------
    #get SOMEIP-TP-CONNECTION info - SDU to PDU mapping
    sdu_pdu_mapping = {}
    someip_tp_connections = root.findall(f'.//{ns}SOMEIP-TP-CONNECTION')
    for someip_tp_connection in someip_tp_connections:
        temp_tp_data = data_extractor(someip_tp_connection)
        if temp_tp_data:
            sdu_ref = temp_tp_data.get('TP-SDU-REF', None)
            Pdu_Ref = temp_tp_data.get('TRANSPORT-PDU-REF', None)
            if sdu_ref!=None and Pdu_Ref!=None:
                sdu_pdu_mapping[Pdu_Ref] = sdu_ref
                #sdu_ref_split = sdu_ref.split(r'/')
                #Pdu_Ref_split = Pdu_Ref.split(r'/')
                # if sdu_ref_split[-2] not in sdu_pdu_mapping:
                #     sdu_pdu_mapping[sdu_ref_split[-2]]= {}
                #sdu_pdu_mapping[sdu_ref_split[-1]] = Pdu_Ref_split[-1]



    # # connection bundles ######################################################################################################
    CONNECTION_BUNDLE_DICT = {}

    sa_bundles = eth_cluster_packages[0].findall(f'.//{ns}SOCKET-CONNECTION-BUNDLE')

    for sb in sa_bundles:
        sb_name = sb.find(f'.//{ns}SHORT-NAME').text
        try:
            server_port_ref = sb.find(f'.//{ns}SERVER-PORT-REF')

            if server_port_ref is None:
                continue

            server_port_name = getNameFromRef(server_port_ref.text)

            if (server_port_name not in provided_service_socket_address_list):
                continue

            #print(server_port_name)

            CONNECTION_BUNDLE_DICT[server_port_name] = {}


            #SOCKET-CONNECTION-IPDU-IDENTIFIER

            pdu_identifiers = sb.findall(f'.//{ns}SOCKET-CONNECTION-IPDU-IDENTIFIER')

            for pdu_identifier in pdu_identifiers:
                pdu_idfer_info = data_extractor(pdu_identifier)
                pdu_triggering_name = pdu_idfer_info.get("PDU-TRIGGERING-REF", None)
                pdu_triggering_name = sdu_pdu_mapping.get(pdu_triggering_name, pdu_triggering_name)
                try:
                    routing_group_name = pdu_idfer_info.get("ROUTING-GROUP-REF", None)

                    if (pdu_triggering_name is None) or (routing_group_name is None):
                        continue

                    system_sig_name = getSystemSignalRef(pdu_triggerings, normal_pdus_packages, signal_packages, pdu_triggering_name)

                    if system_sig_name is None:
                        continue

                    system_sig_name = system_signal_group_dict.get(system_sig_name, system_sig_name)

                    if routing_group_name not in CONNECTION_BUNDLE_DICT[server_port_name].keys():
                        CONNECTION_BUNDLE_DICT[server_port_name][routing_group_name] = []


                    member_info = DATA_MAPPING_DICT.get(system_sig_name, None)

                    if member_info is None:
                        continue

                    header_id = pdu_idfer_info.get("HEADER-ID", None)
                    if header_id:
                        member_info["Header_id"] = header_id

                    CONNECTION_BUNDLE_DICT[server_port_name][routing_group_name].append(member_info)
                except Exception as e:
                    logger.warning(f"Error occurred while extracting pdu_triggering-{pdu_triggering_name} info in a socket bundle-{sb_name} -> {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error occurred while extracting socket bundle info - {sb_name}-> {e}")
            continue
    # print('='*80)
    # print(len(CONNECTION_BUNDLE_DICT['SA_SOA_UDP_CCZM_Prvdr_1']['SoAdRG_Method_DoorService_DoorService']))
    # print(CONNECTION_BUNDLE_DICT['SA_SOA_UDP_CCZM_Prvdr_1']['SoAdRG_Method_DoorService_DoorService'])
    logger.info(f"Found {len(CONNECTION_BUNDLE_DICT)} server ports in socket bundles")


    # # Socket Address service extraction

    # In[12]:




    #qq=[]
    # classic_hpccb_serices = {"p":{},"c":{}}
    # rbs_services = {"p":{},"c":{}}

    socket_address_dict = {}
    for eth_cluster in eth_cluster_packages:
        if eth_nwt_name == eth_cluster.find(f'.//{ns}SHORT-NAME').text:
            SAs = eth_cluster.findall(f'.//{ns}SOCKET-ADDRESS')

            event_group_dict = {}
            for SA in SAs:
                sa_name = SA.find(f'.//{ns}SHORT-NAME').text
                try:
                    consumed_services = SA.findall(f'.//{ns}CONSUMED-SERVICE-INSTANCE')
                    if not(consumed_services):
                        continue
                    for cons_service in consumed_services:
                        cons_ser_name = cons_service.find(f'.//{ns}SHORT-NAME').text
                        event_group_dict[cons_ser_name] = {}
                        cons_event_groups = cons_service.findall(f'.//{ns}CONSUMED-EVENT-GROUP')
                        for cons_evg_grp in cons_event_groups:
                            evg_info = data_extractor(cons_evg_grp)
                            event_group_dict[cons_ser_name][evg_info['SHORT-NAME']] = evg_info
                except Exception as e:
                    logger.warning(f"Error occurred while extracting event_group for info socket address - {sa_name}-> {e}")
                    continue



            for SA in SAs:
                sa_name = SA.find(f'.//{ns}SHORT-NAME').text
                try:
                    #get port numbers-----------------------------------------------------
                    udp_port_number = None
                    tcp_port_number = None

                    upd_port = SA.find(f'.//{ns}APPLICATION-ENDPOINT//{ns}TP-CONFIGURATION//{ns}UDP-TP')
                    tcp_port = SA.find(f'.//{ns}APPLICATION-ENDPOINT//{ns}TP-CONFIGURATION//{ns}TCP-TP')

                    if upd_port is not None:
                        upd_port_number = data_extractor(upd_port).get("PORT-NUMBER", None)
                    if tcp_port is not None:
                        tcp_port_number = data_extractor(tcp_port).get("PORT-NUMBER", None)

                    #------------------------------------------------------------------------
                    #get ip address-----------------------------------------------------
                    ip_address = None
                    network_endpoint_ref = SA.find(f'.//{ns}NETWORK-ENDPOINT-REF')
                    if network_endpoint_ref is not None:
                        network_endpoint_name = network_endpoint_ref.text.split("/")[-1]
                        network_ep_physical_channel_name = network_endpoint_ref.text.split("/")[-2]

                        nw_ep_dict = network_endpoints_dict.get(network_ep_physical_channel_name, {}).get(network_endpoint_name, {})
                        ipv4 = nw_ep_dict.get("IPV-4-ADDRESS", None)
                        ipv6 = nw_ep_dict.get("IPV-6-ADDRESS", None)
                        if ipv4:
                            ip_address = ipv4
                        elif ipv6:
                            ip_address = ipv6
                    #------------------------------------------------------------------------
                    consumed_event_group_pakages = SA.findall(f'.//{ns}CONSUMED-EVENT-GROUP')

                    consumed_services = SA.findall(f'.//{ns}CONSUMED-SERVICE-INSTANCE')
                    provided_services = SA.findall(f'.//{ns}PROVIDED-SERVICE-INSTANCE')

                    if not(consumed_services) and not(provided_services): # skip DOIP socket address
                        continue

                    connector_ref = SA.find(f'.//{ns}CONNECTOR-REF')
                    if connector_ref is not None:
                        ecu_node_name = connector_ref.text.split("/")[-2]
                        # if ecu_node_name!= node_name: # check id node name is the required one or not in this case required is Classic hpccb
                        #     continue
                    else:
                        ecu_node_name = "VectorSimulationNode"

                    if ecu_node_name not in socket_address_dict:
                        socket_address_dict[ecu_node_name] = {"C-SERVICES":{}, "P-SERVICES":{}}

                    if ip_address not in socket_address_dict[ecu_node_name]["C-SERVICES"]:
                        socket_address_dict[ecu_node_name]["C-SERVICES"][ip_address] = {}
                    if ip_address not in socket_address_dict[ecu_node_name]["P-SERVICES"]:
                        socket_address_dict[ecu_node_name]["P-SERVICES"][ip_address] = {}


                    if consumed_services:
                        for cons_service in consumed_services:
                            dict_service_info = {}
                            dict_service_info["service_name"] = cons_service.find(f'.//{ns}SHORT-NAME').text
                            dict_service_info["ip_address"] = ip_address
                            dict_service_info["udp_port_number"] = upd_port_number
                            dict_service_info["tcp_port_number"] = tcp_port_number

                            event_groups = cons_service.findall(f'.//{ns}CONSUMED-EVENT-GROUP')
                            if event_groups:
                                eg_name_list = []
                                for eg in event_groups:
                                    eg_name_list.append("evg_"+str(eg.find(f'.//{ns}EVENT-GROUP-IDENTIFIER').text))
                                if eg_name_list:
                                    dict_service_info["event_groups"] = eg_name_list

                            temp = data_extractor(cons_service)
                            dict_service_info["minor_version"] = temp.get("CLIENT-SERVICE-MINOR-VERSION",None)
                            dict_service_info["major_version"] = temp.get("CLIENT-SERVICE-MAJOR-VERSION",None)
                            dict_service_info["SD Type"] = "consume"
                            try:
                                dict_service_info["provided_service_ref"] = temp.get("PROVIDED-SERVICE-INSTANCE-REF",None).split("/")[-1]
                            except Exception as p:
                                logger.warning(f'Provided service ref not defined in socket address {sa_name} - {ip_address} for consumed service instance {dict_service_info["service_name"]}')
                                continue

                            #routing_ref = cons_service.find(f'.//{ns}ROUTING-GROUP-REFS//{ns}ROUTING-GROUP-REF').text.split('/')[-1]
                            #dict_service_info["consumed_methods"] = routing_ref
                            #dict_service_info["consumed_methods"] = CONNECTION_BUNDLE_DICT[dict_service_info["provided_service_ref"]][routing_ref]

            #                 if node_name in SA.find(f'.//{ns}SHORT-NAME').text:
            #                     classic_hpccb_serices["c"][dict_service_info["service_name"]] = dict_service_info
            #                 else:
            #                     #rbs
            #                     rbs_services["c"][dict_service_info["service_name"]] = dict_service_info
                            socket_address_dict[ecu_node_name]["C-SERVICES"][ip_address][dict_service_info["service_name"]] = dict_service_info



                           # print("C::",cons_service.find(f'.//{ns}SHORT-NAME').text)
                    elif provided_services:
                        #print(sa_name ,"->", len(provided_services))
                        for prov_service in provided_services:
                            dict_service_info = {}
                            dict_service_info["service_name"] = prov_service.find(f'.//{ns}SHORT-NAME').text
                            dict_service_info["ip_address"] = ip_address
                            dict_service_info["udp_port_number"] = upd_port_number
                            dict_service_info["tcp_port_number"] = tcp_port_number
                            
                            #print(dict_service_info["service_name"])

                            event_handlers = prov_service.findall(f'.//{ns}EVENT-HANDLER')
                            eg_handlers_list = []
                            if event_handlers:
                                for eh in event_handlers:
                                    consumed_event_ref = eh.findall(f'.//{ns}CONSUMED-EVENT-GROUP-REF')
                                    if consumed_event_ref==[]:
                                        temp_print = dict_service_info["service_name"]
                                        logger.warning(f"Consumed Event ref not defined for {temp_print}")
                                        continue
                                    else:
                                        consumed_event_ref = consumed_event_ref[0].text
                                    split_ = consumed_event_ref.split("/")
                                    evg_grp_info = event_group_dict[split_[-2]][split_[-1]]
                                    #print(evg_grp_info)
                                    evg_grp_id = "evg_" + str(evg_grp_info['EVENT-GROUP-IDENTIFIER'])
                                    rut_grp_name = evg_grp_info['ROUTING-GROUP-REF']
                                    temp = {}
                                    temp[evg_grp_id] = CONNECTION_BUNDLE_DICT[sa_name].get(rut_grp_name, [])

                                    eg_handlers_list.append(temp)

                                dict_service_info["event_groups"] = eg_handlers_list
        #                         if eg_name_list:
        #                             dict_service_info["event_groups"] = eg_handlers_list[0] if len(eg_handlers_list)==1 else eg_handlers_list
        #                         else:
        #                             dict_service_info["event_groups"] = ""
                            else:
                                dict_service_info["event_groups"] = ""

                            temp = data_extractor(prov_service)
                            dict_service_info["service_id"] = temp.get("SERVICE-IDENTIFIER",None)
                            dict_service_info["instance_id"] = temp.get("INSTANCE-IDENTIFIER",None)
                            dict_service_info["minor_version"] = temp.get("SERVER-SERVICE-MINOR-VERSION",None)
                            dict_service_info["major_version"] = temp.get("SERVER-SERVICE-MAJOR-VERSION",None)
                            dict_service_info["SD Type"] = "provide"


                            routing_ref = prov_service.find(f'{ns}ROUTING-GROUP-REFS//{ns}ROUTING-GROUP-REF')
                            if routing_ref is not None:
                                routing_ref = routing_ref.text.split('/')[-1]
        #                         if "event" in routing_ref.lower():
        #                             print(routing_ref)
                                dict_service_info["provided_methods"] = CONNECTION_BUNDLE_DICT[sa_name].get(routing_ref, [])
        #                     else:
        #                         print(dict_service_info["service_name"])

                            #print(len(socket_address_dict[ecu_node_name]["P-SERVICES"].keys()))
                            temp = dict_service_info.copy()
                            socket_address_dict[ecu_node_name]["P-SERVICES"][ip_address][dict_service_info["service_name"]] = temp
                except Exception as e:
                    traceback.print_exc()
                    logger.warning(f"Error occurred in service info extraction from socket address - {sa_name}-> {e}")
                    continue

    logger.info("-------------------- Summary of Found Services -----------------------")
    for ecuNodeName, ecuData in socket_address_dict.items():
        for servType, servTypeData in ecuData.items():
            for ip, ip_data in servTypeData.items():
                logger.info(f"{ecuNodeName} - {servType} - {ip} - {len(ip_data)}")
    logger.info("----------------------------------------------------------------------")


    # ## get interface name for each method

    # CSIs = root.findall(f'.//{ns}CLIENT-SERVER-INTERFACE')
    # METHOD_INTERFACE_MAPPING = {}
    # for csi in CSIs:
    #     try:
    #         csi_name = csi.find(f'.//{ns}SHORT-NAME').text
    #         operations = csi.findall(f'.//{ns}CLIENT-SERVER-OPERATION')
    #         ops_info = []
    #
    #         for operation in operations:
    #             operation_info = {}
    #             op_name = operation.find(f'.//{ns}SHORT-NAME').text
    #             METHOD_INTERFACE_MAPPING[op_name] = csi_name
    #     except Exception as e:
    #         logger.warning(f"Error occurred while extracting interface names from CLIENT-SERVER-INTERFACE -> {e}")
    #         continue


    # # Create rows for Provide services

    ROWS = []

    # excel_rows = {node_name:[],"RBS":[]}
    excel_rows = {}

    for node, data in socket_address_dict.items():
        excel_rows[node] = []
        for service_type, ip_adds_dict in data.items():
            for ip_adds, services in ip_adds_dict.items():
                if service_type=="P-SERVICES":
                    for service_name, service_info in services.items():
                        try:
                            #print(service_info)
                            row = {}
                            #print(service_name)

                            prov_method = service_info.get("provided_methods", [])
                            event_groups_list = service_info.get("event_groups", [])

                            #check if no methods and events present in the arxml for this service
                            if prov_method==[]:
                                event_found = False
                                for elem in event_groups_list:
                                    for evgid, event_list in elem.items():
                                        if event_list!=[]:
                                            event_found=True
                                            break
                                if not event_found:
                                    row={}
                                    row["Service"] = service_name
                                    row["Service Instance"] = service_name
                                    row["Service ID"] = service_info["service_id"]
                                    row["Instance ID"] = service_info["instance_id"]
                                    row["Major version"] = service_info["major_version"]
                                    row["Minor version"] = service_info["minor_version"]

                                    row["IP_Address"] = service_info.get("ip_address", "")
                                    row["UDP_Port"] = service_info.get("udp_port_number", "")
                                    row["TCP_Port"] = service_info.get("tcp_port_number", "")

                                    row["SD Type"] = "provide"
                                    temp = row.copy()
                                    ROWS.append(temp)
                                    excel_rows[node].append(temp)
                                    continue

                            for member_dict in prov_method:
                                #print(member_dict)
                                member_name = member_dict["Member_name"]
                                member_type = member_dict["Member_type"]
                                fire_and_forget = member_dict.get('fire_and_forget', '')

                                # calculate method_id
                                method_id = "not_found"
                                header_id = member_dict.get("Header_id", None)

                                if header_id:
                                    method_id = calculateMethodID(int(header_id))

                                if member_type=='event':
                                    row = {}
                                    row["Service"] = service_name
                                    row["Service Instance"] = service_name
                                    row["Service ID"] = service_info["service_id"]
                                    row["Instance ID"] = service_info["instance_id"]
                                    row["Major version"] = service_info["major_version"]
                                    row["Minor version"] = service_info["minor_version"]

                                    row["IP_Address"] = service_info.get("ip_address", "")
                                    row["UDP_Port"] = service_info.get("udp_port_number", "")
                                    row["TCP_Port"] = service_info.get("tcp_port_number", "")

                                    row["SD Type"] = "provide"
                                    row["Member"] = member_name
                                    row["Member Type"] = 'method'
                                    row["Fire_and_forget"] = 'true'
                                    row["Member ID"] = method_id
                                    d_type = datatype_tags.get(member_dict['Member_info']['DEST'], None)
                                    if d_type:
                                        row['Parameter'] = member_name
                                        row['Parameter Type'] = 'IN_PARAMETERS'
                                        if d_type == 'VALUE':
                                            dtype_info = find_data_structure(member_dict['Member_info']['DEST'],
                                                                             member_dict['Member_info']['text'])
                                            row["Minimum"] = dtype_info.get('Minimum', None)
                                            row["Maximum"] = dtype_info.get('Maximum', None)
                                            row["Unit"] = dtype_info.get('unit', None)
                                            row["Signal Data Type"] = dtype_info.get('elem_base_type', None)
                                            temp = row.copy()
                                            ROWS.append(temp)
                                            excel_rows[node].append(temp)
                                        elif d_type == 'ARRAY':

                                            dtype_info = find_data_structure(member_dict['Member_info']['DEST'],
                                                                             member_dict['Member_info']['text'])
                                            row["No of Parameters"] = dtype_info["array_max_size"]

                                            namespace_info = generate_namespace(dtype_info['element_info'])
                                            # if dtype_info['elem_dtype'] == 'ARRAY':
                                            #     print('ARRAY of ARRAY passed')
                                            if dtype_info['elem_dtype'] == 'VALUE':
                                                clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                    'Maximum', 'Unit',
                                                                    'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                    'parameter_dtype_l3',
                                                                    'parameter_dtype_l4', 'parameter_dtype_l5']
                                                for col in clear_row_values:
                                                    row[col] = ''

                                                row["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                                row["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                                row["Unit"] = dtype_info['element_info'].get('unit', None)
                                                row["Signal Data Type"] = dtype_info['element_info'].get('elem_base_type', None)
                                                temp = row.copy()
                                                ROWS.append(temp)
                                                excel_rows[node].append(temp)
                                            else:
                                                for s, nms_info in namespace_info.items():
                                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                        'Maximum', 'Unit',
                                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                        'parameter_dtype_l3',
                                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                                    for col in clear_row_values:
                                                        row[col] = ''
                                                    namespace = nms_info['namespace']
                                                    if '.' in namespace:
                                                        temp_split = namespace.split('.')
                                                        signal = temp_split[-1]
                                                        if '[' in signal:
                                                            temp_split2 = signal.split('[')
                                                            row['Signal'] = temp_split2[0]
                                                            row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                        else:
                                                            row['Signal'] = signal
                                                        row["Minimum"] = nms_info.get('minimum', None)
                                                        row["Maximum"] = nms_info.get('maximum', None)
                                                        row["Unit"] = nms_info.get('unit', None)
                                                        row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                        for i, data_structure in enumerate(temp_split[:-1]):
                                                            key = f'parameter_dtype_l{i + 1}'
                                                            row[key] = data_structure
                                                    else:
                                                        if '[' in namespace:
                                                            temp_split = namespace.split('[')
                                                            row['Signal'] = temp_split[0]
                                                            row['No of Elements'] = temp_split[-1].split(']')[0]

                                                        else:
                                                            row['Signal'] = namespace
                                                        row["Minimum"] = nms_info.get('minimum', None)
                                                        row["Maximum"] = nms_info.get('maximum', None)
                                                        row["Unit"] = nms_info.get('unit', None)
                                                        row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                                    temp = row.copy()
                                                    ROWS.append(temp)
                                                    excel_rows[node].append(temp)

                                        elif d_type == 'STRUCTURE':
                                            dtype_info = find_data_structure(member_dict['Member_info']['DEST'],
                                                                             member_dict['Member_info']['text'])
                                            namespace_info = generate_namespace(dtype_info)

                                            # if dtype_info['elem_dtype'] == 'ARRAY':
                                            #     print('ARRAY of ARRAY passed')
                                            #     pass
                                            for s, nms_info in namespace_info.items():
                                                clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                    'Maximum', 'Unit',
                                                                    'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                    'parameter_dtype_l3',
                                                                    'parameter_dtype_l4', 'parameter_dtype_l5']
                                                for col in clear_row_values:
                                                    row[col] = ''
                                                namespace = nms_info['namespace']
                                                if '.' in namespace:
                                                    temp_split = namespace.split('.')
                                                    signal = temp_split[-1]
                                                    # check if array
                                                    if '[' in signal:
                                                        temp_split2 = signal.split('[')
                                                        row['Signal'] = temp_split2[0]
                                                        row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                    else:
                                                        row['Signal'] = signal
                                                    row["Minimum"] = nms_info.get('minimum', None)
                                                    row["Maximum"] = nms_info.get('maximum', None)
                                                    row["Unit"] = nms_info.get('unit', None)
                                                    row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                    for i, data_structure in enumerate(temp_split[:-1]):
                                                        key = f'parameter_dtype_l{i + 1}'
                                                        row[key] = data_structure
                                                else:
                                                    # check if array
                                                    if '[' in namespace:
                                                        temp_split = namespace.split('[')
                                                        row['Signal'] = temp_split[0]
                                                        row['No of Elements'] = temp_split[-1].split(']')[0]

                                                    else:
                                                        row['Signal'] = namespace
                                                    row["Minimum"] = nms_info.get('minimum', None)
                                                    row["Maximum"] = nms_info.get('maximum', None)
                                                    row["Unit"] = nms_info.get('unit', None)
                                                    row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                                temp = row.copy()
                                                ROWS.append(temp)
                                                excel_rows[node].append(temp)
                                        else:
                                            logger.warning(f"Unknown datatype found for event {event['Member_name']} of service {service_name}")
                                    else:
                                        logger.warning(f"Datatype mapping not found in event {event['Member_name']} of service {service_name}")
                                        temp = row.copy()
                                        ROWS.append(temp)
                                        excel_rows[node].append(temp)

                                if member_type not in ["method", "trigger"]:
                                    continue

                                if member_type=='trigger':
                                    row = {}
                                    row["Service"] = service_name
                                    row["Service Instance"] = service_name
                                    row["Service ID"] = service_info["service_id"]
                                    row["Instance ID"] = service_info["instance_id"]
                                    row["Major version"] = service_info["major_version"]
                                    row["Minor version"] = service_info["minor_version"]

                                    row["IP_Address"] = service_info.get("ip_address", "")
                                    row["UDP_Port"] = service_info.get("udp_port_number", "")
                                    row["TCP_Port"] = service_info.get("tcp_port_number", "")

                                    row["SD Type"] = "provide"
                                    row["Member"] = member_name
                                    row["Member Type"] = 'method'
                                    row["Fire_and_forget"] = 'true'
                                    row["Member ID"] = method_id
                                    temp = row.copy()
                                    ROWS.append(temp)
                                    excel_rows[node].append(temp)

                                if member_type!="method":
                                    continue

                                #print(member_name)

                                for arg_dict in member_dict.get("arguements",[]):
                                    d_type = arg_dict["datatype"]

                                    row = {}
                                    row["Service"] = service_name
                                    row["Service Instance"] = service_name
                                    row["Service ID"] = service_info["service_id"]
                                    row["Instance ID"] = service_info["instance_id"]
                                    row["Major version"] = service_info["major_version"]
                                    row["Minor version"] = service_info["minor_version"]

                                    row["IP_Address"] = service_info.get("ip_address", "")
                                    row["UDP_Port"] = service_info.get("udp_port_number", "")
                                    row["TCP_Port"] = service_info.get("tcp_port_number", "")

                                    row["SD Type"] = "provide"
                                    row["Member"] = member_name
                                    row["Member Type"] = member_type
                                    row["Member ID"] = method_id
                                    row["Fire_and_forget"] = fire_and_forget

                                    row["Parameter"] = arg_dict["arg_name"]
                                    row["Parameter Type"] = arg_dict["direction"]


                                    if d_type=='VALUE':
                                        dtype_info = find_data_structure(arg_dict["arg_info"]['DEST'], arg_dict["arg_info"]['text'])
                                        row["Minimum"] = dtype_info.get('Minimum', None)
                                        row["Maximum"] = dtype_info.get('Maximum', None)
                                        row["Unit"] = dtype_info.get('unit', None)
                                        row["Signal Data Type"] = dtype_info.get('elem_base_type', None)
                                        temp = row.copy()
                                        ROWS.append(temp)
                                        excel_rows[node].append(temp)
                                    elif d_type=='ARRAY':

                                        dtype_info = find_data_structure(arg_dict["arg_info"]['DEST'], arg_dict["arg_info"]['text'])
                                        row["No of Parameters"] = dtype_info["array_max_size"]

                                        # if dtype_info['elem_dtype'] == 'ARRAY':
                                        #     print('ARRAY of ARRAY passed')

                                        namespace_info = generate_namespace(dtype_info['element_info'])

                                        if dtype_info['elem_dtype'] == 'VALUE':
                                            clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                                'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                'parameter_dtype_l3',
                                                                'parameter_dtype_l4', 'parameter_dtype_l5']
                                            for col in clear_row_values:
                                                row[col] = ''

                                            row["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                            row["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                            row["Unit"] = dtype_info['element_info'].get('unit', None)
                                            row["Signal Data Type"] = dtype_info['element_info'].get('elem_base_type', None)
                                            temp = row.copy()
                                            ROWS.append(temp)
                                            excel_rows[node].append(temp)
                                        else:
                                            for s, nms_info in namespace_info.items():
                                                clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                                     'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                                     'parameter_dtype_l4', 'parameter_dtype_l5']
                                                for col in clear_row_values:
                                                    row[col] = ''
                                                namespace = nms_info['namespace']
                                                if '.' in namespace:
                                                    temp_split = namespace.split('.')
                                                    signal = temp_split[-1]
                                                    if '[' in signal:
                                                        temp_split2 = signal.split('[')
                                                        row['Signal'] = temp_split2[0]
                                                        row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                    else:
                                                        row['Signal'] = signal
                                                    row["Minimum"] = nms_info.get('minimum', None)
                                                    row["Maximum"] = nms_info.get('maximum', None)
                                                    row["Unit"] = nms_info.get('unit', None)
                                                    row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                    for i,data_structure in enumerate(temp_split[:-1]):
                                                        key = f'parameter_dtype_l{i+1}'
                                                        row[key] = data_structure
                                                else:
                                                    if '[' in namespace:
                                                        temp_split = namespace.split('[')
                                                        row['Signal'] = temp_split[0]
                                                        row['No of Elements'] = temp_split[-1].split(']')[0]

                                                    else:
                                                        row['Signal'] = namespace
                                                    row["Minimum"] = nms_info.get('minimum', None)
                                                    row["Maximum"] = nms_info.get('maximum', None)
                                                    row["Unit"] = nms_info.get('unit', None)
                                                    row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                                temp = row.copy()
                                                ROWS.append(temp)
                                                excel_rows[node].append(temp)

                                    elif d_type=='STRUCTURE':

                                        dtype_info = find_data_structure(arg_dict["arg_info"]['DEST'], arg_dict["arg_info"]['text'])
                                        namespace_info = generate_namespace(dtype_info)


                                        # if dtype_info['elem_dtype'] == 'ARRAY':
                                        #     print('ARRAY of ARRAY passed')
                                        #     pass
                                        for s, nms_info in namespace_info.items():
                                            clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                                 'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                                 'parameter_dtype_l4', 'parameter_dtype_l5']
                                            for col in clear_row_values:
                                                row[col] = ''
                                            namespace = nms_info['namespace']
                                            if '.' in namespace:
                                                temp_split = namespace.split('.')
                                                signal = temp_split[-1]
                                                #check if array
                                                if '[' in signal:
                                                    temp_split2 = signal.split('[')
                                                    row['Signal'] = temp_split2[0]
                                                    row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                else:
                                                    row['Signal'] = signal
                                                row["Minimum"] = nms_info.get('minimum', None)
                                                row["Maximum"] = nms_info.get('maximum', None)
                                                row["Unit"] = nms_info.get('unit', None)
                                                row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                for i,data_structure in enumerate(temp_split[:-1]):
                                                    key = f'parameter_dtype_l{i+1}'
                                                    row[key] = data_structure
                                            else:
                                                #check if array
                                                if '[' in namespace:
                                                    temp_split = namespace.split('[')
                                                    row['Signal'] = temp_split[0]
                                                    row['No of Elements'] = temp_split[-1].split(']')[0]

                                                else:
                                                    row['Signal'] = namespace
                                                row["Minimum"] = nms_info.get('minimum', None)
                                                row["Maximum"] = nms_info.get('maximum', None)
                                                row["Unit"] = nms_info.get('unit', None)
                                                row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                            temp = row.copy()
                                            ROWS.append(temp)
                                            excel_rows[node].append(temp)
                                    else:
                                        logger.warning(f"Unknown datatype found for parameter {arg_dict['arg_name']} in method {member_name} of service {service_name}")


                            for elem in event_groups_list:
                                for evgid, event_list in elem.items():
                                    for event in event_list:
                                        event_id = "not_found"
                                        header_id = event.get("Header_id", None)
                                        if header_id:
                                            event_id = calculateEventID(int(header_id))



                                        row = {}
                                        row["Service"] = service_name
                                        row["Service Instance"] = service_name
                                        row["Service ID"] = service_info["service_id"]
                                        row["Instance ID"] = service_info["instance_id"]
                                        row["Major version"] = service_info["major_version"]
                                        row["Minor version"] = service_info["minor_version"]

                                        row["IP_Address"] = service_info.get("ip_address", "")
                                        row["UDP_Port"] = service_info.get("udp_port_number", "")
                                        row["TCP_Port"] = service_info.get("tcp_port_number", "")

                                        row["SD Type"] = "provide"
                                        row["Member"] = event['Member_name']
                                        row["Member Type"] = event['Member_type']

                                        row["Event Group"] = evgid
                                        row["Event_GroupId"] = extract_digits(evgid)
                                        row["Member ID"] = event_id
                                        d_type = datatype_tags.get(event['Member_info']['DEST'], None)
                                        if d_type:
                                            if d_type == 'VALUE':
                                                dtype_info = find_data_structure(event['Member_info']['DEST'],
                                                                                 event['Member_info']['text'])
                                                row["Minimum"] = dtype_info.get('Minimum', None)
                                                row["Maximum"] = dtype_info.get('Maximum', None)
                                                row["Unit"] = dtype_info.get('unit', None)
                                                row["Signal Data Type"] = dtype_info.get('elem_base_type', None)
                                                temp = row.copy()
                                                ROWS.append(temp)
                                                excel_rows[node].append(temp)
                                            elif d_type == 'ARRAY':

                                                dtype_info = find_data_structure(event['Member_info']['DEST'],
                                                                                 event['Member_info']['text'])
                                                row["No of Parameters"] = dtype_info["array_max_size"]

                                                namespace_info = generate_namespace(dtype_info['element_info'])
                                                # if dtype_info['elem_dtype'] == 'ARRAY':
                                                #     print('ARRAY of ARRAY passed')
                                                if dtype_info['elem_dtype'] == 'VALUE':
                                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                        'Maximum', 'Unit',
                                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                        'parameter_dtype_l3',
                                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                                    for col in clear_row_values:
                                                        row[col] = ''

                                                    row["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                                    row["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                                    row["Unit"] = dtype_info['element_info'].get('unit', None)
                                                    row["Signal Data Type"] = dtype_info['element_info'].get('elem_base_type', None)
                                                    temp = row.copy()
                                                    ROWS.append(temp)
                                                    excel_rows[node].append(temp)
                                                else:
                                                    for s, nms_info in namespace_info.items():
                                                        clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                            'Maximum', 'Unit',
                                                                            'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                            'parameter_dtype_l3',
                                                                            'parameter_dtype_l4', 'parameter_dtype_l5']
                                                        for col in clear_row_values:
                                                            row[col] = ''
                                                        namespace = nms_info['namespace']
                                                        if '.' in namespace:
                                                            temp_split = namespace.split('.')
                                                            signal = temp_split[-1]
                                                            if '[' in signal:
                                                                temp_split2 = signal.split('[')
                                                                row['Signal'] = temp_split2[0]
                                                                row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                            else:
                                                                row['Signal'] = signal
                                                            row["Minimum"] = nms_info.get('minimum', None)
                                                            row["Maximum"] = nms_info.get('maximum', None)
                                                            row["Unit"] = nms_info.get('unit', None)
                                                            row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                            for i, data_structure in enumerate(temp_split[:-1]):
                                                                key = f'parameter_dtype_l{i + 1}'
                                                                row[key] = data_structure
                                                        else:
                                                            if '[' in namespace:
                                                                temp_split = namespace.split('[')
                                                                row['Signal'] = temp_split[0]
                                                                row['No of Elements'] = temp_split[-1].split(']')[0]

                                                            else:
                                                                row['Signal'] = namespace
                                                            row["Minimum"] = nms_info.get('minimum', None)
                                                            row["Maximum"] = nms_info.get('maximum', None)
                                                            row["Unit"] = nms_info.get('unit', None)
                                                            row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                                        temp = row.copy()
                                                        ROWS.append(temp)
                                                        excel_rows[node].append(temp)

                                            elif d_type == 'STRUCTURE':

                                                dtype_info = find_data_structure(event['Member_info']['DEST'],
                                                                                 event['Member_info']['text'])
                                                namespace_info = generate_namespace(dtype_info)

                                                # if dtype_info['elem_dtype'] == 'ARRAY':
                                                #     print('ARRAY of ARRAY passed')
                                                #     pass
                                                for s, nms_info in namespace_info.items():
                                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum',
                                                                        'Maximum', 'Unit',
                                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                                        'parameter_dtype_l3',
                                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                                    for col in clear_row_values:
                                                        row[col] = ''
                                                    namespace = nms_info['namespace']
                                                    if '.' in namespace:
                                                        temp_split = namespace.split('.')
                                                        signal = temp_split[-1]
                                                        # check if array
                                                        if '[' in signal:
                                                            temp_split2 = signal.split('[')
                                                            row['Signal'] = temp_split2[0]
                                                            row['No of Elements'] = temp_split2[-1].split(']')[0]

                                                        else:
                                                            row['Signal'] = signal
                                                        row["Minimum"] = nms_info.get('minimum', None)
                                                        row["Maximum"] = nms_info.get('maximum', None)
                                                        row["Unit"] = nms_info.get('unit', None)
                                                        row["Signal Data Type"] = nms_info.get('elem_base_type', None)

                                                        for i, data_structure in enumerate(temp_split[:-1]):
                                                            key = f'parameter_dtype_l{i + 1}'
                                                            row[key] = data_structure
                                                    else:
                                                        # check if array
                                                        if '[' in namespace:
                                                            temp_split = namespace.split('[')
                                                            row['Signal'] = temp_split[0]
                                                            row['No of Elements'] = temp_split[-1].split(']')[0]

                                                        else:
                                                            row['Signal'] = namespace
                                                        row["Minimum"] = nms_info.get('minimum', None)
                                                        row["Maximum"] = nms_info.get('maximum', None)
                                                        row["Unit"] = nms_info.get('unit', None)
                                                        row["Signal Data Type"] = nms_info.get('elem_base_type', None)
                                                    temp = row.copy()
                                                    ROWS.append(temp)
                                                    excel_rows[node].append(temp)
                                            else:
                                                logger.warning(f"Unknown datatype found for event {event['Member_name']} of service {service_name}")
                                        else:
                                            logger.warning(f"Datatype mapping not found in event {event['Member_name']} of service {service_name}")

                                            temp = row.copy()
                                            ROWS.append(temp)
                                            excel_rows[node].append(temp)
                                        #print(row)
                        except Exception as e:
                            logger.warning(f"Error occurred while mapping all data and creating row for service_name-{service_name}, service_type-{service_type}, node-{node} -> {e}")
                            traceback.print_exc()
                            continue

    

    # #process rows for direction INOUT
    # for i,row in enumerate(ROWS):
    #     try:
    #         mem_type=row.get("Parameter Type","")
    #         if mem_type=="INOUT":
    #             r1 = deepcopy(row)
    #             r1["Parameter Type"] = "IN_PARAMETERS"
    #             ROWS[i] = r1

    #             row["Parameter Type"] = "RETURN_PARAMETERS"
    #             ROWS.insert(i+1,row)
    #     except Exception as e:
    #         logger.error(f"Error occurred while  handling INOUT scenarios-> {e}")
    #         break


    # for sheet, data in excel_rows.items():
    #     for i, row in enumerate(data):
    #         mem_type=row.get("Parameter Type","")
    #         if mem_type=="INOUT":

    #             r1 = deepcopy(row)

    #             r1["Parameter Type"] = "RETURN_PARAMETERS"
    #             excel_rows[sheet][i] = r1

    #             row["Parameter Type"] = "IN_PARAMETERS"
    #             excel_rows[sheet].insert(i+1,row)


    # # Create rows for Comsume services

    provided_services_df = pd.DataFrame(ROWS, columns = eth_column_names)
    for node, data in socket_address_dict.items():
        for service_type, ip_adds_dict in data.items():
            for ip_adds, services in ip_adds_dict.items():
                if service_type=="C-SERVICES":
                    for service_name, service_info in services.items():
                        try:
                            row = {}
                            if service_info["SD Type"] != "consume":
                                continue
                            provided_serice_ref = service_info["provided_service_ref"]
                            minor_version = service_info["minor_version"]
                            major_version = service_info["major_version"]

                            ip_address = service_info.get("ip_address", "")
                            udp_port_number = service_info.get("udp_port_number", "")
                            tcp_port_number = service_info.get("tcp_port_number", "")

                            filtered_df = provided_services_df[((provided_services_df["Service"]==provided_serice_ref))]
                            if major_version in filtered_df["Major version"].values:
                                filtered_df = filtered_df[filtered_df["Major version"] == major_version]
                            if minor_version in filtered_df["Minor version"].values:
                                filtered_df = filtered_df[filtered_df["Minor version"] == minor_version]

                            # filtered_df = provided_services_df[
                            #     ((provided_services_df["Service"] == provided_serice_ref) &
                            #      (provided_services_df["Major version"] == major_version) &
                            #      (provided_services_df["Minor version"] == minor_version))]
                            filtered_df["IP_Address"] = ip_address
                            filtered_df["UDP_Port"] = udp_port_number
                            filtered_df["TCP_Port"] = tcp_port_number
                            filtered_df["Service"] = service_name
                            filtered_df["Service Instance"] = service_name

                            filtered_df = filtered_df.fillna("")
            #                 if node=="ClassicHPCCB":
            #                     print(len(filtered_df))
            #                     print(provided_serice_ref,"min-",minor_version,",maj-",major_version)



                            if not(filtered_df.empty):
                                if filtered_df.iloc[0]["Member Type"]=="":
                                    #print(len(filtered_df), provided_serice_ref)
                                    for i, row in filtered_df.iterrows():
                                        row["SD Type"] = "consume"
                                        excel_rows[node].append(row.to_dict())

                                else:
                                    for member_type, member_type_df in filtered_df.groupby("Member Type"):
                                        if member_type=="method":
                                            for i, row in member_type_df.iterrows():
                                                row["SD Type"] = "consume"
                                                excel_rows[node].append(row.to_dict())
                                                #print(node)
                                        elif member_type=="event":
                                            evnt_grps = service_info.get('event_groups', [])
                                            if not(evnt_grps):
                                                continue
                                            for i, row in member_type_df.iterrows():
                                                if row["Event Group"] in evnt_grps:
                                                    row["SD Type"] = "consume"
                                                    excel_rows[node].append(row.to_dict())


                        except Exception as e:
                            logger.warning(f"Error occurred while consumed instance information from provided services for service_name-{service_name}, service_type-{service_type}, node-{node} -> {e}")
                            continue

    #handle INOUT rows
    for ecu_node, data_rows in excel_rows.items():
        for i,current_row in enumerate(data_rows):
            if current_row.get('Parameter Type', '') == 'INOUT':
                r1 = current_row.copy()
                r1['Parameter Type'] = 'RETURN_PARAMETERS'
                excel_rows[ecu_node][i] = r1

                r2 = current_row.copy()
                r2['Parameter Type'] = 'IN_PARAMETERS'
                excel_rows[ecu_node].insert(i+1, r2)

    #remove consumed services which are provided by RBS and consumed also by RBS
    #excel_rows["VectorSimulationNode"] = remove_RBS_irrelevant_rows(excel_rows["VectorSimulationNode"])
    return excel_rows

def remove_RBS_irrelevant_rows(excel_rows_rbs):
    provided_rbs_service_list = []
    RBS_ROWS_filtered = []
    rbs_df = pd.DataFrame(excel_rows_rbs, columns=eth_column_names)
    rbs_df_provided = rbs_df[rbs_df['SD Type'] == 'provide']
    rbs_df_consumed = rbs_df[rbs_df['SD Type'] == 'consume']

    for i, row in rbs_df_provided.iterrows():
        RBS_ROWS_filtered.append(row.to_dict())
        temp = 'sif_' + str(row['Service ID']) +'_'+ str(row['Major version']) +'_'+ str(row['Minor version']) + '_' + str(row['Instance ID'])
        provided_rbs_service_list.append(temp)

    for i, row in rbs_df_consumed.iterrows():
        temp = 'sif_' + str(row['Service ID']) +'_'+ str(row['Major version']) +'_'+ str(row['Minor version']) + '_' + str(row['Instance ID'])
        if temp not in provided_rbs_service_list:
            RBS_ROWS_filtered.append(row.to_dict())
    
    return RBS_ROWS_filtered

def getEthernetMappingSheetData(wb, mapping_sheet_name):
    """
    gets ethernet mapping sheet data from excel
    Args:
        wb (workbook): excel workbook of autosar_excel
        mapping_sheet_name (str): mapping sheet name

    Returns:
        mapping_df (dataframe): mapping sheet dataframe
        arxml_index_map (dict): arxml index mapped to arxml file name
    """
    ws = wb[mapping_sheet_name]
    mapping_df = pd.DataFrame(ws.values)
    if len(mapping_df.dropna(how='all'))==0:
        logger.warning(f"{mapping_sheet_name} sheet is empty")
        return None,None
    col_names = list(mapping_df.iloc[0])
    mapping_df = mapping_df.iloc[1:]
    mapping_df.columns = col_names
    mapping_df = mapping_df.replace(np.nan, '', regex=True)

    #get
    arxml_index_map = {}
    for i, row in mapping_df.iterrows():
        arxml_name = row["db_file_name"]
        arxml_index = row["db_file_name_index"]
        if arxml_name:
            arxml_index_map[arxml_index] = arxml_name

    return mapping_df, arxml_index_map


def create_eth_pdu_dataframe(data):
    try:

        data_set = []
        for row_list in data:
            for row in row_list:
                data_set.append(row)
        df_template = pd.DataFrame(data_set, columns=eth_column_names)
        df_template['variant'] = df_template['variant'].fillna('')

        max_float = sys.float_info.max
        for i, row in df_template.iterrows():
            try:
                df_template.loc[i, "variant"]= 'Common'
                signal_length = row["Signal_Length [Bit]"]

                if not(is_empty_or_spaces(signal_length)):
                    byte_order = row["Byte Order"]
                    if byte_order.upper() != 'OPAQUE' and signal_length < 100:
                        max_value = (2 ** int(signal_length)) - 1
                        if max_value < max_float:
                            df_template.loc[i, "max_value"] = max_value
            except:
                pass
        df_template = df_template.reindex(columns=eth_column_names)
        return df_template
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Failed to create dataframe --> {e}")
        raise e

def write_to_excel(sheets_dict):
    """
    write dictionary data into excel

    Args:
      sheets_dict (dict): dictionary to write into excel

    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    try:
        ''' Writing the excel'''
        logger.info("Opening Autosar_Gen_Database.xlsx for writing...")
        with pd.ExcelWriter(script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx',
                            engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for sheet, value in sheets_dict.items():
                value.to_excel(writer, index=False, sheet_name=sheet)
                logger.info(f"Created sheet --> {sheet} --> rows - {len(value)}")
        logger.info('DataFrame is written to Excel File successfully.')
    except Exception as e:
        logger.info(f"Failed to write dataframe to excel --> {e}")
        raise e


def external_call():
    """ main function"""
    try:
        logger.info("########## START 'Create Node Sheets ARXML ETH' DEBUG INFORMATION ##############")
        script_path = os.path.dirname(os.path.abspath(__file__))
        arxml_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Database\DBC'
        excel_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'
        wb, sheet_list, autosar_directory = load_excel_sheet()
        if "ETHArxmlMapping" not in sheet_list:
            logger.warning(f"ETHArxmlMapping sheet not found in Autosar_Gen_Database")
            return

        # get mapping sheet data
        eth_mapping_df, arxml_index_map = getEthernetMappingSheetData(wb, "ETHArxmlMapping")
        if eth_mapping_df is None:
            logger.warning(f"ETHArxmlMapping sheet is empty in Autosar_Gen_Database")
            return

        #delete old sheets
        for sheet in sheet_list:
            if sheet.upper().startswith('ETH') and ('MAPPING' not in sheet.upper()):
                del wb[sheet]
        wb.save(excel_path)
        logger.info("Deleted old ETH node sheets")

        write_data_dict = {}

        for cluster_name, cluster_df in eth_mapping_df.groupby("db_network_node"):
            for arxml_index, arxml_index_df in cluster_df.groupby("mapping_canoe_ecu_to_db"):
                for autosar_type, autosar_type_df in arxml_index_df.groupby("autosar_type"):
                    if ';' in str(arxml_index):
                        arxml_index_list = str(arxml_index).strip().split(';')
                        arxml_file_list = [arxml_path + "\\" + arxml_index_map[int(str(arxml_index).strip())] for arxml_index in arxml_index_list]
                    else:
                        arxml_file_list = [arxml_path + "\\" + arxml_index_map[int(str(arxml_index).strip())]]

                    for arxml_file_path in arxml_file_list:
                        autosar_pdu_data = None
                        if 'classic' in autosar_type.lower():
                            extracted_data = getClassicSomeIpData(arxml_file_path, cluster_name)
                            classic_autosar_parser = ClassicArxmlParser(arxml_file_path, protocol='ETH')
                            autosar_pdu_data = classic_autosar_parser.ethernet_cluster_info
                        elif 'adaptive' in autosar_type.lower():
                            extracted_data = getAdaptiveSomeIpData(arxml_file_path)
                        else:
                            logger.warning(f"Invalid autosar type found in ETHArxmlMapping sheet for ecu-{arxml_ecu_name}")
                            continue

                        for arxml_ecu_name, ecu_df in arxml_index_df.groupby("db_ecu_name"):
                            # arxml_index = list(ecu_df["mapping_canoe_ecu_to_dbc"].unique())[0]
                            # arxml_network_cluster_name = list(ecu_df["dbc_network_node"].unique())[0]

                            for i, row in ecu_df.iterrows():
                                node_sheet_name = row["network_name"] + "_" + row["canoe_ecu_node"] + "_" + "arxml"

                                #extracted_data = getSomeIpData(arxml_file_path, arxml_network_cluster_name, arxml_ecu_name)
                                ecu_data_to_save = extracted_data.get(arxml_ecu_name,[])

                                for i, row in enumerate(ecu_data_to_save):
                                    for col, value in row.items():
                                        try:
                                            value = float(value)
                                            row[col] = value
                                            ecu_data_to_save[i] = row
                                        except:
                                            continue

                                pdu_df = None
                                if autosar_pdu_data is not None:
                                    pdu_cluster_data = autosar_pdu_data.get(cluster_name, None)
                                    if pdu_cluster_data is not None:
                                        ecu_data_from_all_chnls = []
                                        if (arxml_ecu_name.lower() in ["vectorsimulationnode", "rbs"]) or ('simulated' in arxml_ecu_name.lower()):
                                            for chnl, chnl_data in pdu_cluster_data.items():
                                                for arxml_ecu_, arxml_ecu_data_ in chnl_data.items():
                                                    ecu_data_from_all_chnls.append(arxml_ecu_data_)
                                        else:
                                            for chnl, chnl_data in pdu_cluster_data.items():
                                                if arxml_ecu_name in chnl_data:
                                                    ecu_data_from_all_chnls.append(chnl_data[arxml_ecu_name])
                                        pdu_dir = 'RX' if arxml_ecu_name.lower() in ["vectorsimulationnode", "rbs"] else 'TX'

                                        pdu_dfs = []
                                        for ecu_pdu_data in ecu_data_from_all_chnls:
                                            ecu_pdu_data = ecu_pdu_data.get(pdu_dir, None)
                                            if ecu_pdu_data is not None:
                                                pdu_df = create_eth_pdu_dataframe(ecu_pdu_data)
                                                if not (pdu_df.empty):
                                                    pdu_dfs.append(pdu_df)

                                        if len(pdu_dfs) != 0:
                                            if len(pdu_dfs) == 1:
                                                pdu_df = pdu_dfs[0]
                                            else:
                                                pdu_df = pd.concat(pdu_dfs, sort=True, ignore_index=True).fillna(np.nan)

                                df = pd.DataFrame(ecu_data_to_save, columns=eth_column_names)

                                df["Network Protocol"] = 'ETH_SOMEIP'

                                df["Member Type"] = df["Member Type"].replace(np.nan, "not_found")
                                df["Member Type"] = df["Member Type"].replace("", "not_found")


                                if 'adaptive' in autosar_type.lower():
                                    df['SD Type'] = df['SD Type'].replace('REQUIRED-SOMEIP-SERVICE-INSTANCE','consume')
                                    df['SD Type'] = df['SD Type'].replace('PROVIDED-SOMEIP-SERVICE-INSTANCE','provide')

                                if (pdu_df is not None) and not (pdu_df.empty) and not (df.empty):
                                    df = pd.concat([df, pdu_df], sort=False, ignore_index=True)
                                elif (pdu_df is not None) and not (pdu_df.empty) and (df.empty):
                                    df = pdu_df

                                df['Autosar Type'] = autosar_type

                                # df["Factor"] = 1
                                # df["Offset"] = 0
                                df = df.drop_duplicates(subset=[col for col in df.columns if col not in ['Service', 'Service Instance']])
                                #df = df.sort_values('Service ID')

                                if (node_sheet_name in write_data_dict) and (isinstance(write_data_dict[node_sheet_name], pd.DataFrame)):
                                    write_data_dict[node_sheet_name] = pd.concat([write_data_dict[node_sheet_name], df], ignore_index=True)
                                    write_data_dict[node_sheet_name] = write_data_dict[node_sheet_name].drop_duplicates(ignore_index=True)
                                else:
                                    write_data_dict[node_sheet_name] = df
        wb.close()
        if write_data_dict != {}:
            write_to_excel(write_data_dict)
        else:
            logger.warning("Mapping Information is empty in ETHArxmlMapping sheet")

        logger.info("###### END 'Create Autosar ARXML ETH' DEBUG INFORMATION ######")
        logger.info('-' * 80)
        return True
    except Exception as exp:
        logger.error(f"Failed to create arxml: {exp}")
        traceback.print_exc()
        raise Exception(exp)
        return False


if __name__ == "__main__":
    external_call()