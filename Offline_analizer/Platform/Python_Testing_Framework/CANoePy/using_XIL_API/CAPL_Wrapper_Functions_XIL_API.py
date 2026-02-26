#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 01.Oct.2024
#this is an library implementing the common CAPL functions using ASAM XIL API v2.1
#from inspect import trace
import sys
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")

import CANoe_XIL_API_Automation as XIL_API
import HTML_Logger
import time
from threading import Thread
from matplotlib import pyplot as plt
import os
import pandas as pd
import plotly.express as px
import threading


#global dictionary for trace logging functions
trace_dict = {}
trace_dict.clear()

def Extract_CANoe_Symbols():
    list1=XIL_API.Extract_CANoe_Symbol_Database()
    for el in list1:
        HTML_Logger.ReportWhiteMessage(el)

def GetSignal(namespace, name, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : GetSignal",silent_flag)
    try:
       read_signal_value=XIL_API.Read_Canoe_Symbol(namespace, name)
       HTML_Logger.ReportWhiteMessage("Signal " + namespace + " : " + name + "  value = " + str(read_signal_value),silent_flag)  # yellow colour
       #HTML_Logger.ReportWhiteMessage("\n", silent_flag)
       ReportTestStepPass(" -> PASSED",silent_flag)
    except:
       read_signal_value= 0xFFFFFFFFFFFFFF #invalid value
       ReportTestStepFail(" -> FAILED",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")
    return read_signal_value

def GetSignal_Array(namespace, name, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : GetSignalArray",silent_flag)
    try:
       read_signal_value=XIL_API.Read_Canoe_ArraySymbol(namespace, name)
       HTML_Logger.ReportYellowMessage("Signal " + namespace + " : " + name + "  value = " + str(read_signal_value),silent_flag)  # yellow colour
       HTML_Logger.ReportWhiteMessage("\n", silent_flag)
       ReportTestStepPass(" -> PASSED",silent_flag)
    except:
       read_signal_value= 0xFFFFFFFFFFFFFF #invalid value
       ReportTestStepFail(" -> FAILED",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")
    return read_signal_value

def SetSignal(namespace, name, value, delay_after_set = 0.1, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage('----------------------------------------------------------------------------------------------------------------------------------------------------------------',silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : SetSignal",silent_flag)
    HTML_Logger.ReportYellowMessage("Set Signal "+namespace+" : "+name+" to value "+str(value),silent_flag) #yellow colour
    try:
        XIL_API.Write_Canoe_Symbol(namespace, name, value)
        ReportTestStepPass(" -> PASSED",silent_flag)
    except:
        ReportTestStepFail(" -> FAILED",silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    time.sleep(delay_after_set)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def SetSignal_Array(namespace, name, value, delay_after_set = 0.1, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : SetSignalArray",silent_flag)
    HTML_Logger.ReportYellowMessage("Set Signal "+namespace+" : "+name+" to value "+str(value),silent_flag) #yellow colour
    try:
        XIL_API.Write_Canoe_ArraySymbol(namespace, name, value)
        ReportTestStepPass(" -> PASSED", silent_flag)
    except:
        ReportTestStepFail(" -> FAILED",silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    time.sleep(delay_after_set)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def SetCheckSignal(namespace, name, value, delay_after_set = 0.1, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : SetCheckSignal",silent_flag)
    HTML_Logger.ReportYellowMessage("Set Signal "+namespace+" : "+name+" to value "+str(value),silent_flag) #yellow colour
    try:
        XIL_API.Write_Canoe_Symbol(namespace, name, value)
        ReportTestStepPass(" -> PASSED",silent_flag)
    except:
        ReportTestStepFail(" -> FAILED",silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    time.sleep(delay_after_set)
    CheckSignal(namespace, name, value, silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def CheckSignal(namespace, name, expected_value, silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    read_signal_value = XIL_API.Read_Canoe_Symbol(namespace,name)
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : Check Signal",silent_flag)
    HTML_Logger.ReportWhiteMessage("Expected Value = " + str(expected_value),silent_flag)
    HTML_Logger.ReportWhiteMessage("Real Value = " + str(read_signal_value),silent_flag)
    if (expected_value ==read_signal_value):
        ReportTestStepPass("Check Signal "+namespace+" : "+name+" = "+str(expected_value)+"  -> PASSED",silent_flag)
    else:
        ReportTestStepFail("Check Signal " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED",silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def BackgroundCheck_ValueMatch(namespace, name, expected_value, duration, refresh_rate = 50, silent_flag=False):
        if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
        HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
        HTML_Logger.ReportBlueMessage("Test Step : Background Check : Value Match", silent_flag)
        HTML_Logger.ReportWhiteMessage("refresh rate (ms) = "+ str(refresh_rate), silent_flag)
        HTML_Logger.ReportWhiteMessage("duration     (ms) = "+ str(duration), silent_flag)
        HTML_Logger.ReportWhiteMessage("Background_Check started  ...")
        thread = Thread(target=BackgroundCheck_ValueMatch_threaded_function, args=(namespace, name, expected_value, duration, refresh_rate, silent_flag))
        thread.start()
        #thread.join()
        if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def BackgroundCheck_ValueMatch_threaded_function(namespace, name, expected_value, duration, refresh_rate = 50, silent_flag=False):
    if duration>1000: #wait of 1000s is not a real use case, most probably the user just had mistaken the power/order/accuracy of the parameter
        HTML_Logger.ReportWhiteMessage("WARNING : Maybe you have mistaken the power/order/accuracy of the number - > converted milliseconds to seconds")
        HTML_Logger.ReportWhiteMessage("In VTestStudio the value is in miliseconds, in CANoepy it is seconds")
        duration=duration/1000
    num_of_cycles = int(duration / refresh_rate)
    for i in range(num_of_cycles):
        read_signal_value = XIL_API.Read_Canoe_Symbol(namespace, name)
        HTML_Logger.ReportWhiteMessage("Expected Value = " + str(expected_value), silent_flag)
        HTML_Logger.ReportWhiteMessage("Real Value = " + str(read_signal_value), silent_flag)
        if (expected_value == read_signal_value):
            ReportTestStepPass("Background Check : Value Match : " + namespace + " : " + name + " = " + str(expected_value) + "  -> PASSED", silent_flag)
        else:
            ReportTestStepFail("Background Check : Value Match : " + namespace + " : " + name + " = " + str(expected_value) + "  -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)
        time.sleep(refresh_rate / 1000)

def BackgroundCheck_SignalInRange(namespace, name, expected_lower_value, expected_higher_value, duration, refresh_rate=50, silent_flag=False):
        if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
        HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
        HTML_Logger.ReportBlueMessage("Test Step : Background Check : Signal In Range", silent_flag)
        HTML_Logger.ReportWhiteMessage("refresh rate (ms) = " + str(refresh_rate), silent_flag)
        HTML_Logger.ReportWhiteMessage("duration     (ms) = " + str(duration), silent_flag)
        HTML_Logger.ReportWhiteMessage("Background_Check started  ...")
        thread = Thread(target=BackgroundCheck_SignalInRange_threaded_function, args=(namespace, name, expected_lower_value, expected_higher_value, duration, refresh_rate, silent_flag))
        thread.start()
        #thread.join()
        if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def BackgroundCheck_SignalInRange_threaded_function(namespace, name, expected_lower_value, expected_higher_value, duration, refresh_rate=50,silent_flag=False):
    if duration>1000: #wait of 1000s is not a real use case, most probably the user just had mistaken the power/order/accuracy of the parameter
        HTML_Logger.ReportWhiteMessage("WARNING : Maybe you have mistaken the power/order/accuracy of the number - > converted milliseconds to seconds")
        HTML_Logger.ReportWhiteMessage("In VTestStudio the value is in miliseconds, in CANoepy it is seconds")
        duration=duration/1000
    num_of_cycles = int(duration / refresh_rate)
    for i in range(num_of_cycles):
        read_signal_value = XIL_API.Read_Canoe_Symbol(namespace, name)
        HTML_Logger.ReportWhiteMessage("Expected LOWEST Value = " + str(expected_lower_value), silent_flag)
        HTML_Logger.ReportWhiteMessage("Expected HIGHEST Value = " + str(expected_higher_value), silent_flag)
        HTML_Logger.ReportWhiteMessage("Real Value = " + str(read_signal_value), silent_flag)
        if (read_signal_value>=expected_lower_value) and (read_signal_value<=expected_higher_value):
            ReportTestStepPass("Background Check : Signal In Range : " + namespace + " : " + name + " is between " + str(expected_lower_value) + " and "+ str(expected_higher_value) + "  -> PASSED", silent_flag)
        else:
            ReportTestStepFail("Background Check : Signal In Range : " + namespace + " : " + name + " is between " + str(expected_lower_value) + " and "+ str(expected_higher_value) + "  -> FAILED", silent_flag)
        HTML_Logger.ReportWhiteMessage("\n", silent_flag)
        time.sleep(refresh_rate / 1000)

def Trace_Signal(namespace, name, duration, refresh_rate=50, silent_flag=False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : Trace (log) Signal", silent_flag)
    HTML_Logger.ReportWhiteMessage("signal being traced : " + str(name), silent_flag)
    HTML_Logger.ReportWhiteMessage("refresh rate (ms) = "+ str(refresh_rate), silent_flag)
    HTML_Logger.ReportWhiteMessage("duration     (ms) = "+ str(duration), silent_flag)
    thread = Thread(target=Trace_Signal_threaded_function, args=(namespace, name, duration, refresh_rate, silent_flag))
    thread.start()
    #thread.join()
    HTML_Logger.ReportWhiteMessage("Trace_Signal started  ...")
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def Trace_Signal_threaded_function(namespace, name, duration, refresh_rate=50, silent_flag=False):
    num_of_cycles = int(duration / refresh_rate)
    initial_time = time.time()
    trace_dict.update({str(namespace+name): {"trace_log_list_values": [], "trace_log_list_timestamps": []}})

    for i in range(num_of_cycles):
        read_signal_value = XIL_API.Read_Canoe_Symbol(namespace, name)
        delta_t =  time.time() - initial_time

        #add in the trace dict
        trace_dict[str(namespace+name)]['trace_log_list_values'].append(read_signal_value)
        trace_dict[str(namespace+name)]['trace_log_list_timestamps'].append(delta_t)
        time.sleep(refresh_rate / 1000)

def AwaitValueMatch(namespace, name, expected_value, timeout, silent_flag = False, tolerance = 0.001):
    if timeout>1000: #wait of 1000s is not a real use case, most probably the user just had mistaken the power/order/accuracy of the parameter
        HTML_Logger.ReportWhiteMessage("WARNING : Maybe you have mistaken the power/order/accuracy of the number - > converted milliseconds to seconds")
        HTML_Logger.ReportWhiteMessage("In VTestStudio the value is in miliseconds, in CANoepy it is seconds")
        timeout=timeout/1000
    number_of_checks = int(timeout / 0.050) #refresh rate = 50ms
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : AwaitValueMatch",silent_flag)
    HTML_Logger.ReportWhiteMessage("Expected Value : " +namespace+" : "+name+" = "+ str(expected_value)+"  (within time (s) : "+str(timeout)+")",silent_flag)
    flag_value_received = 0
    for current_check in range(number_of_checks):
        read_signal_value = XIL_API.Read_Canoe_Symbol(namespace, name)
        if (abs(expected_value - read_signal_value)<tolerance):
            HTML_Logger.ReportWhiteMessage("Value received after time (s) :   " + str(current_check*0.050),silent_flag)
            ReportTestStepPass(" -> PASSED", silent_flag)
            flag_value_received = 1
            break
        time.sleep(0.050)
    if (flag_value_received == 0):
        ReportTestStepFail("Expected value NOT received within expected time -> FAILED",silent_flag)
        ReportTestStepFail("Received value : " + str(read_signal_value), silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")
    return flag_value_received

def WaitForSignalInRange(namespace, name, expected_lower_value, expected_higher_value, timeout, silent_flag = False):
    if timeout>1000: #wait of 1000s is not a real use case, most probably the user just had mistaken the power/order/accuracy of the parameter
        HTML_Logger.ReportWhiteMessage("WARNING : Maybe you have mistaken the power/order/accuracy of the number - > converted milliseconds to seconds")
        HTML_Logger.ReportWhiteMessage("In VTestStudio the value is in miliseconds, in CANoepy it is seconds")
        timeout=timeout/1000
    number_of_checks = int(timeout / 0.050) #refresh rate = 50ms
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : WaitForSignalInRange",silent_flag)
    HTML_Logger.ReportWhiteMessage("Expected Value : " +namespace+" : "+name+" between "+ str(expected_lower_value)+" and "+str(expected_higher_value)+"  (within time (s) : "+str(timeout)+")",silent_flag)
    flag_value_received = 0
    for current_check in range(number_of_checks):
        read_signal_value = XIL_API.Read_Canoe_Symbol(namespace, name)
        if (read_signal_value <= expected_higher_value and read_signal_value>=expected_lower_value):
            HTML_Logger.ReportWhiteMessage("Value received after time (s) :   " + str(current_check*0.050),silent_flag)
            ReportTestStepPass(" -> PASSED", silent_flag)
            flag_value_received = 1
            break
        time.sleep(0.050)
    if (flag_value_received == 0):
        ReportTestStepFail("Expected value NOT received within expected time -> FAILED",silent_flag)
        ReportTestStepFail("Received value : " + str(read_signal_value), silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")
    return flag_value_received

def ReportTestStepPass(string,silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStepResult>\n")
    HTML_Logger.ReportGreenMessage(string,silent_flag)    #green colour
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStepResult>\n")

def ReportTestStepFail(string,silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStepResult>\n")
    HTML_Logger.ReportRedMessage("FAILED:"+string,silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStepResult>\n")

def TestWaitForTimeout(time_ms,silent_flag = False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------",silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : TestWaitForTimeout",silent_flag)
    HTML_Logger.ReportWhiteMessage("Time Delay applied : "+str(time_ms)+" (ms)",silent_flag)
    try:
        time.sleep(time_ms/1000)
        ReportTestStepPass(" -> PASSED",silent_flag)
    except:
        ReportTestStepFail(" -> FAILED",silent_flag)
    HTML_Logger.ReportWhiteMessage("\n",silent_flag)
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def StopMeasurement():
    XIL_API.StopSimulation()

def StartMeasurement():
    XIL_API.StartSimulation()

def Dispose():
    XIL_API.Dispose()

def Disconnect():
    XIL_API.Disconnect()

#matplotlib
def Plot_Signal(namespace, name, silent_flag=False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : Plot Signal", silent_flag)
    #print(trace_log_list_values)
    #print(trace_dict)
    plt.style.use('dark_background')
    plt.plot(trace_dict[str(namespace+name)]['trace_log_list_timestamps'], trace_dict[str(namespace+name)]['trace_log_list_values'])
    plt.xlabel('Time (s)')
    plt.ylabel('Signal Values')
    plt.title('Plotting a logged signal : '+ str(namespace+name))
    list_names=[]
    list_names.append(str(namespace+name))
    plt.legend(list_names)
    filename = str(namespace+name)
    filename = filename.replace("/","_")
    filename = filename.replace('\\', "_")
    filename = filename.replace("::", "_")
    filename = filename.replace(":", "_")
    filename = filename.replace(",", "_")
    filename = filename.replace("*", "_")
    filename = filename.replace("?", "_")
    filename = "Reports\\plots\\plot_"+filename+"_"+HTML_Logger.find_newest_file_in_folder('Reports').replace(".html","")+".jpg"
    #print(filename)
    #plot file name contains the HTML report name + logged signal name
    plt.savefig(filename)
    #plt.show()
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def Plot_All_Signals(silent_flag=False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : Plot All Signals", silent_flag)
    list_names_of_logged_signals = []
    list_names_of_logged_signals.clear()
    number_of_logged_signals = 0
    signal_names = ""
    for el in trace_dict:
        list_names_of_logged_signals.append(el)
        signal_names = signal_names + el + "___"
        number_of_logged_signals = number_of_logged_signals + 1
    #print("___debug___ list_names_of_logged_signals = ", list_names_of_logged_signals)
    #print("___debug___ number_of_logged_signals = ", number_of_logged_signals)

    plt.style.use('dark_background')
    for el in trace_dict:
        plt.plot(trace_dict[str(el)]['trace_log_list_timestamps'], trace_dict[str(el)]['trace_log_list_values'])    #you need to call .plot for all signals seperetally and they are added to the graphics
    plt.xlabel('Time (s)')
    plt.ylabel('Signal Values')
    plt.title('Plotting all logged signals : ' + signal_names)
    plt.legend(list_names_of_logged_signals)
    filename = signal_names
    filename = filename.replace("/", "_")
    filename = filename.replace('\\', "_")
    filename = filename.replace("::", "_")
    filename = filename.replace(":", "_")
    filename = filename.replace(",", "_")
    filename = filename.replace("*", "_")
    filename = filename.replace("?", "_")
    filename = "Reports\\plots\\plot_" + filename + "_" + HTML_Logger.find_newest_file_in_folder('Reports').replace(".html","") + ".jpg"
    # print(filename)
    # plot file name contains the HTML report name + logged signal name
    plt.savefig(filename)
    #plt.show()
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

#plotly library
def Complex_Plot_From_Dict(trace_dict, signal_name,title, hover_name,color: str = None, save_as_html: bool = False, silent_flag=False):
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("<TestStep>\n")
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------", silent_flag)
    HTML_Logger.ReportBlueMessage("Test Step : Complex Plot Signal", silent_flag)
    #print(trace_dict['CarMaker/Car/v']['trace_log_list_timestamps'])
    lst = trace_dict['CarMaker/Car/v']['trace_log_list_timestamps']
    # Calling DataFrame constructor on list
    df = pd.DataFrame(lst)
    #print(df)

    my_figure = px.line(x=trace_dict['CarMaker/Car/v']['trace_log_list_timestamps'], y=trace_dict['CarMaker/Car/v']['trace_log_list_values'], title=signal_name,color=color)
    #my_figure = px.line(x=trace_dict['CarMaker/Car/v']['trace_log_list_timestamps'], y=trace_dict['CarMaker/Car/v']['trace_log_list_values'], title="Venci", color=color)
    #my_figure.show()
    if save_as_html:
        #filename = f"{title.replace(' ', '_').lower()}.html"
        filename = signal_name
        filename = filename.replace("/", "_")
        filename = filename.replace('\\', "_")
        filename = filename.replace("::", "_")
        filename = filename.replace(":", "_")
        filename = filename.replace(",", "_")
        filename = filename.replace("*", "_")
        filename = filename.replace("?", "_")
        filename = "Reports\\plots\\plot_" + filename + "_" + HTML_Logger.find_newest_file_in_folder('Reports')
        my_figure.write_html(filename)
        print(f"Plot saved as {filename}")
    else:
        my_figure.show()
    if (silent_flag == False):HTML_Logger.global_XML_file_handler.write("</TestStep>\n\n")

def Check_And_Acknowledge_HIL_Abort_Messages():
    CheckSignal("hil_ctrl","abort_message","no abort")
    abort_message = GetSignal("","hil_ctrl/abort_message", silent_flag=True)
    if (abort_message=="no abort"):
        ReportTestStepPass("\nThere are no HIL abort messages")
    else:
        ReportTestStepFail("\nAbort Message : "+abort_message)
        #press the ACK button
        SetSignal("","hil_ctrl/ack_abort_msg_btn",1)
        TestWaitForTimeout(150)
        SetSignal("", "hil_ctrl/ack_abort_msg_btn", 0)
        #press Init RBS button
        SetSignal("", "hil_ctrl/init_rbs", 1)
        AwaitValueMatch("hil_ctrl", "init_rbs",0,15)
        abort_message = GetSignal("", "hil_ctrl/abort_message", silent_flag=True)
        if (abort_message == "no abort"):
            ReportTestStepPass("\nHIL abort messages acknowledged successfully")
        else:
            ReportTestStepFail("\nHIL abort messages can NOT be healed !!!")

def Testcase_Start(title, version, filename):
    HTML_Logger.setup(title, version, filename)  # create the HTML report
    #0 -> testcase not running
    #1 -> testcase running
    SetSignal("","Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", 1, silent_flag=True)
    t1 = threading.Thread(target=TDP_Process_Function, args=[])
    t1.start()

def Testcase_End():
    #0 -> testcase not running
    #1 -> testcase running
    SetSignal("", "Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", 0, silent_flag=True)
    #t1.join()

    #generate testcase final verdict
    f_name = "Reports\\" + HTML_Logger.find_newest_file_in_folder('Reports')
    f1 = open(f_name)
    testcase_verdict = "PASSED"
    for el in f1:
        if el.find("FAIL") >= 0:    testcase_verdict = "FAILED"

    SetSignal("", "Python_coupling/string_result_from_Python", testcase_verdict,silent_flag = True)
    HTML_Logger.ReportWhiteMessage("\n\n----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportWhiteMessage(   "TESTCASE FINAL VERDICT : ")
    if (testcase_verdict=="PASSED"):
        HTML_Logger.ReportGreenMessage("PASSED\n\n\n")
    else:
        HTML_Logger.ReportRedMessage("FAILED\n\n\n")
    f1.close()

    # RENAME MF4/BLF CANoe trace if trace logging is active (if logging not active do nothing))
    logging_state = GetSignal("", "hil_ctrl/trace_logging_start_mf4",True)
    #print(logging_state)

    if (logging_state==1):
        HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
        HTML_Logger.ReportBlueMessage("Renaming CANoe trace\n")
        HTML_Logger.ReportGreenMessage(" -> PASSED")
        try:
            #try in folder one level up first
            Stop_MF4_BLF_Logging()
            TestWaitForTimeout(7000, True) #wait 5s so CANoe closes the trace
            # print(os.path.abspath(os.getcwd()))
            last_mf4_file = HTML_Logger.find_newest_file_in_folder(r"..\CustomerPrj\Traces")
            last_mf4_file_extension_type = last_mf4_file.split('.')[1]
            last_HTML_report_file = HTML_Logger.find_newest_file_in_folder(r"Reports")
            # print("last_mf4_file = ", last_mf4_file)
            # print("last_HTML_report_file = ", last_HTML_report_file)
            # print("last_mf4_file_extension_type =", last_mf4_file_extension_type)
            os.rename("..\\CustomerPrj\\Traces\\" + last_mf4_file, "..\\CustomerPrj\\Traces\\" + last_HTML_report_file.replace(".html", "") + "." + last_mf4_file_extension_type)
        except:
            try:
                TestWaitForTimeout(3000, True)  # wait 5s so CANoe closes the trace
                last_mf4_file = HTML_Logger.find_newest_file_in_folder(r"..\CustomerPrj\Traces")
                last_mf4_file_extension_type = last_mf4_file.split('.')[1]
                last_HTML_report_file = HTML_Logger.find_newest_file_in_folder(r"Reports")
                os.rename("..\\CustomerPrj\\Traces\\" + last_mf4_file, "..\\CustomerPrj\\Traces\\" + last_HTML_report_file.replace(".html", "") + "." + last_mf4_file_extension_type)
            except:
                try:
                    TestWaitForTimeout(3000, True)  #wait 5s so CANoe closes the trace
                    last_mf4_file = HTML_Logger.find_newest_file_in_folder(r"CustomerPrj\Traces")
                    last_mf4_file_extension_type = last_mf4_file.split('.')[1]
                    last_HTML_report_file = HTML_Logger.find_newest_file_in_folder(r"Reports")
                    os.rename("CustomerPrj\\Traces\\" + last_mf4_file, "CustomerPrj\\Traces\\" + last_HTML_report_file.replace(".html", "") + "." + last_mf4_file_extension_type)
                except:
                    try:
                        TestWaitForTimeout(3000, True)  # wait 5s so CANoe closes the trace
                        last_mf4_file = HTML_Logger.find_newest_file_in_folder(r"..\CustomerPrj\Traces")
                        last_mf4_file_extension_type = last_mf4_file.split('.')[1]
                        last_HTML_report_file = HTML_Logger.find_newest_file_in_folder(r"Reports")
                        os.rename("..\\CustomerPrj\\Traces\\" + last_mf4_file, "..\\CustomerPrj\\Traces\\" + last_HTML_report_file.replace(".html", "") + "." + last_mf4_file_extension_type)
                    except:
                        pass
                        #HTML_Logger.ReportRedMessage("CANoe trace (MF4/BLF) can not be renamed ! ! ! ")
                        #ReportTestStepFail(" -> FAILED")

    if (testcase_verdict=="PASSED"):
        exit(0)
    else:
        exit(-1)

def TDP_Process_Function():
    TDP_refresh_rate = GetSignal("","Python_coupling/Python_Framework_TDP_refresh_rate",silent_flag=True)
    if TDP_refresh_rate==0:
        TDP_refresh_rate = 500   #put 500ms if the value can not be taken from the CANoe sysvar
    TDP_refresh_rate=TDP_refresh_rate/1000
    is_TC_running = GetSignal("","Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", True)
    #abort message read refresh rate is around 500ms
    #the function GetSignal for the abort message is called 10x slower than the TDP refresh rate (Python<>CANoe sync time)
    #reason is to save XIL API bandwidth for reading-reading-reading
    cnt=0
    flag_abort_execution=0
    while(is_TC_running==1 and flag_abort_execution==0):
        if cnt==0:
            # the function GetSignal for the abort message is called 10x slower than the TDP refresh rate (Python<>CANoe sync time)
            # reason is to save XIL API bandwidth for reading-reading-reading
            if (GetSignal("", "hil_ctrl/abort_message", silent_flag=True) != "no abort"):
                HTML_Logger.ReportRedMessage("\n\n=======================================================================")
                HTML_Logger.ReportRedMessage("WARNING : HIL ABORT MESSAGE occurred now")
                HTML_Logger.ReportRedMessage(GetSignal("", "hil_ctrl/abort_message", True))
                HTML_Logger.ReportYellowMessage("Following measures are taken : ")
                HTML_Logger.ReportWhiteMessage("1)Testcase global verdict set to : FAILED")
                HTML_Logger.ReportWhiteMessage("2)Testcase execution aborted")
                HTML_Logger.ReportWhiteMessage("3)HTML/XML report created until HIL abort occurred")
                HTML_Logger.ReportWhiteMessage("4)MF4/BLF trace will be recorded until HIL abort occurred")
                HTML_Logger.ReportWhiteMessage("5)All teststeps after the HIL abort will NOT be executed")
                HTML_Logger.ReportRedMessage("=======================================================================\n\n")
                flag_abort_execution=1
                reaction_on_abort_message()
        cnt=cnt+1
        if cnt>10: cnt = 0
        is_TC_running = GetSignal("", "Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", True)
        CANoe_global_counter_value = GetSignal("", "hil_ctrl::global_counter", True)
        SetSignal("","Python_coupling/Python_Framework_CANoe_counter_loopback",CANoe_global_counter_value, 0,True)
        time.sleep(TDP_refresh_rate)
    #os._exit(0)

def reaction_on_abort_message():
    SetSignal("", "Python_coupling/Python_Framework_IsTestcaseCurrentlyRunning", 0, silent_flag=True)
    SetSignal("Customer_specific", "cm_stopsim", 1)  # press the STOP SIM button to END scenario/test
    if GetSignal("", "hil_ctrl/jenkins_control") == 0: HTML_Logger.Show_HTML_Report()  # opens the HTML report in Browser  (using the default OS configured browser)
    SetSignal("", "hil_ctrl/ack_abort_msg_btn", 1)
    TestWaitForTimeout(200)
    SetSignal("", "hil_ctrl/ack_abort_msg_btn", 0)
    SetSignal("", "hil_ctrl/trace_logging_start_mf4", 0)
    SetSignal("", "hil_ctrl/init_rbs", 1)
    SetSignal("", "Python_coupling/string_result_from_Python", "FAILED", silent_flag=True)
    os._exit(0)

def Start_MF4_BLF_Logging():
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportBlueMessage("Start MF4/BLF CANoe trace logging\n")
    SetSignal("", "hil_ctrl/trace_logging_start_mf4", 1, silent_flag=True)
    HTML_Logger.ReportGreenMessage(" -> PASSED")

def Stop_MF4_BLF_Logging():
    HTML_Logger.ReportWhiteMessage("----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    HTML_Logger.ReportBlueMessage("Stop MF4/BLF CANoe trace logging\n")
    SetSignal("", "hil_ctrl/trace_logging_start_mf4", 0, silent_flag=True)
    HTML_Logger.ReportGreenMessage(" -> PASSED")

