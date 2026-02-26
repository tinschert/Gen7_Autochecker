# -*- coding: utf-8 -*-
# @file python_func_docstring_templete_appender.py
# @author ADAS_HIL_TEAM
# @date 11-14-2023

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
this file is used for adding comment/docstring templete for all python functions in given path
"""

import os
import subprocess

script_path = os.path.dirname(os.path.abspath(__file__))
adas_hil_repo_path = script_path + r"\\..\\..\\..\\.."


# #testing
# adas_hil_repo_path = r"C:\GIT_WORKSPACE\AD_HIL"

FILE_PATTERN = ".py"

def append_docstring_templete():
    """adds docstring templete"""

    for (dirpath, dirnames, filenames) in os.walk(adas_hil_repo_path):
        for file in filenames:
            if file.endswith(FILE_PATTERN):
                try:
                    command = f'pyment -w -o google -f false {file}'
                    result = subprocess.check_output(command, shell=True, cwd=dirpath).decode('utf-8')
                    print(f"converted -> {file}")
                except Exception as e:
                    print(f"Error while processing -> {file} -> {e}")

if __name__ == "__main__":
    append_docstring_templete()
