# -*- coding: utf-8 -*-
# @file INI_parser.py
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


import csv
import numpy as np
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import openpyxl
import os


#variables
init_can = """includes {
  
}


variables {
 
  char SIGNAL_INIFILE[255] = "Init/signal.ini";
  
  char CAN1_CHANNEL[255] = "UN_HSCAN";
  char CAN2_CHANNEL[255] = "Vector_XXX";
  char FLEXRAY_CHANNEL[255] = "Flexray";
  char Ethernet_CHANNEL[255] = "Ethernet";
  
}
"""
end_can = """qword getSignalValue(char signal_name[])
{
  qword val=99;
  val = getProfileInt(CAN1_CHANNEL, signal_name, -1, SIGNAL_INIFILE);
  if (val >= 0) {
    return val;
  } else {
    val = getProfileInt(CAN2_CHANNEL, signal_name, -1, SIGNAL_INIFILE);
    if (val >= 0) {
      return val;
    } else {
      val = getProfileInt(FLEXRAY_CHANNEL, signal_name, -1, SIGNAL_INIFILE);
      if (val >= 0) {
       return val;
      } else {
        return getProfileInt(Ethernet_CHANNEL, signal_name, -1, SIGNAL_INIFILE);
        }
    }
  }
}

"""

def write_text(file_name, data1, data2):          # generate files with the signals selection and their values    
    """
    

    Args:
      file_name: 
      data1: 
      data2: 

    Returns:

    """
    filename = file_name                                        # add the name of the file to generate with the extension
    file = open(filename, "a")                                  # 4 parameters are to be added, in case 4 parameters are too much
    file.write(data1)                                           # keep the data slot empty
    file.write(data2)                                           # the file will be opened and after each data written,  
    file.write("\n")                                            # a jump line is added qt the end of each new element in the file
    file.close()


def delete_if_exist(file_name):
    """
    

    Args:
      file_name: 

    Returns:

    """
    dirList = os.listdir()   
    dirList.sort()

    for file in dirList:
        if file == file_name:
            os.remove(file)
        else:
            pass


def read_text(file_in):                                 # load the file to read, in this case, the csv file
    """
    

    Args:
      file_in: 

    Returns:

    """
    file_temp = open(file_in, "r")                      # the file should be plaed in this same directory as the python file
    data = file_temp.read()
    return data


def serach_data(data1, data2):                  # return the index position of data2 in data1
    """
    

    Args:
      data1: 
      data2: 

    Returns:

    """
    return data1.find(data2)                    # if data2 is not to be foundm the result is -1


def generate_sig_name(str_in):                              # extracts the signal name from the header including the CAN + PDU + signal name
    """
    

    Args:
      str_in: 

    Returns:

    """
    for i in range(2):                                      
        #serach_data(str_in, "::")                           # search for the "::" in the file name and crop the first part
        try:
            str_in = str_in[serach_data(str_in, "::") + 2:]     # repeat this operation twice to reach the signal name
        except:
            print("error in extracting signal name")
    if serach_data(str_in, "[") > -1:
        str_in = str_in[0:serach_data(str_in, "[")]
    return (str_in)                                         # this is used fro CAN1, Ethernet & FlexRay


def generate_sig_name_CAN2(str_in):                         # extract the signal name and the PDU name from the header including CAN + PDU + signal name                                           
    """
    

    Args:
      str_in: 

    Returns:

    """
    #serach_data(str_in, "::")                               # this is made for the CAN2 signals as the CAN config requires this special format
    try:
        str_in = str_in[serach_data(str_in, "::") + 2:]      
    except:
        print("error in extracting CAN2 signal name")
    if serach_data(str_in, "["):
        str_in = str_in[0:serach_data(str_in, "[")]  
    str_in = str_in.replace("::", "_")
    return (str_in)


def generate_signal_list(filename, list1, list2):                       # collest the sigansl into one list to be used as an input to the ini file
    """
    

    Args:
      filename: 
      list1: 
      list2: 

    Returns:

    """
    for i in range(len(list1)):                                         # add an "_Rv" extension to match the environment variables mapped to the actual signals
        write_text(filename+".ini", list1[i]+"_Rv", " = " + list2[i])   # this si valid for both CAN1, Ethernet & Flexray signals
        #write_text(filename +".can", "\t"+"putValue(" + list1[i]+"_Rv,", ' getSignalValue("'+list1[i]+'_Rv"));')

