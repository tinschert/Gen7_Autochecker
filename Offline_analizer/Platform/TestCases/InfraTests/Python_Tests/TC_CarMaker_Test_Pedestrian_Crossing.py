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


def TC_CarMaker_Test_Pedestrian_Crossing():
    
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    HTML_Logger.TestReportHeader("Example : CANoePy v1.1 CarMaker_Test_Pedestrian_Crossing with ADAS HIL 2.xx")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : 1")
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
    capl.CheckSignal("hil_ctrl","configuration_od",2) #check configuration == 2
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.CheckSignal("hil_ctrl", "hil_mode", 4) #check HIL mode == 4
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", "AEB_EgoLong_PedestrianCrossing_left_to_right")  # fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.CheckSignal("Customer_specific", "cm_scenario","AEB_EgoLong_PedestrianCrossing_left_to_right")  # check if scenario field is populated
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

    # add here some more set signal functions to activate your feature
    tf.Set_Ego_Vehicle_Velocity(50.0)  # set ego speed
    capl.SetSignal("hil_drv", "gear_req", 3)  # set Gear to DRIVE

    # add here some more check functions to check if ACC works
    # capl.CheckSignal()
    #capl.TestWaitForTimeout(10000) #drive 10 seconds
    capl.WaitForSignalInRange("CarMaker", "RB/TrafficObj/object0/dtx",25,30,60)
    capl.SetSignal("hil_drv","brake_pedal_position",40)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long",[13,0,0,0,0,0,0,0,0,0,0])
    #END OF SIMULATION
    capl.TestWaitForTimeout(5000) #wait 5 seconds

    tf.Check_And_Acknowledge_HIL_Abort_Messages()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    #capl.StopMeasurement() #STOPS CANoe measurement
    #capl.Dispose()

    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    return capl.Testcase_End()

if __name__ == "__main__":
    TC_CarMaker_Test_Pedestrian_Crossing()


