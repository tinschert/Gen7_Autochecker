#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an test function library

import sys

sys.path.append(r"..\..\..\Platform\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Platform\\Python_Testing_Framework\ReportGen")
#sys.path.append(r"..\..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")

import CAPL_Wrapper_Functions_XIL_API as capl
import time
import os
import HTML_Logger
##################################################################################################################################################################################################################
# TEST FUNCTIONS using the CAPL wrapper functions
##################################################################################################################################################################################################################
def Set_Drv_gear(gear):
    # 0-park,1-reverse,2-neutral, 3-drive
    temp_val = int(gear)
    capl.SetSignal("hil_drv","gear_req",temp_val)
    capl.TestWaitForTimeout(500)

def Set_Ego_Vehicle_Velocity(ego_speed):
    temp_val = float(ego_speed)
    capl.SetSignal("hil_drv","target_velocity",temp_val)
    #capl.WaitForSignalInRange("hil_hvm","velocity_x", temp_val-1,temp_val+1,25)
    capl.TestWaitForTimeout(500)

def Activate_ACC_Cus():
    #val1 = capl.GetSignal("hil_drv","hmi_btn_adas_acc::pressed")
    #2 - pressed
    #1 - not pressed
    capl.SetSignal("hil_drv", "hmi_btn_adas_acc",2)
    capl.TestWaitForTimeout(500);
    #val2=capl.GetSignal("hil_drv::hmi_btn_adas_acc","not_pressed")
    capl.SetSignal("hil_drv", "hmi_btn_adas_acc",0)
    capl.TestWaitForTimeout(500);

def Check_ACC_Status_Cus():
    #1 - active
    #0 - not active
    val1 = capl.GetSignal("hil_adas","hmi_display_adas_acc_status")
    #val2 = capl.GetSignal("hil_adas::hmi_display_adas_acc_status","active")
    if (val1 == 3): #Check Status ACC
        capl.ReportTestStepPass("ACC is active");
    else:
        capl.ReportTestStepFail("ACC is not active");

    capl.TestWaitForTimeout(200);

def ShortPress_ACC_SetPlus_Cus():
    #5 - plus button pressed
    #4 - minus button pressed
    #0 - not pressed
    #val1=capl.GetSignal("hil_drv::hmi_btn_cc::set_plus","")
    capl.SetSignal("hil_drv","hmi_btn_cc",5)
    capl.TestWaitForTimeout(1000)
    #val2 = capl.GetSignal("hil_drv::hmi_btn_cc::not_pressed", "")
    capl.SetSignal("hil_drv","hmi_btn_cc",0)
    capl.TestWaitForTimeout(300)

def Check_API_Connection():
    counter = 0
    for i in range(50):
        value_1 = capl.GetSignal("", "hil_ctrl::global_counter", True)
        time.sleep(0.002)
        value_2 = capl.GetSignal("", "hil_ctrl::global_counter",True)
        time.sleep(0.002)
        if (value_1==value_2):
            capl.ReportTestStepFail("API Communication Check : FAILED")
            return("FAILED")
        else:
            capl.ReportTestStepPass("API Communication Check : PASSED")
            return ("PASSED")


# Variables
msg_buffer = ""
WaitResult = 0
negative_test_flag = 0
Graphic_Window_Count = 24
GraphicWindow = [
    "",  # 0 Off
    "Test_basic_DPCdelta1",  # 1 DPCdelta1
    "",  # 2 Phi1V
    "Test_basic_RPCalpha2",  # 3 RPCAlpha2
    "Test_basic_DPCdelta1",  # 4 DPCdelta1_1V1D
    "",  # 5 not used
    "Test_basic_DPCdelta5",  # 6 DPCdelta5
    "Test_basic_DPCdelta5",  # 7 DPCdelta5_1V1D
    "",  # 8 not used
    "",  # 9 not used
    "",  # 10 TestDCP_1V1D4N
    "Test_basic_RPCalpha2",  # 11 RPCAlpha2_1R1V
    "",  # 12 not used
    "",  # 13 not used
    "",  # 14 not used
    "",  # 15 not used
    "",  # 16 not used
    "",  # 17 not used
    "",  # 18 not used
    "",  # 19 not used
    "",  # 20 not used
    "Test_basic_DPCdelta1",  # 21 Replay_DPCdelta1
    "Test_basic_DPCdelta5",  # 22 Replay_DPCdelta5
    "Test_basic_RPCalpha2"  # 23 Replay_RPCalpha2
]

def addCANoeWindowCapture(Variant, title=""):
    capl.TestReportAddWindowCapture(GraphicWindow[Variant], "", title)


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
def Precondition_CM_TestPrep(config, scenario, vehicle_code):
    cf_testPreparation()
    capl.SetSignal("","hil_ctrl/vehicle", vehicle_code) # set the vehicle variant
    SetScenario(scenario)
    PreConditionsCM(config)
    capl.SetSignal("Customer_specific", "load_scenario", 1)  # press the LOAD SCENARIO button
    CM_start()
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 70)

def cf_testPreparation():
    HTML_Logger.TestReportHeader("Sample CANoePy test case")
    HTML_Logger.TestReportHeader("Company : Robert Bosch GmbH")
    HTML_Logger.TestReportHeader("Tester name : Rafael H")
    HTML_Logger.TestReportHeader("CANoe : Version 18SP3")
    HTML_Logger.TestReportHeader("SUT : AEB test")

def SetScenario(scenario):
    scenarios = {
        1: "ACC_Smoke_Test",
        2: "ACC_target_overtaking_ego_10m_cut",
        3: "AEB_EgoLong_TargetLong_Car__AEB_CCRs",
        4: "AEB_EgoLong_PedestrianCrossing_left_to_right",
        5: "AEB_EgoLong_TargetOncoming_same_lane__AEB_CCFhos",
        6: "AEB_EgoTurnLeft_TargetLong_Car__AEB_CCFTap",
        7: "AES_EgoLong_TargetLong_Car__AEB_CCRs",
        8: "LKA_activation_left_right",
        9: "LCCM_activation_left_right",
        10: "ALC_activation",
        11: "HF_EST_activation",
        12: "ELKA_oncoming_left",
        13: "ELKA_RE_activation_left_right"
    }
    capl.SetSignal("","Customer_specific/cm_scenario", scenarios.get(scenario, ""))

