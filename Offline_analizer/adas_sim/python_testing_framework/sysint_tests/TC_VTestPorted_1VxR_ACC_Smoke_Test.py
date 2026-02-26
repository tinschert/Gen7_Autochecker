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
import Test_Functions_1VxR_XIL_API as tf




def ACC_Smoke_Test(config, ego_speed, tgt_speed):
    capl.Testcase_Start(__file__, "CANoePy Testcase",
                      filename=HTML_Logger.generate_report_name())  # create the HTML report
    #capl.ReportTestStepPass("Test case:Start")

    tf.Precondition_CM_TestPrep(config,1,0)
    tf.PreConditions_ACC()
    tf.Set_Ego_Vehicle(ego_speed)
    tf.Activate_ACC_Cus()
    tf.Check_ACC_Status_Cus()

    for i in range(2):  # set ACC Speed to 50kph
        tf.ShortPress_ACC_SetPlus_Cus()

    # Check following Mode ACC set to 50 kph and obj_target speed 40kph
    capl.TestWaitForTimeout(1000)
    result1=capl.WaitForSignalInRange("","hil_hvm/velocity_x", 39, 41, 25)  # check 40kph
    tf.EvaluateResult(result1)
    capl.TestWaitForTimeout(2000)  # wait for second Check
    result2=capl.WaitForSignalInRange("","hil_hvm/velocity_x", 44, 54, 25)  # check 50kph
    tf.EvaluateResult(result2)
    capl.TestWaitForTimeout(500)

    # Check Stop and go
    result3=capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0.00, 1.00, 35)  # check 0kph
    tf.EvaluateResult(result3)
    capl.TestWaitForTimeout(500)

    # check cruise control 50kph
    result4=capl.WaitForSignalInRange("","hil_hvm/velocity_x", 39.00, 41.00, 25)  # check 50kph
    tf.EvaluateResult(result4)
    capl.TestWaitForTimeout(2000)
    result5=capl.WaitForSignalInRange("","hil_hvm/velocity_x", 49.00, 51.00, 25)  # check 50kph
    tf.EvaluateResult(result5)
    capl.TestWaitForTimeout(100)

    capl.ReportTestStepPass("ACC Testcase are done")

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
    ACC_Smoke_Test(2,30,0)