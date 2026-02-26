from can import io
import re
import pandas as pd
import ctypes
import sys
from typing import List
from enum import Enum
from asammdf import MDF
import os

# Get the directory of the current script

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Append the relative paths to sys.path
    sys.path.append(os.path.join(script_dir, "../ReportGen"))
    sys.path.append(os.path.join(script_dir, "../ByteArrayParser"))
    import ra6_sgu_reader as ra6
    import HTML_Logger
except:
    import Platform.Python_Testing_Framework.ReportGen.HTML_Logger as HTML_Logger
    import Platform.Python_Testing_Framework.ByteArrayParser.ra6_sgu_reader as ra6


# Define an enumeration for the conditions
class RADAR_ID(Enum):
    RFC = 0x18A
    RFL = 0x38A
    RFR = 0x48A
    RRL = 0x58A
    RRR = 0x68A

def convert_mf4_to_asc(mf4_path):
    """
        Function to convert MF4 file to new ASC file (old file is not deleted)
        :param mf4_path Path to the input MF4 file
        :return: Creates new ASC file with the same name as input file, but with .asc extension
        """
    try:
        # Load the MF4 file
        mdf = MDF(mf4_path)
        # Export to ASC format
        mdf.export('asc', mf4_path)
        print(f"Converting {mf4_path} to ASC format...")
        print(f"Successfully converted {mf4_path} to ASC format.")
        return re.split(r'\.mf4|\.MF4', mf4_path)[0] + '.asc'
    except Exception as e:
        HTML_Logger.ReportYellowMessage(f"Error during converting {mf4_path} to ASC format!!!")
        HTML_Logger.ReportRedMessage(e)
        HTML_Logger.Show_HTML_Report()
        raise f"Error during converting {mf4_path} to ASC format!!!"

# Function delete specific header information
def remove_headers(data) -> list:
    """
        Function to remove header from bytearray data
        :param inout bytearray
        :return: bytearray without headers
        """
    # Check for the pattern [0x10, 0x00] at the beginning
    if data[:2] == ['0x10', '0x00']:
        data = data[6:]
    else:
        # Check for the pattern [0x1X, 0xXX] at the beginning
        pattern = r"\['0x1[0-9A-Fa-f]', '0x[0-9A-Fa-f]{2}'\]"
        str_data_list = str(data[0:2])

        # Check for a match
        match = re.search(pattern, str_data_list)
        if match:
            del data[:2]
        else:
            print("No match found.")

    return data

def extract_bytearrays_signals(timestamps: list, data: list[list[int]], id: RADAR_ID, max_obj_nr: int) -> List[pd.DataFrame]:
    """
        Function to convert bytearrays in meaningful data as pd.Dataframe
        :param timestamps Signals timestamps (list)
        :param data 2D list of the bytearrays
        :return: list of dataframes each containing all signals and their values at specific timestamp
    """
    byte_arrays_dfs_list = []

    for index, single_data in enumerate(data):
        bytearray = (ctypes.c_ubyte * len(single_data)).from_buffer_copy(bytes(single_data))
        # Create DataFrame with ByteArray from file
        input_df = pd.DataFrame({
            'Signal Name': "ByteArray",
            'Timestamp': timestamps[index],
            'Byte Array': [bytearray]
        })
        
        # Read all signal values from the ByteArray of the specific radar
        if id == RADAR_ID.RFC:
            df_data = ra6.read_all_signal_values(input_df,"RFC",max_obj_nr)
        elif id == RADAR_ID.RFL:
            df_data = ra6.read_all_signal_values(input_df,"RFL",max_obj_nr)
        elif id == RADAR_ID.RFR:
            df_data = ra6.read_all_signal_values(input_df,"RFR",max_obj_nr)
        elif id == RADAR_ID.RRL:
            df_data = ra6.read_all_signal_values(input_df,"RRL",max_obj_nr)
        elif id == RADAR_ID.RRR:
            df_data = ra6.read_all_signal_values(input_df,"RRR",max_obj_nr)
        else:
            print("Invalid radar ID")

        # Example of how to read specific signals
        #signal_names = [
        #    "RFL_Object_SpiHdr_SensorOriginPointX",
        #    "RFL_Object_SpiHdr_SensorOriginPointY",
        #    "RFL_Object_SpiHdr_SensorOriginPointZ",
        #    "RFL_Object_ObjHdr_NumValidObjects",
        #    "RFL_Object_Obj1_Px",
        #    "RFL_Object_Obj2_Px"
        #]
        #df_data = ra6.read_specific_signal_values(input_df,signal_names)

        # Print the timestamp and update in the same line
        print(f"\rProcessing timestamp: {timestamps[index]} of {timestamps[-1]}", end="")
        byte_arrays_dfs_list.append(df_data)

    if byte_arrays_dfs_list:
        print("Successfully extracted all signals.")
        return generate_signal_dataframes(byte_arrays_dfs_list)
    else:
        HTML_Logger.ReportYellowMessage(f"No ID={hex(id.value)} in the provided log file!")
        return None


