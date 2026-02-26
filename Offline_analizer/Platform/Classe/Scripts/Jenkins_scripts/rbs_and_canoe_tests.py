# -*- coding: utf-8 -*-
# @file rbs_and_canoe_tests.py
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


import argparse
import os,sys
import xml.etree.ElementTree as ET
import openpyxl

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\KPI_scripts")
from rbs_kpi import getAutosarData, parseTrace, merge_sheets_into_single_sheet, merge_excel_files_into_sheets

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\FVideo_KPIs")
from fvideo_kpi import runFvideoKPI, get_scenario_target_type


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import datetime
import shutil
import subprocess
import pythoncom
import time
from pathlib import Path
import canoe_client_1
from json import loads


def execute_update_sysvartab(script_path):
    """
    runs update_sysvartab script

    Args:
      script_path (str): path to the  update_sysvartab.py script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    logger.info(f"Run RBS Scripts from {scripts_abs_path}")
    sys.path.append(scripts_abs_path)
    import update_sysvartab
    update_sysvartab.external_call()


def execute_create_nodes(script_path):
    """
    runs create_nodes script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_nodes
    create_nodes.external_call()


def execute_create_sysvar(script_path):
    """
    runs create_sysvar script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_sysvar
    create_sysvar.external_call()


def execute_create_ininode(script_path):
    """
    runs create_ininode script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_ininode
    create_ininode.external_call()


def execute_create_gw(script_path):
    """
    runs create_gw script

    Args:
      script_path: path to the script

    Returns:

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_gw
    create_gw.external_call()


def execute_update_fdx_nodes(script_path):
    """
    runs update_fdx_nodes script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\FDX_Scripts"
    sys.path.append(scripts_abs_path)
    import fdx_to_rbs_mapping
    fdx_to_rbs_mapping.external_call()

def execute_update_fdx_database(script_path):
    """
    runs update_fdx_database script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\FDX_Scripts"
    sys.path.append(scripts_abs_path)
    import fdx_database_gen
    fdx_database_gen.external_call()

# def excecute_update_cm_nodes(script_path):
#     scripts_abs_path = script_path + r"\Platform\Classe\Scripts\CarMaker_scripts"
#     sys.path.append(scripts_abs_path)
#     import cm_to_rbs_mapping
#     cm_to_rbs_mapping.external_call()

def execute_autosar(script_path):
    """
    runs create_autosar script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_autosar
    create_autosar.external_call()

def execute_create_arxml(script_path):
    """
    runs create_arxml_v2 script

    Args:
      script_path (str): path to the script

    """
    scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
    sys.path.append(scripts_abs_path)
    import create_arxml_v5
    create_arxml_v5.external_call()

def copyReport(source_report_path, dest_report_path, cfg_file):
    """
    copies test report to the given path

    Args:
      source_report_path (str): path to the source report
      dest_report_path (str): destination report path
      cfg_file (str): canoe cfg file name

    """
    logger.info("Start copying Test Reports")
    try:
        if "_FORD" in str(cfg_file).upper():
            report_file_extension = ".html"
        else:
            report_file_extension = ".vtestreport"

        folder_name = datetime.date.today().strftime("%m-%d-%Y")
        dest_folder_path = os.path.join(dest_report_path, folder_name)
        if os.path.exists(dest_folder_path):
            shutil.rmtree(dest_folder_path)
        os.mkdir(dest_folder_path)
        for filename in os.listdir(source_report_path):
            if filename.endswith(report_file_extension):
                file_path = os.path.join(source_report_path, filename)
                shutil.copy(file_path, dest_folder_path)
                logger.info(f"Copied {filename} to -> {dest_folder_path}")
    except Exception as e:
        raise Exception(f"Failed while copying test report -> {e}")
    
