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
    HTML_Logger.ReportYellowMessage("This is the list of all CANoe symbols from your project : ")
    capl.Extract_CANoe_Symbols()


    #capl.SetSignal("","DIAG_Tester_uC/DID/Req_SW_Tag",1,0)
    #capl.TestWaitForTimeout(150)
    #capl.SetSignal("", "DIAG_Tester_uC/DID/Req_SW_Tag", 0, 0)

    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    TC_API_Perfo_Read_CANoe_Global_Time()
    capl.Disconnect()
    capl.Dispose()
