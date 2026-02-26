# -*- coding: utf-8 -*-
# @file Generate_FDX_in_XCP_Mappings_CAPL_file_v1.py
# @author ADAS_HIL_TEAM
# @date 10-04-2022

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2022-2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import easygui
#from fuzzywuzzy import fuzz
import pandas as pd

fdx_xls_file = easygui.fileopenbox("Select the <<FDX_DATABASE.xlsx>> file /used for triggers extraction/: ")
#fdx_xls_file = r"D:\ADAS_HIL\CustomerPrj\FDX\FDX_Database.xlsx"
A2L_file = easygui.fileopenbox("Select the .A2L file /used to extract the XCP names/ : ")
#A2L_file = r"C:\Users\NEV1SF4\Desktop\HIL-3_transfer_files\RadarFC_RC12.a2l"
output_file = 'FDX_in_to_XCP.can'

list_a2l_items = []
list_a2l_items.clear()
list_rows_from_a2l_file = []
list_rows_from_a2l_file.clear()
triggers_list = []
triggers_list.clear()
Reduced_Triggers_Names_List = []
Reduced_Triggers_Names_List.clear()
Reduced_A2L_Items_Names = []
Reduced_A2L_Items_Names.clear()

def Read_FDX_Database_XLS(excel_filename):
    """
    

    Args:
      excel_filename: 

    Returns:

    """
    triggers_df=pd.read_excel(open(excel_filename, 'rb'), sheet_name='fdxTriggersDatabase')

    #convert dataframes to lists for easier C-like handling :)
    list1=triggers_df.values.tolist()
    for el in list1:
        #print(el)
        if (el[0].find("FDX_out")<0):   #only fdx_in are needed
            triggers_list.append([el[0],el[1]])

def Reduce_Triggers_List_Name(orig_name):
    """
    

    Args:
      orig_name: 

    Returns:

    """
    temp_str=orig_name
    #remove prefixes
    temp_str = temp_str.replace("m_data_m_Lss_m_impl_m_data","")
    temp_str = temp_str.replace("m_data_m_LongComfDriverInputProvider_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_LksCondition_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_Lks_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_mpip_Hf_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_Common_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_Alc_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_AccStateMachine_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_Aeb_m_impl_m_data", "")
    temp_str = temp_str.replace("m_data_m_AccControlUnit_m_impl_m_data", "")
    temp_str = temp_str.replace("m_mapInfo", "")
    temp_str = temp_str.replace("m_radarObjects", "")
    temp_str = temp_str.replace("m_videoLines", "")
    temp_str = temp_str.replace("m_vehicleInfo", "")
    temp_str = temp_str.replace("__m_value", "")
    temp_str = temp_str.replace("_m_value", "")
    #temp_str = temp_str.replace("FDX_out__", "")
    temp_str = temp_str.replace("FDX_in__", "")
    #temp_str = temp_str.replace("FDX_out_", "")
    temp_str = temp_str.replace("FDX_in_", "")
    return temp_str

def Reduce_Triggers_Names():
    """ """
    for el in triggers_list[1]:
        tmp_str=Reduce_Triggers_List_Name(el)
        Reduced_Triggers_Names_List.append(tmp_str)

def Read_A2L_file():
    """ """
    f1 = open(A2L_file, "r")
    for x in f1:
        list_rows_from_a2l_file.append(x)
    f1.close()

def Extract_A2l_Variables():
    """ """
    #add the MEASUREMENTS
    #for el in list_rows_from_a2l_file:
    #    if (el.find("/begin MEASUREMENT ")>=0):
    #        temp_str=el.replace("    /begin MEASUREMENT ","")
    #        temp_str=temp_str.split(' "')[0]
    #        temp_str = temp_str.replace('\n', '')
    #        list_a2l_items.append(temp_str)
    #        # add the MEASUREMENTS
    # add the CHARACTERISTICS

    #only characteristics can be mapped to a trigger
    for el in list_rows_from_a2l_file:
        if (el.find("/begin CHARACTERISTIC ") >= 0):
            temp_str = el.replace("    /begin CHARACTERISTIC ", "")
            temp_str = temp_str.split(' "')[0]
            temp_str = temp_str.replace('\n', '')
            list_a2l_items.append(temp_str)


