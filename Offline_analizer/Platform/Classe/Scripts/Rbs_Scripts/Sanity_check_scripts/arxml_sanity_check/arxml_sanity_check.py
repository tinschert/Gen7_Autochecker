import os
import xmlschema
from lxml import etree
import xml.etree.ElementTree as ET
from json import dumps as json_dumps
import sys
import time
import win32com.client as win32
import argparse

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.getcwd() + r"\..\..\..\Control")
    from logging_config import logger

ns = "{http://autosar.org/schema/r4.0}"

class AdaptiveArxmlValidator:
    def __init__(self, schema=None, expected_schema_version=None):
        self.schema = schema
        self.expected_schema_version = expected_schema_version

    @staticmethod
    def get_element_path_by_reference(element, target_attribute, target_elem, current_path=""):
        """
        Recursively constructs the path using SHORT-NAME for each element
        """
        element_short_name = element.find('ns:SHORT-NAME', namespaces={'ns': 'http://autosar.org/schema/r4.0'})
        if element_short_name is not None:
            current_path = f"{current_path}/{element_short_name.text}" if current_path else element_short_name.text

        if element.tag.endswith(target_attribute) and target_elem == element:
            return current_path

        for child in element:
            result = AdaptiveArxmlValidator.get_element_path_by_reference(child, target_attribute, target_elem, current_path)
            if result:
                return result

        return None

    def get_schema_version(self, arxml_file):
        """Get the schema version from the ARXML file.

        Args:
            arxml_file (str): Path to the ARXML file.

        Returns:
            str,str: Schema version if successful, error message if not.
        """
        try:
            tree = etree.parse(arxml_file)
            root = tree.getroot()
            schema_location = root.attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation', '')
            schema_version = schema_location.split()[-1]
            return schema_version, None
        except etree.XMLSyntaxError as e:
            return None, f"Syntax error in {arxml_file}: {e}"
        except Exception as e:
            return None, f"Error reading schema version from {arxml_file}: {e}"

    def validate_arxml_schema(self, arxml_file):
        """Validate the ARXML file against the schema.

        Args:
            arxml_file (str): Path to the ARXML file.

        Returns:
            tuple: (bool, str) True if the ARXML file is valid, False otherwise, and the error message if any.
        """
        try:
            is_valid = self.schema.is_valid(arxml_file)
            if is_valid:
                return True, None
            else:
                error_message_dict = {}
                error_list = self.schema.iter_errors(arxml_file)
                for err in error_list:
                    error_path = err.path
                    reason = err.reason
                    if "doesn't match any pattern" in reason:
                        if "Doesn't match pattern as per schema" not in error_message_dict:
                            error_message_dict["Doesn't match pattern as per schema"] = []
                        error_message_dict["Doesn't match pattern as per schema"].append(error_path)
                    else:
                        if "Others" not in error_message_dict:
                            error_message_dict["Others"] = []
                        error_message_dict["Others"].append(f"{reason} :: {error_path}")
                

                return False, error_message_dict
        except xmlschema.XMLSchemaException as e:
            return False, f"Schema validation error: {e}"
        except etree.XMLSyntaxError as e:
            return False, f"Syntax error: {e}"

    def validate_event_groups_instances(self, evg_deployment_dict, evg_instances_dict):
        result_dict = {}
        for service_deployment, evg_deployments in evg_deployment_dict.items():
            evg_instances = evg_instances_dict.get(service_deployment, {})
            if not evg_instances:
                result_dict[service_deployment] = [f"Service {service_deployment} does not have any instance defined."]
            else:
                for evg_deployment in evg_deployments:
                    missing_instances = [instance for instance, evg_instance in evg_instances.items() if evg_deployment not in evg_instance]
                    for instance in missing_instances:
                        if service_deployment not in result_dict:
                            result_dict[service_deployment] = []
                        result_dict[service_deployment].append(f"Instance {instance} does not have {evg_deployment} event group defined for service {service_deployment}.")
        return result_dict

    def get_event_group_deployments(self, arxml_root):
        """
        Retrieves the event group deployments from the given ARXML root.

        Args:
            arxml_root (Element): The root element of the ARXML document.

        Returns:
            dict: A dictionary containing the event group deployments. The keys are the complete paths of the service interface deployments,
                  and the values are lists of complete names of the event groups.
        """
        service_interface_deployments = arxml_root.findall(f'.//{ns}SOMEIP-SERVICE-INTERFACE-DEPLOYMENT')
        if service_interface_deployments is None:
            return {}

        evg_deployment_dict = {}
        for service_interface_deployment in service_interface_deployments:
            complete_path = r'/' + self.get_element_path_by_reference(arxml_root, 'SOMEIP-SERVICE-INTERFACE-DEPLOYMENT', service_interface_deployment)
            evg_deployment_dict.setdefault(complete_path, [])
            evg_deployments = service_interface_deployment.findall(f'.//{ns}SOMEIP-EVENT-GROUP')
            for evnt_grp in evg_deployments:
                evg_complete_name = r'/' + self.get_element_path_by_reference(arxml_root, 'SOMEIP-EVENT-GROUP', evnt_grp)
                evg_deployment_dict[complete_path].append(evg_complete_name)
        return evg_deployment_dict

    def get_event_groups_instances(self, arxml_root):
        provided_service_instances = arxml_root.findall(f'.//{ns}PROVIDED-SOMEIP-SERVICE-INSTANCE')
        required_service_instances = arxml_root.findall(f'.//{ns}REQUIRED-SOMEIP-SERVICE-INSTANCE')

        if provided_service_instances is None and required_service_instances is None:
            return {}

        evg_instances_dict = {}
        if provided_service_instances is not None:
            for provided_service_instance in provided_service_instances:
                complete_path = self.get_element_path_by_reference(arxml_root, 'PROVIDED-SOMEIP-SERVICE-INSTANCE', provided_service_instance)
                deployment_ref = provided_service_instance.find(f'.//{ns}SERVICE-INTERFACE-DEPLOYMENT-REF')
                if deployment_ref is not None:
                    deployment_ref = deployment_ref.text
                    evg_instances_dict.setdefault(deployment_ref, {})
                    evg_instances_dict[deployment_ref].setdefault(complete_path, [])
                    provided_evg_groups = provided_service_instance.findall(f'.//{ns}SOMEIP-PROVIDED-EVENT-GROUP')
                    if provided_evg_groups is not None:
                        for evg in provided_evg_groups:
                            event_ref = evg.find(f'.//{ns}EVENT-GROUP-REF')
                            if event_ref is not None:
                                evg_instances_dict[deployment_ref][complete_path].append(event_ref.text)

        if required_service_instances is not None:
            for required_service_instance in required_service_instances:
                complete_path = self.get_element_path_by_reference(arxml_root, 'REQUIRED-SOMEIP-SERVICE-INSTANCE', required_service_instance)
                deployment_ref = required_service_instance.find(f'.//{ns}SERVICE-INTERFACE-DEPLOYMENT-REF')
                if deployment_ref is not None:
                    deployment_ref = deployment_ref.text
                    evg_instances_dict.setdefault(deployment_ref, {})
                    evg_instances_dict[deployment_ref].setdefault(complete_path, [])
                    required_evg_groups = required_service_instance.findall(f'.//{ns}SOMEIP-REQUIRED-EVENT-GROUP')
                    if required_evg_groups is not None:
                        for evg in required_evg_groups:
                            event_ref = evg.find(f'.//{ns}EVENT-GROUP-REF')
                            if event_ref is not None:
                                evg_instances_dict[deployment_ref][complete_path].append(event_ref.text)
        return evg_instances_dict



