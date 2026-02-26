#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for Gen6 Project

import sys, os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger

try:
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
except:
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser

# Define a constant for log files, could be a single log or a directory
LOG = r"C:\TOOLS\Gen6_parcer\temp_folder" # Single log example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\SPA_Demo_20241218_101337_001.mf4"
def CycleStatus_CycleCounter_Check(Radar_Channels, Radar):
    trace = CommonFunc()
    HTML_Logger.ReportWhiteMessage(f"=> {Radar} Check")
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 1 and 2:  RPTS Performance & Health Check")
    HTML_Logger.ReportWhiteMessage(f"Signal_name: {Radar}.g_ConfigurationData.m_cycleStatus.m_status")
    cycleStatus_data = trace.get_signal_value(Radar_Channels["g_ConfigurationData.m_cycleStatus.m_status"], 0, 0)
    trace.check_signal_update(cycleStatus_data, Condition.CONSTANT, "EOk")
    HTML_Logger.ReportWhiteMessage(f"Signal_name: {Radar}.g_ConfigurationData.m_misc.m_cycleCounter")
    cycle_Counter_data = trace.get_signal_value(Radar_Channels["g_ConfigurationData.m_misc.m_cycleCounter"], 0, 0)
    trace.check_alive_counter_consistency(cycle_Counter_data)

def get_base_name(file_path):
    return os.path.basename(file_path)

def convert_pandas_ms_to_kmh(data):
    # Ensure the input is a valid DataFrame
    if data is None or not isinstance(data, pd.DataFrame):
        raise ValueError("Input data must be a valid pandas DataFrame.")
    
    # Create a copy of the DataFrame to avoid modifying the original
    data = data.copy()
    
    # Multiply the "Signal Value" column by 3.6 to convert m/s to km/h
    data['Signal Value'] = data['Signal Value'].astype(float) * 3.6
    
    return data


def save_dataframe_to_csv(dataframe, output_path):
    # Replace "." with "," in the "Timestamp" column
    if 'Timestamp' in dataframe.columns:
        dataframe['Timestamp'] = dataframe['Timestamp'].apply(lambda x: str(x).replace('.', ','))

    # Convert all numeric columns (integers and floats) to strings and replace "." with ","
    for column in dataframe.select_dtypes(include=['number']).columns:
        dataframe[column] = dataframe[column].apply(lambda x: str(x).replace('.', ',') if isinstance(x, float) else str(x))

    # Save the entire DataFrame to a CSV file with ";" as the separator
    dataframe.to_csv(output_path, sep=';', index=False)

def synch_data(dumpID_data, vxvref_data, MODID_data):
    """
    Synchronizes the data from three pandas DataFrames based on the Timestamp and Signal Value.

    Args:
        dumpID_data (list or pd.DataFrame): List of dictionaries or DataFrame containing the dumpID data.
        vxvref_data (list or pd.DataFrame): List of dictionaries or DataFrame containing the vxvref data.
        MODID_data (list or pd.DataFrame): List of dictionaries or DataFrame containing the MODID data.

    Returns:
        pd.DataFrame: A DataFrame containing the synchronized data with four columns:
                      'Timestamp', 'DumID value', 'vxvref value', and 'MODID value'.
        str: An error message if a timestamp delta exceeds ±0.1 seconds.
    """
    # Convert inputs to DataFrames if they are lists
    if isinstance(dumpID_data, list):
        dumpID_df = pd.DataFrame(dumpID_data)
    else:
        dumpID_df = dumpID_data

    if isinstance(vxvref_data, list):
        vxvref_df = pd.DataFrame(vxvref_data)
    else:
        vxvref_df = vxvref_data

    if isinstance(MODID_data, list):
        MODID_df = pd.DataFrame(MODID_data)
    else:
        MODID_df = MODID_data

    # Ensure Timestamps are floats
    dumpID_df['Timestamp'] = dumpID_df['Timestamp'].astype(float)
    vxvref_df['Timestamp'] = vxvref_df['Timestamp'].astype(float)
    MODID_df['Timestamp'] = MODID_df['Timestamp'].astype(float)

    # Perform a merge with a tolerance of ±0.1 seconds for dumpID and vxvref
    synchronized_df = pd.merge_asof(
        dumpID_df.sort_values('Timestamp'),
        vxvref_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )

    # Perform a merge with MODID data
    synchronized_df = pd.merge_asof(
        synchronized_df.sort_values('Timestamp'),
        MODID_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )

    # Check for rows where no match was found (NaN values in 'Signal Value_y' or 'Signal Value')
    if synchronized_df[['Signal Value_y', 'Signal Value']].isnull().any().any():
        print("Warning: Time delta exceeds ±0.1 seconds for some rows.")

    # Rename columns to match the desired output format
    synchronized_df = synchronized_df.rename(
        columns={
            'Signal Value_x': 'DumID value',
            'Signal Value_y': 'vxvref value',
            'Signal Value': 'MODID value'
        }
    )

    # Keep only the required columns
    synchronized_df = synchronized_df[['Timestamp', 'DumID value', 'vxvref value', 'MODID value']]

    return synchronized_df

