# -*- coding: utf-8 -*-
# @file cict_main.py
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
import os
import fix_a2l_jenkins
import subprocess as sp
import update_xcp_configuration
import rbs_and_canoe_tests

#parse command line arguments
commandLineParser = argparse.ArgumentParser(description='Platform CI/CT.')
commandLineParser.add_argument('--project', action="store", dest="project", required=True, help="Select project")
commandLineParser.add_argument('--variant', action="store", dest="variant", required=True, help="Select variant")
# commandLineParser.add_argument('--dasy_sw_path', action="store", dest="dasy_sw_path", required=False, help="DaSy SW path")
# commandLineParser.add_argument('--front_center_sw_path', action="store", dest="front_center_sw_path", required=False, help="Front Center Radar SW path")
# commandLineParser.add_argument('--corner_sw_path', action="store", dest="corner_sw_path", required=False, help="Corner Radar SW path")
# commandLineParser.add_argument('--video_sw_path', action="store", dest="video_sw_path", required=False, help="Video SW path")
commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,help="Absolute path to customer folder")
# commandLineParser.add_argument('--classe_tests', action="store", dest="classe_tests", required=False, help="Execute classe tests True/False")
# commandLineParser.add_argument('--cloe_tests', action="store", dest="cloe_tests", required=True,help="Execute cloe tests True/False")
arguments = commandLineParser.parse_args()

platform_path = r"D:\Jenkins\ADAS_Platform"
front_center_sw_path = r"D:\ADAS_HIL\SW_Release\Front"
corner_sw_path = r"D:\ADAS_HIL\SW_Release\Corner"
video_sw_path = r"D:\ADAS_HIL\SW_Release\Video"


def get_paths_dasy():
    """ """
    dasy_sw_path = r"D:\Jenkins\ADAS_Platform\SW_Release\Dasy"
    canape_project_path = ""
    a2l_absolute_path = ""
    sw_flash_path = ""

    for root, dirs, files in os.walk(dasy_sw_path):
        for name in dirs:
            if "measurement_golf" in name.lower():
                measurement_path = os.path.join(root, name)
                a2l_folder_path = measurement_path + r"\database\a2l"
                canape_project_path = measurement_path + r"\Canape"
                sw_flash_path = canape_project_path + "\\" + "01_FlashActualDasySwToECU.bat"

    for root, dirs, files in os.walk(a2l_folder_path):
        for name in files:
            if ".a2l" in name.lower():
                a2l_absolute_path = a2l_folder_path + "\\" + name
    return canape_project_path, a2l_absolute_path, sw_flash_path


canape_path, a2l_path_dasy, flash_batch_path = get_paths_dasy()

if arguments.project == "OD":
    if arguments.variant == "1D":
        update_xcp_configuration.update_xcpconfig(None, None, a2l_path_dasy)
        os.chdir(canape_path)
        p = sp.Popen(flash_batch_path)
        #stdout, stderr = p.communicate()
        rbs_and_canoe_tests.copy_platform(platform_path, arguments.customer_path)
        rbs_and_canoe_tests.execute_update_sysvartab(arguments.customer_path)
        rbs_and_canoe_tests.execute_create_nodes(arguments.customer_path)
        rbs_and_canoe_tests.execute_create_sysvar(arguments.customer_path)
        rbs_and_canoe_tests.execute_create_ininode(arguments.customer_path)
        rbs_and_canoe_tests.execute_update_ini(arguments.customer_path)
        rbs_and_canoe_tests.execute_create_gw(arguments.customer_path)
        if arguments.classe_tests is True:
            canoe_cfg = rbs_and_canoe_tests.get_canoe_cfg(arguments.customer_path)
            conf_full_path = arguments.customer_path + "\\" + canoe_cfg
            rbs_and_canoe_tests.run_canoe_test(conf_full_path, platform_path)
        if arguments.cloe_tests is True:
            pass

    if arguments.variant == "1R":
        fix_a2l_jenkins.main_sequence(canape_project_path, a2l_absolute_path)





