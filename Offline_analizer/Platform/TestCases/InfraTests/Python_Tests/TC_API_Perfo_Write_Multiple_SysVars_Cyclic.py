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

write_cycle_time = 0.002  #2ms

def TC_API_Perfo_Write_Multiple_SysVars_Cyclic(test_duration = 10):   #default test duration 10 seconds
    
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    HTML_Logger.TestReportHeader("Example : CANoePy v1.1 API_Perfo_Write_Multiple_SysVars_Cyclic with ADAS HIL 2.xx")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : TestCase_API_Perfo_Write_Multiple_SysVars_Cyclic")
    HTML_Logger.TestReportHeader("DefectID : None")

    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    #capl.StartMeasurement()
    # HIL MODE = Classe then Configuration 1R1D to enable bus communication
    capl.Start_MF4_BLF_Logging()

    capl.SetSignal("hil_ctrl", "hil_mode", 2)  # set HIL mode to Classe
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl","configuration_od", 2)  # set configuration = 2
    capl.TestWaitForTimeout(3000)

    counter = 0
    counter2 = 0
    num_loops_for_required_test_duration = test_duration/write_cycle_time/4
    #print(num_loops_for_required_test_duration)
    while (counter2<=num_loops_for_required_test_duration):
        while(counter<=1):
            capl.SetCheckSignal("", "hil_ctrl::abort_message", "text"+str(counter), write_cycle_time,True)
            capl.SetCheckSignal("", "hil_ctrl::adas_hil_version_minor", counter, write_cycle_time,True)
            counter = counter + 1
        counter = 0
        counter2=counter2+1

    #under heavy stress load API connection is lost -> CANoe crashes or stops updating write values; read values are freezed to last values
    final_verdict=tf.Check_API_Connection()
    #capl.StopMeasurement()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    TC_API_Perfo_Write_Multiple_SysVars_Cyclic()
    capl.Disconnect()
    capl.Dispose()