def getCanoeWarnings(arxml_files, canoe_can_cluster_arxmls, canoe_eth_cluster_arxmls):
    """
    Get warnings from CANoe for the provided ARXML files.

    Parameters:
    arxml_files (list): List of ARXML file paths to check.
    canoe_can_cluster_arxmls (list): List of ARXML files for CAN cluster.
    canoe_eth_cluster_arxmls (list): List of ARXML files for Ethernet cluster.

    Returns:
    dict: Dictionary with file names as keys and warnings as values.
    """
    if arxml_files == [] or (canoe_can_cluster_arxmls == [] and canoe_eth_cluster_arxmls == []):
        return {}

    warnings_dict = {}
    version = ''

    try:
        logger.info("Starting CANoe application...")
        
        CANoe = win32.Dispatch("CANoe.Application")
        CANoe.Visible = False
        time.sleep(3)
        version = CANoe.Version.FullName
        logger.info(f"Loaded CANoe version --> {version}")
        buses = CANoe.Configuration.SimulationSetup.Buses

        can_network = buses.AddWithType("CAN_DB_TEST", 1)
        eth_network = buses.AddWithType("ETHERNET_DB_TEST", 11)

        for arxml_file in arxml_files:
            file_name = os.path.basename(arxml_file)
            logger.info(f'Getting write window warnings for {file_name}')
            if file_name not in warnings_dict:
                warnings_dict[file_name] = {}
            if file_name in canoe_can_cluster_arxmls:
                warnings_dict[file_name]['CAN'] = []
                CANoe.UI.Write.Clear()
                try:
                    can_network.Databases.Add(arxml_file)
                    time.sleep(1)
                    warnings = CANoe.UI.Write.Text
                    if warnings:
                        warnings = warnings.split('\n')
                        warnings = [i.replace('\r\r','').replace('[W]\t[System]\t','') for i in warnings if '[W]\t[System]\t\r\r' not in i or 'Due to having an incomplete database a simulated peer node has been generated' not in i]
                        warnings_dict[file_name]['CAN'] = warnings

                    can_network.Databases.Remove(1)
                except:
                    pass

                CANoe.UI.Write.Clear()
            if file_name in canoe_eth_cluster_arxmls:
                warnings_dict[file_name]['ETH'] = []
                CANoe.UI.Write.Clear()
                try:
                    eth_network.Databases.Add(arxml_file)
                    time.sleep(1)
                    warnings = CANoe.UI.Write.Text
                    if warnings:
                        warnings = warnings.split('\n')
                        warnings = [i.replace('\r\r','').replace('[W]\t[System]\t','') for i in warnings if '[W]\t[System]\t\r\r' not in i]
                        warnings_dict[file_name]['ETH'] = warnings

                    eth_network.Databases.Remove(1)
                except:
                    pass
                CANoe.UI.Write.Clear()

        logger.info("Finished getting write window warnings")
        
        try:
            CANoe.Configuration.Modified = False
            logger.info("Discarding configuration changes")
            CANoe.Application.Quit()
            logger.info("CanOE application quit")
        except Exception as e:
            logger.warning(f"Control script was unable to quit CanOE app due to {e}")
            return warnings_dict,version

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        try:
            CANoe.Configuration.Modified = False
            logger.info("Discarding configuration changes")
            CANoe.Application.Quit()
            logger.info("CanOE application quit")
        except Exception as e:
            logger.warning(f"Control script was unable to quit CanOE app due to {e}")
            return warnings_dict,version
        return warnings_dict,version

    return warnings_dict,version



