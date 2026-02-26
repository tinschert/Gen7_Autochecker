#created by PF Team
#copyright Robert Bosch GMBH
#date :
#this is a golden example of Python Offline testcase

import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\ReportGen"))
sys.path.append(os.path.join(script_dir, r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions"))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\TraceParser"))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\CommonTestFunctions"))

#Offline analysis imports
try:
    import HTML_Logger
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser
    from args import get_args
except:
    import Platform.Python_Testing_Framework.ReportGen.HTML_Logger as HTML_Logger
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
    from Platform.Python_Testing_Framework.TraceParser.args import get_args


test_args = get_args()  # Get parsed arguments
# Define a constant for log files, could be a single log or a directory
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
LOG = test_args.log_file_path


def TC_ACC_Test(input_log):

    ################# Initialization ##############################################################################
    HTML_Logger.setup(__file__, "Offline Analyzer Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Tester : XXX")
    HTML_Logger.TestReportHeader(f"TestCaseName : {os.path.basename(__file__)}")
    HTML_Logger.TestReportHeader("DefectID : None")
    HTML_Logger.TestReportHeader(f"RQM_ID : 3253665")
    HTML_Logger.TestReportHeader(f"Input log file -> {LOG}")
    trace = CommonFunc()  # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects
    channels = output.get_channels(["RFC_LocHdr_SensorOriginPointX", "Vehicle_Variant", "ADAS_1C0_AliveCounter"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    ################ TEST STEPS Section ############################################################################
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 1 --------------------")
    # Get Dataframe for signal of provided range
    # FLOATING point example
    data = trace.get_signal_value(channels["RFC_LocHdr_SensorOriginPointX"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.NOT_EQUALS, 3.55)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 2 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0, 0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.EQUALS,6)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 3 --------------------")
    # STRING example
    data = trace.get_signal_value(channels["Vehicle_Variant"], 0,0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.NOT_EQUALS,"Golf")
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 4 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0, 0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    # Perform operations on the DataFrame
    data.at[19, 'Signal Value'] = 3
    data.at[87, 'Signal Value'] = 2
    data.at[42, 'Signal Value'] = 7  # Repeated value
    data.at[50, 'Signal Value'] = None
    trace.check_alive_counter_consistency(data)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 5 --------------------")
    # Check signal dependency
    data_input = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0,
                                        0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    data_to_check = trace.get_signal_value(channels["Vehicle_Variant"], 0,
                                           0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range

    trace.check_signal_dependency(data_input, data_to_check, 5, 'Golf', 200)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 6 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0,
                                  0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.WITHIN_RANGE, signal_range=[5,10])
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 7 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0,
                                  0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_incrementing(data, 14)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 8 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0,
                                  0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_pattern_with_delta(data, 0, 1, 14)
    HTML_Logger.ReportTestStepEnd()

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 9 --------------------")
    # INTEGER example
    data = trace.get_signal_value(channels["ADAS_1C0_AliveCounter"], 0,
                                  0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_pattern_with_delta(data, 0, 2, 14)
    HTML_Logger.ReportTestStepEnd()

    
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


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_ACC_Test(log)
    else:
        TC_ACC_Test(LOG)
