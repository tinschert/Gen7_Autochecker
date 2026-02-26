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
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching_arxml import *


class ArxmlParser:
    can_frame_entity = []
    can_frames_full_data = []

    def __int__(self):
        pass

    def get_arxml_list(self, path, excel_path):
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
            child_attributes = ArxmlParser.data_extractor(child_element)
            dictt.update(child_attributes)
        return dictt

    def create_arxml_main(self, arxmls_path):
        sheets_to_write = {}
        script_path = os.path.dirname(os.path.abspath(__file__))
        excel_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx'
        arxml_map = generate_dbc_map(excel_path, "ArxmlMapping")
        variant_dict = extractVariant(excel_path, "ArxmlMapping")
        wb, sheet_list, autosar_directory = load_excel_sheet()
        list_node, dict_node, dict_ecu_name, tx_messages, block_messages, direction = get_node_name(wb, "ArxmlMapping", True)
        arxmls = self.get_arxml_list(arxmls_path, excel_path)

        ''' Parse all data from all arxmls mapped in Autosar database'''
        start_time = time.time()
        big_data = []
        for arxml_index, value in arxmls.items():
            channels = dict_ecu_name.values()
            channels_reduced = list(set([item for sublist in channels for item in sublist]))
            data = self.parse_autosar(arxmls[arxml_index], channels_reduced)
            big_data.append(data)

        for _map in arxml_map:
            arxml_index = _map[1]
            sheet_index = _map[0]
            specific_node_data = self.create_nodes(big_data[arxml_index], dict_ecu_name[list_node[sheet_index]],
                                              direction[sheet_index])
            df_to_write = self.create_dataframe(specific_node_data, variant_dict)
            sheets_to_write[list_node[sheet_index]] = df_to_write
        logger.info(f"Arxml(s) parsing took {time.time() - start_time} seconds")
        start_time = time.time()
        self.write_to_excel(sheets_to_write)
        logger.info(f"Arxml(s) data were recorded in Autosar_Gen_Database.xlsx for {time.time() - start_time} seconds")
    
    def parse_autosar(self, arxml_path, channels):
        try:
            logger.info(f"Start extracting data from {arxml_path}")
            can_frames_full_data = []

            try:
                tree = ET.parse(arxml_path)
                root = tree.getroot()
                ns = "{http://autosar.org/schema/r4.0}"
            except Exception as e:
                logger.error(f"Failed parsing {arxml_path}. Reason --> {e}")
                raise e

            cluster_packages = root.findall(f'.//{ns}CAN-CLUSTER')
            frame_port_packages = root.findall(f'.//{ns}FRAME-PORT')
            can_frame_packages = root.findall(f'.//{ns}CAN-FRAME')
            normal_pdus_packages = root.findall(f'.//{ns}I-SIGNAL-I-PDU')
            nm_pdus_package = root.findall(f'.//{ns}NM-PDU')
            signal_packages = root.findall(f'.//{ns}I-SIGNAL')
            compu_method_packages = root.findall(f'.//{ns}COMPU-METHOD')
            system_signal_packages = root.findall(f'.//{ns}SYSTEM-SIGNAL')
            can_tp_connection_packages = root.findall(f'.//{ns}CAN-TP-CONNECTION')
            sig_group_packages = root.findall(f'.//{ns}I-SIGNAL-GROUP')
            secured_pdus_packages = root.findall(f'.//{ns}SECURED-I-PDU')
            pdu_triggerings = root.findall(f'.//{ns}PDU-TRIGGERING')

            network_node = ''
            for cluster in cluster_packages:
                cluster_name = cluster.find(f'.//{ns}SHORT-NAME').text
                if cluster_name in channels:
                    network_node = cluster_name
                    can_frame_triggering_packages = cluster.findall(f'.//{ns}CAN-FRAME-TRIGGERING')
                    break
            if network_node == '':
                logger.error(f"None of the Excel CAN nodes can be found in the arxml {arxml_path}")
                raise Exception("Wrong/not found entry populated in dbc_network_node.")
            
            ArxmlParser.e2e_data_dict = {}
            e2e_packages = root.findall(f'.//{ns}END-TO-END-PROTECTION')
            for e2e_package in e2e_packages:
                try:
                    e2e_name = e2e_package.find(f'.//{ns}SHORT-NAME').text
                    e2e_info_dict = self.data_extractor(e2e_package)
                    sig_group = e2e_info_dict.get('I-SIGNAL-GROUP-REF', None)
                    e2e_info = str(e2e_info_dict.get('CATEGORY', '')) + '::' + str(e2e_info_dict.get('DATA-ID', ''))
                    ArxmlParser.e2e_data_dict[sig_group] = e2e_info
                except:
                    continue

            for can_frame in can_frame_triggering_packages:
                ArxmlParser.can_frame_entity = [{}]  # Create a single entity which encapsulates all data inside one CAN frame
                ArxmlParser.can_frame_entity[0]["NETWORK"] = network_node
                """ Get References """
                frame_port_ref = can_frame.find(f'.//{ns}FRAME-PORT-REF').text.split("/")[-1]
                frame_ref = can_frame.find(f'.//{ns}FRAME-REF').text.split("/")[-1]
                pdu_triggering_ref = can_frame.find(f'.//{ns}PDU-TRIGGERING-REF').text.split("/")[-1]

                ''' TYPE and DIRECTION(IN/OUT) to the list '''
                ArxmlParser.can_frame_entity[0]["DIRECTION"] = self.get_direction(frame_port_packages, frame_port_ref)
                pdu_type, pdu_ref = self.get_can_frame_data(can_frame_packages, frame_ref)

                """ Add corresponding PDU name """
                ArxmlParser.can_frame_entity[0]['PDU'] = pdu_ref

                ''' Extract Message ID '''
                message_id = can_frame.find(f'{ns}IDENTIFIER').text
                hex_value = hex(int(message_id))
                ArxmlParser.can_frame_entity[0]['Message ID'] = hex_value.upper()

                ''' Call function to collect all signals data inside current PDU'''
                if pdu_type == "I-SIGNAL-I-PDU":
                    ''' Add not necessary fields for non NPDUs '''

                    self.get_i_signal_i_pdu_data(pdu_ref, pdu_type, normal_pdus_packages, signal_packages, compu_method_packages, system_signal_packages, sig_group_packages)
                    ArxmlParser.can_frame_entity.pop(0)
                    ''' Append collected single frame data to the main data list '''
                    can_frames_full_data.append(ArxmlParser.can_frame_entity)  # Add current set to the big data set

                elif pdu_type == "SECURED-I-PDU":
                    for secured_pdu in secured_pdus_packages:
                        if pdu_ref == secured_pdu.find(f'.//{ns}SHORT-NAME').text:
                            payload_ref = secured_pdu.find(f'.//{ns}PAYLOAD-REF').text.split("/")[-1]
                            break
                    for pdu_triggering in pdu_triggerings:
                        if payload_ref == pdu_triggering.find(f'.//{ns}SHORT-NAME').text:
                            payload_pdu = pdu_triggering.find(f'.//{ns}I-PDU-REF').text.split("/")[-1]
                            ArxmlParser.can_frame_entity[0]['Payload PDU'] = payload_pdu
                            break

                    self.get_i_signal_i_pdu_data(payload_pdu, pdu_type, normal_pdus_packages, signal_packages, compu_method_packages, system_signal_packages, sig_group_packages)
                    can_frames_full_data.append(ArxmlParser.can_frame_entity)  # Add current set to the big data set

                elif pdu_type == "NM-PDU":
                    self.get_i_signal_i_pdu_data(pdu_ref, pdu_type, nm_pdus_package, signal_packages, compu_method_packages,
                                                 system_signal_packages, sig_group_packages)

                    ''' Append collected single frame data to the main data list '''
                    ArxmlParser.can_frame_entity.pop(0)
                    can_frames_full_data.append(ArxmlParser.can_frame_entity)  # Add current set to the big data set
                elif pdu_type == "N-PDU":
                    try:
                        pdu_ref_tp, npdu_special_info, control_type = self.get_can_tp_data(pdu_ref, can_tp_connection_packages)
                    except:
                        pdu_ref_tp = None
                    if pdu_ref_tp is None:
                        del ArxmlParser.can_frame_entity
                    else:

                        ArxmlParser.can_frame_entity[0].update(npdu_special_info)
                        ArxmlParser.can_frame_entity[0]["Payload PDU"] = pdu_ref_tp  # Add pointer to I-SIG-I-PDU
                        if control_type == "DATA_CONTROL":
                            self.get_i_signal_i_pdu_data(pdu_ref_tp, pdu_type, normal_pdus_packages, signal_packages, compu_method_packages, system_signal_packages, sig_group_packages)
                        can_frames_full_data.append(ArxmlParser.can_frame_entity)  # Add current set to the big data set

            return can_frames_full_data
        except Exception as e:
            traceback.print_exc()
            raise e


    def get_direction(self, frame_port_package, frame_port_ref):
        """ Function to retrieve current frame direction Tx/Rx in format IN/OUT"""
        for frame in frame_port_package:
            if frame_port_ref == frame.find(f'.//{ns}SHORT-NAME').text:
                return frame.find(f'.//{ns}COMMUNICATION-DIRECTION').text

    def get_can_frame_data(self, can_frame_packages, can_frame_name):
        try:
            for can_frame_data in can_frame_packages:
                if can_frame_name == can_frame_data.find(f'.//{ns}SHORT-NAME').text:
                    pdu_type = can_frame_data.find(f'.//{ns}PDU-REF').get("DEST")
                    pdu_ref = can_frame_data.find(f'.//{ns}PDU-REF').text.split("/")[-1]
                    ArxmlParser.can_frame_entity[0]["Message"] = can_frame_name
                    ArxmlParser.can_frame_entity[0]["PDU Type"] = pdu_type
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
            if pdu == name_ref or pdu == flow_ctrl:
                if can_tp_pointer.attrib["DEST"] != "I-SIGNAL-I-PDU":
                    return None, None
                else:
                    can_tp_max_block_size_pntr = can_tp.find(f'{ns}MAX-BLOCK-SIZE')
                    can_tp_addr_format = can_tp.find(f'{ns}ADDRESSING-FORMAT')
                    can_tp_padding = can_tp.find(f'{ns}PADDING-ACTIVATION')

                    if can_tp_max_block_size_pntr is not None:
                        can_tp_additional_data["Block_size"] = can_tp_max_block_size_pntr.text
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

    def get_i_signal_i_pdu_data(self, pdu_ref, pdu_type, pdus_packages, signals_package, compu_package, sys_signal_package, sig_groups_packages):
        try:
            found = False
            for pdu_package in pdus_packages:
                if pdu_ref == pdu_package.find(f'.//{ns}SHORT-NAME').text:
                    found = True
                    signals_ref = pdu_package.findall(f'.//{ns}I-SIGNAL-REF')
                    start_position_ref = pdu_package.findall(f'.//{ns}START-POSITION')
                    byte_orders_ref = pdu_package.findall(f'.//{ns}PACKING-BYTE-ORDER')
                    pdu_groups = pdu_package.findall(f'.//{ns}I-SIGNAL-GROUP-REF')
                    if pdu_groups:
                        group = pdu_groups[0].text.split("/")[-1]
                        for group_ref in sig_groups_packages:
                            if group == group_ref.find(f'.//{ns}SHORT-NAME').text:
                                e2e_rf = group_ref.findall(f'.//{ns}TRANSFORMER-REF')
                                if e2e_rf:
                                    e2e = e2e_rf[0].text.split("/")[-1]
                                    ArxmlParser.can_frame_entity[0]['EndToEndProtection'] = e2e  # Add EndToEndProtection for sig group
                                else:
                                    ArxmlParser.can_frame_entity[0]['EndToEndProtection'] = None
                    else:
                        ArxmlParser.can_frame_entity[0]['EndToEndProtection'] = None  # Add None for EndToEndProtection
                    cycle_time_ref = pdu_package.find(f'.//{ns}TIME-PERIOD/{ns}VALUE')
                    if cycle_time_ref is not None:
                        cycle_time = cycle_time_ref.text
                        ArxmlParser.can_frame_entity[0]['Cycle Time [ms]'] = float(cycle_time) * 1000
                    else:
                        ArxmlParser.can_frame_entity[0]['Cycle Time [ms]'] = None
                    for sig, start_pos, byte_order in zip(signals_ref, start_position_ref, byte_orders_ref):
                        signal_data = {}
                        if pdu_type == "N-PDU" or pdu_type == "SECURED-I-PDU":
                            signal_data['PDU'] = pdu_ref
                            signal_data['PDU Type'] = "I-SIGNAL-I-PDU"
                            signal_data['EndToEndProtection'] = ArxmlParser.can_frame_entity[0]['EndToEndProtection']
                            signal_data['Cycle Time [ms]'] = ArxmlParser.can_frame_entity[0]['Cycle Time [ms]']
                            signal_data['Message'] = ArxmlParser.can_frame_entity[0]['Message']
                            signal_data['Message ID'] = ArxmlParser.can_frame_entity[0]['Message ID']
                        signal_name = sig.text.split("/")[-1]
                        signal_data["Name"] = signal_name
                        start_position = int(start_pos.text)
                        signal_data['Startbit'] = start_position

                        ### Get multiplexing group ####
                        if pdu_groups:
                            found = False
                            for pdu_group in pdu_groups:
                                group = pdu_group.text.split("/")[-1]
                                for group_ref in sig_groups_packages:
                                    if group == group_ref.find(f'.//{ns}SHORT-NAME').text:
                                        group_signals = group_ref.findall(f'.//{ns}I-SIGNAL-REF')
                                        for group_entity in group_signals:
                                            if group_entity.text.split("/")[-1] == signal_name:
                                                signal_data['Multiplexing/Group'] = group  # Add signal group
                                                if ArxmlParser.e2e_data_dict.get(group, None):
                                                    signal_data['EndToEndProtection'] = ArxmlParser.e2e_data_dict.get(group)
                                                found = True
                                                break
                                    if found:
                                        break
                        else:
                            signal_data['Multiplexing/Group'] = None  # Add None Signal group
                        ### End Get mulitplexing group #######
                        
                        if byte_order is not None:
                            if byte_order.text == "MOST-SIGNIFICANT-BYTE-LAST":
                                signal_data['Byte Order'] = "Intel"
                            elif byte_order.text == "MOST-SIGNIFICANT-BYTE-FIRST":
                                signal_data['Byte Order'] = "Motorola"
                            else:
                                signal_data['Byte Order'] = byte_order.text
                        else:
                            signal_data['Byte Order'] = None

                        for signal_package in signals_package:
                            if signal_name == signal_package.find(f'.//{ns}SHORT-NAME').text:
                                initial_value_ref = signal_package.find(f'.//{ns}VALUE')
                                if initial_value_ref is not None:
                                    int_value_string = initial_value_ref.text
                                    if "0x" in int_value_string:
                                        initial_value = int(int_value_string, 16)
                                    else:
                                        initial_value = int(int_value_string)
                                else:
                                    initial_value = None
                                signal_data["Initial Value"] = initial_value
                                length = signal_package.find(f'.//{ns}LENGTH').text
                                try:
                                    comment = signal_package.find(f'{ns}DESC/{ns}L-2')
                                    if comment is not None:
                                        signal_data['Comment'] = comment.text
                                except:
                                    signal_data['Comment'] = ""
                                signal_data['Length [Bit]'] = int(length)

                                compu_method_obj = signal_package.find(f'.//{ns}COMPU-METHOD-REF')
                                sys_signal_ref_obj = signal_package.find(f'.//{ns}SYSTEM-SIGNAL-REF')
                                if compu_method_obj is not None:
                                    compu_method = compu_method_obj.text.split("/")[-1]
                                elif sys_signal_ref_obj is not None:
                                    sys_signal = sys_signal_ref_obj.text.split("/")[-1]
                                    compu_method = self.get_compu_method(sys_signal, sys_signal_package )
                                else:
                                    compu_method = None

                                if compu_method:
                                    additional_sig_data = self.get_signal_properties(compu_method, compu_package)
                                    signal_data.update(additional_sig_data)
                                else:
                                    signal_data['texttable'] = None
                                    signal_data['Factor'] = 1
                                    signal_data['Offset'] = 0
                                    signal_data['Minimum'] = None
                                    signal_data['Maximum'] = None
                                    signal_data['texttable values'] = None
                                if pdu_type == "N-PDU" or pdu_type == "SECURED-I-PDU":
                                    ArxmlParser.can_frame_entity.append(signal_data)
                                else:
                                    frame_data = ArxmlParser.can_frame_entity[0].copy()
                                    ArxmlParser.can_frame_entity.append(frame_data | signal_data)
                                break
                if found:
                    break
        except Exception as e:
            traceback.print_exc()
            raise e

    def get_compu_method(self, sys_signal, sys_signal_package):
        for sig in sys_signal_package:
            name = sig.find(f'{ns}SHORT-NAME').text
            if sys_signal == name:
                compu_method_ref = sig.findall(f'.//{ns}COMPU-METHOD-REF')
                if not compu_method_ref:
                    return None
                else:
                    compu_method_name = compu_method_ref[0].text.split("/")[-1]
                    return compu_method_name

    def get_signal_properties(self, compu_method_name, compu_data_type):
        try:
            additonal_data = {}

            for compu_method in compu_data_type:
                if compu_method_name == compu_method.find(f'{ns}SHORT-NAME').text:
                    category = compu_method.find(f'{ns}CATEGORY').text
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
                        break
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
                            additonal_data['Minimum'] = int(min_value_ref.text)
                        else:
                            additonal_data['Minimum'] = None
                        max_value_ref = compu_method.find(max_value_path)
                        if max_value_ref is not None:
                            additonal_data['Maximum'] = int(max_value_ref.text)
                        else:
                            additonal_data['Maximum'] = None
                        enum = compu_method.findall(enums_path)
                        enum_entries = []
                        for texttable_entry in enum[1:]:
                            enum_entries.append("LogicalValue: " + texttable_entry.find(
                                f'{ns}LOWER-LIMIT').text + " " + texttable_entry.find(
                                f'{ns}COMPU-CONST/{ns}VT').text)
                        additonal_data['texttable values'] = "\n".join(enum_entries)  # Add texttable values for the signal
                        break

                    elif category == "LINEAR" or category == "SCALE_LINEAR":
                        additonal_data['texttable'] = None  # Texttable is none
                        try:
                            additonal_data['Factor'] = float(compu_method.find(factors_path_type_1).text)
                            additonal_data['Offset'] = float(compu_method.find(offsets_path_type_1).text)
                            additonal_data['texttable values'] = None
                        except:
                            additonal_data['Factor'] = float(compu_method.find(factors_path_type_2).text)
                            additonal_data['Offset'] = float(compu_method.find(offsets_path_type_2).text)
                            additonal_data['texttable values'] = None
                        min_value_ref = compu_method.find(min_value_path)
                        if min_value_ref is not None:
                            additonal_data['Minimum'] = int(min_value_ref.text)
                        else:
                            additonal_data['Minimum'] = None
                        max_value_ref = compu_method.find(max_value_path)
                        if max_value_ref is not None:
                            additonal_data['Maximum'] = int(max_value_ref.text)
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

                    break

            return additonal_data
        except:
            traceback.print_exc()
            raise Exception

    def create_nodes(self, signals_full_data, excel_node, direction):
        if direction.lower() == "tx":
            dir_string = "OUT"
        elif direction.lower() == "rx":
            dir_string = "IN"
        else:
            raise "Unknown signal direction"

        ''' Separate nodes'''
        sig_ready_for_df = []
        for signal in signals_full_data:
            if signal[0]["DIRECTION"] == dir_string and signal[0]["NETWORK"] == excel_node[0]:
                sig_ready_for_df.append(signal)

        return sig_ready_for_df

    def create_dataframe(self, data, variant_dict):

        try:
            # df_template = pd.DataFrame(columns=['Name', 'PDU', "PDU Type", "Payload PDU", 'Message', "Multiplexing/Group", 'Startbit',
            #                                'Length [Bit]', 'Byte Order', "Initial Value",
            #                                'Factor', 'Offset', 'Minimum',
            #                                'Maximum', 'Message ID', 'Cycle Time [ms]', 'Comment','texttable', 'texttable values',
            #                                'EndToEndProtection', 'Block_size', 'Address_formate', 'Padding_active', 'STMin',
            #                             'MAXFC_wait'])
            
            data_set = []
            for row_list in data:
                for row in row_list:
                    data_set.append(row)
            df_template = pd.DataFrame(data_set, columns=['Name', 'PDU', "PDU Type", "group", "Payload PDU", 'Message', 'Message ID', "Multiplexing/Group", 'Startbit',
                                           'Length [Bit]', 'Byte Order', "Initial Value", 'Factor', 'Offset', 'Minimum',
                                           'Maximum','max_value', 'Cycle Time [ms]', 'texttable', 'texttable values',
                                           'Value Type', 'Unit', 'Comment', "dlc", 'variant', 'Value Table', 'EndToEndProtection', 'Block_size', 'Address_formate', 'Padding_active', 'STMin',
                                        'MAXFC_wait'])
            

            df_template['variant'] = df_template['variant'].fillna('')
               
            #df_data = pd.DataFrame.from_dict(data_set)
            # if df_template.empty:
            #     df_template = df_data
            # else:
            #     df_template = pd.concat([df_template, df_data], sort=True, ignore_index=True).fillna('')

            # columns_to_add = {"group": 1, 'Value Type': 9, 'Unit': 15, 'Value Table': 16,
            #                   "max_value": 23, "dlc": 24, "variant": 25}
            # for key, value in columns_to_add.items():
            #     df_template.insert(value, key, '')

            # fill variants
            for i, row in df_template.iterrows():
                # fill variant column
                if row['PDU'] in variant_dict["a_variant"]:
                    df_template.loc[i, "variant"] = "a_variant"
                    #df_template["variant"][i] = "a_variant"
                elif row['PDU'] in variant_dict["b_variant"]:
                    df_template.loc[i, "variant"] = "b_variant"
                    #df_template["variant"][i] = "b_variant"
                else:
                    df_template.loc[i, "variant"] = "Common"
                    #df_template["variant"][i] = "Common"

                # fill max_value column
                try:
                    if not(pd.isna(df_template.loc[i, "Length [Bit]"]) or (df_template.loc[i, "Length [Bit]"] == '')):
                        if df_template.loc[i, "Byte Order"].upper() != 'OPAQUE' and df_template.loc[i, "Length [Bit]"] <100:
                            df_template.loc[i, "max_value"] = (2 ** (int(df_template.loc[i, "Length [Bit]"]))) - 1
                except:
                    pass

            df_template = df_template.reindex(columns=['Name', 'PDU', "PDU Type", "group", "Payload PDU", 'Message', 'Message ID', "Multiplexing/Group", 'Startbit',
                                           'Length [Bit]', 'Byte Order', "Initial Value", 'Factor', 'Offset', 'Minimum',
                                           'Maximum','max_value', 'Cycle Time [ms]', 'texttable', 'texttable values',
                                           'Value Type', 'Unit', 'Comment', "dlc", 'variant', 'Value Table', 'EndToEndProtection', 'Block_size', 'Address_formate', 'Padding_active', 'STMin',
                                        'MAXFC_wait'])


            return df_template
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Failed to create dataframe --> {e}")
            raise e

    def write_to_excel(self, sheets_dict):
        script_path = os.path.dirname(os.path.abspath(__file__))
        try:
            ''' Writing the excel'''
            logger.info("Open Autosar_Gen_Database.xlsx for writing...")
            with pd.ExcelWriter(script_path + r'\..\..\..\..\CustomerPrj\Restbus\Autosar_Gen_Database.xlsx',
                                engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                for sheet, value in sheets_dict.items():
                    value.to_excel(writer, index=False, sheet_name=sheet)
                    logger.info(f"Created sheet --> {sheet}")
            logger.info('DataFrame is written to Excel File successfully.')
        except Exception as e:
            logger.info(f"Failed to write dataframe to excel --> {e}")
            raise e


def external_call():
    """ """
    try:
        logger.info("###### START 'Create Autosar ARXML' DEBUG INFORMATION ######")
        script_path = os.path.dirname(os.path.abspath(__file__))
        arxml_path = script_path + r'\..\..\..\..\CustomerPrj\Restbus\Database\DBC'
        arxml_parse = ArxmlParser()
        arxml_parse.create_arxml_main(arxml_path)
        logger.info("###### END 'Create Autosar ARXML' DEBUG INFORMATION ######")
        logger.info('-' * 80)
    except Exception as exp:
        logger.error(f"Failed to create arxml: {exp}")
        raise Exception(exp)


if __name__ == "__main__":
    external_call()