import xml.etree.ElementTree as ET
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
import os, sys
import time
import traceback
from lxml import etree


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
    from pattern_matching import is_empty_or_spaces
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching_arxml import *
    from pattern_matching import is_empty_or_spaces


ns = "{http://autosar.org/schema/r4.0}"

eth_column_names = ("Service",
                    "Service ID",
                    "Major version",
                    "Minor version",
                    "Instance ID",
                    "Member Type",
                    "Event Group",
                    "Member",
                    "Member ID",
                    "Parameter",
                    "Parameter Type",
                    "No of Parameters",
                    'parameter_dtype_l1',
                    'parameter_dtype_l2',
                    'parameter_dtype_l3',
                    'parameter_dtype_l4',
                    'parameter_dtype_l5',
                    "Signal",
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
                    "No of Elements",
                    "Signal Data Type",
                    "Byte Order",
                    "Factor",
                    "Offset",
                    "Minimum",
                    "Maximum",
                    "Unit",
                    "SD Type",
                    "Network Protocol"
                    )

can_column_names = ("Signal",
                    "Signal_Group",
                    "PDU",
                    "PDU_Type",
                    "Payload_PDU_Type",
                    "Payload_PDU",
                    "Selector_Field_Signal",
                    "Message",
                    "Message ID",
                    "Header ID",
                    "Startbit",
                    "PDU_Length [Byte]",
                    "Signal_Length [Bit]",
                    "Payload_PDU_Length [Byte]",
                    "Signal Base Type",
                    "Initial Value",
                    "max_value",
                    "Transmission Mode",
                    "Cycle Time [ms]",
                    "texttable",
                    "texttable values",
                    "Value Type",
                    "Comment",
                    "dlc",
                    "Payload PDU DLC",
                    "variant",
                    "Value Table",
                    "EndToEndProtection",
                    "Byte Order",
                    "Factor",
                    "Offset",
                    "Minimum",
                    "Maximum",
                    "Unit",
                    'Cantp_Pdu_Type',
                    'Block_size', 
                    'Address_formate', 
                    'Padding_active', 
                    'STMin',
                    'MAXFC_wait'
                    )