def convert_BLF_to_MF4(canoeClient, src_folder, dest_folder):
    """
    converts log file format from blf to mf4

    Args:
      canoeClient (object): canoeClient instance
      src_folder (str): folder path where source log files are present
      dest_folder (str): destination folder path

    Returns:
        list: returns list of converted file paths
    """
    try:
        converted_files = []
        os.mkdir(dest_folder)
        for (dirpath, dirnames, filenames) in os.walk(src_folder):
            for file in filenames:
                if ".blf" in file.lower():
                    source_file = src_folder+r"\\"+file
                    destination_file = dest_folder+r"\\"+file.replace(".blf",".mf4")
                    converted = canoeClient.convert_logged_file(destination_file=destination_file, source_file=source_file)
                    converted_files.append(destination_file)
        return converted_files
    except Exception as e:
        logger.error(f"ERROR while converting blf to mf4 -> {e}")

def get_testcase_info(path_platform, customer):
    try:
        logger.info("########################## START TEST CASE INFO EXTRACT #############################")
        if customer == "FORD":
            path_platform = path_platform + r"\\CustomerPrj\\Testcases"
        else:
            path_platform = path_platform + r"\\Platform\\Testcases"
        tc_log_file_path = path_platform + r'\tc_log.txt'
        logfile = open(tc_log_file_path, 'w')
        xml_files = []
        test_case_info = dict()
        for file in os.listdir(path_platform):
            # Construct the full file path
            file_path = os.path.join(path_platform, file)
            # Check if it is a file and has the .vtestreport extension
            if os.path.isfile(file_path) and file.endswith('.xml'):
                xml_files.append(file_path)
        for f_path in xml_files:
            if "_report" in f_path:
                key = f_path.split('\\')[-1].replace('.xml','').replace('_report','').replace('Report_','')
                failed = []
                passed = []
                # Parse the XML file
                tree = ET.parse(f_path)
                root = tree.getroot()

                # Find all <testcase> elements
                testcases = root.findall('.//testcase')
                for testcase in testcases:
                    verdict = testcase.find('verdict')
                    if verdict is not None:
                        verdict_result = verdict.get('result')
                    if verdict_result == "fail":
                        test_case_name = testcase.find('title')
                        failed.append(test_case_name.text)
                    elif verdict_result == "pass":
                        test_case_name = testcase.find('title')
                        passed.append(test_case_name.text)
                logfile.write(f"In TestModule : {key}: \n")
                if len(passed) >= 1:
                    logfile.write("_________________________________PASSED_TSETCASES_________________________________\n")
                    for passed_tc in passed:
                        logfile.write(f"[PASSED] : {key} : {passed_tc} \n")
                if len(failed) >= 1:
                    logfile.write("_________________________________FAILED_TSETCASES_________________________________\n")
                    for failed_tc in failed:
                        logfile.write(f"[FAILED] : {key} : {failed_tc} \n")
                logfile.write("__________________________________________________________________________________\n")  
                test_case_info.update({key: {"passed": passed, "failed": failed}})
        logger.info("########################## END TEST CASE INFO EXTRACT #############################")
    except Exception as e:
        logger.error(f"error in fetching test case info --> {e}")
    return test_case_info

def get_mf4_log_file_paths(directory_path):
    mf4_files = []
    # List files in the top-level directory only
    for file in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file)
        # Check if it's a file and ends with .mf4
        if os.path.isfile(full_path) and file.endswith(".mf4"):
            mf4_files.append(full_path)
    return mf4_files

def move_mf4_files(source_dir, dest_dir):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for file in os.listdir(source_dir):
        source_path = os.path.join(source_dir, file)
        if os.path.isfile(source_path) and file.endswith(".mf4"):
            destination_path = os.path.join(dest_dir, file)
            shutil.move(source_path, destination_path)
            logger.info(f"Moved: {source_path} -> {destination_path}")

