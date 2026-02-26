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



global i

def ACC_target_overtaking_ego_10m_cut(config, ego_speed, tgt_speed):
    capl.Testcase_Start(__file__, "CANoePy Testcase",
                        filename=HTML_Logger.generate_report_name())  # create the HTML report

    #capl.ReportTestStepPass("Test case:Start")
    tf.Precondition_CM_TestPrep(config, 2, 0)
    tf.Set_Drv_gear(3)  # set Drive gear
    capl.SetSignal("","hil_drv/target_velocity", ego_speed)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # set target object to tgt_speed
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.ctrl_status_lane_lat_offset", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.SetSignal("","Classe_Obj_Sim/obj_ctrl.par_lane_offset_timeconstraint", 1) # set to 1 sec the time to change the lane
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed-1,ego_speed+1,25)
    capl.WaitForSignalInRange("","CarMaker/RB/TrafficObj/object0/dtx", -10,-1,30)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [3.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.WaitForSignalInRange("","CarMaker/RB/TrafficObj/object0/dtx", 10,20,30)
    capl.SetSignal_Array("","Classe_Obj_Sim/obj_ctrl.obj_target_lane_lat_offset", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    tf.Activate_ACC_Cus()
    tf.Check_ACC_Status_Cus()
    tf.ShortPress_ACC_SetPlus_Cus()

    tf.PostConditions_ACC()
    tf.PostConditionsCM()

    tf.Check_And_Acknowledge_HIL_Abort_Messages()

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
    ACC_target_overtaking_ego_10m_cut(5,40,60)