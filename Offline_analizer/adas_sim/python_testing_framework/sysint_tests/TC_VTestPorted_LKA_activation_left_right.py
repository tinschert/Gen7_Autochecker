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




def LKA_activation_left_right(config, ego_speed, tgt_speed):
  capl.Testcase_Start(__file__, "CANoePy Testcase",
                      filename=HTML_Logger.generate_report_name())  # create the HTML report

  #capl.ReportTestStepPass("Test case:Start")
  tf.Precondition_CM_TestPrep(config, 8, 0)
  tf.PreConditions_LKA()
  capl.SetSignal("","hil_drv/target_velocity",ego_speed)
  capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # set target object to tgt_speed
  capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed-1,ego_speed+1,25)
  tf.Activate_LKA_ELK_Cus()
  capl.SetSignal("","hil_drv/steering_wheel_angle_req", -5)
  tf.Check_LKA_Status_Cus(config)

  tf.PostConditions_LKA()
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
    LKA_activation_left_right(5,70,30)