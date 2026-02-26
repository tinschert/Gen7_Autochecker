# -*- coding: utf-8 -*-
# @file logging_config.py
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


import logging
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = ColoredFormatter('%(log_color)s[%(asctime)s] [%(levelname)s] [%(filename)s] [%(message)s]')
#formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] [%(message)s]')

file_handler = logging.FileHandler('Debug.log',mode="w+")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)