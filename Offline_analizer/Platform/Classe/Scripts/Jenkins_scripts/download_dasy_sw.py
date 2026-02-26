# -*- coding: utf-8 -*-
# @file download_dasy_sw.py
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
this file has all functions related to dasy sw path handling and finding dasy a2l path
"""

import glob
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import zipfile
import argparse


def get_latest_dir(dpc_build_no, dasy_variant):
    """
    gets the sw path in the given artifactory in the nightly release artifactory path

    Args:
      dpc_build_no (int): directory name i.e build number

    Returns:
        str: sw path

    """
    remote_path = r"\\abtvdfs2.de.bosch.com\ismdfs\iad\DACore\artifacts\nightly-release"
    list_of_dirs = glob.glob(rf"{remote_path}\*")

    if dpc_build_no!=None:
        latest_dir = remote_path + "\\" + str(dpc_build_no).strip()
    else:
        latest_dir = max(list_of_dirs, key=os.path.getctime)
    
    try:
        if dasy_variant == 'DPCdelta1':
            os.chdir(latest_dir + r'\DASY_dpc_apl_dev')
        elif dasy_variant == 'DPCdelta5':
            os.chdir(latest_dir + r'\DASY_dpc_delta_5')
        else:
            logger.error(f"Invalid variant passed please check parameters")
            sys.exit(-1)
    except FileNotFoundError as e:
        logger.error(f"DASY_dpc_apl_dev folder not found in latest artifact -> {latest_dir}")
        raise Exception(f"DASY_dpc_apl_dev folder not found in latest artifact -> {latest_dir}")
    sw_full_path = os.getcwd()
    return sw_full_path, latest_dir


def extract_dast_sw(path, zip_pattern):
    """
    get dasy sw path from the zip file and extracts the zip file

    Args:
      path (str): path where the zip file is present
      zip_pattern (str): zip file name pattern to search

    Returns:

    """
    extract_dir = r'D:\Jenkins\ADAS_Platform\SW_Release\Dasy'
    file_list = os.listdir(path)
    zip_file_found = False
    for sw_zip in file_list:
        if zip_pattern in sw_zip:
            try:
                zip_file_found = True
                zip_full_path = os.getcwd() + '\\' + sw_zip
                with zipfile.ZipFile(zip_full_path, 'r') as zip_ref:
                    logger.info(f"Start extracting dasy_sw_path#:#{zip_full_path}#:#")
                    zip_ref.extractall(extract_dir)
                    logger.info("Extracting of the latest Dasy SW was successful")
            except Exception as e:
                raise e
    if zip_file_found == False:
        logger.error(f"Dasy ZIP file not found with pattern {zip_pattern} at {path}")
        raise Exception(f"Dasy ZIP file not found with pattern {zip_pattern} at {path}")

def download_main(dasy_variant, par_vtc_BuildNo, dpc_build_no=None):
    """
    main function for this file, main idea is to get the dasy sw path

    Args:
      par_vtc_BuildNo: parvtc build number
      dpc_build_no (int/None):  (Default value = None) if particular build number is needed in nightly release artifactory

    Returns:

    """
    if par_vtc_BuildNo != None:
        # for par vtc build path
        if dasy_variant == "DPCdelta1":
            folder_name = "DASY_dpc_delta_1"
        elif dasy_variant == "DPCdelta5":
            folder_name == "DASY_dpc_delta_5"
        else:
            logger.error(f"invalid variant is passed --> {dasy_variant}")
        remote_path = r"\\abtvdfs2.de.bosch.com\ismdfs\iad\DACore\artifacts\par-vtc\\" + str(par_vtc_BuildNo).strip() + rf'\{folder_name}'
        try:
            os.chdir(remote_path)
            #zip_pattern = "DASY_DPC_APL_DEV"
        except FileNotFoundError as e:
            raise Exception(f"\n-> {e} \n-> DASY_DPC_APL_DEV or DASY_DPC_APL folder not found or build no. path not found")

        sw_full_path = os.getcwd()
        if dasy_variant == "DPCdelta1":
            zip_pattern = rf"SysC_DPC_DELTA1_nightly-release_{latest_build_no}_DASY_dpc_apl_dev_TC397XL_BC.zip"
        elif dasy_variant == "DPCdelta5":
            zip_pattern == rf"SysC_DPC_DELTA_5_nightly-release_{latest_build_no}_DASY_dpc_delta_5_TC397XL_BC.zip"
        extract_dast_sw(sw_full_path, zip_pattern)
    else:
        # for OD_nightly-release
        sw_path, latest_build_no = get_latest_dir(dpc_build_no, dasy_variant)
        latest_build_no = latest_build_no.replace('\\', '_').split("_")[-1]
        if dasy_variant == "DPCdelta1":
            zip_pattern = rf"SysC_DPC_DELTA1_nightly-release_{latest_build_no}_DASY_dpc_apl_dev_TC397XL_BC.zip"
        elif dasy_variant == "DPCdelta5":
            zip_pattern = rf"SysC_DPC_DELTA_5_nightly-release_{latest_build_no}_DASY_dpc_delta_5_TC397XL_BC.zip"
        else:
            logger.error(f"invalid variant is passed --> {dasy_variant}")
        extract_dast_sw(sw_path, zip_pattern)


if __name__ == '__main__':
    try:
        # parse command line arguments
        commandLineParser = argparse.ArgumentParser(description='Dasy sw path DPC CI')
        commandLineParser.add_argument('--variant', action="store", dest="variant", required=True,
                                    default=None, help="dasy variant")
        commandLineParser.add_argument('--build_number', action="store", dest="par_vtc_buildNumber", required=False,
                                    default=None, help="build number of par vtc build for DASy sw path")
        

        commandLineParser.add_argument('--release_build_no', action="store", dest="release_build_no", required=False,default=None,
                                    help="dpc ci nightly release build number")
        
        arguments = commandLineParser.parse_args()

        dasy_variant = arguments.variant

        dpc_build_no = arguments.release_build_no   # dpc nightly release build number can be given from jenkins else latest folder will be considered from arifactory

        par_vtc_BuildNo = arguments.par_vtc_buildNumber   #this is par-vtc OD job build number

        download_main(dasy_variant, par_vtc_BuildNo, dpc_build_no=dpc_build_no)
    except Exception as e:
        logger.error(f"Error in dasy sw extraction -> {e}")
        raise e