def PreConditionsCM(config):
    global msg_buffer, WaitResult

    capl.ReportTestStepPass("Pre-cond CM Start")

    capl.SetSignal("hil_ctrl", "configuration_od", config)
    time.sleep(5)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    time.sleep(1)
    capl.AwaitValueMatch("hil_ctrl", "init_cm_done", 1, 180)  # wait green LED
    time.sleep(6)

    if capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_lksState") == 1:
        capl.ReportTestStepPass("Pre-cond CM:Reset ALC")
        #0 - not pressed
        #1 - pressed Off
        #2 - pressed On
        capl.SetSignal("","hil_drv/hmi_btn_adas_lks", 1)
        time.sleep(1)
        capl.SetSignal("","hil_drv/hmi_btn_adas_lks", 0)
        time.sleep(0.5)

def PreconditionsCM_noScenario(config):
    capl.ReportTestStepPass("Pre-cond CM:Start")

    capl.SetSignal("","hil_ctrl/configuration_od", config)
    time.sleep(5)
    capl.SetSignal("","hil_ctrl/hil_mode", 4)
    time.sleep(1)
    if capl.GetSignal("","hil_ctrl/init_cm_done") == 0:
        capl.AwaitValueMatch("","hil_ctrl/init_cm_done", 1, 180)
    else:
        capl.ReportTestStepPass("Pre-cond CM:Carmaker already intialized")
    time.sleep(1)

def CM_start():
    capl.ReportTestStepPass("Pre-cond CM 3:Run")
    if capl.GetSignal("","hil_ctrl/cm_ready_to_start") == 0:
        capl.AwaitValueMatch("","hil_ctrl/cm_ready_to_start", 1,58)
    else:
        HTML_Logger.ReportGreenMessage("Carmaker was previously ready")
    time.sleep(0.5)
    if capl.GetSignal("","hil_ctrl/jenkins_control") == 1:
        capl.SetSignal("","hil_ctrl/trace_logging_start_mf4", 1)
        time.sleep(1)
    capl.SetSignal("","hil_ctrl/scenario_start", 1)
    time.sleep(1)
    if capl.GetSignal("","hil_ctrl/configuration_od") in [3, 11]:
        capl.SetSignal("","XCP/RadarFC_Obj/_g_PL_AD_fw_Radar_1R1V_rpc_XilObjBypassingRunnable_XilObjBypassingRunnable/_m_pad_hilActive_par", 1)
        #syspar["RPCalpha2"]["pad_hilActive_par"] = 1

def PostConditionsCM():
    global msg_buffer, WaitResult
    capl.ReportTestStepPass("Post-cond CM:Start")
    #this code for putting trace start to OFF is moved to Testcase_End function (CAPL Wrapper library)
    #if capl.GetSignal("","hil_ctrl/jenkins_control") == 1:
    #   capl.SetSignal("","hil_ctrl/trace_logging_start_mf4", 0)
    #    time.sleep(1)

    if (capl.GetSignal("","hil_ctrl/abort_message") == "no abort") or negative_test_flag == 1:
        capl.ReportTestStepPass("PASSED")
    else:
        capl.ReportTestStepFail("FAILED")
        capl.ReportTestStepFail("Error in ADAS HIL. See abort Message and write window. To continue clear the abort message.")
    time.sleep(0.5)
    capl.SetSignal("","hil_ctrl/ack_abort_msg_btn", 1)
    time.sleep(0.5)
    capl.SetSignal("","hil_ctrl/ack_abort_msg_btn", 0)

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test
    time.sleep(2)
    WaitResult = capl.AwaitValueMatch("","hil_ctrl/init_done", 1, 30)
    if WaitResult == 0:
        capl.ReportTestStepFail("Post-cond CM:Init rbs FAILED")
    else:
        capl.ReportTestStepPass("Post-cond CM:Init rbs done")
    time.sleep(4)
    capl.ReportTestStepPass("Passed")

    time.sleep(5.5) # wait for the CANoe trace file to be closed by CANoe

    #Rename_CANoe_Trace()

def Rename_CANoe_Trace():
    print(os.path.abspath(os.getcwd()))
    try:
        last_mf4_file = HTML_Logger.find_newest_file_in_folder(r"CustomerPrj\Traces")
        last_mf4_file_extension_type = last_mf4_file.split('.')[1]
        last_HTML_report_file = HTML_Logger.find_newest_file_in_folder(r"Reports")
        #print("last_mf4_file = ", last_mf4_file)
        #print("last_HTML_report_file = ", last_HTML_report_file)
        #print("last_mf4_file_extension_type =", last_mf4_file_extension_type)
        os.rename("CustomerPrj\\Traces\\"+last_mf4_file, "CustomerPrj\\Traces\\"+last_HTML_report_file.replace(".html","")+"."+last_mf4_file_extension_type)
        capl.ReportTestStepPass("CANoe trace renamed successfully.")
    except:
        HTML_Logger.ReportRedMessage("CANoe trace (MF4/BLF) can not be renamed ! ! ! ")
        capl.ReportTestStepFail("CANoe trace NOT renamed.")

def PreCondition_Init_Classe():
    capl.ReportTestStepPass("Pre-cond Init Classe : Start")

    hil_ctrl["hil_mode"] = "Classe"
    time.sleep(0.5)

    Classe_Obj_Sim["obj_delete_btn"] = 1
    time.sleep(0.5)
    Classe_Obj_Sim["obj_delete_btn"] = 0

    capl.ReportTestStepPass("Passed")

def PostCondition_DeInit_Classe():
    capl.ReportTestStepPass("Post-cond DeInit Classe : Start")

    Classe_Obj_Sim["obj_delete_btn"] = 1
    time.sleep(0.5)
    Classe_Obj_Sim["obj_delete_btn"] = 0

    time.sleep(0.5)

    hil_ctrl["init_rbs"] = 1
    time.sleep(0.5)
    hil_ctrl["init_rbs"] = 0
    capl.AwaitValueMatch("","hil_ctrl/init_done", 1, 20)

    capl.ReportTestStepPass("Passed")

