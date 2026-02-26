# -*- coding: utf-8 -*-
# @file canape_client.py
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


import win32com.client as win32
from logging_config import logger
import os


class CanapeClient:
    """A COM client used to remote control CANoe."""

    def __init__(self):
        self.CANape = win32.gencache.EnsureDispatch("CANape.Application")
        self.script_path = os.path.dirname(os.path.abspath(__file__))

    def open(self, path: str):
        """
        Opens path to the Canape project

        Args:
          path (str): Path to the canape project
        Returns:
        """
        self.CANape.Open1(path, 1, 500000, 1)
        logger.info(f"Opening Canape prject --> {path}")

    def load_cna(self, path_cna):
        """
        Loads cna file in Canape via COM interface

        Args:
          path_cna (str) : Path to the Canape cna file
        Returns:

        """
        self.CANape.LoadCNAFile(path_cna)

    def stop_save_meas(self):
        """ Call RecorderStopSave.cns in order to stop and save measurement """
        self.CANape.RunScript(self.script_path + "\RecorderStopSave.cns")
        logger.info("Stop and save MF4 log")

    def start_meas(self):
        """ Call RecorderStart.cns in order to start measurement """
        self.CANape.RunScript(self.script_path + "\RecorderStart.cns")
        logger.info("Starting CANape MF4 logging")

    def stop_meas(self):
        """ Call StopRecorder.cns in order to stop measurement """
        self.CANape.RunScript(self.script_path + "\StopRecorder.cns")
        logger.info("Stopping CANape MF4 logging")

    def start_measurement(self):
        """ Start measurement via COM interface """
        logger.info("Starting Canape measurement")
        self.CANape.Measurement.Start()

    def stop_measurement(self):
        """ Stop measurement via COM interface """
        logger.info("Stopping Canape measurement")
        self.CANape.Measurement.Stop()

    def check_measurement_status(self):
        """ Check measurement status of Canape"""
        return self.CANape.Measurement.Running

    def quit(self):
        """ Quit Canape """
        self.CANape.Quit()
        logger.info("Canape quit")

    def recorder_status(self):
        """ Check recorder status """
        return self.CANape.Recorders.Item(1).State
