import argparse
import re
import os, sys
import pandas as pd
import time
import shutil
import subprocess
import pythoncom
from openpyxl import load_workbook
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\..\..\..\..\Platform\Classe\Scripts\Jenkins_scripts")

from update_xcp_configuration import update_xcpconfig, get_paths_dasy

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\..\Control")
from logging_config import logger

def main(ecus, folder_name):
    dasy_delta1_a2l_path = None
    dasy_delta5_a2l_path = None
    alpha2_radar_fc_a2l_path = None
    radar_fc_a2l_path_loc = None
    radar_corner_a2l_path = None
    dasy_a2l_path = None
    customer = "OD"

    container_path = r"D:\_Temp_Baseline_Container"
    for ecu in ecus.split(" "):
        ecu = ecu.strip().lower()
        if ecu == "delta1":
            dasy_sw_path = container_path + rf"\{folder_name}" + r"\DASY"
            dasy_delta1_sw_path  = None
            if os.path.exists(dasy_sw_path):
                for sub_dir in os.listdir(dasy_sw_path):
                    full_sub_dir_path = os.path.join(dasy_sw_path, sub_dir)
                    if os.path.isdir(full_sub_dir_path) and 'delta1' in sub_dir.lower():
                        dasy_delta1_sw_path = full_sub_dir_path
                        break
                if dasy_delta1_sw_path != None:
                    for root, dirs, files in os.walk(dasy_delta1_sw_path):
                        for name in dirs:
                            if "measurement_golf" in name.lower():
                                measurement_path = os.path.join(root, name)
                                delta1_a2l_folder_path = measurement_path + r"\database\a2l"
                                break
                    for root, dirs, files in os.walk(delta1_a2l_folder_path):
                        for name in files:
                            if ".a2l" in name.lower() and "reduced" not in name.lower():
                                dasy_delta1_a2l_path = delta1_a2l_folder_path + "\\" + name
                else:
                    logger.warning(f"delta1 folder not found in {dasy_sw_path}")
        if ecu == "delta5":
            dasy_sw_path = container_path + rf"\{folder_name}" + r"\DASY"
            dasy_delta5_sw_path = None
            if os.path.exists(dasy_sw_path):
                for sub_dir in os.listdir(dasy_sw_path):
                    full_sub_dir_path = os.path.join(dasy_sw_path, sub_dir)
                    if os.path.isdir(full_sub_dir_path) and 'delta_5' in sub_dir.lower():
                        dasy_delta5_sw_path = full_sub_dir_path
                        break
                if dasy_delta5_sw_path != None:
                    for root, dirs, files in os.walk(dasy_delta5_sw_path):
                        for name in dirs:
                            if "measurement_golf" in name.lower():
                                measurement_path = os.path.join(root, name)
                                delta5_a2l_folder_path = measurement_path + r"\database\a2l"
                                break
                    for root, dirs, files in os.walk(delta5_a2l_folder_path):
                        for name in files:
                            if ".a2l" in name.lower() and "reduced" not in name.lower():
                                dasy_delta5_a2l_path = delta5_a2l_folder_path + "\\" + name
                else:
                    logger.warning(f"delta5 folder not found in {dasy_sw_path}")
        if ecu == "alpha2":
            dasy_sw_path = container_path + rf"\{folder_name}" + r"\FR5"
            alpha2_sw_path = None
            if os.path.exists(dasy_sw_path):
                for sub_dir in os.listdir(dasy_sw_path):
                    full_sub_dir_path = os.path.join(dasy_sw_path, sub_dir)
                    if os.path.isdir(full_sub_dir_path) and 'alpha_2' in sub_dir.lower():
                        alpha2_sw_path = full_sub_dir_path
                        break
                if alpha2_sw_path != None:
                    for root, dirs, files in os.walk(alpha2_sw_path):
                        for name in dirs:
                            if "measurement_golf" in name.lower():
                                measurement_path = os.path.join(root, name)
                                alpha2_a2l_folder_path = measurement_path + r"\database\a2l"
                                break
                    for root, dirs, files in os.walk(alpha2_a2l_folder_path):
                        for name in files:
                            if ".a2l" in name.lower() and "reduced" not in name.lower():
                                alpha2_radar_fc_a2l_path = alpha2_a2l_folder_path + "\\" + name
                else:
                    logger.warning(f"alpha2 folder not found in {dasy_sw_path}")
    
    update_xcpconfig(radar_fc_a2l_path_loc, alpha2_radar_fc_a2l_path, radar_corner_a2l_path, customer, dasy_a2l_path,
                     dasy_delta1_a2l_path, dasy_delta5_a2l_path)

if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated fix of A2L file with Canape.')
    commandLineParser.add_argument('--ecus', action="store", dest="ecus", required=True,
                                   help="ecu args to be flashed")
    commandLineParser.add_argument('--folder_name', action="store", dest="folder_name", required=True,
                                   help="name of the folder where database container ectracted")
    arguments = commandLineParser.parse_args()
    ecus = str(arguments.ecus).strip()
    folder_name = arguments.folder_name
    if not(ecus):
        logger.warning("-------No ECUs were given as arguement for flashing-----------")
    else:
        main(ecus, folder_name)