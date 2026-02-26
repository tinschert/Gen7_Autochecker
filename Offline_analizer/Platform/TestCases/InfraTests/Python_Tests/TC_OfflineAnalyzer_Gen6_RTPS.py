#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for E3 Project

import sys, os
import matplotlib.pyplot as plt
import pandas as pd
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

def MOD_ID_Check(synch_data, min_vxvref, max_vxvref, MOD_ID_1_list, MOD_ID_2_list, MOD_ID_3_list, consecutive_failures=20):
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
    HTML_Logger.ReportWhiteMessage(f"Check for constancy: R{radar_short}_SpiHdr_DmpId")
    data_Object_DmpID_Radar = trace.get_signal_value(Object_SpiHdr_DmpId_channels[f"R{radar_short}_SpiHdr_DmpId"], 0, 0)
    data_MODID_Radar = trace.get_signal_value(Radar_Channels[f"R{radar_short}_SpiHdr_ModId"], 0, 0)
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
        MOD_ID_1_list = [1058, 1059, 1084, 1085]
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

def TC_Gen6_RTPS(input_log):

    HTML_Logger.setup(__file__, "Gen6 RTPS Checks", filename=HTML_Logger.generate_report_name())  # create the HTML report
    Measurement_name = get_base_name(input_log)

    HTML_Logger.ReportWhiteMessage(f"--------------------Checking Measurement: {Measurement_name}---------------------------")

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    output.list_channels() # If needed user can check all available channels objects
    # input from jenkins a trace or folder and from the online analyzer *** 

    #CAN Signals to check
    vxvref_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value")])
    Object_SpiHdr_DmpId_channels = output.get_channels(["RFC_SpiHdr_DmpId","RFL_SpiHdr_DmpId","RRL_SpiHdr_DmpId"])
    Object_ShiiHdr_DataMeasured_channels = output.get_channels(["RFC_Shii_DataMeasured","RFL_Shii_DataMeasured","RRL_Shii_DataMeasured"])
    
    RadarFC_channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RFC_SpiHdr_ModId"),
                                            ("Veh_SenIn_RadioAstronomy")
                                            ])
    
    RadarFL_channels = output.get_channels([("RadarFL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarFL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RFL_SpiHdr_ModId"),
                                            ("Veh_SenIn_RadioAstronomy")
                                            ])
    
    #RadarFR_channels = output.get_channels([("RadarFR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
    #                                        ("RadarFR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
    #                                        ("RadarFR", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
    #                                        ("FD3_RA6_Toliman_LGU_3_1_FR", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy")
    #                                        ])
    #
    RadarRL_channels = output.get_channels([("RadarRL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
                                            ("RadarRL", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
                                            ("RRL_SpiHdr_ModId"),
                                            ("Veh_SenIn_RadioAstronomy")
                                            ])
    
    #RadarRR_channels = output.get_channels([("RadarRR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_cycleStatus.m_status"),
    #                                        ("RadarRR", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_misc.m_cycleCounter"),
    #                                        ("RadarRR", "MEAS_DSP2COREX_RSP_EV", "g_measure_LocationInterface.m_SensState.ModulationPerformance_st.ModID"),
    #                                        ("FD3_RA6_Toliman_LGU_3_1_RR", "Veh_SensorInput", "Veh_SenIn_RadioAstronomy")
    #                                        ])
                                    
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
    
    #CycleStatus_CycleCounter_Check(RadarFR_channels, "RadarFR")
    #dmpID_speed_check(Object_SpiHdr_DmpId_channels, "RadarFR", vxvref_data_kmh,RadarFR_channels)
    #health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarFR")
    #radio_astronomy_check (RadarFR_channels, "RadarFR")

    CycleStatus_CycleCounter_Check(RadarRL_channels, "RadarRL")
    dmpID_speed_check(Object_SpiHdr_DmpId_channels , "RadarRL", vxvref_data_kmh,RadarRL_channels)
    health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarRL")
    radio_astronomy_check (RadarRL_channels, "RadarRL")
    
    #CycleStatus_CycleCounter_Check(RadarRR_channels, "RadarRR")
    #dmpID_speed_check(Object_SpiHdr_DmpId_channels , "RadarRR", vxvref_data_kmh,RadarRR_channels)
    #health_header_check(Object_ShiiHdr_DataMeasured_channels, "RadarRR")
    #radio_astronomy_check (RadarRR_channels, "RadarRR")

    #HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_Gen6_RTPS(log)
    else:
        TC_Gen6_RTPS(LOG)
