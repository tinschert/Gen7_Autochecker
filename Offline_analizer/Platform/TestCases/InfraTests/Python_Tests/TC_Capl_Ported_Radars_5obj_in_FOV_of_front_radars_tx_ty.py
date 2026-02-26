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

# C++ TO PYTHON CONVERTER TASK: The following method format was not recognized, possibly due to an unrecognized macro:

tolerance = 3.0
angle_from_CM = 0.0 #heading angle of the target as loopback from CarMaker (taken from RB::Radar DVAs structure)
current_object = 0
number_of_objects_in_testcase = 5
FC_mounting_pos = 0.0
FL_mounting_pos = 45.0
FR_mounting_pos = -45.0
RL_mounting_pos = 135.0
RR_mounting_pos = -135.0
ego_length = 5.5
expected_FL_dx = 0.0
expected_FL_dy = 0.0
expected_FR_dx = 0.0
expected_FR_dy = 0.0

target_radar_fc_sim_objdata_obj_heading_angle = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_distance_x_previous = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_distance_x = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_distance_y_previous = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_distance_y = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_length = [0 for _ in range(11)]
target_radar_fc_sim_objdata_obj_width = [0 for _ in range(11)]

target_radar_fl_sim_objdata_obj_heading_angle = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_distance_x_previous = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_distance_x = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_distance_y_previous = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_distance_y = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_length = [0 for _ in range(11)]
target_radar_fl_sim_objdata_obj_width = [0 for _ in range(11)]

target_radar_fr_sim_objdata_obj_heading_angle = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_distance_x_previous = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_distance_x = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_distance_y_previous = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_distance_y = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_length = [0 for _ in range(11)]
target_radar_fr_sim_objdata_obj_width = [0 for _ in range(11)]

target_radar_rl_sim_objdata_obj_heading_angle = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_distance_x_previous = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_distance_x = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_distance_y_previous = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_distance_y = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_length = [0 for _ in range(11)]
target_radar_rl_sim_objdata_obj_width = [0 for _ in range(11)]

target_radar_rr_sim_objdata_obj_heading_angle = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_distance_x_previous = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_distance_x = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_distance_y_previous = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_distance_y = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_length = [0 for _ in range(11)]
target_radar_rr_sim_objdata_obj_width = [0 for _ in range(11)]


