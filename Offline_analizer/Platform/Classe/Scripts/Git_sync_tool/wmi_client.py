# -*- coding: utf-8 -*-
# @file wmi_client.py
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


import wmi
from socket import getfqdn
import shutil
import pythoncom


class RemoteConnection:
    """ """
    def __init__(self, host):
        pythoncom.CoInitialize()
        #self.host = 'FE-Z1R59.lr.de.bosch.com'
        self.host = host
        self.username = r'DE\SYA9LR'
        self.password = 'Adassystestereet#1'
        
    def connect_to_host(self):
        """ """
        global connection
        try:
            print(f"Establishing connection to {self.host}")
            connection = wmi.WMI(self.host, user=self.username, password=self.password)
            SW_SHOWNORMAL = 1
            process_startup = connection.Win32_ProcessStartup.new()
            process_startup.ShowWindow = SW_SHOWNORMAL
            print(f"Connection established to {self.host}")
            return process_startup
        except wmi.x_wmi as e:
            print("Your Username and Password of " + getfqdn(self.host) + " are wrong.")
            raise e

    def run_command(self, command, process_startup):
        """
        

        Args:
          command: 
          process_startup: 

        Returns:

        """
        try:
            print(f"Starting server on {self.host}")
            connection.Win32_Process.Create(CommandLine=command, ProcessStartupInformation=process_startup)
        except wmi.x_wmi as e:
            print(f"Command could not be executed on remote machine --> {e}.")
            raise e

#     def copylog(self):
#         shutil.copyfile(r'\\FE-Z1R59.lr.de.bosch.com\Cloe_share_measurements\test.txt', r'D:\Temp\test.txt')
# 
# 
#to_run = 'cmd.exe /c ipconfig'
# 

# #command = 'cmd.exe /c mkdir D:\\Plamen'
# x = RemoteConnection('FE-Z1R59.lr.de.bosch.com')
# x.connect_to_host()
# x.run_command(to_run)
# x.copylog()

# try:
#     connection.Win32_Process.Create(CommandLine='cmd.exe /c copy D:\\Plamen\\test.png D:\\')
# except:
#     print("Brada")