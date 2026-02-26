# -*- coding: utf-8 -*-
# @file copyrights_generator.py
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


import os,sys
from datetime import datetime
import subprocess

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger

script_path = os.path.dirname(os.path.abspath(__file__))
adas_hil_repo_path = script_path + r"\\..\\..\\..\\.."




# GUI input

file_patterns = ["py", "can", "cin"]



CAPL_FILE_HEADER = """/*@!Encoding:1252*/
/**
 * @file <file_name>
 * @author <author_name>
 * @date <file_creation_date>
 * @brief <file_brief>
 *
 * ################################################################
 * C O P Y R I G H T S
 * ----------------------------------------------------------------
 * Copyright (c) <file-created-year><file-last-modified-year> by Robert Bosch GmbH. All rights reserved.
 
 * The reproduction, distribution and utilization of this file as
 * well as the communication of its contents to others without express
 * authorization is prohibited. Offenders will be held liable for the
 * payment of damages. All rights reserved in the event of the grant
 * of a patent, utility model or design.
 *
 * ################################################################
*/
"""

CR_ALREADY_PRESENT_HEADER_CAPL = " * Copyright (c) <file-created-year><file-last-modified-year> by Robert Bosch GmbH. All rights reserved.\n"

PYTHON_FILE_HEADER = """# -*- coding: utf-8 -*-
# @file <file_name>
# @author <author_name>
# @date <file_creation_date>

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) <file-created-year><file-last-modified-year> by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################

"""

CR_ALREADY_PRESENT_HEADER_PYTHON = "# Copyright (c) <file-created-year><file-last-modified-year> by Robert Bosch GmbH. All rights reserved.\n"

special_case_files_list = ["datahandling.cin"]


def get_file_creation_date(cwd_dirpath, file_name):
    """
    finds the file creation date using git command

    Args:
      cwd_dirpath(str): directory path where the file is present
      file_name(str): name of the file

    Returns:
      dict: {"year":year, "date":date}

    """
    try:
        git_command = f'git log --follow --format="%ad" --date=format:"%m-%d-%Y" -- {file_name}'
        date = subprocess.check_output(git_command, shell=True, cwd=cwd_dirpath).decode('utf-8')

        date = date.strip().split("\n")[-1]
        year = date.split("-")[-1]

        return {"year": year, "date": date}
    except Exception as e:
        logger.error(f"Error occured while finding file creation date for {file_name} -> {e}")
        return None



def isCopyrightsPresent(file_path):
    """
    checks if already copyrights header is present in the given file

    Args:
      file_path (str): path to file

    Returns:
        bool: True if present else False
    """
    copyrights_str = "Copyright (c)"
    with open(file_path, encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
        for i,line in enumerate(lines):
            if i > 30:
                return False
            if copyrights_str in line:
                return i
        file.close()
        return False


def generate_copy_rights():
    """ main function for copy rights generation, reads files and adds/updates copyrights"""
    for (dirpath, dirnames, filenames) in os.walk(adas_hil_repo_path):

        if (r"\.git" in dirpath) or (r"\.idea" in dirpath) or (r"\.run" in dirpath) or (r"\venv" in dirpath):
            continue

        for file in filenames:
            if file.lower() in special_case_files_list:
                logger.warning(f"Skipped {file} due to invalid characters, please update copyrights manually")
                continue
            file_type = file.split(".")[-1].lower()
            if file_type in file_patterns:
                header = PYTHON_FILE_HEADER if file_type == "py" else CAPL_FILE_HEADER

                #if already present
                already_present_header = CR_ALREADY_PRESENT_HEADER_PYTHON if file_type == "py" else CR_ALREADY_PRESENT_HEADER_CAPL

                #logger.info(dirpath)
                file_path = os.path.join(dirpath, file)
                dict_date = get_file_creation_date(dirpath, file)
                if dict_date is None:
                    continue
                last_modified_year = datetime.fromtimestamp(os.path.getmtime(file_path)).year

                already_present_index = isCopyrightsPresent(file_path)

                if already_present_index:
                    with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                        file_content = f.readlines()
                        already_present_header = already_present_header.replace("<file-created-year>", str(dict_date['year']))
                        if str(dict_date['year']).strip() == str(last_modified_year).strip():
                            already_present_header = already_present_header.replace("<file-last-modified-year>", "")
                        else:
                            already_present_header = already_present_header.replace("<file-last-modified-year>", "-" + str(last_modified_year))
                        file_content[already_present_index] = already_present_header

                else:
                    header = header.replace("<file_name>", file)
                    header = header.replace("<author_name>", "ADAS_HIL_TEAM")
                    header = header.replace("<file_creation_date>", str(dict_date['date']))
                    header = header.replace("<file-created-year>", str(dict_date['year']))
                    if str(dict_date['year']).strip() == str(last_modified_year).strip():
                        header = header.replace("<file-last-modified-year>", "")
                    else:
                        header = header.replace("<file-last-modified-year>", "-" + str(last_modified_year))

                    if file_type == "py":
                        with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for ind,l in enumerate(lines):
                                if l[0].isalpha() or l[0]=='"':
                                    break
                            lines = lines[ind:]
                            if l[0]!='"':
                                file_content = [header, "\n"] + lines
                            else:
                                file_content = [header,"\n"] + lines
                            f.close()

                    else:
                        try:
                            search_string = "{"
                            brief = ""
                            file_content = []
                            with open(file_path, "r", encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                found = False
                                for i, line in enumerate(lines):
                                    if search_string in line:
                                        header = header.replace("<file_brief>", brief)
                                        if i >= 2:
                                            if lines[i-1].strip()=="" and lines[i].strip()=="{": # now found the { of capl, now find the keyword like include or variable etc
                                                for j in range(i-1,0,-1):
                                                    if lines[j].strip()!="":
                                                        i=j
                                                        break


                                            file_content = [header, "\n"] + lines[i - 1:]
                                            # header += lines[i - 1]
                                        else:
                                            file_content = [header, "\n"] + lines[0:]
                                        found = True
                                        break
                                    elif "@brief" in line:
                                        brief = line.strip().split("@brief")[-1] if not (brief) else brief + "\t" + \
                                                                                                     line.strip().split("@brief")[-1]

                                f.close()

                        except Exception as e:
                            logger.error(f"error occured for file - >{file}")
                            continue
                    # logger.info("=" * 10)
                    # logger.info(file)
                    # logger.info("creation_date: ", dict_date["date"])
                    # logger.info("creation_year: ", dict_date["year"])
                    # logger.info("last_modified_year: ", last_modified_year)
                try:
                    with open(file_path, "w", encoding='utf-8', errors='ignore') as f:
                        f.writelines(file_content)
                        logger.info(f"Updated -> {file}")
                        f.close()
                except Exception as e:
                    logger.error(f"Error while updating -> {file_path}, ->{e} , invalid characters found, update copyrights manually")



if __name__ == "__main__":
    generate_copy_rights()
