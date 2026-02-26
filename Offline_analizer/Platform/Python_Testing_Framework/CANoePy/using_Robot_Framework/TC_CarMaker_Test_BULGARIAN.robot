*** Settings ***
Documentation     Example CANoePy test case using the Robot Framework
Resource          resources/Keywords.resource
Library           XIL_API_Handler.py
Library           HTML_Logger.py

*** Test Cases ***
CANoe Simple Test
    Стартирай логване в HTML формат                      TEST REPORT : Python ACC Test with ADAS HIL 2.xx      CANoePy 1.1       CANoe Simple Test
    Отвори връзка през XIL API с CANoe                   #връзва се с XIL API
    Сетни променлива на CANoe                            hil_ctrl       abort_message           text123
    Сетни променлива на CANoe                            hil_ctrl       configuration_od        5
    Сетни променлива на CANoe                            hil_ctrl       hil_mode               4
    Изчакай определено време                             1000
    Сетни променлива на CANoe                            Customer_specific     cm_scenario     AEB_EgoLong_PedestrianCrossing_left_to_right  # попълване на името на сценария в полето за сценарий в КАНу
    Изчакай определено време                             1000
    Провери сигнал                                       Customer_specific     cm_scenario     AEB_EgoLong_PedestrianCrossing_left_to_right  # проверява дали се е попълнило правилно
    Чакай Докато                                         hil_ctrl    init_cm_done     1       60  # чака до 60 секунди, за да зареди КарМейкър
    Изчакай определено време                             1000
    Сетни променлива на CANoe                            Customer_specific    load_scenario     1  # натиска се бутона LOAD SCENARIO
    Изчакай определено време                             500
    Чакай Докато                                         hil_ctrl    cm_ready_to_start   1  60  # чака се до 60 секунди, за да може CarMaker да зареди сценария
    Изчакай определено време                             1000
    Сетни променлива на CANoe                            hil_ctrl    scenario_start    1  # натиска се бутона START SCENARIO
    Изчакай определено време                             1500
    Чакай Докато                                         CarMaker       SC::State    8       30
    Ускори ego-то до зададена скорост                    50        # сетване на его скорост 50 кмч
    Сетни променлива на CANoe                            hil_drv    gear_req    3  # минаване на предавка DRIVE
    Wait For Signal In Range                             CarMaker    RB/TrafficObj/object0/dtx      25      30      60      #чака егото да достигне на 25 метра от пешеходеца
    Сетни променлива тип масив на CANoe                  Classe_Obj_Sim      obj_ctrl.obj_target_v_long       [13.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]    #пешеходецът скача пред колата
    Сетни променлива на CANoe                            hil_drv      brake_pedal_position       40
    Изчакай определено време                             5000
    Сетни променлива на CANoe                            Customer_specific    cm_stopsim       1  # натиска се бутона STOP SCENARIO за край на симулацията от CarMaker



