import elporto_rqm
import subprocess
import sys
import os
import xml.etree.ElementTree as ET
import argparse
from urllib.parse import urlparse, parse_qs, unquote
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a logger instance
logger = logging.getLogger(__name__)


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
    rqm_server = "https://rb-alm-13-p.de.bosch.com/qm/web/console/RAD5_VW_FR5CP_MRR5E3%20(qm)#action=com.ibm.rqm.planning.home.actionDispatcher&subAction=viewTestPlan&id=99645"
    project_area = "W620_System_Integration"
    testplan_id = "99645"
    rqm_release_iteration = "W620"
    test_reports_path = r"C:\TOOLS\Offline_analizer\Platform\TestCases\InfraTests\Python_Tests\Reports"
    username = "tic7lr"
    password = "password"
    update_test_results_to_rqm(rqm_server, project_area, testplan_id, rqm_release_iteration, test_reports_path, username, password)