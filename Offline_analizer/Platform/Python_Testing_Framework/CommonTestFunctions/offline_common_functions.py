import sys, os
from enum import Enum
from typing import Union, Dict
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Any

try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(script_dir, r"..\CommonTestFunctions"))
    sys.path.append(os.path.join(script_dir, r"..\ReportGen"))
    import HTML_Logger
    from plotter import PlotlyVisualizer
    import numpy as np
except ImportError as e:
    print(f"Import error --> {e}")

# Define an enumeration for the conditions
class Condition(Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    WITHIN_RANGE = ","
    CONSTANT = "=="

@dataclass
class CommonFunc:

    @staticmethod
    def find_mf4_files(directory: str) -> List[str]:
        """
        Function to collect all mf4 files in given path

        Args:
            directory (str): Path to the folder containing mf4 files
        Returns:
            None
        Example:
            find_mf4_files(C:\\My_mf4_files)
        """

        path = Path(directory)
        mf4_files = [str(file) for file in path.rglob('*.mf4') if file.is_file() or file.name.lower().endswith('.mf4')]
        return list(mf4_files)

    def create_plot(self, signal_data, path_to_the_tc) -> None:
        r"""
        Function to create signal plot

        Args:
            signal_data (DataFrame): Dataframe for the signal to be plotted
            path_to_the_tc (str): Path to the TC location

        Returns:
            None

        Example:
            obj = CommonFunc()\n
            obj.create_plot(signal_dataframe, "D:\Tests\Testcase.py)
        """
        plt = PlotlyVisualizer(signal_data)
        plt.line_plot("Timestamp", "Signal Value", title=f"{signal_data.at[1, 'Signal Name']}", save_as_html=True, path=path_to_the_tc)
        HTML_Logger.ReportHTMLLink("Plot", path_to_file=rf"{signal_data.at[1, 'Signal Name']}.html", hyperlink=True)

    def create_combined_plot(self, channels: pd.DataFrame, tc_path: str) -> None:
        r"""
        Function to create combined plot of dataframe with different signals

        Args:
            channels (DataFrame): Dataframe with more than one signal
            tc_path (str): Path to the TC location

        Returns:
            None

        Example:
            obj = CommonFunc()\n
            obj.create_plot(signal_dataframe, "D:\Tests\Testcase.py)
        """
        # Creates combined plot for all data
        dataframes = []  # This will store all your DataFrames
        for key, value in channels.items():
            dataframes.append(value)
        result = pd.concat(dataframes, axis=0, ignore_index=True)
        self.create_plot(result, tc_path)

    def check_alive_counter_consistency(self, dataframe: pd.DataFrame) -> None:
        """
        Function to check alive counter consistency\n
          - Check for repeated values in a sequence (Example: 0,1,2,3,4,4,5)\n
          - Check missing values in a sequence (Example: 1,2,4,5,6)

        Args:
            dataframe (DataFrame): The DataFrame containing 'Timestamp' and 'Signal Value' columns.

        Returns:
            None

        Example:
            obj = CommonFunc()\n
            obj.check_alive_counter_consistency(signal_dataframe)
        """

        # Identify consecutive repetitions
        consecutive_repeats = []
        for i in range(1, len(dataframe)):
            if dataframe['Signal Value'][i] == dataframe['Signal Value'][i - 1]:
                # Add to consecutive repeats if they are the same
                if not consecutive_repeats or consecutive_repeats[-1][0] != dataframe['Signal Value'][i]:
                    consecutive_repeats.append(
                        (dataframe['Signal Value'][i], [dataframe['Timestamp'][i - 1], dataframe['Timestamp'][i]]))
                else:
                    consecutive_repeats[-1][1].append(dataframe['Timestamp'][i])

        # Print consecutive repetitions
        if consecutive_repeats:
            HTML_Logger.ReportRedMessage(f"Consecutive repeated AliveCounter values found for {dataframe['Signal Name'][i]}")
            for value, ts in consecutive_repeats:
                HTML_Logger.ReportRedMessage(f"Value = {value} : Timestamp: {ts}")
            HTML_Logger.ReportOfflineTestStepFail()
            failed = True
        else:
            HTML_Logger.ReportWhiteMessage(f"No consecutive AliveCounter repetitions found in the log file for {dataframe['Signal Name'][i]}.")
            HTML_Logger.ReportOfflineTestStepPass()

        # Check for None values and print their timestamps
        none_timestamps = dataframe[dataframe['Signal Value'].isnull()]['Timestamp'].tolist()

        if none_timestamps:
            HTML_Logger.ReportRedMessage(f"Timestamp where AliveCounter is not received for for {dataframe['Signal Name'][i]} : {none_timestamps}")
            HTML_Logger.ReportOfflineTestStepFail()
        else:
            HTML_Logger.ReportWhiteMessage(
                f"AliveCounter is received for every timestamp in the log file for {dataframe['Signal Name'][i]}.")
            HTML_Logger.ReportOfflineTestStepPass()


    def check_incrementing(self, df: pd.DataFrame, max_value: int) -> None:
        """
        Check if the 'Signal Value' column in the DataFrame is properly incrementing,
        allowing for a repeat from min to max after reaching the maximum value.
        Print pairs of (Timestamp: Signal Value) where the pattern is not correct.

        Args:
            max_value (int): Maximum value of counter before reset
            df (DataFrame): The DataFrame containing 'Timestamp' and 'Signal Value' columns.

        Returns:
            None

        Example:
            obj = CommonFunc()\n
            obj.check_incrementing(signal_dataframe, 14)
        """

        HTML_Logger.ReportWhiteMessage(f"Check incrementing pattern of {df['Signal Name'].iloc[0]} from 0 to {max_value}.")
        signal_values = df["Signal Value"].tolist()
        timestamps = df["Timestamp"].tolist()

        failed = False
        for i in range(1, len(signal_values)):
            if signal_values[i] <= signal_values[i - 1]:
                # Check if the pattern is allowed to repeat
                if signal_values[i] < signal_values[i - 1] and signal_values[i - 1] == max_value:
                    # Allow repeat from min to max
                    continue
                HTML_Logger.ReportRedMessage(f"Pattern violation at Timestamp: {timestamps[i]} - Signal Value: {signal_values[i]}")
                failed = True
        if failed:
            HTML_Logger.ReportOfflineTestStepFail()
        else:
            HTML_Logger.ReportOfflineTestStepPass()


    def check_decrementing(self, df: pd.DataFrame, min_value: int):
        """
        Check if the 'Signal Value' column in the DataFrame is properly decrementing,
        allowing for a repeat from max to min after reaching the minimum value.
        Print pairs of (Timestamp: Signal Value) where the pattern is not correct.

        Args:
            min_value (int): Minimum value of counter before reset
            df (DataFrame): The DataFrame containing 'Timestamp' and 'Signal Value' columns.

        Returns:
            None

        Example:
            obj = CommonFunc()\n
            obj.check_decrementing(signal_dataframe, 0)
        """
        HTML_Logger.ReportWhiteMessage(f"Check incrementing pattern of {df['Signal Name'].iloc[0]} from 14 to {min_value}.")
        signal_values = df["Signal Value"].tolist()
        timestamps = df["Timestamp"].tolist()

        failed = False
        for i in range(1, len(signal_values)):
            if signal_values[i] >= signal_values[i - 1]:
                # Check if the pattern is allowed to repeat
                if signal_values[i] > signal_values[i - 1] and signal_values[i - 1] == min_value:
                    # Allow repeat from max to min
                    continue
                HTML_Logger.ReportRedMessage(f"Pattern violation at Timestamp: {timestamps[i]} - Signal Value: {signal_values[i]}")
                failed = True
        if failed:
            HTML_Logger.ReportOfflineTestStepFail()
        else:
            HTML_Logger.ReportOfflineTestStepPass()


    def check_pattern_with_delta(self, dataframe: pd.DataFrame,
                                  initial_value: Union[int, float]=0,
                                  delta_value: Union[int, float]=1,
                                  max_value: Union[int, float]=14,
                                  decrement: bool=False) -> None:
        """
        Checks whether the 'Signal Value' in the given DataFrame increments consistently
        up to a specified max_value, starting from delta_value when exceeding max_value.

        Args:
            dataframe (pd.Dataframe): The DataFrame containing 'Signal Value', 'Timestamp', and 'Signal Name'.
            initial_value (int, float, optional): Initial value expected when max_value is reached. Default = 0
            delta_value (int,float): The step with which the values shall change. Default = 1
            max_value (int,float): The maximum value before resetting to initial_value.Default = 14
            decrement (bool, optional): Check for decrementing pattern.Default = False

        Returns:
            None

        Examples:
            obj = CommonFunc()\n
            obj.check_pattern_with_delta(signal_dataframe, 0, 1, 14)
        """

        n = len(dataframe)
        failed = False

        # Start checking from the first index
        current_value = dataframe["Signal Value"].iloc[0]

        # Check the incrementing pattern to max_value

        HTML_Logger.ReportWhiteMessage(f"Check incrementing pattern of {dataframe['Signal Name'].iloc[0]} from "
                                       f"{initial_value} to {max_value} with delta {delta_value}")

        error_df = pd.DataFrame(columns=['Signal Name', 'Timestamp', 'Expected Value', 'Actual Value'])
        for i in range(n):
            if dataframe["Signal Value"].iloc[i] != current_value:
                HTML_Logger.ReportRedMessage(f"Increment is NOT consistent for {dataframe['Signal Name'].iloc[i]}")
                HTML_Logger.ReportRedMessage(
                    f"Expected value [{current_value}]"
                    f"| Found [{dataframe['Signal Value'].iloc[i]}]"
                    f"| Timestamp [{dataframe['Timestamp'].iloc[i]}]")

                # Create error dataframe
                error_df_len = len(error_df)
                if error_df_len == 0:
                    index = 0
                else:
                    index += 1
                error_df.loc[index] = [dataframe['Signal Name'].iloc[i], dataframe['Timestamp'].iloc[i], dataframe['Signal Value'].iloc[i], current_value]
                failed = True

            # Increment or decrement the expected value
            if decrement:
                current_value -= delta_value
            else:
                current_value += delta_value

            # Reset to initial_value if it exceeds max_value
            if decrement:
                if current_value == max_value - 1:
                    current_value = initial_value
            else:
                if current_value > max_value:
                    current_value = initial_value

        if not failed:
            HTML_Logger.ReportWhiteMessage(f"Increment is consistent for {dataframe['Signal Name'].iloc[0]}")
            HTML_Logger.ReportOfflineTestStepPass()
        else:
            HTML_Logger.ReportOfflineTestStepFail()


    def _filter_dataframe(self, signal_data: pd.DataFrame,
                         start_time: Union[int,float],
                         end_time: Union[int,float]) -> pd.DataFrame:
        """
        Returns a filtered dataframe based given time range.

        Args:
            signal_data (pd.Dataframe): DataFrame with columns ['Signal Name', 'Timestamp', 'Signal Value']
            start_time (int, float): Start of the timestamp range
            end_time (int, float): End of the timestamp range

        Returns:
             Dataframe with Timestamp as keys and Signal Value as values

        Examples:
            obj = CommonFunc()\n
            obj.filter_dataframe(signal_dataframe, 0, 0)\n
            0,0 - all range | x,0 - from x:end | 0,x - beginning:x | x,x - defined range
        """

        # Filter the DataFrame based on the TimeStamp range
        if end_time == 0:
            # Get the last row in the DataFrame
            last_time = signal_data['Timestamp'].iloc[-1]
            if start_time > last_time:
                HTML_Logger.ReportRedMessage(f"Wrong range for {signal_data['Signal Name'].iloc[0]}")
                HTML_Logger.ReportRedMessage(f"Expected start_timestamp={start_time} must be < end_timestamp={last_time}.")
                HTML_Logger.Show_HTML_Report()
            else:
                return signal_data[(signal_data['Timestamp'] >= start_time) & (signal_data['Timestamp'] <= last_time)]
        elif start_time == end_time:
            # Find rows where Values are greater than or equal to the specified value
            filtered_df = signal_data[signal_data['Timestamp'] >= start_time]

            if not filtered_df.empty:
                # If there are matching values, return the first match wrapped in a DataFrame
                return filtered_df.head(1)
            else:
                # If no match, find the closest higher value
                closest_higher = filtered_df[filtered_df['Timestamp'] > start_time]
                if not closest_higher.empty:
                    return closest_higher.loc[[closest_higher['Timestamp'].idxmin()]]  # Return as DataFrame
                else:
                    return pd.DataFrame()  # Return an empty DataFrame if no higher value is found
        else:
            return signal_data[(signal_data['Timestamp'] >= start_time) & (signal_data['Timestamp'] <= end_time)]


    def get_signal_value(self, signal_data: pd.DataFrame,
                         start_time: Union[int,float]=0,
                         end_time: Union[int,float]=0,
                         convert_to_dict=False) -> Dict[str, Union[str, float]] or pd.DataFrame:
        """
        Returns a dictionary or DataFrame of TimeStamp:Value for the given time range.

        Args:
            signal_data (pd.Dataframe): DataFrame with columns ['Signal Name', 'Timestamp', 'Signal Value']
            start_time (int, float, optional): Start of the timestamp range. Default=0
            end_time (int, float, optional) : End of the timestamp range. Default=0
            convert_to_dict (bool): Convert output to dictionary. Default=False
        Returns:
            DataFrame or Dictionary with Timestamp as keys and Signal Value as values
        Examples:
            obj = CommonFunc()\n
            obj.get_signal_value(signal_data, 0, 0)
            """

        filtered_df = self._filter_dataframe(signal_data, start_time, end_time)

        # Create a dictionary from the filtered DataFrame
        if convert_to_dict:
            result = dict(zip(filtered_df['Timestamp'], filtered_df['Signal Value']))
            return result

        return filtered_df.reset_index(drop=True)

    def _count_decimal_places(self, value):
        """Counts the number of decimal places in a float value."""
        str_value = str(value)
        if '.' in str_value:
            return len(str_value.split('.')[1])
        return 0

    def _save_df_as_html(self, df):
        # Convert DataFrame to HTML
        html_output = df.to_html()

        # save to an HTML file
        with open('output.html', 'w') as f:
            f.write(html_output)

    def check_signal_update(self, signal_data: pd.DataFrame,
                            condition: Condition,
                            value: Union[int, float, str] = None,
                            signal_range: Union[List[int],List[float]] = None,
                            single_occurrence: bool=False,
                            plot: bool = False,
                            tc_path: str = None,
                            full_result: bool = False):
        """
        Function to check signal value

        Args:
            signal_data (pd.Dataframe): Dataframe of the signal to be checked
            condition (Enum.Condition): Condition to be checked - EQUAL, NOT_EQUAL, CONSTANT and RANGE
            value (int, float, str): Value to be checked
            signal_range (int, float): Signal range to be checked
            single_occurrence (bool): Find only the first occurrence of the searched value. Default=False
            plot (bool): Create a plot for the input signal
            tc_path (str): Full path to the test cases (needed only if plot=True)
            full_result (bool): Output all timestamps where the "value" was found, not only header and tail of the DF
        Returns:
            None
        Examples:
            obj = CommonFunc()\n
            obj.check_signal_update(signal_data, 5) - check for value in entire dataframe\n
            obj.check_signal_update(signal_data, 5, single_occurrence=True) - check first expected value in the dataframe\n
            obj.check_signal_update(signal_data, signal_range=[5,10]) - check range. In the example 10 is excluded!!!\n
        """


        if value or value == 0 or value == 0.0:
            rounding = self._count_decimal_places(value)
        else:
            rounding = self._count_decimal_places(signal_range[0])

        if condition.name == "EQUALS":
            HTML_Logger.ReportWhiteMessage(f"Expected Value: {signal_data.at[1, 'Signal Name']} {condition.value} {value}")
            # Find the first occurrence of the value in the specified column
            if not isinstance(value, str):
                value_extract = signal_data[signal_data['Signal Value'].round(rounding) == value]
            else:
                value_extract = signal_data[signal_data['Signal Value'] == value]
            # Check if any occurrence was found and return the first row
            if not value_extract.empty:
                if single_occurrence:
                    html_output = value_extract.iloc[[0]].to_html() # Use double brackets to keep it as a DataFrame
                elif full_result:
                    html_output = value_extract.to_html()
                else:
                    combined_df = pd.concat([value_extract.head(), value_extract.tail()])
                    html_output = combined_df.to_html()
                if plot:
                    self.create_plot(signal_data, tc_path)
                HTML_Logger.ReportDF_HTML(html_output)
                HTML_Logger.ReportOfflineTestStepPass()
            else:
                HTML_Logger.ReportRedMessage(f"Expected value not found.")
                HTML_Logger.ReportOfflineTestStepFail()

        elif condition.name == "NOT_EQUALS":
            HTML_Logger.ReportWhiteMessage(f"Expected Value: {signal_data.at[1, 'Signal Name']} {condition.value} {value}")
            # Find the first occurrence of the value in the specified column
            if not isinstance(value, str):
                value_extract = signal_data[signal_data['Signal Value'].round(rounding) == value]
            else:
                value_extract = signal_data[signal_data['Signal Value'] == value]
            # Check if any occurrence was found and return the first row
            if value_extract.empty:
                HTML_Logger.ReportOfflineTestStepPass()
            else:
                if single_occurrence:
                    html_output = value_extract.iloc[[0]].to_html()  # Use double brackets to keep it as a DataFrame
                else:
                    HTML_Logger.ReportRedMessage(f"Value was found in the log.")
                    html_output = value_extract.head().to_html()
                HTML_Logger.ReportDF_HTML(html_output)
                HTML_Logger.ReportOfflineTestStepFail()

        elif condition.name == "WITHIN_RANGE":
            HTML_Logger.ReportWhiteMessage(f"Expected Range: {signal_data.at[1, 'Signal Name']} = {signal_range}")
            # Find the first occurrence of the value in the specified column
            if not isinstance(value, str):
                value_extract = signal_data[(signal_data['Signal Value'].round(rounding) >= signal_range[0]) & (signal_data['Signal Value'] <= signal_range[1])]
            else:
                value_extract = signal_data[(signal_data['Signal Value'].round(rounding) >= signal_range[0]) & (signal_data['Signal Value'] <= signal_range[1])]
            # Check if any occurrence was found and return the first row
            if not value_extract.empty:
                if single_occurrence:
                    html_output = value_extract.iloc[[0]].to_html() # Use double brackets to keep it as a DataFrame
                elif full_result:
                    html_output = value_extract.to_html()
                else:
                    combined_df = pd.concat([value_extract.head(), value_extract.tail()])
                    html_output = combined_df.to_html()
                HTML_Logger.ReportDF_HTML(html_output)
                HTML_Logger.ReportOfflineTestStepPass()
            else:
                HTML_Logger.ReportRedMessage(f"Expected value not found.")
                HTML_Logger.ReportOfflineTestStepFail()

        if condition.name == "CONSTANT":
            HTML_Logger.ReportWhiteMessage(f"Expected Constant Value: {signal_data.at[1, 'Signal Name']} {condition.value} {value}")
            # Find the first occurrence of the value in the specified column
            if not isinstance(value, str):
                signal_data['Signal Value'] = signal_data['Signal Value'].round(rounding)
                # Find the first occurrence
                first_occurrence_index = signal_data[signal_data['Signal Value'].round(rounding) == value].index[0]
            else:
                first_occurrence_index = signal_data[signal_data['Signal Value'] == value].index[0]

            # Check if all values from the first occurrence to the end are 'value'
            subset = signal_data.loc[first_occurrence_index:, 'Signal Value']
            # Check if any value is not 'value'
            if not (subset == value).all():
                mismatched_rows = signal_data.loc[first_occurrence_index:][subset != value]
            else:
                mismatched_rows = pd.DataFrame()

            # Check if any occurrence was found and return the first row
            if not mismatched_rows.empty:
                if single_occurrence:
                    html_output = mismatched_rows.iloc[[0]].to_html() # Use double brackets to keep it as a DataFrame
                elif full_result:
                    html_output = mismatched_rows.to_html()
                else:
                    combined_df = pd.concat([mismatched_rows.head(), mismatched_rows.tail()])
                    html_output = combined_df.to_html()
                HTML_Logger.ReportDF_HTML(html_output)
                HTML_Logger.ReportOfflineTestStepFail()
            else:
                HTML_Logger.ReportGreenMessage(f"Expected value is constant in the log.")
                HTML_Logger.ReportOfflineTestStepPass()



    def parse_dem_events(self, dem_events_file: str, exclusion_list: str) -> Dict[str | Any, str]:

        """
        Function to return a list of DEM events from given C header file (.h)

        Args:
            dem_events_file (str): C header file containing all dem events
            exclusion_list (str): text file with DEM events which shall be excluded from the check
        Returns:
            Key:value pairs in format DEM_EVENT:ID
        Examples:
            obj = CommonFunc()\n
            obj.parse_dem_events(DEM_HEADER_FILE, DEM_EXCLUSION_LIST)
          """
        # Dictionary to hold the key-value pairs
        key_value_pairs = {}

        if exclusion_list != "":
            excluded_dems = self._parse_exclusion_file(exclusion_list)

        # Regular expression to match the lines
        pattern = re.compile(r"#define DemConf_DemEventParameter_(\w+)\s+(\d+)")

        # Read from the file
        with open(dem_events_file, 'r') as file:
            for line in file:
                match = pattern.match(line.strip())
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if excluded_dems and key in excluded_dems:
                        continue
                    else:
                        key_value_pairs[key] = f"_Dem_AllEventsStatusByte._{value}_"

        return key_value_pairs

    def _parse_exclusion_file(self, exclusion_list: str):

        """
        Function to return a list of DEM events which shall be excluded from the check

        Args:
          exclusion_list (str): text file with DEM events which shall be excluded from the check
        Returns:
          list of DEM events which shall be excluded from the check
        Examples:
            obj = CommonFunc()\n
            obj.parse_exclusion_file(exclusion_list)
        """
        pattern = re.compile(r"#define DemConf_DemEventParameter_(\w+)\s+(\d+)")

        excluded_dems = []
        # Read from the file
        with open(exclusion_list, 'r') as file:
            for line in file:
                match = pattern.match(line.strip())
                if match:
                    key = match.group(1)
                    excluded_dems.append(key)

        return excluded_dems

    def check_dem_events(self, channel_df: pd.DataFrame, dem_event: str) -> None:
        """
        Function to check DEM events status in log file, based on Dem_Cfg_EventId.h

        Args:
            channel_df (pd.Dataframe): Dataframe containing the DEM event data
            dem_event (str): DEM event name
        Returns:
            List of failed DEM events (first byte, Bit0 => This Bit is “testFailed”)
        Examples:
            obj = CommonFunc()\n
            obj.check_dem_events(dem_event_dataframe, dem_event_X)
        """
        # Filter rows where the first bit is 1
        filtered_df = channel_df[channel_df['Signal Value'].apply(self._check_first_bit)]

        # Concatenate if multiple rows found (this will not change the DataFrame)
        if not filtered_df.empty:
            HTML_Logger.ReportRedMessage(f"{dem_event} -> testFailed")
            html_output = filtered_df.to_html()  # Use double brackets to keep it as a DataFrame
            HTML_Logger.ReportOfflineTestStepFail()
            HTML_Logger.ReportDF_HTML(html_output)
        else:
            HTML_Logger.ReportGreenMessage(f"{dem_event} - PASSED")
            HTML_Logger.ReportOfflineTestStepPass()

    def _check_first_bit(self, value):
        # Convert integer value to byte
        byte_value = value.to_bytes(1, byteorder='big')
        # Check if the first bit is 1
        return (byte_value[0] & 0b10000000) != 0


    def check_signal_dependency(self, activation_signal_df: pd.DataFrame,
                                triggered_signal_df: pd.DataFrame,
                                activation_value: Union[int, float],
                                triggered_value: Union[int, float],
                                timeout: int=None):
        """
        Function to check the dependency between two signal with timeout as an option

        Args:
            activation_signal_df (pd.Dataframe): Dataframe of the activation signal
            triggered_signal_df (pd.Dataframe): Dataframe of the triggered signal
            activation_value (int, float): Activation signal value to find
            triggered_value (int, float):  Triggered signal value to find
            timeout (int): Maximum timeout between triggering of activation signal and detection of the triggered value

        Returns:
            Dataframe table with correlation between activaiton signal and triggered signal
        Examples:
            obj = CommonFunc()\n
            obj.check_signal_dependency(data_input, data_to_check, 5, 100, 200)
        """

        # Define the column names
        columns = ['Signal Name', 'Timestamp', 'Value', 'Expected Timeout', 'Actual Reaction Time']
        # Create the empty DataFrame
        result_df = pd.DataFrame(columns=columns)

        # Find the index of the first occurrence of the value
        first_occurrence_index = activation_signal_df[activation_signal_df['Signal Value'] == activation_value].index

        activation_signal = activation_signal_df.at[1, 'Signal Name']
        triggered_signal = triggered_signal_df.at[1, 'Signal Name']

        # Check if the value exists and retrieve the corresponding Timestamp
        if not first_occurrence_index.empty:
            first_timestamp = activation_signal_df.loc[first_occurrence_index[0], 'Timestamp']
            print(f"The first occurrence of {activation_signal}={activation_value} has a Timestamp of: {first_timestamp}")
        else:
            HTML_Logger.ReportRedMessage(f"{activation_signal} = {activation_value} was not found in the log file.")
            HTML_Logger.ReportOfflineTestStepFail()
            return
        # Find the value in df2 based on first_timestamp
        if first_timestamp is not None:
            # Check if first_timestamp exists in df2
            result = triggered_signal_df[triggered_signal_df['Timestamp'] == first_timestamp]

            if not result.empty:
                signal_value = result['Signal Value'].values[0]
                print(f"The Signal Value of {triggered_signal} at Timestamp {first_timestamp} is: {signal_value}")

                # Print the absolute difference
                abs_difference = abs(first_timestamp - first_timestamp)  # This will be 0
                closest_timestamp = first_timestamp
                print(f"Absolute difference: {abs_difference}")
            else:
                # Find the closest upper timestamp
                closest_upper = triggered_signal_df[triggered_signal_df['Timestamp'] > first_timestamp]

                if not closest_upper.empty:
                    closest_timestamp = closest_upper['Timestamp'].min()  # Get the minimum upper timestamp
                    signal_value = triggered_signal_df[triggered_signal_df['Timestamp'] == closest_timestamp]['Signal Value'].values[0]
                    print(f"No exact match found. The closest upper Timestamp is {closest_timestamp} with Signal Value: {signal_value}")

                    # Print the absolute difference
                    abs_difference = abs(first_timestamp - closest_timestamp)
                    print(f"Absolute difference: {abs_difference}")
                else:
                    print(f"No upper timestamps found in df2.")
        else:
            print("No valid first timestamp found.")

        # Add a value in 'Signal Name' for the first row
        result_df.loc[0] = [activation_signal, first_timestamp, activation_value, None, None]
        result_df.loc[1] = [triggered_signal, closest_timestamp, triggered_value, str(timeout) + ' [ms]', str(abs_difference) + ' [ms]']
        html_output = result_df.to_html()
        HTML_Logger.ReportDF_HTML(html_output)
        if abs_difference > timeout/1000:
            HTML_Logger.ReportRedMessage(f"Expected max timeout = {timeout/1000}ms. Actual timeout = {abs_difference}ms")
            HTML_Logger.ReportOfflineTestStepFail()
        else:
            HTML_Logger.ReportOfflineTestStepPass()


    def check_dataframes_for_zero(self, dataframes: List[pd.DataFrame], threshold_percent: int):
        """
        Check if the percentage of dataframes without the value 0 in the 'Signal Value' column
        meets the specified threshold.

        Args:
            dataframes (List[pd.Dataframe]): List of pandas DataFrames
            threshold_percent (int): Percentage threshold (0 to 100)

        Returns:
            None
        """

        if not isinstance(threshold_percent, int):
            HTML_Logger.ReportRedMessage("Threshold value shall be of type INT.")
            raise ValueError("Threshold value shall be of type INT.")

        # Count the number of dataframes that do not contain 0 in the 'Signal Value' column
        no_zero_count = 0
        for key, df in dataframes.items():
            if 'Signal Value' not in df.columns:
                raise ValueError("One or more dataframes do not contain the 'Signal Value' column.")
            # Calculate the mean of the 'Signal Value' column
            mean_value = df['Signal Value'].mean()
            if mean_value != 0:
                no_zero_count += 1

        # Calculate the percentage of dataframes without 0
        percent_without_zero = (no_zero_count / len(dataframes)) * 100

        # Check if the percentage meets the threshold
        if percent_without_zero >= threshold_percent:
            HTML_Logger.ReportGreenMessage(f"{percent_without_zero:.2f}% of valid input signals are updating. (Threshold: {threshold_percent}%).")
            HTML_Logger.ReportOfflineTestStepPass()
        else:
            HTML_Logger.ReportRedMessage(f"Only {percent_without_zero:.2f}% of valid input signals are updating. (Threshold: {threshold_percent}%).")
            HTML_Logger.ReportOfflineTestStepFail()


    def check_cycle_time(self, mdf_object: object, sources : List[str]):
        for group_index, group in enumerate(mdf_object.groups):
            try:
                if group.channel_group.acq_source.name and group.channel_group.acq_source.name in sources:
                    if "_LocationHdrA" in group.channel_group.acq_name or "_LocationHdrB" in group.channel_group.acq_name:
                        # Get the master channel timestamps for the group
                        timestamps = mdf_object.get_master(group_index)
                        # Calculate the time differences between consecutive samples
                        if len(timestamps) >= 2:
                            HTML_Logger.ReportWhiteMessage(f"Found samples: {len(timestamps)}")
                            time_diffs = np.diff(timestamps) * 1000
                            avg_interval_ms = time_diffs.mean()

                            # Find cycle times outside the acceptable range (50 - 100ms)
                            invalid_cycles = [(i, ct) for i, ct in enumerate(time_diffs) if ct < 46 or ct > 86]

                            # Print the group index and sampling rate
                            HTML_Logger.ReportWhiteMessage(f"Group Index: {group_index}")
                            HTML_Logger.ReportWhiteMessage(f"Group : {group.channel_group.acq_name}")
                            HTML_Logger.ReportWhiteMessage(f"Transmission min = {time_diffs.min():.2f} ms")
                            HTML_Logger.ReportWhiteMessage(f"Transmission max = {time_diffs.max():.2f} ms")
                            HTML_Logger.ReportWhiteMessage(f"Average Sampling Interval: {avg_interval_ms:.2f} ms")
                            HTML_Logger.ReportWhiteMessage(f"Violations (outside 46-86ms range): {len(invalid_cycles)}")

                            if len(invalid_cycles) != 0:
                                # Print details of violations
                                for index, ct in invalid_cycles:
                                    HTML_Logger.ReportWhiteMessage(f"Cycle time violation at index {index}: {ct:.2f} ms")
                                    HTML_Logger.ReportOfflineTestStepFail()
                            else:
                                HTML_Logger.ReportOfflineTestStepPass()
                            HTML_Logger.ReportWhiteMessage("-" * 40)

            except AttributeError:
                continue









