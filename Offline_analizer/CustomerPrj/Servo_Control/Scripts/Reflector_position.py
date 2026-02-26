# -*- coding: utf-8 -*-
# @file Reflector_position.py
# @author ADAS_HIL_TEAM
# @date 03-09-2023

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


import maestro
import time
servo = maestro.Controller('COM5')
servo.setAccel(0,10)      #set servo 0 acceleration to 4
servo.setTarget(0,5000)  #set servo to move to center position
servo.setSpeed(0,100)    #set speed of servo 1
x = servo.getPosition(0) #get the current position of servo 1
servo.close()