def generate_files(filename, temp_list_flex, temp_list_flex2, temp_list_ether, temp_list_ether2, temp_list_Eth1, temp_list_Eth12, temp_list_CAN, temp_list_CAN2):   # this function was created to make sure
    """
    

    Args:
      filename: 
      temp_list_flex: 
      temp_list_flex2: 
      temp_list_ether: 
      temp_list_ether2: 
      temp_list_Eth1: 
      temp_list_Eth12: 
      temp_list_CAN: 
      temp_list_CAN2: 

    Returns:

    """
    #write_text(filename+".can","//Flexray","")
    write_text(filename+".ini", "", "[FLEXRAY]")
    try:
        generate_signal_list(filename, temp_list_flex, temp_list_flex2)
    except:
        print("FLEXRAY signal list is not correctly created")

    #write_text(filename+".can","//Ethernet","")
    write_text(filename+".ini", "\n", "[Ethernet]")
    try:
        generate_signal_list(filename, temp_list_ether, temp_list_ether2)
    except:
        print("Ethernet signal list is not correctly created")

    #write_text(filename+".can","//Eth1","")
    write_text(filename+".ini", "\n", "[Eth1]")
    try:
        generate_signal_list(filename, temp_list_Eth1, temp_list_Eth12)
    except:
        print("Eth1 signal list is not correctly created")

    #write_text(filename+".can","//CAN_FD","")
    write_text(filename+".ini", "\n", "[CAN]")
    try:
        generate_signal_list(filename, temp_list_CAN, temp_list_CAN2)
    except:
        print("CAN signal list is not correctly created")
    
    #write_text(filename+".can","}","")      

"""
def time_row_creator(data_list, time):
    """
    

    Args:
      data_list: 
      time: 

    Returns:

    """
    time_row_selector = []
    for i in range(len(data_list)):
        if (time in data_list[i].split(";")[0]):              # if ( time == (columns_data[i].split(";"))[0] ):
            time_row_selector.append(i)
    if (len(time_row_selector) > 0):
        return time_row_selector[0]
    else:
        print("element not found")
"""

def ini_value_optimizer(columns_data, num_signals):
    """
    

    Args:
      columns_data: 
      num_signals: 

    Returns:

    """

    columns_values = []
    ini_values = []

    for i in range(1, len(columns_data)):
        row_data = columns_data[i].split(";")[1:]
        if len(row_data) == num_signals:
            columns_values.append(row_data)
    columns_values = np.array(columns_values)
    
    for i in range(num_signals):
        col_values = columns_values[:, i]
        col_value_set = set(col_values)
        if len(col_value_set) == 1:
            ini_values.append(col_value_set.pop())
        else:
            index = np.where(col_values != '0')
            col_values = col_values[index]
            values, counts = np.unique(col_values, return_counts=True)
            ini_values.append(values[np.argmax(counts)])
    return ini_values


