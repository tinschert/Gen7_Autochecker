# -*- coding: utf-8 -*-
# @file sw_versions_extractor.py
# @author ADAS_HIL_TEAM
# @date 09-11-2023

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


from win32api import GetFileVersionInfo, LOWORD, HIWORD
import os, sys
import subprocess,io
from itertools import chain
import gitinfo
import socket
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\..\Control")
from logging_config import logger

list_of_sw = ('CANoe64.exe', "CANape64.exe", "vTESTstudio.exe", "VXconfig.exe")


def get_canoe_commit() -> list:
    """ """
    git_repo_summary = gitinfo.get_git_info()
    git_repo_data = [(key, value) for key, value in git_repo_summary.items()]
    return git_repo_data


def get_sw_paths():
    """ """
    sw_paths = []
    prg_files_path = [r"C:\Program Files", r"C:\Program Files (x86)"]
    for path, subdirs, files in chain.from_iterable(os.walk(path) for path in prg_files_path):
        for name in files:
            if name.endswith(list_of_sw):
                sw_paths.append(os.path.join(path, name))
    return sw_paths


def get_version_number(filename):
    """
    

    Args:
      filename: 

    Returns:

    """
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
    except:
        return "Unknown version"


def get_hostnames():
    """ """
    domains_list = []
    hils_dict = {
        "FE-Z1R59.lr.de.bosch.com": "FE-C-00968.lr.de.bosch.com",
        "FE-C-005CP.lr.de.bosch.com": "LR-C-002FV.lr.de.bosch.com",
        "WE-C-0003R.lr.de.bosch.com": "LR-C-002MR.lr.de.bosch.com",
        "FE-Z1VJ4.fe.de.bosch.com": "ABT-C-000KJ.fe.de.bosch.com",
        # "FE-Z1VJ4.fe.de.bosch.com": "LR-Z10002.fe.de.bosch.com",
        "fe-c-005dl.fe.de.bosch.com": "FE-Z1VXQ.fe.de.bosch.com",
        "ABTZ0NQC.abt.de.bosch.com": "ABT-C-000KK.abt.de.bosch.com"
    }

    win_hostname = socket.gethostname()
    win_ip = socket.gethostbyname(win_hostname)
    domains_list.append(f"Windows GUI PC domain/IP = {win_hostname}[{win_ip}]{new_line}")

    if win_hostname in hils_dict:
        try:
            linux_hostname = hils_dict[win_hostname]
            linux_ip = socket.gethostbyname(linux_hostname)
            domains_list.append(f"Linux PC domain/IP = {linux_hostname}[{linux_ip}]")
            return domains_list
        except Exception as e:
            logger.warning(f"Unable to get Linux IP address --> {e}")
    else:
        logger.warning("Unknown windows GUI PC")


def get_project():
    """ """
    projects = ["PSA", "OD", "FORD"]
    main_repo_path = os.path.dirname(os.path.abspath(__file__)) + '/../../../..'
    for (dirpath, dirnames, filenames) in os.walk(main_repo_path):
        for file in filenames:
            if ".cfg" in file:
                found_file = str(file).split(".")[0]
                project = found_file.split('_')[1]
                logger.info(f"Local repository project is --> {project}")
                return project


if __name__ == "__main__":
    text = []
    new_line = "\n"

    """ Retrieve project """
    text.append(40 * "#" + " Current project " + 40 * "#" + "\n")
    project_name = get_project()
    text.append(f"Project is {project_name}{new_line}")

    """ Retrieve Vector software versions """
    logger.info("Retrieve Vector software installation paths and versions")
    paths = get_sw_paths()
    text.append(40 * "#" + " Vector Software " + 40 * "#" + "\n")
    for key in paths:
        version = ".".join([str(i) for i in get_version_number(key)])
        text.append(f"PATH = {key} [{version}]{new_line}")

    """ Retrieve Python Version and Libraries """
    logger.info("Retrieve Python version and libraries")
    text.append("\n" + 40 * "#" + " Python Version and Libraries " + 40 * "#" + "\n")
    text.append(f"Current Python Version: {sys.version}{new_line}")
    process = subprocess.Popen(["X:\Tools\venv\Scripts\python.exe", "-m", "pip", "list"], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        text.append(line)

    """ Retrieve Canoe Repo current working commit """
    logger.info("Retrieve Canoe repo current working commit information")
    text.append("\n" + 40 * "#" + " CANoe repo commit " + 40 * "#" + "\n")
    repo_data = get_canoe_commit()
    for data in repo_data:
        text.append(f'{data[0]} = {data[1]}{new_line}')

    """ Retrieve Windows GUI pc domain/IP and linux domain/IP address """
    logger.info("Retrieve Windows GUI pc domain/IP and linux domain/IP address")
    text.append("\n" + 40 * "#" + " GUI PC and Linux PC hostnames/ip " + 40 * "#" + "\n")
    hosts_data = get_hostnames()
    text.extend(hosts_data)

    """ Write the log file """
    logger.info("Write the log file")
    test_to_write = "".join(text)
    with open(r"D:\ADAS_HIL_info.txt", "w") as f:
        f.write(test_to_write)
    logger.info(r"Please find the log in D:\ADAS_HIL_info.txt")



