# -*- coding: utf-8 -*-
# @file start_cm_without_RT_rack.py
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


from pathlib import Path
import subprocess
import sys


def start_carmaker():
    """ """
    path = Path(__file__).parent / "../../../../adas_sim/cm_project"
    #path = r"D:\adas_hil_CM\adas_sim\cm_project\CANoe_Test"
    p = subprocess.Popen(["CM.exe", path, "-start"], shell=True, cwd=r'C:\IPG\carmaker\win64-11.1\bin', stdout=sys.stdout)
    p.communicate()


def start_ipgmovie():
    """ """
    p = subprocess.Popen(["Movie.exe"], shell=True, cwd=r'C:\IPG\carmaker\win64-11.1\GUI', stdout=sys.stdout)
    p.communicate()


if __name__ == "__main__":
    start_carmaker()
    start_ipgmovie()

