# -*- coding: utf-8 -*-
# @file doxygen_capl_filter.py
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


import re
import sys

input_file = sys.argv[1]
#input_file = r"temp_file.can"
includes = 0
variables = 0

def main():
    """ """
    try:


        with open(input_file, 'r') as file_handler:
            if (input_file.lower().endswith(".can") or input_file.lower().endswith(".cin")):
                for line in file_handler:
                    global includes, variables
                    line = line.rstrip('\n')

                    # Remove include and brackets
                    if line.startswith('includes'):
                        includes = 1
                        line = line.replace('includes', '')

                    line = re.sub(r'#include.*', '', line)

                    if includes == 1:
                        if '{' in line:
                            line = line.replace('{', '')
                        if '}' in line:
                            line = line.replace('}', '')
                            includes = 0

                    # Remove pragma
                    line = re.sub(r'#pragma.*', '', line)

                    # Remove variables and brackets
                    if line.startswith('variables'):
                        variables = 1
                        line = line.replace('variables', '')

                    if variables > 0:
                        if '{' in line:
                            if variables == 1:
                                line = line.replace('{', '')
                            variables += 1
                        if '}' in line:
                            variables -= 1
                            if variables == 1:
                                line = line.replace('}', '')
                                variables = 0

                    # Replace "on xyz abc" => "on_xyz_abc()"
                    on_match = re.match(r'[Oo]n\s(\S+)\s(\S+)', line)
                    if on_match:
                        line = re.sub(r'::', '_', line)
                        line = re.sub(r'\*', 'asterisk', line)
                        line = re.sub(r'[Oo]n\s(\S+)\s(\S+)', r'on_\1_\2()', line)

                    # Replace "on xyz" => "on_xyz()"
                    line = re.sub(r'[Oo]n\s(\S+)', r'on_\1()', line)

                    # Replace "testcase xyz" => "testcase_xyz"
                    line = re.sub(r'^testcase\s', 'testcase_', line)

                    print(line)
            else:
                for line in file_handler:
                    print(line)

    except FileNotFoundError:
        print(f"Can't open {input_file} for reading")

if __name__ == "__main__":
    main()
