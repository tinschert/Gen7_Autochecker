#created by PF Team
#copyright Robert Bosch GMBH
#date :
#this is a golden example of Python Offline testcase

import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\ReportGen"))
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
# LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
# DEM_HEADER_FILE = r"C:\Users\pep3sf4\Desktop\Test_mf4\Dem_Cfg_EventId.h"
# DEM_EXCLUSION_LIST = r"C:\Users\pep3sf4\Desktop\Test_mf4\Dem_exclusion_list.txt"
LOG = test_args.log_file_path
DEM_HEADER_FILE = test_args.dem_header_path
DEM_EXCLUSION_LIST = test_args.dem_exclusion_list

def TC_DEM_Events_Test(input_log):

    ################# Initialization ##############################################################################
    HTML_Logger.setup(__file__, "Offline Analyzer Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Tester : XXX")
    HTML_Logger.TestReportHeader(f"TestCaseName : {os.path.basename(__file__)}")
    HTML_Logger.TestReportHeader("DefectID : None")
    HTML_Logger.TestReportHeader(f"RQM_ID : 3253665")
    HTML_Logger.TestReportHeader(f"Input log file -> {LOG}")
    HTML_Logger.TestReportHeader(f"DEM events header file -> {DEM_HEADER_FILE}")
    HTML_Logger.TestReportHeader(f"DEM events exclusion list file -> {DEM_EXCLUSION_LIST}")
    trace = CommonFunc()  # Create testing functions object, shall be instantiated once per test
    ################################################################################################################

    ################ TEST STEPS Section ############################################################################
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    #output.list_channels() # If needed user can check all available channels objects
    dem_dict = trace.parse_dem_events(DEM_HEADER_FILE, DEM_EXCLUSION_LIST)


    for index, (key, val) in enumerate(dem_dict.items()):
        HTML_Logger.ReportTestStepStart()
        HTML_Logger.ReportWhiteMessage(f"--------------- Test Step {index+1} --------------------")
        channel = output.get_channels([val]) # Provide channels of interest as a string list. Functions will return mdf channel objects
        if channel:
            channel[key] = channel[val]
            del channel[val]
            print(f"Analyzing -> {key}")
            data = channel[key]
            data.at[1, 'Signal Value'] = 255
            data.at[34, 'Signal Value'] = 255
            trace.check_dem_events(channel[key], key)

        HTML_Logger.ReportTestStepEnd()
    # opens the HTML report in Browser  (using the default OS configured browser)
    HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)

    # capl.StopMeasurement()

if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_DEM_Events_Test(log)
    else:
        TC_DEM_Events_Test(LOG)
