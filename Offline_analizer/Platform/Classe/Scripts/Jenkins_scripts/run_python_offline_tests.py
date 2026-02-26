import sys
import os
import xml.etree.ElementTree as ET
import argparse
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import subprocess

def get_rqm_test_details(rqm_url):

    try:
        if not rqm_url:
            raise ValueError("The RQM URL cannot be empty or None.")
        # Parse the URL
        parsed_url = urlparse(rqm_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid RQM URL format. Ensure it includes the scheme (e.g., https://) and domain.")
        # Extract the server
        rqm_server = f"{parsed_url.scheme}://{parsed_url.netloc}"
        # Extract the project area from the path
        if not parsed_url.path:
            raise ValueError("The URL path is missing, unable to extract the project area.")
        project_area = parsed_url.path.split('/')[-1]
        project_area = unquote(project_area) # Decode %20 (space)
        # Extract the test plan ID from the fragment
        if not parsed_url.fragment:
            raise ValueError("The URL fragment is missing, unable to extract the test plan ID.")
        query_params = parse_qs(parsed_url.fragment)
        testplan_id = query_params.get('id', [None])[0]
        if not testplan_id:
            raise ValueError("The test plan ID is missing in the URL fragment.")
        logger.info(f"RQM Server : {rqm_server}")
        logger.info(f"Project Area : {project_area}")
        logger.info(f"Test Plan ID : {testplan_id}")
        return rqm_server, project_area, testplan_id
    except Exception as e:
        logger.error(f"An error occurred while parsing the RQM URL: {e}")
        return None, None, None
    
def run_python_offline_tests(test_cases, trace_file_paths):
    try:
        for trace_file_path in trace_file_paths:
            for test_case in test_cases:
                test_cases_path = os.path.dirname(test_case)
                command = rf"D:\Tools\venv\Scripts\python.exe {test_case} --log_file_path {trace_file_path}"
                process = subprocess.run(command, shell=True, cwd=test_cases_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                error_output = process.stderr.strip()
                if "No Python at" in error_output or "not found" in error_output.lower() or "no such file" in error_output.lower():
                    raise Exception(f"Execution failed: {error_output}")
                critical_errors = ["ImportError", "ModuleNotFoundError", "NameError", "SyntaxError", "AttributeError"]
                if any(error in error_output for error in critical_errors):
                    raise Exception(f"An error occurred while executing test case {test_case}: \n{error_output}")
                if process.returncode != 0:
                    logger.warning(f"{test_case} execution is failed. Please check report.")
                else:
                    logger.info(f"test case {test_case} executed successfully.")
        return   
    except FileNotFoundError as e:
        raise Exception(f"Execution failed: {e}")
    except OSError as e:
        raise Exception(f"OS-related error occurred: {e}")
    

def get_test_results(reports_paths):
    failed_tests = []
    passed_tests = []
    tc_result_dict = {}

    logger.info("start parsing report files to get test case results")
    for reports_path in reports_paths:
        xml_files = [f for f in os.listdir(reports_path) if f.endswith(".xml") and os.path.isfile(os.path.join(reports_path, f))]

        for file in xml_files:
            file_path = os.path.join(reports_path, file)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                test_case_headers = root.findall(".//TestCaseHeader")
                if test_case_headers:
                    last_test_case_header = test_case_headers[-1].text.strip()
                    type_of_test_case = last_test_case_header.split('|')[-1].strip()
                test_case_file_name = root.find(".//TestCaseName")
                test_case_full_file_path = os.path.join(os.path.dirname(reports_path), test_case_file_name.text.strip())

                # Fetch all <TestStepResult> elements
                test_result = root.find(".//FinalResult").text.strip()
                if "FAILED" in test_result and "Negative Testcase" in type_of_test_case:
                    passed_tests.append(test_case_full_file_path)
                elif "PASSED" in test_result and "Negative Testcase" in type_of_test_case:
                    failed_tests.append(test_case_full_file_path)
                elif "FAILED" in test_result:
                    failed_tests.append(test_case_full_file_path)
                elif "PASSED" in test_result:
                    passed_tests.append(test_case_full_file_path)
                else:
                    logger.warning(f"Invalid test result --> please check report {file_path}")

            except ET.ParseError as e:
                logger.error(f"Error parsing {file_path}: {e}")
    if len(passed_tests) >= 1:
        tc_result_dict.update({"PASSED": passed_tests})
    if len(failed_tests) >= 1:
        tc_result_dict.update({"FAILED": failed_tests})
    logger.info("end parsing report files to get test case results")

    return tc_result_dict
    
def update_test_results_to_rqm(rqm_server, project_area, testplan_id, rqm_release_iteration, reports_path, username, password):
    try:
        logger.info(f"start updating test results rqm from --> {reports_path}")
        command = f'''rqm --domain "{rqm_server}" --action "update-create" --username "{username}" --password "{password}" \
-pa "{project_area}" -tp "{testplan_id}" -r "{rqm_release_iteration}" -res "{reports_path}"'''
        process = subprocess.run(command, shell=True, cwd=r'D:\Tools\venv\Scripts', stdout=sys.stdout, stderr=sys.stderr)
        if process.returncode == 0:
            logger.info(f"test results from {reports_path} are updated to RQM successfully.")
        else:
            logger.error(f"Test results from {reports_path} are not updated to RQM. command execution is failed please check.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred : {str(e)}")



if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated script for updating testresults to RQM.')
    
    commandLineParser.add_argument('--test_case_names', action="store", dest="test_case_names", required=True,
                                   help="test_case_file_names_to_execute")
    commandLineParser.add_argument('--trace_file_or_folder_link', action="store", dest="trace_file_or_folder_link", required=True,
                                   help="Please provide path of trace files foder or specific trace file path")
    commandLineParser.add_argument('--rqm_utility', action="store", dest="rqm_utility", required=False,
                                   help="check if rqm utility is required")
    commandLineParser.add_argument('--test_catalog_link', action="store", dest="test_catalog_link", required=False,
                                   help="link for RQM test catalog")
    commandLineParser.add_argument('--rqm_release_iteration', action="store", dest="rqm_release_iteration", required=False,
                                   help="RQM Release iteration value")
    commandLineParser.add_argument('--username', action="store", dest="username", required=False,
                                   help="username for RQM")
    commandLineParser.add_argument('--password', action="store", dest="password", required=False,
                                   help="password for RQM")
    arguments = commandLineParser.parse_args()
    rqm_utility = True if arguments.rqm_utility == "true" else False
    rqm_release_iteration = arguments.rqm_release_iteration
    
    
    
    script_path = os.path.abspath(__file__)
    script_path_obj = Path(script_path)
    desired_path = list(script_path_obj.parts)[:script_path_obj.parts.index("Platform")]
    customer_path = Path(*desired_path)

    test_case_file_paths = []
    if os.path.isfile(arguments.test_case_names):
        with open(arguments.test_case_names, 'r') as file:
            test_case_file_names = file.readlines()
            test_case_file_paths = [os.path.join(customer_path, file_name.strip()) for file_name in test_case_file_names]
    elif os.path.isdir(arguments.test_case_names):
        test_case_file_paths = [os.path.join(arguments.test_case_names, file) for file in os.listdir(arguments.test_case_names) if file.lower().endswith('.py') and os.path.isfile(os.path.join(arguments.test_case_names, file))]
    else:
        test_case_file_names = arguments.test_case_names.split(",")
        test_case_file_paths = [os.path.join(customer_path, file_name.strip()) for file_name in test_case_file_names]
    
    for file_path in test_case_file_paths:
        if not os.path.isfile(file_path):
            raise Exception(f"Error: {file_path} does not exist. Please provide proper file names.")
        if not file_path.lower().endswith('.py'):
            raise Exception(f"Error: {file_path} is not a valid Python file. Please provide proper file names.")

    
    trace_file_or_folder_link = arguments.trace_file_or_folder_link
    trace_file_paths = []
    if os.path.isfile(trace_file_or_folder_link):
        if not trace_file_or_folder_link.lower().endswith('.mf4'):
            raise Exception(f"Given file {trace_file_or_folder_link} is not an .mf4 file")
        else:
            trace_file_paths.append(trace_file_or_folder_link)
    elif os.path.isdir(trace_file_or_folder_link):
        trace_file_paths = [os.path.join(trace_file_or_folder_link, file) for file in os.listdir(trace_file_or_folder_link) if file.lower().endswith('.mf4') and os.path.isfile(os.path.join(trace_file_or_folder_link, file))]

    run_python_offline_tests(test_case_file_paths, trace_file_paths)

    username = arguments.username
    password = arguments.password
    test_case_folder_paths = list(set(os.path.dirname(path) for path in test_case_file_paths))
    test_reports_paths = [os.path.join(folder_name.strip(), "Reports") for folder_name in test_case_folder_paths]
    tc_result_dict = {}
    tc_result_dict = get_test_results(test_reports_paths)
    logger.info("started writing python offline test results to log file")
    py_tc_log_file_path = str(customer_path) + r'\py_offline_tc_log.txt'
    with open(py_tc_log_file_path, 'w') as py_tc_log_file:
        for verdict, test_cases in tc_result_dict.items():
            py_tc_log_file.write(f"{verdict}\n")
            for test_case in test_cases:
                py_tc_log_file.write(f"{test_case}\n")
    logger.info("end writing python offline test results to log file")
    if rqm_utility:
        rqm_server, project_area, testplan_id = get_rqm_test_details(arguments.test_catalog_link)
        for test_reports_path in test_reports_paths:
            update_test_results_to_rqm(rqm_server, project_area, testplan_id, rqm_release_iteration, test_reports_path, username, password)
    py_failed_tcs = tc_result_dict.get("FAILED", [])
    if py_failed_tcs:
        logger.error(f"Tests ended with result FAILED -> {py_failed_tcs} Please check the report!!!")
        raise Exception(f"Failed test cases -> {py_failed_tcs}")