from copy import deepcopy
import xml.etree.ElementTree as ET
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
import os, sys
import traceback
from lxml import etree

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


ns = "{http://autosar.org/schema/r4.0}"

class AdaptiveArxmlParser:
    """AUTOSAR_00050.xsd and above"""
    
    def __init__(self, file_path):
        self.root = ET.parse(file_path).getroot()
        self.file = file_path
        
    @staticmethod   
    def data_extractor(element):
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
            child_attributes = AdaptiveArxmlParser.data_extractor(child_element)
            dictt.update(child_attributes)
        return dictt
    
    @staticmethod
    def get_ref_name(ref_path):
        return ref_path.split("/")[-1]
    
    @staticmethod
    def get_short_name(element):
        return element.find(f'{ns}SHORT-NAME').text
    
    @staticmethod
    def map_implementation_datatypes(DATATYPE_DICT):
        print('code still not implemented')
    
    def get_machine_to_machinedesign_map(self):
        machines = self.root.findall(f'.//{ns}MACHINE')
        machine_info_dict = {}
        for machine in machines:
            machine_name = self.get_short_name(machine)
            machine_design_ref = self.get_ref_name(machine.find(f'{ns}MACHINE-DESIGN-REF').text)
            machine_info_dict[machine_design_ref] = machine_name
        return machine_info_dict
    
    def get_ap_application_endpoints_info(self, ap_application_endpoints_list):
        ap_application_endpoints_info_dict = {}
        for ap_application_endpoint in ap_application_endpoints_list:
            ap_application_endpoint_name = self.get_short_name(ap_application_endpoint)
            ap_application_endpoints_info_dict[ap_application_endpoint_name] = {}
            upd_tp_port = ap_application_endpoint.find(f'.//{ns}UDP-TP-PORT')
            tcp_tp_port = ap_application_endpoint.find(f'.//{ns}TCP-TP-PORT')
            if upd_tp_port is not None:
                ap_application_endpoints_info_dict[ap_application_endpoint_name]['PROTOCOL'] = 'UDP'
                ap_application_endpoints_info_dict[ap_application_endpoint_name]['PORT'] = upd_tp_port.find(f'{ns}PORT-NUMBER').text
            elif tcp_tp_port is not None:
                ap_application_endpoints_info_dict[ap_application_endpoint_name]['PROTOCOL'] = 'TCP'
                ap_application_endpoints_info_dict[ap_application_endpoint_name]['PORT'] = tcp_tp_port.find(f'{ns}PORT-NUMBER').text
            else:
                continue
        return ap_application_endpoints_info_dict
    
    def get_eth_connectors_info(self, ethernet_connectors_list):
        eth_connectors_info_dict = {}
        for eth_connector in ethernet_connectors_list:
            eth_connector_name = self.get_short_name(eth_connector)
            eth_connectors_info_dict[eth_connector_name] = {}
            ap_application_endpoints = eth_connector.findall(f'.//{ns}AP-APPLICATION-ENDPOINT')
            if ap_application_endpoints:
                eth_connectors_info_dict[eth_connector_name]['AP-APPLICATION-ENDPOINT'] = self.get_ap_application_endpoints_info(ap_application_endpoints)
            
            nwt_endpoint_ref = eth_connector.find(f'.//{ns}NETWORK-ENDPOINT-REF')
            if nwt_endpoint_ref is not None:
                eth_connectors_info_dict[eth_connector_name]['NWT_ENDPOINT_REF'] = nwt_endpoint_ref.text
            
            unicast_nwt_endpoint_ref = eth_connector.find(f'{ns}UNICAST-NETWORK-ENDPOINT-REF')
            if unicast_nwt_endpoint_ref is not None:
                eth_connectors_info_dict[eth_connector_name]['UNICAST_NWT_ENDPOINT_REF'] = unicast_nwt_endpoint_ref.text
        return eth_connectors_info_dict
            
    def get_someip_service_discovery_info(self, service_discovery_configs_list):
        service_discovery_configs_info_list = []
        for SD in service_discovery_configs_list:
            SD_info = {}
            sd_multicast_address = SD.find(f'{ns}MULTICAST-SD-IP-ADDRESS-REF')
            if sd_multicast_address.text is not None:
                SD_info['SD_IP_ADDRESS_REF'] = sd_multicast_address.text
                SD_info['SD_PORT'] = self.data_extractor(SD).get('SOMEIP-SERVICE-DISCOVERY-PORT', '')
                service_discovery_configs_info_list.append(SD_info)
        return service_discovery_configs_info_list
        
    def get_machine_design_info(self):
        machine_designs = self.root.findall(f'.//{ns}MACHINE-DESIGN')
        machine_design_info_dict = {}
        for MD in machine_designs:
            md_name = self.get_short_name(MD)
            machine_design_info_dict[md_name] = {}
            ethernet_connectors = MD.findall(f'.//{ns}ETHERNET-COMMUNICATION-CONNECTOR')
            if ethernet_connectors:
                machine_design_info_dict[md_name]['ETHERNET-COMMUNICATION-CONNECTOR'] = self.get_eth_connectors_info(ethernet_connectors)
            service_discovery_configs = MD.findall(f'.//{ns}SOMEIP-SERVICE-DISCOVERY')
            if service_discovery_configs:
                machine_design_info_dict[md_name]['SOMEIP-SERVICE-DISCOVERY'] = self.get_someip_service_discovery_info(service_discovery_configs)
        return machine_design_info_dict
    
    def get_ethernet_cluster_info(self):
        eth_cluster_info = {}
        ethernet_clusters = self.root.findall(f'.//{ns}ETHERNET-CLUSTER')
        for eth_cluster in ethernet_clusters:
            cluster_name = self.get_short_name(eth_cluster)
            if cluster_name not in eth_cluster_info:
                eth_cluster_info[cluster_name] = {}
            ethernet_physical_channels = eth_cluster.findall(f'.//{ns}ETHERNET-PHYSICAL-CHANNEL')
    
            for channel in ethernet_physical_channels:
                channel_name = self.get_short_name(channel)
                if channel_name not in eth_cluster_info[cluster_name]:
                    eth_cluster_info[cluster_name][channel_name] = {}

                eth_cluster_info[cluster_name][channel_name]['NETWORK-ENDPOINTS'] = {}
                eth_cluster_info[cluster_name][channel_name]['VLAN'] = {}
                nwt_endpoints = channel.findall(f'.//{ns}NETWORK-ENDPOINT')
                if nwt_endpoints:

                    for nwt_endpoint in nwt_endpoints:
                        nwt_endpoint_name = self.get_short_name(nwt_endpoint)
                        eth_cluster_info[cluster_name][channel_name]['NETWORK-ENDPOINTS'][nwt_endpoint_name] = {}
                        #ipv4
                        ipv4_info = nwt_endpoint.find(f'.//{ns}IPV-4-CONFIGURATION')
                        if ipv4_info is not None:
                            ipv4_info = self.data_extractor(ipv4_info)
                            eth_cluster_info[cluster_name][channel_name]['NETWORK-ENDPOINTS'][nwt_endpoint_name]['IPV4_ADDRESS'] = ipv4_info.get('IPV-4-ADDRESS', '')
                            eth_cluster_info[cluster_name][channel_name]['NETWORK-ENDPOINTS'][nwt_endpoint_name]['IPV4_MASK'] = ipv4_info.get('NETWORK-MASK', '')
                            eth_cluster_info[cluster_name][channel_name]['NETWORK-ENDPOINTS'][nwt_endpoint_name]['IPV4_ADDRESS_SOURCE'] = ipv4_info.get('IPV-4-ADDRESS-SOURCE', '')
                vlan_info = channel.find(f'.//{ns}VLAN')
                if vlan_info is not None:
                    eth_cluster_info[cluster_name][channel_name]['VLAN'] = self.data_extractor(vlan_info)


        return eth_cluster_info
    
    def get_computation_methods(self):
        compu_method_dict = {}
        compu_method_pakages = self.root.findall(f'.//{ns}COMPU-METHOD')
        for com_method in compu_method_pakages:
            compu_name = self.get_short_name(com_method)
            try:
                category = com_method.find(f'.//{ns}CATEGORY').text
                unit = com_method.find(f'.//{ns}UNIT-REF')
                if unit:
                    unit = self.get_ref_name(unit.text).replace("NoUnit","")
                else:
                    unit=""

                temp = {}
                temp["unit"] = unit
                temp["elem_dtype"] = category
                if category == "LINEAR" or category == "SCALE_LINEAR":
                    try:
                        temp["Minimum"] = com_method.find(min_value_path).text
                        temp["Maximum"] = com_method.find(max_value_path).text
                    except:
                        compu_method_dict[compu_name] = temp
                        continue
                    #factor offset
                elif "TEXTTABLE" in category:
                    com_scales = com_method.findall(f'.//{ns}COMPU-SCALE')
                    t=[]
                    texttable = ""
                    for cs in com_scales:
                        key = cs.find(f'.//{ns}LOWER-LIMIT').text
                        try:
                            t.append(int(key))
                        except ValueError as vr:
                            if 'x' in key.lower():
                                t.append(int(key, 16))
                            else:
                                logger.warning(f'Error in {compu_name} texttable info extraction -> {vr}')
                                compu_method_dict[compu_name] = temp
                                continue
                        
                        value = cs.find(f'.//{ns}COMPU-CONST//{ns}VT').text
                        texttable+=f"{key}: {value}\n"
                    temp["Minimum"] = min(t)
                    temp["Maximum"] = max(t)
                    temp["texttable"] = texttable
                else:
                    try:
                        temp["Minimum"] = com_method.find(min_value_path).text
                        temp["Maximum"] = com_method.find(max_value_path).text
                    except:
                        compu_method_dict[compu_name] = temp
                        continue
                compu_method_dict[compu_name] = temp
            except Exception as e:
                logger.warning(f"Error occurred while extracting Computation method info of -> {compu_name} -> {e}")
                traceback.print_exc()
                compu_method_dict[compu_name] = temp
                continue
        return {'COMPU-METHOD': compu_method_dict}

    def get_implementation_dtypes(self):
        implementation_dtype_dict = {}
        ar_packages = self.root.findall(f'.//{ns}AR-PACKAGE')
        for ar_package in ar_packages:
            ar_package_name = self.get_short_name(ar_package)
            std_cpp_datatype_packages = ar_package.findall(f'{ns}ELEMENTS//{ns}STD-CPP-IMPLEMENTATION-DATA-TYPE')

            if std_cpp_datatype_packages:
                if ar_package_name not in implementation_dtype_dict:
                    implementation_dtype_dict[ar_package_name] = {}
                for std_cpp_imple_dtype in std_cpp_datatype_packages:
                    std_cpp_name = self.get_short_name(std_cpp_imple_dtype)
                    try:
                        category = std_cpp_imple_dtype.find(f'.//{ns}CATEGORY').text
                        temp = {}
                        temp["category"] = category

                        if category in ['VECTOR', 'ARRAY']:
                            temp["array_size"] = ''
                            array_size = std_cpp_imple_dtype.find(f'.//{ns}ARRAY-SIZE')
                            if array_size is not None:
                                temp["array_size"] = array_size.text
                                try:
                                    if int(array_size.text) > 50:
                                        temp["array_size"] = 30
                                except:
                                    pass
                            temp["element_info"] = {}
                            element_infos = std_cpp_imple_dtype.find(f'.//{ns}CPP-TEMPLATE-ARGUMENT')
                            temp["element_info"]["category"] = std_cpp_imple_dtype.find(f'.//{ns}CATEGORY').text
                            #self.get_ref_name(element_infos.find(f'.//{ns}TEMPLATE-TYPE-REF').text)
                            temp["element_info"]["text"] = (element_infos.find(f'.//{ns}TEMPLATE-TYPE-REF').text.split("/")[-2], element_infos.find(f'.//{ns}TEMPLATE-TYPE-REF').text.split("/")[-1])  #(ar_package_name, type_name)
                            temp["element_info"]["DEST"] = element_infos.find(f'.//{ns}TEMPLATE-TYPE-REF').get('DEST')

                        elif category in ['STRUCTURE', 'VARIANT']:
                            temp["members"] = []
                            members = std_cpp_imple_dtype.findall(f'.//{ns}CPP-IMPLEMENTATION-DATA-TYPE-ELEMENT')
                            for mem in members:
                                strct_memb_info = {}
                                strct_memb_info["mem_name"] = mem.find(f'.//{ns}SHORT-NAME').text
                                strct_memb_info["text"] = (mem.find(f'.//{ns}TYPE-REFERENCE-REF').text.split("/")[-2], mem.find(f'.//{ns}TYPE-REFERENCE-REF').text.split("/")[-1])  #(ar_package_name, type_name)
                                #self.get_ref_name(mem.find(f'.//{ns}TYPE-REFERENCE-REF').text)
                                strct_memb_info["DEST"] = mem.find(f'.//{ns}TYPE-REFERENCE-REF').get('DEST')
                                temp["members"].append(deepcopy(strct_memb_info))

                        elif category == "TYPE_REFERENCE":
                            temp["text"] = (std_cpp_imple_dtype.find(f'.//{ns}TYPE-REFERENCE-REF').text.split("/")[-2], std_cpp_imple_dtype.find(f'.//{ns}TYPE-REFERENCE-REF').text.split("/")[-1])  #(ar_package_name, type_name)
                            #self.get_ref_name(std_cpp_imple_dtype.find(f'.//{ns}TYPE-REFERENCE-REF').text)
                            temp["DEST"] = std_cpp_imple_dtype.find(f'.//{ns}TYPE-REFERENCE-REF').get('DEST')
                        elif category == "VALUE":
                            compu_ref = std_cpp_imple_dtype.find(f'.//{ns}COMPU-METHOD-REF')
                            if compu_ref is not None:
                                temp["compu_method"] = self.get_ref_name(compu_ref.text)
                                temp["compu_DEST"] = compu_ref.get('DEST')
                            type_ref = std_cpp_imple_dtype.find(f'.//{ns}TYPE-REFERENCE-REF')
                            if type_ref is not None:
                                temp["text"] = (type_ref.text.split("/")[-2], type_ref.text.split("/")[-1])  #(ar_package_name, type_name)
                                #self.get_ref_name(type_ref.text)
                                temp["DEST"] = type_ref.get('DEST')
                        elif category == "STRING":
                            temp["dtype"] = 'string'
                        else:
                            print(f"new datatype found --> {std_cpp_name} --> {category}, not handled in code")
                        implementation_dtype_dict[ar_package_name][std_cpp_name] = temp
                    except Exception as e:
                        print(
                            f"Error occurred while extracting STD-CPP-IMPLEMENTATION-DATA-TYPE info of -> {std_cpp_name} -> {e}")
                        traceback.print_exc()
                        continue
        return {'STD-CPP-IMPLEMENTATION-DATA-TYPE': implementation_dtype_dict}
        
    
    def get_events_info(self, service_interface):
        events_package = service_interface.findall(f'.//{ns}VARIABLE-DATA-PROTOTYPE')
        events_info_dict = {}
        for elem in events_package:
            elements_dict={}
            elem_name = self.get_short_name(elem)
            try:
                elements_dict["Member_name"] = elem_name
                elements_dict["Member_type"] = "event"
                elem_type_ref = elem.find(f'.//{ns}TYPE-TREF')
                elem_type = elem_type_ref.get("DEST")
                elem_type_name = (elem_type_ref.text.split("/")[-2], elem_type_ref.text.split("/")[-1])  #(ar_package_name, type_name)
                elem_info = {"DEST":elem_type, "text":elem_type_name}
                elements_dict["Member_info"] = elem_info

                events_info_dict[elem_name]=elements_dict
            except Exception as e:
                logger.warning(f"Error occurred while extracting EVENT variables info of -> {elem_name} -> {e}")
                continue
        return events_info_dict
    
    def get_fields_info(self, service_interface):
        fields_package = service_interface.findall(f'.//{ns}FIELD')
        fields_info_dict = {}
        for elem in fields_package:
            elements_dict={}
            elem_name = self.get_short_name(elem)
            try:
                elements_dict["Member_name"] = elem_name
                elements_dict["Member_type"] = "field"
                elem_type_ref = elem.find(f'.//{ns}TYPE-TREF')
                elem_type = elem_type_ref.get("DEST")
                elem_type_name = (elem_type_ref.text.split("/")[-2], elem_type_ref.text.split("/")[-1])  #(ar_package_name, type_name)
                elem_info = {"DEST":elem_type, "text":elem_type_name}
                elements_dict["Member_info"] = elem_info
                
                field_data = self.data_extractor(elem)
                elements_dict["HAS-GETTER"] = field_data.get("HAS-GETTER","-")
                elements_dict["HAS-SETTER"] = field_data.get("HAS-SETTER","-")
                elements_dict["HAS-NOTIFIER"] = field_data.get("HAS-NOTIFIER","-")

                fields_info_dict[elem_name]=elements_dict
            except Exception as e:
                logger.warning(f"Error occurred while extracting FIELD variables info of -> {elem_name} -> {e}")
                continue
        return fields_info_dict
    
    def get_methods_info(self, service_interface):
        methods_info_dict = {}
        methods_package = service_interface.findall(f'.//{ns}CLIENT-SERVER-OPERATION')
        for operation in methods_package:
            operation_info = {}
            op_name = self.get_short_name(operation)
            try:
                operation_info["Member_name"] = op_name
                operation_info["Member_type"] = "method"
                fire_and_forget = operation.find(f'.//{ns}FIRE-AND-FORGET')
                if fire_and_forget is not None:
                    operation_info["fire_and_forget"] = fire_and_forget.text
                op_arguements = operation.findall(f'.//{ns}ARGUMENT-DATA-PROTOTYPE')
                op_arguements_list = []
                for arg in op_arguements:
                    arg_name = self.get_short_name(arg)
                    temp={}
                    temp["arg_name"] = arg_name
                    direction = arg.find(f'.//{ns}DIRECTION').text.upper()
                    dir_mapping = {"IN":"IN_PARAMETERS", "OUT":"RETURN_PARAMETERS","INOUT":"INOUT"}
                    temp["direction"]=dir_mapping.get(direction,direction)

                    arg_type_ref = arg.find(f'.//{ns}TYPE-TREF')
                    arg_type = arg_type_ref.get("DEST")
                    arg_type_name = (arg_type_ref.text.split("/")[-2], arg_type_ref.text.split("/")[-1])  #(ar_package_name, type_name)
                    
                    temp["arg_info"] = {"DEST":arg_type, "text":arg_type_name}
                    op_arguements_list.append(temp)

                operation_info["arguements"]=op_arguements_list
                methods_info_dict[op_name] = operation_info
            except Exception as e:
                logger.warning(f"Error occurred while extracting METHOD info of -> {op_name} -> {e}")
                continue
        return methods_info_dict
        
    def get_service_interfaces_info(self):
        services_interfaces = self.root.findall(f'.//{ns}SERVICE-INTERFACE')
        service_interface_info_dict = {}
        for service_interface in services_interfaces:
            service_name = self.get_short_name(service_interface)
            try:
                major_version = service_interface.find(f'{ns}MAJOR-VERSION').text
                minor_version = service_interface.find(f'{ns}MINOR-VERSION').text
            except:
                major_version = ''
                minor_version = ''
            temp = {}
            temp['major_version'] = major_version
            temp['minor_version'] = minor_version
            temp['EVENTS'] = self.get_events_info(service_interface)
            temp['FIELDS'] = self.get_fields_info(service_interface)
            temp['METHODS'] = self.get_methods_info(service_interface)
            service_interface_info_dict[service_name] = temp
        return service_interface_info_dict
    
    def get_event_groups_info(self, service_interface_deployment):
        event_groups = service_interface_deployment.findall(f'.//{ns}SOMEIP-EVENT-GROUP')
        event_group_info_dict = {}
        for evnt_grp in event_groups:
            evnt_grp_name = self.get_short_name(evnt_grp)
            evnt_grp_id = evnt_grp.find(f'{ns}EVENT-GROUP-ID').text
            events_refs = evnt_grp.findall(f'.//{ns}EVENT-REF')
            for evnt_ref in events_refs:
                event_name = self.get_ref_name(evnt_ref.text)
                event_group_info_dict[event_name] = [evnt_grp_id, evnt_grp_name]
        return event_group_info_dict
        
    def get_events_deployments_info(self, service_interface_deployment):
        events_deployments = service_interface_deployment.findall(f'.//{ns}SOMEIP-EVENT-DEPLOYMENT')
        events_dps = {}
        for event_deployment in events_deployments:
            event_name = self.get_ref_name(event_deployment.find(f'{ns}EVENT-REF').text)
            event_id = event_deployment.find(f'{ns}EVENT-ID').text
            event_tp_protocol = event_deployment.find(f'{ns}TRANSPORT-PROTOCOL').text
            events_dps[event_name] = {'event_id':event_id, 'event_tp_protocol': event_tp_protocol}
        return events_dps
    
    def get_fields_deployments_info(self, service_interface_deployment):
        fields_deployments = service_interface_deployment.findall(f'.//{ns}SOMEIP-FIELD-DEPLOYMENT')
        fields_dps = {}
        for field_deployment in fields_deployments:
            temp = {}
            field_name = self.get_ref_name(field_deployment.find(f'{ns}FIELD-REF').text)
            temp['getter_info'] = self.data_extractor(field_deployment.find(f'{ns}GET'))
            temp['setter_info'] = self.data_extractor(field_deployment.find(f'{ns}SET'))
            temp['notifier_info'] = self.data_extractor(field_deployment.find(f'{ns}NOTIFIER'))
            fields_dps[field_name] = temp
        return fields_dps
    
    def get_methods_deployments_info(self, service_interface_deployment):
        methods_deployments = service_interface_deployment.findall(f'.//{ns}SOMEIP-METHOD-DEPLOYMENT')
        methods_dps = {}
        for method_deployment in methods_deployments:
            method_name = self.get_ref_name(method_deployment.find(f'{ns}METHOD-REF').text)
            methods_dps[method_name] = self.data_extractor(method_deployment)
        return methods_dps
    
    def get_service_interface_deployments_info(self):
        service_interface_deployments = self.root.findall(f'.//{ns}SOMEIP-SERVICE-INTERFACE-DEPLOYMENT')
        service_interface_deployment_dict = {}
        for service_interface_deployment in service_interface_deployments:
            sid_info_dict = {}
            service_interface_deployment_name = self.get_short_name(service_interface_deployment)
            sid_info_dict['service_interface_id'] = service_interface_deployment.find(f'{ns}SERVICE-INTERFACE-ID').text
            sid_info_dict['major_version'] = service_interface_deployment.find(f'.//{ns}MAJOR-VERSION').text
            sid_info_dict['minor_version'] = service_interface_deployment.find(f'.//{ns}MINOR-VERSION').text
            sid_info_dict['service_ref_name'] = self.get_ref_name(service_interface_deployment.find(f'{ns}SERVICE-INTERFACE-REF').text)
            
            #events info
            event_groups_dict = self.get_event_groups_info(service_interface_deployment)
            event_deployments_dict = self.get_events_deployments_info(service_interface_deployment)
            for evnt_name, evnt_info in event_deployments_dict.items():
                try:
                    event_deployments_dict[evnt_name]['event_group_id'] = event_groups_dict.get(evnt_name, [])[0]
                    event_deployments_dict[evnt_name]['event_group_name'] = event_groups_dict.get(evnt_name, [])[1]
                except:
                    logger.warning(f"Error while trying to fetch Event group info for event {evnt_name} of service {sid_info_dict['service_interface_id']}")
            sid_info_dict['event_deployments'] = event_deployments_dict
            #fields info
            field_deployments_dict = self.get_fields_deployments_info(service_interface_deployment)
            for field_name, field_info in field_deployments_dict.items():
                if field_info.get('notifier_info', {}):
                    field_deployments_dict[field_name]['notifier_info']['event_group_id'] = event_groups_dict.get(field_info.get('notifier_info', {}).get('SHORT-NAME', ''),  ['',''])[0]
                    field_deployments_dict[field_name]['notifier_info']['event_group_name'] = event_groups_dict.get(field_info.get('notifier_info', {}).get('SHORT-NAME', ''),  ['',''])[1]
        
            sid_info_dict['field_deployments'] = field_deployments_dict
            
            
            #methods info
            sid_info_dict['methods_deployments'] = self.get_methods_deployments_info(service_interface_deployment)
            
            service_interface_deployment_dict[service_interface_deployment_name] = sid_info_dict
            
        return service_interface_deployment_dict
    
    def get_sd_client_service_instance_config_info(self):
        client_sd_configs = self.root.findall(f'.//{ns}SOMEIP-SD-CLIENT-SERVICE-INSTANCE-CONFIG')
        client_sd_configs_info_dict = {}
        for client_sd_config in client_sd_configs:
            client_sd_configs_info_dict[self.get_short_name(client_sd_config)] = self.data_extractor(client_sd_config)
        return client_sd_configs_info_dict
            
    
    def get_service_instances_info(self):
        required_service_instances = self.root.findall(f'.//{ns}REQUIRED-SOMEIP-SERVICE-INSTANCE')
        required_service_instances_dict = {}
        for rq_service_instance in required_service_instances:
            r_name = self.get_short_name(rq_service_instance)
            required_service_instances_dict[r_name] = self.data_extractor(rq_service_instance)
            #print(required_service_instances_dict[r_name])
            
        provided_service_instances = self.root.findall(f'.//{ns}PROVIDED-SOMEIP-SERVICE-INSTANCE')
        provided_service_instances_dict = {}
        for pvd_service_instance in provided_service_instances:
            p_name = self.get_short_name(pvd_service_instance)
            provided_service_instances_dict[p_name] = self.data_extractor(pvd_service_instance)
            
        return {'REQUIRED-SOMEIP-SERVICE-INSTANCE':required_service_instances_dict,
               'PROVIDED-SOMEIP-SERVICE-INSTANCE':provided_service_instances_dict}
     
        