def PostCondition_XCP_Disconnect():
    if capl.GetSignal("","hil_ctrl/configuration_od") == "RPCAlpha2":
        xcpDisconnect("RadarFC_Obj")
        time.sleep(1)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == "DPCdelta1":
        xcpDisconnect("DPCdelta1")
        time.sleep(1)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == "DPCdelta5":
        xcpDisconnect("DPCdelta5")
        time.sleep(1)

def Init_DPC_Config():
    PreCondition_Init_Classe()

    capl.SetSignal("","hil_ctrl/configuration_od", "DPCdelta1")
    time.sleep(1)

    PostCondition_XCP_Disconnect()

def Init_Ego_vehicle():
    #global ESP_SysSts_EPB
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    time.sleep(0.5)
    capl.SetSignal("","hil_drv/gear_req", 3)
    time.sleep(0.5)
    #3->cranking
    #2->engine running
    #1->ignition on
    #0->off
    #4->programming
    capl.SetSignal("","hil_hvm/power_mode", 2) #engine running
    time.sleep(0.5)
    capl.ReportTestStepPass("Passed")

def PreCondition_Clear_Read_DTC():
    time.sleep(10)
    sysvar["DIAG_ADAS"]["SESSION"]["DEF_SESS"] = 1
    time.sleep(0.2)
    sysvar["DIAG_ADAS"]["DTC_INFO"]["DTC_Clear"] = 1
    time.sleep(0.5)
    testWaitForSignalMatch(sysvar["DIAG_ADAS"]["sysDataReceived"], 54, 10000)
    sysvar["DIAG_ADAS"]["DTC_INFO"]["DTC_Read"] = 1
    time.sleep(2)
    capl.ReportTestStepPass("Passed")

def PreCondition_Clear_Read_DTC_Video():
    time.sleep(10)
    sysvar["DIAG_FVIDEO"]["SESSION"]["DEF_SESS"] = 1
    time.sleep(0.2)
    sysvar["DIAG_FVIDEO"]["DTC_INFO"]["DTC_Clear"] = 1
    time.sleep(0.5)
    testWaitForSignalMatch(sysvar["DIAG_FVIDEO"]["sysDataReceived"], 54, 10000)
    sysvar["DIAG_FVIDEO"]["DTC_INFO"]["DTC_Read"] = 1
    time.sleep(2)
    capl.ReportTestStepPass("Passed")

def Power_SW_Reset():
    #0->off
    #2->real
    #1->simulated

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
    if capl.GetSignal("","hil_ctrl/configuration_od") == 1:     #"DPCdelta1":
        capl.SetSignal("","hil_ctrl/adas_1_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/adas_1_sim", 2)
        time.sleep(5)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == 6:     #"DPCdelta5":
        capl.SetSignal("","hil_ctrl/adas_2_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/adas_2_sim", 2)
        time.sleep(5)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == 3:     #"RPCAlpha2":
        capl.SetSignal("","hil_ctrl/adas_1_sim", 0)
        time.sleep(0.1)
        capl.SetSignal("","hil_ctrl/radar_fc_obj_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/radar_fc_obj_sim", 2)
        time.sleep(5)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == 4:     #"DPCdelta1_1V1D":
        capl.SetSignal("","hil_ctrl/adas_1_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/adas_1_sim", 2)
        time.sleep(0.1)
        capl.SetSignal("","hil_ctrl/fvideo_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/fvideo_sim", 2)
        time.sleep(5)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == 7:     #"DPCdelta5_1V1D":
        capl.SetSignal("","hil_ctrl/adas_2_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/adas_2_sim", 2)
        time.sleep(0.1)
        capl.SetSignal("","hil_ctrl/fvideo_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/fvideo_sim", 2)
        time.sleep(5)
    elif capl.GetSignal("","hil_ctrl/configuration_od") == 2:     #"Phi1V":
        capl.SetSignal("","hil_ctrl/fvideo_sim", 0)
        time.sleep(1)
        capl.SetSignal("","hil_ctrl/fvideo_sim", 2)
        time.sleep(5)
    capl.ReportTestStepPass("Passed")

def SensorDataTransferProtocolSnapshot():
    TestReportAddWindowCapture("Sensor_data_protocol", "Sensor_protocol_window", "Screenshot of Sensor Data Protocol window")




def Set_Indicate_Left():
    #0->not active
    #1->left turn
    #2->right turn
    capl.SetSignal("","hil_drv/indicator_light", 1) #hil_drv.indicator_light.leftturn  # left indicator
    capl.TestWaitForTimeout(2000)

def Set_Indicate_Right():
    #0->not active
    #1->left turn
    #2->right turn
    capl.SetSignal("","hil_drv/indicator_light", 2)
    capl.TestWaitForTimeout(2000)

def Set_Indicator_Inactive():
    capl.SetSignal("","hil_drv/indicator_light", 0) #hil_drv.indicator_light.not_active)
    capl.TestWaitForTimeout(2000)

def Set_Ego_Vehicle(ego_speed):
    capl.SetSignal("","hil_drv/target_velocity", ego_speed)
    #capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed - 1, ego_speed + 1, 25)
    capl.TestWaitForTimeout(500)

def Set_HandsOn_Cus():
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/GW_HSC8_FrP16/HODDetnSts_h8HSC8", 2)   #HODDetnSts_h8HSC8 = 2  # valid contact detected
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/GW_HSC8_FrP16/HODTchZone1Sts_h8HSC8",1)    #HODTchZone1Sts_h8HSC8 = 1  # hand detected
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DrvrDstcnStsHSC4", 1)   #DrvrDstcnStsHSC4 = 1  # no distraction
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DrvrGazeRgnHSC4", 1)    #DrvrGazeRgnHSC4 = 1  # driver side of windscreen
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DMSStsHSC4", 2)    #DMSStsHSC4 = 2  # active
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DrvrPrstHSC4", 2)    #DrvrPrstHSC4 = 2  # driver presence

