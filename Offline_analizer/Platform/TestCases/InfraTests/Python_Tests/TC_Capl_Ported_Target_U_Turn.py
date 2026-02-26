#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Nov.2024
#this is an example Python testcase using the XIL API

import sys
sys.path.append(r"../../../Python_Testing_Framework/CANoePy/using_XIL_API")
sys.path.append(r"../../../Python_Testing_Framework/ReportGen")
sys.path.append(r"../../../../adas_sim/python_testing_framework/common_test_functions")
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_1VxR_XIL_API as tf

import math

def Target_U_Turn(config, ego_speed, tgt_speed, vehicle_code):
    current_ego_tx = 0
    current_ego_ty = 0
    current_target_tx = 0
    current_target_ty = 0
    delta_tx = 0
    delta_ty = 0
    value1_drz = 0
    value2_drz = 0
    value3_drz = 0
    value4_drz = 0
    temp_string = str(['\0' for _ in range(255)])

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Example : Python Framework Testcase")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : Target_U_Turn")
    HTML_Logger.TestReportHeader("DefectID : None")
    # ===========================================================================================================================================================================

    # TEST STARTS HERE:

    capl.SetSignal("", "hil_adas/lat_ctrl_is_enabled", 0) #"Disable ADAS control over lateral movement of Ego");
    capl.SetSignal("", "hil_adas/long_ctrl_is_enabled", 0) #Disable ADAS control over longitudinal movement of Ego");

    capl.SetSignal("", "hil_ctrl::vehicle", vehicle_code)  # set the vehicle variant
    capl.SetSignal("hil_ctrl", "configuration_od", config)
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", r"Target_Overtaking_Ego_10m_cut")  # fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("hil_ctrl", "init_cm_done", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1)  # press the LOAD SCENARIO button
    # capl.TestWaitForTimeout(500)
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1)  # press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 70)

    tf.Set_Ego_Vehicle_Velocity(ego_speed)
    tf.Set_Drv_gear(3)  # set Drive gear
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed - 1,ego_speed + 1,25)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_velocity", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.ctrl_status_tgt_steering_wheel_angle", [1,0,0,0,0,0,0,0,0,0,0])

    capl.TestWaitForTimeout(5000)

    value1_drz = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/drz") * 57.29577951307854999853275233034  # radian-to-degree
    HTML_Logger.ReportWhiteMessage("value1_drz : " +str(value1_drz))
    # check that rotation Z equals 0 degrees
    if abs(value1_drz - 0) < 1.0:
        capl.ReportTestStepPass("Target rot Z DVA is equal to 0 degrees -> OK")
    else:
        capl.ReportTestStepFail("Target rot Z DVA is NOT equal to 0 degrees -> NOK")
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_tgt_steering_wheel_angle", [75,0,0,0,0,0,0,0,0,0,0])  # steer left 75 degrees
    capl.TestWaitForTimeout(12000)  # drive U turn for 15 seconds
    value2_drz = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/drz") * 57.29577951307854999853275233034  # radian-to-degree
    HTML_Logger.ReportWhiteMessage("value2_drz : "+str(value2_drz))
    # check that rotation Z equals 180 degrees
    if abs(value2_drz - 180) < 45.0:
        capl.ReportTestStepPass("Target rot Z DVA is equal to 180 degrees -> OK")
    else:
        capl.ReportTestStepFail("Target rot Z DVA is NOT equal to 180 degrees -> NOK")
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_tgt_steering_wheel_angle", [0,0,0,0,0,0,0,0,0,0,0])  # steer straight forward
    capl.TestWaitForTimeout(5000)  # drive forward 5 seconds after the U turn
    value3_drz = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/drz") * 57.29577951307854999853275233034  # radian-to-degree
    HTML_Logger.ReportWhiteMessage("value3_drz : " + str(value3_drz))
    # check that rotation Z doesnt change any more
    if abs(value3_drz - value2_drz) < 2.0:
        capl.ReportTestStepPass("Target rot Z DVA is not changing any more -> OK")
    else:
        capl.ReportTestStepFail("Target rot Z DVA is still changing -> NOK")

    capl.SetSignal("", "hil_adas/lat_ctrl_is_enabled", 1)  # "Enable ADAS control over lateral movement of Ego");
    capl.SetSignal("", "hil_adas/long_ctrl_is_enabled", 1)  # Enable ADAS control over longitudinal movement of Ego");

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test
    tf.Check_And_Acknowledge_HIL_Abort_Messages()
    if capl.GetSignal("", "hil_ctrl/jenkins_control") == 0: HTML_Logger.Show_HTML_Report()

    return capl.Testcase_End()

if __name__ == "__main__":
    # 0->off
    # 1->DPCDelta1
    # 2->Phi1V
    # 3->RPCAlpha2
    # 4->DPCdelta1_1V1D
    # 5->DPCdelta1_1R1D
    # 6->DPCdelta5
    # 7->DPCdelta5_1V1D
    # 8->DPCdelta5_1R1D
    # 9->TestDCP_1V1D4N
    # 10->RPCAlpha2_1R1V
    # 11->Replay_DPCdelta1
    # 12->Replay_DPCdelta5
    # 13->Replay_DPCalpha2
    Target_U_Turn(5, 0, 2, 0)
