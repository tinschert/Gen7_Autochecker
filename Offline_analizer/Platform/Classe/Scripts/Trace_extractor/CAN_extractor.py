# -*- coding: utf-8 -*-
# @file CAN_extractor.py
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
    for i in range(2):                                      
        serach_data(str_in, "::")                           # search for the "::" in the file name and crop the first part
        try:
            str_in = str_in[serach_data(str_in, "::") + 2:]     # repeat this operation twice to reach the signal name
        except:
            print("error in extracting signal name")    
    if serach_data(str_in, "["):
        str_in = str_in[0:serach_data(str_in, "[")]  
    return (str_in)                                         # this is used fro CAN1, Ethernet & FlexRay


def generate_sig_name_CAN2(str_in):                         # extract the signal name and the PDU name from the header including CAN + PDU + signal name                                           
    """
    

    Args:
      str_in: 

    Returns:

    """
    serach_data(str_in, "::")                               # this is made for the CAN2 signals as the CAN config requires this special format
    try:
        str_in = str_in[serach_data(str_in, "::") + 2:]         
    except:
        print("error in extracting CAN2 signal name")
    if serach_data(str_in, "["):
        str_in = str_in[0:serach_data(str_in, "[")]  
    str_in = str_in.replace("::","_")
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
        write_text(filename , list1[i], " = "+list2[i])    # this si valid for both CAN1, Ethernet & Flexray signals
        
def generate_signal_list_CAN2(filename, list1, list2):                  # this function is special for the CAN2 siganls as they reauire an additional
    """
    

    Args:
      filename: 
      list1: 
      list2: 

    Returns:

    """
    for i in range(len(list1)):                                         # prefix as follows "E_pubc_Vector_XXX_"
        write_text(filename , "E_pubc_Vector_XXX_"+list1[i], " = "+list2[i])


