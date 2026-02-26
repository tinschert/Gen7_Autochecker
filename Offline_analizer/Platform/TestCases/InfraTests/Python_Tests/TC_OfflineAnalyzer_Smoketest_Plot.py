#created by PF Team
#copyright Robert Bosch GMBH
#date :
#this is a golden example of Python Offline testcase

import sys, os
import pandas as pd

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
    TC_Path = HTML_Logger.generate_report_offline(os.path.basename(__file__))
    HTML_Logger.setup(__file__, "Offline Analyzer Testcase", filename=TC_Path)  # create the HTML report
    HTML_Logger.TestReportHeader("Tester : XXX")
    HTML_Logger.TestReportHeader(f"TestCaseName : {os.path.basename(__file__)}")
    HTML_Logger.TestReportHeader("DefectID : None")
    HTML_Logger.TestReportHeader(f"RQM_ID : 3253665")
    HTML_Logger.TestReportHeader(f"Input log file -> {LOG}")
    trace = CommonFunc()  # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects
    channels = output.get_channels(["RFC_LocHdr_SensorOriginPointX", "ESP_WhlSpdVld_RR", "ADAS_1C0_AliveCounter"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    ################ TEST STEPS Section ############################################################################
    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 1 --------------------")
    # Get Dataframe for signal of provided range
    # FLOATING point example
    data = trace.get_signal_value(channels["RFC_LocHdr_SensorOriginPointX"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    data.at[462, 'Signal Value'] = 3
    trace.check_signal_update(data, Condition.EQUALS, 3.48)
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
    data = trace.get_signal_value(channels["ESP_WhlSpdVld_RR"], 0,0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.NOT_EQUALS,10)
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
    data_to_check = trace.get_signal_value(channels["ESP_WhlSpdVld_RR"], 0,
                                           0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range

    trace.check_signal_dependency(data_input, data_to_check, 5, 'Valid', 200)
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

    HTML_Logger.ReportWhiteMessage(f"--------------- Signals Plot --------------------")
    # Create combined plot of all input signals
    trace.create_combined_plot(channels, TC_Path)

    # opens the HTML report in Browser  (using the default OS configured browser)
    HTML_Logger.Show_HTML_Report(TC_Path)     #opens the HTML report in Browser  (using the default OS configured browser)


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_ACC_Test(log)
    else:
        TC_ACC_Test(LOG)
