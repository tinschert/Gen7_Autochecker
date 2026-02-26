# -*- coding: utf-8 -*-
# @file report_handler.py
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


import os
import pathlib
import re
from re import sub
import time
import datetime as dt
from zipfile import ZipFile, ZIP_DEFLATED
from linux_client import ExecClient
from test_parameters import TestParameters

# transferinfo = {
#                 "remote_evald_report": "/home/sya9lr/GIT_Workspace/OD_PSA_Testing/evald_report",  # this was used for debug
#                 "remote_mf4_path": "/home/sya9lr/GIT_Workspace/OD_PSA_Testing/measurementsmountfromcanoesystemuser/TC_111111.mf4",  # this was used for debug
#                 "local_results_path": "D:\\CloeSmokeTests\\"
#                 }


class ReportHandler:

    def __init__(self, connection_obj, **transfer_info):
    """
    This class takes two params --> a connection object, used to find linux stuff
            and a dict with the hardcoded paths to the local result

    Args:

    Returns:

    """
        self.connection_obj = connection_obj
        self.local_results_path = transfer_info["local_results_path"]
        self.local_report_path = transfer_info["local_results_path"] + "last_report\\"  # this will be a hardcoded path somewhere in the Bosch servers
        self.remote_mf4_path = self.connection_obj.find("measurementsmountfromcanoesystemuser").strip()
        self.remote_report_path = self.connection_obj.find("evald_report").strip()
        if self.remote_report_path == "":
            self.remote_report_path = sub("measurementsmountfromcanoesystemuser", "evald_report", self.remote_mf4_path)
        self.renamed_report = ""

    def transfer_report_from_linux2local(self):
        """Copy evald report from linux host to a windows appointed location"""

        try:
            evald_dir = self.remote_report_path
            for dir_item in self.connection_obj.list_dir(self.remote_report_path.strip()):
                if dir_item == "plot":
                    plot_dir = self.connection_obj.list_dir(evald_dir.strip() + "/plot")
                    for plot_item in plot_dir:
                        self.connection_obj.get_file(evald_dir.strip() + "/plot/" + plot_item, self.local_report_path + "\\plot\\")
                else:
                    self.connection_obj.get_file(evald_dir.strip() + "/" + dir_item, self.local_report_path)
        except Exception as e:
            raise e

    @staticmethod
    def compress_mf4_log(dir_path, mf4_name):
        """
        

        Args:
          dir_path: 
          mf4_name: 

        Returns:

        """
        windows_path = pathlib.Path(dir_path)
        mf4_path = dir_path + mf4_name
        win_mf4_path = pathlib.Path(mf4_path)
        mf4_zip = re.sub("\\.mf4", ".zip", mf4_path)
        try:
            with ZipFile(mf4_zip, 'w', ZIP_DEFLATED, compresslevel=9) as zf:
                zf.write(win_mf4_path, arcname=win_mf4_path.relative_to(windows_path))
        except FileNotFoundError:
            print(f"MF4 log not found")
        else:
            os.remove(mf4_path)

    def transfer_mf4_from_linux2local(self, mf4_id, local_path):
        """
        Copy MF4 log from linux host to a windows appointed location

        Args:
          mf4_id: 
          local_path: 

        Returns:

        """
        # We will need the test name (for example TC_111111 + .mf4)
        # We get this info after we have analyzed the report
        try:
            mf4_dir = self.connection_obj.list_dir(self.remote_mf4_path)  # list the items of the report folder
            for mf4_log in mf4_dir:
                if mf4_log == mf4_id:  # if mf4 log is found
                    self.connection_obj.get_file(self.remote_mf4_path + '/' + mf4_log, local_path)
                    break
        except Exception as e:
            print(f"copy failed. Reason = {e}")

    def rename_report_folder(self, rename_to_what):
        """
        Renames the copied report folder and returns the name of the

        Args:
          rename_to_what: 

        Returns:

        """
        if os.path.exists(self.local_results_path + rename_to_what):
            time_now = str(time.strftime("%Hh%Mm%Ss"))
            os.rename(self.local_report_path, self.local_results_path + rename_to_what + "_old_" + time_now)
            self.renamed_report = self.local_results_path + rename_to_what + "_old_" + time_now
        else:
            os.rename(self.local_report_path, self.local_results_path + rename_to_what)
            self.renamed_report = self.local_results_path + rename_to_what


def copy_report_to_test_run_folder(test_run_folder_name, tool_results_folder_path, renamed_report, test_status):  # 2, 1, 4, 3
    """
    

    Args:
      test_run_folder_name: 
      tool_results_folder_path: 
      renamed_report: 
      test_status: 

    Returns:

    """
    if test_status == 'Passed':
        move_command = "move" + " " + renamed_report + " " + tool_results_folder_path + test_run_folder_name + "\\passed"
        os.system(move_command)
    if test_status == 'Failed':
        move_command = "move" + " " + renamed_report + " " + tool_results_folder_path + test_run_folder_name + "\\failed"
        os.system(move_command)
    if test_status == 'Skipped':
        move_command = "move" + " " + renamed_report + " " + tool_results_folder_path + test_run_folder_name + "\\skipped"
        os.system(move_command)


def name_the_tc_run_folder():
    """ """
    date_now = str(dt.date.today()) + "_"
    time_now = str(time.strftime("%Hh%Mm%Ss"))
    testrun_name = "tc_run_" + date_now + time_now
    return testrun_name


def create_test_results_folder(local_results_path, tc_run_folder_name):
    """
    Creates a test run folder in 'local_results_path'

    Args:
      local_results_path: 
      tc_run_folder_name: 

    Returns:

    """

    if not os.path.exists(local_results_path):  # create the folder 'Reports_from_Test_Execution_Tool' if it does not already exist
        try:
            os.system("mkdir " + local_results_path)
        except Exception as e:
            raise e
    if not os.path.exists(local_results_path + tc_run_folder_name + "\\"):  # create the folder 'exp_tc_run' in 'Reports_from_Test_Execution_Tool' if it does not already exist
        try:
            os.system("mkdir " + local_results_path + tc_run_folder_name + "\\")
        except Exception as e:
            raise e
    try:
        os.system("mkdir " + local_results_path + tc_run_folder_name + "\\" + "passed")
        os.system("mkdir " + local_results_path + tc_run_folder_name + "\\" + "failed")
        os.system("mkdir " + local_results_path + tc_run_folder_name + "\\" + "skipped")
    except Exception as e:
        print("Some error?")
        raise e

