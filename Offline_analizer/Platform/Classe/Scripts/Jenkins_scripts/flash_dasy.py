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
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import shutil
import subprocess
import pythoncom
import time
import canoe_client_1
from update_xcp_configuration import get_paths_dasy
from rbs_and_canoe_tests import logWriteWindowErrors


def run_canoe_for_flashing(cfg_file, path_platform, xcp_conf_path, flash_path, sw_variant):
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
    canape_path = os.path.dirname(flash_path)
    try:
        canoeClient.openConfiguration(cfg_file)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        canoeClient.enable_write_window_log(write_errors_path)
        canoeClient.removeAllXCPDevices()
        canoeClient.addXCPConfiguration(xcp_conf_path)
        canoeClient.startMeasurement()
        canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
        
        if sw_variant != "[Default]":
            if sw_variant == "DPCdelta5":
                sw_variant = 6
            elif sw_variant == "DPCdelta1":
                sw_variant = 1
            else:
                logger.error(f"for {sw_variant} system variable value is not set. please check and update script")
            canoeClient.setVariableToValue("hil_ctrl", "configuration_od", sw_variant)
        else:
            canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 1)
        time.sleep(5)
        current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
        logger.info(f"Current Dasy consumption is {current_consumption.Value}")
        if current_consumption.Value > 0.13:
            p = subprocess.Popen(["01_FlashActualDasySwToECU.bat"], shell=True, cwd=canape_path, stdout=sys.stdout)
            p.communicate()
        else:
            logger.warning(f"Dasy is not powered.Current consumption is {current_consumption.Value}\n Trying Again...")
            canoeClient.stopMeasurement()
            time.sleep(10)
            canoeClient.startMeasurement()
            canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
            if sw_variant != "[Default]":
                if sw_variant == "DPCdelta5":
                    sw_variant = 6
                elif sw_variant == "DPCdelta1":
                    sw_variant = 1
                else:
                    logger.error(f"for {sw_variant} system variable value is not set. please check and update script")
                canoeClient.setVariableToValue("hil_ctrl", "configuration_od", sw_variant)
            else:
                canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 1)
            time.sleep(5)
            current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
            logger.info(f"Current Dasy consumption is {current_consumption.Value}")
            if current_consumption.Value > 0.13:
                p = subprocess.Popen(["01_FlashActualDasySwToECU.bat"], shell=True, cwd=canape_path, stdout=sys.stdout)
                p.communicate()
            else:
                raise Exception(f"Dasy is not powered tried 2 times.Current consumption is {current_consumption.Value}")
        if not(parseLog(flash_path)):
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

def parseLog(flash_path):
    """
    checks if flashing was success or failure by parsing the flash log txt file
    Returns:
        bool: true if success else false
    """
    canape_path = os.path.dirname(flash_path)
    flasg_log_path = canape_path + r"\FLASH_CFG\WriteWindow_log.TXT"
    success_count = 0
    try:
        with open(flasg_log_path, 'r', encoding='latin-1') as log_file:
            for line in log_file.readlines():
                if "[SUCESS]" in line:
                    success_count += 1
            log_file.close()
        if success_count >= 3:
            return True
        return False
    except Exception as e:
        raise Exception(f"Error while parsing flash log -> {e}")


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS scripts and Canoe Integration tests execution.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    commandLineParser.add_argument('--sw_variant', action="store", dest="sw_variant", required=False, default=None,
                                   help="software variant to configure")
    arguments = commandLineParser.parse_args()

    platform_path = r"D:\Jenkins\ADAS_Platform"
    canoe_cfg = get_canoe_cfg(arguments.customer_path)
    conf_full_path = arguments.customer_path + "\\" + canoe_cfg
    xcp_full_path = arguments.customer_path + "\\CustomerPrj\\XCP\\XCP_config_gen.xcpcfg"
    _, flash_bat_path = get_paths_dasy()
    run_canoe_for_flashing(conf_full_path, platform_path, xcp_full_path, flash_bat_path, arguments.sw_variant)