def Set_HandsOff_Cus():
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/GW_HSC8_FrP16/HODDetnSts_h8HSC8", 0)    #HODDetnSts_h8HSC8 = 0  # valid contact detected
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/GW_HSC8_FrP16/HODTchZone1Sts_h8HSC8", 0)    #HODTchZone1Sts_h8HSC8 = 0  # hand detected
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/GW_HSC8_FrP16/HODTchZone1Val_h8HSC8", 0)    #HODTchZone1Val_h8HSC8 = 0  #
    capl.TestWaitForTimeout(2000)

def PreConditionsAEB():
    capl.ReportTestStepPass("Pre-cond AEB:Start")

    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    Set_Drv_gear(3)  # set Drive gear
    if capl.GetSignal("","hil_ctrl/configuration_od") in [3, 11]:
        capl.ReportTestStepPass("Pre-cond AEB : sensor configuration is Radar based")
        #syspar.RPCalpha2.aebEncodingBypass = 1
        #syspar.RPCalpha2.aebHMISwitchBypass = 1
        #syspar.RPCalpha2.fcwHMISwitchBypass = 1
        capl.SetSignal("","XCP/DPCdelta5/FctParam/AebCommon/aebEncodingBypass",1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebEncodingBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.AEB_m_update = 1
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)

        if capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState") in [1, 2]:  # Value 1 is suppressed and 2 is available
            capl.ReportTestStepPass("Pre-cond AEB:AEB state available or suppressed")
            capl.ReportTestStepPass("Pre-cond AEB:Expected aebTiplLongFullBrakeState = 1 or 2, but obtained = {syspar.RPCalpha2.aebTiplLongFullBrakeState}")
        else:
            capl.ReportTestStepFail("Pre-cond AEB:AEB state unavailable")
            capl.ReportTestStepFail("Pre-cond AEB:Expected aebTiplLongFullBrakeState = 1 or 2, but obtained = {syspar.RPCalpha2.aebTiplLongFullBrakeState}")
    else:
        capl.ReportTestStepPass("Pre-cond AEB : sensor configuration is other than Radar based")
        #syspar.DPCdelta1.aebEncodingBypass = 1
        #capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.aebHMISwitchBypass = 1
        #capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.fcwHMISwitchBypass = 1
        #capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.AEB_m_update = 1
        capl.SetSignal("","XCP/DPCdelta5/FctParam/AebCommon/aebEncodingBypass",1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebEncodingBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.AEB_m_update = 1
        capl.SetSignal("", "XCP/DPCdelta5/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)
        if capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState") in [1, 2]:  # Value 1 is suppressed and 2 is available
            capl.ReportTestStepPass("Pre-cond AEB : AEB state available or suppressed")
            capl.ReportTestStepPass("Pre-cond AEB : Expected aebTiplLongFullBrakeState = 1 or 2, but obtained different")
        else:
            capl.ReportTestStepFail("Pre-cond AEB : AEB state unavailable")
            capl.ReportTestStepFail("Pre-cond AEB : Expected aebTiplLongFullBrakeState = 1 or 2, but obtained different")

def PostConditionsAEB():
    capl.ReportTestStepPass("Post-cond AEB : Start")
    if capl.GetSignal("","hil_drv/DIL_mode") == 3: # 3 -> steeringwheel_g29
        capl.SetSignal("","hil_drv/target_velocity", 0)
        capl.WaitForSignalInRange(sysvar.hil_hvm.velocity_x, 0, 0.5, 25)
    else:
        capl.TestWaitForTimeout(10000)

def Set_Ego_Vehicle_AEB(ego_speed, tgt_speed):
    capl.SetSignal("","hil_drv/target_velocity", ego_speed)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [tgt_speed, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])  # set target object to tgt_speed
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_velocity", [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", ego_speed - 1, ego_speed + 1, 25)

def Check_AEB_Turn_Status_Cus(config):
    if config in [1, 4]:  # Delta1 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplTurnFullBrakeState", 3, 30)
        capl.TestWaitForTimeout(200)
        state = capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplTurnFullBrakeState")    #syspar.DPCdelta1.aebTiplTurnFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case:AEB Turn remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case:AEB Turn remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case:AEB Turn was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2:
                capl.ReportTestStepPass("Test case:AEB Turn activated")
            elif APL.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
                capl.ReportTestStepFail("Test case:AEB Turn was active but no brake request sent")
        capl.TestWaitForTimeout(2000)
    elif config in [6, 7]:  # Delta5 Variants
        pass
    elif config in [3, 11]:  # RPCalpha2 Variants
        capl.AwaitValueMatch("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplTurnFullBrakeState", 3, 30)
        capl.TestWaitForTimeout(200)
        state = syspar.RPCalpha2.aebTiplTurnFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB Turn remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB Turn remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB Turn was available but not active")
        elif state == 3:
            if sysvar.hil_adas.acceleration_x_type_req == 2:
                capl.ReportTestStepPass("Test case : AEB Turn activated")
            elif sysvar.hil_adas.acceleration_x_type_req == 0:
                capl.ReportTestStepFail("Test case : AEB Turn was active but no brake request sent")
        capl.TestWaitForTimeout(2000)

def Check_AEB_TIPL_Long_Status_Cus(config):
    if config in [1, 4]:  # Delta1 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState", 3, 30)   #capl.AwaitValueMatch("","syspar.DPCdelta1.aebTiplLongFullBrakeState, 3, 30000)
        capl.TestWaitForTimeout(200)
        state = capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState")    #syspar.DPCdelta1.aebTiplTurnFullBrakeState #state = syspar.DPCdelta1.aebTiplLongFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2:
                capl.ReportTestStepPass("Test case : AEB activated")
            elif capl.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
                capl.ReportTestStepFail("Test case : AEB was active but no brake request sent")
        capl.TestWaitForTimeout(2000)
    elif config in [6, 7]:  # Delta5 Variants
        pass
    elif config in [3, 11]:  # RPCalpha2 Variants
        capl.AwaitValueMatch("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState", 3, 30)   #capl.AwaitValueMatch("","syspar.DPCdelta1.aebTiplLongFullBrakeState, 3, 30000)
        capl.TestWaitForTimeout(200)
        state = capl.GetSignal("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState")    #syspar.DPCdelta1.aebTiplTurnFullBrakeState #state = syspar.DPCdelta1.aebTiplLongFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2:
                capl.ReportTestStepPass("Test case : AEB activated")
            elif capl.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
                capl.ReportTestStepFail("Test case : AEB was active but no brake request sent")
        capl.TestWaitForTimeout(2000)

