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

old_offset = 0
new_offset = 0
temp_str = str(['\0' for _ in range(256)])
tolerance = 0.5 #tolerance for checking if the ego really moved 0.1 = 0.1 meters
ego_offset = 3.5 #3.5 meters are checked in both directions


def Ego_Lane_Change_CCRs(config, ego_speed, tgt_speed, vehicle_code):
    i = 0

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Example : Python Framework Testcase")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : Ego_Lane_Change_CCRs")
    HTML_Logger.TestReportHeader("DefectID : None")
    # ===========================================================================================================================================================================

    # TEST STARTS HERE:
    capl.SetSignal("", "hil_ctrl::vehicle", vehicle_code)  # set the vehicle variant
    capl.SetSignal("hil_ctrl", "configuration_od", config)
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario", r"Infra_scenarios/Ego_Lane_Change_CCRs")  # fill the scenario name
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
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_velocity", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed - 1,ego_speed + 1,25)
    capl.SetSignal("","hil_ctrl/Ego_lane_offset_time", 2)
    capl.TestWaitForTimeout(10000)
    old_offset = capl.GetSignal("","CarMaker/Car/Gen/ty") #this is the loop-back if EGO really changed the lane
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", ego_offset)
    capl.TestWaitForTimeout(10000)
    new_offset = capl.GetSignal("","CarMaker/Car/Gen/ty") #this is the loop-back if EGO really changed the lane
    #new_offset=GetSignal("","hil_ctrl::Ego_lane_offset")
    if (new_offset <= (old_offset + ego_offset + tolerance)) and (new_offset >= (old_offset + ego_offset - tolerance)):
        capl.ReportTestStepPass("Left EGO offset worked properly")
    else:
        capl.ReportTestStepFail("Left EGO offset didn't work properly")
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", 0)
    capl.TestWaitForTimeout(10000)
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", -ego_offset)
    capl.TestWaitForTimeout(10000)
    new_offset = capl.GetSignal("","CarMaker/Car/Gen/ty") #this is the loop-back if EGO really changed the lane
    if (new_offset >= old_offset - (ego_offset + tolerance)) and (new_offset <= old_offset - (ego_offset - tolerance)):
        capl.ReportTestStepPass("Right EGO offset worked properly")
    else:
        capl.ReportTestStepFail("Right EGO offset didn't work properly")
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", 0)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset",[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

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
    Ego_Lane_Change_CCRs(2, 25, 25, 0)