#     def get_service_to_machine_mappings(self):
#         service_machine_mappings = self.root.findall(f'.//{ns}SOMEIP-SERVICE-INSTANCE-TO-MACHINE-MAPPING')
#         service_machine_mappings_info_dict = {}
#         for service_machine_mapping in service_machine_mappings:
#             info = {}
#             mapping_name = self.get_short_name(service_machine_mapping)
#             info['communication_connector'] = self.get_ref_name(service_machine_mapping.find(f'{ns}COMMUNICATION-CONNECTOR-REF').text)
#             service_instance_refs = service_machine_mapping.findall(f'.//{ns}SERVICE-INSTANCE-REF')
#             si_refs_dict={}
#             for si_ref in service_instance_refs:
#                 dest = si_ref.get('DEST')
#                 if dest not in si_refs_dict:
#                     si_refs_dict[dest] = []
#                 si_refs_dict[dest].append(self.get_ref_name(si_ref.text))
                
#             info['service_instance_refs'] = si_refs_dict
            
#             udp_port_ref = service_machine_mapping.find(f'{ns}UDP-PORT-REF')
#             tcp_port_ref = service_machine_mapping.find(f'{ns}TCP-PORT-REF')
            
#             if udp_port_ref is not None:
#                 info['port_ref'] = self.get_ref_name(udp_port_ref.text)
#             elif tcp_port_ref is not None:
#                 info['port_ref'] = self.get_ref_name(tcp_port_ref.text)
        
