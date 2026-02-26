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



def Target_Lane_Change_CCRs(config, ego_speed, tgt_speed, vehicle_code):
    old_offset = 0.0
    new_offset = 0.0
    tolerance = 1.0
    target_offset = 3.5

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    HTML_Logger.TestReportHeader("Example : Python Framework Testcase")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : Target_Lane_Change_CCRs")
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
    capl.SetSignal("Customer_specific", "cm_scenario", r"Infra_scenarios/Target_Lane_Change_CCRs")  # fill the scenario name
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

    old_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")

    # check with timeconstant 5 seconds
    capl.SetSignal("","Classe_Obj_Sim/obj_ctrl.par_lane_offset_timeconstraint", 5)
    # offset 3.5m(left)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [3.5,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = "+str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if ((new_offset <= (old_offset + target_offset + tolerance)) and (new_offset >= (old_offset + target_offset - tolerance))):
        capl.ReportTestStepPass("Left target offset worked properly")
    else:
        capl.ReportTestStepFail("Left target offset didn't work properly")

    # offset 0m (original lane)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)

    # offset -3.5m (right)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset",[-3.5,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = " + str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if new_offset >= old_offset - (target_offset + tolerance) and new_offset <= old_offset - (target_offset - tolerance):
        capl.ReportTestStepPass("Right target offset worked properly")
    else:
        capl.ReportTestStepFail("Right target offset didn't work properly")

    capl.TestWaitForTimeout(1000)

    # offset 0m (original lane)
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", 0)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0,0,0,0,0,0,0,0,0,0,0])

    # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # check with timeconstant 10 seconds
    capl.SetSignal("","Classe_Obj_Sim/obj_ctrl.par_lane_offset_timeconstraint", 10)
    # offset 3.5m(left)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [3.5,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = " + str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if new_offset <= old_offset + target_offset + tolerance and new_offset >= old_offset + target_offset - tolerance:
        capl.ReportTestStepFail("Too early --> NOK")
    else:
        capl.ReportTestStepPass("Not yet changed lane -> OK")
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = " + str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if new_offset <= old_offset + target_offset + tolerance and new_offset >= old_offset + target_offset - tolerance:
        capl.ReportTestStepPass("Time for lane change -> OK")
    else:
        capl.ReportTestStepFail("Time for lane change NOK")

    # offset 0m (original lane)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)

    # offset -3.5m (right)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [-3.5,0,0,0,0,0,0,0,0,0,0])
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = " + str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if new_offset >= old_offset - (target_offset + tolerance) and new_offset <= old_offset - (target_offset - tolerance):
        capl.ReportTestStepFail("Too early --> NOK")
    else:
        capl.ReportTestStepPass("Not yet changed lane -> OK")
    capl.TestWaitForTimeout(5000)
    new_offset = capl.GetSignal("","CarMaker/RB/TrafficObj/object0/dty")
    HTML_Logger.ReportWhiteMessage("old offset = " + str(old_offset))
    HTML_Logger.ReportWhiteMessage("new offset = " + str(new_offset))
    if new_offset >= old_offset - (target_offset + tolerance) and new_offset <= old_offset - (target_offset - tolerance):
        capl.ReportTestStepPass("Time for lane change -> OK")
    else:
        capl.ReportTestStepFail("Time for lane change NOK")
    capl.TestWaitForTimeout(1000)

    # offset 0m (original lane)
    capl.SetSignal("","hil_ctrl/Ego_lane_offset", 0)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0,0,0,0,0,0,0,0,0,0,0])

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
    Target_Lane_Change_CCRs(2, 35, 35, 0)
