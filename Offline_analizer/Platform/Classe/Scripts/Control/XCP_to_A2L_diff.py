# -*- coding: utf-8 -*-
# @file XCP_to_A2L_diff.py
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


import pandas as pd
# Set the option to opt-in to the future behavior
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import os, sys

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.getcwd() + r"\..\Control")
    from logging_config import logger
import numpy as np
from itertools import islice
import fileinput
from openpyxl import load_workbook
from distutils.file_util import copy_file
import xml.etree.ElementTree as ET


class XCPConfigurator:
    """ Main class"""

    def __init__(self, a2l_file):
        self.a2l_file = a2l_file
        self.a2lfile_missvar = {}

    def parseFDX_evald(self, path_fdx=r'..\..\..\..\CustomerPrj\FDX\FDX_Database.xlsx'):
        """
        Function to extract the signals from FXD_Database.xlsx fdxChecksDatabase sheet
        Args
            path_fdx (str) : Path to the FDX_Database.xlsx
        Returns
            List of all XCP variables (list)

        Args:
          path_fdx:  (Default value = r'..\\..\\..\\..\\CustomerPrj\\FDX\\FDX_Database.xlsx')

        Returns:

        """

        final_signal_list = []
        df = pd.read_excel(path_fdx, sheet_name='fdxChecksDatabase', na_values=['NA'], usecols='B:B')
        signal_list = df['A2L_mapped_Name'].tolist()
        for signals in signal_list:
            if signals != 'not_found':
                final_signal_list.append(signals)
        logger.info("Step 1 --> FDX_Databse XCP list generated")
        return set(final_signal_list)

    def sanityCheck(self, path_xcp, columns):
        """
        Function to check the consistency of XCP database

        Args:
          path_xcp (str): Path to the XCP_Database.xlsx
          columns (list): Columns to be checked

        Returns:
        """
        logger.info("++++ Start XCP_Database sanity check ++++")

        dasy_empty_col_list = ["num_iteration", "Message", "stimTrigger", "stimCalibration"]  # if dasy in sheet name
        radar_empty_col_list = ["num_iteration", "Message"]  # if radar in sheet name

        empty_cols = ["num_iteration"]  # default if no dasy or radar in sheet name

        error = False
        d_type = {'Name': str, 'Message': str, 'autoread': str, 'read': str, 'stimEnabled': str, 'stimTriggerUsed': str}

        try:
            df = pd.ExcelFile(path_xcp)
        except Exception as e:
            logger.error(f"Failed to load XCP_database.xlsx for sanity check -> {e}")
            return
            # raise Exception(f"Failed to load XCP_database.xlsx for sanity check {e}")

        sheet_names = df.sheet_names
        if sheet_names == []:
            logger.error(f"No sheets in XCP_database.xlsx for sanity check -> {e}")
            return
        output = "XCP_Database.xlsx : sheet - {} : column - {} : row - {} : {}"

        dasy_list = ["xcp_Dasy", "xcp_DPCdelta1", "xcp_DPCdelta5"]
        radar_list = ["xcp_RPCgamma1", "xcp_RPCalpha2", "xcp_RadarFL", "xcp_RadarFR", "xcp_RadarRL", "xcp_RadarRR",
                      "xcp_RadarFC"]
        for st in sheet_names:  # iterate sheets
            if str(st) in radar_list:
                empty_cols = radar_empty_col_list
            elif str(st) in dasy_list:
                empty_cols = dasy_empty_col_list
            no_empty_cols = [i for i in columns if i not in empty_cols]

            try:
                df_temp = df.parse(st, usecols=columns, dtype=d_type, na_filter=False)
            except Exception as e:
                logger.error(f"Failed to load XCP_database.xlsx sheet", st, " for sanity check -> {e}")
                return
                # raise Exception(f"Failed to load XCP_database.xlsx sheet for sanity check {e}")

            if not (df_temp.empty):  # check if sheet is empty
                for row in df_temp.iterrows():  # iterate rows in the sheet
                    if len(set(row[1].values)) == 1:
                        continue
                    if (len(row), len(row[1])) != (2, len(columns)):  # just checking to avoid errors
                        logger.error(f"Error while parsing ", st, " in XCP_Database.xlsx for sanity check")
                        return
                    if (str(row[1]["num_iteration"]).strip() != "") and ("[0…n]" not in str(
                            row[1]["Message"])):  # check if [0…n] is present when there is num_iteration
                        logger.error(output.format(st, "Message", row[0] + 2, "[0…n] pattern error"))
                        error = output.format(st, "Message", row[0] + 2, "[0…n] pattern error")

                    for col in no_empty_cols:
                        if str(row[1][col]).strip() == "":  # check if a cell is empty
                            logger.error(output.format(st, col, row[0] + 2, "empty cell"))
                            error = output.format(st, col, row[0] + 2, "empty cell")
                        elif (str(row[1][col]).strip() != str(row[1][col])):  # check if cell contains extra spaces
                            logger.error(output.format(st, col, row[0] + 2, "extra space found"))
                            error = output.format(st, col, row[0] + 2, "extra space found")
        if error:
            raise Exception("Sanity Check failed :: " + error + ", check console output for more error info")
        df.close()
        logger.info("++++ Done XCP_Database sanity check -> ALL OK  ++++")

    def parseXCP(self, ecu, path_xcp=r'..\..\..\..\CustomerPrj\XCP\XCP_Database.xlsx', all_data=True):
        """
        Function to extract the XCP variables from XCP_Database.xlsx
        Args
            path_xcp (str) : Path to the XCP_Database.xlsx
        Returns
            List of all XCP variables for FC and FR (list)

        Args:
          ecu: 
          path_xcp:  (Default value = r'..\\..\\..\\..\\CustomerPrj\\XCP\\XCP_Database.xlsx')
          all_data:  (Default value = True)

        Returns:

        """

        columns = ['Name', 'num_iteration', 'Message', 'autoread', 'read', 'cycle', 'stimEnabled', 'stimTriggerUsed',
                   'stimTrigger', 'stimCalibration']

        # call sanity check
        self.sanityCheck(path_xcp, columns)

        try:
            data = self.get_excel_xcp_data(path_xcp, ecu, columns)
            logger.info(f"{ecu} variables list generated")
            return data
        except Exception as e:
            logger.error(f"Parsing {ecu} variables failed due to --> {e}")
            raise Exception(f"Parsing {ecu} variables failed due to --> {e}")

    def get_excel_xcp_data(self, path_excel, sheet_name, columns):
        """
        Extract data from XCP_Database.xlsx

        Args:
          path_excel (str): Path to Excel database
          sheet_name (sheet): Sheet name
          columns (list) : Columns to be taken into account

        Returns:
        """
        df_main = pd.read_excel(path_excel, sheet_name=sheet_name, na_values=['nan'], usecols=columns)
        xcp_list = df_main.values
        return self.update_num_of_targets(xcp_list)

    def update_num_of_targets(self, targets_list):
        """
        Function to update the single '[0…n]' string into multiple targets
        Args
            targets_list (ndarray) : list of xcp variables that should be updated
        Returns
            List of all XCP variables updated (ndarray)

        Args:
          targets_list: 

        Returns:

        """

        targets_string = '[0…n]'
        new_target_list = []

        try:
            for xcp_signal in targets_list:
                if str(xcp_signal[0]) != 'nan':
                    targets = xcp_signal[1]
                    if str(xcp_signal[2]) != 'nan':
                        if targets_string in xcp_signal[2] and str(targets) != 'nan':
                            updated_targets = []
                            targets_int = int(targets)
                            for n in range(targets_int):
                                cloned_xcp = xcp_signal.copy()
                                updated_targets.append(cloned_xcp)
                            for n in range(targets_int):
                                upd_target = updated_targets[n][2].replace(targets_string, str(n))
                                updated_targets[n][2] = upd_target
                            new_target_list.extend(updated_targets)
                        else:
                            new_target_list.append(xcp_signal)
                    else:
                        new_target_list.append(xcp_signal)
            return new_target_list
        except Exception as e:
            logger.error(f"Failed updating the targets --> {e}")

    def extract_A2l(self, a2l_file):
        """
        Function to extract A2L file entries as list

        Args:
          a2l_file (str): A2L file to extracted

        Returns:
        """
        new_list = []
        with open(f"{a2l_file}", 'r') as f:
            lines = f.readlines()
            for x in lines:
                if x.startswith("    /begin MEASUREMENT") or x.startswith("    /begin CHARACTERISTIC"):
                    new_list.append(x)
        logger.info(f"XCP list generated from {a2l_file}")
        return new_list

    def parseA2l(self, a2l_File, xcp_list, a2l_signals):
        """
        Function to compare signal list from XCP_Database.xlsx with A2L file

        Args:
          a2l_File (str): Path to the a2l file
          xcp_list (list): XCP list extract
          a2l_signals (list): All a2l signals

        Returns:
        """
        file_path = os.path.dirname(os.path.realpath(__file__))
        not_found = []

        for xcp_var in xcp_list:
            if str(xcp_var[2]) == "nan":
                xcp_v = ""
            else:
                xcp_v = xcp_var[2]

            if any((xcp_v + xcp_var[0]) in s for s in a2l_signals):
                continue
            else:
                not_found.append(xcp_v + xcp_var[0])

        if not_found:
            not_found.insert(0, "\nA2l file -> " + a2l_File + ", \nMissing XCP Variables are -> \n")
            not_found.append('-' * 200)
            joined_string = "\n".join(not_found)
            if a2l_File in self.a2lfile_missvar.keys():
                if joined_string not in self.a2lfile_missvar[a2l_File]:
                    self.a2lfile_missvar[a2l_File].append(joined_string)
            else:
                self.a2lfile_missvar[a2l_File] = joined_string

            with open(f"{file_path}\\Missing_XCP_variables_in_A2L.txt", 'a') as f:
                f.write(joined_string)
            logger.error(f"========= XCP variables NOT found in A2L ===========")
            logger.error(f"{joined_string}")
            # raise Exception("Missing XCP variables")
            return
        else:
            logger.info("All XCP_Database.xlsx XCP entries are part of A2L file")

    def parseXCPconfig(self, xcp_config):
        """
        Function extract xcp variables available in CanOE XCP config file

        Args:
          xcp_config (str) : Path to the XCP config file

        Returns:
        """

        conf_xcp = list()
        with open(f"{xcp_config}", 'r') as f:
            line = f.readline()

            while line:
                stripped = line.lstrip()
                if stripped.startswith('<signal enabled'):
                    conf_xcp.append(line.rstrip('"  />\n').split('name="')[1])
                    line = f.readline()
                else:
                    line = f.readline()
        # print(*conf_xcp, sep='\n')
        return conf_xcp

    def parseXCPconfig2(self, xcp_config, ecu_index):
        """
        Function extract xcp variables available in CanOE XCP config file

        Args:
          xcp_config (str): Path to the XCP config file
          ecu_index (str): ECU index to searching for

        Returns:
        """

        conf_xcp = list()
        with open(f"{xcp_config}", 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if "</signals>" in line and i > ecu_index:
                    return conf_xcp
                elif i > ecu_index and stripped.startswith('<signal enabled'):
                    conf_xcp.append(line.rstrip('"  />\n').split('name="')[1])

    def xcpDiff(self, a2l_xcp, conf_xcp):
        """
        Function to compare variables available in CanOE XCP config file with A2L file

        Args:
          a2l_xcp (list): A2l file list of xcps
          conf_xcp (list): XCP config file list of xcps

        Returns:
        """
        filtered = []
        for xcp_var in conf_xcp:
            if any(xcp_var in s for s in a2l_xcp):
                result = True
            else:
                filtered.append(xcp_var)
        if not filtered:
            logger.info("Step 4 --> Old XCP config file entries found in A2L file.")
        else:
            logger.warning("Step 4 --> Found missing XCP variables in A2L file:")
            for var in filtered:
                logger.warning(var)

    def xcpDiff_excel(self, excel_xcp, conf_xcp, radar):
        """
        Function to compare variables available in CanOE XCP config file against Excel entries

        Args:
          excel_xcp (str): Path to the database
          conf_xcp (str): Path to the XCP config
          radar (str): Radar(ECU) name

        Returns:
        """

        excel_xcp_lean = []
        for xcp in excel_xcp:
            excel_xcp_lean.append(xcp[1] + xcp[0])

        filtered_list = list(set(excel_xcp_lean).difference(conf_xcp))
        filtered_list.sort()

        if not filtered_list:
            logger.info(f"\033[92m No new entries found for {radar}.XCP configuration is up-to-date. \033[00m")
        else:
            logger.warning(f"Found {len(filtered_list)} missing XCP variable(s) in config file for {radar}:")
            for var in filtered_list:
                logger.warning(var)

        filtered_list_full_info = []
        for filtered_xcp in filtered_list:
            for full_xcp_info in excel_xcp:
                if filtered_xcp == full_xcp_info[1] + full_xcp_info[0]:
                    filtered_list_full_info.append(full_xcp_info)
        return filtered_list_full_info

    def find_ECU(self, xcp_config, device_name):
        """
        Find ECU by name inside given XCP config

        Args:
          xcp_config (str) : Path to the XCP config
          device_name (str): Name of the ECU

        Returns:
        """

        with open(f"{xcp_config}", 'r') as f:
            line = f.readlines()
            x = f'<device name="{device_name}"'
            if any(x in string for string in line):
                logger.info(f"{device_name} ECU available in XCP configuration.")
                meas_index = [line.index(i) for i in line if device_name in i]
                return meas_index[0]
            else:
                logger.warning(f"{device_name} NOT available in XCP configuration")
                # raise ValueError(f"{device_name} NOT available in XCP configuration")

    def add_XCP(self, xcp_config, missing_xcp, index, ecu):
        """
        Function to add XCP in the XCP config file

        Args:
          xcp_config (str): Path to the XCP config file
          missing_xcp (str): XCP to be added
          index (str): Index of the ECU inside config file
          ecu (str): ECU name

        Returns:

        """
        string_start = "<signals>"
        stop_string = "</signals>"

        try:
            with open(f"{xcp_config}", 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if stop_string in line and i > index:
                        break
                    if index < i and string_start in line:
                        if ecu != "Dasy":
                            signal_line_radar = f'            <signal enabled="true" autoread="{str(missing_xcp[3]).lower()}" read="{missing_xcp[4]}" cycle="{int(missing_xcp[5])}" stimEnabled="{str(missing_xcp[6]).lower()}" stimTriggerUsed="{str(missing_xcp[7]).lower()}" stimTrigger="{int(missing_xcp[8])}" stimCalibration="{int(missing_xcp[9])}" name="'
                            if str(missing_xcp[2]) != 'nan':
                                lines[i] = lines[i] + f'{signal_line_radar}{missing_xcp[2]}{missing_xcp[0]}" />\n'
                            else:
                                lines[i] = lines[i] + f'{signal_line_radar}{missing_xcp[0]}" />\n'
                        else:
                            signal_line_dasy = f'            <signal enabled="true" autoread="{str(missing_xcp[3]).lower()}" read="{missing_xcp[4]}" cycle="{int(missing_xcp[5])}" stimEnabled="{str(missing_xcp[6]).lower()}" stimTriggerUsed="{str(missing_xcp[7]).lower()}" stimTrigger="{int(missing_xcp[8])}" stimCalibration="{int(missing_xcp[9])}" name="'
                            if str(missing_xcp[2]) != 'nan':
                                lines[i] = lines[i] + f'{signal_line_dasy}{missing_xcp[2]}{missing_xcp[0]}" />\n'
                            else:
                                lines[i] = lines[i] + f'{signal_line_dasy}{missing_xcp[0]}" />\n'
            with open(f"{xcp_config}", 'w') as f:
                f.writelines(lines)
        except Exception as e:
            logger.error(f"Adding new XCP variable failed --> {e}")
            raise Exception(f"Adding new XCP variable failed --> {e}")

    def extract(self, file, string, index):
        """
        Extract Measurement/Characteristic XCP from given index and name

        Args:
          file (str): Name of the file
          string (str): String to be searched
          index: Index of the string

        Returns:
        """
        try:
            return file.index(string, index, index + 13)
        except ValueError:
            return None

    def reduce_A2l(self, a2l_file, xcp_variables_conf, a2l_type, customer):
        """
        Function to reduce A2L file entries

        Args:
          a2l_file (str): Path to the a2l file
          xcp_variables_conf (str): Path to the xcp config file
          a2l_type (str): ECU name
          customer (str): Customer name

        Returns
        """

        tail_start = f"    /begin COMPU_METHOD"

        var_index = []
        head = []
        logger.info(f"Start reducing {a2l_file}.Please wait, takes around 5 minutes")
        """Get the head of the a2l file """
        try:
            with open(f"{a2l_file}", 'r') as f:
                for line in f:
                    if line.startswith(f"    /begin MEASUREMENT") or line.startswith(f"    /begin CHARACTERISTIC"):
                        break
                    else:
                        head.append(line)
            head_end_index = len(head) - 1
        except Exception as e:
            logger.error(f"Unable to get the head part of {a2l_file}.Fail reason --> {e}")
            raise Exception(f"Unable to get the head part of {a2l_file}.Fail reason --> {e}")

        """Get the index of tail part """
        with open(f"{a2l_file}", 'r') as f:
            for index, line in enumerate(f):
                if line.startswith(tail_start):
                    tail_index = index
                    break

        """Extract the tail from a2l file """
        with open(f"{a2l_file}", 'r') as f:
            tail = list(islice(f, tail_index, None))

        """Get the index of xcp variable which should be part of the new a2l """
        try:
            with open(f"{a2l_file}", 'r') as f:
                for index, line in enumerate(f):
                    if index > head_end_index:
                        if line.startswith(f"    /begin MEASUREMENT") or line.startswith(f"    /begin CHARACTERISTIC"):
                            for variable in xcp_variables_conf:
                                a2l_line_split_right = line.split('"')[0]
                                a2l_get_exact_value = a2l_line_split_right.split(" ")[-2]
                                if variable == a2l_get_exact_value:
                                    # if line.startswith(f'    /begin MEASUREMENT {variable} ""') or line.startswith(f'    /begin CHARACTERISTIC {variable} ""'):
                                    var_index.append(index)
        except Exception as e:
            logger.error(
                f"Unable to get the index of xcp variables which should be part of the new a2l.Fail reason --> {e}")
            raise Exception(
                f"Unable to get the index of xcp variables which should be part of the new a2l.Fail reason --> {e}")

        """Extract xcp variables information based on the index logic"""
        with open(f"{a2l_file}", 'r') as f:
            p = f.readlines()
            string_mes = "    /end MEASUREMENT\n"
            string_char = "    /end CHARACTERISTIC\n"
            valid_xcp = []
            for idx in var_index:
                measurement = self.extract(p, string_mes, idx)
                characteristic = self.extract(p, string_char, idx)
                if measurement is not None:
                    lines = p[idx:measurement + 1]
                else:
                    lines = p[idx:characteristic + 1]
                valid_xcp.extend(lines)

        head.extend(valid_xcp)
        head.extend(tail)

        try:
            path = a2l_file.split(".")
            path_new = path[0] + "_reduced." + path[1]
            with open(path_new, "w") as f:
                new_content = "".join(head)
                f.write(new_content)
                logger.info(f"Created {path_new} successfully")
        except Exception as e:
            logger.error(f"Failed creating new {path_new}.Fail reason --> {e}")
            raise Exception(f"Failed creating new {path_new}.Fail reason --> {e}")

        a2l_dst = self.get_path(a2l_type)
        self.delete_files_in_folder(a2l_dst)

        self.copy_a2l(path_new, a2l_dst)
        if customer == "FORD" and a2l_type == "ACP_FD3":
            dir_list = os.listdir(a2l_dst)
            for index, a2l in enumerate(dir_list):
                if ".a2l" in a2l:
                    a2l_index = index
            full_path = a2l_dst + "\\" + dir_list[a2l_index]
            os.rename(full_path, a2l_dst + r"\ACP_FD3_reduced.a2l")

        # try:
        #     new_name = path[0]+"_original."+path[1]
        #     if not os.path.isfile(new_name):
        #         os.rename(a2l_file, new_name)
        #     logger.info(f"Renamed {a2l_file} to {new_name}")
        # except Exception as e:
        #     logger.error(f"A2L file renaming failed due to --> {e}")
        #     raise Exception(f"A2L file renaming failed due to --> {e}")

    def delete_files_in_folder(self, folder_path):
        """
        Delete all files in given folder

        Args:
          folder_path (str): Path to the folder

        Returns:
        """
        file_names = os.listdir(folder_path)
        # Iterate over the file names and delete each file
        for file_name in file_names:
            # Create the full path to the file
            file_path = os.path.join(folder_path, file_name)
            # Check if the current path is a file (not a directory)
            if os.path.isfile(file_path):
                # Delete the file
                os.remove(file_path)

    def get_path(self, a2l_type):
        """
        Get full path to A2L file

        Args:
          a2l_type (str): Type of the a2l file

        Returns:
        Directory to the a2l file
        """
        dirname = os.path.realpath(os.path.dirname(__file__))
        main_dir = dirname + "\\..\\..\\..\\..\\CustomerPrj\\XCP\\A2Ls\\" + a2l_type
        dir_exist = os.path.exists(main_dir)
        if not dir_exist:
            # Create a new directory because it does not exist
            os.makedirs(main_dir)
        return main_dir

    def copy_a2l(self, src, dst):
        """
        Copies A2L file from source to destination folder

        Args:
          src (str): Path to the source folder
          dst (str): Path to the destination folder

        Returns:

        """
        try:
            logger.info(f"Start copying A2L")
            copy_file(src, dst, update=True, verbose=True)
            logger.info(f"Finished copying")
            with open(dst + r"\Original_A2L_path.txt", "w+") as f:
                f.write(src)
            revision_file = src + "\\..\\..\\..\\..\\Revision.txt"
            if os.path.exists(revision_file):
                copy_file(revision_file, dst, update=True, verbose=True)
        except PermissionError as e:
            logger.error(f"Permission denied --> {e}")
            raise e
        except Exception as e:
            logger.error(f"Failed to copy A2L file --> {e}")
            raise e

    def generate_xcp_init(self, xcp_fc, xcp_fr, ecus):
        """
        Function to create the content for generation of init_xcp.cin file
        Args:
            xcp_fc (list) : list of front radar xcp variables
            xcp_fr (list) : list of rear radar xcp variables
            ecus (list with tuples) : number of available ECUs in xcp config file
        Returns:
            List of all xcp varialbes that should be added in init_xcp.cin file (list)
        """

        logger.info("Start generation of init_xcp.cin list")
        modified_list = []
        modified_list_fr = []

        if np.size(xcp_fc):
            for modified in xcp_fc:
                message_modified = modified[1].replace(".", "::")
                modified_list.append("RadarFC::" + message_modified + modified[0])
            logger.info(f"Found {len(modified_list)} XCP variables for RadarFC")
        else:
            logger.warning("No XCP variables for Front Center Radar")

        if np.size(xcp_fr):
            for ecu in ecus[1:]:
                if ecu[0] is not None:
                    for modified_fr in xcp_fr:
                        message_modified = modified_fr[1].replace(".", "::")
                        modified_list_fr.append(ecu[1] + "::" + message_modified + modified_fr[0])
            logger.info(f"Found {len(modified_list_fr)} XCP variables for Corner Radar(s)")
        else:
            logger.warning("No XCP variables for Corner Radar(s)")

        modified_list.extend(modified_list_fr)
        head = '''/**
 * @file signal.can
 * @author Rafael Herrera - /XCP initialization file
 * @date 04.03.2022
 * @brief contains code that initilizes the XCP variables
 */
includes
{
}

variables
{
}

/***** Automated code generation starts here *****/

void init_xcp()
{
  if(init_count == 1)
  {'''

        item_xml = []
        txt = "/*@!Encoding:1252*/ \n" + "// Autogenerated by -> " + os.path.dirname(
            os.path.abspath(__file__)) + r"\XCP_to_A2L_diff.py "+ "\n" + head
        xml = [txt]
        flag_count = 1
        signal_batch = 25
        var_count = 0

        if modified_list:
            for xcp_var in modified_list:
                item_xml.append(f'  @sysvar::XCP::{xcp_var} = @sysvar::XCP::{xcp_var};')
                var_count += 1
                # case new set of 25 signals
                if var_count % signal_batch == 0:
                    # except for the first signal
                    item_xml.append('  }')
                    ini_count = var_count // signal_batch + 1
                    item_xml.append(f'  if(init_count == {ini_count})')
                    item_xml.append('  {')

            flag_count += 1
            item_xml.append('  initFlag = {0};'.format(flag_count))
            item_xml.append('  }')
            item_xml.append('  init_count++;')
            item_xml.append('}')
            xml.extend(item_xml)

            file = r"../Restbus/Nodes/Functions/init_xcp.cin"
            try:
                logger.info("Updating init_xcp.cin")
                with open(file, 'w') as outfile:
                    outfile.write("\n".join(str(item) for item in xml))
                    outfile.close()
                logger.info(f"{file} updated successfully")
            except Exception as e:
                logger.error(f"ERROR updating init_xcp.cin --> {e}")
        else:
            logger.warning("No XCPs found in the FDX_Database.xlsx sheets")

    def create_xcp_template(self, xcp_config, customer, front_a2l_path_loc=None, front_a2l_path_obj=None,
                            rear_a2l_path=None, dasy_a2l_path=None, use_lean_a2l=False, is_jenkins=False):
        """
        Function to create CanOE XCP config file template

        Args:
          xcp_config (str): Path to the xcp config file
          customer (str): Customer
          front_a2l_path_loc:  (Default value = None)
          front_a2l_path_obj:  (Default value = None)
          rear_a2l_path:  (Default value = None)
          dasy_a2l_path:  (Default value = None)
          use_lean_a2l:  (Default value = False)
          is_jenkins:  (Default value = False)

        Returns:

        """
        # IMPORTANT:
        # COM interface cannot load xcp_config in canoe if relative path is given
        # Hence always give absolute path when updated through jenkins

        xcp_folder_path = "\\".join(xcp_config.split("\\")[:-1])
        if front_a2l_path_loc is not None:
            if use_lean_a2l is True:
                front_a2l_path_reduced = front_a2l_path_loc.split(".")[0] + "_reduced.a2l"
                if is_jenkins:
                    path_front_loc = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{front_a2l_path_reduced}" /></a2l>'
                else:
                    if customer == "FORD":
                        path_front_loc = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\RadarFC_Locations\RadarFC_reduced.a2l" /></a2l>'
                    else:
                        path_front_loc = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\RadarFC_Locations_Gamma\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_front_loc = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{front_a2l_path_loc}" /></a2l>'
        else:
            # no need of update, if is_jenkins true then change to absolute path
            if is_jenkins:
                if customer == "FORD":
                    path_front_loc = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\RadarFC_Locations\RadarFC_reduced.a2l" /></a2l>'
                else:
                    path_front_loc = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\RadarFC_Locations_Gamma\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_front_loc = ""

        if front_a2l_path_obj is not None:
            if use_lean_a2l is True:
                front_a2l_path_reduced = front_a2l_path_obj.split(".")[0] + "_reduced.a2l"
                if is_jenkins:
                    path_front_obj = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{front_a2l_path_reduced}" /></a2l>'
                else:
                    if customer == "FORD":
                        path_front_obj = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\RadarFC_Objects\RadarFC_reduced.a2l" /></a2l>'
                    else:
                        path_front_obj = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\RadarFC_Objects_Alpha\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_front_obj = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{front_a2l_path_obj}" /></a2l>'
        else:
            if is_jenkins:
                if customer == "FORD":
                    path_front_obj = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\RadarFC_Objects\RadarFC_reduced.a2l" /></a2l>'
                else:
                    path_front_obj = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\RadarFC_Objects_Alpha\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_front_obj = ""

        if rear_a2l_path is not None:
            if use_lean_a2l is True:
                rear_a2l_path_reduced = rear_a2l_path.split(".")[0] + "_reduced.a2l"
                if is_jenkins:
                    path_corner = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{rear_a2l_path_reduced}" /></a2l>'
                else:
                    path_corner = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\RadarCorner\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_corner = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{rear_a2l_path}" /></a2l>'
        else:
            if is_jenkins:
                path_corner = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\RadarCorner\RadarFC_reduced.a2l" /></a2l>'
            else:
                path_corner = ""

        if dasy_a2l_path is not None:
            if use_lean_a2l is True:
                dasy_a2l_path_reduced = dasy_a2l_path.split(".")[0] + "_reduced.a2l"
                if is_jenkins:
                    path_dasy = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{dasy_a2l_path_reduced}" /></a2l>'
                else:
                    if customer != "FORD":
                        path_dasy = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\DASY\DASY_BASE_01_reduced.a2l" /></a2l>'
                    else:
                        path_dasy = r'        <a2l><VFileName v="V9" f="QL" init="1" name="A2Ls\APC_FD3\ACP_FD3_reduced.a2l" /></a2l>'
            else:
                path_dasy = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{dasy_a2l_path}" /></a2l>'
        else:
            if is_jenkins:
                if customer != "FORD":
                    path_dasy = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\DASY\DASY_BASE_01_reduced.a2l" /></a2l>'
                else:
                    path_dasy = rf'        <a2l><VFileName v="V9" f="QL" init="1" name="{xcp_folder_path}\A2Ls\APC_FD3\ACP_FD3_reduced.a2l" /></a2l>'
            else:
                path_dasy = ""

        signals_tag = "            <signal"
        if customer == "FORD":
            a2l_dasy = 'name="ACP_FD3"'
            a2l_front_obj = 'name="RadarFC"'
        else:
            a2l_dasy = 'name="DASY_BASE_01"'
            a2l_front_obj = 'name="RadarFC_Obj"'
        a2l_front_loc = 'name="RadarFC_Loc"'
        a2l_rear_fr = 'name="RadarFR"'
        a2l_rear_fl = 'name="RadarFL"'
        a2l_rear_rr = 'name="RadarRR"'
        a2l_rear_rl = 'name="RadarRL"'
        line_radar_fc_loc = None
        line_radar_fc_obj = None
        line_radar_fr = None
        line_radar_fl = None
        line_radar_rr = None
        line_radar_rl = None
        line_dasy = None
        offset = 2

        with open(xcp_config) as f:
            for line_no, line in enumerate(f):
                if a2l_rear_fr in line:
                    line_radar_fr = line_no + offset
                elif a2l_rear_fl in line:
                    line_radar_fl = line_no + offset
                elif a2l_rear_rl in line:
                    line_radar_rl = line_no + offset
                elif a2l_rear_rr in line:
                    line_radar_rr = line_no + offset
                elif a2l_front_loc in line:
                    line_radar_fc_loc = line_no + offset
                elif a2l_front_obj in line:
                    line_radar_fc_obj = line_no + offset
                elif a2l_dasy in line:
                    line_dasy = line_no + offset
        try:
            for line_num, line in enumerate(fileinput.input(xcp_config, inplace=1)):
                if signals_tag in line:
                    continue
                elif line_num == line_radar_fc_loc and (front_a2l_path_loc != None or is_jenkins):
                    line = line.replace(line, path_front_loc + "\n")
                    sys.stdout.write(line)
                elif line_num == line_radar_fc_obj and (front_a2l_path_obj != None or is_jenkins):
                    line = line.replace(line, path_front_obj + "\n")
                    sys.stdout.write(line)
                elif line_num in (line_radar_fr, line_radar_fl, line_radar_rl, line_radar_rr) and (
                        rear_a2l_path != None or is_jenkins):
                    line = line.replace(line, path_corner + "\n")
                    sys.stdout.write(line)
                elif line_num == line_dasy and (dasy_a2l_path != None or is_jenkins):
                    line = line.replace(line, path_dasy + "\n")
                    sys.stdout.write(line)
                else:
                    sys.stdout.write(line)
        except Exception as e:
            logger.error(f"Failed --> {e}")
            raise

    def delete_signals(self, xcp_config, a2l_path, value, customer, use_lean_a2l=False, is_jenkins=False):
        """
        Function to create XCP template file

        Args:
          xcp_config (str): Path to the xcp config file
          a2l_path (str): Path to a2l file
          value (str): What to be deleted
          customer (str): Current customer
          use_lean_a2l (bool): Lean A2l True/False (Default value = False)
          is_jenkins (bool): Is function used in Jenkins run  (Default value = False)

        Returns:
        """

        try:

            if use_lean_a2l is True:
                a2l_path_reduced = a2l_path.split(".")[0] + "_reduced.a2l"
                if is_jenkins:
                    path = a2l_path_reduced
                else:
                    if customer != "FORD":
                        match value:
                            case "DPCdelta1":
                                path = r"A2Ls\DPCdelta1\DASY_BASE_01_reduced.a2l"
                            case "DPCdelta5":
                                path = r"A2Ls\DPCdelta5\DASY_BASE_01_reduced.a2l"
                            case "RadarFC_Loc":
                                path = r"A2Ls\RadarFC_Locations_Gamma\RadarFC_reduced.a2l"
                            case "RadarFC_Obj":
                                path = r"A2Ls\RadarFC_Objects_Alpha\RadarFC_reduced.a2l"
                            case "RadarFR":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarFL":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarRL":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarRR":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"

                    else:
                        match value:
                            case "ACP_FD3":
                                path = r"A2Ls\APC_FD3\ACP_FD3_reduced.a2l"
                            case "RadarFC_Loc":
                                path = r"A2Ls\RadarFC_Locations\RadarFC_reduced.a2l"
                            case "RadarFC":
                                path = r"A2Ls\RadarFC_Objects\RadarFC_reduced.a2l"
                            case "RadarFR":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarFL":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarRL":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"
                            case "RadarRR":
                                path = r"A2Ls\RadarCorner\RadarFC_reduced.a2l"

            else:
                path = a2l_path

            # Parse the XML content from the input file
            tree = ET.parse(xcp_config)
            root = tree.getroot()
            attribute = "name"
            matching_elements = root.findall(".//device[@{}='{}']".format(attribute, value))
            a2l_path_ref = matching_elements[0].findall(".//a2l/VFileName")
            a2l_path_ref[0].set(attribute, path)
            # Find the element with the tag you want to remove content from
            element_to_remove_content = matching_elements[0].findall(".//signals")
            children_to_remove = list(element_to_remove_content[0])
            for child_element in children_to_remove:
                element_to_remove_content[0].remove(child_element)

            # Serialize the modified XML and save it to the output file
            tree.write(xcp_config, xml_declaration=True, method='xml', encoding='Windows-1252')

            logger.info(f"Template XML has been saved to {xcp_config}")

        except Exception as e:
            logger.error(f"Failed --> {e}")
            raise
