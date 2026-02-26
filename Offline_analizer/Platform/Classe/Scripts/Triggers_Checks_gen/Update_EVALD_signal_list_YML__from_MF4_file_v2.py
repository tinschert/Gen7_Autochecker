# -*- coding: utf-8 -*-
# @file Update_EVALD_signal_list_YML__from_MF4_file_v2.py
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


import easygui
from fuzzywuzzy import fuzz

input_file = easygui.fileopenbox("Select the INPUT file (evald_signal_list.yml) that you want to update :","*.yml")     #'All_Interfaces_from_DOORS_updated.csv'

output_file = input_file.replace('.yml','')+'_output'+'.yml'

MF4_file = easygui.fileopenbox("Select the MF4 file (exported to .txt format) as a DATABASE")  #'SW_4_3_0_ODS_Signal_List.txt'


#input_file ='evald_interface_list_RBBG.yml'
#output_file = 'evald_interface_list_RBBG_output.yml'
#MF4_file = 'SW_4_3_0_ODS_Signal_List.txt'

inp_file = open(input_file, "r")
out_file = open(output_file, "w+")

list_rows_from_file = []

def Read_MF4_txt_file():
    """ """
    MF4_dbc_file = open(MF4_file, "r")
    for x in MF4_dbc_file:
        list_rows_from_file.append(x)
    MF4_dbc_file.close()

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
    for el_from_MF4_file in list_rows_from_file:
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

    #print(list_rows_from_file)
    is_found=False
    found_string=""
    for el_from_MF4_file in list_rows_from_file:
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


Read_MF4_txt_file()

for current_obj in inp_file:
    if (current_obj.find('Alias: "')>=0):
        old_name=current_obj[current_obj.find('Alias: "')+len('Alias: "'):].replace('$"','')
        print("OLD NAME FROM EXCEL       = ", old_name.replace('\n',''))
        if (old_name.find(".*")>=0):
            alias_best_match = FindBestMatch_Wildcards(old_name.replace('\n', ''))
        else:
            alias_best_match=FindBestMatch(old_name.replace('\n',''))
        out_file.write('         Alias: "'+alias_best_match+'$"\n')
        #out_file.write('         PrevA: "' + old_name.replace('\n','')+'$"\n')
    else:
        out_file.write(current_obj)


inp_file.close()
out_file.close()

