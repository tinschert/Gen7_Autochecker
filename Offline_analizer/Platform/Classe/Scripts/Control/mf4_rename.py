# -*- coding: utf-8 -*-
# @file mf4_rename.py
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


import asammdf
import os
import sys


def rename_mf4_traces():
    """ Renames all mf4 files in a defied directory based on FDX_in_HIL_specific_input_triggers::FDX_in_TestCaseID value"""
    path = sys.argv[1]
    fdx_tc_id_name = "FDX_in_HIL_specific_input_triggers::FDX_in_TestCaseID"

    mf4_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for file in filenames:
            if ".mf4" in file:
                mf4_files.append(file)
        print(f"Found MF4 file/s --> {mf4_files}")
    if mf4_files:
        for mf4 in mf4_files:
            tc_id = int()
            with asammdf.MDF(f"{path}\{mf4}") as mdf:
                for sig in mdf.iter_channels():
                    if fdx_tc_id_name in sig.name:
                        tc_id = int(list(sig.samples)[-1])
                        print(f"{mf4} {fdx_tc_id_name} = {tc_id}")
            if tc_id != 0:
                try:
                    new_name = f"{path}\TC_{tc_id}.mf4"
                    os.rename(f"{path}\{mf4}", new_name)
                    print(f"Renamed {mf4} to {new_name}")
                except Exception as e:
                    print(f"MF4 file renaming failed due to --> {e}")
                    raise e
            else:
                print(f"FDX_in_HIL_specific_input_triggers::FDX_in_TestCaseID not found in {mf4}")


if __name__ == "__main__":
    rename_mf4_traces()
