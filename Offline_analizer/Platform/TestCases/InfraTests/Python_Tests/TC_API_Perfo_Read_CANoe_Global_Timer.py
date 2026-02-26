#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the XIL API

import sys
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf
import time

read_cycle_time = 0.05  #50ms

def TC_API_Perfo_Read_CANoe_Global_Time(test_duration = 10):   #default test duration 10 seconds
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())
    HTML_Logger.TestReportHeader("Example : CANoePy v1.1 API_Perfo_Read_CANoe_Global_Time with ADAS HIL 2.xx")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseName : TestCase_API_Perfo_Read_CANoe_Global_Time")
    HTML_Logger.TestReportHeader("Requirement_ID : 123456789")
    HTML_Logger.TestReportHeader("RQM_ID : 12345")
    HTML_Logger.TestReportHeader("Defect_ID : None")
    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    #capl.StartMeasurement()
    #HIL MODE = Classe then Configuration 1R1D to enable bus communication
    capl.Start_MF4_BLF_Logging()

    capl.SetSignal("hil_ctrl", "hil_mode", 2)  # set HIL mode to Classe
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "configuration_od", 2)  # set configuration = 2
    capl.TestWaitForTimeout(3000)

    #get signal in silent mode (no console output) for better performance
    num_loops_for_required_test_duration = test_duration / read_cycle_time / 4 / 2
    # print(num_loops_for_required_test_duration)
    counter2 = 0
    while (counter2<=num_loops_for_required_test_duration):
            value_1 = capl.GetSignal("", "hil_ctrl::global_counter", False)
            time.sleep(read_cycle_time)
            value_2 = capl.GetSignal("", "hil_ctrl::global_counter",False)
            counter2=counter2+1
            time.sleep(read_cycle_time)
            if (value_1==value_2):
                capl.ReportTestStepFail("Values of CANoe global timer are the same -> FAILED",False)
                final_verdict="FAILED"

    #capl.StopMeasurement()
    #capl.SetSignal("hil_ctrl","abort_message","Fake abort message")
    tf.Check_And_Acknowledge_HIL_Abort_Messages()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    TC_API_Perfo_Read_CANoe_Global_Time()
    capl.Disconnect()
    capl.Dispose()