#             service_machine_mappings_info_dict[mapping_name] = info
#         return service_machine_mappings_info_dict
    
    def get_service_to_machine_mappings(self):
        service_machine_mappings = self.root.findall(f'.//{ns}SOMEIP-SERVICE-INSTANCE-TO-MACHINE-MAPPING')
        service_machine_mappings_info_dict = {}
        for service_machine_mapping in service_machine_mappings:
            comm_conn_ref = service_machine_mapping.find(f'{ns}COMMUNICATION-CONNECTOR-REF').text
            commu_connector_name = self.get_ref_name(comm_conn_ref)
            machine_design = comm_conn_ref.split('/')[-2]
            if machine_design not in service_machine_mappings_info_dict:
                service_machine_mappings_info_dict[machine_design] = {}
            if commu_connector_name not in service_machine_mappings_info_dict[machine_design]:
                service_machine_mappings_info_dict[machine_design][commu_connector_name] = {}
                
            service_instance_refs = service_machine_mapping.findall(f'.//{ns}SERVICE-INSTANCE-REF')
            for service_instance_ref in service_instance_refs:
                info = {}
                info['communication-connector-ref'] = comm_conn_ref
                if service_instance_ref is not None:
                    dest = service_instance_ref.get('DEST')
                    if dest not in service_machine_mappings_info_dict[machine_design][commu_connector_name]:
                        service_machine_mappings_info_dict[machine_design][commu_connector_name][dest] = []
                    service_ref_name = self.get_ref_name(service_instance_ref.text)
                    info['service_instance_ref'] = service_ref_name
                    udp_port_ref = service_machine_mapping.find(f'{ns}UDP-PORT-REF')
                    tcp_port_ref = service_machine_mapping.find(f'{ns}TCP-PORT-REF')

    #                 if udp_port_ref is not None:
    #                     info['port_ref'] = self.get_ref_name(udp_port_ref.text)
    #                 elif tcp_port_ref is not None:
    #                     info['port_ref'] = self.get_ref_name(tcp_port_ref.text)
                    if udp_port_ref is not None:
                        info['port_ref'] = udp_port_ref.text
                    elif tcp_port_ref is not None:
                        info['port_ref'] = tcp_port_ref.text

                    service_machine_mappings_info_dict[machine_design][commu_connector_name][dest].append(info)
                
        return service_machine_mappings_info_dict
            
            
    def __str__(self):
        return self.file
    





