# -*- coding: utf-8 -*-
# @file Update_EVALD_signal_list_YML__from_A2L_file.py
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
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import sys, os

logger_path = os.path.abspath(os.path.join(os.getcwd(), r"..\..\Platform\Classe\Scripts\Control"))
sys.path.append(logger_path)
from logging_config import logger

def get_input_file():
    """ """
    return easygui.fileopenbox("Select the <<evald_interface_list.yml>> file : ")

def get_A2L_file():
    """ """
    return easygui.fileopenbox("Select the A2L file as a DATABASE : ")

#input_file ='evald_interface_list_RBBG_2.yml'
output_file = 'evald_interface_list_RBBG_output.yml'
#A2L_file ='RadarFC.a2l'

def Reduce_A2L_Items_Names():
    """ """
    for el in list_a2l_items:
        #temp_list=Multiple_Split(el,["._.",""])
        temp_str=""
        if (el.find("._.")>=0):
            idx=el.find("._.")
            temp_str=el[idx+2:]
        else:
            temp_str=el
        # element [0] - full name, el[1] - reduced name
        Reduced_A2L_Items_Names.append([el,temp_str])

def Read_A2L_file():
    """ """
    f1 = open(A2L_file, "r")
    for x in f1:
        list_rows_from_a2l_file.append(x)
    f1.close()

def Extract_A2l_Variables():
    """ """
    #add the MEASUREMENTS
    for el in list_rows_from_a2l_file:
        if (el.find("/begin MEASUREMENT ")>=0):
            temp_str=el.replace("    /begin MEASUREMENT ","")
            temp_str=temp_str.split(' "')[0]
            temp_str = temp_str.replace('\n', '')
            list_a2l_items.append(temp_str)
            # add the MEASUREMENTS
    # add the CHARACTERISTICS
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
    logger.info("DEBUG max intersection = ", max_prob)
    if (max_prob<3):    #ignore all results if prob <30%
        logger.info("!!! BEST MATCH is NOT proper to be used (last 2 words do NOT match 100%) - ORIGINAL STRING WILL BE LEFT !!!")
        logger.info(f"ORIGINAL = {string_to_update}")
        logger.info("=" * 100)
        logger.info("=" * 100)
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
    logger.info(f"BEST MATCH                = {best_match}")
    logger.info(f"BEST PROBABILITY          = {max_element[0]}")
    best_match_splitted=best_match.split(".")
    original_string_splitted=string_to_update.split(".")
    #print("STR TO UPDATE splitted",original_string_splitted)
    #print("BEST MATCH splitted   ",best_match_splitted)
    logger.info(f"LAST WORD = {best_match_splitted[len(best_match_splitted)-1]}")
    logger.info(f"BEFORE THE LAST WORD = {best_match_splitted[len(best_match_splitted) - 2]}")
    if ( (best_match_splitted[len(best_match_splitted)-1] in original_string_splitted) and (best_match_splitted[len(best_match_splitted)-2] in original_string_splitted) ):
        logger.info("BEST MATCH is proper to be used (last 2 words match 100%)")
        logger.info("=" * 100)
        logger.info("=" * 100)
        return best_match
    else:
        print("!!! BEST MATCH is NOT proper to be used (last 2 words do NOT match 100%) - ORIGINAL STRING WILL BE LEFT !!!")
        print(f"ORIGINAL = {string_to_update}")
        logger.info("=" * 100)
        logger.info("=" * 100)
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
    logger.info(f"!DEBUG wildcards words_list= {words_list}")

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
        logger.info(f"BEST MATCH                = {found_string}")
        logger.info("=" * 100)
        logger.info("=" * 100)
        return found_string
    else:
        print("!!! NOTHING FULFILLS THE WILDCARDS- ORIGINAL STRING WILL BE LEFT !!!")
        print(f"ORIGINAL = {string_to_update}")
        logger.info("=" * 100)
        logger.info("=" * 100)
        return string_to_update


def main_sequence():
    """ """
    try:
        inp_file = open(get_input_file(), "r")
        out_file = open(get_A2L_file(), "w+")


        list_rows_from_a2l_file = []
        list_rows_from_a2l_file.clear()
        Read_A2L_file()
        list_a2l_items=[]
        list_a2l_items.clear()
        Extract_A2l_Variables()


        #element [0] - full name, el[1] - reduced name
        Reduced_A2L_Items_Names=[]
        Reduced_A2L_Items_Names.clear()
        Reduce_A2L_Items_Names()

        excel_output_list=[]
        excel_output_list.clear()
        for current_obj in inp_file:
            if (current_obj.find('Alias: "')>=0):
                old_name=current_obj[current_obj.find('Alias: "')+len('Alias: "'):].replace('$"','')
                logger.info("OLD NAME FROM EXCEL       = {}".format(old_name.replace('\n','')))
                if (old_name.find(".*")>=0):
                    alias_best_match = FindBestMatch_Wildcards(old_name.replace('\n', ''))
                else:
                    alias_best_match=FindBestMatch(old_name.replace('\n',''))
                out_file.write('         HIL_A: "'+alias_best_match+'$"\n')
                out_file.write('         Alias: "' + old_name.replace('\n','')+'$"\n')
                if (old_name.replace('\n','')==alias_best_match):
                    excel_output_list.append([old_name.replace('\n',''), "not_found"])
                else:
                    excel_output_list.append([old_name.replace('\n',''), alias_best_match])
            else:
                out_file.write(current_obj)


        inp_file.close()
        out_file.close()

        #save to EXCEL
        evald_names = pd.DataFrame(excel_output_list, columns=['Original Name','A2L_mapped_Name'])
        writer = pd.ExcelWriter('FDX_Database_checks_out.xlsx', engine='xlsxwriter')
        evald_names.to_excel(writer, sheet_name='xcpChecksDatabase')
        writer.save()
        return True
    except Exception as e:
        logger.error(f"Failure reason {e}")
        return False