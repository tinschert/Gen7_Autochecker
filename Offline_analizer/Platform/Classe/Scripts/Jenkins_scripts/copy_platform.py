# -*- coding: utf-8 -*-
# @file copy_platform.py
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
import os,sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import shutil


def copy_mf4(project_path):
    """
    

    Args:
      project_path: 

    Returns:

    """
    try:
        logger.info("Copy mf4_rename.exe to local repository")
        shutil.copy(
            r'\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\mf4_rename.exe',
            project_path)
    except PermissionError as e:
        logger.info(f"Permission denied to access mf4_rename.exe --> {e}")
        raise e
    except Exception as e:
        logger.info(f"Failed to copy mf4_rename.exe --> {e}")
        raise e


def copy_platform(source, target):
    """
    

    Args:
      source: 
      target: 

    Returns:

    """
    if not os.path.isdir(source):
        raise Exception(f"Platform repository {source} does not exist")
    else:
        if target != '':
            if not os.path.isdir(target):
                raise Exception(f"Customer branch repository path {target} does not exist")
            else:
                try:
                    shutil.copytree(source, target,
                                    ignore=shutil.ignore_patterns('CustomerPrj', '*.stcfg', '*.cfg', '.git',
                                                                  '.idea', '.run', '*.local'),
                                    dirs_exist_ok=True)
                    logger.info(f"Latest Platform copied from {source} to {target}")
                except Exception as e:
                    logger.error(f"Exception raised during copying from from {source} to {target} --> {e}")
                    raise e
                copy_mf4(target + r"\Platform\Classe\Scripts\Control")


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated RBS script for copying platform into customer.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    arguments = commandLineParser.parse_args()

    platform_path = r"D:\Jenkins\ADAS_Platform"
    if arguments.customer_path != platform_path:
        copy_platform(platform_path, arguments.customer_path)


