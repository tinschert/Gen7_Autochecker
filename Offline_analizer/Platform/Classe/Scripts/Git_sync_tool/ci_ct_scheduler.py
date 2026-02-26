# -*- coding: utf-8 -*-
# @file ci_ct_scheduler.py
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


import Git_gui_main
import Git_Clone
import configparser
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import subprocess as sp

sequence = Git_gui_main.MainWin()

config = configparser.ConfigParser()
config.read('ci_ct_configuration.ini')

pf_branch = config['platform']['pf_branch']
pf_local_dir = config['platform']['pf_local_dir']
commit_message = config['platform']['commit_mes']
od_local_dir = config['od']['cust_local_dir']
psa_local_dir = config['psa']['cust_local_dir']
ford_local_dir = config['ford']['cust_local_dir']
toyota_local_dir = config['toyota']['cust_local_dir']
psa_dcross_local_dir = config['toyota']['cust_local_dir']
projects_path = [od_local_dir, psa_local_dir, ford_local_dir, toyota_local_dir, psa_dcross_local_dir]

try:
    Git_Clone.checkout_repo(pf_branch, pf_local_dir)
    for target in projects_path:
        if target != '':
            sequence.copy_platform(pf_local_dir, target)
            sequence.execute_rbs_scripts(target)
            canoe_cfg = sequence.get_canoe_cfg(target)
            test_status = sequence.run_canoe_test_scheduler(canoe_cfg, pf_local_dir)
            if test_status == 1:
                logger.info("CanOE system integration tests PASSED")
                Git_Clone.commit_push(pf_local_dir, commit_message)
                logger.info("Platform integration test sequence finished successfully")
            else:
                logger.error("CanOE integration tests FAILED. Please check the report!")

except Exception as e:
    logger.error(f"Platform integration tests failed --> {e}")

sp.Popen(["notepad.exe", "Debug.log"])




