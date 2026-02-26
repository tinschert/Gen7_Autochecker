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



def TC_TDP_InfraTest_Stop_CANoe_GlobalTimer():
    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    HTML_Logger.TestReportHeader("Example : Python Framework Testcase")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : "+__file__)
    HTML_Logger.TestReportHeader("DefectID : None")

    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    #capl.Extract_CANoe_Symbols()
    #capl.StartMeasurement()
    capl.Start_MF4_BLF_Logging()

    if capl.GetSignal("","hil_ctrl/Project_ID", silent_flag=True)=="OD":
        capl.SetSignal("hil_ctrl", "configuration_od", 5)   #Phi1V
        HTML_Logger.ReportWhiteMessage("Execution in OD variant with Phi1V")
    elif capl.GetSignal("","hil_ctrl/Project_ID", silent_flag=True)=="FORD_DAT3":
        capl.SetSignal("hil_ctrl", "configuration_ford", 8)   #FULL STANDARD LIGHT
        HTML_Logger.ReportWhiteMessage("Execution in FORD variant with FULL STANDARD")
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", r"Infra_scenarios\\PER_tests\\Fusion_MultiObj")  # fill the scenario name
    capl.TestWaitForTimeout(1000)
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

    tf.Set_Ego_Vehicle_Velocity(58.0)  # set 40kph
    tf.Set_Drv_gear(3)  # set Drive gear
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [45, 55, 50, 45, 45, 45, 35, 55, 55, 55, 55])   #set target object to 40kph

    #capl.SetSignal("","hil_drv/high_beam_is_on",1)   #high beam ON
    #capl.SetSignal("","hil_drv/low_beam_is_on", 1)   #low beam ON
    #capl.SetSignal("","hil_drv/indicator_light", 3)  #hazard lights

    capl.TestWaitForTimeout(2500)
    capl.SetSignal("", "hil_ctrl/Ego_lane_offset", 3.5)  # move left lane
    capl.TestWaitForTimeout(2500)

    #trigger a TDP fault : Stop CANoe global counter for 2 seconds
    HTML_Logger.ReportWhiteMessage("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportBlueMessage("!!! Stop CANoe global counter for 2 seconds !!!\n")
    capl.SetSignal("","hil_ctrl/global_counter",0)
    for i in range(200):
        capl.SetSignal("","hil_ctrl/global_counter",0,delay_after_set=0, silent_flag=True)
        capl.TestWaitForTimeout(10)
    capl.TestWaitForTimeout(2000)

    tf.Check_And_Acknowledge_HIL_Abort_Messages()


    #generate testcase final verdict - > PASSED if there is a TDP error reaction
    f_name = "Reports\\" + HTML_Logger.find_newest_file_in_folder('Reports')
    f1 = open(f_name)
    testcase_verdict = "FAILED"
    for el in f1:
        if el.find(r"Abort Message : PYTHON TDP ERROR:cnt_diff=") >= 0:
            testcase_verdict = "PASSED"
            break

    capl.SetSignal("", "Python_coupling/string_result_from_Python", testcase_verdict,silent_flag = True)
    HTML_Logger.ReportWhiteMessage("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportWhiteMessage(   "TESTCASE FINAL VERDICT : ")
    if (testcase_verdict=="PASSED"):
        HTML_Logger.ReportGreenMessage("PASSED\n\n\n")
    else:
        HTML_Logger.ReportRedMessage("FAILED\n\n\n")
    f1.close()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    # opens the HTML report in Browser  (using the default OS configured browser)
    if capl.GetSignal("", "hil_ctrl/jenkins_control") == 0: HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)

    if (testcase_verdict=="PASSED"):
        exit(0)
    else:
        exit(-1)


if __name__ == "__main__":
    TC_TDP_InfraTest_Stop_CANoe_GlobalTimer()

#capl.Dispose()