def main(folder_input, get_canoe_warnings=False, is_jenkins=False):
    schema_folder = r'\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Restbus\ARXML_Schemas'
    loaded_schemas = {}
    arxml_files = []
    arxml_report_dict = {}
    evg_deployments_dict = {}
    evg_instances_dict = {}
    canoe_eth_cluster_arxmls = []
    canoe_can_cluster_arxmls = []

    if isinstance(folder_input, str) and os.path.isdir(folder_input):
        # If folder_input is a directory
        for root, dirs, files in os.walk(folder_input):
            for file in files:
                if file.endswith(".arxml"):
                    arxml_files.append(os.path.join(root, file))
    elif isinstance(folder_input, list):
        # If folder_input is a list of files
        for file in folder_input:
            if file.endswith(".arxml"):
                arxml_files.append(file)
    else:
        raise ValueError("Invalid input: folder_input should be a directory path or a list of .arxml files")

    for arxml_file in arxml_files:
        file_name = os.path.basename(arxml_file)
        logger.info(f'Analyzing {file_name}...')

        validator = AdaptiveArxmlValidator()
        schema_version, error_message = validator.get_schema_version(arxml_file)
        if schema_version is None:
            arxml_report_dict.setdefault(file_name, []).append(error_message.replace(folder_input, ''))
            continue

        if schema_version not in loaded_schemas:
            schema_file = os.path.join(schema_folder, schema_version)
            if not os.path.exists(schema_file):
                error_message = f"Schema file {schema_file} not found."
                arxml_report_dict.setdefault(file_name, []).append(error_message)
                continue
            loaded_schemas[schema_version] = xmlschema.XMLSchema(schema_file)
            logger.info(f"Loaded schema version {schema_version}")

        

        schema = loaded_schemas[schema_version]
        validator = AdaptiveArxmlValidator(schema, schema_version)

        #--------------VAlidate ARXML Schema----------------
        logger.info(f"Validating {file_name} against schema version {schema_version}...")
        is_valid, error_message = validator.validate_arxml_schema(arxml_file)
        if not is_valid:
            arxml_report_dict.setdefault(file_name, []).append(error_message)

        
        #--------------Get Event Group Deployments and Instances----------------
        arxml_root = ET.parse(arxml_file).getroot()
        evg_deployments_dict.update(validator.get_event_group_deployments(arxml_root))
        evg_instances_dict.update(validator.get_event_groups_instances(arxml_root))

        #-------------- Know if arxmls has can cluster or eth cluster or both
        if get_canoe_warnings:
            can_cluster = arxml_root.findall(f'.//{ns}CAN-CLUSTER')
            eth_cluster = arxml_root.findall(f'.//{ns}ETHERNET-CLUSTER')
            if can_cluster:
                logger.info(f"{file_name} has CAN cluster")
                canoe_can_cluster_arxmls.append(file_name)
            if eth_cluster:
                logger.info(f"{file_name} has ETHERNET cluster")
                canoe_eth_cluster_arxmls.append(file_name)

    
    #--------------Validate Event Group Instances----------------
    evg_validation_errors = validator.validate_event_groups_instances(evg_deployments_dict, evg_instances_dict)

    #--------------Get Canoe write window warnings-----------------------------
    canoe_warnings_dict = {}
    canoe_version = ''
    if get_canoe_warnings and len(arxml_files)<10:
        canoe_warnings_dict, canoe_version = getCanoeWarnings(arxml_files, canoe_can_cluster_arxmls, canoe_eth_cluster_arxmls)
        #print(canoe_warnings_dict)

    if isinstance(folder_input, str) and folder_input.endswith('Database\\DBC'):
        for arxml_file in arxml_files:
            file_name = os.path.basename(arxml_file)
            error_log_file = f"{file_name}_arxml_error_log.txt"
            with open(error_log_file, 'w') as file:
                file.write('')
                if file_name in arxml_report_dict:
                    file.write("ARXML Schema Errors:----------------------------------------------------------------\n")
                    file.write(json_dumps(arxml_report_dict[file_name], indent=4))
                if evg_validation_errors:
                    file.write("\n\n\n\n\nEvent Group Validation Errors:----------------------------------------------------------------\n")
                    file.write(json_dumps(evg_validation_errors, indent=4))
                if canoe_warnings_dict.get(file_name, None):
                    file.write("\n\n\n\n\nCANoe Write Window Warnings----------------------------------------------------------------\n")
                    file.write(f"VERSION:  {canoe_version}\n\n")
                    file.write(json_dumps(canoe_warnings_dict.get(file_name, {}), indent=4))
            if not(is_jenkins) and (arxml_report_dict or evg_validation_errors or canoe_warnings_dict.get(file_name, None)):
                os.startfile(error_log_file)
    else:
        with open("arxml_error_log.txt", 'w') as file:
            file.write('')
            if arxml_report_dict:
                file.write("ARXML Schema Errors:\n")
                file.write(json_dumps(arxml_report_dict, indent=4))
            if evg_validation_errors:
                file.write("\n\n\nEvent Group Validation Errors:\n")
                file.write(json_dumps(evg_validation_errors, indent=4))
            if canoe_warnings_dict:
                file.write("\n\n\n\n\nCANoe Write Window Warnings----------------------------------------------------------------\n")
                file.write(f"VERSION:  {canoe_version}\n\n")
                file.write(json_dumps(canoe_warnings_dict, indent=4))
            if not(is_jenkins) and (arxml_report_dict or evg_validation_errors or canoe_warnings_dict):
                os.startfile("arxml_error_log.txt")

    summarized_dict = {}

    if arxml_report_dict:
        if 'Schema Warnings:' not in summarized_dict:
            summarized_dict['Schema Warnings:'] = []
        summarized_dict['Schema Warnings:'] = list(set(list(arxml_report_dict.keys())))
    if canoe_warnings_dict:
        if 'Canoe Warnings:' not in summarized_dict:
            summarized_dict['Canoe Warnings:'] = []
        for f_nme in canoe_warnings_dict.keys():
            for k, v in canoe_warnings_dict[f_nme].items():
                if v:
                    if f_nme not in summarized_dict['Canoe Warnings:']:
                        summarized_dict['Canoe Warnings:'].append(f_nme)

    if evg_validation_errors:
        summarized_dict['Others:'] = ['Event group validation warnings']

    if summarized_dict:
        summary_file_name = 'summary_arxml_error_log.txt'
        with open(summary_file_name, 'w') as file:
            file.write(r'--------------------------------SUMMARY--------------------------------------\n\n')
            for headi, value_list in summarized_dict.items():
                file.write(headi)
                file.write('\n')
                if value_list:
                    for v in value_list:
                        file.write('\t-'+str(v)+'\n')
                file.write('\n\n')

    logger.info("Validation completed. Please check error_log.txt for details.")


if __name__ == "__main__":
    #pass
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='ARXML Sanity Check')
    commandLineParser.add_argument('--folder_path', action="store", dest="folder_path", required=True, help="Folder container where arxmls are stored")

    commandLineParser.add_argument('--is_jenkins', action="store", dest="is_jenkins", required=True, default="yes", help="if script is triggered from jenkins or not yes/no")
    commandLineParser.add_argument('--get_canoe_warnings', action="store", dest="get_canoe_warnings", required=False,
                                   default="yes", help="If True canoe write_window warnings will be extracted. yes/no")
    arguments = commandLineParser.parse_args()

    folder_input = arguments.folder_path
    is_jenkins = arguments.is_jenkins
    get_canoe_warnings = arguments.get_canoe_warnings
    is_jenkins = True if is_jenkins=='yes' else False
    get_canoe_warnings = True if get_canoe_warnings=='yes' else False

    main(folder_input, get_canoe_warnings, is_jenkins)
    