def run_canoe_test(sw_variant, cfg_file, xcp_conf_path, path_platform, test_unit, copy_report_dest_path,
                   run_restbus_kpi, run_fvideo_kpi, customer, is_xcp_updated, endurance_test_module="",
                   run_fvideo_kpi_endurance=False):
    """
    opens canoe runs given test cases then caculates kpi if needed

    Args:
      sw_variant (str): vteststudio catalog test profile
      cfg_file (str): path to the canoe cfg file
      xcp_conf_path (str): path to the scp config file
      path_platform (str): main repo folder path
      test_unit (dict):  test unit to run capl/vtest
      copy_report_dest_path (str): copy report path
      run_restbus_kpi (bool): true/false
      run_fvideo_kpi (bool): true/false
      customer (str): name of customer
      endurance_test_module (str):  (Default value = "") endurance run test module with no of iteration
      run_fvideo_kpi_endurance (bool):  (Default value = False) true/false

    """
    logging_folder_path = path_platform + r"\\CustomerPrj\\Traces"
    write_errors_path = path_platform + r"\write_window.txt"
    failed_test_units = []
    capl_failed_tms = {}
    
    p = subprocess.Popen(["powershell.exe", path_platform + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    try:
        canoeClient.openConfiguration(cfg_file)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")

        canoeClient.enable_write_window_log(write_errors_path)
        if is_xcp_updated == 'yes':
            canoeClient.removeAllXCPDevices()
            canoeClient.addXCPConfiguration(xcp_conf_path)
        
        # logging_path = canoeClient.set_logging_path(logging_path)
        if run_restbus_kpi:
            canoeClient.activate_measurementSetup_block("CAN Statistics")
            canoeClient.enable_logging_filter([1,2,3,4,7])

        if customer == "FORD" and run_restbus_kpi and not (endurance_test_module):
            try:
                canoeClient.enableTestEnvironments("Infratesting_CarMaker")
            except Exception as e:
                logger.error(f"Error while enabling test env Infratesting_CarMaker for rbs_kpi -> {e}")

            
        canoeClient.startMeasurement()
        #canoeClient.set_logging_path(r"D:\_RBS\cloe_share_measurements\{IncTrigger|061}_{LocalTime}.mf4")
        if customer == "OD":
            canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)

        if run_restbus_kpi or run_fvideo_kpi:
            canoeClient.setVariableToValue("hil_ctrl", "jenkins_control", 1)

        if test_unit["CAPL"]:
            capl_tcs_split = test_unit["CAPL"].split("@@")
            if "TEST_ENVIRONMENT" in capl_tcs_split:
                capl_failed_tms = canoeClient.executeTestModules(capl_tcs_split[0])   #returns {module_name: failed_verdict- failed/unavailable}
            else:
                capl_failed_tms = canoeClient.executeTestsInTestModules(capl_tcs_split[0])
            
            time.sleep(1)

        # if customer=="FORD" and run_restbus_kpi and not(endurance_test_module):
        #     failed_tests = canoeClient.executeTestsInTestModules("Infratesting_CarMaker")  #returns {module_name: failed_verdict- failed/unavailable}
        #     if failed_tests:
        #         for mod, verdict in failed_tests.items():
        #             capl_failed_tms[mod] = verdict


        if test_unit["VTEST"]:
            if "::" in test_unit["VTEST"]:
                tests = test_unit["VTEST"].split(",")
                tests = [i.strip() for i in tests]
                for i, t in enumerate(tests):
                    if "::" in t:
                        split_t = t.split("::")
                        test_name = split_t[0]
                        sw_variant = split_t[1]
                        failed_tests = canoeClient.executeTestsInTestConfiguration(test_name, customer, path_platform, sw_variant)
                        if failed_tests:
                            failed_test_units.append(failed_tests)
            else:
                failed_test_units = canoeClient.executeTestsInTestConfiguration(test_unit["VTEST"], customer, path_platform, sw_variant)
        # canoeClient.setVariableToValue("hil_ctrl", "trace_logging_start_mf4", 0.0)


        time.sleep(5)
        #ENDURANCE_RUN to begin with only consider test modules
        if endurance_test_module:
            #temporary need to implement kpi for endurance run
            canoeClient.setVariableToValue("hil_ctrl", "jenkins_control", 0)

            dict_endurance_results = {}
            logger.info("-------Starting Endurance Runs--------")
            for value in endurance_test_module:
                tm_split = value.strip().split("::")
                if len(tm_split)!=2:
                    logger.error(f"Invalid syntax given in endurance run -> {value}")
                    continue
                test_module_name, no_iterations = tm_split
                
                try:
                    no_iterations = int(no_iterations)
                except:
                    logger.error(f"Test module iteration in endurance run is not int, check syntax")
                    continue
                dict_endurance_results[test_module_name] = {}
                dict_endurance_results[test_module_name]["no_iterations"] = no_iterations
                dict_endurance_results[test_module_name]["passed"] = 0
                dict_endurance_results[test_module_name]["failed"] = 0
                for i in range(1,no_iterations+1):
                    logger.info(f"{test_module_name} - Iteration-{i}")
                    verdict = canoeClient.executeTestsInTestModules(test_module_name, kpi_run=True)
                    if verdict:
                        logger.warning("Verdict -> failed")
                        dict_endurance_results[test_module_name]["failed"] +=1
                    else:
                        dict_endurance_results[test_module_name]["passed"] +=1
                        logger.info("Verdict -> passed")

            #log info for jenkins
            for test_mod, dict_results in dict_endurance_results.items():
                logger.info(f"ENDURANCE_RUN_INFO#:#<b>{test_mod}:</b>#:#")
                logger.info(f"ENDURANCE_RUN_INFO#:#        -Iterations -> {dict_results['no_iterations']}#:#")
                logger.info(f"ENDURANCE_RUN_INFO#:#        -Passed -> {dict_results['passed']}#:#")
                logger.info(f"ENDURANCE_RUN_INFO#:#        -Failed -> {dict_results['failed']}#:#")
                logger.info(f"ENDURANCE_RUN_INFO#:#                        #:#")
                

        time.sleep(10)
        try:
            canoeClient.stopMeasurement()
        except Exception as e:
            logger.warning(f"Couldn't stop measurement, quiting canoe -> {e}")
            canoeClient.quitCanoe(False)
            if (run_restbus_kpi or run_fvideo_kpi):
                time.sleep(4)
                start_canoe = time.time()
                canoeClient = canoe_client_1.CANoeClient()
                canoeClient.openConfiguration(cfg_file)
                canoe_started = time.time()
                logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")

        time.sleep(5)

        #BASIC run KPI calculation
        if (run_restbus_kpi or run_fvideo_kpi):
            mf4_converted_files = convert_BLF_to_MF4(canoeClient, src_folder = logging_folder_path, dest_folder = logging_folder_path+"\\MF4_CONVERTED")
            time.sleep(5)
            rest_bus_log_path = os.path.join(path_platform, 'performance_errors.txt')
            if mf4_converted_files == []:
                mf4_converted_files = get_mf4_log_file_paths(logging_folder_path)
            for mf4_file_path in mf4_converted_files:
                file_name=mf4_file_path.split("\\")[-1]
                if run_restbus_kpi:
                    runKPI(mf4_file_path, path_platform, rest_bus_log_path)
                    logger.info(f"-----------FINISHED RESTBUS KPI calculation  for -> {file_name}-----------")
                if run_fvideo_kpi and "config4" in file_name.lower():
                    output_excel_path = path_platform + r"\\FVIDEO_KPI_" + file_name.replace(".mf4",".xlsx")
                    scenario_type, scenario_target_type = get_scenario_target_type(file_name)
                    if not(scenario_type):
                        logger.warning(f"Couldn't find scenario_type from test module_name -> {file_name}, the pattern and scenario might not be defined in evaluation excel/ script dict mapping")
                        continue
                    logger.info(f"Found scenario_type -> {scenario_type}, scenario_target_type -> {scenario_target_type}")
                    runFvideoKPI(mf4_file_path,output_excel_path,scenario_type, scenario_target_type)

            if run_restbus_kpi:
                merge_excel_files_into_sheets(path_platform+r"\\KPI_OUTPUT", main_folder = path_platform)
 


        #move test report to given network_folder
        if copy_report_dest_path != "no":
            copyReport(path_platform, copy_report_dest_path, cfg_file)   #cfg_file is for finding the customer name

        
        get_testcase_info(path_platform, customer)
        if customer != "FORD":
            logWriteWindowErrors(write_errors_path)
        
        if failed_test_units or capl_failed_tms:
            logger.error(f"Tests ended with result FAILED -> vtest: {failed_test_units}, capl: {capl_failed_tms}. Please check the report!!!")
            raise Exception(f"Failed test cases -> vtest: {failed_test_units},capl: {capl_failed_tms}")
                # return testConfiguration.Verdict

        return ""
    except Exception as e:
        if customer != "FORD":
            logWriteWindowErrors(write_errors_path)
        logger.error(f"Stop at exception --> {e}")
        raise e

def logWriteWindowErrors(txt_file_path):
    """
    prints the logged write window errors to jenkins console

    Args:
      txt_file_path (str): path to logged txt file

    """
    if os.path.exists(txt_file_path):
        with open(txt_file_path,"r") as file:
            lines = file.readlines()
            if len(lines)>0:
                for line in lines:
                    logger.warning(f"WRITE_WINDOW::- {line.strip()}::")
            file.close()



def get_canoe_cfg(target_path):
    """
    get canoe cfg name

    Args:
      target_path (str): main repo path

    Returns:
        path of the found cfg file
    """
    for (dirpath, dirnames, filenames) in os.walk(target_path):
        for file in filenames:
            if ".cfg" in file:
                logger.info(f"CANoe configuration path --> {target_path}\\{file}")
                return file


def runKPI(log_file_path, path_platform, rest_bus_log_path):
    """
    runs RBS kpi and creates report

    Args:
      log_file_path (str): path where measurement files are saved
      path_platform (str): main repo path

    """
    try:
        logger.info("########################## START KPI STATS EXTRACT #############################")
        autosar_excel_path = path_platform + r'\\CustomerPrj\\Restbus\\Autosar_Gen_Database.xlsx'
        dict_autosar_data = getAutosarData(autosar_excel_path)
        parseTrace(log_file_path, dict_autosar_data, rest_bus_log_path)
        logger.info("########################## END KPI STATS EXTRACT #############################")
    except Exception as e:
        logger.error(f"error in KPI  --> {e}")



if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS scripts and Canoe Integration tests execution.')
    # commandLineParser.add_argument('--platform_path', action="store", dest="platform_path", required=True,
    #                                help="Absolute path PF folder")
    commandLineParser.add_argument('--sw_variant', action="store", dest="sw_variant", required=False, default=None,
                                   help="software variant to configure")
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    commandLineParser.add_argument('--test_unit', action="store", dest="test_unit", required=False, default=None,
                                   help="Test unit name")
    commandLineParser.add_argument('--update_rbs', action="store", dest="update_rbs", required=True,
                                   help="Update RBS True/False")
    commandLineParser.add_argument('--update_fdx', action="store", dest="update_fdx", required=True,
                                   help="Update FDX True/False")
    # commandLineParser.add_argument('--update_cm', action="store", dest="update_cm", required=True,
    #                                help="Update CarMaker nodes True/False")
    commandLineParser.add_argument('--autosar', action="store", dest="autosar", required=True,
                                   help="Create Autosar sheets True/False")
    commandLineParser.add_argument('--create_arxml', action="store", dest="create_arxml", required=True,
                                   help="Create ARXML sheets True/False")
    commandLineParser.add_argument('--copy_report_path', action="store", dest="copy_report_path", required=False, default="no",
                                   help="provide a path where test reports should be copied")
    commandLineParser.add_argument('--run_restbus_kpi', action="store", dest="run_restbus_kpi", required=False, default=None,
                                   help="check if rbs kpi is required")
    commandLineParser.add_argument('--run_fvideo_kpi', action="store", dest="run_fvideo_kpi", required=False, default=None,
                                   help="check if fvideo kpi is required")
    commandLineParser.add_argument('--capl_tests_endurance_run', action="store", dest="capl_tests_endurance_run", required=False, default="-",
                                   help="capl tests with no_of_iterations,syntax: test_module_name::no_of_iterations,...")
    commandLineParser.add_argument('--run_fvideo_kpi_endurance', action="store", dest="run_fvideo_kpi_endurance", required=False, default=None,
                                   help="check if fvideo kpi is required")
    commandLineParser.add_argument('--customer', action="store", dest="customer", required=True,
                                   help="Customer name")
    commandLineParser.add_argument('--is_xcp_updated', action="store", dest="is_xcp_updated", required=False, default="no",
                                   help="check xcp is updated or not")

    arguments = commandLineParser.parse_args()

   
    if arguments.autosar == "true":
        execute_autosar(arguments.customer_path)
    if arguments.create_arxml == "true":
        execute_create_arxml(arguments.customer_path)
    if arguments.update_rbs == "true":
        execute_update_sysvartab(arguments.customer_path)
        execute_create_nodes(arguments.customer_path)
        execute_create_sysvar(arguments.customer_path)
        execute_create_ininode(arguments.customer_path)
        #execute_create_gw(arguments.customer_path)
    if arguments.update_fdx == 'true':
        execute_update_fdx_nodes(arguments.customer_path)
        execute_update_fdx_database(arguments.customer_path)
    # if arguments.update_cm == "true":
    #     excecute_update_cm_nodes(arguments.customer_path)

    canoe_cfg = get_canoe_cfg(arguments.customer_path)
    conf_full_path = arguments.customer_path + r"\\" + canoe_cfg
    xcp_full_path = arguments.customer_path + r"\\CustomerPrj\\XCP\\XCP_config_gen.xcpcfg"

    run_restbus_kpi = True if arguments.run_restbus_kpi == "true" else False
    run_fvideo_kpi = True if arguments.run_fvideo_kpi == "true" else False
    run_fvideo_kpi_endurance = True if arguments.run_fvideo_kpi_endurance == "true" else False


    if run_restbus_kpi or run_fvideo_kpi:
        os.mkdir(arguments.customer_path + r"\\KPI_OUTPUT")

    if run_fvideo_kpi_endurance:
        os.mkdir(arguments.customer_path + r"\\KPI_OUTPUT_ENDURANCE")

    try:
        test_units = arguments.test_unit.replace("'",'"')
        test_units = loads(test_units)
    except:
        logger.error(f"test unit name input error --> {arguments.test_unit}")
        raise Exception(f"test unit name input error --> {arguments.test_unit}")
    

    #endurance
    capl_test_modules_split=False
    capl_test_modules_endurance = arguments.capl_tests_endurance_run
    if capl_test_modules_endurance!="-":
        capl_test_modules_split = capl_test_modules_endurance.split(",")



    if test_units:
        run_canoe_test(arguments.sw_variant, conf_full_path,xcp_full_path, arguments.customer_path,
                       test_units, arguments.copy_report_path, run_restbus_kpi, run_fvideo_kpi,arguments.customer,arguments.is_xcp_updated,
                       endurance_test_module = capl_test_modules_split, run_fvideo_kpi_endurance = run_fvideo_kpi_endurance)
    
