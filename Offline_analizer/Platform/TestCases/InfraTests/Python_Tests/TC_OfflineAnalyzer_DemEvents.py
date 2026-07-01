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
import HTML_Logger
import pandas as pd
import numpy as np

try:
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
except:
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser


# Define a constant for log files, could be a single log or a directory
LOG = r"C:\TOOLS\Gen7_DEM_Events\Measurements\RA7_20260503_152136_013.MF4" # Path example
# DEM_HEADER_FILE = r"C:\Users\pep3sf4\Desktop\Test_mf4\Dem_Cfg_EventId.h"
# DEM_EXCLUSION_LIST = r"C:\Users\pep3sf4\Desktop\Test_mf4\Dem_exclusion_list.txt"
#LOG = test_args.log_file_path
#DEM_HEADER_FILE = test_args.dem_header_path
#DEM_EXCLUSION_LIST = test_args.dem_exclusion_list

def expand_array_signal(Array_data):
    def to_binary_byte_array(value):
        # Some traces provide [[...bytes...]] per row; flatten one level if present.
        if isinstance(value, np.ndarray):
            value = value.tolist()

        if isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], (list, tuple, np.ndarray)):
            value = value[0]

        if isinstance(value, np.ndarray):
            value = value.tolist()

        if not isinstance(value, (list, tuple)):
            return []

        return [format(int(byte) & 0xFF, "08b") for byte in value]

    expanded = pd.DataFrame(
        Array_data["Signal Value"].apply(to_binary_byte_array).tolist()
    )

    expanded.columns = [
        f"EventStatusByte_{i}"
        for i in range(expanded.shape[1])
    ]

    result = pd.concat(
        [
            Array_data[["Signal Name", "Timestamp"]],
            expanded
        ],
        axis=1
    )

    return result

def DEM_Events_Check(input_log):
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    output.list_channels() # If needed user can check all available channels objects
    # input from jenkins a trace or folder and from the online analyzer ***

    # load DEM event IDs
    DEM_Events_Channels = output.get_channels([("RadarFC", "MEAS_COREX_RSP_EV", "g_ConfigurationData.m_envData.vxvRef.m_value"),
                                                ("RadarFC", "MEAS_CORE0_10MS_EV","Dem_AllEventsMonitorStatus"),
                                                ("RadarFC", "m051F2FDD", "g_ARM_rbBsw_rbCom_rbCom_netRunnable_m_portPerEmsComInput_out_local.m_arrayPool[1].elem.comSensorSignals.accelerationSensorInput.axVehSensor.m_value"),
                                                ("RadarFC", "MEAS_CORE0_10MS_EV", "Dem_AllEventsStatusByte")])
     
    DEM_Event_data = trace.get_signal_value(DEM_Events_Channels["Dem_AllEventsStatusByte"], 0, 0)
    
    Converted_DEM_Event_data = expand_array_signal(DEM_Event_data)
 
    print("test")


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            DEM_Events_Check(log)
    else:
        DEM_Events_Check(LOG)