def CarMaker_DVAs_mapping():
  HTML_Logger.ReportYellowMessage("CarMaker DVAs mapping started...")
  HTML_Logger.ReportYellowMessage("================================")
  global target_radar_fc_sim_objdata_obj_heading_angle
  global target_radar_fc_sim_objdata_obj_distance_x_previous
  global target_radar_fc_sim_objdata_obj_distance_x
  global target_radar_fc_sim_objdata_obj_distance_y_previous
  global target_radar_fc_sim_objdata_obj_distance_y
  global target_radar_fc_sim_objdata_obj_length
  global target_radar_fc_sim_objdata_obj_width

  global target_radar_fl_sim_objdata_obj_heading_angle
  global target_radar_fl_sim_objdata_obj_distance_x_previous
  global target_radar_fl_sim_objdata_obj_distance_x
  global target_radar_fl_sim_objdata_obj_distance_y_previous
  global target_radar_fl_sim_objdata_obj_distance_y
  global target_radar_fl_sim_objdata_obj_length
  global target_radar_fl_sim_objdata_obj_width

  global target_radar_fr_sim_objdata_obj_heading_angle
  global target_radar_fr_sim_objdata_obj_distance_x_previous
  global target_radar_fr_sim_objdata_obj_distance_x
  global target_radar_fr_sim_objdata_obj_distance_y_previous
  global target_radar_fr_sim_objdata_obj_distance_y
  global target_radar_fr_sim_objdata_obj_length
  global target_radar_fr_sim_objdata_obj_width

  global target_radar_rl_sim_objdata_obj_heading_angle
  global target_radar_rl_sim_objdata_obj_distance_x_previous
  global target_radar_rl_sim_objdata_obj_distance_x
  global target_radar_rl_sim_objdata_obj_distance_y_previous
  global target_radar_rl_sim_objdata_obj_distance_y
  global target_radar_rl_sim_objdata_obj_length
  global target_radar_rl_sim_objdata_obj_width

  global target_radar_rr_sim_objdata_obj_heading_angle
  global target_radar_rr_sim_objdata_obj_distance_x_previous
  global target_radar_rr_sim_objdata_obj_distance_x
  global target_radar_rr_sim_objdata_obj_distance_y_previous
  global target_radar_rr_sim_objdata_obj_distance_y
  global target_radar_rr_sim_objdata_obj_length
  global target_radar_rr_sim_objdata_obj_width

  target_radar_fc_sim_objdata_obj_distance_x_previous[0] = target_radar_fc_sim_objdata_obj_distance_x[0]
  target_radar_fc_sim_objdata_obj_distance_x_previous[1] = target_radar_fc_sim_objdata_obj_distance_x[1]
  target_radar_fc_sim_objdata_obj_distance_x_previous[2] = target_radar_fc_sim_objdata_obj_distance_x[2]
  target_radar_fc_sim_objdata_obj_distance_x_previous[3] = target_radar_fc_sim_objdata_obj_distance_x[3]
  target_radar_fc_sim_objdata_obj_distance_x_previous[4] = target_radar_fc_sim_objdata_obj_distance_x[4]
  target_radar_fc_sim_objdata_obj_distance_x_previous[5] = target_radar_fc_sim_objdata_obj_distance_x[5]
  target_radar_fc_sim_objdata_obj_distance_x_previous[6] = target_radar_fc_sim_objdata_obj_distance_x[6]
  target_radar_fc_sim_objdata_obj_distance_x_previous[7] = target_radar_fc_sim_objdata_obj_distance_x[7]
  target_radar_fc_sim_objdata_obj_distance_x_previous[8] = target_radar_fc_sim_objdata_obj_distance_x[8]
  target_radar_fc_sim_objdata_obj_distance_x_previous[9] = target_radar_fc_sim_objdata_obj_distance_x[9]
  target_radar_fc_sim_objdata_obj_distance_x_previous[10] = target_radar_fc_sim_objdata_obj_distance_x[10]

  target_radar_fl_sim_objdata_obj_distance_x_previous[0] = target_radar_fl_sim_objdata_obj_distance_x[0]
  target_radar_fl_sim_objdata_obj_distance_x_previous[1] = target_radar_fl_sim_objdata_obj_distance_x[1]
  target_radar_fl_sim_objdata_obj_distance_x_previous[2] = target_radar_fl_sim_objdata_obj_distance_x[2]
  target_radar_fl_sim_objdata_obj_distance_x_previous[3] = target_radar_fl_sim_objdata_obj_distance_x[3]
  target_radar_fl_sim_objdata_obj_distance_x_previous[4] = target_radar_fl_sim_objdata_obj_distance_x[4]
  target_radar_fl_sim_objdata_obj_distance_x_previous[5] = target_radar_fl_sim_objdata_obj_distance_x[5]
  target_radar_fl_sim_objdata_obj_distance_x_previous[6] = target_radar_fl_sim_objdata_obj_distance_x[6]
  target_radar_fl_sim_objdata_obj_distance_x_previous[7] = target_radar_fl_sim_objdata_obj_distance_x[7]
  target_radar_fl_sim_objdata_obj_distance_x_previous[8] = target_radar_fl_sim_objdata_obj_distance_x[8]
  target_radar_fl_sim_objdata_obj_distance_x_previous[9] = target_radar_fl_sim_objdata_obj_distance_x[9]
  target_radar_fl_sim_objdata_obj_distance_x_previous[10] = target_radar_fl_sim_objdata_obj_distance_x[10]
  target_radar_fr_sim_objdata_obj_distance_x_previous[0] = target_radar_fr_sim_objdata_obj_distance_x[0]
  target_radar_fr_sim_objdata_obj_distance_x_previous[1] = target_radar_fr_sim_objdata_obj_distance_x[1]
  target_radar_fr_sim_objdata_obj_distance_x_previous[2] = target_radar_fr_sim_objdata_obj_distance_x[2]
  target_radar_fr_sim_objdata_obj_distance_x_previous[3] = target_radar_fr_sim_objdata_obj_distance_x[3]
  target_radar_fr_sim_objdata_obj_distance_x_previous[4] = target_radar_fr_sim_objdata_obj_distance_x[4]
  target_radar_fr_sim_objdata_obj_distance_x_previous[5] = target_radar_fr_sim_objdata_obj_distance_x[5]
  target_radar_fr_sim_objdata_obj_distance_x_previous[6] = target_radar_fr_sim_objdata_obj_distance_x[6]
  target_radar_fr_sim_objdata_obj_distance_x_previous[7] = target_radar_fr_sim_objdata_obj_distance_x[7]
  target_radar_fr_sim_objdata_obj_distance_x_previous[8] = target_radar_fr_sim_objdata_obj_distance_x[8]
  target_radar_fr_sim_objdata_obj_distance_x_previous[9] = target_radar_fr_sim_objdata_obj_distance_x[9]
  target_radar_fr_sim_objdata_obj_distance_x_previous[10] = target_radar_fr_sim_objdata_obj_distance_x[10]
  target_radar_rl_sim_objdata_obj_distance_x_previous[0] = target_radar_rl_sim_objdata_obj_distance_x[0]
  target_radar_rl_sim_objdata_obj_distance_x_previous[1] = target_radar_rl_sim_objdata_obj_distance_x[1]
  target_radar_rl_sim_objdata_obj_distance_x_previous[2] = target_radar_rl_sim_objdata_obj_distance_x[2]
  target_radar_rl_sim_objdata_obj_distance_x_previous[3] = target_radar_rl_sim_objdata_obj_distance_x[3]
  target_radar_rl_sim_objdata_obj_distance_x_previous[4] = target_radar_rl_sim_objdata_obj_distance_x[4]
  target_radar_rl_sim_objdata_obj_distance_x_previous[5] = target_radar_rl_sim_objdata_obj_distance_x[5]
  target_radar_rl_sim_objdata_obj_distance_x_previous[6] = target_radar_rl_sim_objdata_obj_distance_x[6]
  target_radar_rl_sim_objdata_obj_distance_x_previous[7] = target_radar_rl_sim_objdata_obj_distance_x[7]
  target_radar_rl_sim_objdata_obj_distance_x_previous[8] = target_radar_rl_sim_objdata_obj_distance_x[8]
  target_radar_rl_sim_objdata_obj_distance_x_previous[9] = target_radar_rl_sim_objdata_obj_distance_x[9]
  target_radar_rl_sim_objdata_obj_distance_x_previous[10] = target_radar_rl_sim_objdata_obj_distance_x[10]
  target_radar_rr_sim_objdata_obj_distance_x_previous[0] = target_radar_rr_sim_objdata_obj_distance_x[0]
  target_radar_rr_sim_objdata_obj_distance_x_previous[1] = target_radar_rr_sim_objdata_obj_distance_x[1]
  target_radar_rr_sim_objdata_obj_distance_x_previous[2] = target_radar_rr_sim_objdata_obj_distance_x[2]
  target_radar_rr_sim_objdata_obj_distance_x_previous[3] = target_radar_rr_sim_objdata_obj_distance_x[3]
  target_radar_rr_sim_objdata_obj_distance_x_previous[4] = target_radar_rr_sim_objdata_obj_distance_x[4]
  target_radar_rr_sim_objdata_obj_distance_x_previous[5] = target_radar_rr_sim_objdata_obj_distance_x[5]
  target_radar_rr_sim_objdata_obj_distance_x_previous[6] = target_radar_rr_sim_objdata_obj_distance_x[6]
  target_radar_rr_sim_objdata_obj_distance_x_previous[7] = target_radar_rr_sim_objdata_obj_distance_x[7]
  target_radar_rr_sim_objdata_obj_distance_x_previous[8] = target_radar_rr_sim_objdata_obj_distance_x[8]
  target_radar_rr_sim_objdata_obj_distance_x_previous[9] = target_radar_rr_sim_objdata_obj_distance_x[9]
  target_radar_rr_sim_objdata_obj_distance_x_previous[10] = target_radar_rr_sim_objdata_obj_distance_x[10]