def synch_data_mal(ego_speed_ms, Vehicle_acceleration_ms2, RotationRateYaw_rad_s,AzOOPCause_text,ElOOPCause_text):
    """
    Synchronizes the data from three pandas DataFrames based on the Timestamp and Signal Value.

    Args:
        ego_speed_ms (list or pd.DataFrame): List of dictionaries or DataFrame containing the ego_speed_ms data.
        Vehicle_acceleration_ms2, (list or pd.DataFrame): List of dictionaries or DataFrame containing the Vehicle_acceleration_ms2, data.
        RotationRateYaw_rad_s (list or pd.DataFrame): List of dictionaries or DataFrame containing the RotationRateYaw_rad_s data.
        AzOOPCause_text (list or pd.DataFrame): List of dictionaries or DataFrame containing the AzOOPCause_text data.
        ElOOPCause_text (list or pd.DataFrame): List of dictionaries or DataFrame containing the ElOOPCause_text data.

    Returns:
        pd.DataFrame: A DataFrame containing the synchronized data with four columns:
            - 'Timestamp': The synchronized timestamp.
            - 'ego_speed_ms': The ego speed in meters per second.
            - 'Vehicle_acceleration_ms2': The vehicle acceleration in meters per second squared.
            - 'RotationRateYaw_rad_s': The rotation rate in radians per second.

    """
    # Convert inputs to DataFrames if they are lists
    if isinstance(ego_speed_ms, list):
        ego_speed_ms_df = pd.DataFrame(ego_speed_ms)
    else:
        ego_speed_ms_df = ego_speed_ms

    if isinstance(Vehicle_acceleration_ms2, list):
        Vehicle_acceleration_ms2_df = pd.DataFrame(Vehicle_acceleration_ms2)
    else:
        Vehicle_acceleration_ms2_df = Vehicle_acceleration_ms2

    if isinstance(RotationRateYaw_rad_s, list):
        RotationRateYaw_rad_s_df = pd.DataFrame(RotationRateYaw_rad_s)
    else:
        RotationRateYaw_rad_s_df = RotationRateYaw_rad_s

    if isinstance(AzOOPCause_text, list):
        AzOOPCause_df = pd.DataFrame(AzOOPCause_text)
    else:
        AzOOPCause_df = AzOOPCause_text

    if isinstance(ElOOPCause_text, list):
        ElOOPCause_df = pd.DataFrame(ElOOPCause_text)
    else:
        ElOOPCause_df = ElOOPCause_text

    # Ensure Timestamps are floats
    ego_speed_ms_df['Timestamp'] = ego_speed_ms_df['Timestamp'].astype(float)
    Vehicle_acceleration_ms2_df['Timestamp'] = Vehicle_acceleration_ms2_df['Timestamp'].astype(float)
    RotationRateYaw_rad_s_df['Timestamp'] = RotationRateYaw_rad_s_df['Timestamp'].astype(float)
    AzOOPCause_df['Timestamp'] = AzOOPCause_df['Timestamp'].astype(float)
    ElOOPCause_df['Timestamp'] = ElOOPCause_df['Timestamp'].astype(float)

    # Perform a merge with a tolerance of ±0.1 seconds for ego_speed_ms and Vehicle_acceleration_ms2 data
    synchronized_df = pd.merge_asof(
        ego_speed_ms_df.sort_values('Timestamp'),
        Vehicle_acceleration_ms2_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )

    # Perform a merge with data RotationRateYaw
    synchronized_df = pd.merge_asof(
        synchronized_df.sort_values('Timestamp'),
        RotationRateYaw_rad_s_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )

    # Perform a merge with data RotationRateYaw
    synchronized_df = pd.merge_asof(
        synchronized_df.sort_values('Timestamp'),
        AzOOPCause_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )

        # Perform a merge with data RotationRateYaw
    synchronized_df = pd.merge_asof(
        synchronized_df.sort_values('Timestamp'),
        ElOOPCause_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest',
        tolerance=0.1
    )


    # Check for rows where no match was found (NaN values in 'Signal Value_y' or 'Signal Value')
    if synchronized_df[['Signal Value_y', 'Signal Value']].isnull().any().any():
        print("Warning: Time delta exceeds ±0.1 seconds for some rows.")

       # Rename columns to match the desired output format
    synchronized_df = synchronized_df.rename(
        columns={
            'Signal Value_x': 'ego_speed_ms',
            'Signal Value_y': 'Vehicle_acceleration_ms2',
            'Signal Value': 'RotationRateYaw_rad_s',
            'Decoded Text_x': 'AzOOPCause',
            'Decoded Text_y': 'ElOOPCause'
        }
    )

    # Keep only the required columns (adjust as needed)
    synchronized_df = synchronized_df[['Timestamp', 'ego_speed_ms', 'Vehicle_acceleration_ms2', 'RotationRateYaw_rad_s', 'AzOOPCause', 'ElOOPCause']]
    
    return synchronized_df