def FindBestMatch(str_to_upd):
    """
    

    Args:
      str_to_upd: 

    Returns:

    """
    string_to_update = str_to_upd
    probability_list=[]
    list_1 = string_to_update.split(".")
    set_1=set(list_1)
    for el_from_MF4_file in list_a2l_items:
        temp_str=el_from_MF4_file.replace("\n", "")
        el_from_MF4_file_splitted=temp_str.split(".")
        #print("EL FROM MF4 splitted   ", el_from_MF4_file_splitted)
        #print("LIST 1 /original/= ", list_1)
        #print("LIST 2 /MF4 line/= ", el_from_MF4_file_splitted)
        set_2=set(el_from_MF4_file_splitted)
        intersection_weight=len(set_1.intersection((set_2)))
        #print("DEBUG!!! intersection weight = ",intersection_weight)
        probability_list.append([intersection_weight, el_from_MF4_file])  # this uses sets intersection
        #first step is sets intersection and generate a new list with weight + value


    probability_list.sort()
    #limit the possibilities by taking only the highest score of intersection
    #print("DEBUG! prob_list",probability_list)
    max_prob=probability_list[len(probability_list)-1][0]
    print("DEBUG max intersection = ", max_prob)
    if (max_prob<3):    #ignore all results if prob <30%
        print("!!! BEST MATCH is NOT proper to be used (last 2 words do NOT match 100%) - ORIGINAL STRING WILL BE LEFT !!!")
        print("ORIGINAL = ", string_to_update)
        print("================================================================================================================================================================================================================================================")
        print("================================================================================================================================================================================================================================================")
        return string_to_update
    possibilities_list=[]
    for el in probability_list:
        if el[0]==max_prob:
            possibilities_list.append(el)
    #print("DEBUG! POSSIBILITIES list", possibilities_list)
    #print("DEBUG max_prob = ",max_prob)

    #2nd filter by fuzzy logic on the limited list (list of only the highest intersections)
    new_probability_list=[]
    for elmnt in possibilities_list:
        new_probability_list.append([fuzz.token_sort_ratio(elmnt[1],string_to_update),elmnt[1]])     #this uses fuzzy logic alg.


    #print("PROBABILITY LIST= ",probability_list)
    probability_list=new_probability_list
    probability_list.sort()
    max_element = probability_list[len(probability_list)-1]
    best_match = max_element[1].replace("\n", "")
    print("BEST MATCH                = ", best_match)
    print("BEST PROBABILITY          =", max_element[0])
    best_match_splitted=best_match.split(".")
    original_string_splitted=string_to_update.split(".")
    #print("STR TO UPDATE splitted",original_string_splitted)
    #print("BEST MATCH splitted   ",best_match_splitted)
    print("LAST WORD = ",best_match_splitted[len(best_match_splitted)-1])
    print("BEFORE THE LAST WORD = ", best_match_splitted[len(best_match_splitted) - 2])
    if ( (best_match_splitted[len(best_match_splitted)-1] in original_string_splitted) and (best_match_splitted[len(best_match_splitted)-2] in original_string_splitted) ):
        print("BEST MATCH is proper to be used (last 2 words match 100%)")
        print("================================================================================================================================================================================================================================================")
        print("================================================================================================================================================================================================================================================")
        return best_match
    else:
        print("!!! BEST MATCH is NOT proper to be used (last 2 words do NOT match 100%) - ORIGINAL STRING WILL BE LEFT !!!")
        print("ORIGINAL = ",string_to_update)
        print("================================================================================================================================================================================================================================================")
        print("================================================================================================================================================================================================================================================")
        return string_to_update

