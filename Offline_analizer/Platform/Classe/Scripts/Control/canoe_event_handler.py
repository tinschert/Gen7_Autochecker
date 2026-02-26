# -*- coding: utf-8 -*-
# @file canoe_event_handler.py
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


class SystemVariablesHandler:
    """Handler for CANoe var events"""

    def __init__(self):
        self.Changed = False

    def OnChange(self, value):
        """
        triggers when a event occurs and set changed to True

        Args:
          value: event type


        """
        self.Changed = True


class TestConfigurationEventHandler:
    """
    A handler for events that come from a test configuration
    """
    
    def __init__(self):
        self.testConfigStarted = False
        
    def OnStart(self):
        """
        Called when a test configuration is
        started.

        """
        self.testConfigStarted = True
        
class MeasurementEventHandler:
    """
    A handler for events that come from a
    measurement
    """
    
    def __init__(self):
        self.measurementStarted = False
        self.measurementStopped = False
        
    def OnStart(self):
        """
        Called when a measurement is
        started.
        """
        self.measurementStarted = True
        
    def OnStop(self):
        """
        Called when a measurement is
        stopped.
        """
        self.measurementStopped = True


class ModuleEventHandler:
    """ handler for test nodules start and stop"""
    def __init__(self):
        self.testModuleStarted = False
        self.testModuleStopped = False

    def OnStop(self, reason):  
        """
        on stop event actions

        Args:
          reason: reason for stop

        """
        self.testModuleStopped = True   
        return                      

    def OnStart(self):   
        """ handler for test module start"""
        self.testModuleStarted = True  
        return


class ReportEventHandler:
    """ test report handler"""
    def __init__(self):
        self.statusReportGenerated = False 

    def OnReportGenerated(self, success, sourceFullName, generatedFullName):
        """
        called when test report is generated

        Args:
          success:
          sourceFullName (str):
          generatedFullName (str):

        Returns:

        """
        print("TestModule - Report Generated [" + str(success) + "]: " + str(sourceFullName) + " -> " + str(generatedFullName))   
        self.statusReportGenerated = True  
        return