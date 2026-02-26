#created by Christian Tinschert Rivera 
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for E3 Project

import sys, os
import matplotlib.pyplot as plt
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger

def find_stc_passed_timestamps(df):
    # Filter the DataFrame to get rows where "Signal Value" is "STC_PASSED"
    stc_passed_df = df[df['Signal Value'] == 'STC_PASSED']
    
    # Return the "Timestamp" column of the filtered DataFrame
    return stc_passed_df['Timestamp'].tolist()

def get_signal_values_at_timestamps(df, timestamps):
    # Initialize an empty list to store the signal values
    signal_values = []
    
    # Iterate over the list of timestamps
    for timestamp in timestamps:
        # Find the row in the DataFrame that matches the timestamp
        row = df[df['Timestamp'] == timestamp]
        
        # If a matching row is found, get the signal value and multiply by 57.2958
        if not row.empty:
            signal_value = row['Signal Value'].values[0] * 57.2958
            signal_values.append(signal_value)
        else:
            # If no matching row is found, append None or any other placeholder
            signal_values.append(None)
    
    return signal_values

def plot_points(x_values, y_values, output_file='plot.png'):
    # Create a new figure
    plt.figure()
    
    # Plot the points
    plt.scatter(x_values, y_values, marker='o')
    
    # Add labels and title
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.title('Plot of Points in Coordinate System')
    
    # Save the plot as an image file
    plt.savefig(output_file)
    
    # Close the plot to free up memory
    plt.close()


#Offline analysis imports
try:
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
except:
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser

# Define a constant for log files, could be a single log or a directory
LOG = r"C:\TOOLS\Gen6_parcer\Matzes_Task" # Single log example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\SPA_Demo_20241218_101337_001.mf4"

def TC_ACC_Test(input_log):

    HTML_Logger.setup(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects

    channels = output.get_channels([("RadarFC", "MEAS_DSP_0_EV", "scom_g_DSP_rbRsp_Dsp_rbRsp_dsp_FacadeDsp_m_LocationInterface_senderPort_local._P_T1.m_arrayPool")])

    Location_array_data = trace.get_signal_value(channels["scom_g_DSP_rbRsp_Dsp_rbRsp_dsp_FacadeDsp_m_LocationInterface_senderPort_local._P_T1.m_arrayPool"], 0, 0)

    print("Task Done!")
    # INTEGER example
    # Analysis
    #trace.check_signal_update(data, Condition.EQUALS,5)  # Returns bool(True/False) and pd.Dataframe

    # STRING example
    #data = trace.get_signal_value(channels["RHLowBeamStatus"], 0,0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    #trace.check_signal_update(data, Condition.EQUALS,"OFF")  # Returns bool(True/False) and pd.Dataframe

    # INTEGER example
    #data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0, 0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    # Perform operations on the DataFrame
    #data.at[19, 'Signal Value'] = 3
    #data.at[87, 'Signal Value'] = 2
    #data.at[42, 'Signal Value'] = 7  # Repeated value
    #data.at[50, 'Signal Value'] = None
    #trace.check_alive_counter_consistency(data)  # Returns bool(True/False) and pd.Dataframe
    ##############################################################################

    # Rafael coding of radar functions

    # Preconditions
    #ecu_online = traceSearchSignalValue(DPCdelta5::_g_PL_AD_fw_OneDrivingSW_dsm_StateManagement_SscRunnable_SscRunnable_m_daCoreStateNotification_out_local::m_daCoreState, 7, 0)
    #if ecu_online not false then: do next  else: step failed, end test

    # Test step 1
    #mount_x_fc = trace.check_signal_update(RFC_LocHdr_SensorOriginPointX, ecu_online)
    #if mount_x_fc == true: passed
    #else:failed
    #param_mount_x_fc = 1
    #if mount_x_fc == param_mount_x_fc: passed
    #else: failed
    #mount_y_fc = traceGetSignalValue(RFC_LocHdr_SensorOriginPointY, ecu_online)
    #if mount_y_fc == true: passed
    #else:failed
    #param_mount_y_fc = 1
    #if mount_y == param_mount_y_fc: passed
    #else: failed
    #mount_z_fc = traceGetSignalValue(RFC_LocHdr_SensorOriginPointZ, ecu_online)
    #if mount_z_fc == true: passed
    #else:failed
    #param_mount_z_fc = 1
    #if mount_z_fc == param_mount_z_fc: passed
    #else: failed

    # Test step 2
    #num_valid_loc_fc = traceGetSignalValue (RFC_LocHdr_NumValidDetections, ecu_online)
    #if num_valid_loc_fc == true: passed
    #else: failed
    #if num_valid_loc_fc != 0: passed
    #else: failed
    #time_stamp_fc = traceGetSignalValue(RFC_LocHdr_TimeStamp, ecu_online, 0)
    #if checkupdate(time_stamp_fc, ">0", 9999999999 ) ==  true: passed
    #else: failed
    #time_stamp_status_fc = traceGetSignalValue(RFC_LocHdr_TimeStampStatus, ecu_online, 0)
    #if checkupdate (time_stamp_status_fc, "=8") == true: passed
    #else: failed

    # Test step 3
    #prot_block_ctr_fc_000_002 = traceGetSignalValue(RFC_Loc000_002_ProtBlockCtr, ecu_online, 0)
    #if checkupdate(prot_block_ctr_fc_000_002, ">1", 15) == true: passed
    #else: failed
    #ac_ctr_fc_000_002 = traceGetSignalValue(RFC_Loc000_002_AliveCtr, ecu_online, 0)
    #if checkupdate(ac_ctr_fc_000_002, ">1", 15 ) == true: passed
    #else: failed
    #crc_fc_000_002 = traceGetSignalValue(RFC_Loc000_002_CRC, ecu_online, 0)
    #if checkupdate(crc_fc_000_002, "!=") == true: passed
    #else: failed

    # Test step 4
    #traceSearchCondition((RFC_Loc000_Azimuth == 0 || RFC_Loc001_Azimuth == 0 || RFC_Loc002_Azimuth == 0), ecu_online, 0)

    # Test step 5 

    # Test step 6
    #traceCheckFrameCycleTime(RFC_Location_000_002, 46, 86, ecu_online, 0)

    # Robins test case for CAN TP

    # opens the HTML report in Browser  (using the default OS configured browser)
    HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)

    # capl.StopMeasurement()

if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_ACC_Test(log)
    else:
        TC_ACC_Test(LOG)
