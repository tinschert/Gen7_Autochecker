#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an library implementing the common CAPL functions using Python COM API of CANoe

import CANoe_COM_Automation
import HTML_Logger
import time

canoeClient = CANoe_COM_Automation.CANoeClient()


# Examples for CANoe API function calls     --> implemented in CANoe_COM_Automation.py by Ventsislav Negentsov
# string = canoeClient.getSysVarValue("hil_custom_scripts","string_data_received_from_Python")
# val1 = canoeClient.getSysVarValue("hil_custom_scripts","int_data_received_from_Python")
# HTML_Logger.ReportInfoMsg("Data received from CANoe via COM : "+string)
# HTML_Logger.ReportInfoMsg("Data received from CANoe via COM : "+str(val1))
# canoeClient.setVariableToValue("hil_custom_scripts","string_data_received_from_Python","Hello CANoe, my name is Python and I call you from your COM object !!!")
# canoeClient.setVariableToValue("hil_custom_scripts","int_data_received_from_Python",666)
# canoeClient = CANoeClient()
# canoeClient.openConfiguration(r'D:\ADAS_Develop\RBS_OD.cfg')
# canoeClient.set_logging_path()
# canoeClient.addXCPConfiguration(r'D:\test_canoe_multiecu_hil_Test\Functions\XCP\XCP_PSA_FrontRadar.xcpcfg')
# canoeClient.startMeasurement()
# canoeClient.executeTestsInTestConfiguration("SystemIntegration")
# canoeClient.setVariableToValue("hil_ctrl","hil_mode",2)
# canoeClient.getSysVarValue("hil_custom_scripts","int_data_received_from_Python")
# canoeClient.stopMeasurement()

def GetSignal(namespace, name):
    HTML_Logger.ReportInfoMsg("=============================")
    HTML_Logger.ReportInfoMsg("Get Signal function triggered")
    HTML_Logger.ReportInfoMsg("=============================")
    try:
        read_signal_value=canoeClient.getSysVarValue(namespace, name)
        HTML_Logger.ReportWarnMsg("Signal " + namespace + " : " + name + "  value = " + str(read_signal_value))  # yellow colour
        HTML_Logger.ReportInfoMsg("\n")
        ReportTestStepPass(" -> PASSED")
    except:
        ReportTestStepFail(" -> FAILED")
    return read_signal_value

