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

# print out function for debugging purposes, can be removed later
def save_dataframe_to_csv(df, filename):
    """
    Saves the given DataFrame to C:\TOOLS\Gen6_parcer\{filename}.csv for debug
    with ';' as delimiter and ',' as decimal separator.
    """
    save_dir = r"C:\TOOLS\Gen6_parcer"
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

def synchronize_multiple_dataframes(*dfs, tolerance=0.02):
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

def Gen7_RTPS_Checks(RTPS_Channels, Radar):
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
        ModID_list = [3079, 3088]
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")

    #conditions for fornt corner soensors.
    elif Radar == "RadarFL" or Radar == "RadarFR":
        trace.check_signal_update(DmpId_data, Condition.EQUALS, 5)
        ModID_list = [3084, 3093]
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")

    #conditions for rear corner sensors
    elif Radar == "RadarRL" or Radar == "RadarRR":
        trace.check_signal_update(DmpId_data, Condition.EQUALS, 5)
        ModID_list = [3087, 3092]
        MODID_check_result = MODID_check(ModID_data, ModID_list)
        HTML_Logger.ReportWhiteMessage(f"---- RQM test step 4:  ModID Check")
        trace.check_signal_update(MODID_check_result, Condition.CONSTANT, "pass")

    #Place holders for the side sensors.

    #Radio Astronomy protection check:
    HTML_Logger.ReportWhiteMessage(f"---- RQM test step 5:  Radio Astronomy Protection Check")
    Radio_Astronomy_data = trace.get_signal_value(RTPS_Channels["R"+Radar[-2:]+"_Shii_RadioAstronomyProtection"], 0, 0)
    vehicle_Radio_Astronomy_data = trace.get_signal_value(RTPS_Channels["Veh_SenIn_RadioAstronomy"], 0, 0)
    Radio_protection_synch_df = synchronize_multiple_dataframes(Radio_Astronomy_data, vehicle_Radio_Astronomy_data, tolerance=0.02)
    astronomy_check_result = astronomy_check(Radio_protection_synch_df, "R"+Radar[-2:])
    trace.check_signal_update(astronomy_check_result, Condition.CONSTANT, "pass")

def TC_Gen7_Checks(input_log):
    Measurement_name = get_base_name(input_log)
    HTML_Logger.setup(__file__, "Gen7 Checker", filename=HTML_Logger.generate_report_name())  # create the HTML report

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    output.list_channels() # If needed user can check all available channels objects

    Sensor_list = detect_sensors_in_file(output)
    HTML_Logger.ReportWhiteMessage(f"--------------------Checking Measurement: {Measurement_name}---------------------------")
    HTML_Logger.ReportWhiteMessage(f"Sensors detected in the log: {Sensor_list}")
    for sensor in Sensor_list:
        logging.info(f"Start analysing data from sensor: {sensor}")
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
        
        Gen7_RTPS_Checks(RTPS_channels, sensor)

        MAL_channels = output.get_channels([("R"+sensor[-2:]+"_SpiHdr_SensorOrientYaw"),
                                            ("R"+sensor[-2:]+"_SpiHdr_SensorOrientPitch"),
                                            ("R"+sensor[-2:]+"_Shii_MisAzOOPCause"),
                                            ("R"+sensor[-2:]+"_Shii_MisElOOPCause"),
                                            ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_azIndicator.m_estimation.m_val.m_value"),
                                            ("Radar"+sensor[-2:], "MEAS_COREX_RSP_EV", "g_ARM_rbMal_RunnableMeasureAlignment.filterStateCache.m_elIndicator.m_estimation.m_val.m_value")
                                            ])
        
        logging.info(f"Number of channels found for {sensor}: {len(RTPS_channels)+len(MAL_channels)}")
    
    logging.info(f"Script finished")


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_Gen7_Checks(log)
    else:
        TC_Gen7_Checks(LOG)
