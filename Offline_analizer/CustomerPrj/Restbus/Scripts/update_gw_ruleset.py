# -*- coding: utf-8 -*-
# @file update_gw_ruleset.py
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


import numpy as np
import pandas as pd
# Set the option to opt-in to the future behavior
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import sys, os

try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger

try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import *
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\CustomerPrj\Restbus\Scripts")
    from pattern_matching import *

column_names = ["Name", "group", "pdu", "Message", "Multiplexing/Group", "Startbit", "Length [Bit]", "Byte Order", "Value Type", "Initial Value", "Factor", "Offset", "Minimum", "Maximum", "Unit", "Value Table", "Comment", "Message ID", "Cycle Time [ms]", "texttable", "texttable values", "max_value", "dlc", "variant", "Src IP", "Dst IP", "Multi Dst IP", "Src Port", "Dst Port", "Vlan ID", "Src Mac", "Dst Mac", "sender", "gw", "a_variant_veh_0", "a_variant_veh_1", "b_variant_veh_0", "b_variant_veh_1"]

col_name = column_names.index("Name")
col_message = column_names.index("Message")
col_message_id = column_names.index("Message ID")
col_sender = column_names.index("sender")
col_gw = column_names.index("gw")
col_variant = column_names.index("variant")
col_a_variant_veh_0 = column_names.index("a_variant_veh_0")
col_a_variant_veh_1 = column_names.index("a_variant_veh_1")
col_b_variant_veh_0 = column_names.index("b_variant_veh_0")
col_b_variant_veh_1 = column_names.index("b_variant_veh_1")
col_variant = column_names.index("variant")
#allow longer names up to 100 characters
pd.options.display.max_colwidth = 100
pd.options.display.colheader_justify = 'left'
pd.set_option('mode.chained_assignment', None)

def checkVariant(vnt1,vnt2):
    """
    

    Args:
      vnt1: 
      vnt2: 

    Returns:

    """
    if ((vnt1=="a_variant") and (vnt2=="b_variant")) or ((vnt1=="b_variant") and (vnt2=="a_variant")):
        return False
    return True

def update_gw(database_array):
    """
    

    Args:
      database_array: 

    Returns:

    """
    if len(nwt_priority_list)==0:
        logger.info("No gateway messages given in the list hence gateway not filled")
        return database_array
    count_1 = 0
    gw_count = 1
    # get a copy of database array
    origin_database_array = np.copy(database_array)
    # filter column counter_crc with empty
    # change other signals to empty
    #signal_name_array = np.where(sysvar_filter_out_pattern(database_array[:, col_message],database_array[:, col_name]) == None, database_array[:, col_name], '')#Filter out Diag ,Alive counter,CRC and CHKSUM
    gw_filter_index = np.array([gateway_filter_out_pattern(msg, sig) for msg, sig in database_array[:, [col_message, col_name]]])
    signal_name_array = np.where(gw_filter_index == None, database_array[:, col_name], '')
    # replace signal name in database
    database_array[:, col_name] = signal_name_array
    # remove empty from signal name array
    signal_name_array = signal_name_array[signal_name_array != '']
    signal_count = signal_name_array.shape[0]
    signal_name_list = sorted(list(set(signal_name_array)))
    uni_signal_count = len(signal_name_list)
    for name in signal_name_list:
        name_index = np.where(database_array[:, col_name] == name)[0]
        # case 1: unique signal name: not mark gw
        if len(name_index) == 1:
            count_1 += 1
        else:
            # case 2: same signal name
            #rule to fill GW : same signal name & same msg ID & different msg name
            signal_names = list(database_array[name_index, col_name])  # returns list of signal names present in the index name_index
            message_names = list(database_array[name_index, col_message])  # returns list of message names present in the index name_index
            message_id_list = list(database_array[name_index, col_message_id])  # returns list of message ID  present in the index name_index
            variant_list = list(database_array[name_index, col_variant])  # returns list of variant col  present in the index name_index

            if len(set(message_id_list))!=len(message_id_list) and len(set(signal_names))==1:#signal names are same and atleast 2 msg IDs are same
                temp_df = pd.DataFrame(message_id_list,columns=["msgID"])
                for msgid in set(message_id_list):
                    if message_id_list.count(msgid)>1:#check msg IDs are repated in list
                        list_index = temp_df[temp_df.msgID == msgid].index.tolist()#taking the index of msg ID from dataframe
                        temp_messages=[message_names[i] for i in  list_index]
                        if len(set(temp_messages)) == len(temp_messages):#checking whether the msg name is different
                            for lst_indx in list_index:
                                for nwt_index in range(len(nwt_priority_list)):
                                    patt = str(nwt_priority_list[nwt_index])
                                    if re.search(patt,message_names[lst_indx]) != None:  # if msg name starts with FD3 n/w name
                                        index = name_index[lst_indx]# finding the index to fill gateway count
                                        origin_database_array[index, col_gw] = gw_count+(nwt_index/10)  # updating the gateway count for FD3 as integer value(master)
                            gw_count += 1#increament the GW count

    #case3: same signal name with variant match(a/b to a/b,a/b to common)
    for name in signal_name_list:
        name_index = np.where((origin_database_array[:, col_name] == name) & (origin_database_array[:, col_gw] == ''))[0]

        if len(name_index) == 1:
            count_1 += 1
        else:
            message_names = list(database_array[name_index, col_message])  # returns list of message names present in the index name_index
            variant_list = list(database_array[name_index, col_variant])  # returns list of variant col  present in the index name_index
            df_gw = pd.DataFrame(list(zip(message_names, variant_list)), columns=["msg", "var"])
            master_df = df_gw[df_gw['msg'].str.contains(nwt_priority_list[0])]

            dfs = []
            for ptn in nwt_priority_list[1:]:
                temp_df = df_gw[df_gw['msg'].str.contains(ptn)]
                if not (temp_df.empty):
                    dfs.append(temp_df)

            fill_gw_list = {}
            if dfs != []:
                for m_row in master_df.iterrows():
                    for s_df in dfs:
                        for s_row in s_df.iterrows():
                            v_m = m_row[1]["var"]
                            v_s = s_row[1]["var"]
                            if checkVariant(v_m, v_s) and not (s_df.empty):
                                m_msg = m_row[1].msg
                                s_msg = s_row[1].msg
                                s_df = s_df.drop(s_row[0], axis=0)

                                if m_msg not in fill_gw_list.keys():
                                    fill_gw_list[m_msg] = [s_msg]
                                else:
                                    fill_gw_list[m_msg].append(s_msg)

            if fill_gw_list != {}:
                for key in fill_gw_list.keys():
                    temp_list = fill_gw_list[key]
                    temp_list.append(key)
                    temp_list = list(set(temp_list))
                    for msg in temp_list:
                        for nwt_index in range(len(nwt_priority_list)):
                            patt = str(nwt_priority_list[nwt_index])
                            if re.search(patt, msg) != None:  # if msg name starts with FD3 n/w name
                                index = name_index[message_names.index(msg)]  # finding the index to fill gateway count
                                origin_database_array[index, col_gw] = gw_count + (nwt_index / 10)  # updating the gateway count for FD3 as integer value(master)
                    gw_count += 1

    logger.info("==================== Summary of gw ====================")
    logger.info("The number of signals (filtered with counter_crc): {0} no duplicates, {1} including duplicates.".format(uni_signal_count, signal_count))
    logger.info("The number of signals with unique names: {0}.".format(count_1))
    logger.info("The number of signals marked with GW: {0}.".format((gw_count-1)*2))

    return origin_database_array
