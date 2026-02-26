# -*- coding: utf-8 -*-
# @file file_search.py
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


import pandas as pd
# Set the option to opt-in to the future behavior
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import os, sys
import openpyxl
import re
try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.getcwd() + r"\..\Control")
    from logging_config import logger
import xml.etree.ElementTree as ET


def create_mapping_from_a2l(input_filename):
    """
    

    Args:
      input_filename: 

    Returns:

    """
    events = []
    start_index = []
    stop_index = []
    try:
        with open(input_filename, 'r') as input_file:
            content = input_file.read()
            content_list = content.splitlines()
            for index, line in enumerate(content_list):
                if "/begin EVENT" in line:
                    start_index.append(index)
                elif "/end EVENT" in line:
                    stop_index.append(index)
        for start, end in zip(start_index,stop_index):
            events.append(content_list[start+1:end])
    except FileNotFoundError:
        print("Input file not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def generate_event_list(raw_events): # Function logic will be updated when more info is available
    """
    

    Args:
      raw_events: 

    Returns:

    """
    events = []
    for raw_event in raw_events:
        sampling = int(raw_event[5].strip(), 0)
        event_id = int(raw_event[2].strip(), 0)
        name = raw_event[0].strip()[1:-1]
        rate = int(sampling/10) if sampling != 100 else int(sampling/100)
        daq_lists = int(raw_event[4].strip(), 0)
        prio = int(raw_event[7].strip(), 0)
        properties = int(raw_event[6].strip(), 0)
        event = f'<customDaqEvent daqEventId="{event_id}" name="{name}" rate="{rate}" unit="kSampleUnit{sampling}ms" maxDaqLists="{daq_lists}" priority="{prio}" properties="{properties}" />'
        events.append(event)
    return events


def create_mapping(xcp_config, index):
    """
    

    Args:
      xcp_config: 
      index: 

    Returns:

    """
    search_string = "customDaqEvent"
    mapping_daq_events = {}

    try:
        with open(xcp_config, 'r') as file:
            for current_row, line in enumerate(file, start=1):
                if current_row > index:
                    if "/customdaqevents" in line:
                        return mapping_daq_events
                    elif search_string in line:
                        split_line = line.split()
                        key = split_line[2].split("=")[1][1:-1]
                        value = split_line[1].split("=")[1][1:-1]
                        mapping_daq_events[key] = value
    except FileNotFoundError:
        return "File not found"


def extract_daq_events_from_a2l(a2l_path):
    """
    

    Args:
      a2l_path: 

    Returns:

    """
    start_string = '/begin EVENT'
    end_string = '/end EVENT'
    try:
        contents = []
        with open(a2l_path, 'r') as file:
            file_contents = file.read()
            pattern = re.compile(fr'{re.escape(start_string)}(.*?){re.escape(end_string)}', re.DOTALL)
            for match in pattern.finditer(file_contents):
                contents.append(match.group(1))

        if contents:
            daq_events_list = []
            for content in contents:
                text_without_long_spaces = re.sub(r'\s+', ' ', content)
                fixed_event_list = text_without_long_spaces.split(" ")
                daqEventId = int(fixed_event_list[3], 16)
                name = fixed_event_list[1]
                rate = int(fixed_event_list[6], 16)
                maxDaqLists = int(fixed_event_list[5], 16)
                priority = int(fixed_event_list[8], 16)

                if "_t" in name:
                    sample = int(int(name.split("_t")[-1].rstrip('"'))/rate)
                elif "_bg" in name:
                    sample = int(50/rate)
                    if sample == 0:
                        sample = 1
                else:
                    sample = 10

                daq_event = fr'<customDaqEvent daqEventId="{daqEventId}" name={name} rate="{rate}" unit="kSampleUnit{sample}ms" maxDaqLists="{maxDaqLists}" priority="{priority}" properties="4" />'
                logger.info(daq_event)
                daq_events_list.append(daq_event)
            return daq_events_list
        else:
            logger.warning(f"No DAQ Event found in {a2l_path}.")
    except Exception as e:
        raise e


def separate_file_by_string(file_path, split_string):
    """
    

    Args:
      file_path: 
      split_string: 

    Returns:

    """
    dictionary = {}
    current_key = ""
    current_array = []

    with open(file_path, "r") as f:
        for line in f:
            if split_string in line:
                # Add the current array to the dictionary with the current key
                dictionary[current_key] = current_array

                # Start a new array and update the current key
                current_key = line.strip()
                current_array = []
            else:
                # Add the line to the current array
                current_array.append(line.split(",")[0])

        # Add the last array to the dictionary with the last key
        dictionary[current_key] = current_array

    return dictionary


def read_xcp_database(ecu, database):
    """
    

    Args:
      ecu: 
      database: 

    Returns:

    """
    # Load the Excel file
    excel_file = pd.ExcelFile(database)

    # Create an empty dictionary to hold the DataFrames
    dataframes = {}

    # Loop through each sheet in the Excel file
    try:
        for sheet_name in excel_file.sheet_names:
            if sheet_name == ecu:
                # Load the sheet into a DataFrame
                df = excel_file.parse(sheet_name)

                # Add the DataFrame to the dictionary with the sheet name as the key
                dataframes[sheet_name] = df
    except Exception as e:
        logger.error(f"Unable to read the database --> {e}")

    # Print each DataFrame
    # for sheet_name, df in dataframes.items():
    #     print(f"Sheet name: {sheet_name}")
    #     print(df.head())

    return dataframes


def signal_search(signals_database, xcel_database, mapping):
    """
    

    Args:
      signals_database: 
      xcel_database: 
      mapping: 

    Returns:

    """
    try:
        # Iterate through each row in the DataFrame
        updated_cycle_time = {}
        for key, df in xcel_database.items():
            for index, row in df.iterrows():
                if row["read"] == "DAQ" and row["cycle"] != 27 and row["cycle"] != 29:
                    # Create full signal name
                    if isinstance(row["Message"], float):
                        message = ""
                    else:
                        message = row["Message"]
                    if message:
                        search_string = message.split(".")[0] + "."
                    else:
                        search_string = row["Name"]
                    cycle_time = row["cycle"]
                    signal_list_cycle_time = search_in_signal_list(signals_database, search_string, cycle_time, mapping)
                    # Print the values in each column for the current row
                    if signal_list_cycle_time is None:
                        logger.warning(f"Missing in signal list --> {search_string}")
                    elif cycle_time != signal_list_cycle_time:
                        updated_cycle_time[index+2] = signal_list_cycle_time
                        # df.at[index, "cycle"] = signal_list_cycle_time
                        logger.info(f"Updated daqEventId for runnable {search_string} from {cycle_time} to {signal_list_cycle_time}")
        return updated_cycle_time
    except Exception as e:
        logger.error(f"Failed updating daqEvent --> {e}")
        raise e


def search_in_signal_list(signal_database, signal_name, current_cycle_time, mapping):
    """
    

    Args:
      signal_database: 
      signal_name: 
      current_cycle_time: 
      mapping: 

    Returns:

    """
    # Iterate current signal through signal database in order to find the correct cycle time
    for key, value in signal_database.items():
        filtered_list = [item for item in value if item.startswith(signal_name)]
        if len(filtered_list) > 0 and "on event" not in key:
            # print(signal_name)
            # print(key)
            # If populated cycle time in XCP_Database is the same as in the signal list do nothing
            if int(mapping[key.lstrip("[").rstrip("]")]) == current_cycle_time:
                return current_cycle_time
            else:
                # Else return the correct cycle time
                return mapping[key.lstrip("[").rstrip("]")]


def get_signal_list_file(path):
    """
    

    Args:
      path: 

    Returns:

    """
    substring = 'signals_list.txt'
    for root, dirs, files in os.walk(path):
        for file in files:
            if substring in file:
                return os.path.join(root, file)
    return None


def write_database(updates_cycles, database, sheet_name):
    """
    

    Args:
      updates_cycles: 
      database: 
      sheet_name: 

    Returns:

    """
    # Load the Excel file
    workbook = openpyxl.load_workbook(database)

    # Select the sheet you want to update
    sheet = workbook[sheet_name]

    # Update the value of a specific cell
    cell_column = 'AF'
    for key, value in updates_cycles.items():
        sheet[f'{cell_column}{key}'] = int(value)

    # Save the changes to the Excel file
    try:
        workbook.save(database)
        logger.info("Cells has been updated in the XCP_Database Excel file.")
        workbook.close()
    except Exception as e:
        logger.error(e)


def update_daq_events_xcpconfig(xcp_config, ecu, customevents_list):
    """
    

    Args:
      xcp_config: 
      ecu: 
      customevents_list: 

    Returns:

    """
    try:
        # Parse the XML content from the input file
        tree = ET.parse(xcp_config)
        root = tree.getroot()
        attribute = "name"
        matching_elements = root.findall(".//device[@{}='{}']".format(attribute, ecu))

        # Find the element with the tag you want to remove content from
        element_to_remove_content = matching_elements[0].findall(".//customdaqevents")
        children_to_remove = list(element_to_remove_content[0])
        for child_element in children_to_remove:
            element_to_remove_content[0].remove(child_element)

        # Write updated customevents
        # Append each tag as a subelement to the existing root
        for event in customevents_list:
            sub_element = ET.fromstring(event)
            sub_element.tail = '\n\t\t  '
            element_to_remove_content[0].append(sub_element)


        # Serialize the modified XML and save it to the output file
        tree.write(xcp_config, xml_declaration=True, method='xml', encoding='Windows-1252')

        logger.info(f"Template XML has been saved to {xcp_config}")

    except Exception as e:
        logger.error(f"Failed --> {e}")
        raise


def update_database_cycle_times(sheet, a2l_path, xcp_config, index, ecu_tag):
    """
    

    Args:
      sheet: 
      a2l_path: 
      xcp_config: 
      index: 
      ecu_tag: 

    Returns:

    """
    excel_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../CustomerPrj/XCP/XCP_Database.xlsx"))
    sig_list_abs_path = os.path.abspath(a2l_path + r"\..\..\..\Canape\addon\EDITCNA_UC1")
    sig_list_file = get_signal_list_file(sig_list_abs_path)
    if sig_list_file is not None:
        daq_events_list = extract_daq_events_from_a2l(a2l_path)
        update_daq_events_xcpconfig(xcp_config, ecu_tag, daq_events_list)
        mapping = create_mapping(xcp_config, index)
        sig_database = separate_file_by_string(sig_list_file, "[")
        excel_database = read_xcp_database(sheet, excel_file_path)
        new_cycle_times = signal_search(sig_database, excel_database, mapping)
        if new_cycle_times:
            write_database(new_cycle_times, excel_file_path, sheet)
        else:
            logger.info("Cycle times are up to date.")


if __name__ == "__main__":
    update_database_cycle_times(ecu, a2l_path)

