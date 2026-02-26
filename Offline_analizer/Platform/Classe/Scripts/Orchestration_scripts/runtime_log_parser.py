# -*- coding: utf-8 -*-
# @file runtime_log_parser.py
# @author ADAS_HIL_TEAM
# @date 09-13-2023

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


def get_latest_log():
    """ """

    # Specify the main dir
    main_path = r'D:\CarMaker_Project\SimOutput'
    # Get HIL name in the specified path
    hil_name = os.listdir(main_path)
    directory_path = main_path + "\\" + hil_name[0] + "\\Log"
    
    # Get a list of all files in the directory
    files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if
             os.path.isfile(os.path.join(directory_path, file))]

    # Check if there are any files in the directory
    if not files:
        print("No files found in the directory.")
    else:
        # Get the latest (most recently modified) file
        latest_file = max(files, key=os.path.getmtime)

        # Print latest log file
        print("Latest log file:", latest_file)
        return latest_file


def parse_error_log(error_log_file):
    """
    

    Args:
      error_log_file: 

    Returns:

    """
    # Define the input file path and output file path
    output_file_path = r'X:\error_log.txt'

    # Open the input file for reading and the output file for writing
    try:
        with open(error_log_file, 'r') as input_file, open(output_file_path, 'w') as output_file:
            # Iterate through each line in the input file
            for line in input_file:
                # Check if the line starts with "ERROR"
                if line.startswith("ERROR"):
                    # Write the line to the output file
                    output_file.write(line)
    except FileNotFoundError:
        print(f"The input file '{error_log_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    log_file = get_latest_log()
    parse_error_log(log_file)

