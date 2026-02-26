import asammdf.blocks.utils
from asammdf import MDF, set_global_option
import time
import numpy as np
import pandas as pd
from pandas import DataFrame
import sys,os
import re
from typing import Union

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(script_dir, r"..\ReportGen"))
    import HTML_Logger
    #from input_parser import create_signal_dataframe
except:
    #from Platform.Python_Testing_Framework.TraceParser.input_parser import create_signal_dataframe
    import Platform.Python_Testing_Framework.ReportGen.HTML_Logger as HTML_Logger


set_global_option("raise_on_multiple_occurrences", False)
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class ChannelFinder:
    mdf_file: str
    mdf: MDF = field(init=False)

    def __post_init__(self):
        if not os.path.exists(self.mdf_file):
            HTML_Logger.ReportRedMessage(f"Log file '{self.mdf_file}' does not exist.")
            HTML_Logger.ReportOfflineTestStepFail()
            HTML_Logger.ReportFinalVerdict()
            HTML_Logger.Show_HTML_Report()
            raise FileNotFoundError(f"Log file '{self.mdf_file}' does not exist.")

        if self.mdf_file.lower().endswith('.mf4'):
            # Load the MDF file upon initialization
            start_time = time.time()
            print(f"Start parsing: {self.mdf_file}")
            self.mdf = MDF(self.mdf_file)
            end_time = time.time()
            # Calculate the elapsed time
            elapsed_time = end_time - start_time
            # Print the load time
            print(f"Time taken to load the MDF file: {elapsed_time:.2f} seconds")
        else:
            HTML_Logger.ReportRedMessage(f"Input file '{self.mdf_file}' must have a .mf4 extension.")
            HTML_Logger.Show_HTML_Report()
            raise ValueError(f"Input file '{self.mdf_file}' must have a .mf4 extension.")

    def list_channels(self) -> None:
        """List all available channels in the MDF file."""
        channel_list = [channel for channel in self.mdf.channels_db]

        # Write all available channels into txt file
        with open("output.txt", "w") as f:
            f.writelines(s + '\n' for s in channel_list)

    def find_channel(self, channel_name: Union[str, tuple[str]]) -> Optional[str]:
        """Find a specific channel by name."""
        try:
            if isinstance(channel_name, tuple):
                # Define the group name (path name)
                group_name = channel_name[1]

                # Iterate through all groups to find the group
                for group_index, channel_group in enumerate(self.mdf.groups):
                    # Check if the group name matches the Ethernet group name
                    if channel_group.channel_group.acq_name == group_name:
                        print(f"Found group: {group_name} at group index {group_index}")

                        # Extract
                        for channel_index, channel in enumerate(channel_group.channels):
                            if channel_name[2] in channel.name:
                                print(f"Extracting  frames from channel: {channel.name}")

                                # Get channel data
                                channel_data = self.mdf.get(group=group_index, index=channel_index)
                                if channel_data.source.path == channel_name[0]:
                                    # Print the raw Ethernet frames
                                    print(channel_data)
                                    return channel_data
            else:
                channel_data = self.mdf.get(channel_name)
                return channel_data

        except KeyError:
            HTML_Logger.ReportRedMessage(f"Channel {channel_name} not found!!!")
            HTML_Logger.ReportOfflineTestStepFail()
            HTML_Logger.ReportFinalVerdict()
            HTML_Logger.Show_HTML_Report()
            exit(0)
        except asammdf.blocks.utils.MdfException:
            HTML_Logger.ReportRedMessage(f"Channel {channel_name} not found!!!")
            HTML_Logger.ReportOfflineTestStepFail()
            HTML_Logger.ReportFinalVerdict()
            HTML_Logger.Show_HTML_Report()
            exit(0)

    # def search_channels_from_input_file(self) -> List[str]:
    #     """Search for channels specified in the channel file."""
    #     found_channels = []
    #     try:
    #         input_dataframe = create_signal_dataframe()
    #
    #         for row in input_dataframe.itertuples(index=False):
    #             result = self.find_channel(row.SignalName)
    #             found_channels.append((result, row.Maximum))
    #     except FileNotFoundError:
    #         found_channels.append(f"Channel file '{row.SignalName}' not found.")
    #
    #     return self.create_dataframes_for_channels_from_excel_input(found_channels)

    def get_channels(self, channels_input: List[str]) -> List[str]:
        """Search for channels as list input."""
        found_channels = []

        for channel in channels_input:
            result = self.find_channel(channel)
            if len(result.samples) != 0:
                found_channels.append(result)
            else:
                HTML_Logger.ReportRedMessage(f"Signal {channel} has no data (samples)!!!")
                HTML_Logger.ReportOfflineTestStepFail()
                HTML_Logger.ReportFinalVerdict()
                HTML_Logger.Show_HTML_Report()

        return self.create_dataframes_for_channels(found_channels)

    def get_channels_regex(self, channels_input: List[str]) -> List[str]:
        r"""
        Function to return a key value pair list of signals based on regex input

        Args:
            channels_input (List[str]): List of signals to be found in the mf4 file based on regex input
        Returns:
            List of Key:value pairs in format signal_name:pd.Dataframe
        Examples:
            get_channels_regex([r'^RF[A-Z]{1}_Loc\d{3}_Azimuth$'])
        """
        all_signals_obj = []
        # Get all signal names
        all_signals = self.mdf.channels_db
        for channel in channels_input:
            # Define a regex pattern
            pattern = re.compile(channel)  # Case-insensitive regex
            # Filter signals using the regex pattern
            matching_signals = [signal for signal in all_signals if pattern.search(signal)]
            all_signals_obj.extend(matching_signals)
        found_channels = []
        try:
            for signal_obj in all_signals_obj:
                result = self.find_channel(signal_obj)
                if len(result.samples) == 0:
                    HTML_Logger.ReportYellowMessage(f"Signal {signal_obj} has no data!!!")
                else:
                    found_channels.append(result)
        except FileNotFoundError:
            found_channels.append(f"Channel file '{channel}' not found.")

        return self.create_dataframes_for_channels(found_channels)

    def convert_bytearray_to_string_array(self, bytearray_array: np.ndarray) -> np.ndarray:
        """Convert a NumPy array of bytearray to a NumPy array of strings."""
        return np.array([bytes(x).decode('utf-8') for x in bytearray_array])

    def normalize_ndarray(self, arrays: List[np.ndarray]) -> List[bool]:
        results = []
        for arr in arrays:
            # Check if the first element is a bytearray
            if arr.size > 0:
                results.append(isinstance(arr[0], bytearray))
            else:
                results.append(False)  # Handle empty arrays
        return results

    def create_dataframes_for_channels_from_excel_input(self, found_channels: List[pd.DataFrame]) -> List[pd.DataFrame]:
        """Create separate DataFrames for each found channel."""
        channel_dataframes = {}
        dataframes = []
        for channel in found_channels:
            if channel is not None:
                # Create DataFrame for the channel's data
                df = pd.DataFrame({
                    'Signal Name': channel[0].name,
                    'Timestamp': channel[0].timestamps,
                    'Signal Value': channel[0].samples,
                    'Maximum': channel[1]
                })

                # Truncate the 'Timestamp' values to two decimal places
                df['Timestamp'] = df['Timestamp'].round(2)

                # Check if the first element in the 'Signal Value' is a bytearray
                is_first_bytearray = isinstance(df['Signal Value'].iloc[0], bytes)
                # Convert the bytearray column to string
                if is_first_bytearray:
                    df['Signal Value'] = df['Signal Value'].apply(lambda x: x.decode('utf-8'))
                dataframes.append(df)
                # channel_dataframes[channel.name] = df

        # combined_df = pd.concat(channel_dataframes.values(), ignore_index=True)
        return dataframes

    def create_dataframes_for_channels(self, found_channels: List[str]) -> dict[str, DataFrame]:
        """Create separate DataFrames for each found channel."""
        dataframes = {}
        for channel in found_channels:
            if channel is not None:
                # Create DataFrame for the channel's data
                df = pd.DataFrame({
                    'Signal Name': channel.name,
                    'Timestamp': channel.timestamps,
                    'Signal Value': channel.samples,
                })

                # Truncate the 'Timestamp' values to two decimal places
                df['Timestamp'] = df['Timestamp'].round(2)

                # Check if the first element in the 'Signal Value' is a bytearray
                is_first_bytearray = isinstance(df['Signal Value'].iloc[0], bytes)
                # Convert the bytearray column to string
                if is_first_bytearray:
                    df['Signal Value'] = df['Signal Value'].apply(lambda x: x.decode('utf-8'))
                dataframes[channel.name] = df

        return dataframes
