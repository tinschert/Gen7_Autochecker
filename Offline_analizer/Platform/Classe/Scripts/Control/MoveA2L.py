# -*- coding: utf-8 -*-
# @file MoveA2L.py
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


import glob
import os
import shutil
from os import walk
from logging_config import logger


class A2L:
    """ Main class """

    destination_path = f'D:\\ADAS_HIL\\CustomerPrj\\XCP\\A2L\\'

    a2l_add_info = """        /begin EVENT
          "STIMSTIM1"
          "STIMSTIM1"
          0x1C
          STIM
          0xFF
          0x01
          0x07
          0x00
        /end EVENT
        /begin EVENT
          "DAQSTIM1"
          "DAQSTIM1"
          0x1B
          DAQ
          0xFF
          0x01
          0x07
          0x00
        /end EVENT\n"""

    def __init__(self,src_path,dst_path=destination_path,a2l_info=a2l_add_info):
        self.src_path = src_path
        self.dst_path = dst_path
        self.a2l_info = a2l_info

    def move_a2l(self):
        """ Function ot move a2l to defined location"""

        corners = ['CRadarFL.a2l', 'CRadarRR.a2l', 'CRadarRL.a2l', 'CRadarFR.a2l']
        
        a2l_files = glob.glob(self.src_path + "*.a2l")

        if len(a2l_files) != 0:
            for a2lf in a2l_files:
                if os.path.exists(self.src_path + "RadarRear.a2l"):
                    for corner in corners:
                        shutil.copy(a2lf, self.dst_path)
                        os.rename(self.dst_path + 'RadarRear.a2l', self.dst_path + corner)
                else:
                    shutil.copy(a2lf, self.dst_path)

            logger.info('Successfully copied all .a2l files!')
        else:
            logger.error('No .a2l file exists in the current CTC')
            raise Exception('No .a2l file exists in the current CTC')

    def list_a2l(self):
        """ List all available a2l files in defined directory"""
        f = []
        for (dirpath, dirnames, filenames) in walk(self.dst_path):
            f.extend(filenames)
            if not f:
                logger.error("No a2l files available")
                raise Exception("No a2l files available")
            else:
                logger.info(f'Available a2l files in {dirpath} --> {f}')
                return f

    def fix_a2l(self, a2l_files):
        """
        Add missing DAQ information in list of a2l files
        Args:
          a2l_files (list): List of a2l files to be update

        Returns:
        """
        logger.info("Starting A2L fixing ...")
        for a2l in a2l_files:
            with open(f"{self.dst_path}{a2l}", 'r+') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('        /end TIMESTAMP_SUPPORTED'):
                        lines[i] = lines[i] + self.a2l_info
                        f.seek(0)
                if "        /end TIMESTAMP_SUPPORTED" not in lines:
                    logger.error("Missing information is A2L file.Please check the integrity of AL2")
                    raise ValueError("Missing information is A2L file.Please check the integrity of AL2")
                else:
                    for line in lines:
                        f.write(line)
                    logger.info(f"A2L {a2l} fixed.")

    def change_ip(self, a2l_files):
        """
        Change IP address in a list of a2l files

        Args:
          a2l_files (list): A2l files to be updated
        Returns:
        """

        ip_address = {"RadarFC.a2l": '        ADDRESS "192.168.0.10"\n',
                      "RadarFL.a2l": '        ADDRESS "192.168.0.5"\n'}

        logger.info("Starting IP change ...")
        for a2l in a2l_files:
            if a2l in ip_address:
                ip = ip_address[a2l]
                with open(f"{self.dst_path}{a2l}", 'r+') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith('        ADDRESS "192.168.0'):
                            lines[i] = ip
                            f.seek(0)
                    for line in lines:
                        f.write(line)
            logger.info(f"IP address of {a2l} updated.")




