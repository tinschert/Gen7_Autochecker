#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an test function library


import CAPL_Wrapper_Functions as capl


##################################################################################################################################################################################################################
# TEST FUNCTIONS using the CAPL wrapper functions
##################################################################################################################################################################################################################
def Set_Ego_Vehicle_Velocity(ego_speed):
    temp_val = float(ego_speed)
    capl.SetSignal("hil_drv","target_velocity",temp_val)
    capl.WaitForSignalInRange("hil_hvm","velocity_x", temp_val-1,temp_val+1,25)
    capl.TestWaitForTimeout(500)

def Activate_ACC_Cus():
    #val1 = capl.GetSignal("hil_drv","hmi_btn_adas_acc::pressed")
    #2 - pressed
    #1 - not pressed
    capl.SetSignal("hil_drv", "hmi_btn_adas_acc",2)
    capl.TestWaitForTimeout(500);
    #val2=capl.GetSignal("hil_drv::hmi_btn_adas_acc","not_pressed")
    capl.SetSignal("hil_drv", "hmi_btn_adas_acc",1)
    capl.TestWaitForTimeout(500);

def Check_ACC_Status_Cus():
    #1 - active
    #0 - not active
    val1 = capl.GetSignal("hil_adas","hmi_display_adas_acc_status")
    #val2 = capl.GetSignal("hil_adas::hmi_display_adas_acc_status","active")
    if (val1 == 1): #Check Status ACC
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