def generate_signal_dataframes(input_df: List[pd.DataFrame]):
    """
        Function separate every signal into dataframe with timestamps and values
        :param input_df list of dataframes
        :return: key-value pair of signal_name:related data
    """
    # Initialize a list to hold the new DataFrames
    new_dataframes = {}

    # Loop through each row index
    for i in range(len(input_df[0])):
        # Extract the i-th row from each dataframe and create a new DataFrame
        row_data = [df.iloc[i] for df in input_df]
        new_df = pd.DataFrame(row_data).reset_index(drop=True)
        key = new_df.loc[0, 'Signal Name']
        new_dataframes[key] = new_df

    # Display the new DataFrames
    for index, df in enumerate(new_dataframes.items()):
        print(f"DataFrame for row {index + 1}:\n{df}\n")
    return new_dataframes

def parse_asc(asc_file: str, id: RADAR_ID, objects_to_analyze: int, start_byte: str="0x1c", end_byte: str="0xcc"):
    """
        Function to parse given asc files into 2D with bytearray values and 1D list with timestamps

        :param asc_file: Asc log files to be parsed
        :param id: ID of the bytearray to be searching for (int)
        :param start_byte: Byte value of the bytearray start header (str)
        :param end_byte: Byte value of the bytearray end header (str)
        :return: 1D timestamps list and 2D signal list in hex format
    """
    asc_file = io.asc.ASCReader(asc_file)

    # Initialize a list to hold the new lists
    new_lists = []
    timestamps = []
    current_list = None

    # Iterate over each list in the input
    for asc_data in asc_file:
        is_starting_header = False
        if asc_data.arbitration_id == id.value and asc_data.channel == 1:
            formatted_hex_list = [f'0x{byte:02x}' for byte in asc_data.data]
            # Check if the current list starts with '0x1C'
            if formatted_hex_list[0] == start_byte:
                # If there is an active current list, save it before starting a new one
                is_starting_header = True
                if current_list is not None:
                    new_lists.append(current_list)

                # Start a new list
                current_list = []

            # If current list is not None, append items
            if current_list is not None:
                if is_starting_header:
                    formatted_hex_list = remove_headers(formatted_hex_list)
                else:
                    del formatted_hex_list[0]
                if formatted_hex_list[-1] == end_byte:
                    new_lists.append(current_list)
                    timestamps.append(asc_data.timestamp)
                    current_list = None  # Reset current list after appending
                else:
                    current_list.extend(formatted_hex_list)
                    #

    # If there is an active current list at the end, add it
    if current_list is not None:
        new_lists.append(current_list)

    # Print the result
    #for i, new_lst in enumerate(new_lists):
    #    with open("data.txt", 'a') as f:
    #        f.write(f"List {i}:{new_lst}\n")

    # Delete last entry if the bytearray is not full
    if len(new_lists[-1]) != len(new_lists[-2]):
        del new_lists[-1]
    #return new_lists
    return extract_bytearrays_signals(timestamps, [[int(hex_str, 16) for hex_str in inner_list] for inner_list in new_lists], id, objects_to_analyze)

if __name__ == "__main__":
    path = r"C:\Users\pep3sf4\Desktop\Test_mf4\SPA_Demo_20241127_153730_001\SPA_Demo_20241127_153730_001.asc"
    extracted_data = parse_asc(path, id=0x38a,start_byte="0x1c",end_byte="0xcc")