def Radars_5obj_in_FOV_of_front_radars_tx_ty(config, ego_speed, number_of_locations_per_object, vendor, vehicle_code):
    global target_radar_fc_sim_objdata_obj_heading_angle
    global target_radar_fc_sim_objdata_obj_distance_x_previous
    global target_radar_fc_sim_objdata_obj_distance_x
    global target_radar_fc_sim_objdata_obj_distance_y_previous
    global target_radar_fc_sim_objdata_obj_distance_y
    global target_radar_fc_sim_objdata_obj_length
    global target_radar_fc_sim_objdata_obj_width

    global target_radar_fl_sim_objdata_obj_heading_angle
    global target_radar_fl_sim_objdata_obj_distance_x_previous
    global target_radar_fl_sim_objdata_obj_distance_x
    global target_radar_fl_sim_objdata_obj_distance_y_previous
    global target_radar_fl_sim_objdata_obj_distance_y
    global target_radar_fl_sim_objdata_obj_length
    global target_radar_fl_sim_objdata_obj_width

    global target_radar_fr_sim_objdata_obj_heading_angle
    global target_radar_fr_sim_objdata_obj_distance_x_previous
    global target_radar_fr_sim_objdata_obj_distance_x
    global target_radar_fr_sim_objdata_obj_distance_y_previous
    global target_radar_fr_sim_objdata_obj_distance_y
    global target_radar_fr_sim_objdata_obj_length
    global target_radar_fr_sim_objdata_obj_width

    global target_radar_rl_sim_objdata_obj_heading_angle
    global target_radar_rl_sim_objdata_obj_distance_x_previous
    global target_radar_rl_sim_objdata_obj_distance_x
    global target_radar_rl_sim_objdata_obj_distance_y_previous
    global target_radar_rl_sim_objdata_obj_distance_y
    global target_radar_rl_sim_objdata_obj_length
    global target_radar_rl_sim_objdata_obj_width

    global target_radar_rr_sim_objdata_obj_heading_angle
    global target_radar_rr_sim_objdata_obj_distance_x_previous
    global target_radar_rr_sim_objdata_obj_distance_x
    global target_radar_rr_sim_objdata_obj_distance_y_previous
    global target_radar_rr_sim_objdata_obj_distance_y
    global target_radar_rr_sim_objdata_obj_length
    global target_radar_rr_sim_objdata_obj_width

    capl.Testcase_Start(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report
    FC_mounting_pos = capl.GetSignal("","radarfc_par::mounting_ori_yaw")*57.29577951307854999853275233034 #radian-to-degree
    FL_mounting_pos = capl.GetSignal("","radarfl_par::mounting_ori_yaw")*57.29577951307854999853275233034 #radian-to-degree
    FR_mounting_pos = capl.GetSignal("","radarfr_par::mounting_ori_yaw")*57.29577951307854999853275233034 #radian-to-degree
    RL_mounting_pos = capl.GetSignal("","radarrl_par::mounting_ori_yaw")*57.29577951307854999853275233034 #radian-to-degree
    RR_mounting_pos = capl.GetSignal("","radarrr_par::mounting_ori_yaw")*57.29577951307854999853275233034 #radian-to-degree


    capl.SetSignal("","hil_ctrl::vehicle", vehicle_code) #set the vehicle variant
    #cf_testPreparation()

    #PreConditionsCM(config)
    capl.SetSignal("hil_ctrl", "configuration_od", config)

    #enable radar sim
    capl.SetSignal("","hil_ctrl::radar_rl_sim",1)
    capl.SetSignal("", "hil_ctrl::radar_rr_sim", 1)

    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)  # set HIL mode to CarMaker
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "cm_scenario",r"Radars_5obj_in_FOV_of_front_radars_tx_ty")  # fill the scenario name
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

    tf.Set_Drv_gear(0)  # set park gear

    tf.Set_Ego_Vehicle_Velocity(0)
    capl.SetSignal("","hil_ctrl::starmodel_max_loc_nr", 15)
    capl.SetSignal("","hil_ctrl::clara_model_max_loc_nr_per_obj", 15)

    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_pos_x", [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    capl.TestWaitForTimeout(1000)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_pos_y", [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0])
    capl.TestWaitForTimeout(1000)

    i = 6.0  # checking pos X
    while i < 9.0:
        HTML_Logger.ReportYellowMessage("Checking with pos X = "+str(i))
        #HTML_Logger.ReportYellowMessage("!!!DEBUG!!! current_pos_x_string = %s",current_pos_x_string)

        capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_x", [i, i, i, i, i, i, 0, 0, 0, 0, 0])
        capl.TestWaitForTimeout(300)

        CarMaker_DVAs_mapping()

        #checks:

        current_object = 0
        while current_object < number_of_objects_in_testcase:
            HTML_Logger.ReportYellowMessage("Checking Road Object : " + str(current_object))
            HTML_Logger.ReportYellowMessage("!!!DEBUG!!! current_object_string = "+str(current_object))

            #check Radar FC only in if it is selected from sensor set
            if (capl.GetSignal("","hil_ctrl::radar_fc_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fc_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fc_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fc_sim")!=0):
                HTML_Logger.ReportYellowMessage("Checking FC radar object injection data")
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FC dx = "+str(target_radar_fc_sim_objdata_obj_distance_x[0]))
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FC dy = "+str(target_radar_fc_sim_objdata_obj_distance_y[0]))

                if abs(target_radar_fc_sim_objdata_obj_distance_x[0] - i) < tolerance:
                    capl.ReportTestStepPass("Distance X Radar FC is in range")
                else:
                    capl.ReportTestStepFail("Distance X Radar FC is NOT in range")
                if target_radar_fc_sim_objdata_obj_distance_y[0] <= tolerance:
                    capl.ReportTestStepPass("Distance Y Radar FC is in range")
                else:
                    capl.ReportTestStepFail("Distance Y Radar FC is NOT in range")

            #check Radar FL only in if it is selected from sensor set
            if (capl.GetSignal("","hil_ctrl::radar_fl_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_sim")!=0):
                HTML_Logger.ReportYellowMessage("Checking FL radar object injection data","")
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FL dx = "+str(target_radar_fl_sim_objdata_obj_distance_x[0]))
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FL dy = "+str(target_radar_fl_sim_objdata_obj_distance_y[0]))

                expected_FL_dx = (i - ego_length) * math.cos(FL_mounting_pos)
                expected_FL_dy = (i) * (-1.0) * math.sin(FL_mounting_pos)

                HTML_Logger.ReportYellowMessage("expected FL_dx : "+str(expected_FL_dx))
                HTML_Logger.ReportYellowMessage("value of target_radar_fl_sim_objdata_obj_distance_x[] : "+str(target_radar_fl_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("expected FL_dy : "+str(expected_FL_dy))
                HTML_Logger.ReportYellowMessage("value of target_radar_fl_sim_objdata_obj_distance_y[] : "+str(target_radar_fl_sim_objdata_obj_distance_y[current_object]))


                if abs(expected_FL_dx - target_radar_fl_sim_objdata_obj_distance_x[0]) < tolerance:
                    capl.ReportTestStepPass("Distance X Radar FL is in range")
                else:
                    capl.ReportTestStepFail("Distance X Radar FL is NOT in range")
                if abs(expected_FL_dy - target_radar_fl_sim_objdata_obj_distance_y[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance Y Radar FL is in range")
                else:
                    capl.ReportTestStepFail("Distance Y Radar FL is NOT in range")


            #check Radar FR only in if it is selected from sensor set
            if (capl.GetSignal("","hil_ctrl::radar_fr_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_sim")!=0):
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FR dx = "+str(target_radar_fr_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FR dy = "+str(target_radar_fr_sim_objdata_obj_distance_y[current_object]))
                HTML_Logger.ReportYellowMessage("Checking FR radar object injection data","")

                expected_FR_dx = (i - ego_length) * math.cos(FR_mounting_pos)
                expected_FR_dy = (i) * (-1.0) * math.sin(FR_mounting_pos)

                HTML_Logger.ReportYellowMessage("expected FR_dx : ", expected_FR_dx)
                HTML_Logger.ReportYellowMessage("value of target_radar_fr_sim_objdata_obj_distance_x[] : "+str(target_radar_fr_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("expected FR_dy : ", expected_FR_dy)
                HTML_Logger.ReportYellowMessage("value of target_radar_fr_sim_objdata_obj_distance_y[] : "+str(target_radar_fr_sim_objdata_obj_distance_y[current_object]))

                if abs(expected_FR_dx - target_radar_fr_sim_objdata_obj_distance_x[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance X Radar FR is in range")
                else:
                    capl.ReportTestStepFail("Distance X Radar FR is NOT in range")
                if abs(expected_FR_dy - target_radar_fr_sim_objdata_obj_distance_y[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance Y Radar FR is in range")
                else:
                    capl.ReportTestStepFail("Distance Y Radar FR is NOT in range")
            current_object = current_object + 1
        i = i + 0.2


    #for testing of Pos Y -> the Pos X is fixed to 10 m
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_x", [10, 10, 10, 10, 10, 10, 0, 0, 0, 0, 0])
#
    i = 0.5  # initializing i
    while i <= 3.5:  # checking pos Y
        HTML_Logger.ReportYellowMessage("Checking with pos y = "+str(i))
        HTML_Logger.ReportYellowMessage("!!!DEBUG!!! current_pos_y_string = "+str(i))

        capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_y", [i, i, i, i, i, i, 0, 0, 0, 0, 0])
        capl.TestWaitForTimeout(300)
#
        CarMaker_DVAs_mapping()
#
        #checks:
#
        current_object = 0
        while current_object < number_of_objects_in_testcase:
            HTML_Logger.ReportYellowMessage("Checking Road Object : "+str(current_object))

            #check Radar FL only in if it is selected from sensor set
            if (capl.GetSignal("","hil_ctrl::radar_fl_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fl_sim")!=0):
                HTML_Logger.ReportYellowMessage("Checking FL radar object injection data","")
                #HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FL dx = ",target_radar_fl_sim_objdata_obj_distance_x[0])
                #HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FL dy = ",target_radar_fl_sim_objdata_obj_distance_y[0])
#
                expected_FL_dx = (i - ego_length) * math.cos(FL_mounting_pos)
                expected_FL_dy = (i + 10 * math.sin(FL_mounting_pos)) * (-1.0) * math.sin(FL_mounting_pos)
#
                HTML_Logger.ReportYellowMessage("expected FL_dx : "+str(expected_FL_dx))
                HTML_Logger.ReportYellowMessage("value of target_radar_fl_sim_objdata_obj_distance_x[] : "+str(target_radar_fl_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("expected FL_dy : "+str(expected_FL_dy))
                HTML_Logger.ReportYellowMessage("value of target_radar_fl_sim_objdata_obj_distance_y[] : "+str(target_radar_fl_sim_objdata_obj_distance_y[current_object]))

                if abs(expected_FL_dx - target_radar_fl_sim_objdata_obj_distance_x[0]) < tolerance:
                    capl.ReportTestStepPass("Distance X Radar FL is in range")
                else:
                    capl.ReportTestStepFail("Distance X Radar FL is NOT in range")
                if abs(expected_FL_dy - target_radar_fl_sim_objdata_obj_distance_y[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance Y Radar FL is in range")
                else:
                    capl.ReportTestStepFail("Distance Y Radar FL is NOT in range")
#
#
            #check Radar FR only in if it is selected from sensor set
            if (capl.GetSignal("","hil_ctrl::radar_fr_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_fr_sim")!=0):
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FR dx = "+str(target_radar_fr_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar FR dy = "+str(target_radar_fr_sim_objdata_obj_distance_y[current_object]))
                HTML_Logger.ReportYellowMessage("Checking FR radar object injection data","")
#
                expected_FR_dx = (i) * math.cos(FR_mounting_pos)
                expected_FR_dy = (i) * (-1.0) * math.sin(FR_mounting_pos)
#
                HTML_Logger.ReportYellowMessage("expected FR_dx : "+str(expected_FR_dx))
                HTML_Logger.ReportYellowMessage("value of target_radar_fr_sim_objdata_obj_distance_x[] : "+str(target_radar_fr_sim_objdata_obj_distance_x[current_object]))
                HTML_Logger.ReportYellowMessage("expected FR_dy : ", expected_FR_dy)
                HTML_Logger.ReportYellowMessage("value of target_radar_fr_sim_objdata_obj_distance_y[] : "+str(target_radar_fr_sim_objdata_obj_distance_y[current_object]))

                if abs(expected_FR_dx - target_radar_fr_sim_objdata_obj_distance_x[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance X Radar FR is in range")
                else:
                    capl.ReportTestStepFail("Distance X Radar FR is NOT in range")
                if abs(expected_FR_dy - target_radar_fr_sim_objdata_obj_distance_y[current_object]) < tolerance:
                    capl.ReportTestStepPass("Distance Y Radar FR is in range")
                else:
                    capl.ReportTestStepFail("Distance Y Radar FR is NOT in range")
            current_object = current_object + 1
        i = i + 0.5

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
    Radars_5obj_in_FOV_of_front_radars_tx_ty(5, 0, 1, 0,0)