def main_ini(input_file, output_file):
    """
    

    Args:
      input_file: 
      output_file: 

    Returns:

    """
    f = read_text("filter_signals.txt")                     # load the to-be filtered siganls file
    filter_sig = f.split("\n")                              # and put all the siganls names in a list
    
    d = read_text(input_file)                                       # load the csv file containing the extract of the blf recordinh
    columns_data = d.split("\n")                                    # return number of columns 
    sign_names = columns_data[0].split(";")[1:]                     # list containing the names of the siganls without time
    num_signals = len(sign_names)                                   # the number of signals

    temp_list_flex =  []             #var starting FlexRay::PDU::is_signame
    temp_list_flex2 = []    
    temp_list_ether =  []            #var starting Ethernet::PDU::is_signame
    temp_list_ether2 = [] 
    temp_list_Eth1 =  []            #var starting Eth1::PDU::is_signame
    temp_list_Eth12 = []     
    temp_list_CAN =  []            #var starting CAN::PDU::is_signame
    temp_list_CAN2 = []   
    
    sign_values = ini_value_optimizer(columns_data, num_signals)
    for i in range(num_signals):                                                                            # go through the sigan list to prepare the final output files, CAN and INI
        for j in range (len(filter_sig)):                                                                       # go through the to-be filtered siganls list to block them for being added
            try:
                if (serach_data(sign_names[i], filter_sig[j]) > -1):                                                # serach for the instances of the sigansl to be filtered  
                    break
            except:
                print("no filters are added in the list")                                                                                           # and stop iterating when an ele?ent is selected
            if (j == len(filter_sig)-1):                                                               # When the sigansl being verified do not appear on the filtered list
                if ( serach_data(sign_names[i], "FlexRay" ) > -1 ):
                    temp_list_flex.append(generate_sig_name(sign_names[i]))
                    temp_list_flex2.append(sign_values[i])
                elif ( serach_data(sign_names[i], "Ethernet" ) > -1 ):
                    temp_list_ether.append(generate_sig_name(sign_names[i]))
                    temp_list_ether2.append(sign_values[i])
                elif ( serach_data(sign_names[i], "Eth1" ) > -1 ):
                    temp_list_Eth1.append(generate_sig_name(sign_names[i]))
                    temp_list_Eth12.append(sign_values[i])
                elif ( serach_data(sign_names[i], "CAN" ) > -1 ):
                    temp_list_CAN.append(generate_sig_name(sign_names[i]))
                    temp_list_CAN2.append(sign_values[i])                     
                else:
                     print(sign_names[i])
                     print(sign_values[i])
    """     
    if (time_row_creator(columns_data, time) == []):
        print("time selected not found")
    else:  
        sign_values = columns_data[time_row_creator(columns_data, time)].split(";")
        Length = len(sign_names)
        for i in range(Length):                                                                            # go through the sigan list to prepare the final output files, CAN and INI
            for j in range (len(filter_sig)):                                                                       # go through the to-be filtered siganls list to block them for being added
                try:
                    if (serach_data(sign_names[i], filter_sig[j]) > -1):                                                # serach for the instances of the sigansl to be filtered  
                        break
                except:
                    print("no filters are added in the list")                                                                                           # and stop iterating when an ele?ent is selected
                if (j == len(filter_sig)-1):                                                                        # When the sigansl being verified do not appear on the filtered list
                    if (serach_data(sign_names[i], "CCM_E_UNHSCAN_NCR18Q4_181105" ) > -1 ):                                             # proceed with writing the in the appropriate list (to be later on added in the output CAN & INI files)
                        temp_list_HSCAN.append(generate_sig_name(sign_names[i]))
                        temp_list_HSCAN2.append(sign_values[i])
                    elif ( serach_data(sign_names[i], "DADCA_A_NCR18Q4_190710" ) > -1 ):
                        temp_list_vector.append(generate_sig_name_CAN2(sign_names[i]))
                        temp_list_vector2.append(sign_values[i])             
                    elif ( serach_data(sign_names[i], "FlexRay" ) > -1 ):
                        temp_list_flex.append(generate_sig_name(sign_names[i]))
                        temp_list_flex2.append(sign_values[i])
                    elif ( serach_data(sign_names[i], "Ethernet" ) > -1 ):
                        temp_list_ether.append(generate_sig_name(sign_names[i]))
                        temp_list_ether2.append(sign_values[i])
                    elif ( serach_data(sign_names[i], "Eth1" ) > -1 ):
                        temp_list_Eth1.append(generate_sig_name(sign_names[i]))
                        temp_list_Eth12.append(sign_values[i])
                    elif ( serach_data(sign_names[i], "IPMA_F_UNCAN_NCR18Q4_190520" ) > -1 ):
                        temp_list_IPMA.append(generate_sig_name(sign_names[i]))
                        temp_list_IPMA2.append(sign_values[i])                      
                    else:
                         print(sign_names[i])
                         print(sign_values[i])
    """
    try:
        # generate the INI & CAN files
        generate_files(output_file, temp_list_flex, temp_list_flex2, temp_list_ether, temp_list_ether2, temp_list_Eth1, temp_list_Eth12, temp_list_CAN, temp_list_CAN2)
        print("\nsuccessfully generated file:", output_file)
        return True
    except Exception as exp:
        print("\nfile could not be generated:", exp)
        return False


def execute_ini():
    """ """
    
    #print('insert the time with the format "ttt.tttttt"')
    #time = input(" time = ")
    print('Please insert the init file name with the format "file.csv", like "VehID_DASy_0000.csv"')
    Input_file = input(" file = ")
    Input_file = Input_file.replace("'", "").replace('"', '')
    print('Please name output file with the format "file_vehicle", like "signal_X590"')
    Output_file = input(" file = ")
    Output_file = Output_file.replace("'", "").replace('"', '').replace(".ini", "")
    
    delete_if_exist(Output_file+".ini") 
    #write_text("signal.can", init_can, "\n")
    main_ini(Input_file, Output_file)
    write_text(Input_file, "\n", end_can)

    return Output_file+".ini"


if __name__ == "__main__":
    main_ini("psa_veh_aeb_active_fd3_fdp1_1corner.csv", "test_output")
