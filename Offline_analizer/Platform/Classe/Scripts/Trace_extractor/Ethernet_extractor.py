# -*- coding: utf-8 -*-
# @file Ethernet_extractor.py
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


def write_text(file_name, data1, data2):          # generate files with the signals selection and their values    
    """
    

    Args:
      file_name: 
      data1: 
      data2: 

    Returns:

    """
    filename = file_name                                        # add the name of the file to generate with the extension
    file = open (filename, "a")                                 # 4 parameters are to be added, in case 4 parameters are too much
    file.write(data1)                                           # keep the data slot empty
    file.write(data2)                                           # the file will be opened and after each data written,  
    file.write("\n")                                            # a jump line is added qt the end of each new element in the file
    file.close()


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
    for i in range(1):                                      
        serach_data(str_in, "::")                           # search for the "::" in the file name and crop the first part
        try:
            str_in = str_in[serach_data(str_in, "::") + 2:]     # repeat this operation twice to reach the signal name
        except:
            print("error in extracting signal name")    
    if serach_data(str_in, "["):
        str_in = str_in[0:serach_data(str_in, "[")]  
    return (str_in)                                         # this is used fro CAN1, Ethernet & FlexRay

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
        if ( time in data_list[i].split(";")[0]  ):              # if ( time == (columns_data[i].split(";"))[0] ):
            time_row_selector.append(i)
    return time_row_selector
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
    

def main_ethernet(input_file, output_file):
    """
    

    Args:
      input_file: 
      output_file: 

    Returns:

    """

    matrix = []
    
    f = read_text("filter_signals.txt")                             # load the to-be filtered siganls file
    filter_sig = f.split("\n")                                      # and put all the siganls names in a list    
    d = read_text(input_file)                                       # load the csv file containing the extract of the blf recordinh
    columns_data = d.split("\n")                                    # splits the data from the csv file   
    sign_names = columns_data[0].split(";")[1:]                     # list containing the names of the siganls without time
    num_signals = len(sign_names)                                   # the number of signals

    sign_values = ini_value_optimizer(columns_data, num_signals)                                                       # parse the data row by row while respecting the time stamp specified
    for i in range(num_signals):                                                                # loop the signals present in the dbc
        for j in range (len(filter_sig)):                                                           # go through the to-be filtered siganls list to block them for being added
            if (serach_data(sign_names[i], filter_sig[j]) > -1):                                    # serach for the instances of the sigansl to be filtered  
                break                                                                               # and stop iterating when an ele?ent is selected             if (j == len(filter_sig)-1):                                                                        # When the sigansl being verified do not appear on the filtered list
            if (j == len(filter_sig)-1):                                                            # in case no filter is found
                matrix.append([generate_sig_name(sign_names[i]), sign_value[i]])   
    """
    if (time_row_creator(columns_data, time) == []):
        print("time selected not found")
    else:  
        for k in range(len(time_row_creator(columns_data, time))):             
            sign_value = columns_data[time_row_creator(columns_data, time)[k]].split(";")                                                          # parse the data row by row while respecting the time stamp specified
            for i in range(len(sign_names)):                                                                # loop the signals present in the dbc
                for j in range (len(filter_sig)):                                                           # go through the to-be filtered siganls list to block them for being added
                    if (serach_data(sign_names[i], filter_sig[j]) > -1):                                    # serach for the instances of the sigansl to be filtered  
                        break                                                                               # and stop iterating when an ele?ent is selected             if (j == len(filter_sig)-1):                                                                        # When the sigansl being verified do not appear on the filtered list
                    if (j == len(filter_sig)-1):                                                            # in case no filter is found
                        matrix.append([generate_sig_name(sign_names[i]), sign_value[i]])                    # add the signal to the list
    """
    for i in range(len(matrix)):                                         
        write_text(output_file, matrix[i][0], " ; "+ matrix[i][1])

#main_ethernet("EgzonPanelFusion.csv","EgzonPanelFusion__687.449073.csv","687.449073")    


def execute_ethernet():
    """ """

    #print('please insert the time with the format "ttt.tttttt"')
    #time = input(" time = ")
    print('please insert the file name with the forma "file.csv" ')
    file = input(" file = ")
    file = file.replace("'", "").replace('"', '')

    main_ethernet(file, "Ethernet_"+str(time)+".csv")

#execute_ethernet()