class ClassicArxmlParser:
    """communication data extraction from classic arxml file"""
    
    def __init__(self, file_path, protocol='ALL'):
        self.root = ET.parse(file_path).getroot()
        self.file = file_path
        self.ecu_instance_info = self.get_ecu_instance_info()
        if 'ETH' in protocol.upper():
            self.ethernet_cluster_info = self.get_ethernet_cluster_info()
        elif 'CAN' in protocol.upper():
            self.can_cluster_info = self.get_can_cluster_info()
        else:
            self.ethernet_cluster_info = self.get_ethernet_cluster_info()
            self.can_cluster_info = self.get_can_cluster_info()

    @staticmethod   
    def data_extractor(element):
        dictt = {}
        if element is None:
            return dictt
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
            child_attributes = ClassicArxmlParser.data_extractor(child_element)
            dictt.update(child_attributes)
        return dictt
    
    @staticmethod
    def get_ref_name(ref_path):
        return ref_path.split("/")[-1]
    
    @staticmethod
    def get_short_name(element):
        return element.find(f'{ns}SHORT-NAME').text
    
    @staticmethod
    def get_dest_and_text(element):
        dest = element.get("DEST")
        text = ClassicArxmlParser.get_ref_name(element.text)
        return dest, text

    @staticmethod
    def get_dlc(pdu_length):
        if pdu_length is None or str(pdu_length) == '':
            return ''
        try:
            pdu_length = int(pdu_length)
        except Exception as e:
            logger.warning(f"error while finding DLC using length -> {e}")

        if pdu_length<=8:
            return pdu_length
        elif (pdu_length > 8 and pdu_length <= 12):
            return 9
        elif (pdu_length > 12 and pdu_length <= 16):
            return 10
        elif (pdu_length > 16 and pdu_length <= 20):
            return 11
        elif (pdu_length > 20 and pdu_length <= 24):
            return 12
        elif (pdu_length > 24 and pdu_length <= 32):
            return 13
        elif (pdu_length > 32 and pdu_length <= 48):
            return 14
        elif (pdu_length > 48 and pdu_length <= 64):
            return 15
        return ''
    
    def get_ecu_instance_info(self):
        ecu_instance_info = {}
        communicator_tag_dict = {'CAN': 'CAN-COMMUNICATION-CONNECTOR', 'ETHERNET': 'ETHERNET-COMMUNICATION-CONNECTOR'}
        #communicator_tag_dict = {'ETHERNET': 'ETHERNET-COMMUNICATION-CONNECTOR'}

        ecu_instance_packages = self.root.findall(f'.//{ns}ECU-INSTANCE')
        for ecu_instance in ecu_instance_packages:
            ecu_instance_name = self.get_short_name(ecu_instance)
            if ecu_instance_name not in ecu_instance_info:
                ecu_instance_info[ecu_instance_name] = {}
            for protocol, connector_tag in communicator_tag_dict.items():
                if protocol not in ecu_instance_info[ecu_instance_name]:
                    ecu_instance_info[ecu_instance_name][protocol] = {}
                communication_connectors = ecu_instance.findall(f'.//{ns}{connector_tag}')
                for communication_connector in communication_connectors:
                    communication_connector_name = self.get_short_name(communication_connector)
                    if communication_connector_name not in ecu_instance_info[ecu_instance_name][protocol]:
                        ecu_instance_info[ecu_instance_name][protocol][communication_connector_name] = {'TX':[], 'RX':[]}
                    if protocol=='CAN':
                        port_packages = communication_connector.findall(f'.//{ns}FRAME-PORT')
                    else:
                        port_packages = communication_connector.findall(f'.//{ns}I-PDU-PORT')
                    for port_package in port_packages:
                        port_name = self.get_short_name(port_package)
                        port_direction = ClassicArxmlParser.data_extractor(port_package).get('COMMUNICATION-DIRECTION','')
                        if port_direction:
                            direction = 'RX' if port_direction == 'IN' else 'TX'
                            ecu_instance_info[ecu_instance_name][protocol][communication_connector_name][direction].append(port_name)

        return ecu_instance_info
    

    def get_e2e_info(self):
        """"""
        result_dict = {}
        e2e_packages = self.root.findall(f'.//{ns}END-TO-END-PROTECTION')
        for e2e_package in e2e_packages:
            try:
                e2e_name = self.get_short_name(e2e_package)
                e2e_info_dict = self.data_extractor(e2e_package)
                sig_group = e2e_info_dict.get('I-SIGNAL-GROUP-REF', None)
                e2e_info = str(e2e_info_dict.get('CATEGORY', '')) + '::' + str(e2e_info_dict.get('DATA-ID', ''))
                result_dict[sig_group] = e2e_info
            except:
                continue
        return result_dict

    

    def get_can_cluster_info(self):

        protocol = 'CAN'
        can_cluster_packages = self.root.findall(f'.//{ns}CAN-CLUSTER')
        normal_pdus_packages = self.root.findall(f'.//{ns}I-SIGNAL-I-PDU')
        nm_pdus_package = self.root.findall(f'.//{ns}NM-PDU')
        signal_packages = self.root.findall(f'.//{ns}I-SIGNAL')
        compu_method_packages = self.root.findall(f'.//{ns}COMPU-METHOD')
        system_signal_packages = self.root.findall(f'.//{ns}SYSTEM-SIGNAL')
        sig_group_packages = self.root.findall(f'.//{ns}I-SIGNAL-GROUP')
        secured_pdus_packages = self.root.findall(f'.//{ns}SECURED-I-PDU')
        container_pdus_packages = self.root.findall(f'.//{ns}CONTAINER-I-PDU')
        multiplexed_pdus_packages = self.root.findall(f'.//{ns}MULTIPLEXED-I-PDU')
        units_packages = self.root.findall(f'.//{ns}UNIT')
        can_frame_packages = self.root.findall(f'.//{ns}CAN-FRAME')
        can_tp_config_packages = self.root.findall(f'.//{ns}CAN-TP-CONFIG')
        can_tp_connection_packages = self.root.findall(f'.//{ns}CAN-TP-CONNECTION')
        sig_group_packages = self.root.findall(f'.//{ns}I-SIGNAL-GROUP')

        #process CAN-Frame
        can_frame_info_dict = {}
        for can_frame in can_frame_packages:
            can_frame_name = self.get_short_name(can_frame)
            can_frame_info_dict[can_frame_name] = can_frame
        del can_frame_packages

        #process i-signal-i-pdus
        normal_pdu_info_dict = {}
        for normal_pdu in normal_pdus_packages:
            pdu_name = self.get_short_name(normal_pdu)
            normal_pdu_info_dict[pdu_name] = normal_pdu
        del normal_pdus_packages

        #process i-signal packages
        signals_info_dict = {}
        for signal_pack in signal_packages:
            signal_name = self.get_short_name(signal_pack)
            signals_info_dict[signal_name] = signal_pack
        del signal_packages

        #process computation methods packages
        compu_methods_info_dict = {}
        for compu_method in compu_method_packages:
            compu_method_name = self.get_short_name(compu_method)
            compu_methods_info_dict[compu_method_name] = compu_method
        del compu_method_packages


        #process SYSTEM-SIGNAL packages
        system_signal_info_dict = {}
        for system_signal in system_signal_packages:
            system_signal_name = self.get_short_name(system_signal)
            system_signal_info_dict[system_signal_name] = system_signal
        del system_signal_packages

        #process I-SIGNAL-GROUP packages
        sig_groups_info_dict = {}
        for sig_group in sig_group_packages:
            sig_group_name = self.get_short_name(sig_group)
            sig_groups_info_dict[sig_group_name] = sig_group
        del sig_group_packages

        #process nm-pdus
        nm_pdus_info_dict = {}
        for nm_pdu in nm_pdus_package:
            pdu_name = self.get_short_name(nm_pdu)
            nm_pdus_info_dict[pdu_name] = nm_pdu
        del nm_pdus_package

        

        #process units
        units_mapping_info = {}
        for unit_pack in units_packages:
            unit_pack_name = self.get_short_name(unit_pack)
            display_name = unit_pack.find(f'{ns}DISPLAY-NAME')
            if display_name is not None:
                units_mapping_info[unit_pack_name] = display_name.text
            else:
                units_mapping_info[unit_pack_name] = unit_pack_name
        del units_packages

        #process can_tp_config ->  cantp_connection_info
        cantp_connection_info_dict = {}
        for can_tp_config in can_tp_config_packages:
            tp_config_cluster = can_tp_config.find(f'{ns}COMMUNICATION-CLUSTER-REF')
            if tp_config_cluster is not None:
                tp_config_cluster = self.get_ref_name(tp_config_cluster.text)
                cantp_connection_info_dict[tp_config_cluster] = {'DATA_PDU':[], 'FLOWCONTROL_PDU':[]}
                can_tp_cons = can_tp_config.findall(f'.//{ns}CAN-TP-CONNECTION')
                for can_tp_connection in can_tp_cons:
                    sdu_pdu_ref = can_tp_connection.find(f'{ns}TP-SDU-REF')
                    if sdu_pdu_ref is None:
                        continue
                    data_pdu_ref = can_tp_connection.find(f'{ns}DATA-PDU-REF')
                    if data_pdu_ref is not None:
                        data_pdu_ref_name = self.get_ref_name(data_pdu_ref.text)
                        cantp_connection_info_dict[tp_config_cluster]['DATA_PDU'].append(data_pdu_ref_name)

                    flow_control_pdu_ref = can_tp_connection.find(f'{ns}FLOW-CONTROL-PDU-REF')
                    if flow_control_pdu_ref is not None:
                        flow_control_pdu_ref_name = self.get_ref_name(flow_control_pdu_ref.text)
                        cantp_connection_info_dict[tp_config_cluster]['FLOWCONTROL_PDU'].append(flow_control_pdu_ref_name)
                    

        #process container pdus
        container_pdus_info = {}
        container_pdu_info_main = {}
        for container_pdu in container_pdus_packages:
            container_pdu_name = self.get_short_name(container_pdu)
            if container_pdu_name not in container_pdu_info_main:
                container_pdu_info_main[container_pdu_name] = []
            container_pdu_length = container_pdu.find(f'{ns}LENGTH').text
            for pdu_triggering in container_pdu.findall(f'.//{ns}CONTAINED-PDU-TRIGGERING-REF'):
                ref_text = pdu_triggering.text.split("/")
                clus_name = ref_text[-3]
                chnl_name = ref_text[-2]
                triggering_name = ref_text[-1]
                container_pdu_info_main[container_pdu_name].append(triggering_name)

                if clus_name not in container_pdus_info:
                    container_pdus_info[clus_name] = {}
                if chnl_name not in container_pdus_info[clus_name]:
                    container_pdus_info[clus_name][chnl_name] = {}
                if container_pdu_name not in container_pdus_info[clus_name][chnl_name]:
                    container_pdus_info[clus_name][chnl_name][container_pdu_name] = {}

                container_pdus_info[clus_name][chnl_name][container_pdu_name]['name'] = container_pdu_name
                container_pdus_info[clus_name][chnl_name][container_pdu_name]['length'] = int(container_pdu_length)

        del container_pdus_packages

        #process multiplexed pdus
        multiplexed_pdus_info = {}       #isignalipdu as key
        multiplexed_pdus_main_dict = {}  #multiplexed pdu as key
        for multiplexed_pdu in multiplexed_pdus_packages:
            multiplexed_pdu_name = self.get_short_name(multiplexed_pdu)
            try:
                multiplexed_pdu_length = multiplexed_pdu.find(f'{ns}LENGTH').text

                multiplexed_pdus_main_dict[multiplexed_pdu_name] = []

                #selector field info
                selector_field_length = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-LENGTH').text
                selector_field_start_position = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-START-POSITION').text
                selector_field_byte_order = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-BYTE-ORDER').text

                #get dynamic part info
                dynamic_part_alternatives = multiplexed_pdu.findall(f'.//{ns}DYNAMIC-PART-ALTERNATIVE')
                for dynamic_part_alternative in dynamic_part_alternatives:
                    dynamic_pdu_info = ClassicArxmlParser.data_extractor(dynamic_part_alternative)
                    dynamic_part_pdu_ref = dynamic_pdu_info.get('I-PDU-REF', None)
                    if dynamic_part_pdu_ref:
                        is_initial_dynamic_part = dynamic_pdu_info.get('INITIAL-DYNAMIC-PART', False)
                        is_initial_dynamic_part = True if is_initial_dynamic_part == 'true' else False
                        multiplexed_pdus_main_dict[multiplexed_pdu_name].append(dynamic_part_pdu_ref)
                        multiplexed_pdus_info[dynamic_part_pdu_ref] = {'selector_field_length': selector_field_length, 
                                                                    'selector_field_start_position': selector_field_start_position, 
                                                                    'selector_field_byte_order': selector_field_byte_order,
                                                                    'multiplexed_pdu_length': multiplexed_pdu_length,
                                                                    'multiplexed_pdu_name': multiplexed_pdu_name,
                                                                    'container_pdu_type': 'MULTIPLEXED-I-PDU',
                                                                    'dynamic_part': True,
                                                                    'is_initial_dynamic_part': is_initial_dynamic_part}
                        
                #get static part info
                static_parts = multiplexed_pdu.findall(f'.//{ns}STATIC-PART')
                for static_part in static_parts:
                    static_pdu_ref = self.get_ref_name(static_part.find(f'{ns}I-PDU-REF').text)
                    if static_pdu_ref:
                        multiplexed_pdus_main_dict[multiplexed_pdu_name].append(dynamic_part_pdu_ref)
                        multiplexed_pdus_info[static_pdu_ref] = {'selector_field_length': selector_field_length, 
                                                        'selector_field_start_position': selector_field_start_position, 
                                                        'selector_field_byte_order': selector_field_byte_order,
                                                        'multiplexed_pdu_length': multiplexed_pdu_length,
                                                        'multiplexed_pdu_name': multiplexed_pdu_name,
                                                        'container_pdu_type': 'MULTIPLEXED-I-PDU',
                                                        'dynamic_part': False} 
            except Exception as e:
                logger.warning(f'Multiplexed pdu info not found for -> {multiplexed_pdu_name}')
                continue          
        del multiplexed_pdus_packages


        
        self.e2e_definitions = self.get_e2e_info()

        #start extraction
        results_dict = {}
        for can_cluster in can_cluster_packages:
            can_cluster_name = self.get_short_name(can_cluster)
            if can_cluster_name not in results_dict:
                results_dict[can_cluster_name] = {}
            #channels/vlans
            physical_channels_packages = can_cluster.findall(f'.//{ns}CAN-PHYSICAL-CHANNEL')
            for physical_channel in physical_channels_packages:
                physical_channel_name = self.get_short_name(physical_channel)
                if physical_channel_name not in results_dict[can_cluster_name]:
                    results_dict[can_cluster_name][physical_channel_name] = {}

                pdu_triggerings_info_dict = {}
                pdu_triggerings = physical_channel.findall(f'.//{ns}PDU-TRIGGERING')
                for pdu_trig_package in pdu_triggerings:
                    pdu_trig_package_name = self.get_short_name(pdu_trig_package)
                    pdu_triggerings_info_dict[pdu_trig_package_name] = pdu_trig_package
                del pdu_triggerings


                for can_frame_triggering in physical_channel.findall(f'.//{ns}CAN-FRAME-TRIGGERING'):
                    self.frame_entity = [{}]  # Create a single entity which encapsulates all data inside one CAN frame
                    """ Get References """
                    frame_port_ref = can_frame_triggering.find(f'.//{ns}FRAME-PORT-REF').text.split("/")[-1]
                    frame_ref = can_frame_triggering.find(f'.//{ns}FRAME-REF').text.split("/")[-1]
                    pdu_triggering_ref = can_frame_triggering.find(f'.//{ns}PDU-TRIGGERING-REF')
                    if pdu_triggering_ref is not None:
                        pdu_triggering_ref = self.get_ref_name(pdu_triggering_ref.text)
                        if pdu_triggering_ref not in pdu_triggerings_info_dict:
                            continue

                    ''' TYPE and DIRECTION(IN/OUT) to the list '''
                    pdu_type, pdu_ref = self.get_can_frame_data(can_frame_info_dict.get(frame_ref, None))

                    """ Add corresponding PDU name """
                    self.frame_entity[0]['PDU'] = pdu_ref

                    ''' Extract Message ID '''
                    message_id = can_frame_triggering.find(f'{ns}IDENTIFIER').text
                    hex_value = hex(int(message_id))
                    self.frame_entity[0]['Message ID'] = hex_value.upper()


                    #check if container pdu is present
                    container_pdu_info_ = container_pdus_info.get(can_cluster_name, {}).get(physical_channel_name, {}).get(pdu_ref, {})
                    container_pdu = container_pdu_info_.get('name', '')
                    container_pdu_length = container_pdu_info_.get('length', '')
                    if container_pdu:
                        container_pdu_info = {'con_pdu_name': container_pdu, 'con_pdu_type': 'CONTAINER-I-PDU', 'length':container_pdu_length}
                    else:
                        container_pdu_info = {}



                    ''' Call function to collect all signals data inside current PDU'''
                    if pdu_type == "I-SIGNAL-I-PDU":
                        ''' Add not necessary fields for non NPDUs '''

                        multiplexed_pdu_info_data = multiplexed_pdus_info.get(pdu_ref, {})

                        normal_pdu_package = normal_pdu_info_dict.get(pdu_ref, None)
                        if normal_pdu_package is None:
                            continue

                        self.get_i_signal_i_pdu_data(protocol,pdu_ref, pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info, container_pdu_info, multiplexed_pdu_info_data)
                        self.frame_entity.pop(0)
                        ''' Append collected single frame data to the main data list '''
                        # can_frames_full_data.append(self.frame_entity)  # Add current set to the big data set
                    elif pdu_type == "MULTIPLEXED-I-PDU":
                        multiplexing_pdu_list = multiplexed_pdus_main_dict.get(pdu_ref, [])
                        for multiplexing_pdu in multiplexing_pdu_list:
                            multiplexed_pdu_info_data = multiplexed_pdus_info.get(multiplexing_pdu, {})
                            normal_pdu_package = normal_pdu_info_dict.get(multiplexing_pdu, None)
                            if normal_pdu_package is None:
                                continue
                            self.get_i_signal_i_pdu_data(protocol,multiplexing_pdu, pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info, container_pdu_info, multiplexed_pdu_info_data)
                            
                            #self.frame_entity.pop(0)
                            ''' Append collected single frame data to the main data list '''
                            # can_frames_full_data.append(self.frame_entity)  # Add current set to the big data set

                    elif pdu_type == "SECURED-I-PDU":
                        for secured_pdu in secured_pdus_packages:
                            if pdu_ref == secured_pdu.find(f'.//{ns}SHORT-NAME').text:
                                payload_ref = secured_pdu.find(f'.//{ns}PAYLOAD-REF').text.split("/")[-1]
                                break
                        pdu_triggering = pdu_triggerings_info_dict.get(payload_ref, None)

                        # for pdu_triggering in pdu_triggerings:
                        #     if payload_ref == pdu_triggering.find(f'.//{ns}SHORT-NAME').text:
                        if pdu_triggering is not None:
                            payload_pdu = pdu_triggering.find(f'.//{ns}I-PDU-REF').text.split("/")[-1]
                            self.frame_entity[0]['Payload_PDU'] = payload_pdu

                        # break
                        
                        normal_pdu_package = normal_pdu_info_dict.get(payload_pdu, None)
                        if normal_pdu_package is None:
                            continue
                        

                        self.get_i_signal_i_pdu_data(protocol,payload_pdu, pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info)
                        # can_frames_full_data.append(self.frame_entity)  # Add current set to the big data set

                    elif pdu_type == "NM-PDU":
                        nm_pdu_package = nm_pdus_info_dict.get(pdu_ref, None)
                        if nm_pdu_package is None:
                            continue
                        self.get_i_signal_i_pdu_data(protocol,pdu_ref, pdu_type, nm_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info)

                        ''' Append collected single frame data to the main data list '''
                        self.frame_entity.pop(0)
                        # can_frames_full_data.append(self.frame_entity)  # Add current set to the big data set
                    elif pdu_type == "N-PDU":
                        try:
                            pdu_ref_tp, npdu_special_info, control_type = self.get_can_tp_data(pdu_ref, can_tp_connection_packages)

                        except:
                            pdu_ref_tp = None
                        if pdu_ref_tp is None:
                            del self.frame_entity
                            continue
                        else:

                            self.frame_entity[0].update(npdu_special_info)
                            self.frame_entity[0]["Payload_PDU"] = pdu_ref_tp  # Add pointer to I-SIG-I-PDU
                            if pdu_ref in cantp_connection_info_dict[can_cluster_name]['DATA_PDU']:
                                self.frame_entity[0]["Cantp_Pdu_Type"] =  'Data_pdu'
                            elif pdu_ref in cantp_connection_info_dict[can_cluster_name]['FLOWCONTROL_PDU']:
                                self.frame_entity[0]["Cantp_Pdu_Type"] = 'Flowcontrol_pdu'

                            if control_type == "DATA_CONTROL":
                                normal_pdu_package = normal_pdu_info_dict.get(pdu_ref_tp, None)
                                if normal_pdu_package is None:
                                    continue
                                self.get_i_signal_i_pdu_data(protocol,pdu_ref_tp, pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info)
                            # can_frames_full_data.append(self.frame_entity)  # Add current set to the big data set
                    elif pdu_type == 'CONTAINER-I-PDU':
                        contained_pdu_triggers = container_pdu_info_main.get(pdu_ref, [])
                        can_frame_data_copy = self.frame_entity.copy()
                        #give payload pdu, payload pdu type
                        self.frame_entity[0]['Payload_PDU'] = pdu_ref
                        self.frame_entity[0]['Payload_PDU_Type'] = 'CONTAINER-I-PDU'

                        for contained_pdu_trigger in contained_pdu_triggers:

                            contained_pdu_type, contained_pdu_ref  = self.get_pdu_triggering_data(contained_pdu_trigger, pdu_triggerings_info_dict.get(contained_pdu_trigger, None))
                            if contained_pdu_type == "I-SIGNAL-I-PDU":
                                multiplexed_pdu_info_data = multiplexed_pdus_info.get(contained_pdu_ref, {})

                                normal_pdu_package = normal_pdu_info_dict.get(contained_pdu_ref, None)
                                if normal_pdu_package is None:
                                    continue

                                self.get_i_signal_i_pdu_data(protocol,contained_pdu_ref, contained_pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                            sig_groups_info_dict, units_mapping_info, container_pdu_info, multiplexed_pdu_info_data)
                                self.frame_entity.pop(0)
                                frame_ports = can_frame_triggering.findall(f'.//{ns}FRAME-PORT-REF')

                                for frame_port in frame_ports:
                                    try:
                                        frame_port_split = frame_port.text.split("/")
                                        node_name = frame_port_split[-3]
                                        channel_name = frame_port_split[-2]
                                        frame_port_name = frame_port_split[-1]

                                        if node_name not in results_dict[can_cluster_name][physical_channel_name]:
                                            results_dict[can_cluster_name][physical_channel_name][node_name] = {'RX':[], 'TX':[]}
                                        
                                        for direction, frame_triggering_list in self.ecu_instance_info.get(node_name, {}).get('CAN', {}).get(channel_name, {}).items():
                                            if frame_port_name in frame_triggering_list:
                                                results_dict[can_cluster_name][physical_channel_name][node_name][direction.upper()].append(self.frame_entity)   
                                    except:
                                        continue
                            self.frame_entity = can_frame_data_copy.copy()
                        continue   

                                
                    
                    frame_ports = can_frame_triggering.findall(f'.//{ns}FRAME-PORT-REF')

                    for frame_port in frame_ports:
                        try:
                            frame_port_split = frame_port.text.split("/")
                            node_name = frame_port_split[-3]
                            channel_name = frame_port_split[-2]
                            frame_port_name = frame_port_split[-1]

                            if node_name not in results_dict[can_cluster_name][physical_channel_name]:
                                results_dict[can_cluster_name][physical_channel_name][node_name] = {'RX':[], 'TX':[]}
                            
                            for direction, frame_triggering_list in self.ecu_instance_info.get(node_name, {}).get('CAN', {}).get(channel_name, {}).items():
                                if frame_port_name in frame_triggering_list:
                                    results_dict[can_cluster_name][physical_channel_name][node_name][direction.upper()].append(self.frame_entity)   
                        except:
                            continue
        return results_dict

    def get_ethernet_cluster_info(self):
        """
        Retrieves information about the Ethernet cluster from the ARXML file.

        Returns:
            dict: A dictionary containing the extracted information about the Ethernet cluster.
        """
        ethernet_cluster_packages = self.root.findall(f'.//{ns}ETHERNET-CLUSTER')
        normal_pdus_packages = self.root.findall(f'.//{ns}I-SIGNAL-I-PDU')
        nm_pdus_package = self.root.findall(f'.//{ns}NM-PDU')
        signal_packages = self.root.findall(f'.//{ns}I-SIGNAL')
        compu_method_packages = self.root.findall(f'.//{ns}COMPU-METHOD')
        system_signal_packages = self.root.findall(f'.//{ns}SYSTEM-SIGNAL')
        sig_group_packages = self.root.findall(f'.//{ns}I-SIGNAL-GROUP')
        secured_pdus_packages = self.root.findall(f'.//{ns}SECURED-I-PDU')

        container_pdus_packages = self.root.findall(f'.//{ns}CONTAINER-I-PDU')
        multiplexed_pdus_packages = self.root.findall(f'.//{ns}MULTIPLEXED-I-PDU')

        units_packages = self.root.findall(f'.//{ns}UNIT')

        def get_autosar_pdutriggering_list(phy_chnl_name, physical_channel_package):
            sc_ipdu_identifiers = physical_channel_package.findall(f'.//{ns}SOCKET-CONNECTION-BUNDLE//{ns}PDUS//{ns}SOCKET-CONNECTION-IPDU-IDENTIFIER')
            if sc_ipdu_identifiers is None or sc_ipdu_identifiers == []:
                return None
            autosar_pdu_triggerings = []
            for pdu_identifier in sc_ipdu_identifiers:
                pdu_identifier_info = self.data_extractor(pdu_identifier)
                if pdu_identifier_info.get('ROUTING-GROUP-REF', None) is None:
                    pdu_trigg = pdu_identifier_info.get('PDU-TRIGGERING-REF', None)
                    if pdu_trigg is not None:
                        autosar_pdu_triggerings.append(pdu_trigg)
            logger.info(f'Found {len(autosar_pdu_triggerings)}  PDU triggerings in {phy_chnl_name} channel.')
            return autosar_pdu_triggerings


        #process i-signal-i-pdus
        normal_pdu_info_dict = {}
        for normal_pdu in normal_pdus_packages:
            pdu_name = self.get_short_name(normal_pdu)
            normal_pdu_info_dict[pdu_name] = normal_pdu
        del normal_pdus_packages

        #process i-signal packages
        signals_info_dict = {}
        for signal_pack in signal_packages:
            signal_name = self.get_short_name(signal_pack)
            signals_info_dict[signal_name] = signal_pack
        del signal_packages

        #process computation methods packages
        compu_methods_info_dict = {}
        for compu_method in compu_method_packages:
            compu_method_name = self.get_short_name(compu_method)
            compu_methods_info_dict[compu_method_name] = compu_method
        del compu_method_packages


        #process SYSTEM-SIGNAL packages
        system_signal_info_dict = {}
        for system_signal in system_signal_packages:
            system_signal_name = self.get_short_name(system_signal)
            system_signal_info_dict[system_signal_name] = system_signal
        del system_signal_packages

        #process I-SIGNAL-GROUP packages
        sig_groups_info_dict = {}
        for sig_group in sig_group_packages:
            sig_group_name = self.get_short_name(sig_group)
            sig_groups_info_dict[sig_group_name] = sig_group
        del sig_group_packages

        

        #process units
        units_mapping_info = {}
        for unit_pack in units_packages:
            unit_pack_name = self.get_short_name(unit_pack)
            display_name = unit_pack.find(f'{ns}DISPLAY-NAME')
            if display_name is not None:
                units_mapping_info[unit_pack_name] = display_name.text
        del units_packages

        #process container pdus
        container_pdus_info = {}
        for container_pdu in container_pdus_packages:
            container_pdu_name = self.get_short_name(container_pdu)
            container_pdu_length = container_pdu.find(f'{ns}LENGTH').text
            for pdu_triggering in container_pdu.findall(f'.//{ns}CONTAINED-PDU-TRIGGERING-REF'):
                ref_text = pdu_triggering.text.split("/")
                clus_name = ref_text[-3]
                chnl_name = ref_text[-2]
                triggering_name = ref_text[-1]

                if clus_name not in container_pdus_info:
                    container_pdus_info[clus_name] = {}
                if chnl_name not in container_pdus_info[clus_name]:
                    container_pdus_info[clus_name][chnl_name] = {}
                if triggering_name not in container_pdus_info[clus_name][chnl_name]:
                    container_pdus_info[clus_name][chnl_name][triggering_name] = {}
                
                container_pdus_info[clus_name][chnl_name][triggering_name]['name'] = container_pdu_name
                container_pdus_info[clus_name][chnl_name][triggering_name]['length'] = container_pdu_length

        del container_pdus_packages

        #process multiplexed pdus
        multiplexed_pdus_info = {}
        multiplexed_pdus_list = []
        for multiplexed_pdu in multiplexed_pdus_packages:
            multiplexed_pdu_name = self.get_short_name(multiplexed_pdu)
            try:
                multiplexed_pdu_length = multiplexed_pdu.find(f'{ns}LENGTH').text

                #selector field info
                selector_field_length = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-LENGTH').text
                selector_field_start_position = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-START-POSITION').text
                selector_field_byte_order = multiplexed_pdu.find(f'.//{ns}SELECTOR-FIELD-BYTE-ORDER').text

                #get dynamic part info
                dynamic_part_alternatives = multiplexed_pdu.findall(f'.//{ns}DYNAMIC-PART-ALTERNATIVE')
                for dynamic_part_alternative in dynamic_part_alternatives:
                    dynamic_pdu_info = ClassicArxmlParser.data_extractor(dynamic_part_alternative)
                    dynamic_part_pdu_ref = dynamic_pdu_info.get('I-PDU-REF', None)
                    if dynamic_part_pdu_ref:
                        multiplexed_pdus_list.append(dynamic_part_pdu_ref)
                        is_initial_dynamic_part = dynamic_pdu_info.get('INITIAL-DYNAMIC-PART', False)
                        is_initial_dynamic_part = True if is_initial_dynamic_part == 'true' else False
                        multiplexed_pdus_info[dynamic_part_pdu_ref] = {'selector_field_length': selector_field_length, 
                                                                    'selector_field_start_position': selector_field_start_position, 
                                                                    'selector_field_byte_order': selector_field_byte_order,
                                                                    'multiplexed_pdu_length': multiplexed_pdu_length,
                                                                    'multiplexed_pdu_name': multiplexed_pdu_name,
                                                                    'container_pdu_type': 'MULTIPLEXED-I-PDU',
                                                                    'dynamic_part': True,
                                                                    'is_initial_dynamic_part': is_initial_dynamic_part}
                        
                #get static part info
                static_parts = multiplexed_pdu.findall(f'.//{ns}STATIC-PART')
                for static_part in static_parts:
                    static_pdu_ref = self.get_ref_name(static_part.find(f'{ns}I-PDU-REF').text)
                    if static_pdu_ref:
                        multiplexed_pdus_list.append(static_pdu_ref)
                        multiplexed_pdus_info[static_pdu_ref] = {'selector_field_length': selector_field_length, 
                                                        'selector_field_start_position': selector_field_start_position, 
                                                        'selector_field_byte_order': selector_field_byte_order,
                                                        'multiplexed_pdu_length': multiplexed_pdu_length,
                                                        'multiplexed_pdu_name': multiplexed_pdu_name,
                                                        'container_pdu_type': 'MULTIPLEXED-I-PDU',
                                                        'dynamic_part': False}
            except Exception as e:
                logger.warning(f'Multiplexed pdu info not found for -> {multiplexed_pdu_name}')
                continue   
                    
        del multiplexed_pdus_packages

        self.e2e_definitions = self.get_e2e_info()

        results_dict = {}
        for ethernet_cluster in ethernet_cluster_packages:
            ethernet_cluster_name = self.get_short_name(ethernet_cluster)
            results_dict[ethernet_cluster_name] = {}
            #channels/vlans
            physical_channels_packages = self.root.findall(f'.//{ns}ETHERNET-PHYSICAL-CHANNEL')
            for physical_channel in physical_channels_packages:
                physical_channel_name = self.get_short_name(physical_channel)

                pdu_triggerings = physical_channel.findall(f'.//{ns}PDU-TRIGGERING')
                # pdu_to_pdu_triggering map
                pdu_pdutriggering_map_dict = {}
                for pdu_triggering in pdu_triggerings:
                    pdu_triggering_name = self.get_short_name(pdu_triggering)
                    pdu_type, pdu_ref = ClassicArxmlParser.get_dest_and_text(pdu_triggering.find(f'{ns}I-PDU-REF'))
                    pdu_pdutriggering_map_dict[pdu_ref] = pdu_triggering_name

                autosar_pdutrigg_list = get_autosar_pdutriggering_list(physical_channel_name, physical_channel)
                for mul_pdu in multiplexed_pdus_list:
                    if pdu_pdutriggering_map_dict.get(mul_pdu, None) is not None:
                        autosar_pdutrigg_list.append(pdu_pdutriggering_map_dict.get(mul_pdu, None))

                results_dict[ethernet_cluster_name][physical_channel_name] = {}


                #isignal_triggerings = physical_channel.findall(f'.//{ns}I-SIGNAL-TRIGGERING')
                #can_frames_full_data=[]
                for pdu_triggering in pdu_triggerings:
                    self.frame_entity = [{}]
                    pdu_triggering_name = self.get_short_name(pdu_triggering)
                    if (autosar_pdutrigg_list is not None) and (pdu_triggering_name not in autosar_pdutrigg_list):
                        continue

                    #check if container pdu is present
                    container_pdu_info_ = container_pdus_info.get(ethernet_cluster_name, {}).get(physical_channel_name, {}).get(pdu_triggering_name, {})
                    container_pdu = container_pdu_info_.get('name', '')
                    container_pdu_length = container_pdu_info_.get('length', '')
                    if container_pdu:
                        container_pdu_info = {'con_pdu_name': container_pdu, 'con_pdu_type': 'CONTAINER-I-PDU', 'length': container_pdu_length}
                    else:
                        container_pdu_info = {}


                    pdu_type, pdu_ref = ClassicArxmlParser.get_dest_and_text(pdu_triggering.find(f'{ns}I-PDU-REF'))

                    self.frame_entity[0]['PDU'] = pdu_ref
                    self.frame_entity[0]['PDU_Type'] = pdu_type
                    self.frame_entity[0]['PDU_Type'] = pdu_type


                    if pdu_type == 'I-SIGNAL-I-PDU':

                        multiplexed_pdu_info_data = multiplexed_pdus_info.get(pdu_ref, {})

                        normal_pdu_package = normal_pdu_info_dict.get(pdu_ref, None)
                        if normal_pdu_package is None:
                            continue
                        
                        self.get_i_signal_i_pdu_data('ETH_PDU',pdu_ref, pdu_type, normal_pdu_package, signals_info_dict, compu_methods_info_dict, system_signal_info_dict,
                                                     sig_groups_info_dict, units_mapping_info, container_pdu_info, multiplexed_pdu_info_data)
                        self.frame_entity.pop(0)
                        #can_frames_full_data.append(self.frame_entity)
                    
                        pdu_ports = pdu_triggering.findall(f'.//{ns}I-PDU-PORT-REF')
                        for pdu_port in pdu_ports:
                            try:
                                pdu_port_split = pdu_port.text.split("/")
                                node_name = pdu_port_split[-3]
                                channel_name = pdu_port_split[-2]
                                pdu_port_name = pdu_port_split[-1]

                                if node_name not in results_dict[ethernet_cluster_name][physical_channel_name]:
                                    results_dict[ethernet_cluster_name][physical_channel_name][node_name] = {'RX':[], 'TX':[]}
                                
                                
                                for direction, pt_triggering_list in self.ecu_instance_info.get(node_name, {}).get('ETHERNET', {}).get(channel_name, {}).items():
                                    if pdu_port_name in pt_triggering_list:
                                        results_dict[ethernet_cluster_name][physical_channel_name][node_name][direction.upper()].append(self.frame_entity)
                                        break
                            except:
                                continue
        
        return results_dict
                
                
    


    def get_i_signal_i_pdu_data(self, protocol, pdu_ref, pdu_type, pdu_package, signals_info_dict, compu_methods_info_dict, 
                                system_signal_info_dict, sig_groups_info_dict, units_mapping_dict,container_pdu_info={}, multiplexed_pdu_info_data={}):
        try:
            # found = False
            # for pdu_package in pdus_packages:
            if pdu_ref == pdu_package.find(f'.//{ns}SHORT-NAME').text:
                # found = True
                signals_ref = pdu_package.findall(f'.//{ns}I-SIGNAL-REF')
                start_position_ref = pdu_package.findall(f'.//{ns}START-POSITION')
                pdu_length = pdu_package.find(f'.//{ns}LENGTH').text
                byte_orders_ref = pdu_package.findall(f'.//{ns}PACKING-BYTE-ORDER')
                contained_pdu_props = pdu_package.find(f'.//{ns}CONTAINED-I-PDU-PROPS')
                header_id = None
                if contained_pdu_props is not None:
                    header_id_info = self.data_extractor(contained_pdu_props)
                    header_id = header_id_info.get('HEADER-ID-SHORT-HEADER', None)
                    if header_id is None:
                        header_id = header_id_info.get('HEADER-ID-LONG-HEADER', None)
                if header_id is not None:
                    self.frame_entity[0]['Header ID'] = hex(int(header_id)).upper()
                pdu_groups = pdu_package.findall(f'.//{ns}I-SIGNAL-GROUP-REF')
                if pdu_groups:
                    group = pdu_groups[0].text.split("/")[-1]
                    group_ref = sig_groups_info_dict.get(group, None)
                    # for group_ref in sig_groups_packages:
                    #     if group == group_ref.find(f'.//{ns}SHORT-NAME').text:
                    if group_ref is not None:
                        e2e_rf = group_ref.findall(f'.//{ns}TRANSFORMER-REF')
                        if e2e_rf:
                            e2e = e2e_rf[0].text.split("/")[-1]
                            self.frame_entity[0]['EndToEndProtection'] = e2e  # Add EndToEndProtection for sig group
                        else:
                            self.frame_entity[0]['EndToEndProtection'] = None
                else:
                    self.frame_entity[0]['EndToEndProtection'] = None  # Add None for EndToEndProtection
                if pdu_length:
                    self.frame_entity[0]['PDU_Length [Byte]'] = int(pdu_length)

                true_timing_info = pdu_package.find(f'.//{ns}TRANSMISSION-MODE-TRUE-TIMING')
                false_timing_info = pdu_package.find(f'.//{ns}TRANSMISSION-MODE-FALSE-TIMING')
                #cycle_time_ref = pdu_package.find(f'.//{ns}TIME-PERIOD/{ns}VALUE')
                cycle_time = None
                transmission_mode = None
                if true_timing_info is not None:
                    is_cyclic = False
                    is_event = False
                    true_timing_cyclic_period = true_timing_info.find(f'.//{ns}CYCLIC-TIMING/{ns}TIME-PERIOD/{ns}VALUE')
                    true_timing_event_repititions = true_timing_info.find(f'.//{ns}EVENT-CONTROLLED-TIMING/{ns}NUMBER-OF-REPETITIONS')
                    if true_timing_cyclic_period is not None:
                        cycle_time = true_timing_cyclic_period.text
                        is_cyclic = True
                    if true_timing_event_repititions is not None:
                        is_event = True
                    if is_cyclic and is_event:
                        transmission_mode = 'Event Periodic'
                    elif is_cyclic is True:
                        transmission_mode = 'Periodic'
                    elif is_event is True:
                        transmission_mode = 'Event'
                elif false_timing_info is not None:
                    is_cyclic = False
                    is_event = False
                    false_timing_cyclic_period = false_timing_info.find(f'.//{ns}CYCLIC-TIMING/{ns}TIME-PERIOD/{ns}VALUE')
                    false_timing_event_repititions = false_timing_info.find(f'.//{ns}EVENT-CONTROLLED-TIMING/{ns}NUMBER-OF-REPETITIONS')

                    if false_timing_cyclic_period is not None:
                        cycle_time = false_timing_cyclic_period.text
                        is_cyclic = True
                    if false_timing_event_repititions is not None:
                        is_event = True
                    if is_cyclic and is_event:
                        transmission_mode = 'Event Periodic'
                    elif is_cyclic is True:
                        transmission_mode = 'Periodic'
                    elif is_event is True:
                        transmission_mode = 'Event'

                if cycle_time is not None:
                    self.frame_entity[0]['Cycle Time [ms]'] = float(cycle_time) * 1000
                else:
                    self.frame_entity[0]['Cycle Time [ms]'] = None

                if transmission_mode is not None:
                    self.frame_entity[0]['Transmission Mode'] = transmission_mode
                else:
                    self.frame_entity[0]['Transmission Mode'] = None




                if not(signals_ref):
                    frame_data = self.frame_entity[0].copy()
                   
                    if pdu_type != 'I-SIGNAL-I-PDU':
                        frame_data['PDU'] = pdu_ref
                        frame_data['PDU_Type'] = "I-SIGNAL-I-PDU"
                        frame_data['Payload_PDU_Type'] = pdu_type
                    frame_data['Network Protocol'] = protocol
                    self.frame_entity.append(frame_data)
                    return


                for sig, start_pos, byte_order in zip(signals_ref, start_position_ref, byte_orders_ref):
                    signal_data = {}
                    if pdu_type == "N-PDU" or pdu_type == "SECURED-I-PDU" or pdu_type == "MULTIPLEXED-I-PDU" or pdu_type == "CONTAINER-I-PDU":
                        signal_data['PDU'] = pdu_ref
                        signal_data['PDU_Type'] = "I-SIGNAL-I-PDU"
                        signal_data["Transmission Mode"] = self.frame_entity[0]['Transmission Mode']
                    signal_name = sig.text.split("/")[-1]
                    if 'ETH' in protocol.upper():
                        signal_data['Network Protocol'] = protocol

                    signal_data["Signal"] = signal_name
                    start_position = int(start_pos.text)
                    signal_data['Startbit'] = start_position
                    signal_data['PDU_Length [Byte]'] = int(pdu_length)
                    if 'CAN' in protocol.upper():
                        signal_data['dlc'] = self.get_dlc(pdu_length)

                    if multiplexed_pdu_info_data:
                        signal_data['Payload_PDU_Type'] = multiplexed_pdu_info_data.get('container_pdu_type', '')
                        signal_data['Payload_PDU'] = multiplexed_pdu_info_data.get('multiplexed_pdu_name', '')
                        if 'CAN' in protocol.upper():
                            signal_data['Message'] = self.frame_entity[0]["Message"]
                            signal_data['Message ID'] = self.frame_entity[0]['Message ID']
                        if multiplexed_pdu_info_data.get('dynamic_part', False) and multiplexed_pdu_info_data.get('is_initial_dynamic_part', False):
                            if start_pos.text == multiplexed_pdu_info_data.get('selector_field_start_position', ''):
                                signal_data['Selector_Field_Signal'] = 'yes'

                    
                    if container_pdu_info: 
                        signal_data['Payload_PDU_Type'] = container_pdu_info.get('con_pdu_type', '')
                        signal_data['Payload_PDU'] = container_pdu_info.get('con_pdu_name', '')
                        signal_data['Payload_PDU_Length [Byte]'] = container_pdu_info.get('length', '')
                        if 'CAN' in protocol.upper():
                            signal_data['Payload PDU DLC'] = self.get_dlc(container_pdu_info.get('length', ''))
                            signal_data['Message'] = self.frame_entity[0]["Message"]
                            signal_data['Message ID'] = self.frame_entity[0]['Message ID']

                    ### signal group ####
                    if pdu_groups:
                        found = False
                        for pdu_group in pdu_groups:
                            group = pdu_group.text.split("/")[-1]
                            group_ref = sig_groups_info_dict.get(group, None)
                            # for group_ref in sig_groups_packages:
                            #     if group == group_ref.find(f'.//{ns}SHORT-NAME').text:
                            if group_ref is not None:
                                group_signals = group_ref.findall(f'.//{ns}I-SIGNAL-REF')
                                for group_entity in group_signals:
                                    if group_entity.text.split("/")[-1] == signal_name:
                                        signal_data['Signal_Group'] = group  # Add signal group
                                        if self.e2e_definitions.get(group, None):
                                            signal_data['EndToEndProtection'] = self.e2e_definitions.get(group)
                                        found = True
                                        break
                            # if found:
                            #     break
                    else:
                        signal_data['Signal_Group'] = None  # Add None Signal group
                    ### End Get signal group #######
                    
                    if byte_order is not None:
                        if byte_order.text == "MOST-SIGNIFICANT-BYTE-LAST":
                            signal_data['Byte Order'] = "Intel"
                        elif byte_order.text == "MOST-SIGNIFICANT-BYTE-FIRST":
                            signal_data['Byte Order'] = "Motorola"
                        else:
                            signal_data['Byte Order'] = byte_order.text
                    else:
                        signal_data['Byte Order'] = None

                    # for signal_package in signals_package:
                        # if signal_name == signal_package.find(f'.//{ns}SHORT-NAME').text:

                    signal_package = signals_info_dict.get(signal_name, None)
                    if signal_package is None:
                        continue

                    initial_value_ref = signal_package.find(f'.//{ns}VALUE')
                    if initial_value_ref is not None:
                        int_value_string = initial_value_ref.text
                        try:
                            if "0x" in int_value_string.lower():
                                initial_value = int(int_value_string, 16)
                            else:
                                initial_value = float(int_value_string.strip())
                        except:
                            initial_value = None
                    else:
                        initial_value = None
                    signal_data["Initial Value"] = initial_value
                    length = signal_package.find(f'.//{ns}LENGTH').text
                    signal_data['Signal_Length [Bit]'] = int(length)

                    compu_method_obj = signal_package.find(f'.//{ns}COMPU-METHOD-REF')
                    sys_signal_ref_obj = signal_package.find(f'.//{ns}SYSTEM-SIGNAL-REF')

                    base_type_ref = signal_package.find(f'.//{ns}BASE-TYPE-REF')
                    if base_type_ref is not None:
                        signal_data['Signal Base Type'] = self.get_ref_name(base_type_ref.text).lower()

                    if compu_method_obj is not None:
                        compu_method = compu_method_obj.text.split("/")[-1]
                    elif sys_signal_ref_obj is not None:
                        sys_signal = sys_signal_ref_obj.text.split("/")[-1]

                        sys_signal_info = self.data_extractor(system_signal_info_dict.get(sys_signal, None))
                        #sys_signal_info = self.get_system_signal_info(sys_signal, system_signal_info_dict.get(sys_signal, None) )
                        compu_method = sys_signal_info.get('COMPU-METHOD-REF', None)
                        signal_data['Comment'] = sys_signal_info.get('L-2', None)
                    else:
                        compu_method = None

                    if compu_method:
                        additional_sig_data = self.get_signal_properties(compu_method, compu_methods_info_dict.get(compu_method, None), units_mapping_dict)
                        signal_data.update(additional_sig_data)
                    else:
                        signal_data['texttable'] = None
                        signal_data['Factor'] = 1
                        signal_data['Offset'] = 0
                        signal_data['Minimum'] = None
                        signal_data['Maximum'] = None
                        signal_data['texttable values'] = None
                    if pdu_type == "N-PDU" or pdu_type == "SECURED-I-PDU" or pdu_type == "MULTIPLEXED-I-PDU" or pdu_type == "CONTAINER-I-PDU":
                        signal_data['Payload_PDU_Type'] = pdu_type
                        self.frame_entity.append(signal_data)
                    else:
                        frame_data = self.frame_entity[0].copy()
                        self.frame_entity.append(frame_data | signal_data)
                    #break
            # if found:
            #     break
        except Exception as e:
            traceback.print_exc()
            raise e

    # def get_system_signal_info(self, sys_signal, sys_signal_package):
    #     if sys_signal_package is None:
    #         return {}
    #     # for sig in sys_signal_package:
    #     #     name = sig.find(f'{ns}SHORT-NAME').text
    #     #     if sys_signal == name:
    #     return self.data_extractor(sig)
    #             # compu_method_ref = sig.findall(f'.//{ns}COMPU-METHOD-REF')
    #             # if not compu_method_ref:
    #             #     return None
    #             # else:
    #             #     compu_method_name = compu_method_ref[0].text.split("/")[-1]
    #             #     return compu_method_name

    def get_signal_properties(self, compu_method_name, compu_method, unit_mapping_dict):
        try:
            additonal_data = {}

            if compu_method is None:
                return additonal_data

            # for compu_method in compu_data_type:
            #     if compu_method_name == compu_method.find(f'{ns}SHORT-NAME').text:

            #get unit info
            unit_ref = compu_method.find(f'{ns}UNIT-REF')
            if unit_ref is not None:
                unit_name = self.get_ref_name(unit_ref.text)
                additonal_data['Unit'] = unit_mapping_dict.get(unit_name, '')

            category = compu_method.find(f'{ns}CATEGORY')
            if category is None:
                return additonal_data
            else:
                category = category.text

            if category.startswith("TEXTTABLE"):
                additonal_data['texttable'] = category.lower()  # Add category for the signal
                additonal_data['Factor'] = 1  # Add factor value for the signal
                additonal_data['Offset'] = 0  # Add offset value for the signal
                enum = compu_method.findall(enums_path)
                enum_entries = []
                for texttable_entry in enum:
                    enum_entries.append("LogicalValue: " + texttable_entry.find(
                        f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                        f'{ns}COMPU-CONST/{ns}VT').text)
                additonal_data['Minimum'] = 0  # Minimum value for texttable
                additonal_data['Maximum'] = len(enum_entries) - 1  # Maximum value for enum entry
                additonal_data['texttable values'] = "\n".join(enum_entries)  # Add texttable values for the signal
                # break
            elif "SCALE_LINEAR_AND_TEXTTABLE" in category:
                additonal_data['texttable'] = category.lower()
                try:
                    additonal_data['Factor'] = float(compu_method.find(factors_path_type_2).text)
                    additonal_data['Offset'] = float(compu_method.find(offsets_path_type_2).text)
                except:
                    additonal_data['Factor'] = None
                    additonal_data['Offset'] = None

                min_value_ref = compu_method.find(min_value_path)
                if min_value_ref is not None:
                    try:
                        additonal_data['Minimum'] = float(min_value_ref.text)
                    except:
                        additonal_data['Minimum'] = None
                else:
                    additonal_data['Minimum'] = None
                max_value_ref = compu_method.find(max_value_path)
                if max_value_ref is not None:
                    try:
                        additonal_data['Maximum'] = float(max_value_ref.text)
                    except:
                        additonal_data['Maximum'] = None
                else:
                    additonal_data['Maximum'] = None
                enum = compu_method.findall(enums_path)
                enum_entries = []
                for texttable_entry in enum[1:]:
                    try:
                        enum_entries.append("LogicalValue: " + texttable_entry.find(
                            f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                            f'{ns}COMPU-CONST/{ns}VT').text)
                    except:
                        continue
                additonal_data['texttable values'] = "\n".join(enum_entries)  # Add texttable values for the signal
                # break

            elif category == "LINEAR" or category == "SCALE_LINEAR":
                additonal_data['texttable'] = None  # Texttable is none
                try:
                    additonal_data['Factor'] = float(compu_method.find(factors_path_type_1).text)
                    additonal_data['Offset'] = float(compu_method.find(offsets_path_type_1).text)
                    additonal_data['texttable values'] = None
                except:
                    try:
                        additonal_data['Factor'] = float(compu_method.find(factors_path_type_2).text)
                        additonal_data['Offset'] = float(compu_method.find(offsets_path_type_2).text)
                        additonal_data['texttable values'] = None
                    except:
                        additonal_data['Factor'] = None
                        additonal_data['Offset'] = None
                        additonal_data['texttable values'] = None

                min_value_ref = compu_method.find(min_value_path)
                if min_value_ref is not None:
                    additonal_data['Minimum'] = float(min_value_ref.text)
                else:
                    additonal_data['Minimum'] = None
                max_value_ref = compu_method.find(max_value_path)
                if max_value_ref is not None:
                    additonal_data['Maximum'] = float(max_value_ref.text)
                else:
                    additonal_data['Maximum'] = None
                additonal_data['texttable values'] = None  # No texttable data for LINEAR signals
            else:
                additonal_data['texttable'] = None
                additonal_data['Factor'] = 1
                additonal_data['Offset'] = 0
                additonal_data['Minimum'] = None
                additonal_data['Maximum'] = None
                additonal_data['texttable values'] = None

            # break

            return additonal_data
        except:
            traceback.print_exc()
            raise Exception

    def get_can_frame_data(self, can_frame_data):
        try:

            if can_frame_data is None:
                return None, None
            # for can_frame_data in can_frame_packages:
            #     if can_frame_name == can_frame_data.find(f'.//{ns}SHORT-NAME').text:
            pdu_type = can_frame_data.find(f'.//{ns}PDU-REF').get("DEST")
            pdu_ref = can_frame_data.find(f'.//{ns}PDU-REF').text.split("/")[-1]
            self.frame_entity[0]["Message"] = can_frame_data.find(f'.//{ns}SHORT-NAME').text
            self.frame_entity[0]["PDU_Type"] = pdu_type
            return pdu_type, pdu_ref
        except:
            traceback.print_exc()

    def get_pdu_triggering_data(self, pdu_trigger_ref, pdu_triggering_data):
        try:

            if pdu_triggering_data is None:
                return None, None
            # for can_frame_data in can_frame_packages:
            #     if can_frame_name == can_frame_data.find(f'.//{ns}SHORT-NAME').text:
            pdu_type = pdu_triggering_data.find(f'.//{ns}I-PDU-REF').get("DEST")
            pdu_ref = pdu_triggering_data.find(f'.//{ns}I-PDU-REF').text.split("/")[-1]
            self.frame_entity[0]["PDU"] = pdu_ref
            self.frame_entity[0]["PDU_Type"] = pdu_type
            return pdu_type, pdu_ref
        except:
            traceback.print_exc()

    def get_can_tp_data(self, pdu, can_tp_pkg):
        can_tp_additional_data = {}
        for can_tp in can_tp_pkg:
            name_ref = can_tp.find(f'.//{ns}DATA-PDU-REF').text.split("/")[-1]
            flow_ctrl_ref = can_tp.find(f'.//{ns}FLOW-CONTROL-PDU-REF')
            if flow_ctrl_ref is not None:
                flow_ctrl = flow_ctrl_ref.text.split("/")[-1]
            else:
                flow_ctrl = None

            can_tp_pointer = can_tp.find(f'.//{ns}TP-SDU-REF')
            if can_tp_pointer is None:
                continue
            if pdu == name_ref or pdu == flow_ctrl:
                if can_tp_pointer.attrib["DEST"] != "I-SIGNAL-I-PDU":
                    continue
                    #return None, None
                else:
                    can_tp_max_block_size_pntr = can_tp.find(f'{ns}MAX-BLOCK-SIZE')
                    can_tp_addr_format = can_tp.find(f'{ns}ADDRESSING-FORMAT')
                    can_tp_padding = can_tp.find(f'{ns}PADDING-ACTIVATION')

                    if can_tp_max_block_size_pntr is not None:
                        can_tp_additional_data["Block_size"] = int(can_tp_max_block_size_pntr.text)
                    else:
                        can_tp_additional_data["Block_size"] = None
                    if can_tp_padding is not None:
                        can_tp_additional_data['Padding_active'] = can_tp_padding.text
                    else:
                        can_tp_additional_data['Padding_active'] = None
                    if can_tp_addr_format is not None:
                        can_tp_additional_data['Address_formate'] = can_tp_addr_format.text
                    else:
                        can_tp_additional_data['Address_formate'] = None
                    can_tp_additional_data['MAXFC_wait'] = None #
                    can_tp_additional_data['STMin'] = None # STMin
                    if pdu == name_ref:
                        control_type = "DATA_CONTROL"
                    elif pdu == flow_ctrl:
                        control_type = "FLOW_CONTROL"
                    if set(can_tp_additional_data) != {None}:
                        return can_tp_pointer.text.split("/")[-1], can_tp_additional_data, control_type
                    else:
                        return can_tp_pointer.text.split("/")[-1], None, None
        return None,None,None
                    