def getAdaptiveSomeIpData(arxml_file_path):
    """_summary_

    Args:
        arxml_file_path (_type_): _description_
    """

    def get_type_reference_info():
        pass

    def find_data_structure(dest, name):
        datatype_info = DATATYPES_DICT[dest][name[0]][name[1]].copy()
        category = datatype_info.get('category','')

        if category in ['VALUE','TYPE_REFERENCE']:
            imp_dtype = datatype_info.get('text', ('', ''))
            imp_dtype = DATATYPES_DICT[dest].get(imp_dtype[0], {}).get(imp_dtype[1], datatype_info).copy()
            imp_dtype = imp_dtype.get('text', datatype_info.get('text', ('','')))[1]
            datatype_info['signal_dtype'] = imp_dtype.lower()

            #get compudata
            compu_data = DATATYPES_DICT.get('COMPU-METHOD',{}).get(datatype_info.get('compu_method', ''), {})
            datatype_info['minimum'] = compu_data.get('Minimum')
            datatype_info['maximum'] = compu_data.get('Maximum')
            datatype_info['unit'] = compu_data.get('unit')
            return datatype_info
        elif category in ['STRING']:
            datatype_info['signal_dtype'] = 'string'
            return datatype_info
        elif category in ['ARRAY', 'VECTOR']:
            # if datatype_info['elem_dtype'] == 'VALUE':
            #     datatype_info.update(DATATYPES_DICT[datatype_info['element_info']['DEST']][datatype_info['element_info']['text']])
            #     del datatype_info['element_info']
            #     return datatype_info
            # else:
            datatype_info['element_info'] = find_data_structure(datatype_info['element_info']['DEST'], datatype_info['element_info']['text'])
            return datatype_info
        elif category in ['STRUCTURE', 'VARIANT']:
            structure_elements_list = []
            for struct_elem in datatype_info.get('members', []):
                temp = DATATYPES_DICT[struct_elem['DEST']][struct_elem['text'][0]][struct_elem['text'][1]]
                st_mem_categ = temp['category']
                if st_mem_categ == 'TYPE_REFERENCE':
                    type_ref_temp = DATATYPES_DICT[struct_elem['DEST']][temp['text'][0]][temp['text'][1]]
                    if type_ref_temp.get('category', '') not in ['VALUE', 'TYPE_REFERENCE']:
                        st_mem_categ = type_ref_temp.get('category', '')
                        struct_elem['text'] = temp.get('text', ('',''))

                if st_mem_categ in ['VALUE','TYPE_REFERENCE', 'STRING']:
                    if st_mem_categ in ['STRING']:
                        struct_elem['signal_dtype'] = 'string'
                    else:
                        imp_dtype = temp.get('text', ('', ''))
                        imp_dtype = DATATYPES_DICT[dest].get(imp_dtype[0], {}).get(imp_dtype[1], temp).copy()
                        imp_dtype = imp_dtype.get('text', temp.get('text', ('', '')))[1]
                        struct_elem['signal_dtype'] = imp_dtype.lower()

                    structure_elements_list.append(struct_elem)
                else:
                    temp = struct_elem.copy()
                    temp['element_info'] = find_data_structure(struct_elem['DEST'], struct_elem['text'])
                    structure_elements_list.append(temp)
            return structure_elements_list
        logger.warning(f"Unknown data structure -> {dest} -> {name} -> {category}")
        return []

    def generate_namespace(data, prefix='', result=None):
        if result is None:
            result = {}
        if isinstance(data, dict):
            if 'mem_name' in data:

                namespace = f'{prefix}.{data["mem_name"]}' if prefix else data["mem_name"]
                
                dest = data.get('DEST','')
                dest_text = data.get('text','  ')
                mem_dtype_info = DATATYPES_DICT[dest][dest_text[0]][dest_text[1]]
                category = mem_dtype_info.get('category','')
                if category in  ['STRUCTURE', 'VARIANT']:
                    generate_namespace(data['element_info'], namespace, result)
                elif category in ['ARRAY', 'VECTOR']:
                    #print(data)
                    arr_size = data['element_info']['array_size']
                    if str(arr_size) == '':
                        arr_size = 10
                    array_namespace = f'{namespace}[{arr_size}]'
                    
                    if ((data['element_info']['category'] in ['VALUE','TYPE_REFERENCE','STRING']) or
                            (isinstance(data['element_info']['element_info'], dict) and (data['element_info']['element_info'].get('category', '') in ['VALUE','TYPE_REFERENCE','STRING']))):
                        result[data['mem_name']] = {
                            'namespace': array_namespace,
                            'minimum': data['element_info']['element_info'].get('Minimum', None),
                            'maximum': data['element_info']['element_info'].get('Maximum', None),
                            'unit': data['element_info']['element_info'].get('unit', None),
                            'signal_dtype': data['element_info']['element_info'].get('signal_dtype', '')
                        }
                    else:
                        generate_namespace(data['element_info']['element_info'], array_namespace, result)
                elif category in ['VALUE','TYPE_REFERENCE','STRING']:
                    if data.get('array_size', None) is not None:
                        result[data['mem_name']] = {
                            'namespace': namespace,
                            'minimum': data['element_info'].get('Minimum', None),
                            'maximum': data['element_info'].get('Maximum', None),
                            'unit': data['element_info'].get('unit', None),
                            'signal_dtype': data['element_info'].get('signal_dtype', '')
                        }
                    else:
                        result[data['mem_name']] = {
                            'namespace': namespace,
                            'minimum': data.get('Minimum', None),
                            'maximum': data.get('Maximum', None),
                            'unit': data.get('unit', None),
                            'signal_dtype': data.get('signal_dtype', '')
                    }
            else:  # if the dictionary is a list of elements
                for item in data.values():
                    if isinstance(item, dict):
                        generate_namespace(item, prefix, result)
                #return result
        elif isinstance(data, list):
            for element in data:
                generate_namespace(element, prefix, result)
        return result
    
    arxml_parser_obj = AdaptiveArxmlParser(arxml_file_path)
    #datatypes-----------------------------------------------------------------------
    DATATYPES_DICT = {}  
    #COMPU-METHOD
    comupation_method_dict = arxml_parser_obj.get_computation_methods()
    for key, value in comupation_method_dict.items():
        if key in DATATYPES_DICT:
            DATATYPES_DICT[key].update(value)
        else:
            DATATYPES_DICT[key] = value
            
    #STD-CPP-IMPLEMENTATION-DATA-TYPE
    implementation_datatype_dict = arxml_parser_obj.get_implementation_dtypes()
    for key, value in implementation_datatype_dict.items():
        if key in DATATYPES_DICT:
            DATATYPES_DICT[key].update(value)
        else:
            DATATYPES_DICT[key] = value


    #service_interfaces--------------------------------------------------------------                    
    SERVICE_INTERFACES = {}
    SERVICE_INTERFACES.update(arxml_parser_obj.get_service_interfaces_info())
    logger.info(f'Found {len(SERVICE_INTERFACES)} service definitions')


    #service_interface_deployments----------------------------------------------------
    SERVICE_INTERFACE_DEPLOYMENTS_DICT = {}
    #SD_CLIENT_SERVICE_INSTANCE_CONFIG_DICT = {}
    SERVICE_INSTANCES_DICT = {}
    SERVICE_TO_MACHINE_MAPPING_DICT = {}
    
    # get service deploymenyts
    SERVICE_INTERFACE_DEPLOYMENTS_DICT.update(arxml_parser_obj.get_service_interface_deployments_info())
    
    #ServiceInstances required or provided
    service_instances_dict = arxml_parser_obj.get_service_instances_info()
    for instance_type, instance_info in service_instances_dict.items():
        if instance_type not in SERVICE_INSTANCES_DICT:
            SERVICE_INSTANCES_DICT[instance_type] = {}
        SERVICE_INSTANCES_DICT[instance_type].update(instance_info)
    
    # get SomeipSdTimingConfigs - SOMEIP-SD-CLIENT-SERVICE-INSTANCE-CONFIG
    #SD_CLIENT_SERVICE_INSTANCE_CONFIG_DICT.update(arxml_parser_obj.get_sd_client_service_instance_config_info())
    

    #get ethernet cluster info
    eth_cluster_info_dict = arxml_parser_obj.get_ethernet_cluster_info()

    #get machine_design_info
    machine_design_info_dict = arxml_parser_obj.get_machine_design_info()

    # get service to machine mapping
    service_machine_mappings_dict = arxml_parser_obj.get_service_to_machine_mappings()




    #extract data------------------------------------------------------------------------------------------------------
    EXTRACT_DICT = {}

    for machine_design, machine_design_info in service_machine_mappings_dict.items():
        EXTRACT_DICT[machine_design] = []
        for comm_connector, comm_connector_info in machine_design_info.items():
            #print(comm_connector_info)
            for service_instance_type, service_instance_list in comm_connector_info.items():
                for elem in service_instance_list:
                    udp_port = ''
                    ip_address = ''
                    vlan_id = ''
                    vlan_name = ''

                    port_ref = elem['port_ref']
                    md_name, chnl_name, port_name = port_ref.rsplit('/', maxsplit=3)[-3:]
                    udp_port = machine_design_info_dict.get(md_name,{}).get('ETHERNET-COMMUNICATION-CONNECTOR',{}).get(chnl_name,{}).get('AP-APPLICATION-ENDPOINT',{}).get(port_name,{}).get('PORT','')
                    unicast_nwt_ref = machine_design_info_dict.get(md_name,{}).get('ETHERNET-COMMUNICATION-CONNECTOR',{}).get(chnl_name,{}).get('UNICAST_NWT_ENDPOINT_REF',None)
                    if unicast_nwt_ref:
                        clst_name, phy_chnl_name, end_point_name = unicast_nwt_ref.rsplit('/', maxsplit=3)[-3:]
                        ip_address = eth_cluster_info_dict.get(clst_name,{}).get(phy_chnl_name,{}).get('NETWORK-ENDPOINTS',{}).get(end_point_name,{}).get('IPV4_ADDRESS','')
                        vlan_id = eth_cluster_info_dict.get(clst_name,{}).get(phy_chnl_name,{}).get('VLAN',{}).get('VLAN-IDENTIFIER', '')
                        vlan_name = eth_cluster_info_dict.get(clst_name,{}).get(phy_chnl_name,{}).get('VLAN',{}).get('SHORT-NAME', '')


                    service_instance = elem['service_instance_ref']
                    service_instance_info = service_instances_dict.get(service_instance_type,{}).get(service_instance,{})
                    #print(service_instance_info)
                    #print('==')
                    
                    srv_dep_ref = service_instance_info['SERVICE-INTERFACE-DEPLOYMENT-REF']
                    
                    service_deployment_info = SERVICE_INTERFACE_DEPLOYMENTS_DICT.get(srv_dep_ref,{})
                    if service_deployment_info == {}:
                        print(f"service_deployment_info not found for -> {service_instance}")
                        continue
                    #print('==')
                    
                    srv_interface_ref = service_deployment_info['service_ref_name']
                    srv_interface_info = SERVICE_INTERFACES.get(srv_interface_ref)
                    #print(srv_interface_info['EVENTS'])
                    #print('==')
                    
                    row = {}
                    row['IP_Address'] = ip_address
                    row['UDP_Port'] = udp_port
                    row['VLAN_ID'] = vlan_id
                    row['VLAN_Name'] = vlan_name

                    row['Service'] = srv_dep_ref
                    row["Service Instance"] = service_instance
                    row['Service ID'] = service_deployment_info.get('service_interface_id','')
                    row['Major version'] = service_deployment_info.get('major_version','')
                    row['Minor version'] = service_deployment_info.get('minor_version','')
                    if 'PROVIDED' in service_instance_type:
                        row['Instance ID'] = service_instance_info.get('SERVICE-INSTANCE-ID','')
                    else:
                        row['Instance ID'] = service_instance_info.get('REQUIRED-SERVICE-INSTANCE-ID','')
                        row['Minor version'] = service_instance_info.get('REQUIRED-MINOR-VERSION',row['Minor version'])
                        
                    row['SD Type'] = service_instance_type
                    
                    #print('==================')
                    
                    #evnets
                    for event_name, event_info in service_deployment_info.get('event_deployments', {}).items():
                        row_event_info = {}
                        row_event_info['Member Type'] = 'event'
                        row_event_info['Member'] = event_name
                        row_event_info['Member ID'] = event_info.get('event_id', '')
                        event_tp_protocol = event_info.get('event_tp_protocol', '')
                        row_event_info['Event Group'] = event_info.get('event_group_name', '')
                        row_event_info['Event_GroupId'] = event_info.get('event_group_id', '')
                        event_dtype_ref = srv_interface_info.get('EVENTS', {}
                                                                        ).get(event_name, {}
                                                                                ).get('Member_info', {}
                                                                                    ).get('text', [])
                        if len(event_dtype_ref) !=2:
                            EXTRACT_DICT[machine_design].append(row_event_info.copy())
                            logger.warning(f'Datatype not found for -> {event_name} for service {srv_dep_ref}')
                            continue
                        #row_event_info['Signal Data Type'] = '/'.join(event_dtype_ref)
                        
                        
                        dtype_info = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(event_dtype_ref[0],{}).get(event_dtype_ref[1], {})
                        
                        if dtype_info:
                            category = dtype_info.get('category', '')
                            if category == 'TYPE_REFERENCE':
                                type_ref_text = dtype_info.get('text', ('',''))
                                type_ref_temp = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(type_ref_text[0],{}).get(type_ref_text[1], {})
                                if type_ref_temp.get('category', '') not in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                    category = type_ref_temp.get('category', '')
                                    event_dtype_ref = dtype_info.get('text', ('',''))
                            if category in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                row_event_info['Signal'] = event_name
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', event_dtype_ref)
                                row_event_info['Signal Data Type'] = dtype_info.get('signal_dtype','')
                                row_event_info.update(row)
                                EXTRACT_DICT[machine_design].append(row_event_info.copy())
                            
                            elif category in ['ARRAY', 'VECTOR']:
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', event_dtype_ref)
                                

                                namespace_info = generate_namespace(dtype_info['element_info'])
                                if type(dtype_info['element_info']) is list:
                                    categ = 'STRUCTURE'
                                else:
                                    categ = dtype_info['element_info']['category']
                                    
                                if categ in ['ARRAY','VECTOR']:
                                    logger.warning('ARRAY of ARRAY - review')
                                if categ in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                        'parameter_dtype_l3',
                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                    for col in clear_row_values:
                                        row_event_info[col] = ''

                                    row_event_info["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                    row_event_info["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                    row_event_info["Unit"] = dtype_info['element_info'].get('unit', None)
                                    row_event_info["Signal Data Type"] = dtype_info['element_info'].get('signal_dtype', None)

                                    row_event_info.update(row)
                                    EXTRACT_DICT[machine_design].append(row_event_info.copy())
                                else:
                                    for s, nms_info in namespace_info.items():
                                        temp_data = {}
                                        clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                            'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                            'parameter_dtype_l4', 'parameter_dtype_l5']
                                        for col in clear_row_values:
                                            temp_data[col] = ''
                                        namespace = nms_info['namespace']
                                        if '.' in namespace:
                                            temp_split = namespace.split('.')
                                            signal = temp_split[-1]
                                            if '[' in signal:
                                                temp_split2 = signal.split('[')
                                                temp_data['Signal'] = temp_split2[0]
                                                temp_data['No of Elements'] = temp_split2[-1].split(']')[0]

                                            else:
                                                temp_data['Signal'] = signal
                                            temp_data["Minimum"] = nms_info.get('minimum', None)
                                            temp_data["Maximum"] = nms_info.get('maximum', None)
                                            temp_data["Unit"] = nms_info.get('unit', None)
                                            temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                            for i,data_structure in enumerate(temp_split[:-1]):
                                                key = f'parameter_dtype_l{i+1}'
                                                temp_data[key] = data_structure
                                        else:
                                            if '[' in namespace:
                                                temp_split = namespace.split('[')
                                                temp_data['Signal'] = temp_split[0]
                                                temp_data['No of Elements'] = temp_split[-1].split(']')[0]

                                            else:
                                                temp_data['Signal'] = namespace
                                            temp_data["Minimum"] = nms_info.get('minimum', None)
                                            temp_data["Maximum"] = nms_info.get('maximum', None)
                                            temp_data["Unit"] = nms_info.get('unit', None)
                                            temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)
                                        row_event_info.update(row)
                                        row_event_info.update(temp_data)
                                        EXTRACT_DICT[machine_design].append(row_event_info.copy())
                            
                            elif category in ['STRUCTURE', 'VARIANT']:
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', event_dtype_ref)
                                namespace_info = generate_namespace(dtype_info)
                                for s, nms_info in namespace_info.items():
                                    temp_data = {}
                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                        'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                    for col in clear_row_values:
                                        temp_data[col] = ''
                                    namespace = nms_info['namespace']
                                    if '.' in namespace:
                                        temp_split = namespace.split('.')
                                        signal = temp_split[-1]
                                        #check if array
                                        if '[' in signal:
                                            temp_split2 = signal.split('[')
                                            temp_data['Signal'] = temp_split2[0]
                                            temp_data['No of Elements'] = temp_split2[-1].split(']')[0]

                                        else:
                                            temp_data['Signal'] = signal
                                        temp_data["Minimum"] = nms_info.get('minimum', None)
                                        temp_data["Maximum"] = nms_info.get('maximum', None)
                                        temp_data["Unit"] = nms_info.get('unit', None)
                                        temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                        for i,data_structure in enumerate(temp_split[:-1]):
                                            key = f'parameter_dtype_l{i+1}'
                                            temp_data[key] = data_structure
                                    else:
                                        #check if array
                                        if '[' in namespace:
                                            temp_split = namespace.split('[')
                                            temp_data['Signal'] = temp_split[0]
                                            temp_data['No of Elements'] = temp_split[-1].split(']')[0]

                                        else:
                                            temp_data['Signal'] = namespace
                                        temp_data["Minimum"] = nms_info.get('minimum', None)
                                        temp_data["Maximum"] = nms_info.get('maximum', None)
                                        temp_data["Unit"] = nms_info.get('unit', None)
                                        temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                    row_event_info.update(temp_data)
                                    row_event_info.update(row)
                                    EXTRACT_DICT[machine_design].append(row_event_info.copy())
                                
                                    
                            else:
                                logger.warning(f'{dtype_info}- review')
                                row_event_info['Signal Data Type'] = category
                                row_event_info.update(row)
                                EXTRACT_DICT[machine_design].append(row_event_info.copy())
                                
                    
                    #fields
                    for field_name, field_info in service_deployment_info.get('field_deployments', {}).items():
                        row_field_info = {}
                        row_field_info['Member Type'] = 'field'
                        row_field_info['Field Name'] = field_name

                        field_details = srv_interface_info.get('FIELDS', {}).get(field_name, {})
                        
                        field_dtype_ref = field_details.get('Member_info', {}).get('text', [])

                        if len(field_dtype_ref) !=2:
                            EXTRACT_DICT[machine_design].append(row_field_info.copy())
                            logger.warning(f'Datatype not found for field -> {field_name} for service {srv_dep_ref}')
                            continue
                        #row_field_info['Signal Data Type'] = '/'.join(field_dtype_ref)

                        dtype_info = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(field_dtype_ref[0],{}).get(field_dtype_ref[1], {})
                        
                        if dtype_info:
                            category = dtype_info.get('category', '')
                            if category == 'TYPE_REFERENCE':
                                type_ref_text = dtype_info.get('text', ('',''))
                                type_ref_temp = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(type_ref_text[0],{}).get(type_ref_text[1], {})
                                if type_ref_temp.get('category', '') not in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                    category = type_ref_temp.get('category', '')
                                    field_dtype_ref = dtype_info.get('text', ('',''))

                            if category in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', field_dtype_ref)
                                row_field_info['Signal Data Type'] = dtype_info.get('signal_dtype', None)
                                row_field_info.update(row)
                                #EXTRACT_DICT[machine_design].append(row_field_info.copy())
                                if field_details.get('HAS-GETTER', '') == 'true':
                                    field_getter_row = row_field_info.copy()
                                    field_getter_row['Field Type'] = 'getter'
                                    field_getter_row['Member ID'] = int(field_info.get('getter_info',{}).get('METHOD-ID'))
                                    field_getter_row['Member'] = field_info.get('getter_info',{}).get('SHORT-NAME', field_name)
                                    EXTRACT_DICT[machine_design].append(field_getter_row)

                                if field_details.get('HAS-SETTER', '') == 'true':
                                    field_setter_row = row_field_info.copy()
                                    field_setter_row['Field Type'] = 'setter'
                                    field_setter_row['Member ID'] = int(field_info.get('setter_info',{}).get('METHOD-ID'))
                                    field_setter_row['Member'] = field_info.get('setter_info',{}).get('SHORT-NAME', field_name)
                                    EXTRACT_DICT[machine_design].append(field_setter_row)

                                if field_details.get('HAS-NOTIFIER', '') == 'true':
                                    field_notifier_row = row_field_info.copy()
                                    field_notifier_row['Field Type'] = 'notifier'
                                    field_notifier_row['Member ID'] = field_info.get('notifier_info',{}).get('EVENT-ID')
                                    field_notifier_row['Event Group'] = field_info.get('notifier_info',{}).get('event_group_name','')
                                    field_notifier_row['Event_GroupId'] = field_info.get('notifier_info',{}).get('event_group_id','')
                                    field_notifier_row['Member'] = field_info.get('notifier_info',{}).get('SHORT-NAME', field_name)
                                    EXTRACT_DICT[machine_design].append(field_notifier_row)     
                            
                            elif category in ['ARRAY', 'VECTOR']:
                                #print(field_dtype_ref)
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', field_dtype_ref)
                                row_field_info["No of Parameters"] = dtype_info.get("array_size", 20)
                                if row_field_info["No of Parameters"] == '':
                                    row_field_info["No of Parameters"] = 20

                                namespace_info = generate_namespace(dtype_info['element_info'])
                                if type(dtype_info['element_info']) is list:
                                    categ = 'STRUCTURE'
                                else:
                                    categ = dtype_info['element_info']['category']
                                
                                if categ in ['ARRAY','VECTOR']:
                                    logger.warning('ARRAY of ARRAY - review')
                                if categ in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                        'parameter_dtype_l3',
                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                    for col in clear_row_values:
                                        row_field_info[col] = ''

                                    row_field_info["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                    row_field_info["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                    row_field_info["Unit"] = dtype_info['element_info'].get('unit', None)
                                    row_field_info['Signal Data Type'] = dtype_info['element_info'].get('signal_dtype', None)
                                    row_field_info.update(row)
                                    #EXTRACT_DICT[machine_design].append(row_field_info.copy())
                                    if field_details.get('HAS-GETTER', '') == 'true':
                                        field_getter_row = row_field_info.copy()
                                        field_getter_row['Field Type'] = 'getter'
                                        field_getter_row['Member ID'] = int(field_info.get('getter_info',{}).get('METHOD-ID'))
                                        field_getter_row['Member'] = field_info.get('getter_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_getter_row)

                                    if field_details.get('HAS-SETTER', '') == 'true':
                                        field_setter_row = row_field_info.copy()
                                        field_setter_row['Field Type'] = 'setter'
                                        field_setter_row['Member ID'] = int(field_info.get('setter_info',{}).get('METHOD-ID'))
                                        field_setter_row['Member'] = field_info.get('setter_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_setter_row)

                                    if field_details.get('HAS-NOTIFIER', '') == 'true':
                                        field_notifier_row = row_field_info.copy()
                                        field_notifier_row['Field Type'] = 'notifier'
                                        field_notifier_row['Member ID'] = field_info.get('notifier_info',{}).get('EVENT-ID')
                                        field_notifier_row['Event Group'] = field_info.get('notifier_info',{}).get('event_group_name','')
                                        field_notifier_row['Event_GroupId'] = field_info.get('notifier_info',{}).get('event_group_id','')
                                        field_notifier_row['Member'] = field_info.get('notifier_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_notifier_row)   
                                else:
                                    for s, nms_info in namespace_info.items():
                                        temp_data = {}
                                        clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                            'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                            'parameter_dtype_l4', 'parameter_dtype_l5']
                                        for col in clear_row_values:
                                            temp_data[col] = ''
                                        namespace = nms_info['namespace']
                                        if '.' in namespace:
                                            temp_split = namespace.split('.')
                                            signal = temp_split[-1]
                                            if '[' in signal:
                                                temp_split2 = signal.split('[')
                                                temp_data['Signal'] = temp_split2[0]
                                                temp_data['No of Elements'] = temp_split2[-1].split(']')[0]

                                            else:
                                                temp_data['Signal'] = signal
                                            temp_data["Minimum"] = nms_info.get('minimum', None)
                                            temp_data["Maximum"] = nms_info.get('maximum', None)
                                            temp_data["Unit"] = nms_info.get('unit', None)
                                            temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                            for i,data_structure in enumerate(temp_split[:-1]):
                                                key = f'parameter_dtype_l{i+1}'
                                                temp_data[key] = data_structure
                                        else:
                                            if '[' in namespace:
                                                temp_split = namespace.split('[')
                                                temp_data['Signal'] = temp_split[0]
                                                temp_data['No of Elements'] = temp_split[-1].split(']')[0]

                                            else:
                                                temp_data['Signal'] = namespace
                                            temp_data["Minimum"] = nms_info.get('minimum', None)
                                            temp_data["Maximum"] = nms_info.get('maximum', None)
                                            temp_data["Unit"] = nms_info.get('unit', None)
                                            temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)
                                        
                                        row_field_info.update(temp_data)
                                        row_field_info.update(row)
                                        #EXTRACT_DICT[machine_design].append(row_field_info.copy())
                                        if field_details.get('HAS-GETTER', '') == 'true':
                                            field_getter_row = row_field_info.copy()
                                            field_getter_row['Field Type'] = 'getter'
                                            field_getter_row['Member ID'] = int(field_info.get('getter_info',{}).get('METHOD-ID'))
                                            field_getter_row['Member'] = field_info.get('getter_info',{}).get('SHORT-NAME', field_name)
                                            EXTRACT_DICT[machine_design].append(field_getter_row)

                                        if field_details.get('HAS-SETTER', '') == 'true':
                                            field_setter_row = row_field_info.copy()
                                            field_setter_row['Field Type'] = 'setter'
                                            field_setter_row['Member ID'] = int(field_info.get('setter_info',{}).get('METHOD-ID'))
                                            field_setter_row['Member'] = field_info.get('setter_info',{}).get('SHORT-NAME', field_name)
                                            EXTRACT_DICT[machine_design].append(field_setter_row)

                                        if field_details.get('HAS-NOTIFIER', '') == 'true':
                                            field_notifier_row = row_field_info.copy()
                                            field_notifier_row['Field Type'] = 'notifier'
                                            field_notifier_row['Member ID'] = field_info.get('notifier_info',{}).get('EVENT-ID')
                                            field_notifier_row['Event Group'] = field_info.get('notifier_info',{}).get('event_group_name','')
                                            field_notifier_row['Event_GroupId'] = field_info.get('notifier_info',{}).get('event_group_id','')
                                            field_notifier_row['Member'] = field_info.get('notifier_info',{}).get('SHORT-NAME', field_name)
                                            EXTRACT_DICT[machine_design].append(field_notifier_row)   
                            
                            elif category in ['STRUCTURE', 'VARIANT']:
                                dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', field_dtype_ref)
                                namespace_info = generate_namespace(dtype_info)
                                for s, nms_info in namespace_info.items():
                                    temp_data = {}
                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                        'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                    for col in clear_row_values:
                                        temp_data[col] = ''
                                    namespace = nms_info['namespace']
                                    if '.' in namespace:
                                        temp_split = namespace.split('.')
                                        signal = temp_split[-1]
                                        #check if array
                                        if '[' in signal:
                                            temp_split2 = signal.split('[')
                                            temp_data['Signal'] = temp_split2[0]
                                            temp_data['No of Elements'] = temp_split2[-1].split(']')[0]

                                        else:
                                            temp_data['Signal'] = signal
                                        temp_data["Minimum"] = nms_info.get('minimum', None)
                                        temp_data["Maximum"] = nms_info.get('maximum', None)
                                        temp_data["Unit"] = nms_info.get('unit', None)
                                        temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                        for i,data_structure in enumerate(temp_split[:-1]):
                                            key = f'parameter_dtype_l{i+1}'
                                            temp_data[key] = data_structure
                                    else:
                                        #check if array
                                        if '[' in namespace:
                                            temp_split = namespace.split('[')
                                            temp_data['Signal'] = temp_split[0]
                                            temp_data['No of Elements'] = temp_split[-1].split(']')[0]

                                        else:
                                            temp_data['Signal'] = namespace
                                        temp_data["Minimum"] = nms_info.get('minimum', None)
                                        temp_data["Maximum"] = nms_info.get('maximum', None)
                                        temp_data["Unit"] = nms_info.get('unit', None)
                                        temp_data["Signal Data Type"] = nms_info.get('signal_dtype', None)
                                    
                                    row_field_info.update(temp_data)
                                    row_field_info.update(row)
                                    #EXTRACT_DICT[machine_design].append(row_field_info.copy())
                                    if field_details.get('HAS-GETTER', '') == 'true':
                                        field_getter_row = row_field_info.copy()
                                        field_getter_row['Field Type'] = 'getter'
                                        field_getter_row['Member ID'] = int(field_info.get('getter_info',{}).get('METHOD-ID'))
                                        field_getter_row['Member'] = field_info.get('getter_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_getter_row)

                                    if field_details.get('HAS-SETTER', '') == 'true':
                                        field_setter_row = row_field_info.copy()
                                        field_setter_row['Field Type'] = 'setter'
                                        field_setter_row['Member ID'] = int(field_info.get('setter_info',{}).get('METHOD-ID'))
                                        field_setter_row['Member'] = field_info.get('setter_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_setter_row)

                                    if field_details.get('HAS-NOTIFIER', '') == 'true':
                                        field_notifier_row = row_field_info.copy()
                                        field_notifier_row['Field Type'] = 'notifier'
                                        field_notifier_row['Member ID'] = field_info.get('notifier_info',{}).get('EVENT-ID')
                                        field_notifier_row['Event Group'] = field_info.get('notifier_info',{}).get('event_group_name','')
                                        field_notifier_row['Event_GroupId'] = field_info.get('notifier_info',{}).get('event_group_id','')
                                        field_notifier_row['Member'] = field_info.get('notifier_info',{}).get('SHORT-NAME', field_name)
                                        EXTRACT_DICT[machine_design].append(field_notifier_row)   
                                
                                    
                            else:
                                row_field_info['Signal Data Type'] = category
                                row_field_info.update(row)
                                logger.warning(f'{dtype_info}- review')
                        

                    #methods
                    for method_name, method_info in service_deployment_info.get('methods_deployments', {}).items():
                        row_method_info = {}
                        row_method_info['Member Type'] = 'method'
                        row_method_info['Member'] = method_name
                        row_method_info['Member ID'] = method_info.get('METHOD-ID', '')
                        method_details = srv_interface_info.get('METHODS', {})

                        row_method_info['Fire_and_forget'] = method_details.get(method_name, {}).get('fire_and_forget', '').lower()
                        #row_method_info.update(row)
                        for arguments_dict in method_details.get(method_name, {}).get('arguements', []):
                            #print(arguments_dict)
                            arguement_info = {}
                            arguement_info['Parameter'] = arguments_dict.get('arg_name', '')
                            arguement_info['Parameter Type'] = arguments_dict.get('direction', '')
                            
                            parameter_dtype_ref = arguments_dict.get('arg_info', {}).get('text',[])

                            if len(parameter_dtype_ref) != 2:
                                EXTRACT_DICT[machine_design].append(arguement_info.copy())
                                logger.warning(f'Datatype not found for method -> {method_name} for service {srv_dep_ref}')
                                continue
                            #arguement_info['Signal Data Type'] = '/'.join(parameter_dtype_ref)

                            dtype_info = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(parameter_dtype_ref[0],{}).get(parameter_dtype_ref[1], {})

                        
                            if dtype_info:
                                category = dtype_info.get('category', '')
                                if category == 'TYPE_REFERENCE':
                                    type_ref_text = dtype_info.get('text', ('', ''))
                                    type_ref_temp = DATATYPES_DICT['STD-CPP-IMPLEMENTATION-DATA-TYPE'].get(type_ref_text[0], {}).get(type_ref_text[1], {})
                                    if type_ref_temp.get('category', '') not in ['VALUE', 'TYPE_REFERENCE', 'STRING']:
                                        category = type_ref_temp.get('category', '')
                                        parameter_dtype_ref = dtype_info.get('text', ('', ''))
                                if category in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                    dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE',parameter_dtype_ref)
                                    arguement_info["Signal Data Type"] = dtype_info.get('signal_dtype', None)

                                    #arguement_info['Signal'] = field_name
                                    row_method_info.update(arguement_info)
                                    
                                    row_method_info.update(row)
                                    EXTRACT_DICT[machine_design].append(row_method_info.copy())

                                elif category in ['ARRAY', 'VECTOR']:
                                    #print(parameter_dtype_ref)
                                    dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', parameter_dtype_ref)
                                    arguement_info["No of Parameters"] = dtype_info.get("array_size", '')

                                    namespace_info = generate_namespace(dtype_info['element_info'])
                                    if type(dtype_info['element_info']) is list:
                                        categ = 'STRUCTURE'
                                    else:
                                        categ = dtype_info['element_info']['category']

                                    if categ in ['ARRAY','VECTOR']:
                                        logger.warning('ARRAY of ARRAY - review')
                                    if categ in ['VALUE','TYPE_REFERENCE', 'STRING']:
                                        clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                            'parameter_dtype_l1', 'parameter_dtype_l2',
                                                            'parameter_dtype_l3',
                                                            'parameter_dtype_l4', 'parameter_dtype_l5']
                                        for col in clear_row_values:
                                            arguement_info[col] = ''

                                        arguement_info["Minimum"] = dtype_info['element_info'].get('Minimum', None)
                                        arguement_info["Maximum"] = dtype_info['element_info'].get('Maximum', None)
                                        arguement_info["Unit"] = dtype_info['element_info'].get('unit', None)
                                        arguement_info["Signal Data Type"] = dtype_info['element_info'].get('signal_dtype', None)
                                        row_method_info.update(arguement_info)
                                        row_method_info.update(row)
                                        EXTRACT_DICT[machine_design].append(row_method_info.copy())
                                    else:
                                        for s, nms_info in namespace_info.items():
                                            clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                                'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                                'parameter_dtype_l4', 'parameter_dtype_l5']
                                            for col in clear_row_values:
                                                arguement_info[col] = ''
                                            namespace = nms_info['namespace']
                                            if '.' in namespace:
                                                temp_split = namespace.split('.')
                                                signal = temp_split[-1]
                                                if '[' in signal:
                                                    temp_split2 = signal.split('[')
                                                    arguement_info['Signal'] = temp_split2[0]
                                                    arguement_info['No of Elements'] = temp_split2[-1].split(']')[0]

                                                else:
                                                    arguement_info['Signal'] = signal
                                                arguement_info["Minimum"] = nms_info.get('minimum', None)
                                                arguement_info["Maximum"] = nms_info.get('maximum', None)
                                                arguement_info["Unit"] = nms_info.get('unit', None)
                                                arguement_info["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                                for i,data_structure in enumerate(temp_split[:-1]):
                                                    key = f'parameter_dtype_l{i+1}'
                                                    arguement_info[key] = data_structure
                                            else:
                                                if '[' in namespace:
                                                    temp_split = namespace.split('[')
                                                    arguement_info['Signal'] = temp_split[0]
                                                    arguement_info['No of Elements'] = temp_split[-1].split(']')[0]

                                                else:
                                                    arguement_info['Signal'] = namespace
                                                arguement_info["Minimum"] = nms_info.get('minimum', None)
                                                arguement_info["Maximum"] = nms_info.get('maximum', None)
                                                arguement_info["Unit"] = nms_info.get('unit', None)
                                                arguement_info["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                            row_method_info.update(arguement_info)
                                            row_method_info.update(row)
                                            EXTRACT_DICT[machine_design].append(row_method_info.copy())

                                elif category in ['STRUCTURE', 'VARIANT']:
                                    dtype_info = find_data_structure('STD-CPP-IMPLEMENTATION-DATA-TYPE', parameter_dtype_ref)
                                    namespace_info = generate_namespace(dtype_info)
                                    for s, nms_info in namespace_info.items():
                                        clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                            'parameter_dtype_l1', 'parameter_dtype_l2', 'parameter_dtype_l3',
                                                            'parameter_dtype_l4', 'parameter_dtype_l5']
                                        for col in clear_row_values:
                                            arguement_info[col] = ''
                                        namespace = nms_info['namespace']
                                        if '.' in namespace:
                                            temp_split = namespace.split('.')
                                            signal = temp_split[-1]
                                            #check if array
                                            if '[' in signal:
                                                temp_split2 = signal.split('[')
                                                arguement_info['Signal'] = temp_split2[0]
                                                arguement_info['No of Elements'] = temp_split2[-1].split(']')[0]

                                            else:
                                                arguement_info['Signal'] = signal
                                            arguement_info["Minimum"] = nms_info.get('minimum', None)
                                            arguement_info["Maximum"] = nms_info.get('maximum', None)
                                            arguement_info["Unit"] = nms_info.get('unit', None)
                                            arguement_info["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                            for i,data_structure in enumerate(temp_split[:-1]):
                                                key = f'parameter_dtype_l{i+1}'
                                                arguement_info[key] = data_structure
                                        else:
                                            #check if array
                                            if '[' in namespace:
                                                temp_split = namespace.split('[')
                                                arguement_info['Signal'] = temp_split[0]
                                                arguement_info['No of Elements'] = temp_split[-1].split(']')[0]

                                            else:
                                                arguement_info['Signal'] = namespace
                                            arguement_info["Minimum"] = nms_info.get('minimum', None)
                                            arguement_info["Maximum"] = nms_info.get('maximum', None)
                                            arguement_info["Unit"] = nms_info.get('unit', None)
                                            arguement_info["Signal Data Type"] = nms_info.get('signal_dtype', None)

                                        row_method_info.update(arguement_info)
                                        row_method_info.update(row)
                                        EXTRACT_DICT[machine_design].append(row_method_info.copy())


                                else:
                                    logger.warning(f'{dtype_info}- review')
                                    #print(method_name)
                                    row_method_info["Signal Data Type"] = category
                                    clear_row_values = ['Signal', 'No of Elements', 'Minimum', 'Maximum', 'Unit',
                                                        'parameter_dtype_l1', 'parameter_dtype_l2',
                                                        'parameter_dtype_l3',
                                                        'parameter_dtype_l4', 'parameter_dtype_l5']
                                    for col in clear_row_values:
                                        arguement_info[col] = ''
                                    row_method_info.update(arguement_info)
                                    row_method_info.update(row)
                                    EXTRACT_DICT[machine_design].append(row_method_info.copy())


    #                         arguement_info.update(row)
    #                         EXTRACT_DICT[machine_design].append(arguement_info.copy())

    return EXTRACT_DICT
                    
                    
                    
                    
                    