def analyze_synch_data(synch_data, min_vxvref, max_vxvref, tolerance=20):
    """
    Args:
        synch_data (pd.DataFrame): DataFrame with columns 'Timestamp', 'DumID value', and 'vxvref value'.
        min_vxvref (float): Minimum threshold for vxvref value.
        max_vxvref (float): Maximum threshold for vxvref value.
        tolerance (int): Number of consecutive failures required to flag as "fail".

    Returns:
        pd.DataFrame: A DataFrame with 'Signal Name', 'Timestamp', and 'Signal Value' columns indicating "pass" or "fail".
    """
    # Create a copy of the input DataFrame to avoid modifying the original
    result_df = synch_data.copy()

    # Apply thresholds to determine the expected DmpID value
    result_df['Expected DmpID'] = result_df['vxvref value'].apply(
        lambda x: 1 if x < min_vxvref else (2 if min_vxvref <= x <= max_vxvref else 3)
    )

    # Check if the actual DmpID value matches the expected value
    result_df['Threshold_check'] = result_df.apply(
        lambda row: "pass" if row['DumID value'] == row['Expected DmpID'] else "fail",
        axis=1
    )

    # Track consecutive failures dynamically based on the tolerance
    failure_count = 0
    consecutive_fail_flags = []
    for value in result_df['Threshold_check']:
        if value == "fail":
            failure_count += 1
        else:
            failure_count = 0  # Reset the counter on a "pass"
        consecutive_fail_flags.append(failure_count >= tolerance)

    # Add the consecutive failure flags to the DataFrame
    result_df['Consecutive_fail'] = consecutive_fail_flags

    # Update the 'Threshold_check' column to flag only rows with consecutive failures as "fail"
    result_df['Threshold_check'] = result_df.apply(
        lambda row: "fail" if row['Consecutive_fail'] else "pass",
        axis=1
    )

    # Filter rows where the test failed
    failed_rows = result_df[result_df['Threshold_check'] == "fail"]
    save_dataframe_to_csv(result_df , r"C:\TOOLS\Gen6_parcer\Radar_DmpID_check_results.csv")

    # Print timestamps where the test failed
    if not failed_rows.empty:
        print("Failed Timestamps:")
        print(failed_rows['Timestamp'].to_list())

    # Rename 'Threshold_check' to 'Signal Value' for the output
    result_df = result_df.rename(columns={'Threshold_check': 'Signal Value'})

    # Add a new column 'Signal Name' with the value 'DmpID_Check'
    result_df['Signal Name'] = 'DmpID_Check'

    # Return a DataFrame with 'Signal Name', 'Timestamp', and 'Signal Value' columns
    return result_df[['Signal Name', 'Timestamp', 'Signal Value']]

