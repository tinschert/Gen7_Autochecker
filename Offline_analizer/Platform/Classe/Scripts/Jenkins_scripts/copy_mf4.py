# -*- coding: utf-8 -*-
# @file copy_mf4.py
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


if __name__ == '__main__':
    copy_mf4(r"D:\Jenkins\ADAS_Platform\Platform\Classe\Scripts\Control")


