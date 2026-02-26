#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the XIL API

import time
import threading
import sys
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf

force_stop_thread = False

def TDP_Process_Function():
    global force_stop_thread
    TDP_refresh_rate = capl.GetSignal("","Python_coupling/Python_Framework_TDP_refresh_rate",silent_flag=True)
    if TDP_refresh_rate==0:
        TDP_refresh_rate = 500   #put 500ms if the value can not be taken from the CANoe sysvar
    TDP_refresh_rate=TDP_refresh_rate/1000
    is_TC_running = capl.GetSignal("","Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", True)
    #abort message read refresh rate is around 500ms
    #the function GetSignal for the abort message is called 10x slower than the TDP refresh rate (Python<>CANoe sync time)
    #reason is to save XIL API bandwidth for reading-reading-reading
    cnt=0
    while(is_TC_running==1):
        if cnt==0:
            # the function GetSignal for the abort message is called 10x slower than the TDP refresh rate (Python<>CANoe sync time)
            # reason is to save XIL API bandwidth for reading-reading-reading
            if (capl.GetSignal("", "hil_ctrl/abort_message", silent_flag=True) != "no abort"):
                HTML_Logger.ReportRedMessage("\n\n=======================================================================")
                HTML_Logger.ReportRedMessage("WARNING : HIL ABORT MESSAGE occurred now")
                HTML_Logger.ReportRedMessage(capl.GetSignal("", "hil_ctrl/abort_message", True))
                HTML_Logger.ReportYellowMessage("Following measures are taken : ")
                HTML_Logger.ReportWhiteMessage("1)Testcase global verdict set to : FAILED")
                HTML_Logger.ReportWhiteMessage("2)Testcase execution aborted")
                HTML_Logger.ReportWhiteMessage("3)HTML/XML report created until HIL abort occurred")
                HTML_Logger.ReportWhiteMessage("4)MF4/BLF trace will be recorded until HIL abort occurred")
                HTML_Logger.ReportWhiteMessage("5)All teststeps after the HIL abort will NOT be executed")
                HTML_Logger.ReportRedMessage("=======================================================================\n\n")
                capl.reaction_on_abort_message()
        cnt=cnt+1
        if cnt>10: cnt = 0
        is_TC_running = capl.GetSignal("", "Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", True)
        CANoe_global_counter_value = capl.GetSignal("", "hil_ctrl::global_counter", True)
        capl.SetSignal("","Python_coupling/Python_Framework_CANoe_counter_loopback",CANoe_global_counter_value, 0,True)
        time.sleep(TDP_refresh_rate)
        if force_stop_thread == True: exit()
    exit()

t1 = threading.Thread(target=TDP_Process_Function, args=[])

def TC_TDP_InfraTest_Stop_Python_Loopback():
    #function capl.Testcase_Start is not called (which starts the TDP threads;
    HTML_Logger.setup(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name()) #create the HTML report
    #0 -> testcase not running
    #1 -> testcase running
    capl.SetSignal("","Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", 1, silent_flag=True)
    t1.start()
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

    #trigger a TDP fault : Stop Python Loopback counter to CANoe
    HTML_Logger.ReportWhiteMessage("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportBlueMessage("!!! Stop Python Loopback counter to CANoe !!!\n")

    global force_stop_thread
    force_stop_thread = True
    capl.TestWaitForTimeout(10000) #wait some time with stopped loopback counter so CANoe has to react with HIL abort message

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
    TC_TDP_InfraTest_Stop_Python_Loopback()

#capl.Dispose()