def MOD_ID_Check(synch_data, min_vxvref, max_vxvref, MOD_ID_1_list, MOD_ID_2_list, MOD_ID_3_list, consecutive_failures=10):
    """
    Args:
        synch_data (pd.DataFrame): DataFrame with columns 'Timestamp', 'vxvref value', and 'MODID value'.
        min_vxvref (float): Minimum threshold for vxvref value.
        max_vxvref (float): Maximum threshold for vxvref value.
        MOD_ID_1_list (list): List of valid MODID values for speeds below min_vxvref.
        MOD_ID_2_list (list): List of valid MODID values for speeds between min_vxvref and max_vxvref.
        MOD_ID_3_list (list): List of valid MODID values for speeds above max_vxvref.
        consecutive_failures (int): Number of consecutive failures required to flag as "fail".

    Returns:
        pd.DataFrame: A DataFrame with 'Signal Name', 'Timestamp', and 'Signal Value' columns indicating "pass" or "fail".
    """
    # Create a copy of the input DataFrame to avoid modifying the original
    result_df = synch_data.copy()

    # Determine the expected MODID list based on the vxvref value
    def get_expected_modid_list(vxvref):
        if vxvref < min_vxvref:
            return MOD_ID_1_list
        elif min_vxvref <= vxvref <= max_vxvref:
            return MOD_ID_2_list
        else:
            return MOD_ID_3_list

    # Check if the MODID value is in the expected list
    result_df['Threshold_check'] = result_df.apply(
        lambda row: "pass" if row['MODID value'] in get_expected_modid_list(row['vxvref value']) else "fail",
        axis=1
    )

    # Track consecutive failures
    failure_count = 0
    consecutive_fail_flags = []
    for value in result_df['Threshold_check']:
        if value == "fail":
            failure_count += 1
        else:
            failure_count = 0  # Reset the counter on a "pass"
        consecutive_fail_flags.append(failure_count >= consecutive_failures)

    # Add the consecutive failure flags to the DataFrame
    result_df['Consecutive_fail'] = consecutive_fail_flags

    # Update the 'Threshold_check' column to flag only rows with consecutive failures as "fail"
    result_df['Threshold_check'] = result_df.apply(
        lambda row: "fail" if row['Consecutive_fail'] else "pass",
        axis=1
    )

    # Filter rows where the test failed
    failed_rows = result_df[result_df['Threshold_check'] == "fail"]

    # Print timestamps where the test failed
    if not failed_rows.empty:
        print("Failed Timestamps:")
        print(failed_rows['Timestamp'].to_list())

    # Rename 'Threshold_check' to 'Signal Value' for the output
    result_df = result_df.rename(columns={'Threshold_check': 'Signal Value'})

    # Add a new column 'Signal Name' with the value 'MODID_Check'
    result_df['Signal Name'] = 'MODID_Check'

    # Return a DataFrame with 'Signal Name', 'Timestamp', and 'Signal Value' columns
    return result_df[['Signal Name', 'Timestamp', 'Signal Value']]

def dmpID_speed_check(Object_SpiHdr_DmpId_channels, Radar,vxvref_data_kmh,Radar_Channels):
    trace = CommonFunc()
    radar_short = get_last_two_letters(Radar)
    HTML_Logger.ReportWhiteMessage(f"Check for constancy: {Radar}.Object_SpiHdr_DmpId_R{radar_short}")
    data_Object_DmpID_Radar = trace.get_signal_value(Object_SpiHdr_DmpId_channels[f"R{radar_short}_RXX_SpiHdr_DmpId"], 0, 0)
    data_MODID_Radar = trace.get_signal_value(Radar_Channels[f"g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"], 0, 0)
    Radar_DmpID_vxvref_synch = synch_data(data_Object_DmpID_Radar, vxvref_data_kmh,data_MODID_Radar)
    if Radar == "RadarFC":
        HTML_Logger.ReportWhiteMessage(f"Radar FC check if dmpID and MODID is correct for speed range 0-65-115 km/h")
        Radar_DmpID_check = analyze_synch_data(Radar_DmpID_vxvref_synch, 65, 115)
        MOD_ID_1_list = [1033, 1034, 1035, 1083]
        MOD_ID_2_list = [1037, 1038, 1039, 1040]
        MOD_ID_3_list = [1041, 1042, 1043, 1044] 
        MOD_ID_Check_result = MOD_ID_Check(Radar_DmpID_vxvref_synch, 65, 115, MOD_ID_1_list, MOD_ID_2_list, MOD_ID_3_list)
    else:
        HTML_Logger.ReportWhiteMessage(f"Radar {Radar} check if dmpID abd MODID is correct for speed range 0-7-65 km/h")
        Radar_DmpID_check = analyze_synch_data(Radar_DmpID_vxvref_synch, 7, 65)
        MOD_ID_1_list = [1058, 1059,1084, 1085]
        MOD_ID_2_list = [1061, 1062, 1063, 1086]
        MOD_ID_3_list_ = [1065, 1066, 1067, 1068]
        MOD_ID_Check_result = MOD_ID_Check(Radar_DmpID_vxvref_synch, 7, 65, MOD_ID_1_list, MOD_ID_2_list, MOD_ID_3_list_)
        #save_dataframe_to_csv(Radar_DmpID_vxvref_synch , r"C:\TOOLS\Gen6_parcer\Radar_DmpID_vxvref_synch.csv")

    HTML_Logger.ReportWhiteMessage(f"---- RQM Test step 3 DumpID Constancy Check")
    trace.check_signal_update(Radar_DmpID_check, Condition.NOT_EQUALS, "fail")
    HTML_Logger.ReportWhiteMessage(f"---- RQM Test step 4 MODID Constancy Check")
    trace.check_signal_update(MOD_ID_Check_result, Condition.NOT_EQUALS, "fail")