def Check_AEB_TIPL_Long_Oncoming_Status_Cus(config):
    #aebTiplLongOncomingFullBrakeState
    if config in [1, 4]:  # Delta1 Variants
        capl.AwaitValueMatch("","hil_adas/acceleration_x_type_req", 2, 40)
        capl.AwaitValueMatch("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongOncomingFullBrakeState", 3, 5)
        state = capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongOncomingFullBrakeState")    #state = syspar.DPCdelta1.aebTiplLongOncomingFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB Oncoming remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB Oncoming remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB Oncoming was available but not active")
        elif state == 3:
            capl.ReportTestStepPass("Test case : AEB Oncoming activated")
        capl.TestWaitForTimeout(2000)
    elif config in [6, 7]:  # Delta5 Variants
        pass
    elif config in [3, 11]:  # RPCalpha2 Variants
        capl.AwaitValueMatch("","hil_adas/acceleration_x_type_req", 2, 40)
        capl.AwaitValueMatch("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongOncomingFullBrakeState", 3, 5)
        state = capl.GetSignal("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongOncomingFullBrakeState")    #state = syspar.DPCdelta1.aebTiplLongOncomingFullBrakeState
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB Oncoming remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB Oncoming remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB Oncoming was available but not active")
        elif state == 3:
            capl.ReportTestStepPass("Test case : AEB Oncoming activated")
        capl.TestWaitForTimeout(2000)

def Check_AEB_Cfm_FullBrake_Status_Cus(config):
    #aebCfmFullBrakeState
    if config in [1, 4]:  # Delta1 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebCfmFullBrakeState", 3, 30)
        capl.TestWaitForTimeout(200)
        state = state = capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebCfmFullBrakeState")
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB Cfm remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB Cfm remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB Cfm was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2:
                capl.ReportTestStepPass("Test case : AEB Cfm activated")
            elif capl.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
                capl.ReportTestStepFail("Test case : AEB Cfm was active but no brake request sent")
        capl.TestWaitForTimeout(2000)
    elif config in [6, 7]:  # Delta5 Variants
        pass
    elif config in [3, 11]:  # RPCalpha2 Variants
        capl.AwaitValueMatch("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebCfmFullBrakeState", 3, 30000)
        capl.TestWaitForTimeout(200)
        state = capl.GetSignal("","XCP/RPCalpha2/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebCfmFullBrakeState")
        if state == 0:
            capl.ReportTestStepFail("Test case : AEB Cfm remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AEB Cfm remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AEB Cfm was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2:
                capl.ReportTestStepPass("Test case : AEB Cfm activated")
            elif capl.GetSignal("","hil_adas/acceleration_x_type_req") == 0:
                capl.ReportTestStepFail("Test case : AEB Cfm was active but no brake request sent")
        capl.TestWaitForTimeout(2000)

def Check_AES_Status_Cus(config):
    if config in [1, 4]:  # Delta1 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongAesState", 3, 30)
        capl.TestWaitForTimeout(200)
        state = capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongAesState")
        if state == 0:
            capl.ReportTestStepFail("Test case : AES remained in 'invalid' state")
        elif state == 1:
            capl.ReportTestStepFail("Test case : AES remained in 'suppressed' state")
        elif state == 2:
            capl.ReportTestStepFail("Test case : AES was available but not active")
        elif state == 3:
            if capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2 and capl.GetSignal("","hil_adas/latl_req_type") == 1:
                capl.ReportTestStepPass("Test case:AES activated")
            elif capl.GetSignal("","hil_adas/acceleration_x_type_req") == 2 and capl.GetSignal("","hil_adas/latl_req_type") == 0:
                capl.ReportTestStepFail("Test case : AES was active with brake request, but no steering Request received")
            else:
                capl.ReportTestStepFail("Test case : AES didn't work in full chain")
        capl.TestWaitForTimeout(2000)
    elif config in [6, 7]:  # Delta5 Variants
        pass
    elif config in [3, 11]:  # RPCalpha2 Variants
        pass

def PreConditionAEB_Activation():
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
    capl.ReportTestStepPass("Pre-cond AEB activation:Start")
    if capl.GetSignal("","hil_ctrl/configuration_od") == 3: #RPCAlpha2:
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.aebEncodingBypass = 1
        capl.SetSignal("","XCP/RPCalpha2/FctParam/AebCommon/aebEncodingBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.aebHMISwitchBypass = 1
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.fcwHMISwitchBypass = 1
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.RPCalpha2.AEB_m_update = 1
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)
        capl.ReportTestStepPass("Passed")
    elif capl.GetSignal("","hil_ctrl/configuration_od") in [1,4,5]:   # DPCdelta1:
        capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.aebEncodingBypass = 1
        capl.SetSignal("","XCP/DPCdelta1/FctParam/AebCommon/aebEncodingBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.aebHMISwitchBypass = 1
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.fcwHMISwitchBypass = 1
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/fcwHMISwitchBypass", 1)
        capl.TestWaitForTimeout(500)
        #syspar.DPCdelta1.AEB_m_update = 1
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)
        capl.ReportTestStepPass("Passed")

def PostConditionAEB_Deactivation():
    capl.ReportTestStepPass("Post-cond AEB deactivation : Start")
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
    capl.ReportTestStepPass("Pre-cond AEB activation:Start")
    if capl.GetSignal("", "hil_ctrl/configuration_od") == 3:  # RPCAlpha2:
        capl.TestWaitForTimeout(500)
        # syspar.RPCalpha2.aebEncodingBypass = 0
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/aebEncodingBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.RPCalpha2.aebHMISwitchBypass = 0
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/aebHMISwitchBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.RPCalpha2.fcwHMISwitchBypass = 0
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/fcwHMISwitchBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.RPCalpha2.AEB_m_update = 1
        capl.SetSignal("", "XCP/RPCalpha2/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)
        capl.ReportTestStepPass("Passed")
    elif capl.GetSignal("", "hil_ctrl/configuration_od") in [1, 4, 5]:  # DPCdelta1:
        capl.TestWaitForTimeout(500)
        # syspar.DPCdelta1.aebEncodingBypass = 0
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebEncodingBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.DPCdelta1.aebHMISwitchBypass = 0
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebHMISwitchBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.DPCdelta1.fcwHMISwitchBypass = 0
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/fcwHMISwitchBypass", 0)
        capl.TestWaitForTimeout(500)
        # syspar.DPCdelta1.AEB_m_update = 1
        capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/_m_trigger/_m_update", 1)
        capl.TestWaitForTimeout(500)
        capl.ReportTestStepPass("Passed")

        #if capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState") == 1:  # Value 1 is suppressed as per Enum table
        #    capl.ReportTestStepPass("PASSED")  # capl.ReportTestStepPass("Pre-cond AEB", "AEB state suppressed")
        #else:
        #    capl.ReportTestStepFail("FAILED")  # capl.ReportTestStepFail("Pre-cond AEB", "AEB state unavailable")

# ACC Smoke Test
# *********************************************************************************************************************************

def PreConditions_ACC():
    capl.ReportTestStepPass("Pre-cond ACC : Start")
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    Set_Drv_gear(3)  # set Drive gear

    capl.TestWaitForTimeout(500)

    if capl.GetSignal("","hil_adas/hmi_display_adas_acc_status") == 1:  #1->"passive":3->active
        capl.ReportTestStepPass("Pre-cond ACC : ACC ready ")
    else:
        capl.ReportTestStepFail("Pre-cond ACC : ACC not ready")

def PostConditions_ACC():
    capl.ReportTestStepPass("Post-cond ACC : Start")
    if capl.GetSignal("","hil_drv/DIL_mode") == 3: # 3 -> steeringwheel_g29
        hil_drv_target_velocity = 0
        capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0, 0.5, 25)
    else:
        capl.TestWaitForTimeout(10000)

def Activate_ACC_Cus():
    #0->not pressed
    #1->pressed off
    #2->pressed on
    capl.SetSignal("","hil_drv/hmi_btn_adas_acc", 2)    #"pressed_on")  # Set ACC active
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","hil_drv/hmi_btn_adas_acc", 0)    #hil_drv_hmi_btn_adas_acc = "not_pressed"
    capl.TestWaitForTimeout(500)

def Check_ACC_Status_Cus():
    if capl.GetSignal("","hil_adas/hmi_display_adas_acc_status") == 3:  #1->"passive":3->active
        capl.ReportTestStepPass("PASSED")
    else:
        capl.ReportTestStepFail("FAILED")
    capl.TestWaitForTimeout(200)

def ShortPress_ACC_SetPlus_Cus():
    # 0->not pressed
    # 1->
    # 2->
    # 3->
    # 4-> set minus
    # 5-> set plus
    capl.SetSignal("","hil_drv/hmi_btn_cc", 5)  # set ACC +10 kph
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("","hil_drv/hmi_btn_cc", 0)
    capl.TestWaitForTimeout(300)

def ShortPress_ACC_SetMinus_Cus():
    # 0->not pressed
    # 1->
    # 2->
    # 3->
    # 4-> set minus
    # 5-> set plus
    capl.SetSignal("","hil_drv/hmi_btn_cc", 4)  # set ACC -10 kph
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("","hil_drv/hmi_btn_cc", 0)
    capl.TestWaitForTimeout(300)

# LKA Smoke Test
# *********************************************************************************************************************************

def PreConditions_LKA():
    capl.ReportTestStepPass("Pre-cond LKA : Start")
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    Set_Drv_gear(3)  # set Drive gear
    capl.TestWaitForTimeout(500)

def PostConditions_LKA():
    #0->not pressed, 1 - off, 2 - on
    capl.ReportTestStepPass("Post-cond LKA : Start")
    capl.SetSignal("","hil_drv/hmi_btn_adas_lka", 1)  # pressed button LKA to switch off
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","hil_drv/hmi_btn_adas_lka", 0)  # button released
    capl.TestWaitForTimeout(500)
    if capl.GetSignal("","hil_drv/DIL_mode") == 3: # 3 -> steeringwheel_g29
        hil_drv_target_velocity = 0
        capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0, 0.5, 25)
    else:
        capl.TestWaitForTimeout(500)