def create_eth_dataframe(data):
    try:
        df_template = pd.DataFrame(columns=eth_column_names)

        for data_set in data:
            df_data = pd.DataFrame(data_set, columns=eth_column_names)
            df_template = pd.concat([df_template, df_data], sort=True, ignore_index=True).fillna(np.nan)

#         columns_to_add = {"group": 1, 'Value Type': 9, 'Unit': 15, 'Value Table': 16,
#                             'Comment': 17,
#                             "max_value": 23, "dlc": 24, "variant": 25}
#         for key, value in columns_to_add.items():
#             df_template.insert(value, key, np.nan)
        max_float = sys.float_info.max
        for i, row in df_template.iterrows():
            try:
                df_template.loc[i, "variant"]= 'Common'
                #df_template["variant"][i] = 'Common'
                signal_length = row["Signal_Length [Bit]"]
                if signal_length:
                    max_value = (2 ** int(signal_length)) - 1
                    if max_value < max_float:
                        df_template.loc[i, "max_value"] = max_value
                        #df_template["max_value"][i] = max_value
            except:
                pass

#         df_template = df_template.reindex(columns=['Name', 'PDU', "PDU_Type", "group", "Payload_PDU", 'Message', 'Message ID', "Multiplexing/Group", 'Startbit',
#                                         'Length [Bit]', 'Byte Order', "Initial Value", 'Factor', 'Offset', 'Minimum',
#                                         'Maximum','max_value', 'Cycle Time [ms]', 'texttable', 'texttable values',
#                                         'Value Type', 'Unit', 'Comment', "dlc", 'variant', 'Value Table', 'EndToEndProtection', 'Block_size', 'Address_formate', 'Padding_active', 'STMin',
#                                     'MAXFC_wait'])

        df_template = df_template.reindex(columns=eth_column_names)
        return df_template
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Failed to create dataframe --> {e}")
        raise e
    