def get_last_two_letters(input_string):
    return input_string[-2:]

def health_header_check(Object_ShiiHdr_DataMeasured_channels, Radar):
    trace = CommonFunc()
    HTML_Logger.ReportWhiteMessage(f"Check for constancy: {Radar}.Object_SpiiHdr_DataMeasured_R{get_last_two_letters(Radar)}")
    data_Object_DataMeasured_Radar = trace.get_signal_value(Object_ShiiHdr_DataMeasured_channels[f"R{get_last_two_letters(Radar)}_Shii_DataMeasured"], 0, 0)
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 5 Health Header Check")
    trace.check_signal_update(data_Object_DataMeasured_Radar, Condition.CONSTANT, "DataMeasured_Valid")

def radio_astronomy_check (Radar_Channels, Radar):
    trace = CommonFunc()
    HTML_Logger.ReportWhiteMessage(f"Check for constancy: {Radar}.Veh_SenIn_RadioAstronomy")
    data_Radio_Astronomy_Radar = trace.get_signal_value(Radar_Channels["Veh_SenIn_RadioAstronomy"], 0, 0)
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 6 Radio Astronomy Check")
    trace.check_signal_update(data_Radio_Astronomy_Radar, Condition.CONSTANT, "RADIO_PROTECTION_DISABLED")

def check_aliment_data(alignment_dataframe):
    # Convert Signal Value from radians to degrees
    degrees = np.degrees(alignment_dataframe['Signal Value'])
    min_mal = degrees.min()
    max_mal = degrees.max()
    avg_mal = degrees.mean()
    value_range = max_mal - min_mal

    return min_mal, max_mal, avg_mal, value_range

def get_relative_yaw(yaw_dataframe, mounting_position):
    """
    Returns the same dataframe with 'Signal Value' replaced by the absolute difference
    between Signal Value and mounting_position.
    """
    result = yaw_dataframe.copy()
    result['Signal Value'] = (result['Signal Value'] - mounting_position).abs()
    return result

def check_mal_data(Relative_mal_dataframe):
    radian_limit = 0.113446  # approx 6.5 degrees in radians

    # Check if Signal Value is within [-radian_limit, radian_limit]
    result = Relative_mal_dataframe.copy()
    result['Signal Value'] = result['Signal Value'].apply(
        lambda x: "pass" if -radian_limit <= x <= radian_limit else "fail"
    )
    return result

def convert_dec_text(decimal_dataframe):
    # Bit definitions
    bit_labels = [
        "EGO_VELOCITY_LOW",
        "EGO_VELOCITY_HIGH",
        "EGO_YAW_RATE_HIGH",
        "EGO_ACCELERATION_HIGH",
        "LOCATION_NUMBER_LOW",
        "FAILURE_STATE_INVALID",
        "LOCATION_DISTRIBUTION_INVALID",
        "INPUT_INVALID"
    ]

    def decode_bits(value):
        bits = f"{int(value):08b}"[::-1]  # Reverse for LSB first
        return [bit_labels[i] for i, b in enumerate(bits) if b == '1']

    # Apply decoding to each row
    decoded = decimal_dataframe['Signal Value'].apply(decode_bits)
    # Custom join: if value is 0, write "MAL Active"
    decoded_text = [
        "MAL Active" if int(val) == 0 else ', '.join(bits) if bits else "NONE"
        for val, bits in zip(decimal_dataframe['Signal Value'], decoded)
    ]

    # Build new DataFrame
    result_df = pd.DataFrame({
        'Timestamp': decimal_dataframe['Timestamp'],
        'Decoded Text': decoded_text
    })

    return result_df