def Activate_LKA_ELK_Cus():
    # 0->not pressed, 1 - off, 2 - on
    capl.SetSignal("","hil_drv/hmi_btn_adas_lka", 2)  # pressed button LKA to switch ON
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","hil_drv/hmi_btn_adas_lka", 0)  # button released
    capl.TestWaitForTimeout(500)

def Check_ELKA_Oncoming_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_elkOcvState", 3, 30)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_elkOcvState")  #syspar_DPCdelta5_elkOcvState
        if switch == 0:
            capl.ReportTestStepFail("Test case:ELKA_Oncoming remained in 'off' state")
        elif switch == 1:
            capl.ReportTestStepFail("Test case:ELKA_Oncoming remained in 'passive' state")
        elif switch == 2:
            capl.ReportTestStepFail("Test case:ELKA_Oncoming was available but not active")
        elif switch == 3:
            capl.ReportTestStepPass("Test case:ELKA_Oncoming activated")
        elif switch == 4:
            capl.ReportTestStepFail("Test case:ELKA_Oncoming failure")
        elif switch == 5:
            capl.ReportTestStepFail("Test case:ELKA_Oncoming Blindness")
        capl.TestWaitForTimeout(10000)


def Check_ELKA_RoadEdge_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_elkReHState", 3, 30)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_elkReHState") #syspar_DPCdelta5_elkReHState
        if switch == 0:
            capl.ReportTestStepFail("Test case:ELKA_RoadEdge remained in 'off' state")
        elif switch == 1:
            capl.ReportTestStepFail("Test case:ELKA_RoadEdge remained in 'passive' state")
        elif switch == 2:
            capl.ReportTestStepFail("Test case:ELKA_RoadEdge was available but not active")
        elif switch == 3:
            capl.ReportTestStepPass("Test case:ELKA_RoadEdge activated")
        elif switch == 4:
            capl.ReportTestStepFail("Test case:ELKA_RoadEdge failure")
        elif switch == 5:
            capl.ReportTestStepFail("Test case:ELKA_RoadEdge Blindness")
        capl.TestWaitForTimeout(2000)

