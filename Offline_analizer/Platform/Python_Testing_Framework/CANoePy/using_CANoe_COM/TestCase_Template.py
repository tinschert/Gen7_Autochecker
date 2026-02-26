#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface

import HTML_Logger
import CAPL_Wrapper_Functions as capl
import Test_Functions as tf

def TestCase_Template():
    capl.Testcase_Start("TEST REPORT : Python ACC Test with ADAS HIL 2.15", "CANoePy 1.0") #create the HTML report

    HTML_Logger.TestReportHeader("Example : CANoePy v1.0 POC ACC Test with ADAS HIL 2.15")
    HTML_Logger.TestReportHeader("Tester : Ventsislav Negentsov")
    HTML_Logger.TestReportHeader("TestCaseID : 123456789")
    HTML_Logger.TestReportHeader("DefectID : 123456789")


    #===========================================================================================================================================================================
    #TEST STARTS HERE:
    capl.SetSignal("hil_ctrl","configuration_od",2) #set configuration = 5
    capl.CheckSignal("hil_ctrl","configuration_od",2) #check configuration == 5
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "hil_mode", 4)   #set HIL mode to CarMaker
    capl.CheckSignal("hil_ctrl", "hil_mode", 4) #check HIL mode == 4
    capl.TestWaitForTimeout(1000)
    capl.SetSignal_String("Customer_specific", "cm_scenario", "ACC_CountryRoad_Test")   #fill the scenario name
    capl.TestWaitForTimeout(1000)
    capl.CheckSignal_String("Customer_specific", "cm_scenario", "ACC_CountryRoad_Test")  #check if scenario field is populated
    capl.AwaitValueMatch("hil_ctrl","init_cm_done",1,60)    #wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("Customer_specific", "load_scenario", 1) #press the LOAD SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.SetSignal("Customer_specific", "load_scenario", 0) #release the LOAD SCENARIO button
    capl.AwaitValueMatch("hil_ctrl", "cm_ready_to_start", 1, 60)    #wait green LED
    capl.TestWaitForTimeout(1000)
    capl.SetSignal("hil_ctrl", "scenario_start", 1) #press the START SCENARIO button
    capl.TestWaitForTimeout(500)
    capl.SetSignal("hil_ctrl", "scenario_start", 0) #release the START SCENARIO button
    capl.TestWaitForTimeout(1000)
    capl.AwaitValueMatch("CarMaker/SC", "State", 8, 70)

    #add here some more set signal functions to activate ACC
    #capl.SetSignal()
    #add here some more check functions to check if ACC works
    #capl.CheckSignal()

    capl.TestWaitForTimeout(20000)      #wait 20 seconds for scenario to execute

    capl.SetSignal("Customer_specific", "cm_stopsim", 1)       #press the STOP SIM button to END scenario/test
    #capl.SetSignal("Customer_specific", "cm_stopsim", 0)  # press the STOP SIM button to END scenario/test


TestCase_Template()
