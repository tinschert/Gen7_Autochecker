import argparse
import os,sys
from rbs_and_canoe_tests import *
import re
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import subprocess
import pythoncom
import time
import canoe_client_1

def find_python_files(path, file_names):
    found_files = []
    for file_name in file_names:
        full_file_name = f"{file_name}.py"
        for root, dirs, files in os.walk(path):
            if full_file_name in files:
                found_files.append(os.path.join(root, full_file_name))
    return found_files

def fetch_verdict_from_xml(xml_file):
    try:
        with open(xml_file, 'r') as file:
            content = file.read()  # Read the entire file as a string
        
        # Regular expression to find "Testcase final verdict : PASSED" or "FAILED"
        match = re.search(r"TESTCASE FINAL VERDICT\s*:\s*(\w+)", content)
        
        if match:
            # Extract the verdict (PASSED/FAILED)
            verdict = match.group(1)
            return verdict
        else:
            return "Verdict not found"
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_test_case_result_info(report_paths):
    tc_result_dict = {}
    passed = []
    failed = []
    for reports_path in report_paths:
        reports_path = Path(reports_path)
        logger.info("started parsing report files to get test case results")
        xml_report_files = list(reports_path.rglob("*.xml"))
        for xml_report_file in xml_report_files:
            verdict = fetch_verdict_from_xml(xml_report_file)
            if verdict == "PASSED":
                passed.append(str(xml_report_file).split("\\")[-1].split("___")[0])
            elif verdict == "FAILED":
                failed.append(str(xml_report_file).split("\\")[-1].split("___")[0])
    if len(passed) >= 1:
        tc_result_dict.update({"PASSED": passed})
    if len(failed) >= 1:
        tc_result_dict.update({"FAILED": failed})
    logger.info("end parsing report files to get test case results")
    return tc_result_dict

def get_blf_log_file_paths(directory_path):
    blf_files = []
    # List files in the top-level directory only
    for file in os.listdir(directory_path):
        full_path = os.path.join(directory_path, file)
        # Check if it's a file and ends with .blf
        if os.path.isfile(full_path) and file.endswith(".blf"):
            blf_files.append(full_path)
    return blf_files


