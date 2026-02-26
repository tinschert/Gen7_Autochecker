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

tolerance = 4.0
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

def Radars_11obj_in_FOV_of_rear_radars_tx_ty(config, ego_speed, vendor, vehicle_code):
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
    ego_length = 5.0

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
    capl.SetSignal("Customer_specific", "cm_scenario",r"Radars_11obj_in_FOV_of_rear_radars_tx_ty")  # fill the scenario name
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

    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_pos_x", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    capl.TestWaitForTimeout(1000)
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.ctrl_status_pos_y", [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    capl.TestWaitForTimeout(1000)

    i = -6.0
    while i >= -10:
      HTML_Logger.ReportYellowMessage("Checking with pos X = ", i)
      capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_x", [i, i, i, i, i, i, i, i, i, i, i])
      capl.TestWaitForTimeout(300)
      CarMaker_DVAs_mapping()

      #checks:

      for current_object in range(0, 11):
        HTML_Logger.ReportYellowMessage("Checking Road Object : " + str(current_object))

        #RL
        if (capl.GetSignal("","hil_ctrl::radar_rl_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_sim")!=0):
          #check Radar RL only in if it is selected from sensor set
          capl.ReportTestStepPass("Checking RL radar object injection data")
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RL dx = "+str(target_radar_rl_sim_objdata_obj_distance_x[0]))
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RL dy = "+str(target_radar_rl_sim_objdata_obj_distance_y[0]))

          expected_RL_dx = abs((i-ego_length)*(-1.0)*math.cos((180.0-RL_mounting_pos)))
          expected_RL_dy = abs((i)*(-1.0)*math.sin((180.0-RL_mounting_pos)))

          HTML_Logger.ReportYellowMessage("expected RL_dx : " + str(expected_RL_dx))
          HTML_Logger.ReportYellowMessage("value of target_radar_rl_sim_objdata_obj_distance_x[] : " + str(target_radar_rl_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("expected RL_dy : " + str(expected_RL_dy))
          HTML_Logger.ReportYellowMessage("value of target_radar_rl_sim_objdata_obj_distance_y[] : " + str(target_radar_rl_sim_objdata_obj_distance_y[current_object]))

          if (abs(expected_RL_dx-target_radar_rl_sim_objdata_obj_distance_x[current_object])<tolerance):
            capl.ReportTestStepPass("Distance X Radar RL is in range")
          else:
            capl.ReportTestStepFail("Distance X Radar RL is NOT in range")
          if (abs(expected_RL_dy-target_radar_rl_sim_objdata_obj_distance_y[current_object])<tolerance):
            capl.ReportTestStepPass("Distance Y Radar RL is in range")
          else:
            capl.ReportTestStepFail("Distance Y Radar RL is NOT in range")


        #RR
        if (capl.GetSignal("","hil_ctrl::radar_rr_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_sim")!=0):

          #check Radar RR only in if it is selected from sensor set
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RR dx = " + str(target_radar_rr_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RR dy = " + str(target_radar_rr_sim_objdata_obj_distance_y[current_object]))
          capl.ReportTestStepPass("Checking FR radar object injection data")

          expected_RR_dx = (i+ego_length)*(-1.0)*math.cos(180.0-RR_mounting_pos)
          expected_RR_dy = (i)*(-1.0)*math.sin(-180.0-RR_mounting_pos)

          HTML_Logger.ReportYellowMessage("expected RR_dx : ", expected_RR_dx)
          HTML_Logger.ReportYellowMessage("value of target_radar_rr_sim_objdata_obj_distance_x[] : " + str(target_radar_rr_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("expected RR_dy : ", expected_RR_dy)
          HTML_Logger.ReportYellowMessage("value of target_radar_rr_sim_objdata_obj_distance_y[] : " + str(target_radar_rr_sim_objdata_obj_distance_y[current_object]))

          if (abs(expected_RR_dx-target_radar_rr_sim_objdata_obj_distance_x[current_object])<tolerance):
            capl.ReportTestStepPass("Distance X Radar RR is in range")
          else:
            capl.ReportTestStepFail("Distance X Radar RR is NOT in range")

          if (abs(expected_RR_dy-target_radar_rr_sim_objdata_obj_distance_y[current_object])<=tolerance):
            capl.ReportTestStepPass("Distance Y Radar RR is in range")
          else:
            capl.ReportTestStepFail("Distance Y Radar RR is NOT in range")
      i = i - 0.2



    #for testing of Pos Y -> the Pos X is fixed to -10 m
    capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_x", [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10])

    i = -3  # initializing i with -3
    while i < -0.5:  # checking pos Y
      HTML_Logger.ReportYellowMessage("Checking with pos Y = ", i)
      #HTML_Logger.ReportYellowMessage(!!!DEBUG!!! current_pos_y_string = %s",current_pos_y_string)
      capl.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_pos_y", [i, i, i, i, i, i, i, i, i, i, i])
      capl.TestWaitForTimeout(300)
      CarMaker_DVAs_mapping()

      #checks:
      for current_object in range(0, 11):
        HTML_Logger.ReportYellowMessage("Checking Road Object : " + str(current_object))

        #RL
        if (capl.GetSignal("","hil_ctrl::radar_rl_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rl_sim")!=0):
          #check Radar RL only in if it is selected from sensor set
          capl.ReportTestStepPass("Checking FL radar object injection data")
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RL dx = " + str(target_radar_rl_sim_objdata_obj_distance_x[0]))
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RL dy = " + str(target_radar_rl_sim_objdata_obj_distance_y[0]))
          angle_from_CM = target_radar_rl_sim_objdata_obj_heading_angle[current_object]*57.297 #in degrees (2*PI radians = 360 degrees)

          expected_RL_dx = (i)*math.cos((180.0-RL_mounting_pos))+ego_length
          expected_RL_dy = (i+10)*math.sin((180.0-RL_mounting_pos))

          HTML_Logger.ReportYellowMessage("expected RL_dx : ", expected_RL_dx)
          HTML_Logger.ReportYellowMessage("value of target_radar_rl_sim_objdata_obj_distance_x[] : " + str(target_radar_rl_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("expected RL_dy : ")
          HTML_Logger.ReportYellowMessage("value of target_radar_rl_sim_objdata_obj_distance_y[] : " + str(target_radar_rl_sim_objdata_obj_distance_y[current_object]))

          if (abs(expected_RL_dx-target_radar_rl_sim_objdata_obj_distance_x[current_object])<tolerance):
            capl.ReportTestStepPass("Distance X Radar RL is in range")
          else:
            capl.ReportTestStepFail("Distance X Radar RL is NOT in range")

          if (abs(expected_RL_dy-target_radar_rl_sim_objdata_obj_distance_y[current_object])<tolerance):
            capl.ReportTestStepPass("Distance Y Radar RL is in range")
          else:
            capl.ReportTestStepFail("Distance Y Radar RL is NOT in range")


        #RR
        if (capl.GetSignal("","hil_ctrl::radar_rr_loc_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_obj_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_raw_sim")!=0 or capl.GetSignal("","hil_ctrl::radar_rr_sim")!=0):

          #check Radar RR only in if it is selected from sensor set
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RR dx = " + str(target_radar_rr_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("!!!DEBUG!!! Value of Radar RR dy = " + str(target_radar_rr_sim_objdata_obj_distance_y[current_object]))
          capl.ReportTestStepPass("Checking RR radar object injection data")
          angle_from_CM = target_radar_rr_sim_objdata_obj_heading_angle[current_object]*57.297 #in degrees (2*PI radians = 360 degrees)

          expected_RR_dx = (i+10)*math.cos(180.0-RR_mounting_pos)
          expected_RR_dy = (i-ego_length)*(-1.0)*math.sin(-180.0-RR_mounting_pos)

          HTML_Logger.ReportYellowMessage("expected RR_dx : ", expected_RR_dx)
          HTML_Logger.ReportYellowMessage("value of target_radar_rr_sim_objdata_obj_distance_x[] : " + str(target_radar_rr_sim_objdata_obj_distance_x[current_object]))
          HTML_Logger.ReportYellowMessage("expected RR_dy : ", expected_RR_dy)
          HTML_Logger.ReportYellowMessage("value of target_radar_rr_sim_objdata_obj_distance_y[] : " + str(target_radar_rr_sim_objdata_obj_distance_y[current_object]))

          if (abs(expected_RR_dx-target_radar_rr_sim_objdata_obj_distance_x[current_object])<tolerance):
            capl.ReportTestStepPass("Distance X Radar RR is in range")
          else:
            capl.ReportTestStepFail("Distance X Radar RR is NOT in range")

          if (abs(expected_RR_dy-target_radar_rr_sim_objdata_obj_distance_y[current_object])<tolerance):
            capl.ReportTestStepPass("Distance Y Radar RR is in range")
          else:
            capl.ReportTestStepFail("Distance Y Radar RR is NOT in range")
      i = i + 0.2



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
  Radars_11obj_in_FOV_of_rear_radars_tx_ty(5,0,1,0)
  #capl.Testcase_Start(__file__, "CANoePy Testcase", filename="List_All_Signals.html")  # create the HTML report
  #capl.Extract_CANoe_Symbols()
  #print(capl.GetSignal("","RBSData::ObjectData.dWidthN"))
  #print(capl.GetSignal("", "RBSData::RadarData::object0::alpPiYawAngleN"))

  #if capl.GetSignal("", "hil_ctrl/jenkins_control") == 0: HTML_Logger.Show_HTML_Report()
  capl.Testcase_End()


