#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface

import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir,r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API"))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\ReportGen"))
sys.path.append(os.path.join(script_dir, r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions"))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\TraceParser"))
sys.path.append(os.path.join(script_dir, r"..\..\..\Python_Testing_Framework\CommonTestFunctions"))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf
import Customer_Specific_Functions as cf
import time

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

#test_args = get_args()  # Get parsed arguments
# Define a constant for log files, could be a single log or a directory
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
#LOG = test_args.log_file_path


def TC_ACC_Test():

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report

    HTML_Logger.TestReportHeader("Example : CANoePy v1.1 POC ACC Test with Offline analysis")
    HTML_Logger.TestReportHeader("Tester : Rafael Herrera")
    HTML_Logger.TestReportHeader("TestCaseID : 3253665")
    HTML_Logger.TestReportHeader("DefectID : 123456789")

    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    #capl.StartMeasurement()
    capl.Start_MF4_BLF_Logging()

    if capl.GetSignal("","hil_ctrl/Project_ID", silent_flag=True)=="OD":
        capl.SetSignal("hil_ctrl", "configuration_od", 2)   #Phi1V
        HTML_Logger.ReportWhiteMessage("Execution in OD variant with Phi1V")
    elif capl.GetSignal("","hil_ctrl/Project_ID", silent_flag=True)=="FORD_DAT3":
        capl.SetSignal("hil_ctrl", "configuration_ford", 8)   #FULL STANDARD LIGHT
        HTML_Logger.ReportWhiteMessage("Execution in FORD variant with FULL STANDARD")
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)   #set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", "ACC_Smoke_Test")   #fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.CheckSignal("Customer_specific", "cm_scenario", "ACC_Smoke_Test")  #check if scenario field is populated
    capl.AwaitValueMatch("hil_ctrl","init_cm_done",1,80)    #wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1) #press the LOAD SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.SetSignal("Customer_specific", "load_scenario", 0) #release the LOAD SCENARIO button
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 80)    #wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1) #press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.SetSignal("hil_ctrl", "scenario_start", 0) #release the START SCENARIO button
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 80)

    #add here some more set signal functions to activate ACC
    tf.Set_Drv_gear(3)  #set Drive gear
    capl.TestWaitForTimeout(1000)
    tf.Set_Ego_Vehicle_Velocity(40.0)  #set 40kph
    capl.WaitForSignalInRange("hil_hvm","velocity_x", 39, 41, 25) #// check    40    kph
    tf.Activate_ACC_Cus()
    capl.TestWaitForTimeout(1000) #// wait    for second Check
    tf.ShortPress_ACC_SetPlus_Cus()
    capl.TestWaitForTimeout(1000)
    tf.ShortPress_ACC_SetPlus_Cus()
    capl.TestWaitForTimeout(1000)
    tf.Check_ACC_Status_Cus()
    capl.TestWaitForTimeout(15000)

    tf.Check_And_Acknowledge_HIL_Abort_Messages()
    capl.Start_MF4_BLF_Logging()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)       #press the STOP SIM button to END scenario/test

    # opens the HTML report in Browser  (using the default OS configured browser)
    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)

    
    # capl.StopMeasurement()

    capl.TestWaitForTimeout(5000) # wait for trace log to be ready
    LOG = r"D:\_RBS\_dev\rafael\adas_hil\Vehicle_Model_Test_1_Config2_T001.mf4"
    TC_ACC_Test_Offline(LOG)

############################# Offline Part ############################################################

def TC_ACC_Test_Offline(input_log):

    ################# Initialization ##############################################################################
    trace = CommonFunc()  # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects
    channels = output.get_channels(["RFC_LocHdr_SensorOriginPointX", "Vehicle_Variant", "ADAS_1C0_AliveCounter"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    ################ TEST STEPS Section ############################################################################

    HTML_Logger.ReportTestStepStart()
    HTML_Logger.ReportWhiteMessage(f"--------------- Test Step 3 --------------------")
    # STRING example
    data = trace.get_signal_value(channels["Vehicle_Variant"], 0,0)  # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    # Analysis
    trace.check_signal_update(data, Condition.NOT_EQUALS,"Golf")
    HTML_Logger.ReportTestStepEnd()

    # opens the HTML report in Browser  (using the default OS configured browser)
    HTML_Logger.Show_HTML_Report()     #opens the HTML report in Browser  (using the default OS configured browser)


if __name__ == "__main__":
    TC_ACC_Test("offline", [r"C:\Users\pep3sf4\Desktop\frame_based\Ego_out_of_boundaries_Config1_T001.mf4"])
