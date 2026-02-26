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



def TC_BackgroundCheck_ValueMatch_EgoSpeed_50kph():
    
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    HTML_Logger.TestReportHeader("Example : CANoePy v1.1 BackgroundCheck_ValueMatch_EgoSpeed_50kph with ADAS HIL 2.xx")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : TC_BackgroundCheck_ValueMatch_EgoSpeed_50kph")
    HTML_Logger.TestReportHeader("DefectID : None")

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
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", "ACC_CountryRoad_Test")  # fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.CheckSignal("Customer_specific", "cm_scenario", "ACC_CountryRoad_Test")  # check if scenario field is populated
    capl.AwaitValueMatch("hil_ctrl", "init_cm_done", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1)  # press the LOAD SCENARIO button
    #capl.TestWaitForTimeout(500)
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1)  # press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 70)
    tf.Set_Ego_Vehicle_Velocity(50.0)  # set ego speed
    capl.SetSignal("hil_drv", "gear_req", 3)  # set Gear to DRIVE
    capl.TestWaitForTimeout(2000)

    capl.BackgroundCheck_ValueMatch("hil_drv", "target_velocity", 50.0,5000)  # background check for ego speed = 50kph for 5 seconds, refresh rate = default (check every 50ms)

    capl.TestWaitForTimeout(10000)  #Wait duration longer than in the background check (to prove that it's really a background check :) )

    tf.Check_And_Acknowledge_HIL_Abort_Messages()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    TC_BackgroundCheck_ValueMatch_EgoSpeed_50kph()

#capl.Dispose()
