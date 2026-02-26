#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for E3 Project

import sys, os
import matplotlib.pyplot as plt
import pandas as pd
import logging
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s -  %(levelname)s  -  %(message)s')



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
def read_config(config_path):
    """
    Reads the JSON configuration file and returns it as a dictionary.
    """
    import json
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config   


# print out function for debugging purposes, can be removed later
def save_dataframe_to_csv(df, filename):
    """
    Saves the given DataFrame to C:\TOOLS\Gen6_parcer\{filename}.csv for debug
    with ';' as delimiter and ',' as decimal separator.
    """
    save_dir = r"C:\TOOLS\Gen7_Checker\Trash"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{filename}.csv")
    df.to_csv(save_path, index=False, sep=';', decimal=',')
    print(f"Saved DataFrame to {save_path}")

def get_base_name(file_path):
    return os.path.basename(file_path)

def detect_sensors_in_file(output):
    Sensors_list = []
    try:
        FC_vxvref_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarFC")
    except:
        logging.debug("NO radar FC Found in the log")
    try:
        FL_vxvref_channels = output.get_channels([("RadarFL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarFL")
    except:
        logging.debug("NO radar FL Found in the log")    
    try:
        FR_vxvref_channels = output.get_channels([("RadarFR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarFR")
    except:
        logging.debug("NO radar FR Found in the log") 
    try:
        RL_vxvref_channels = output.get_channels([("RadarRL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarRL")
    except:
        logging.debug("NO radar RL Found in the log") 
    try:
        RR_vxvref_channels = output.get_channels([("RadarRR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarRR")
    except:
        logging.debug("NO radar RR Found in the log") 

    try:
        RCL_vxvref_channels = output.get_channels([("RadarRCL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarRCL")
    except:
        logging.debug("NO radar RCL Found in the log")

    try:
        RCR_vxvref_channels = output.get_channels([("RadarRCR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("RadarRCR")
    except:
        logging.debug("NO radar RCR Found in the log")

    try:
        SL_vxvref_channels = output.get_channels([("LidarSL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("LidarSL")
    except:
        logging.debug("NO Lidar SL Found in the log")

    try:
        SR_vxvref_channels = output.get_channels([("LidarSR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
        Sensors_list.append("LidarSR")
    except:
        logging.debug("NO Lidar SR Found in the log")                      

    return Sensors_list 

def synchronize_multiple_dataframes(*dfs, tolerance):
    """
    Synchronizes any number of dataframes on 'Timestamp'.
    Returns a DataFrame with columns: 'Signal Name', 'Timestamp', and one column per input DataFrame.
    """
    import pandas as pd

    # Prepare the first dataframe
    merged = dfs[0].sort_values('Timestamp').copy()
    merged = merged.rename(columns={'Signal Value': merged['Signal Name'].iloc[0]})
    merged = merged[['Timestamp', merged['Signal Name'].iloc[0]]]

    # Merge the rest
    for df in dfs[1:]:
        col_name = df['Signal Name'].iloc[0]
        temp = df.sort_values('Timestamp').rename(columns={'Signal Value': col_name})
        temp = temp[['Timestamp', col_name]]
        merged = pd.merge_asof(
            merged.sort_values('Timestamp'),
            temp.sort_values('Timestamp'),
            on='Timestamp',
            direction='nearest',
            tolerance=tolerance
        )

    # Add 'Signal Name' column
    merged.insert(0, 'Signal Name', 'Synchronized_dataframe')
    return merged

# RTPS specific functions to use for the RTPS Testcases:

def MODID_check(ModID_data, ModID_list):
    """
    Checks if the 'Signal Value' in each row is in ModID_list.
    Returns a DataFrame with columns: 'Signal Name', 'Timestamp', 'Signal Value' ('pass'/'fail').
    """
    result_df = pd.DataFrame({
        'Signal Name': 'ModID_Check',
        'Timestamp': ModID_data['Timestamp'],
        'Signal Value': ['pass' if val in ModID_list else 'fail' for val in ModID_data['Signal Value']]
    })
    return result_df


def astronomy_check(df, radar):
    """
    Checks Radio Astronomy Protection synchronization.
    Returns a DataFrame with columns: 'Signal Name', 'Timestamp', 'Signal Value' ('pass'/'fail').
    """
    def check(row):
        if row[f'{radar}_Shii_RadioAstronomyProtection'] == 'RAP_DISABLED':
            return 'pass' if row['Veh_SenIn_RadioAstronomy'] == 'RADIO_PROTECTION_DISABLED' else 'fail'
        elif row[f'{radar}_Shii_RadioAstronomyProtection'] == 'RAP_ENABLED':
            return 'pass' if row['Veh_SenIn_RadioAstronomy'] == 'RADIO_PROTECTION_ENABLED' else 'fail'
        else:
            return 'fail'

    result_df = pd.DataFrame({
        'Signal Name': 'Astronomy_check',
        'Timestamp': df['Timestamp'],
        'Signal Value': df.apply(check, axis=1)
    })
    return result_df


def check_warning(df, label, measurement_name=None, radar=None):
    """
    Checks if 'Signal Value' in the DataFrame goes to 0 and writes a warning to the HTML log if any zeros are found.
    Args:
        df (pd.DataFrame): DataFrame with columns ['Signal Name', 'Timestamp', 'Signal Value']
        label (str): Label to use in the warning message (e.g., 'DmpId', 'ModId')
    """
    zero_count = (df['Signal Value'] == 0).sum()
    if zero_count > 0:
        HTML_Logger.ReportWhiteMessage(
            f"Warning: On {measurement_name} ({radar}) detected {zero_count} occurrences of {label} being 0, which may indicate a potential issue with the sensor or data integrity."
        )


def Gen7_RTPS_Checks(RTPS_Channels, Radar, Measurement_name):
    trace = CommonFunc()
    HTML_Logger.ReportWhiteMessage(f"=> {Radar} Check")
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 1 and 2:  RPTS Performance & Health Check")
    HTML_Logger.ReportWhiteMessage(f"Signal_name: {Radar}.g_ConfigurationData.m_cycleStatus.m_status")
    cycleStatus_data = trace.get_signal_value(RTPS_Channels["g_ConfigurationData.m_cycleStatus.m_status"], 0, 0)
    trace.check_signal_update(cycleStatus_data, Condition.CONSTANT, "EOk")
    HTML_Logger.ReportWhiteMessage(f"Signal_name: {Radar}.g_ConfigurationData.m_misc.m_cycleCounter")
    cycle_Counter_data = trace.get_signal_value(RTPS_Channels["g_ConfigurationData.m_misc.m_cycleCounter"], 0, 0)
    trace.check_alive_counter_consistency(cycle_Counter_data)
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 3:  DmpID Check")
    HTML_Logger.ReportWhiteMessage(f"Signal_name: R{Radar[-2:]}_SpiHdr_DmpId")
    DmpId_data = trace.get_signal_value(RTPS_Channels["R"+Radar[-2:]+"_SpiHdr_DmpId"], 0, 0)
    ModID_data = trace.get_signal_value(RTPS_Channels["R"+Radar[-2:]+"_SpiHdr_ModId"], 0, 0)
    #conditions for front center sensor.
    if Radar == "RadarFC":
        trace.check_signal_update(DmpId_data, Condition.EQUALS, 4)
        check_warning(ModID_data, "ModID", Measurement_name, Radar) # Check for any ModID value of 0 and report a warning if found.
        ModID_list = [0, 3079, 3088]
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")
        check_warning(DmpId_data, "DmpID", Measurement_name, Radar) # Check for any DmpID value of 0 and report a warning if found.

    #conditions for fornt corner soensors.
    elif Radar == "RadarFL" or Radar == "RadarFR":
        trace.check_signal_update(DmpId_data, Condition.EQUALS, 5)
        check_warning(ModID_data, "ModID", Measurement_name, Radar) # Check for any ModID value of 0 and report a warning if found.
        ModID_list = [0, 3084, 3093]
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")
        check_warning(DmpId_data, "DmpID", Measurement_name, Radar) # Check for any DmpID value of 0 and report a warning if found.

    #conditions for rear corner sensors
    elif Radar == "RadarRL" or Radar == "RadarRR":
        trace.check_signal_update(DmpId_data, Condition.EQUALS, 5)
        check_warning(ModID_data, "ModID", Measurement_name, Radar) # Check for any ModID value of 0 and report a warning if found.
        ModID_list = [0,3087, 3092]   
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")
        check_warning(DmpId_data, "DmpID", Measurement_name, Radar) # Check for any DmpID value of 0 and report a warning if found.


    #Place holders for the side sensors.

    #Radio Astronomy protection check:
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 5:  Radio Astronomy Protection Check")
    Radio_Astronomy_data = trace.get_signal_value(RTPS_Channels["R"+Radar[-2:]+"_Shii_RadioAstronomyProtection"], 0, 0)
    vehicle_Radio_Astronomy_data = trace.get_signal_value(RTPS_Channels["Veh_SenIn_RadioAstronomy"], 0, 0)
    Radio_protection_synch_df = synchronize_multiple_dataframes(Radio_Astronomy_data, vehicle_Radio_Astronomy_data, tolerance=0.02)
    astronomy_check_result = astronomy_check(Radio_protection_synch_df, "R"+Radar[-2:])
    trace.check_signal_update(astronomy_check_result, Condition.CONSTANT, "pass")
    HTML_Logger.ReportWhiteMessage(f"-------------Testing for RTPS related checks for {Radar} is finished------------------")

# Mal Specific functions to use for the MAL Testcases:

def format_oos_causes(causes_counts):
    """
    Formats a list of (cause, count) tuples into a string with each pair on a new line.
    """
    return "\n".join(f"{cause}: {count}" for cause, count in causes_counts)


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

    # Build new DataFrame with required columns
    result_df = pd.DataFrame({
        'Signal Name': ["OOS_Cause_Text"] * len(decimal_dataframe),
        'Timestamp': decimal_dataframe['Timestamp'],
        'Signal Value': decoded_text
    })

    return result_df

def OOS_Cause_count(df):
    """
    Counts occurrences of each unique value in the 'Signal Value' column.
    Returns a list of (value, count) tuples sorted by count descending.
    """
    value_counts = df['Signal Value'].value_counts()
    return list(value_counts.items())

def MAL_function_check(df, orientation=None):
    """
    Checks if changes in the azIndicator value only occur when OOS_Cause_Text is 'MAL Active'.
    Returns a DataFrame with columns: Signal Name, Timestamp, Signal Value (Pass/Fail).
    """
    # Identify the azIndicator column (assume it's the last column)
    az_col = df.columns[-1]
    oos_col = 'OOS_Cause_Text'
    timestamps = df['Timestamp']
    signal_name = (str(orientation) + "_" if orientation else "") + 'MAL_function_check'
    result = []
    prev_val = None
    prev_oos = None
    for idx, row in df.iterrows():
        curr_val = row[az_col]
        curr_oos = row[oos_col]
        if prev_val is not None:
            changed = curr_val != prev_val
            if changed:
                # Only allowed if previous or current OOS_Cause_Text is 'MAL Active'
                if prev_oos == 'MAL Active' or curr_oos == 'MAL Active':
                    result.append('Pass')
                else:
                    result.append('Fail')
            else:
                result.append('Pass')
        else:
            # First row, no previous value to compare
            result.append('Pass')
        prev_val = curr_val
        prev_oos = curr_oos
    out_df = pd.DataFrame({
        'Signal Name': [signal_name] * len(df),
        'Timestamp': timestamps,
        'Signal Value': result
    })
    return out_df

def theoretical_oop_check(df, limits):
    """
    Checks each row of the DataFrame against OOP theoretical limits.
    Returns a DataFrame with columns: 'Signal Name', 'Timestamp', 'Signal Value'.
    """
    speed_col = 'g_ConfigurationData.m_envData.vxvRef.m_value'
    yaw_col = 'g_ARM_Per_Arm_Per_arm_EmsRunnable_m_estimatedEgoState_out_local.m_arrayPool[1].elem.yawRate.m_value'
    accel_col = 'g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value'
    timestamp_col = 'Timestamp'

    results = []
    for _, row in df.iterrows():
        causes = []
        if row[speed_col] < limits['oop_min_limit_speed_ms']:
            causes.append("EGO_VELOCITY_LOW")
        if row[speed_col] > limits['oop_max_limit_speed_ms']:
            causes.append("EGO_VELOCITY_HIGH")
        if abs(row[yaw_col]) > limits['oop_max_yaw_rate_rad_s']:
            causes.append("EGO_YAW_RATE_HIGH")
        if abs(row[accel_col]) > limits['oop_max_acceleration_ms2']:
            causes.append("EGO_ACCELERATION_HIGH")
        results.append(", ".join(causes) if causes else "MAL Active")

    out_df = pd.DataFrame({
        'Signal Name': ['theoretical_OOP'] * len(df),
        'Timestamp': df[timestamp_col],
        'Signal Value': results
    })
    return out_df


def oss_text_check(df, tolerance=8, orientation=None, match_window=0):
    """
    Compares 'theoretical_OOP' and 'OOS_Cause_Text' columns.

    ignore_set entries are ignored for comparison, AND they are allowed to match "MAL Active"
    (i.e., MAL Active == ignore-only causes).

    match_window:
        Compare within ±match_window frames (0 = same frame only).

    tolerance:
        Number of consecutive failing frames required before keeping "Fail".
        Any "Fail" streak shorter than tolerance is turned into "Pass".
    """
    ignore_set = {"LOCATION_DISTRIBUTION_INVALID", "LOCATION_NUMBER_LOW", "FAILURE_STATE_INVALID","EGO_YAW_RATE_HIGH, FAILURE_STATE_INVALID"}
    n = len(df)

    def to_set(x):
        s = str(x)
        if s == "MAL Active":
            return {"MAL Active"}
        return set(s.split(", "))

    theo_list = [to_set(x) for x in df["theoretical_OOP"]]
    oos_list  = [to_set(x) for x in df["OOS_Cause_Text"]]

    def strip_ignore(s: set) -> set:
        # Don't strip "MAL Active" itself
        if s == {"MAL Active"}:
            return s
        return s - ignore_set

    def is_ignore_only(s: set) -> bool:
        # True if set is empty after removing ignore_set, and isn't MAL Active
        return s != {"MAL Active"} and len(strip_ignore(s)) == 0

    def match_sets(a: set, b: set) -> bool:
        """
        Match logic:
        - Normal case: compare after ignoring ignore_set
        - Special case: MAL Active matches ignore-only causes
        """
        a_stripped = strip_ignore(a)
        b_stripped = strip_ignore(b)

        # Special equivalence:
        if a == {"MAL Active"} and is_ignore_only(b):
            return True
        if b == {"MAL Active"} and is_ignore_only(a):
            return True

        return a_stripped == b_stripped

    # Step 1: raw pass/fail per frame (optionally within ±match_window)
    raw_pass = []
    for i in range(n):
        theo = theo_list[i]
        found = False

        for j in range(max(0, i - match_window), min(n, i + match_window + 1)):
            if match_sets(theo, oos_list[j]):
                found = True
                break

        raw_pass.append(found)

    # Step 2: apply consecutive-fail tolerance
    # Keep Fail only if there are >= tolerance consecutive fails
    if tolerance is None or tolerance <= 1:
        final_pass = raw_pass
    else:
        final_pass = raw_pass[:]
        i = 0
        while i < n:
            if final_pass[i]:
                i += 1
                continue

            start = i
            while i < n and not final_pass[i]:
                i += 1
            run_len = i - start

            if run_len < tolerance:
                for k in range(start, i):
                    final_pass[k] = True

    results = ["Pass" if p else "Fail" for p in final_pass]

    signal_name = (str(orientation) + "_" if orientation else "") + "OSS_Text_Check"
    return pd.DataFrame({
        "Signal Name": [signal_name] * n,
        "Timestamp": df["Timestamp"],
        "Signal Value": results
    })

def orientation_check(df, orientation=None):
    """
    Checks if the orientation value is within the lower and upper limits for each row.
    Returns a DataFrame with columns: 'Signal Name', 'Timestamp', 'Signal Value'.
    """
    # Find the upper/lower columns dynamically
    upper_col = None
    lower_col = None
    for col in df.columns:
        if col.endswith('.m_azOutOfSpec.m_limits.m_absolute.m_upper.m_value') or col.endswith('.m_elOutOfSpec.m_limits.m_absolute.m_upper.m_value'):
            upper_col = col
        if col.endswith('.m_azOutOfSpec.m_limits.m_absolute.m_lower.m_value') or col.endswith('.m_elOutOfSpec.m_limits.m_absolute.m_lower.m_value'):
            lower_col = col
    if upper_col is None or lower_col is None:
        raise ValueError("No suitable upper/lower limit columns found in DataFrame.")

    timestamp_col = 'Timestamp'
    # Find the value_col dynamically (first col ending with '_SpiHdr_SensorOrientYaw' or '_SpiHdr_SensorOrientPitch')
    value_col = None
    for col in df.columns:
        if col.endswith('_SpiHdr_SensorOrientYaw') or col.endswith('_SpiHdr_SensorOrientPitch'):
            value_col = col
            break
    if value_col is None:
        raise ValueError("No column ending with '_SpiHdr_SensorOrientYaw' or '_SpiHdr_SensorOrientPitch' found in DataFrame.")

    results = []
    out_of_bounds_count = 0
    for idx, row in df.iterrows():
        val = row[value_col]
        lower = row[lower_col]
        upper = row[upper_col]
        if lower <= val <= upper:
            out_of_bounds_count = 0
            results.append("Pass")
        else:
            out_of_bounds_count += 1
            if out_of_bounds_count > 2:
                results.append("Fail")
            else:
                results.append("Pass")

    signal_name = (str(orientation) + "_" if orientation else "") + "Orientation_check"
    return pd.DataFrame({
        'Signal Name': [signal_name] * len(df),
        'Timestamp': df[timestamp_col],
        'Signal Value': results
    })


def Gen7_MAL_Checks(MAL_Channels, Radar):
    trace = CommonFunc()
    oop_limit_dict = {
        "oop_min_limit_speed_ms": 3,
        "oop_max_limit_speed_ms": 70,
        "oop_max_yaw_rate_rad_s": 0.102,
        "oop_max_acceleration_ms2": 4,
    }
    
    # OOP Theoretical limits creation:
    vehicle_speed_data = MAL_Channels.get("g_ConfigurationData.m_envData.vxvRef.m_value")
    yawrate_data = MAL_Channels.get("g_ARM_Per_Arm_Per_arm_EmsRunnable_m_estimatedEgoState_out_local.m_arrayPool[1].elem.yawRate.m_value")
    acceleration_data = MAL_Channels.get("g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value")
    vehicle_speed_yaw_accel_df = synchronize_multiple_dataframes(vehicle_speed_data, yawrate_data, acceleration_data, tolerance=0.1)
    theoretical_oop_check_result = theoretical_oop_check(vehicle_speed_yaw_accel_df, oop_limit_dict)

    #Az information checks:
    HTML_Logger.ReportWhiteMessage(f"=> {Radar} MAL Check")
    HTML_Logger.ReportWhiteMessage(f"-----------------RQM Test step 1: OOS Thresholds are set------------------")
    AzOOS_Cause_data = MAL_Channels.get("R"+Radar[-2:]+"_Shii_MisAzOOPCause")
    AzOOS_Cause_Text = convert_dec_text(AzOOS_Cause_data)
    AzOOS_Cause_Count = OOS_Cause_count(AzOOS_Cause_Text)
    AZOOS_Cause_Count_reformat = format_oos_causes(AzOOS_Cause_Count)
    HTML_Logger.ReportWhiteMessage(f"AzOOS Cause Count:\n{AZOOS_Cause_Count_reformat}") 
    AzCompensation_data = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azCompensation.m_estimation.m_val.m_value")
    Az_synch_df = synchronize_multiple_dataframes(AzOOS_Cause_Text, AzCompensation_data, tolerance=0.1)
    Az_function_check_result = MAL_function_check(Az_synch_df, orientation="Azimuth")
    theoretical_and_measured_AzOOS_df = synchronize_multiple_dataframes(theoretical_oop_check_result, AzOOS_Cause_Text, tolerance=0.1)
    az_oss_text_check_result = oss_text_check(theoretical_and_measured_AzOOS_df, orientation="Azimuth", tolerance=10)
    
    #Elevation information checks:
    ElOOS_Cause_data = MAL_Channels.get("R"+Radar[-2:]+"_Shii_MisElOOPCause")
    ElOOS_Cause_Text = convert_dec_text(ElOOS_Cause_data)
    ElOOS_Cause_Count = OOS_Cause_count(ElOOS_Cause_Text)
    ElOOS_Cause_Count_reformat = format_oos_causes(ElOOS_Cause_Count)
    HTML_Logger.ReportWhiteMessage(f"ElOOS Cause Count:\n{ElOOS_Cause_Count_reformat}")
    ElCompensation_data = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elCompensation.m_estimation.m_val.m_value")
    El_synch_df = synchronize_multiple_dataframes(ElOOS_Cause_Text, ElCompensation_data, tolerance=0.1)
    El_function_check_result = MAL_function_check(El_synch_df, orientation="Elevation")
    theoretical_and_measured_ElOOS_df = synchronize_multiple_dataframes(theoretical_oop_check_result, ElOOS_Cause_Text, tolerance=0.1)
    el_oss_text_check_result = oss_text_check(theoretical_and_measured_ElOOS_df, orientation="Elevation", tolerance=10)
    
    try:
        trace.check_signal_update(az_oss_text_check_result, Condition.CONSTANT, "Pass")
        trace.check_signal_update(el_oss_text_check_result, Condition.CONSTANT, "Pass")
    except Exception as e:
        HTML_Logger.ReportWhiteMessage(f"Error in OOS check: {e}")

    HTML_Logger.ReportWhiteMessage(f"-----------------RQM Test step 2: OOS Functionality------------------")

    trace.check_signal_update(El_function_check_result, Condition.CONSTANT, "Pass")
    trace.check_signal_update(Az_function_check_result, Condition.CONSTANT, "Pass")

    HTML_Logger.ReportWhiteMessage(f"-------------RQM Test step 3: Sensor orientation plausibility ------------------")
    SpiHdr_SensorOrientYaw_df = MAL_Channels.get("R"+Radar[-2:]+"_SpiHdr_SensorOrientYaw")
    az_upper_absolute_limit_df = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azOutOfSpec.m_limits.m_absolute.m_upper.m_value")
    az_lower_absolute_limit_df = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azOutOfSpec.m_limits.m_absolute.m_lower.m_value")
    az_upper_lower_limits_df = synchronize_multiple_dataframes(az_upper_absolute_limit_df, az_lower_absolute_limit_df,  SpiHdr_SensorOrientYaw_df, tolerance=0.1)
    orientation_check_result = orientation_check(az_upper_lower_limits_df, orientation="Azimuth")
    HTML_Logger.ReportWhiteMessage(f"Sensor orientation plausibility check result for {Radar}:\n{orientation_check_result['Signal Value'].value_counts()}")
    trace.check_signal_update(orientation_check_result, Condition.CONSTANT, "Pass")

    SpiHdr_SensorOrientPitch_df = MAL_Channels.get("R"+Radar[-2:]+"_SpiHdr_SensorOrientPitch")
    el_upper_absolute_limit_df = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elOutOfSpec.m_limits.m_absolute.m_upper.m_value")
    el_lower_absolute_limit_df = MAL_Channels.get("g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elOutOfSpec.m_limits.m_absolute.m_lower.m_value")    
    el_upper_lower_limits_df = synchronize_multiple_dataframes(el_upper_absolute_limit_df, el_lower_absolute_limit_df,  SpiHdr_SensorOrientPitch_df, tolerance=0.1)
    orientation_check_result = orientation_check(el_upper_lower_limits_df, orientation="Elevation")
    HTML_Logger.ReportWhiteMessage(f"Sensor orientation plausibility check result for {Radar}:\n{orientation_check_result['Signal Value'].value_counts()}")
    trace.check_signal_update(orientation_check_result, Condition.CONSTANT, "Pass")


    logging.debug(f"Script Completed for {Radar}")

def TC_Gen7_Checks(input_log, RTPS_Check, MAL_Check, Blindness_Check):
    Measurement_name = get_base_name(input_log)
    HTML_Logger.setup(__file__, "Gen7 Checker", filename=HTML_Logger.generate_report_name())  # create the HTML report

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    output.list_channels() # If needed user can check all available channels objects

    Sensor_list = detect_sensors_in_file(output)
    HTML_Logger.ReportWhiteMessage(f"--------------------Checking Measurement: {Measurement_name}---------------------------")
    HTML_Logger.ReportWhiteMessage(f"Sensors detected in the log: {Sensor_list}")

    if RTPS_Check == 1:
        #Opening RTPS related channels for each sensor and performing the checks defined in Gen7_RTPS_Checks function.
        for sensor in Sensor_list:
            logging.info(f"Start analyzing RTPS data from sensor: {sensor}")
            Object_SpiHdr_DmpId_channels = output.get_channels((["R"+sensor[-2:]+"_SpiHdr_DmpId"]))
            Object_ShiiHdr_DataMeasured_channels = output.get_channels((["R"+sensor[-2:]+"_SpiHdr_ModId"]))
            HTML_Logger.ReportWhiteMessage(f"Start analysing data from sensor: {sensor}")
            RTPS_channels = output.get_channels([("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                                 ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                                 ("R"+sensor[-2:]+"_SpiHdr_DmpId"),
                                                 ("R"+sensor[-2:]+"_SpiHdr_ModId"),
                                                 ("R"+sensor[-2:]+"_Shii_RadioAstronomyProtection"),
                                                 ("Veh_SenIn_RadioAstronomy")
                                                 ])

            Gen7_RTPS_Checks(RTPS_channels, sensor, Measurement_name)

    else:
        print("RTPS checks are disabled in the configuration file, skipping RTPS checks.")

    if MAL_Check == 1:
        for sensor in Sensor_list:
            logging.info(f"Start analyzing MAL related data from sensor: {sensor}")
            MAL_channels = output.get_channels([("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value"),
                                                ("Radar"+sensor[-2:], "m01BBAD23", "g_ARM_Per_Arm_Per_arm_EmsRunnable_m_estimatedEgoState_out_local.m_arrayPool[1].elem.yawRate.m_value"),
                                                ("Radar"+sensor[-2:], "m051F2FDD", "g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value"),
                                                ("R"+sensor[-2:]+"_SpiHdr_SensorOrientYaw"),
                                                ("R"+sensor[-2:]+"_SpiHdr_SensorOrientPitch"),
                                                ("R"+sensor[-2:]+"_Shii_MisAzOOPCause"),
                                                ("R"+sensor[-2:]+"_Shii_MisElOOPCause"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azCompensation.m_estimation.m_val.m_value"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elCompensation.m_estimation.m_val.m_value"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azOutOfSpec.m_limits.m_absolute.m_lower.m_value"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azOutOfSpec.m_limits.m_absolute.m_upper.m_value"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elOutOfSpec.m_limits.m_absolute.m_lower.m_value"),
                                                ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elOutOfSpec.m_limits.m_absolute.m_upper.m_value")  
                                                ])
            
            Gen7_MAL_Checks(MAL_channels, sensor)
    
    else:
        print("MAL checks are disabled in the configuration file, skipping MAL checks.")


    if Blindness_Check == 1:
        logging.info(f"Start analyzing Blindness related data from sensor: {sensor}")
        # Place holder for the blindness checks, as the exact checks are still being defined.
        # Once the checks are defined, the related channels can be extracted and the checks can be implemented here.

    else:
        print("Blindness checks are disabled in the configuration file, skipping Blindness checks.")

    logging.info(f"Script finished")


if __name__ == "__main__":
    # Check if the path is a directory
    json_config_path = r"C:\TOOLS\Gen7_Checker\Gen7_config.json"
    json_data = read_config(json_config_path)
    RTPS_Check = json_data.get("RTPS_Checks", 1)  # Default to True if not specified
    MAL_Check = json_data.get("MAL_Checks", 1)  # Default to True if not specified
    LOG = json_data.get("path_to_check", LOG)  # Use the log path from config if available, otherwise use the default LOG
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_Gen7_Checks(log, RTPS_Check, MAL_Check)
    else:
        TC_Gen7_Checks(LOG, RTPS_Check, MAL_Check)