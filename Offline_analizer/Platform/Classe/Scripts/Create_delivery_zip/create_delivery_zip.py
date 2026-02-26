# -*- coding: utf-8 -*-
# @file create_delivery_zip.py
# @author ADAS_HIL_TEAM
# @date 10-02-2023

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
import py_compile
import re
import fnmatch
import zipfile
from pathlib import Path

class Deliver(object):
    def __init__(self) -> None:
        # Create the directory you want to zip
        self.source_directory = os.path.abspath(os.path.abspath(__file__) + r"..\..\..\..\..\..")
        print("Root Directory:", self.source_directory)

        self.project_drive = os.path.abspath(self.source_directory + r"\\..\\FORD_ADAS_HIL_Delivery")
        if not os.path.exists(self.project_drive):
            os.mkdir(self.project_drive)

        self.black_listed_files = []
        self.include_list = []


    def get_black_list(self):
            black_list_path = os.path.dirname(os.path.abspath(__file__)) + "\\black_list.txt"
            customer_black_list = self.source_directory + r"\Deployment\cus_black_list.txt"
            try:
                with open(black_list_path, "r") as file, open(customer_black_list, "r") as cus_file:
                    # Read each line and store them in a list
                    entries = [line.strip() for line in file]
                    entries_cust = [line.strip() for line in cus_file]
                    entries += entries_cust

                    for line in entries:
                        path = self.source_directory + line if "\\" in line else line

                        if '!' in path:
                            # We use ! as a whitelist symbol
                            path = path.replace('!', '')
                            self.include_list.append(path)
                        else:
                            self.black_listed_files.append(path)

                    print(f"Filtered files and folders -- {self.black_listed_files}")
            except FileNotFoundError:
                print(f"File '{black_list_path}' not found.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")


    def create_log_files(self):
        special_files_list = ["pyc", "can", "cin", "bat", "exe", "xvp", "xlsx", "xml"]
        file_list_all = []
        file_list_int_property = []

        for root, dirs, files in os.walk(self.source_directory):
            for file in files:
                file_path = os.path.join(root, file)

                file_list_all.append(file_path)
                if file_path.split(".")[-1] in special_files_list:
                    file_list_int_property.append(file_path)

                if file_path.endswith('.bat'):
                    self.modify_bat_file(file_path)

        # Create log file with the white list files
        file_path_log_all = self.project_drive + r"\\all_files.txt"
        file_path_log_int_property = self.project_drive + r"\\int_property_files.txt"
        with open(file_path_log_all, 'w') as f:
            # Iterate through the list of strings and write each string followed by a newline character
            for line in file_list_all:
                f.write(line + "\n")
        print(f"Created log file which includes all files in the project --> {file_path_log_all}")

        with open(file_path_log_int_property, 'w') as f:
            # Iterate through the list of strings and write each string followed by a newline character
            for line in file_list_int_property:
                f.write(line + "\n")
        print(f"Created log file which includes intellectual property in the project --> {file_path_log_int_property}")


    def compile_python_files(self):
        for root, dirs, files in os.walk(self.source_directory):
            for file in files:
                file_path = os.path.join(root, file)

                if file_path.endswith('.py'):
                    # Compile to a pyc file
                    try:
                        py_compile.compile(file_path, file_path + 'c', doraise=True)
                    except:
                        print(f'Could not compile {file_path}')


    def modify_bat_file(self, path):
        with open(path, 'r') as file:
            lines = file.readlines()

        # Replace line
        new_lines = [re.sub(r'\.py', '.pyc', line) for line in lines]

        # Overwrite file
        with open(path, 'w') as file:
            file.writelines(new_lines)


    def is_blocked(self, path):
        # Unix like match for our file path to blocked patterns
        for pattern in self.black_listed_files:
            if fnmatch.fnmatch(path, pattern):
                return True

        return False


    def zip_directory(self):
        output_zip_file = (self.project_drive + "\\ADAS_HIL_FORD_Delivery.zip")
        with zipfile.ZipFile(output_zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(self.source_directory):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Only filter if there is blocked files
                    if self.black_listed_files and self.is_blocked(file_path):
                        continue

                    arcname = os.path.relpath(file_path, self.source_directory)
                    zip_file.write(file_path, arcname=arcname)

            # Add whitelisted files
            for file_path in self.include_list:
                if os.path.isdir(file_path):
                    for root, _, files in os.walk(file_path):
                        for file in files:
                            temp_path = os.path.join(root, file)
                            arcname = os.path.relpath(temp_path, self.source_directory)
                            zip_file.write(temp_path, arcname=arcname)
                else:
                    arcname = os.path.relpath(file_path, self.source_directory)
                    zip_file.write(file_path, arcname=arcname)

        print(f"Zip delivery file '{output_zip_file}' created successfully.")


    def createDeliveryZipMain(self):
        """
        main function
        Returns:
        """
        self.get_black_list()
        self.compile_python_files()
        self.create_log_files()
        self.zip_directory()


if __name__ == "__main__":
    delivery = Deliver()
    delivery.createDeliveryZipMain()