def create_can_dataframe(data):
    try:
        data_set = []
        for row_list in data:
            for row in row_list:
                data_set.append(row)
        df_template = pd.DataFrame(data_set, columns=can_column_names)

        # df_template = pd.DataFrame(columns=can_column_names)
        #
        # for data_set in data:
        #     df_data = pd.DataFrame(data_set, columns=can_column_names)
        #     df_template = pd.concat([df_template, df_data], sort=True, ignore_index=True).fillna(np.nan)

#         columns_to_add = {"group": 1, 'Value Type': 9, 'Unit': 15, 'Value Table': 16,
#                             'Comment': 17,
#                             "max_value": 23, "dlc": 24, "variant": 25}
#         for key, value in columns_to_add.items():
#             df_template.insert(value, key, np.nan)
        df_template['variant'] = df_template['variant'].fillna('')
        max_float = sys.float_info.max
        for i, row in df_template.iterrows():
            try:
                df_template.loc[i, "variant"]= 'Common'
                #df_template["variant"][i] = 'Common'
                signal_length = row["Signal_Length [Bit]"]
                if not(is_empty_or_spaces(signal_length)):
                    byte_order = row["Byte Order"]
                    if byte_order.upper() != 'OPAQUE' and signal_length < 100:
                        max_value = (2 ** int(signal_length)) - 1
                        if max_value < max_float:
                            df_template.loc[i, "max_value"] = max_value
                            #df_template["max_value"][i] = max_value
            except:
                pass

            try:
                if not (pd.isna(df_template.loc[i, "Length [Bit]"]) or (df_template.loc[i, "Length [Bit]"] == '')):
                    if df_template.loc[i, "Byte Order"].upper() != 'OPAQUE' and df_template.loc[
                        i, "Length [Bit]"] < 100:
                        df_template.loc[i, "max_value"] = (2 ** (int(df_template.loc[i, "Length [Bit]"]))) - 1
            except:
                pass