def crate_OOPCause_messages(Text_dataframe):
    # Count occurrences for each status
    status_counts = Text_dataframe['Decoded Text'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    # Calculate time per row (assume uniform sampling, use median delta)
    if len(Text_dataframe) > 1:
        time_per_row = Text_dataframe['Timestamp'].diff().median()
    else:
        time_per_row = 0

    # Calculate total time for each status
    status_counts['Total Time (s)'] = status_counts['Count'] * time_per_row

    # Filter out statuses under 1 second
    status_counts = status_counts[status_counts['Total Time (s)'] >= 1]

    # Sort by total time descending
    status_counts = status_counts.sort_values(by='Total Time (s)', ascending=False)

    # Print messages
    for _, row in status_counts.iterrows():
        HTML_Logger.ReportWhiteMessage(f"      - {row['Status']}: Total Time = {row['Total Time (s)']:.2f} s")

    return

def convert_df_kmh_to_ms(df, signal_column='Signal Value'):
    df_converted = df.copy()
    df_converted[signal_column] = df_converted[signal_column] / 3.6
    return df_converted

def check_OOP_conditions(
    synchdataframe,
    opp_min_limit_speed_ms,
    oop_max_limit_speed_ms,
    oop_max_yaw_rate_rad_s,
    oop_max_acceleration_ms2,
    tolerance_cycles=4
):
    """
    Checks OOS conditions for each row and returns a DataFrame with 'pass' or 'fail' for each timestamp.
    Only flags as 'fail' if the condition is violated for more than `tolerance_cycles` consecutive points.
    """
    fail_counter = 0
    results = []

    for _, row in synchdataframe.iterrows():
        fail = False
        if row['ego_speed_ms'] < opp_min_limit_speed_ms:
            if "EGO_VELOCITY_LOW" not in str(row['AzOOPCause']) or "EGO_VELOCITY_LOW" not in str(row['ElOOPCause']):
                fail = True
        if row['ego_speed_ms'] > oop_max_limit_speed_ms:
            if "EGO_VELOCITY_HIGH" not in str(row['AzOOPCause']) or "EGO_VELOCITY_HIGH" not in str(row['ElOOPCause']):
                fail = True
        if abs(row['Vehicle_acceleration_ms2']) > oop_max_acceleration_ms2:
            if "EGO_ACCELERATION_HIGH" not in str(row['AzOOPCause']) or "EGO_ACCELERATION_HIGH" not in str(row['ElOOPCause']):
                fail = True
        if abs(row['RotationRateYaw_rad_s']) > oop_max_yaw_rate_rad_s:
            if "EGO_YAW_RATE_HIGH" not in str(row['AzOOPCause']) or "EGO_YAW_RATE_HIGH" not in str(row['ElOOPCause']):
                fail = True

        if fail:
            fail_counter += 1
        else:
            fail_counter = 0

        if fail_counter > tolerance_cycles:
            results.append("fail")
        else:
            results.append("pass")

    result_df = pd.DataFrame({
        "Signal Name": "OOPConditions",
        "Timestamp": synchdataframe["Timestamp"],
        "Signal Value": results
    })

    return result_df

def Mal_Check(Radar_Channels, ego_vehicle_Channels, Radar):
    # Definitions of OOP Limits defined in the testcase 
    opp_min_limit_speed_ms =  0.8333
    oop_max_limit_speed_ms =  70
    oop_max_yaw_rate_rad_s =  0.1
    oop_max_acceleration_ms2 =  5

    yaw_mountings = {
        "RadarFC": 0,
        "RadarFL": 1.0472,
        "RadarFR": -1.0472,
        "RadarRL": 2.0944,
        "RadarRR": -2.0944
    }

    trace = CommonFunc()
    # convert from decimal to text

    HTML_Logger.ReportWhiteMessage(f"--Starting checking {Radar} Sensor Orientation--")

    SensorOrientYaw = trace.get_signal_value(Radar_Channels[f"R{get_last_two_letters(Radar)}_RXX_SpiHdr_SensorOrientYaw"], 0, 0)
    min_mal, max_mal, avg_mal, value_range = check_aliment_data(SensorOrientYaw)
    HTML_Logger.ReportWhiteMessage(f"   - SensorOrientYaw: Avg={avg_mal:.2f}°, Range={value_range:.2f}°")
    relative_SensorOrientYaw = get_relative_yaw(SensorOrientYaw, yaw_mountings.get(Radar, 0))

    SensorOrientYaw_check = check_mal_data(relative_SensorOrientYaw)
    trace.check_signal_update(SensorOrientYaw_check, Condition.NOT_EQUALS, "fail")

    SensorOrientPitch = trace.get_signal_value(Radar_Channels[f"R{get_last_two_letters(Radar)}_RXX_SpiHdr_SensorOrientPitch"], 0, 0)
    min_mal, max_mal, avg_mal, value_range = check_aliment_data(SensorOrientPitch)
    HTML_Logger.ReportWhiteMessage(f"   - SensorOrientPitch: Avg={avg_mal:.2f}°, Range={value_range:.2f}°")

    SensorOrientPitch_check = check_mal_data(SensorOrientPitch)
    trace.check_signal_update( SensorOrientPitch_check, Condition.NOT_EQUALS, "fail")

    AzOOPCause = trace.get_signal_value(Radar_Channels[f"R{get_last_two_letters(Radar)}_Shii_MisAzOOPCause"], 0, 0)
    AzOOPCause_text = convert_dec_text(AzOOPCause)
    HTML_Logger.ReportWhiteMessage(f"   - AzOOPCause Status Summary:")
    crate_OOPCause_messages(AzOOPCause_text)

    ElOOPCause = trace.get_signal_value(Radar_Channels[f"R{get_last_two_letters(Radar)}_Shii_MisElOOPCause"], 0, 0)
    ElOOPCause_text = convert_dec_text(ElOOPCause)
    HTML_Logger.ReportWhiteMessage(f"   - ElOOPCause Status Summary:")
    crate_OOPCause_messages(ElOOPCause_text)


    ego_speed = trace.get_signal_value(ego_vehicle_Channels[("g_ConfigurationData.m_envData.vxvRef.m_value")], 0, 0)
    ego_speed_ms = convert_df_kmh_to_ms(ego_speed)
    Vehicle_acceleration_ms2 = trace.get_signal_value(ego_vehicle_Channels[("g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value")], 0, 0)
    RotationRateYaw_rad_s = trace.get_signal_value(ego_vehicle_Channels[("g_ARM_rbBsw_rbCom_rbCom_netRunnable.m_portCNetRxOmiBswDynVehicleRxSignal_out.m_YawRate_f32.m_phyValue")], 0, 0)
    synchdataframe = synch_data_mal(ego_speed_ms, Vehicle_acceleration_ms2, RotationRateYaw_rad_s,AzOOPCause_text,ElOOPCause_text)

    OOP_check = OOP_check = check_OOP_conditions(synchdataframe, opp_min_limit_speed_ms, oop_max_limit_speed_ms, oop_max_yaw_rate_rad_s, oop_max_acceleration_ms2)
    trace.check_signal_update(OOP_check, Condition.NOT_EQUALS, "fail")

    print("MAL Check completed for ", Radar)

def TC_Gen6_Auto_Check(input_log):

    HTML_Logger.setup(__file__, "Gen6 Auto Checks", filename=HTML_Logger.generate_report_name())  # create the HTML report
    Measurement_name = get_base_name(input_log)

    HTML_Logger.ReportWhiteMessage(f"--------------------Checking Measurement: {Measurement_name}---------------------------")

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    output.list_channels() # If needed user can check all available channels objects
    # input from jenkins a trace or folder and from the online analyzer *** 

    #CAN Signals to check
    vxvref_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
    Object_SpiHdr_DmpId_channels = output.get_channels(["RFC_SpiHdr_DmpId","RFL_SpiHdr_DmpId","RFR_SpiHdr_DmpId","RRL_SpiHdr_DmpIdd","RRR_SpiHdr_DmpId"])
    Object_ShiiHdr_DataMeasured_channels = output.get_channels(["RFC_Shii_DataMeasured","RFL_Shii_DataMeasured","RFR_Shii_DataMeasured","RRL_Shii_DataMeasured","RRR_Shii_DataMeasured"])
    
    #CAN Signals to check
    ego_vehicle_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value"),
                                                ("RadarFC", "MEAS_CORE0_10MS_EV","g_ARM_rbBsw_rbCom_rbCom_netRunnable.m_portCNetRxOmiBswDynVehicleRxSignal_out.m_YawRate_f32.m_phyValue"),
                                                ("RadarFC", "m051F2FDD", "g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value")])


    RadarFC_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RadarFC", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
                                            ("FD3_RA6_Toliman_LGU_3_1", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy"),
                                            ("RFC_RXX_SpiHdr_SensorOrientYaw"),
                                            ("RFC_RXX_SpiHdr_SensorOrientPitch"),
                                            ("RFC_Shii_MisAzOOPCause"),
                                            ("RFC_Shii_MisElOOPCause"),
                                            ])
    
    RadarFL_channels = output.get_channels([("RadarFL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarFL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RadarFL", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
                                            ("FD3_RA6_Toliman_LGU_3_1_FL", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy"),
                                            ("RFL_RXX_SpiHdr_SensorOrientYaw"),
                                            ("RFL_RXX_SpiHdr_SensorOrientPitch"),
                                            ("RFL_Shii_MisAzOOPCause"),
                                            ("RFL_Shii_MisElOOPCause"),
                                            ])
    
    RadarFR_channels = output.get_channels([("RadarFR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarFR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RadarFR", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
                                            ("FD3_RA6_Toliman_LGU_3_1_FR", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy"),
                                            ("RFR_RXX_SpiHdr_SensorOrientYaw"),
                                            ("RFR_RXX_SpiHdr_SensorOrientPitch"),
                                            ("RFR_Shii_MisAzOOPCause"),
                                            ("RFR_Shii_MisElOOPCause"),
                                            ])
    
    RadarRL_channels = output.get_channels([("RadarRL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarRL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RadarFL", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
                                            ("FD3_RA6_Toliman_LGU_3_1_RL", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy"),
                                            ("RRL_RXX_SpiHdr_SensorOrientYaw"),
                                            ("RRL_RXX_SpiHdr_SensorOrientPitch"),
                                            ("RRL_Shii_MisAzOOPCause"),
                                            ("RRL_Shii_MisElOOPCause"),
                                            ])
    
    RadarRR_channels = output.get_channels([("RadarRR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarRR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RadarRR", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
                                            ("FD3_RA6_Toliman_LGU_3_1_RR", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy"),
                                            ("RRR_RXX_SpiHdr_SensorOrientYaw"),
                                            ("RRR_RXX_SpiHdr_SensorOrientPitch"),
                                            ("RRR_Shii_MisAzOOPCause"),
                                            ("RRR_Shii_MisElOOPCause"),
                                            ])
                                    
    # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    # Get Dataframe for signal of provided range
    # FLOATING point example
    vxvref_data = trace.get_signal_value(vxvref_channels["g_ConfigurationData.m_envData.vxvRef.m_value"], 0, 0)
    vxvref_data_kmh = convert_pandas_ms_to_kmh(vxvref_data)  # Convert m/s to km/h

    CycleStatus_CycleCounter_Check(RadarFC_channels, "RadarFC")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels, "RadarFC", vxvref_data_kmh,RadarFC_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarFC")
    radio_astronomy_check (RadarFC_channels, "RadarFC")
    
    CycleStatus_CycleCounter_Check(RadarFL_channels, "RadarFL")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels , "RadarFL", vxvref_data_kmh,RadarFL_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarFL")
    radio_astronomy_check (RadarFL_channels, "RadarFL")
    
    CycleStatus_CycleCounter_Check(RadarFR_channels, "RadarFR")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels, "RadarFR", vxvref_data_kmh,RadarFR_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarFR")
    radio_astronomy_check (RadarFR_channels, "RadarFR")

    CycleStatus_CycleCounter_Check(RadarRL_channels, "RadarRL")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels , "RadarRL", vxvref_data_kmh,RadarRL_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarRL")
    radio_astronomy_check (RadarRL_channels, "RadarRL")
    
    CycleStatus_CycleCounter_Check(RadarRR_channels, "RadarRR")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels , "RadarRR", vxvref_data_kmh,RadarRR_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarRR")
    radio_astronomy_check (RadarRR_channels, "RadarRR")

    #HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)
    # starting MAL Checks
    Mal_Check(RadarFC_channels, ego_vehicle_channels, "RadarFC")
    Mal_Check(RadarFL_channels, ego_vehicle_channels, "RadarFL")
    Mal_Check(RadarFR_channels, ego_vehicle_channels, "RadarFR")
    Mal_Check(RadarRL_channels, ego_vehicle_channels, "RadarRL")
    Mal_Check(RadarRR_channels, ego_vehicle_channels, "RadarRR")



if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_Gen6_Auto_Check(log)
    else:
        TC_Gen6_Auto_Check(LOG)
