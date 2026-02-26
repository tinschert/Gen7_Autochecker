#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Nov.2024
#this is an example Python testcase using the XIL API

import sys
sys.path.append(r"../../../Platform/Python_Testing_Framework/CANoePy/using_XIL_API")
sys.path.append(r"../../../Platform/Python_Testing_Framework/ReportGen")
sys.path.append(r"../common_test_functions")

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf




def AEB_EgoTurnLeft_TargetCrossing_Pedestrian__AEB_CPTA_I_10(config, ego_speed, tgt_speed):
    capl.Testcase_Start(__file__, "CANoePy Testcase",
                      filename=HTML_Logger.generate_report_name())  # create the HTML report

    tf.cf_testPreparation()
    tf.PreConditionsCM(config)
    capl.SetSignal("Customer_specific", "cm_scenario","AEB_EgoTurnLeft_TargetCrossing_Pedestrian__AEB_CPTA_I_10")
    #tf.CM_start()
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("hil_ctrl", "init_cm_done", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1)  # press the LOAD SCENARIO button
    #capl.TestWaitForTimeout(500)
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 80)  # wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1)  # press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    tf.PreConditionsAEB()
    capl.ReportTestStepPass("Test case", "Start")
    tf.Set_Ego_Vehicle_Velocity(ego_speed)
    #hil_ctrl.obj_target_velocity.long_velocity_tgt[0] =
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # set target object to tgt_speed
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed-1, ego_speed+1, 25)
    capl.WaitForSignalInRange("","CarMaker/RB/TrafficObj/object0/rel_dx", 0, 30, 25)
    capl.SetSignal("","hil_ctrl/trigger_tgt_collision_turncross", 0)
    capl.SetSignal("", "CAN_ADAS/OD_ADAS_Public_CANFD/MGW/CIM_0x310/CIM_TurnLampSwtSts", 1)
    capl.WaitForSignalInRange("","hil_adas/acceleration_x_type_req", 1, 3, 40)
    
    if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
        capl.ReportTestStepFail("FAILED")
    elif capl.GetSignal("","hil_adas/acceleration_x_type_req") in [1, 2, 3]:
        capl.ReportTestStepPass("PASSED")
    
    capl.SetSignal("", "CAN_ADAS/OD_ADAS_Public_CANFD/MGW/CIM_0x310/CIM_TurnLampSwtSts", 0)
    capl.TestWaitForTimeout(2000)
    tf.PostConditionsAEB()
    tf.PostConditionsCM()

    tf.Check_And_Acknowledge_HIL_Abort_Messages()

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test

    tf.PostConditionsAEB()
    tf.PostConditionsCM()
    if capl.GetSignal("","hil_ctrl/jenkins_control") == 0:HTML_Logger.Show_HTML_Report()

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
    AEB_EgoTurnLeft_TargetCrossing_Pedestrian__AEB_CPTA_I_10(5,20,50)
