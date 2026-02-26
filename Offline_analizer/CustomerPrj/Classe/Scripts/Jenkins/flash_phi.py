# -*- coding: utf-8 -*-
# @file flash_dasy.py
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

"""
file which triggers flash script in given dasy sw path
"""

import argparse
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\Platform\Classe\Scripts\Control")
from logging_config import logger
import shutil
import subprocess
import pythoncom
import time
import canoe_client_1
#from update_xcp_configuration import get_flsh_sw_and_a2l_paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\Platform\Classe\Scripts\Jenkins_scripts")
from rbs_and_canoe_tests import logWriteWindowErrors


def run_canoe_for_flashing(cfg_file, path_platform, xcp_conf_path, flash_files_path):
    """
    opens canoe and then triggers flash script

    Args:
      cfg_file (str): path to canoe cfg
      path_platform (str): path to main git repo folder
      xcp_conf_path (str): path of XCP configuration
      flash_path (str): flash script path

    """
    p = subprocess.Popen(["powershell.exe", path_platform + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    write_errors_path = path_platform + r"\write_window.txt"
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    #canape_path = os.path.dirname(flash_path)
    try:
        canoeClient.openConfiguration(cfg_file)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        canoeClient.enable_write_window_log(write_errors_path)
        #canoeClient.removeAllXCPDevices()
        # canoeClient.addXCPConfiguration(xcp_conf_path)
        canoeClient.startMeasurement()
        canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
        canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 2)
        time.sleep(5)
        current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
        logger.info(f"Current Dasy consumption is {current_consumption.Value}")
        if current_consumption.Value > 0.13:
            command = rf'X:\Tools\venv\Scripts\python.exe flashbaseline.py --HIL "MPC"'
            p = subprocess.run(command, shell=True, cwd=flash_files_path, stdout=sys.stdout, stderr=sys.stderr)
        else:
            logger.warning(f"MPC3(Phi) is not powered.Current consumption is {current_consumption.Value}\n Trying Again...")
            canoeClient.stopMeasurement()
            time.sleep(10)
            canoeClient.startMeasurement()
            canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
            canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 2)
            time.sleep(5)
            current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
            logger.info(f"Current MPC3(Phi) consumption is {current_consumption.Value}")
            if current_consumption.Value > 0.13:
                command = rf'X:\Tools\venv\Scripts\python.exe flashbaseline.py --HIL "MPC"'
                p = subprocess.run(command, shell=True, cwd=flash_files_path, stdout=sys.stdout, stderr=sys.stderr)
            else:
                raise Exception(f"MPC3(Phi) is not powered tried 2 times.Current consumption is {current_consumption.Value}")
        if not(validate_flashing(flash_files_path)):
            raise Exception(f"Flashing failed")
    except Exception as e:
        logWriteWindowErrors(write_errors_path)
        logger.error(f"Stop at exception --> {e}")
        raise e
    finally:
        canoeClient.stopMeasurement()
        canoeClient.quitCanoe(False)
        canoeClient = None


def get_canoe_cfg(target_path):
    """
    finds the canoe cfg file in the given path
    Args:
      target_path (str): path to main git repo folder

    Returns:
        str: path to canoe cfg

    """
    for (dirpath, dirnames, filenames) in os.walk(target_path):
        for file in filenames:
            if ".cfg" in file:
                logger.info(f"CANoe configuration path --> {target_path}\\{file}")
                return file


def validate_flashing(flash_path):
    """validate if flashing succeded"""
    try:
        logs_path = os.path.join(flash_path,'_logs')
        log_files_list = [f for f in os.listdir(logs_path) if f.endswith('.txt')]
        log_files_list = [i for i in log_files_list if 'overall' not in i.lower()]
        failed_flashing = []
        for log in log_files_list:
            log_file = os.path.join(logs_path, log)
            try:
                with open(log_file, 'r', encoding='utf-16') as f:
                    lines = f.readlines()
            except UnicodeError as e:
                try:
                    with open(log_file, 'r', encoding='ascii') as f:
                        lines = f.readlines()
                except UnicodeError as e:
                    logger.error(f'Could not read -> {log} , ERROR-> {e}')
                    continue
            last_15_lines = lines[-15:]
            flashing_success = False
            for line in last_15_lines:
                if ('FLASHING SUCCEDED' in line.upper()) or ('flashing successful' in line.lower()):
                    logger.info(f'FLASHING_INFO#:# {log} -> flashing success #:#')
                    flashing_success = True
                    break
            if not(flashing_success):
                failed_flashing.append(log)
                logger.error(f'FLASHING_FAILED#:# {log} -> flashing failed #:#')
                continue
        
        if failed_flashing:
            return False
        else:
            logger.info("----------------FLASHING SUCCESSFUL--------------")
            return True
    except Exception as e:
        logger.error(f'Error while validating flashing -> {e}')
        raise Exception(e)


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS scripts and Canoe Integration tests execution.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    commandLineParser.add_argument('--flash_files_path', action="store", dest="flsh_files_path", required=False, default=None,
                                   help="software variant to configure")
    arguments = commandLineParser.parse_args()

    platform_path = r"D:\Jenkins\ADAS_Platform"
    canoe_cfg = get_canoe_cfg(arguments.customer_path)
    conf_full_path = arguments.customer_path + "\\" + canoe_cfg
    xcp_full_path = arguments.customer_path + "\\CustomerPrj\\XCP\\XCP_config_gen.xcpcfg"
    flash_files_path = arguments.flsh_files_path
    # _, flash_bat_path = get_flsh_sw_and_a2l_paths(arguments.sw_variant)
    run_canoe_for_flashing(conf_full_path, platform_path, xcp_full_path, flash_files_path)
