# -*- coding: utf-8 -*-
# @file run_cloe_tests.py
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


import linux_client as client
import report_handler as rh
import test_parameters as tc_params
import excel_table_summary as xls_tbl
from argparse import ArgumentParser
from threading import Thread

arguments = ArgumentParser("Give the linux hostname and product variant")
arguments.add_argument('--hostname', type=str, help="Give the linux machine hostname")
arguments.add_argument('--variant', type=str, help="Give the product variant.")
arguments.add_argument('--cloe_repo', type=str, help="Give the Cloe tests repository path. Example: /workspace/XIL_OD_Testing")
args = arguments.parse_args()

transfer_info = {
                "username": "sya9lr",
                "hostname": "FE-Z1VXQ.lr.de.bosch.com",
                "password": "Infracommon1!",
                "variant": "CDPO",
                "cloe_repo": "/home/sya9lr/GIT_Workspace",
                "smoke_tests_folder_name": "XIL_Smoke_Tests_Catalogue",
                "local_results_path": "D:\\CloeSmokeTests\\"
                }
params_if_not_eom = {
                "tc_name": "",
                "tc_sub_cases": {"": "Not started"},
                "tc_state": "Not started",
                "mf4_name": ""}

if __name__ == "__main__":
    transfer_info["hostname"] = args.hostname  # Parse the arguments
    transfer_info["variant"] = args.variant  # Parse the arguments
    transfer_info["cloe_repo"] = args.cloe_repo  # Parse the arguments
    conn_obj = client.ExecClient(**transfer_info)  # Create a connection object
    conn_obj.connect()
    test_cases_list = conn_obj.get_smoke_tests_list()  # Create a list with the test cases and get evald config
    conn_obj.get_evald_config()
    ods_cloe_tests_path = conn_obj.find("ods_cloe_tests")  # Find the ods_cloe_tests folder
    r_handle = rh.ReportHandler(conn_obj, **transfer_info)  # Create a ReportHandler object
    tc_run_name = rh.name_the_tc_run_folder()  # name the current TC run folder (example: tc_run_(date)(time))
    rh.create_test_results_folder(transfer_info["local_results_path"], tc_run_name)
    xls_summary = xls_tbl.ExcelTestResultSummary(transfer_info["local_results_path"] + tc_run_name + "\\")  # Define an excel table creator obj
    for tc in test_cases_list:  # Start running the tests here:
        oem = conn_obj.check_oem_tag(tc)  # Check if test is applicable for selected variant
        if oem:
            print(f"\n\nSTARTING TEST CASE >>> {tc}")
            conn_obj.call_make_file(tc, ods_cloe_tests_path)
            r_handle.transfer_report_from_linux2local()  # After every test, create a TestParameters object
            tc_par = tc_params.TestParameters(r_handle.local_report_path + "\\index.html")
            param_dict = tc_par.get_tc_params()
            print(f"{param_dict['tc_name']} has ENDED with status '{param_dict['tc_state']}'\n\n")
            r_handle.rename_report_folder(param_dict["tc_name"])  # rename the copied report from 'last_report' to the name of the test
            rh.copy_report_to_test_run_folder(tc_run_name, r_handle.local_results_path, r_handle.renamed_report, param_dict["tc_state"])  # move the renamed report into the 'test_run' folder
            temp_local_mf4_path = r_handle.local_results_path + tc_run_name + "\\" + param_dict["tc_state"] + "\\" + param_dict["tc_name"] + "\\"
            if param_dict["mf4_name"] != 'NotValid':
                r_handle.transfer_mf4_from_linux2local(param_dict["mf4_name"], temp_local_mf4_path)
                r_handle.compress_mf4_log(temp_local_mf4_path, param_dict["mf4_name"])
            xls_summary.update_table(param_dict, oem)  # Update the excel table
        else:
            not_started_tc = tc.split('/')[-1]
            print(f"OEM tag not found! tc_name: {not_started_tc}")
            params_if_not_eom["tc_name"] = not_started_tc
            xls_summary.update_table(params_if_not_eom, oem)  # Update the excel table