def generate_files(filename, list_in1, list_in2, list_in3, list_in4, list_in5, list_in6):   # this function was created to make sure                       # that all the data will be correctly set in the appropriate files
    """
    

    Args:
      filename: 
      list_in1: 
      list_in2: 
      list_in3: 
      list_in4: 
      list_in5: 
      list_in6: 

    Returns:

    """
    write_text(filename, "[UN_HSCAN]","")                                            # and that both the CAN & INI file will hve the same name and sahre the sigansl list
    try:
        generate_signal_list(filename,list_in1,list_in2)                                        # the can file has a header defined by "on start {" and ends with "}"
    except:
        print("CAN1 signal list is not correctly created")
                                                  # this yas added to prepare the CAN file for usage
    write_text(filename, "\n","[Vector_XXX]")                                        # The CAN1, CAN2 & flexRay section are divied by name for both CAN and INI files
    try:
       generate_signal_list_CAN2(filename,list_in3,list_in4 )
    except:
       print("CAN2 signal list is not correctly created")
    
    write_text(filename, "\n","[FLEXRAY]")
    try:
        generate_signal_list(filename,list_in5,list_in6 )
    except:
        print("FLEXRAY signal list is not correctly created")

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

    
def main_can(input_file, output_file, time):
    """
    

    Args:
      input_file: 
      output_file: 
      time: 

    Returns:

    """
    f = read_text("filter_signals.txt")                     # load the to-be filtered siganls file
    filter_sig = f.split("\n")                              # and put all the siganls names in a list
    
    d = read_text(input_file)                                       # load the csv file containing the extract of the blf recordinh
    columns_data = d.split("\n")                                    # return number of columns 
    sign_names = columns_data[0].split(";")[1:]                     # list containing the names of the siganls without time
    num_signals = len(sign_names)                                   # the number of signals

    temp_list_HSCAN =  []            # var starting UN_HSCAN::PDU::is_signname // UN_HSCAN::ABS_RDN_1_Pdu::isBrakePedalAppliedRdn
    temp_list_HSCAN2 = []
    temp_list_vector =  []           # var starting DADCA_A_CCM_ADAS_HSCAN::PDU::signame  // DADCA_A_CCM_ADAS_HSCAN::FR_HDR_A::Hdr_Align_dMountOffset[cm]
    temp_list_vector2 = []    
    temp_list_flex =  []             #var starting FlexRay::PDU::is_signame
    temp_list_flex2 = []    

    sign_values = ini_value_optimizer(columns_data, num_signals)
    for i in range(num_signals):                                                                            # go through the sigan list to prepare the final output files, CAN and INI
        for j in range (len(filter_sig)):                                                                       # go through the to-be filtered siganls list to block them for being added
            try:
                if (serach_data(sign_names[i], filter_sig[j]) > -1):                                                # serach for the instances of the sigansl to be filtered  
                    break
            except:
                print("no filters are added in the list")                                                                                           # and stop iterating when an ele?ent is selected
            if (j == len(filter_sig)-1):                                                                        # When the sigansl being verified do not appear on the filtered list
                if (serach_data(sign_names[i], "UN_HSCAN" ) > -1 ):                                             # proceed with writing the in the appropriate list (to be later on added in the output CAN & INI files)
                    temp_list_HSCAN.append(generate_sig_name(sign_names[i]))
                    temp_list_HSCAN2.append(sign_values[i])
                elif ( serach_data(sign_names[i], "ADAS_HSCAN" ) > -1 ):
                    temp_list_vector.append(generate_sig_name_CAN2(sign_names[i]))
                    temp_list_vector2.append(sign_values[i])     
                elif ( serach_data(sign_names[i], "FlexRay" ) > -1 ):
                    temp_list_flex.append(generate_sig_name(sign_names[i]))
                    temp_list_flex2.append(sign_values[i])
    """
    if (time_row_creator(columns_data, time) == []):
        print("time selected not found")
    else:     
        for k in range(1):  
            sign_values = columns_data[time_row_creator(columns_data, time)[k]].split(";")
            for i in range(len(sign_names)):                                                                            # go through the sigan list to prepare the final output files, CAN and INI
                for j in range (len(filter_sig)):                                                                       # go through the to-be filtered siganls list to block them for being added
                    try:
                        if (serach_data(sign_names[i], filter_sig[j]) > -1):                                                # serach for the instances of the sigansl to be filtered  
                            break
                    except:
                        print("no filters are added in the list")                                                                                           # and stop iterating when an ele?ent is selected
                    if (j == len(filter_sig)-1):                                                                        # When the sigansl being verified do not appear on the filtered list
                        if (serach_data(sign_names[i], "UN_HSCAN" ) > -1 ):                                             # proceed with writing the in the appropriate list (to be later on added in the output CAN & INI files)
                            temp_list_HSCAN.append(generate_sig_name(sign_names[i]))
                            temp_list_HSCAN2.append(sign_values[i])
                        elif ( serach_data(sign_names[i], "ADAS_HSCAN" ) > -1 ):
                            temp_list_vector.append(generate_sig_name_CAN2(sign_names[i]))
                            temp_list_vector2.append(sign_values[i])     
                        elif ( serach_data(sign_names[i], "FlexRay" ) > -1 ):
                            temp_list_flex.append(generate_sig_name(sign_names[i]))
                            temp_list_flex2.append(sign_values[i])
    """
    try:
        generate_files(output_file, temp_list_HSCAN, temp_list_HSCAN2, temp_list_vector, temp_list_vector2, temp_list_flex, temp_list_flex2)    # generate the INI & CAN files  
    except:
        ("file could not be generated")
   
#main_can("CANFollow.csv", "CANFollow__687428281.csv", "687.428281")


def execute_can():
    """ """
    #print('insert the time with the format "ttt.tttttt"')
    #time = input(" time = ")
    print('insert the file name with the forma "file.csv" ')
    file = input(" file = ")
    file = file.replace("'", "").replace('"', '')
   
    main_can(file, "CAN_FLEX_"+str(time)+".csv")



#execute_can()
