import time
import clr
import HTML_Logger
#please do not import clr library with pip install clr; instead use pip install pythonnet; if you have installed clr please uninstall it with pip uninstall clr

# Import required types
clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Implementation.Testbench.dll")
clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Implementation.TestbenchFactory.dll")
clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Interfaces.dll")

from ASAM.XIL.Implementation.TestbenchFactory.Testbench import TestbenchFactory
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import FloatValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import IntValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import UintValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import StringValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import VectorValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import FloatVectorValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import IntVectorValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import UintVectorValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import StringVectorValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import MatrixValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import FloatMatrixValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import IntMatrixValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import UintMatrixValue
from ASAM.XIL.Implementation.Testbench.Common.ValueContainer import StringMatrixValue

from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IFloatValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IIntValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IBaseValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IStringValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IVectorValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IFloatVectorValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IIntVectorValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IStringVectorValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IMatrixValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IFloatMatrixValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IIntMatrixValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IUintMatrixValue
from ASAM.XIL.Interfaces.Testbench.Common.ValueContainer import IStringMatrixValue


class XIL_API_Handler(object):
    factory = None
    maPort = None
    testBench = None
    temp_str = None
    def __init__(self):
        self.factory = TestbenchFactory()
        self.testBench = self.factory.CreateVendorSpecificTestbench("Vector", "CANoe64", "2.1.0")

        # Instantiate a model access port and configure it
        print("Creating the MA port")
        self.maPort = self.testBench.MAPortFactory.CreateMAPort("Python MA Port")
        self.maPort.Configure(self.maPort.LoadConfiguration(r"VectorMAPortConfig.xml"), True)

    def Open_Connection(self):
        self.factory = TestbenchFactory()
        self.testBench = self.factory.CreateVendorSpecificTestbench("Vector", "CANoe64", "2.1.0")

        # Instantiate a model access port and configure it
        print("Creating the MA port")
        self.maPort = self.testBench.MAPortFactory.CreateMAPort("Python MA Port")
        self.maPort.Configure(self.maPort.LoadConfiguration(r"VectorMAPortConfig.xml"), True)
    # Read a variable
    def Read_CANoe_Symbol(self, namespace, name):
        if namespace != "":
            temp_str = namespace + "::" + name
        else:
            temp_str = name
        #print("Reading variable "+temp_str)
        temp_value = (self.maPort.Read(temp_str))
        read_value = temp_value.__raw_implementation__
        read_value = read_value.Value
        #print("Value of the variable is : " + str(read_value))
        return read_value
        #time.sleep(.25)

    # Write a variable
    def Write_CANoe_Symbol(self, namespace, name,value):

        if namespace!="":
            temp_str = namespace + "::" + name
        else:
            temp_str = name
        #self.maPort.Write(temp_str, StringValue(value))
        #self.maPort.Write(temp_str, UintValue(int(value)))
        print("Writing variable "+temp_str+" to value : "+str(value))
        try:
            self.maPort.Write(temp_str, FloatValue(float(value)))
        except:
            try:
                self.maPort.Write(temp_str, IntValue(int(value)))
            except:
                try:
                    self.maPort.Write(temp_str, UintValue(int(value)))
                except:
                    self.maPort.Write(temp_str, StringValue(value))
        #time.sleep(.1)

    def Read_Canoe_ArraySymbol(self, namespace, name):
        if namespace != "":
            temp_str = namespace + "::" + name
        else:
            temp_str = name

        try:
            temp_value = IFloatVectorValue(self.maPort.Read(temp_str))
        except:
            try:
                temp_value = IIntVectorValue(self.maPort.Read(temp_str))
            except:
                temp_value = IStringVectorValue(self.maPort.Read(temp_str))
        read_value = temp_value.__raw_implementation__
        read_value = read_value.Value

        ret_list = []
        for el in read_value:
            ret_list.append(el)
        # print("Reading variable "+temp_str)
        # print("Value of the variable is : " + str(ret_list))
        return ret_list

    # Write a vector variable (array)
    def Write_Canoe_ArraySymbol(self, namespace, name, value):
        if namespace != "":
            temp_str = namespace + "::" + name
        else:
            temp_str = name
        # print("Writing variable "+temp_str+" to value : "+str(value))
        try:
            self.maPort.Write(temp_str, FloatVectorValue(value))
        except:
            try:
                self.maPort.Write(temp_str, IntVectorValue(value))
            except:
                try:
                    self.maPort.Write(temp_str, UintVectorValue(value))
                except:
                    self.maPort.Write(temp_str, StringVectorValue(value))

    def StartSimulation(self):
        self.maPort.StartSimulation()

    def StopSimulation(self):
        self.maPort.StopSimulation()

    def Disconnect(self):
        print("Disconnecting XIL API")
        self.maPort.Disconnect()

    def Dispose(self):
        self.maPort.Dispose()
        # Shut the port down
        print("Shutting down the MA port")
    def Do_Nothing(self):
        pass

    def GetSignal(self, namespace, name, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Get Signal function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        try:
            read_signal_value = self.Read_CANoe_Symbol(namespace, name)
            HTML_Logger.ReportYellowMessage("Signal " + namespace + " : " + name + "  value = " + str(read_signal_value), silent_flag)  # yellow colour
            HTML_Logger.ReportWhiteMessage("\n", silent_flag)
            self.ReportTestStepPass(" -> PASSED", silent_flag)
        except:
            read_signal_value = 0xFFFFFFFFFFFFFF  # invalid value
            self.ReportTestStepFail(" -> FAILED", silent_flag)
        return read_signal_value

    def GetSignal_Array(self, namespace, name, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("===========================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Get Signal Array Array function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("===========================================", silent_flag)
        try:
            read_signal_value = self.Read_Canoe_ArraySymbol(namespace, name)
            HTML_Logger.ReportYellowMessage("Signal " + namespace + " : " + name + "  value = " + str(read_signal_value),silent_flag)  # yellow colour
            HTML_Logger.ReportWhiteMessage("\n", silent_flag)
            self.ReportTestStepPass(" -> PASSED",silent_flag)
        except:
            read_signal_value= 0xFFFFFFFFFFFFFF #invalid value
            self.ReportTestStepFail(" -> FAILED",silent_flag)
        return read_signal_value

    def SetSignal(self, namespace, name, value, delay_after_set=0.1, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Set Signal function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportYellowMessage("Set Signal " + namespace + " : " + name + " to value " + str(value), silent_flag)  # yellow colour
        try:
            self.Write_CANoe_Symbol(namespace, name, value)
            self.ReportTestStepPass(" -> PASSED", silent_flag)
        except:
            self.ReportTestStepFail(" -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)
        time.sleep(delay_after_set)

    def SetSignal_Array(self, namespace, name, value, delay_after_set=0.1, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Set Signal function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportYellowMessage("Set Signal " + namespace + " : " + name + " to value " + str(value), silent_flag)  # yellow colour

        if (isinstance(value,list) == True):    #IF argument value is list (normally it is but if used from Robot Framework then its a string
            try:
                self.Write_Canoe_ArraySymbol(namespace, name, value)
                self.ReportTestStepPass(" -> PASSED", silent_flag)
            except:
                self.ReportTestStepFail(" -> FAILED", silent_flag)
        else:   #convert string argument value to list
            value=value.replace("[","")
            value=value.replace("]", "")
            value=value.replace("{", "")
            value=value.replace("}", "")
            res_list = value.split(",")
            res_list_float = []
            for el in res_list:
                res_list_float.append(float(el))
                #HTML_Logger.ReportYellowMessage(el) debug
            try:
                self.Write_Canoe_ArraySymbol(namespace, name, res_list_float)
                self.ReportTestStepPass(" -> PASSED", silent_flag)
            except:
                self.ReportTestStepFail(" -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)
        time.sleep(delay_after_set)


    def SetCheckSignal(self, namespace, name, value, delay_after_set=0.1, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Set Signal function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("=============================", silent_flag)
        HTML_Logger.ReportYellowMessage("Set Signal " + namespace + " : " + name + " to value " + str(value),  silent_flag)  # yellow colour
        try:
            self.Write_CANoe_Symbol(namespace, name, value)
            self.ReportTestStepPass(" -> PASSED", silent_flag)
        except:
            self.ReportTestStepFail(" -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)
        time.sleep(delay_after_set)
        self.CheckSignal(namespace, name, value, silent_flag)

    def CheckSignal(self, namespace, name, expected_value, silent_flag="false"):
        read_signal_value = self.Read_CANoe_Symbol(namespace, name)
        HTML_Logger.ReportWhiteMessage("===============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Check Signal function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("===============================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Expected Value = " + str(expected_value), silent_flag)
        HTML_Logger.ReportWhiteMessage("Real Value = " + str(read_signal_value), silent_flag)
        try:    #for numbers    (in Robot Framework all parameters are strings)
            if (float(expected_value) == read_signal_value):
                self.ReportTestStepPass("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> PASSED", silent_flag)
            else:
                self.ReportTestStepFail("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED", silent_flag)
        except:     #for strings
            if (expected_value == read_signal_value):
                self.ReportTestStepPass("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> PASSED", silent_flag)
            else:
                self.ReportTestStepFail("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)

    def AwaitValueMatch(self, namespace, name, expected_value, timeout, silent_flag="false"):
        #in Robot Framework all parameters are strings -> thats why I convert timeout to integer (it comes as string)
        number_of_checks = int(int(timeout) / 0.010)  # refresh rate = 10ms
        HTML_Logger.ReportWhiteMessage("====================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Await Value Match function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("====================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Expected Value : " + namespace + " : " + name + " = " + str(expected_value) + "  (within time (s) : " + str(timeout) + ")", silent_flag)
        try:  # for numbers    (in Robot Framework all parameters are strings)
            flag_value_received = 0
            for current_check in range(number_of_checks):
                read_signal_value = self.Read_CANoe_Symbol(namespace, name)
                if (float(expected_value) == read_signal_value):
                    self.ReportTestStepPass("Value received after time (s) :   " + str(current_check * 0.050) + " -> PASSED", silent_flag)
                    flag_value_received = 1
                    break
                time.sleep(0.010)
            if (flag_value_received == 0):
                self.ReportTestStepFail("Expected value NOT received within expected time -> FAILED", silent_flag)
                self.ReportTestStepFail("Received value : "+str(read_signal_value), silent_flag)
        except:     #for strings
            flag_value_received = 0
            for current_check in range(number_of_checks):
                read_signal_value = self.Read_CANoe_Symbol(namespace, name)
                if (expected_value == read_signal_value):
                    self.ReportTestStepPass("Value received after time (s) :   " + str(current_check * 0.050) + " -> PASSED", silent_flag)
                    flag_value_received = 1
                    break
                time.sleep(0.010)
            if (flag_value_received == 0):
                self.ReportTestStepFail("Expected value NOT received within expected time -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)

    def WaitForSignalInRange(self, namespace, name, expected_lower_value, expected_higher_value, timeout, silent_flag="false"):
        #in Robot Framework all parameters are strings -> thats why I convert timeout to integer (it comes as string)
        number_of_checks = int(int(timeout) / 0.050)  # refresh rate = 50ms
        HTML_Logger.ReportWhiteMessage("=======================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("WaitForSignalInRange function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("=======================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("Expected Value : " + namespace + " : " + name + " between " + str(expected_lower_value) + " and " + str(expected_higher_value) + "  (within time (s) : " + str(timeout) + ")", silent_flag)
        try:  # for numbers    (in Robot Framework all parameters are strings)
            flag_value_received = 0
            for current_check in range(number_of_checks):
                read_signal_value = self.Read_CANoe_Symbol(namespace, name)
                if (read_signal_value <= float(expected_higher_value) and read_signal_value >= float(expected_lower_value)):
                    self.ReportTestStepPass("Value received after time (s) :   " + str(current_check * 0.050) + " -> PASSED", silent_flag)
                    flag_value_received = 1
                    break
                time.sleep(0.050)
            if (flag_value_received == 0):
                self.ReportTestStepFail("Expected value NOT received within expected time -> FAILED", silent_flag)
                self.ReportTestStepFail("Received value : " + str(read_signal_value), silent_flag)
        except:     #for strings
            flag_value_received = 0
            for current_check in range(number_of_checks):
                read_signal_value = self.Read_CANoe_Symbol(namespace, name)
                if (read_signal_value <= expected_higher_value and read_signal_value >= expected_lower_value):
                    self.ReportTestStepPass("Value received after time (s) :   " + str(current_check * 0.050) + " -> PASSED", silent_flag)
                    flag_value_received = 1
                    break
                time.sleep(0.050)
            if (flag_value_received == 0):
                self.ReportTestStepFail("Expected value NOT received within expected time -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)

    def ReportTestStepPass(self, string, silent_flag="false"):
        HTML_Logger.ReportGreenMessage(string, silent_flag)  # green colour

    def ReportTestStepFail(self, string, silent_flag="false"):
        HTML_Logger.ReportRedMessage(string, silent_flag)

    def TestWaitForTimeout(self, time_ms, silent_flag="false"):
        HTML_Logger.ReportWhiteMessage("======================================", silent_flag)
        HTML_Logger.ReportWhiteMessage("TestWaitForTimeout function triggered", silent_flag)
        HTML_Logger.ReportWhiteMessage("======================================", silent_flag)
        HTML_Logger.ReportYellowMessage("Time Delay applied : " + str(time_ms) + " (ms)", silent_flag)
        try:
            time.sleep(float(time_ms) / 1000)
            #self.ReportTestStepPass(" -> PASSED", silent_flag)
        except:
            self.ReportTestStepFail(" -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)

    def TestReportHeader(self, string):
        #HTML_Logger.ReportWhiteMessage("==============================================================================================")
        HTML_Logger.ReportWhiteMessage("==============================================================================================")
        HTML_Logger.ReportWhiteMessage("=        " + string)
        #HTML_Logger.ReportWhiteMessage("==============================================================================================")
        HTML_Logger.ReportWhiteMessage("==============================================================================================")
        HTML_Logger.ReportWhiteMessage("\n")

    def Set_Ego_Vehicle_Velocity(self, ego_speed):
        temp_val = float(ego_speed)
        self.SetSignal("hil_drv","target_velocity",temp_val)
        #self.WaitForSignalInRange("hil_hvm","velocity_x", temp_val-1,temp_val+1,25)
        self.TestWaitForTimeout(500)

    def Activate_ACC_Cus(self):
        #val1 = self.GetSignal("hil_drv","hmi_btn_adas_acc::pressed")
        #2 - pressed
        #1 - not pressed
        self.SetSignal("hil_drv", "hmi_btn_adas_acc",2)
        self.TestWaitForTimeout(500);
        #val2=capl.GetSignal("hil_drv::hmi_btn_adas_acc","not_pressed")
        self.SetSignal("hil_drv", "hmi_btn_adas_acc",1)
        self.TestWaitForTimeout(500);

    def Check_ACC_Status_Cus(self):
        #1 - active
        #0 - not active
        val1 = self.GetSignal("hil_adas","hmi_display_adas_acc_status")
        #val2 = capl.GetSignal("hil_adas::hmi_display_adas_acc_status","active")
        if (val1 == 1): #Check Status ACC
            self.ReportTestStepPass("ACC is active");
        else:
            self.ReportTestStepFail("ACC is not active");

        self.TestWaitForTimeout(200);

    def ShortPress_ACC_SetPlus_Cus(self):
        #5 - plus button pressed
        #4 - minus button pressed
        #0 - not pressed
        #val1=capl.GetSignal("hil_drv::hmi_btn_cc::set_plus","")
        self.SetSignal("hil_drv","hmi_btn_cc",5)
        self.TestWaitForTimeout(1000)
        #val2 = capl.GetSignal("hil_drv::hmi_btn_cc::not_pressed", "")
        self.SetSignal("hil_drv","hmi_btn_cc",0)
        self.TestWaitForTimeout(300)

    def Check_API_Connection(self):
        counter = 0
        for i in range(50):
            value_1 = self.GetSignal("", "hil_ctrl::global_counter", "true")
            time.sleep(0.002)
            value_2 = self.GetSignal("", "hil_ctrl::global_counter","true")
            time.sleep(0.002)
            if (value_1==value_2):
                self.ReportTestStepFail("API Communication Check : FAILED")
                return("FAILED")
            else:
                self.ReportTestStepPass("API Communication Check : PASSED")
                return ("PASSED")

#code debugging from here
#obj_XIL = XIL_API_Handler()
#capl.Testcase_Start("TEST REPORT : Python ACC Test with ADAS HIL 2.xx", "CANoePy 1.1", filename="temp.html") #create the HTML report
#obj_XIL.SetSignal("", "hil_ctrl/abort_message", "qwerty")
#obj_XIL.Write_CANoe_Symbol("hil_ctrl", "hil_mode", 4)
#obj_XIL.AwaitValueMatch("hil_ctrl", "init_cm_done",    1, 10)
#obj_XIL.SetSignal_Array("", "Classe_Obj_Sim/obj_ctrl.obj_target_v_long", [112,2,3,4,5,6,7,8,9,10222,11])  # press the STOP SIM button to END scenario/test
#obj_XIL.GetSignal_Array("", "VVN/var1")