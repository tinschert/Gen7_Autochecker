# This script requires pythonnet (can be installed via "pip install pythonnet")
# Please do not import clr library with pip install clr; instead use pip install pythonnet; if you have installed clr please uninstall it with pip uninstall clr
# Add assembly references (if XIL API has been installed to a different location, these need to be adapted)
import clr
import os

clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Implementation.Testbench.dll")
clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Implementation.TestbenchFactory.dll")
clr.AddReference(
    "C:\\Program Files (x86)\\ASAM e.V\\ASAM AE XIL API Standard Assemblies 2.1.0\\bin\\ASAM.XIL.Interfaces.dll")

# Import required types
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

# Additional Python includes
import time

# Instantiate Vector CANoe test bench for XIL API version 2.1.0
# Note: if using 32 bit Python, change "CANoe64" to "CANoe32" (this has nothing
# to do with the CANoe version but the python interpreter version you use!)
factory = TestbenchFactory()
testBench = factory.CreateVendorSpecificTestbench("Vector", "CANoe64", "2.1.0")

# Instantiate a model access port and configure it
def Generate_List_Of_Files(root):
    listOfFile = os.listdir(root)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(root, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + Generate_List_Of_Files(fullPath)
        else:
            allFiles.append(fullPath)
    #print(allFiles)
    return allFiles

def Find_File_Full_Path(name_to_find, root):
    os.chdir(root)
    for i in range(10): #search upto 10 folder levels up
        #print(i)
        list_of_files = Generate_List_Of_Files(os.getcwd())
        for el in list_of_files:
            if el.find(name_to_find)>=0:
                print(el)
                return el
        os.chdir("..")

current_directory = os.getcwd()
xml_file_path=Find_File_Full_Path('VectorMAPortConfig.xml', current_directory)

print("Creating the MA port")
maPort = testBench.MAPortFactory.CreateMAPort("Python MA Port")
maPort.Configure(maPort.LoadConfiguration(xml_file_path), True)
#maPort.StartSimulation()

# Read a scalar variable
def Read_Canoe_Symbol(namespace, name):
    if namespace != "":
        temp_str = namespace + "::" + name
    else:
        temp_str = name
    #print("Reading variable "+temp_str)
    temp_value = (maPort.Read(temp_str))
    read_value = temp_value.__raw_implementation__
    read_value = read_value.Value
    #print("Value of the variable is : " + str(read_value))
    return read_value

# Write a scalar variable
def Write_Canoe_Symbol(namespace, name,value):
    if namespace!="":
        temp_str = namespace + "::" + name
    else:
        temp_str = name
    #print("Writing variable "+temp_str+" to value : "+str(value))
    try:
        maPort.Write(temp_str, FloatValue(value))
    except:
        try:
            maPort.Write(temp_str, IntValue(value))
        except:
            try:
                maPort.Write(temp_str, UintValue(value))
            except:
                maPort.Write(temp_str, StringValue(value))

# Read a vector variable (array)
def Read_Canoe_ArraySymbol(namespace, name):
    if namespace != "":
        temp_str = namespace + "::" + name
    else:
        temp_str = name

    try:
        temp_value = IFloatVectorValue(maPort.Read(temp_str))
    except:
        try:
            temp_value = IIntVectorValue(maPort.Read(temp_str))
        except:
                temp_value = IStringVectorValue(maPort.Read(temp_str))
    read_value = temp_value.__raw_implementation__
    read_value = read_value.Value

    ret_list = []
    for el in read_value:
        ret_list.append(el)
    #print("Reading variable "+temp_str)
    #print("Value of the variable is : " + str(ret_list))
    return ret_list

# Write a vector variable (array)
def Write_Canoe_ArraySymbol(namespace, name,value):
    if namespace!="":
        temp_str = namespace + "::" + name
    else:
        temp_str = name
    #print("Writing variable "+temp_str+" to value : "+str(value))
    try:
        maPort.Write(temp_str, FloatVectorValue(value))
    except:
        try:
            maPort.Write(temp_str, IntVectorValue(value))
        except:
            try:
                maPort.Write(temp_str, UintVectorValue(value))
            except:
                maPort.Write(temp_str, StringVectorValue(value))

def StartSimulation():
    maPort.StartSimulation()

def StopSimulation():
    maPort.StopSimulation()

def Disconnect():
    print("Disconnecting XIL API")
    maPort.Disconnect()

def Dispose():
    maPort.Dispose()
    # Shut the port down
    print("Shutting down the MA port")

def Extract_CANoe_Symbol_Database():
    list_of_symbols=[]
    list_of_symbols.clear()
    for name in maPort.VariableNames:
        list_of_symbols.append(name)
    return list_of_symbols



#examples:
#floatValue = IFloatValue(maPort.Read("Test::Variable1"))
#ReadSysVar("Test::Variable1")
#WriteSysVar("Test::Variable2",5)
#maPort.Write("Test::Variable2", IntValue(5))
#StartSimulation()
#StopSimulation()
#Disconnect()
#Dispose()