def Check_LKA_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_lkaState", 3, 30)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_lkaState")
        if switch == 0:
            capl.ReportTestStepFail("Test case:LKA remained in 'off' state")
        elif switch == 1:
            capl.ReportTestStepFail("Test case:LKA remained in 'passive' state")
        elif switch == 2:
            capl.ReportTestStepFail("Test case:LKA was available but not active")
        elif switch == 3:
            if capl.GetSignal("","hil_adas/latl_req_type") == 1 and capl.GetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/ADAS/ADAS_0x4BA_HMI/LKAStatus") == 6:
                capl.ReportTestStepPass("Test case:LKA activated to left")
            elif capl.GetSignal("","hil_adas/latl_req_type") == 1 and capl.GetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/ADAS/ADAS_0x4BA_HMI/LKAStatus") == 7:
                capl.ReportTestStepPass("Test case:LKA activated to right")
            else:
                capl.ReportTestStepPass("Test case:LKA activated - unknown side")
        elif switch == 4:
            capl.ReportTestStepFail("Test case:LKA failure")
        elif switch == 5:
            capl.ReportTestStepFail("Test case:LKA Blindness")
        capl.TestWaitForTimeout(2000)

def Check_LKS_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_lksState", 3, 30)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_lksState")
        if switch == 0:
            capl.ReportTestStepFail("Test case:LKS remained in 'off' state")
        elif switch == 1:
            capl.ReportTestStepFail("Test case:LKS remained in 'passive' state")
        elif switch == 2:
            capl.ReportTestStepFail("Test case:LKS was available but not active")
        elif switch == 3:
            capl.ReportTestStepPass("Test case:LKS active")
        elif switch == 4:
            capl.ReportTestStepFail("Test case:LKS failure")
        elif switch == 5:
            capl.ReportTestStepFail("Test case:LKS Blindness")
        capl.TestWaitForTimeout(2000)

# TSR Smoke Test
# *********************************************************************************************************************************

def PreConditionsTSR():
    capl.ReportTestStepPass("Pre-cond TSR:Start")
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    Set_Drv_gear(3)  # set Drive gear
    capl.TestWaitForTimeout(500)

def PostConditionsTSR():
    capl.ReportTestStepPass("Post-cond TSR:Start")
    capl.SetSignal("","hil_drv/target_velocity", 0)
    capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0, 0.5, 25)

# RCTA Smoke Test
# *********************************************************************************************************************************

def PreConditionsRCTA():
    capl.ReportTestStepPass("Pre-cond RCTA:Start")
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    #0-park,1-reverse,2-neutral, 3-drive
    capl.SetSignal("","hil_drv/gear_req",1) #"reverse"
    capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebEncodingBypass", 1)
    capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/aebHMISwitchBypass", 1)
    capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/fcwHMISwitchBypass", 1)
    capl.SetSignal("", "XCP/DPCdelta1/FctParam/AebCommon/_m_trigger/_m_update", 1)
    capl.TestWaitForTimeout(500)

    if capl.GetSignal("","XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState") in [1, 2]:  # Value 1 is suppressed and 2 is available
        capl.ReportTestStepPass("Pre-cond AEB:AEB state available or suppressed")
        capl.ReportTestStepPass("Pre-cond AEB:Expected aebTiplLongFullBrakeState = 1 or 2, but obtained = {XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState}")
    else:
        capl.ReportTestStepFail("Pre-cond AEB:AEB state unavailable")
        capl.ReportTestStepFail("Pre-cond AEB:Expected aebTiplLongFullBrakeState = 1 or 2, but obtained = {XCP/DPCdelta1/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_aebTiplLongFullBrakeState}")

def PostConditionsRCTA():
    capl.ReportTestStepPass("Post-cond RCTA:Start")
    if capl.GetSignal("","hil_drv/DIL_mode") == 3: # 3 -> steeringwheel_g29
        capl.SetSignal("","hil_drv/target_velocity", 0)
        capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0, 0.5, 25)
    else:
        capl.TestWaitForTimeout(10000)

# ALC Smoke Test
# *********************************************************************************************************************************

def ALC_activation(config, ego_speed, tgt_speed):
    #capl.ReportTestStepPass("Test case:Start")
    Set_Ego_Vehicle(ego_speed)
    Activate_ACC_Cus()
    Check_ACC_Status_Cus()
    Activate_LKS_Cus()
    Check_LKS_Status_Cus(config)
    Set_Indicate_Left()
    Check_ALC_Status_Cus(config)
    capl.ReportTestStepPass("ALC Testcase are done")

def PreConditions_ALC():
    capl.ReportTestStepPass("Pre-cond ACC:Start")
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/MGW/ESP_0x268/ESP_SysSts_EPB", 1) #Released
    Set_Drv_gear(3)  # set Drive gear
    capl.SetSignal("","XCP/DPCdelta5/FctParam/AlcLane/bypassRoadTypePermittedCond", 1)
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/AlcLane/_m_trigger/_m_update", 1)
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/Est/paramFittedEst", 2)  # enhanced
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/Est/_m_trigger/_m_update", 1)
    capl.TestWaitForTimeout(500)

def PostConditions_ALC():
    capl.ReportTestStepPass("Post-cond ACC", "Start")
    capl.SetSignal("","hil_drv/indicator_light", 0)
    capl.TestWaitForTimeout(200)
    #0_not pressed, 1 - off, 2 - ON
    capl.SetSignal("","hil_drv/hmi_btn_adas_lks", 1) #"pressed_off"  # pressed button LKS to switch off
    capl.TestWaitForTimeout(1000)  # short push on the button
    capl.SetSignal("","hil_drv/hmi_btn_adas_lks", 0) #"not_pressed"  # button released
    capl.TestWaitForTimeout(500)
    if capl.GetSignal("","hil_drv/DIL_mode") == 3: # 3 -> steeringwheel_g29
        capl.SetSignal("","hil_drv/target_velocity", 0)
        capl.WaitForSignalInRange("","hil_hvm/velocity_x", 0, 0.5, 25)
    else:
        capl.TestWaitForTimeout(1000)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/AlcLane/bypassRoadTypePermittedCond", 0)
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/AlcLane/_m_trigger/_m_update", 1)
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/Est/paramFittedEst", 0)  # not enhanced
    capl.TestWaitForTimeout(500)
    capl.SetSignal("","XCP/DPCdelta5/FctParam/Est/_m_trigger/_m_update", 1)
    capl.TestWaitForTimeout(500)