def run_python_tests(cfg_file_path, path_platform, test_case_names_str):
    write_errors_path = path_platform + r"\write_window.txt"
    p = subprocess.Popen(["powershell.exe", path_platform + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    bat_file_path = path_platform + r'\Platform\Python_Testing_Framework\CANoePy\using_XIL_API'
    try:
        canoeClient.openConfiguration(cfg_file_path)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")

        canoeClient.enable_write_window_log(write_errors_path)
        
        canoeClient.activate_measurementSetup_block("CAN Statistics")
        canoeClient.enable_logging_filter([1,2,3,4,7])
        canoeClient.startMeasurement()
        canoeClient.setVariableToValue("hil_ctrl", "jenkins_control", 1)
        if isinstance(test_case_names_str, list):
            for test_case_file_name in test_case_names_str:
                if "full_path" in test_case_file_name:
                    command = rf"X:\Tools\venv\Scripts\python.exe Testcase_Execution_Tool_CLI.py --txt_list_full_path {test_case_file_name}"
                    logger.info(command)
                    p = subprocess.run(command, shell=True, cwd=bat_file_path, stdout=sys.stdout, stderr=sys.stderr)
                else:
                    command = rf"X:\Tools\venv\Scripts\python.exe Testcase_Execution_Tool_CLI.py --txt_list {test_case_file_name}"
                    logger.info(command)
                    p = subprocess.run(command, shell=True, cwd=bat_file_path, stdout=sys.stdout, stderr=sys.stderr)
                    if p.returncode == 0:
                        logger.info(f"Test cases from {test_case_file_name} executed successfully")
                    else:
                        logger.error(f"An error occurred while executing test cases from {test_case_file_name}")
                        
        else:
            command = rf"X:\Tools\venv\Scripts\python.exe Testcase_Execution_Tool_CLI.py {test_case_names_str}"
            logger.info(command)
            p = subprocess.run(command, shell=True, cwd=bat_file_path, stdout=sys.stdout, stderr=sys.stderr)
        
    except Exception as e:
        logger.error(f"Stop at exception --> {e}")
        raise e
    finally:
        canoeClient.stopMeasurement()
        canoeClient.quitCanoe(False)
        canoeClient = None
    

def run_kpis(cfg_file_path, path_platform, run_restbus_kpi):
    try:
        start_canoe = time.time()
        canoeClient = canoe_client_1.CANoeClient()
        canoeClient.openConfiguration(cfg_file_path)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        logging_folder_path = path_platform + r"\\CustomerPrj\\Traces"
        blf_log_files = get_blf_log_file_paths(logging_folder_path)
        mf4_converted_files = convert_BLF_to_MF4(canoeClient, src_folder = logging_folder_path, dest_folder = logging_folder_path+"\\PYTHON_TC_MF4_CONVERTED")
        rest_bus_log_path = os.path.join(path_platform, 'performance_errors.txt')
        if mf4_converted_files == []:
            move_mf4_files(source_dir = logging_folder_path, dest_dir = logging_folder_path+"\\PYTHON_TC_MF4_CONVERTED")
            mf4_log_files_path = logging_folder_path + r"\PYTHON_TC_MF4_CONVERTED"
            mf4_converted_files = get_mf4_log_file_paths(mf4_log_files_path)
        for mf4_file_path in mf4_converted_files:
            file_name=mf4_file_path.split("\\")[-1]
            if run_restbus_kpi:
                runKPI(mf4_file_path, path_platform, rest_bus_log_path)
                logger.info(f"-----------FINISHED RESTBUS KPI calculation  for -> {file_name}-----------")
        if run_restbus_kpi:
            merge_excel_files_into_sheets(path_platform+r"\\KPI_OUTPUT", main_folder = path_platform)
        kpi_file_path = path_platform + r"\RESTBUS_KPI.xlsx"
        if os.path.exists(kpi_file_path):
            new_kpi_file_path = path_platform + rf"\PYTHON_RESTBUS_KPI.xlsx"
            os.rename(kpi_file_path, new_kpi_file_path)
            logger.info(f"Report file name renamed old : {kpi_file_path} new : {new_kpi_file_path}")
        kpi_folder_path = path_platform + r"\KPI_OUTPUT"
        python_kpi_folder_path = path_platform + r"\PYTHON_KPI_OUTPUT"
        os.rename(kpi_folder_path, python_kpi_folder_path)
        logger.info(rf"X:\Tools\venv\Scripts\python.exe kpi folder name renamed old : {kpi_folder_path} new : {python_kpi_folder_path}")
    except Exception as e:
        logger.error(f"Stop at exception --> {e}")
        raise e
    finally:
        canoeClient.stopMeasurement()
        canoeClient.quitCanoe(False)
        canoeClient = None


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS scripts and Canoe Integration tests execution.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    commandLineParser.add_argument('--test_case_names', action="store", dest="test_case_names", required=True, default=None,
                                   help="python test case names")
    commandLineParser.add_argument('--run_restbus_kpi', action="store", dest="run_restbus_kpi", required=False, default=None,
                                   help="check if rbs kpi is required")
    
    arguments = commandLineParser.parse_args()
    run_restbus_kpi = True if arguments.run_restbus_kpi == "true" else False
    
    canoe_cfg = get_canoe_cfg(arguments.customer_path)
    conf_full_path = arguments.customer_path + r"\\" + canoe_cfg
    test_case_names_str = []
    test_case_file_names = []
    if ".txt" in arguments.test_case_names:
        test_case_names_var = arguments.test_case_names
        if "," in test_case_names_var:
            test_case_file_names = test_case_names_var.split(",")
        else:
            test_case_file_names.append(test_case_names_var)
        for test_case_file_name in test_case_file_names:
            if "DUT_independant.txt" in test_case_file_name:
                test_case_file_path = arguments.customer_path + r"\Platform\TestCases\InfraTests\Python_Tests" + rf"\{test_case_file_name}"
                test_case_names_str.append(test_case_file_path)
            if "DUT_dependant.txt" in test_case_file_name:
                test_case_file_path = arguments.customer_path + r"\adas_sim\python_testing_framework\sysint_tests" + rf"\{test_case_file_name}"
                test_case_names_str.append(test_case_file_path)
        
    elif ","  in arguments.test_case_names:
        file_names = arguments.test_case_names.split(",")
        test_case_files_path = arguments.customer_path + r"\Platform\TestCases\InfraTests\Python_Tests" 
        test_case_file_paths = find_python_files(test_case_files_path, file_names)
        test_case_names_str = ' '.join(test_case_file_paths)
        test_case_names_str = test_case_names_str.replace(' ', ',')
    run_python_tests(conf_full_path, arguments.customer_path, test_case_names_str)
    report_paths = []
    pf_report_path = arguments.customer_path + r'\Platform\Reports'
    adassim_report_path = arguments.customer_path + r'\Reports'
    report_paths.append(pf_report_path)
    report_paths.append(adassim_report_path)
    tc_result_dict = get_test_case_result_info(report_paths)
    logger.info("started writing python test results to lof file")
    py_tc_log_file_path = arguments.customer_path + r'\py_tc_log.txt'
    with open(py_tc_log_file_path, 'w') as py_tc_log_file:
        for verdict, test_cases in tc_result_dict.items():
            py_tc_log_file.write(f"{verdict}\n")
            for test_case in test_cases:
                py_tc_log_file.write(f"{test_case}\n")
    logger.info("end writing python test results to log file")
    time.sleep(5)
    
    if run_restbus_kpi:
        os.mkdir(arguments.customer_path + r"\\KPI_OUTPUT")
        run_kpis(conf_full_path, arguments.customer_path, run_restbus_kpi)
    py_failed_tcs = tc_result_dict.get("FAILED", [])
    if py_failed_tcs:
        logger.error(f"Tests ended with result FAILED -> {py_failed_tcs} Please check the report!!!")
        raise Exception(f"Failed test cases -> {py_failed_tcs}")