#         df_template = df_template.reindex(columns=['Name', 'PDU', "PDU_Type", "group", "Payload_PDU", 'Message', 'Message ID', "Multiplexing/Group", 'Startbit',
#                                         'Length [Bit]', 'Byte Order', "Initial Value", 'Factor', 'Offset', 'Minimum',
#                                         'Maximum','max_value', 'Cycle Time [ms]', 'texttable', 'texttable values',
#                                         'Value Type', 'Unit', 'Comment', "dlc", 'variant', 'Value Table', 'EndToEndProtection', 'Block_size', 'Address_formate', 'Padding_active', 'STMin',
#                                     'MAXFC_wait'])

        payload_pdu_types = ['N-PDU','SECURED-I-PDU','MULTIPLEXED-I-PDU','CONTAINER-I-PDU', 'NM-PDU', 'GENERAL-PURPOSE-I-PDU', 'GENERAL-PURPOSE-PDU']
        payload_pdu_df = df_template[df_template['PDU_Type'].isin(payload_pdu_types)]
        #i_signal_i_pdu_df = df_template[~(df_template['PDU_Type'].isin(payload_pdu_types) & (df_template['Payload_PDU'].isin(df_template['PDU'])))]
        i_signal_i_pdu_df = df_template.fillna('')

        copy_columns = [ "Message", "Message ID", "Cycle Time [ms]", "EndToEndProtection", "Block_size", "Address_formate", "Padding_active", "STMin", "MAXFC_wait"]
        payload_pdu_dict = {}
        
        for i,row in payload_pdu_df.iterrows():
            if row['Payload_PDU']!='' and row['Payload_PDU'] not in payload_pdu_dict:
                payload_pdu_dict[row['Payload_PDU']] = row

        #print(payload_pdu_dict)

        for i, row in i_signal_i_pdu_df.iterrows():
            msg_id = row['Message ID']
            if row['PDU'] in payload_pdu_dict:
                if not(is_empty_or_spaces(msg_id)) and msg_id!=payload_pdu_dict[row['PDU']]["Message ID"]: #normal SOK i-signal-i-pdu
                    continue
                i_signal_i_pdu_df.loc[i, "Payload_PDU"] = payload_pdu_dict[row['PDU']]['PDU']
                #i_signal_i_pdu_df["Payload_PDU"][i] = payload_pdu_dict[row['PDU']]['PDU']
                for col in copy_columns:
                    if is_empty_or_spaces(i_signal_i_pdu_df.loc[i, col]):
                        i_signal_i_pdu_df.loc[i, col] = payload_pdu_dict[row['PDU']][col]
                    #i_signal_i_pdu_df[col][i] = payload_pdu_dict[row['PDU']][col]


        df_template = i_signal_i_pdu_df.reindex(columns=can_column_names)
        #df_template = df_template.reindex(columns=can_column_names)
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

