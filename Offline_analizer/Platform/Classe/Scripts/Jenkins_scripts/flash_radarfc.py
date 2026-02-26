# -*- coding: utf-8 -*-
# @file flash_radarfc.py
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
file which triggers flash script in given radarfc sw path
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
from update_xcp_configuration import get_paths_radar_fc
from rbs_and_canoe_tests import logWriteWindowErrors
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Classe\Scripts\Jenkins")
from od_flash_baseline import reset_vx


def run_canoe_for_flashing(cfg_file, path_platform, xcp_conf_path, flash_preparation_bat_path, flash_path):
    """
    opens canoe and then triggers flash script

    Args:
      cfg_file (str): path to canoe cfg
      path_platform (str): path to main git repo folder
      xcp_conf_path (str): path of XCP configuration
      flash_preparation_bat_path (str): path to flash preparation bat file
      flash_path (str): path to flash bat file

    """
    p = subprocess.Popen(["powershell.exe", path_platform + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    write_errors_path = path_platform + r"\write_window.txt"
    reset_vx(path_platform)
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    try:
        canoeClient.openConfiguration(cfg_file)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        canoeClient.enable_write_window_log(write_errors_path)
        #canoeClient.removeAllXCPDevices()
        logger.info("Deactivating XCP Devices...")
        xcp_ecus = canoeClient.CANoe.Configuration.GeneralSetup.XCPSetup.ECUs
        for i in range(1, xcp_ecus.Count + 1):
            xcp_ecus.Item(i).Active = False
            time.sleep(0.5)
        logger.info("Deactivated XCP Devices")
        #canoeClient.addXCPConfiguration(xcp_conf_path)
        canoeClient.startMeasurement()
        canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
        canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 3)
        time.sleep(5)
        current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
        logger.info(f"RadarFC current consumption is {current_consumption.Value}")
        if current_consumption.Value > 0.13:
            p = subprocess.Popen(["01_FlashActualDasySwToECU.bat"], shell=True, cwd=r'D:\Jenkins\ADAS_Platform\SW_Release\RadarFC\RadarFC\measurement_hil\Canape', stdout=sys.stdout)
            p.communicate()
            time.sleep(1)
            logger.info(f"{flash_path} finished running")
        else:
            logger.warning(f"RadarFC is not powered.Current consumption is {current_consumption.Value}\n Trying to start measurement Again...")
            canoeClient.stopMeasurement()
            time.sleep(10)
            canoeClient.startMeasurement()
            canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
            canoeClient.setVariableToValue("hil_ctrl", "configuration_od", 3)
            time.sleep(5)
            current_consumption = canoeClient.getSysVariable("PS", "current_display_Ch1")
            logger.info(f"RadarFC current consumption is {current_consumption.Value}")
            if current_consumption.Value > 0.13:
                p = subprocess.Popen(["01_FlashActualDasySwToECU.bat"], shell=True, cwd=r'D:\Jenkins\ADAS_Platform\SW_Release\RadarFC\RadarFC\measurement_hil\Canape', stdout=sys.stdout)
                p.communicate()
                time.sleep(1)
                logger.info(f"{flash_path} finished running")
            else:
                raise Exception(f"RadarFC is not powered tried 2 times.Current consumption is {current_consumption.Value}")
        if not(parseLog()):
            raise Exception(f"RadarFC Flashing Failed")
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
    find canoe cfg file path

    Args:
      target_path (str): folder path where canoe cfg is present

    Returns:
        str: path to canoe cfg file

    """
    for (dirpath, dirnames, filenames) in os.walk(target_path):
        for file in filenames:
            if ".cfg" in file:
                logger.info(f"CANoe configuration path --> {target_path}\\{file}")
                return file

def parseLog():
    """
    checks if flashing was success or failure by parsing the flash log txt file
    Returns:
        bool: true if success else false
    """
    flash_log_path = r"D:\Jenkins\ADAS_Platform\SW_Release\RadarFC\RadarFC\measurement_hil\Canape\FLASH_CFG\WriteWindow_log.TXT"
    success_count = 0
    try:
        with open(flash_log_path, 'r', encoding='latin-1') as log_file:
            for line in log_file.readlines():
                if "[SUCESS]" in line.upper():
                    success_count += 1
            log_file.close()
        if success_count >= 3:
            logger.info(f'FLASHING_INFO#:# {flash_log_path} -> flashing success #:#')
            return True
        else:
            logger.error(f'FLASHING_INFO#:# {flash_log_path} -> flashing failed #:#')
            return False
    except Exception as e:
        raise Exception(f"Error while parsing flash log -> {e}")


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS scripts and Canoe Integration tests execution.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    arguments = commandLineParser.parse_args()

    platform_path = r"D:\Jenkins\ADAS_Platform"
    canoe_cfg = get_canoe_cfg(arguments.customer_path)
    conf_full_path = arguments.customer_path + "\\" + canoe_cfg
    xcp_full_path = arguments.customer_path + "\\CustomerPrj\\XCP\\XCP_config_gen.xcpcfg"
    _, flash_preparation_bat_path, flash_bat_path = get_paths_radar_fc()
    run_canoe_for_flashing(conf_full_path, platform_path, xcp_full_path, flash_preparation_bat_path, flash_bat_path)
