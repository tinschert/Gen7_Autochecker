#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for OD Project

import sys, os
import matplotlib.pyplot as plt
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")
import json
import os
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger

def get_min_max_signal_values(df):
    min_value = df['Signal Value'].min()
    max_value = df['Signal Value'].max()
    return min_value, max_value

def get_first_last_timestamps(df):
    first_timestamp = df['Timestamp'].iloc[0]
    last_timestamp = df['Timestamp'].iloc[-1]
    return first_timestamp, last_timestamp

def get_modified_basename(file_path):
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    if ext.lower() == '.mf4':
        return f"{name}__ra5".lower()
    else:
        raise ValueError("The provided file is not an .mf4 file")
    
def get_filename_and_extension(file_path):
    return os.path.basename(file_path)

def generate_json(output_path, SEEK_ID, StbM_Status_min, Stbm_status_Max, StbM_Timestamp_Start_26bit, StbM_Timestamp_End_26bit, StbM_Timestamp_Start, StbM_Timestamp_End, MDF_File_Path,MDF_File_name):
    data = {
        "SequenceInformation_Radar": {
            "Modified": datetime.now().isoformat(),
            "StbM_Status_Min": int(StbM_Status_min),
            "StbM_Status_Max": int(Stbm_status_Max),
            "StbM_Timestamp_Start_26bit": int(StbM_Timestamp_Start_26bit),
            "StbM_Timestamp_End_26bit": int(StbM_Timestamp_End_26bit),
            "StbM_Timestamp_Start": int(StbM_Timestamp_Start),
            "StbM_Timestamp_End": int(StbM_Timestamp_End),
            "MDF_File_Path": MDF_File_Path,
            "MDF_File_Name": MDF_File_name
        }
    }
    
    file_name = f"{SEEK_ID}.json"
    file_path = os.path.join(output_path, file_name)
    
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

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
LOG = r"C:\TOOLS\OD_Radar_Seek\File_Temp" # Single log example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\SPA_Demo_20241218_101337_001.mf4"

json_output = r"C:\TOOLS\OD_Radar_Seek\Json_output"

def TC_OD_SEEK_Input(input_log,json_output):

    HTML_Logger.setup(__file__, "OD_Radar_SEEK_Upload", filename=HTML_Logger.generate_report_name())  # create the HTML report

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects

    channels = output.get_channels(["_StbM_GlobalTimeTupleArray_ast._0_._timeBaseStatus",
                                    "_g_PL_AD_fw_fsi_fsi_apl_net_apl_g_netRunnable.m_AbsRefTime_StbM_ms", 
                                    "GNSS_UTC_Unix"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    # Get Dataframe for signal of provided range
    # Extract the StbM Min und maximum values from the measurement.
    StbM_Status_data = trace.get_signal_value(channels["_StbM_GlobalTimeTupleArray_ast._0_._timeBaseStatus"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    StbM_Status_min, Stbm_status_Max = get_min_max_signal_values(StbM_Status_data)
    StbM_Status_first, StbM_Status_last = get_first_last_timestamps(StbM_Status_data)

    #Taking the StbM Timestamps from the measurement
    StbM_Timestamp_data = trace.get_signal_value(channels["_g_PL_AD_fw_fsi_fsi_apl_net_apl_g_netRunnable.m_AbsRefTime_StbM_ms"], 0, 0)
    StbM_Timestamp_Start_26bit, StbM_Timestamp_End_26bit = get_min_max_signal_values(StbM_Timestamp_data)
    
    #Taking the GPS UNIX times form the measurments.
    GNSS_UTC_Unix_data = trace.get_signal_value(channels["GNSS_UTC_Unix"], 0, 0)
    StbM_Timestamp_Start, StbM_Timestamp_End = get_min_max_signal_values(GNSS_UTC_Unix_data)
    
    SEEK_ID = get_modified_basename(input_log)
    MDF_Path = r"\\abtvdfs2.de.bosch.com\ismdfs\iad\validation\ods_vehicle\04_AEB\240506_Alpha2_OD_VTC18106_NCAP26_CMCscp_CPNCO"
    MDF_File_name = get_filename_and_extension(input_log)


    generate_json(json_output, SEEK_ID, StbM_Status_min, Stbm_status_Max,
                   StbM_Timestamp_Start_26bit, StbM_Timestamp_End_26bit,
                   StbM_Timestamp_Start, StbM_Timestamp_End,MDF_Path,MDF_File_name)

    print("Job_done!")


    # opens the HTML report in Browser  (using the default OS configured browser)
    #HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)

    # capl.StopMeasurement()

if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_OD_SEEK_Input(log,json_output)
    else:
        TC_OD_SEEK_Input(LOG,json_output)
