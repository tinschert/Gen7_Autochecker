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

def Vehicle_Model_Test_1(config, ego_speed, tgt_speed, vehicle_code):
    i = 0
    tolerance = 3  # tolerance for checking yaw angle
    angle_from_CM = 0  # heading angle of the target as loopback from CarMaker (taken from RB::Radar DVAs structure)
    temp_string = str(['\0' for _ in range(255)])
    current_object = 0
    current_object_string = str(['\0' for _ in range(255)])
    current_rotation_angle_string = str(['\0' for _ in range(255)])
    old_gen_ty = 0

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Example : Python Framework Testcase")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : Vehicle_Model_Test_1")
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
    capl.SetSignal("Customer_specific", "cm_scenario", r"Vehicle_Model_Test_1")  # fill the scenario name
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
    # 0-park,1-reverse,2-neutral, 3-drive
    tf.Set_Drv_gear(3)  # set Drive gear
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed - 1,ego_speed + 1,25)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_velocity", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    capl.SetSignal("","hil_drv/target_velocity", 10)
    capl.AwaitValueMatch("","hil_hvm/velocity_x", 10, 15)
    capl.TestWaitForTimeout(5000)
    capl.AwaitValueMatch("","hil_hvm/velocity_x", 10, 10)
    old_gen_ty = capl.GetSignal("","CarMaker/Car/Gen/ty")

    HTML_Logger.ReportWhiteMessage("Step 01"+"Check steering mechanism")

    HTML_Logger.ReportWhiteMessage(""+"Initial lateral offset on road: CarMaker::Car::Gen::ty = "+str(capl.GetSignal("","CarMaker/Car/Gen/ty")))
    capl.SetSignal("","hil_drv/steering_wheel_angle_req", 120)
    capl.TestWaitForTimeout(1250)
    capl.WaitForSignalInRange("","CarMaker/Car/Gen/ty", old_gen_ty - 0.75, old_gen_ty - 0.25, 100)
    capl.TestWaitForTimeout(1250)
    capl.SetSignal("","hil_drv/steering_wheel_angle_req", -120)
    capl.TestWaitForTimeout(2500)
    capl.SetSignal("","hil_drv/steering_wheel_angle_req", 0)
    capl.TestWaitForTimeout(2500)
    capl.WaitForSignalInRange("","CarMaker/Car/Gen/ty", old_gen_ty - 3, old_gen_ty - 1, 100)
    HTML_Logger.ReportWhiteMessage("Gen::ty 1 = " +str(capl.GetSignal("","CarMaker/Car/Gen/ty")))
    HTML_Logger.ReportWhiteMessage("DELTA Gen::ty 1 = ", old_gen_ty - capl.GetSignal("","CarMaker/Car/Gen/ty"))

    HTML_Logger.ReportWhiteMessage("Step 02"+"Check target speed control")

    capl.SetSignal("","hil_drv/target_velocity", 0)  # ego_speed;
    capl.SetSignal("","hil_drv/target_velocity", 0)
    capl.AwaitValueMatch("","hil_hvm/velocity_x", 0, 15)
    # 0-park,1-reverse,2-neutral, 3-drive
    capl.SetCheckSignal("","hil_drv/gear_req", 1)
    capl.SetSignal("","hil_drv/target_velocity", 10)
    capl.AwaitValueMatch("","hil_hvm/velocity_x", 10, 10)  # reverse gear 10kph
    capl.SetSignal("","hil_drv/target_velocity", 0)
    capl.TestWaitForTimeout(5000)
    capl.AwaitValueMatch("","hil_hvm/velocity_x", 0, 10)  # reverse gear 10kph

    HTML_Logger.ReportWhiteMessage("Step 03"+"Door control")

    #open
    capl.SetCheckSignal("","hil_vehicle/door_status_fl", 1)
    capl.SetCheckSignal("","hil_vehicle/door_status_fr", 1)
    capl.SetCheckSignal("","hil_vehicle/door_status_rl", 1)
    capl.SetCheckSignal("","hil_vehicle/door_status_rr", 1)

    #closed
    capl.SetCheckSignal("","hil_vehicle/door_status_fl", 0)
    capl.SetCheckSignal("","hil_vehicle/door_status_fr", 0)
    capl.SetCheckSignal("","hil_vehicle/door_status_rl", 0)
    capl.SetCheckSignal("","hil_vehicle/door_status_rr", 0)

    HTML_Logger.ReportWhiteMessage("Step 04"+"Indicator light control")

    capl.SetCheckSignal("","hil_drv/indicator_light", 1)    #left
    capl.SetCheckSignal("","hil_drv/indicator_light", 2)    #Right
    capl.SetCheckSignal("","hil_drv/indicator_light", 3)    #hazard lights
    capl.SetCheckSignal("","hil_drv/indicator_light", 0)    #not active

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
    Vehicle_Model_Test_1(5, 0, 2, 0)