def SetSignal(namespace, name, value):
    HTML_Logger.ReportInfoMsg("=============================")
    HTML_Logger.ReportInfoMsg("Set Signal function triggered")
    HTML_Logger.ReportInfoMsg("=============================")
    HTML_Logger.ReportWarnMsg("Set Signal "+namespace+" : "+name+" to value "+str(value)) #yellow colour
    try:
        canoeClient.setVariableToValue(namespace, name, value)
        ReportTestStepPass(" -> PASSED")
    except:
        ReportTestStepFail(" -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def SetSignal_String(namespace, name, value):
    HTML_Logger.ReportInfoMsg("=============================")
    HTML_Logger.ReportInfoMsg("Set Signal function triggered")
    HTML_Logger.ReportInfoMsg("=============================")
    HTML_Logger.ReportWarnMsg("Set Signal "+namespace+" : "+name+" to value "+value) #yellow colour
    try:
        canoeClient.setVariableToValue(namespace, name, value)
        ReportTestStepPass(" -> PASSED")
    except:
        ReportTestStepFail(" -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def CheckSignal(namespace, name, expected_value):
    read_signal_value = canoeClient.getSysVarValue(namespace,name)
    HTML_Logger.ReportInfoMsg("===============================")
    HTML_Logger.ReportInfoMsg("Check Signal function triggered")
    HTML_Logger.ReportInfoMsg("===============================")
    HTML_Logger.ReportInfoMsg("Expected Value = " + str(expected_value))
    HTML_Logger.ReportInfoMsg("Real Value = " + str(read_signal_value))
    if (expected_value ==read_signal_value):
        ReportTestStepPass("Check Signal "+namespace+" : "+name+" = "+str(expected_value)+"  -> PASSED")
    else:
        ReportTestStepFail("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def CheckSignal_String(namespace, name, expected_value):
    read_signal_value = canoeClient.getSysVarValue(namespace,name)
    HTML_Logger.ReportInfoMsg("===============================")
    HTML_Logger.ReportInfoMsg("Check Signal function triggered")
    HTML_Logger.ReportInfoMsg("===============================")
    HTML_Logger.ReportInfoMsg("Expected Value = " + str(expected_value))
    HTML_Logger.ReportInfoMsg("Real Value = " + str(read_signal_value))
    if (expected_value ==read_signal_value):
        ReportTestStepPass("Check Signal "+namespace+" : "+name+" = "+expected_value+"  -> PASSED")
    else:
        ReportTestStepFail("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def AwaitValueMatch(namespace, name, expected_value, timeout):
    number_of_checks = int(timeout / 0.050) #refresh rate = 50ms
    HTML_Logger.ReportInfoMsg("====================================")
    HTML_Logger.ReportInfoMsg("Await Value Match function triggered")
    HTML_Logger.ReportInfoMsg("====================================")
    HTML_Logger.ReportInfoMsg("Expected Value : " +namespace+" : "+name+" = "+ str(expected_value)+"  (within time (s) : "+str(timeout)+")")
    flag_value_received = 0
    for current_check in range(number_of_checks):
        read_signal_value = canoeClient.getSysVarValue(namespace, name)
        if (expected_value == read_signal_value):
            ReportTestStepPass("Value received after time (s) :   " + str(current_check*0.050) + " -> PASSED")
            flag_value_received = 1
            break
        time.sleep(0.050)
    if (flag_value_received == 0):
        ReportTestStepFail("Expected value NOT received within expected time -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def WaitForSignalInRange(namespace, name, expected_lower_value, expected_higher_value, timeout):
    number_of_checks = int(timeout / 0.050) #refresh rate = 50ms
    HTML_Logger.ReportInfoMsg("=======================================")
    HTML_Logger.ReportInfoMsg("WaitForSignalInRange function triggered")
    HTML_Logger.ReportInfoMsg("=======================================")
    HTML_Logger.ReportInfoMsg("Expected Value : " +namespace+" : "+name+" between "+ str(expected_lower_value)+" and "+str(expected_higher_value)+"  (within time (s) : "+str(timeout)+")")
    flag_value_received = 0
    for current_check in range(number_of_checks):
        read_signal_value = canoeClient.getSysVarValue(namespace, name)
        if (read_signal_value <= expected_higher_value and read_signal_value>=expected_lower_value):
            ReportTestStepPass("Value received after time (s) :   " + str(current_check*0.050) + " -> PASSED")
            flag_value_received = 1
            break
        time.sleep(0.050)
    if (flag_value_received == 0):
        ReportTestStepFail("Expected value NOT received within expected time -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def ReportTestStepPass(string):
    HTML_Logger.ReportDbgMsg(string)    #green colour

def ReportTestStepFail(string):
    HTML_Logger.ReportErrorMsg(string)

def TestWaitForTimeout(time_ms):
    HTML_Logger.ReportInfoMsg("======================================")
    HTML_Logger.ReportInfoMsg("TestWaitForTimeout function triggered")
    HTML_Logger.ReportInfoMsg("======================================")
    HTML_Logger.ReportWarnMsg("Time Delay applied : "+str(time_ms)+" (ms)")
    try:
        time.sleep(time_ms/1000)
        ReportTestStepPass(" -> PASSED")
    except:
        ReportTestStepFail(" -> FAILED")
    HTML_Logger.ReportInfoMsg("\n")

def TestReportHeader(string):
    HTML_Logger.ReportInfoMsg("==============================================================================================")
    HTML_Logger.ReportInfoMsg("==============================================================================================")
    HTML_Logger.ReportInfoMsg("=        "+string)
    HTML_Logger.ReportInfoMsg("==============================================================================================")
    HTML_Logger.ReportInfoMsg("==============================================================================================")
    HTML_Logger.ReportInfoMsg("\n")