def getMappingSheetData(wb, mapping_sheet_name):
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
    logger.info('Got mapping sheet data')
    return mapping_df, arxml_index_map


def external_call(protocol='ALL'):
    """ main function"""
    try:
        logger.info("########## START 'Create Node Sheets ARXML ETH' DEBUG INFORMATION ##############")
        script_path = os.path.dirname(os.path.abspath(__file__))
        arxml_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Database\DBC'
        excel_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'
        wb, sheet_list, autosar_directory = load_excel_sheet()
        
        ## ETH is handled by create_arxml_eth
        # if "ETH" in protocol.upper() or protocol=='ALL':
        #     logger.info(f'----------------------------------ETH Extraction--------------------------------')
        #     if "ETHArxmlMapping" in sheet_list:

        #         # get mapping sheet data
        #         eth_mapping_df, arxml_index_map = getMappingSheetData(wb, "ETHArxmlMapping")
        #         if eth_mapping_df is None:
        #             logger.warning(f"ETHArxmlMapping sheet is empty in Autosar_Gen_Database")
        #         else:
        #             #delete old sheets
        #             for sheet in sheet_list:
        #                 if sheet.upper().startswith('ETH') and ('MAPPING' not in sheet.upper()):
        #                     del wb[sheet]
        #             wb.save(excel_path)
        #             logger.info("Deleted old ETH node sheets")

        #             PARSED_ARXML_DATA = {}
        #             write_data_dict = {}
        #             for cluster_name, cluster_df in eth_mapping_df.groupby("db_cluster_name"):
        #                 for channel_name, channel_df in cluster_df.groupby("db_channel_name"):
        #                     for node_names, node_mapping_df in channel_df.groupby("db_ecu_node"):
        #                         node_names = node_names.strip().split(';')
        #                         node_names = [q.strip() for q in node_names]
        #                         for direction, direction_df in node_mapping_df.groupby("direction"):
        #                             for i,row in direction_df.iterrows():
        #                                 direction = direction.upper()
        #                                 #df_first_row = direction_df.iloc[0]
        #                                 node_sheet_name = row["network_name"] + "_" + row["canoe_ecu_node"] + "_" + "arxml"
                                        
        #                                 arxml_indexes = str(row["mapping_canoe_ecu_to_db"]).split(';')
        #                                 arxml_indexes = [int(q) for q in arxml_indexes]

        #                                 for node_name in node_names:
        #                                     for arxml_index in arxml_indexes:
        #                                         if arxml_index not in PARSED_ARXML_DATA.keys():
        #                                             logger.info(f'----------Parsing -> {arxml_index_map[arxml_index]}----------')
        #                                             arxml_file_path = arxml_path + "\\" + arxml_index_map[arxml_index]
        #                                             arxml_instance = ClassicArxmlParser(arxml_file_path, protocol='ETH')
        #                                             PARSED_ARXML_DATA[arxml_index] = arxml_instance.ethernet_cluster_info
        #                                             if PARSED_ARXML_DATA[arxml_index]:
        #                                                 for clst_name in PARSED_ARXML_DATA[arxml_index].keys():
        #                                                     logger.info(f'Cluster: {clst_name}')
        #                                                     for chanl_name in PARSED_ARXML_DATA[arxml_index].get(clst_name, {}).keys():
        #                                                         logger.info(f'\t-Channel: {chanl_name}')
        #                                                         for nde_name in PARSED_ARXML_DATA[arxml_index].get(clst_name, {}).get(chanl_name, {}).keys():
        #                                                             logger.info(f'\t\t-Node: {nde_name}')
        #                                             logger.info('-------------------------------------------------------------------------------')
        #                                         data_to_write = PARSED_ARXML_DATA[arxml_index].get(cluster_name, {}).get(channel_name, {}).get(node_name, {}).get(direction, [])
        #                                         if data_to_write:
        #                                             #write_data_dict[node_sheet_name] = create_eth_dataframe(data_to_write)
        #                                             logger.info(f'Extracted data for {row["network_name"]} -> {row["canoe_ecu_node"]}')
        #                                             df_new = create_eth_dataframe(data_to_write)
        #                                             if (node_sheet_name in write_data_dict) and (isinstance(write_data_dict[node_sheet_name], pd.DataFrame)):
        #                                                 write_data_dict[node_sheet_name] = pd.concat([write_data_dict[node_sheet_name], df_new], ignore_index=True)
        #                                                 write_data_dict[node_sheet_name] = write_data_dict[node_sheet_name].drop_duplicates(ignore_index=True)
        #                                             else:
        #                                                 write_data_dict[node_sheet_name] = df_new

        #                                             logger.info(f'Extracted data for arxml node {node_name}:: {row["network_name"]} -> {row["canoe_ecu_node"]} ')
                                                    
        #                                             logger.info('-------------------------------------------------------------------------------')
        #                                         else:
        #                                             logger.warning(f"No data found for {node_sheet_name}")
        #             if write_data_dict != {}:
        #                 write_to_excel(write_data_dict)
        #             else:
        #                 logger.warning("Mapping Information is empty in ETHArxmlMapping sheet")
        #     else:
        #         logger.warning(f"ETHArxmlMapping sheet not found in Autosar_Gen_Database")


        #CAN        
        if "CAN" in protocol.upper() or protocol=='ALL':
            logger.info(f'----------------------------------CAN Extraction--------------------------------')
            if "ArxmlMapping" not in sheet_list:
                logger.warning(f"ArxmlMapping sheet not found in Autosar_Gen_Database")
            else:
                # get mapping sheet data
                can_mapping_df, arxml_index_map = getMappingSheetData(wb, "ArxmlMapping")
                if can_mapping_df is None:
                    logger.warning(f"ArxmlMapping sheet is empty in Autosar_Gen_Database")
                else:
                    #delete old sheets
                    for sheet in sheet_list:
                        if sheet.lower().endswith('_arxml') and (sheet.upper().startswith('CAN')) and ('MAPPING' not in sheet.upper()):
                            del wb[sheet]
                    wb.save(excel_path)
                    logger.info("Deleted old ARXML CAN node sheets")
                    wb.close()

                    PARSED_ARXML_DATA = {}
                    write_data_dict = {}
                    for cluster_name, cluster_df in can_mapping_df.groupby("db_cluster_name"):
                        for channel_name, channel_df in cluster_df.groupby("db_channel_name"):
                            for node_names, node_mapping_df in channel_df.groupby("db_ecu_node"):
                                node_names = node_names.strip().split(';')
                                node_names = [q.strip() for q in node_names]
                                for direction, direction_df in node_mapping_df.groupby("direction"):
                                    for i,row in direction_df.iterrows():
                                        direction = direction.upper()
                                        #df_first_row = direction_df.iloc[0]
                                        node_sheet_name = row["network_name"] + "_" + row["canoe_ecu_node"] + "_" + "arxml"

                                        arxml_indexes = str(row["mapping_canoe_ecu_to_db"]).split(';')
                                        arxml_indexes = [int(q) for q in arxml_indexes]


                                        for node_name in node_names:
                                            for arxml_index in arxml_indexes:
                                                if arxml_index not in PARSED_ARXML_DATA.keys():
                                                    logger.info(f'----------Parsing -> {arxml_index_map[arxml_index]}----------')
                                                    arxml_file_path = arxml_path + "\\" + arxml_index_map[arxml_index]
                                                    arxml_instance = ClassicArxmlParser(arxml_file_path, protocol='CAN')
                                                    PARSED_ARXML_DATA[arxml_index] = arxml_instance.can_cluster_info
                                                    
                                                    if PARSED_ARXML_DATA[arxml_index]:
                                                        for clst_name in PARSED_ARXML_DATA[arxml_index].keys():
                                                            logger.info(f'Cluster: {clst_name}')
                                                            for chanl_name in PARSED_ARXML_DATA[arxml_index].get(clst_name, {}).keys():
                                                                logger.info(f'\t-Channel: {chanl_name}')
                                                                for nde_name in PARSED_ARXML_DATA[arxml_index].get(clst_name, {}).get(chanl_name, {}).keys():
                                                                    logger.info(f'\t\t-Node: {nde_name}')
                                                    logger.info('-------------------------------------------------------------------------------')
                                                data_to_write = PARSED_ARXML_DATA[arxml_index].get(cluster_name, {}).get(channel_name, {}).get(node_name, {}).get(direction, [])
                                                if data_to_write:

                                                    df_new = create_can_dataframe(data_to_write)
                                                    if (node_sheet_name in write_data_dict) and (isinstance(write_data_dict[node_sheet_name], pd.DataFrame)):
                                                        write_data_dict[node_sheet_name] = pd.concat([write_data_dict[node_sheet_name], df_new], ignore_index=True)
                                                        write_data_dict[node_sheet_name] = write_data_dict[node_sheet_name].drop_duplicates(ignore_index=True)
                                                    else:
                                                        write_data_dict[node_sheet_name] = df_new

                                                    logger.info(f'Extracted data for arxml node {node_name}:: {row["network_name"]} -> {row["canoe_ecu_node"]} ')
                                                    logger.info('-------------------------------------------------------------------------------')
                                                else:
                                                    logger.warning(f"No data found for {node_sheet_name}")
                    if write_data_dict != {}:
                        write_to_excel(write_data_dict)
                    else:
                        logger.warning("Mapping Information is empty in ArxmlMapping sheet")
                            

        logger.info("###### END 'Create Autosar ARXML ' DEBUG INFORMATION ######")
        
        logger.info('-' * 80)
        return True
    except Exception as exp:
        logger.error(f"Failed to create arxml: {exp}")
        traceback.print_exc()
        raise Exception(exp)
        return False


if __name__ == "__main__":
    external_call()