def Activate_LKS_Cus():
    #hil_drv_hmi_btn_adas_lks = "pressed_on"  # pressed button LKS to switch ON
    capl.SetSignal("", "hil_drv/hmi_btn_adas_lks", 1)  # "pressed_off"  # pressed button LKS to switch off
    capl.TestWaitForTimeout(500)  # short push on the button
    #hil_drv_hmi_btn_adas_lks = "not_pressed"  # button released
    capl.SetSignal("", "hil_drv/hmi_btn_adas_lks", 0)
    capl.TestWaitForTimeout(3000)

def Check_ALC_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.WaitForSignalInRange("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_alcState", 3, 4, 20)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_alcState")
        if switch == 0:
            capl.ReportTestStepFail("Test case:ALC remained in 'off' state")
        elif switch == 1:
            capl.ReportTestStepFail("Test case:ALC remained in 'passive' state")
        elif switch == 2:
            capl.ReportTestStepFail("Test case:ALC was available switched fast to LaneKeeping after activation")
        elif switch == 3:
            # 0->not active
            # 1->left turn
            # 2->right turn
            if capl.GetSignal("","hil_drv/indicator_light") == 1:   #"leftturn":
                capl.ReportTestStepPass("Test case:ALC activated to left")
        elif switch == 4:
            if capl.GetSignal("","hil_drv/indicator_light") == 2:   #"rightturn":
                capl.ReportTestStepPass("Test case:ALC activated to right")
        elif switch == 5:
            capl.ReportTestStepFail("Test case:ALC fadeout")
        elif switch == 6:
            capl.ReportTestStepFail("Test case:ALC failure")
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_alcState", 2, 20)
        capl.TestWaitForTimeout(5000)

# HF_EST Smoke Test
# *********************************************************************************************************************************

def Check_HF_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_hfState", 20, 30)
        capl.TestWaitForTimeout(200)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_hfState")
        if switch == 0:
            capl.ReportTestStepFail("Test case:HF remained in 'off' state")
        elif switch == 10:
            capl.ReportTestStepFail("Test case:HF remained in 'standbySystem' state")
        elif switch == 11:
            capl.ReportTestStepFail("Test case:HF remained in 'standbyDriver' state")
        elif switch == 20:
            capl.ReportTestStepPass("Test case:HF active state")
        elif switch == 21:
            capl.ReportTestStepFail("Test case:HF switched to takeoverRequest")
        elif switch == 22:
            capl.ReportTestStepFail("Test case:HF switched to handsonRequest")
        elif switch == 23:
            capl.ReportTestStepFail("Test case:HF switched to emergencySafeStop")
        elif switch == 40:
            capl.ReportTestStepFail("Test case:HF failure")
        capl.TestWaitForTimeout(2000)

def Check_EST_Status_Cus(config):
    if config in [6, 7]:  # Delta5 Variants
        capl.AwaitValueMatch("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_hfState", 23, 30)
        capl.TestWaitForTimeout(200)
        switch = capl.GetSignal("","XCP/DPCdelta5/_g_PL_AD_fw_OneDrivingSW_fct_fct_mainproc_ods_fct_ods_fct_mainproc_RunnableMainProc/m_portFunctionStates/m_states/m_hfState")
        if switch == 0:
            capl.ReportTestStepFail("Test case:HF remained in 'off' state")
        elif switch == 10:
            capl.ReportTestStepFail("Test case:HF remained in 'standbySystem' state")
        elif switch == 11:
            capl.ReportTestStepFail("Test case:HF remained in 'standbyDriver' state")
        elif switch == 20:
            capl.ReportTestStepFail("Test case:HF active state")
        elif switch == 21:
            capl.ReportTestStepFail("Test case:HF switched to takeoverRequest")
        elif switch == 22:
            capl.ReportTestStepFail("Test case:HF switched to handsonRequest")
        elif switch == 23:
            capl.ReportTestStepPass("Test case:HF switched to emergencySafeStop")
        elif switch == 40:
            capl.ReportTestStepFail("Test case:HF failure")
        capl.TestWaitForTimeout(2000)

def Set_DriverDistraction_Cus():
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DrvrDstcnStsHSC4", 1)  # no distraction
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/EyeOnRoadHSC4", 3)  # eyes off road
    capl.TestWaitForTimeout(15000)
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/DrvrDstcnStsHSC4", 4)  # high level distraction
    capl.SetSignal("","CAN_ADAS/OD_ADAS_Public_CANFD/DMS/DMS_HSC4_FrP01/EyeOnRoadHSC4", 1)  # eyes on road

def Check_And_Acknowledge_HIL_Abort_Messages():
    capl.CheckSignal("hil_ctrl","abort_message","no abort")
    abort_message = capl.GetSignal("","hil_ctrl/abort_message", silent_flag=True)
    if (abort_message=="no abort"):
        capl.ReportTestStepPass("\nThere are no HIL abort messages")
    else:
        capl.ReportTestStepFail("\nAbort Message : "+abort_message)
        #press the ACK button
        capl.SetSignal("","hil_ctrl/ack_abort_msg_btn",1)
        capl.TestWaitForTimeout(150)
        capl.SetSignal("", "hil_ctrl/ack_abort_msg_btn", 0)
        #press Init RBS button
        capl.SetSignal("", "hil_ctrl/init_rbs", 1)
        capl.AwaitValueMatch("hil_ctrl", "init_rbs",0,15)
        abort_message = capl.GetSignal("", "hil_ctrl/abort_message", silent_flag=True)
        if (abort_message == "no abort"):
            capl.ReportTestStepPass("\nHIL abort messages acknowledged successfully")
        else:
            capl.ReportTestStepFail("\nHIL abort messages can NOT be healed !!!")