def FindBestMatch_Wildcards(str_to_upd):
    """
    

    Args:
      str_to_upd: 

    Returns:

    """
    string_to_update = str_to_upd
    words_list=string_to_update.split(".*")
    try:
        words_list.remove('')
    except:
        pass
    #if ('' in words_list):
    #    words_list.remove("''")
    print("!DEBUG wildcards words_list=",words_list)

    #print(list_a2l_items)
    is_found=False
    found_string=""
    for el_from_MF4_file in list_a2l_items:
        temp_str=el_from_MF4_file.replace("\n","")
        is_found=all(x in temp_str for x in words_list)
        #print("!!!DEBUG!!! is_found=",is_found)
        if (is_found == True):
            found_string=temp_str
            break
    if (is_found==True):
        #print(el_from_MF4_file)
        print("BEST MATCH                = ", found_string)
        print("================================================================================================================================================================================================================================================")
        print("================================================================================================================================================================================================================================================")
        return found_string
    else:
        print("!!! NOTHING FULFILLS THE WILDCARDS- ORIGINAL STRING WILL BE LEFT !!!")
        print("ORIGINAL = ", string_to_update)
        print("================================================================================================================================================================================================================================================")
        print("================================================================================================================================================================================================================================================")
        return string_to_update

def Reduce_A2L_Items_Names():
    """ """
    for el in list_a2l_items:
        temp_list = el.split(".")
        temp_len = len(temp_list)
        temp_str = temp_list[temp_len - 1]
        # element [0] - full name, el[1] - reduced name
        Reduced_A2L_Items_Names.append([el,temp_str])

def main():
    """ """
    out_file = open(output_file, "w+")

    Read_A2L_file()
    Extract_A2l_Variables()
    # prints the original a2l items
    #for el in list_a2l_items:
    #     print(el)
    Reduce_A2L_Items_Names()
    #prints the last word of a2l items
    #for el in Reduced_A2L_Items_Names:
    #    print(el)
    #!!!IMPORTANT!!!
    #The reduced name is in Reduced_A2L_Items_Names[1], the full name is in Reduced_A2L_Items_Names[0]

    Read_FDX_Database_XLS(fdx_xls_file)
    #prints the CLOE triggers list
    # for el in triggers_list[1]:
    #     print(el)


    #print(Reduced_A2L_Items_Names)

    #WRITE TO OUTPUT CAPL file
    out_file.write("includes\n{\n\n}\nvariables\n{\n\n}\n\n")
    #ignore list -> all the radar and video objects injection items
    ignore_list=["_m_axN", "_m_vyN","_m_vxN","_m_dzN","_m_dyN","_m_dxN","_m_dWidthN","_m_dLengthN","_m_ayN","_m_alpPiYawAngleN","_timeStamp","_m_current","_width","_length"]
    for el_FDX_trigger in triggers_list:
        for el_a2l in Reduced_A2L_Items_Names:
            if el_FDX_trigger[0].find(el_a2l[1])>=0:
                if len(el_a2l[1])>5:
                    if el_a2l[1] not in ignore_list:
                        #print(el_a2l[1]+" found in "+el_FDX_trigger[0])
                        #auto-code-generation here:
                        print("on sysvar "+el_FDX_trigger[1]+"::"+el_FDX_trigger[0])
                        out_file.write("on sysvar "+el_FDX_trigger[1]+"::"+el_FDX_trigger[0]+"\n")
                        print("{")
                        out_file.write("{\n")
                        print(" @sysvar::XCP::RadarFC::"+el_a2l[0].replace(".","::")+"=@this;")
                        out_file.write(" @sysvar::XCP::RadarFC::"+el_a2l[0].replace(".","::")+"=@this;"+"\n")
                        print("}\n")
                        out_file.write("}\n\n")
    out_file.close()
if __name__ == "__main__":

    main()