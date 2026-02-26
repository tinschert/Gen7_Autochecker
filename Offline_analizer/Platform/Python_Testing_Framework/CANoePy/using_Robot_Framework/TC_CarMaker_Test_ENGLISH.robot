*** Settings ***
Documentation     Example CANoePy test case using the Robot Framework
Resource          resources/Keywords.resource
Library           XIL_API_Handler.py
Library           HTML_Logger.py

*** Test Cases ***
CANoe Simple Test
    Start HTML logging              TEST REPORT : Python ACC Test with ADAS HIL 2.xx      CANoePy 1.1       CANoe Simple Test
    Do Nothing                      # :-) just as POC
    Open Connection                 #connects to XIL API
    Write CANoe Symbol              hil_ctrl       abort_message           text123
    Write CANoe Symbol              hil_ctrl       configuration_od        5
    Set Signal                      hil_ctrl       hil_mode               4
    Test Wait For Timeout           1000
    Set Signal                      Customer_specific     cm_scenario     AEB_EgoLong_PedestrianCrossing_left_to_right  # fill the scenario name
    Test Wait For Timeout           1000
    Check Signal                    Customer_specific     cm_scenario     AEB_EgoLong_PedestrianCrossing_left_to_right  # check if scenario field is populated
    Await Value Match               hil_ctrl    init_cm_done     1       60  # wait green LED
    Test Wait For Timeout           1000
    Set Signal                      Customer_specific    load_scenario     1  # press the LOAD SCENARIO button
    Test Wait For Timeout           500
    #Set Signal                      Customer_specific    load_scenario     0  # release the LOAD SCENARIO button
    Await Value Match               hil_ctrl    cm_ready_to_start   1  60  # wait green LED
    Test Wait For Timeout           1000
    Set Signal                      hil_ctrl    scenario_start    1  # press the START SCENARIO button
    Test Wait For Timeout           500
    #Set Signal                      hil_ctrl    scenario_start     0)  # release the START SCENARIO button
    Test Wait For Timeout           1000
    Await Value Match               CarMaker       SC::State    8       30
    Set Ego Vehicle Velocity        50        # set ego speed
    Set Signal                      hil_drv    gear_req    3  # set Gear to DRIVE
    Wait For Signal In Range        CarMaker    RB/TrafficObj/object0/dtx      25      30      60
    Set Signal Array                Classe_Obj_Sim      obj_ctrl.obj_target_v_long       [13.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    Set Signal                      hil_drv      brake_pedal_position       40
    Test Wait For Timeout           5000
    Set Signal                      Customer_specific    cm_stopsim       1  # press the STOP SIM button to END scenario/test



