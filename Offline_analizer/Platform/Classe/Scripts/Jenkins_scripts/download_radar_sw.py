# -*- coding: utf-8 -*-
# @file download_radar_sw.py
# @author ADAS_HIL_TEAM
# @date 10-05-2023

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
this file has all functions related to radar sw path handling and finding radar a2l path
"""

import glob
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import zipfile
import argparse


def get_latest_dir(rpc_build_no = None):
    """
    gets the sw path in the given artifactory in the nightly release artifactory path

    Args:
      rpc_build_no:  (Default value = None)

    Returns:
        str: sw path

    """
    remote_path = r"\\abtvdfs2.de.bosch.com\ismdfs\iad\DACore\artifacts\nightly-release"
    list_of_dirs = glob.glob(rf"{remote_path}\*")
    if rpc_build_no!=None:
        latest_dir = remote_path + "\\" + str(rpc_build_no).strip()
    else:
        latest_dir = max(list_of_dirs, key=os.path.getctime)
    try:
        os.chdir(latest_dir + r'\\Radar_rpc_alpha_2')
    except FileNotFoundError as e:
        try:
            os.chdir(latest_dir + r'\\Radar_rpc_alpha_2')
        except FileNotFoundError as e:
            logger.error(f"Radar_rpc_alpha_2 folder not found in latest artifact -> {latest_dir}")
            raise Exception(f"Radar_rpc_alpha_2 folder not found in latest artifact -> {latest_dir}")
    sw_full_path = os.getcwd()
    return sw_full_path


def extract_radar_sw(path, zip_pattern):
    """
    search and extract radar sw zip file

    Args:
      path (str): path where zip file is present
      zip_pattern (str): zip file name pattern

    """
    extract_dir = r'D:\Jenkins\ADAS_Platform\SW_Release\RadarFC'
    file_list = os.listdir(path)
    zip_file_found = False
    for sw_zip in file_list:
        if zip_pattern in sw_zip:
            try:
                zip_file_found = True
                zip_full_path = os.getcwd() + '\\' + sw_zip
                with zipfile.ZipFile(zip_full_path, 'r') as zip_ref:
                    logger.info(f"Start extracting radar_sw_path#:#{zip_full_path}#:#")
                    zip_ref.extractall(extract_dir)
                    logger.info("Extracting of the latest Radar SW was successful")
            except Exception as e:
                raise e
    if zip_file_found == False:
        logger.error(f"Radar ZIP file not found with pattern {zip_pattern} at {path}")
        raise Exception(f"Radar ZIP file not found with pattern {zip_pattern} at {path}")



if __name__ == '__main__':
    try:
        # for RPC alpha2 OD_nightly-release
        commandLineParser = argparse.ArgumentParser(description='download latest rpc alpha release folder')
        commandLineParser.add_argument('--release_build_no', action="store", dest="release_build_no", required=False,default=None,
                                    help="rpc ci nightly release build number")
        
        arguments = commandLineParser.parse_args()

        rpc_build_no = arguments.release_build_no   # rpc nightly build number can be given from jenkins else latest folder will be considered

        sw_path = get_latest_dir(rpc_build_no=rpc_build_no)
        extract_radar_sw(sw_path, "RPC_ALPHA_2")
        
    except Exception as e:
        logger.error(f"Error in Radar sw extraction -> {e}")
        raise e



