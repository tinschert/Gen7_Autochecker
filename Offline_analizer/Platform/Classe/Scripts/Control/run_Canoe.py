# -*- coding: utf-8 -*-
# @file run_Canoe.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import time
import os.path
import canape_client
import canoe_client_1
import argparse
import MoveA2L
# import vision_recognition
from logging_config import logger
import glob
from multiprocessing import Process
import fileinput
import sys
import psutil
import time

# def a2l_src_move(path):
#     if os.path.exists(path):
#         logger.info(f"Start copying A2L files from {path} to {dst_path}")
#         a2l = MoveA2L.A2L(path)
#         a2l.move_a2l()
#         a2l.list_a2l()
#     else:
#         logger.error(f"{path} does not exist")
#         raise FileNotFoundError(f"{path} does not exist")
#
#
# def replacement(xcpcfg, al2_name, al2_path_new):
#     for line in fileinput.input(xcpcfg, inplace=1):
#         if al2_name in line:
#             line = line.replace(line, al2_path_new + "\n")
#         sys.stdout.write(line)


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Executes CLOE test units passed in CANoe. For automation the CANoe com interface is used.')
    commandLineParser.add_argument('--sw_release_fr', action="store", dest="sw_release_fr", required=True, help="Absolute path to Front Center Radar AL2 in SW release")  # Example: 20210721_Radar_BoschPsa_KL30_R10_RC01_BTC_MT
    # commandLineParser.add_argument('--sw_release_cr', action="store", dest="sw_release_cr", required=False, help= "Absolute path to Corner Radar AL2 in SW release [Optional]")
    # commandLineParser.add_argument('--configuration', action="store", dest="configuration", required=True, help= "Absolute path to CanOE configuration file")
    # commandLineParser.add_argument('--xcpconfiguration', action="store", dest="xcpconfiguration", required=False, help= "Absolute path to CanOE XCP configuration file [Optional]")
    # commandLineParser.add_argument('--updateXCP', action="store", dest="updateXCP", required=True, help= "Update current XCP configuration - True/False")
    # commandLineParser.add_argument('--masterECU', action="store", dest="masterECU", required=False, help= "Change the default master ECU (RadarFC default) [Optional]")
    # commandLineParser.add_argument('--debugMode', action="store", dest="debugMode", required=True, help= "Use CanAPE in parallel with CanOE - True/False")
    # commandLineParser.add_argument('--canape_project', action="store", dest="canape_project", required=False, help= "Absolute path to Canape project folder [Requiered if --debugMode is True]")
    # commandLineParser.add_argument('--sensor_set', nargs='+', action="store", dest="sensor_set", required=False, help='Sensor set arguments [Shall be passed as space separated arguments]')
    arguments = commandLineParser.parse_args()

    # received_sensor_set = arguments.sensor_set

    src_path_front_radar = arguments.sw_release_fr
    # src_path_corner_radar = arguments.sw_release_cr
    # dst_path = r'..\..\..\..\CustomerPrj\XCP\A2L\\'
    # masterECU = "RadarFC.a2l"
    xcp_configuration = r'..\..\..\..\CustomerPrj\XCP\XCP_config_gen.xcpcfg'
    canape_cna_path = f'{src_path_front_radar.rsplit("database")[0]}Canape'
    # path_front = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{src_path_front_radar}" /></a2l>'
    # path_corner = f'        <a2l><VFileName v="V9" f="QL" init="1" name="{src_path_corner_radar}" /></a2l>'

    # if arguments.masterECU:
    #     masterECU = arguments.masterECU + ".a2l"
    # else:
    #     masterECU = "RadarFC.a2l"

    logger.info("======= Start CanOE automation script ======")

    # if arguments.updateXCP == "True":
    #     # logger.info(f"Cleaning {dst_path}")
    #     # existing_al2s = glob.glob(dst_path + "*.a2l")
    #     # if existing_al2s:
    #     #     for f in existing_al2s:
    #     #         os.remove(f)
    #
    #     # if arguments.sw_release_fr is not None:
    #     #     a2l_src_move(src_path_front_radar)
    #     # if arguments.sw_release_cr is not None:
    #     #     a2l_src_move(src_path_corner_radar)
    #
    #     if arguments.sw_release_fr is not None:
    #         replacement(xcp_configuration, src_path_front_radar.rsplit("\\", 1)[1], path_front)
    #     if arguments.sw_release_cr is not None:
    #         replacement(xcp_configuration, src_path_corner_radar.rsplit("\\", 1)[1], path_corner)
    #
    #     xcp = XCP_to_A2L_diff.XCPConfigurator(src_path_front_radar)
    #     """Create a list of all available XCP signals in FDX_Databse (sheet "Checks cloes") """
    #     excel_signal_list = xcp.parseFDX_evald()
    #     """ Extract MEASUREMENT and CHARACTERISTIC entries into list  """
    #     a2l_list = xcp.extract_A2l(src_path_front_radar)
    #     """ Compare FDX_Database XCP entries against A2L file  """
    #     #xcp.parseA2l(excel_signal_list, a2l_list)
    #     """ Find the index of Radar to be configured in configuration file """
    #     ecu_index = xcp.find_ECU(xcp_configuration, masterECU.split(".")[0])
    #     """ Extract currently configured XCP vars into configuration file """
    #     configured_xcp = xcp.parseXCPconfig2(xcp_configuration, ecu_index)
    #     """ Compare configuration file entries against A2L file """
    #     xcp.xcpDiff(a2l_list, configured_xcp)
    #
    #     """ Compare FDX_Database XCP entries against current XCP config entries """
    #     filtered_list = xcp.xcpDiff_excel(excel_signal_list, configured_xcp)
    #
    #     if filtered_list:
    #         logger.info("Step 6 --> Updating XCP configuration file")
    #         for missing_xcp in filtered_list:
    #             xcp.add_XCP(xcp_configuration, missing_xcp, ecu_index)
    #         logger.info("Step 7 --> Finished updating XCP configuration file")

    """ Canoe section"""
    start_canoe = time.time()
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    canapeClient = canape_client.CanapeClient()
    # canoeClient.openConfiguration(arguments.configuration)
    canoe_started = time.time()
    logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
    canoeClient.startMeasurement()
    time.sleep(10)

    def stop_start_logging():
        """ Stop/Start logging in Canoe"""
        canapeClient.start_measurement()
        if canapeClient.check_measurement_status() is False:
            logger.error("Canape measurement is not started")
        else:
            logger.info("Canape measurement started")
            canapeClient.stop_meas()
            while canapeClient.recorder_status() != 0:
                logger.info("Stopping the logging.Please wait.")
                time.sleep(20)
            logger.info("CANape logging stopped")
            time.sleep(10)
            canapeClient.start_meas()
            while canapeClient.recorder_status() != 2:
                logger.info("Starting the logging.Please wait...")
                time.sleep(30)
            canoeClient.setVariableToValue("hil_ctrl", "debug_trace_radar_fr", 2)
            logger.info("CANape logging started")

    while canoeClient.CANoe.Measurement.Running:
        if int(canoeClient.getSysVariable("hil_ctrl", "debug_trace_radar_fr")) == 1 and int(canoeClient.getSysVariable("hil_ctrl", "trace_logging_start_mf4")) == 1:
            if "CANape64.exe" not in (p.name() for p in psutil.process_iter()):
                # p1 = Process(target=vision_recognition.start_vision_recognition, args=(60,))
                # p1.start()
                logger.info("Starting CANape application")
                p2 = Process(target=canapeClient.open(canape_cna_path))
                p2.start()
                # p1.join()
                p2.join()
                stop_start_logging()
            else:
                stop_start_logging()

        if int(canoeClient.getSysVariable("hil_ctrl", "trace_logging_start_mf4")) == 0 and canapeClient.check_measurement_status():
            if canapeClient.recorder_status() != 0:
                logger.info(f"Stop trace logging detected (trace_logging_start = 0)")
                canapeClient.stop_save_meas()
                while canapeClient.recorder_status() != 0:
                    logger.info("Saving mf4 log.Please wait.")
                    time.sleep(20)
                logger.info("CANape MF4 file saved")

    canapeClient.stop_measurement()
    if canapeClient.check_measurement_status() is True:
        logger.error("Canape measurement could not be stopped")
    else:
        logger.info("Canape measurement stopped successfully")
    canoeClient.quitCanoe(False)
    if "CANape64.exe" in (p.name() for p in psutil.process_iter()):
        canapeClient.quit()
    canoeClient = None
    canapeClient = None


