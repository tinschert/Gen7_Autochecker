# -*- coding: utf-8 -*-
# @file pattern_matching.py
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


import re
import pandas as pd

#KPI
dict_channel_nwtName_mapping = {"CAN1":"CAN_ADAS", "CAN3":"CAN_RadarFC", "CAN4":"CAN_RadarFR", "CAN5":"CAN_RadarFL", "CAN6":"CAN_MPC3"}


duplicate_columnlist_sysvar = ['Name', 'PDU', 'Message', 'Message ID', 'sender']#add column names here to check duplicates in sysvar database

#pattern for GW rule set
nwt_priority_list = []#list shall be kept empty if GW ruleset is not specified by customer, to avoid entering GW ruleset function
pdu_skip = ['RFC_FieldDataCollection','RFL_FieldDataCollection','RFR_FieldDataCollection','RRL_FieldDataCollection','RRR_FieldDataCollection']
#signal group for each node #In initialization functions the signals are split into groups of 25. So max number of signals is 25*sig group(125 for OD)
dict_sigGroupCount_nodeName_mapping = {"CRadarFL":"400", "Toliman":"125", "CRadarFR":"400", "CRadarRL":"400", "CRadarRR":"400", "CRadarFC":"400", "RBS":"400"}

#NOTE : rule to fill GW : same signal name & same msg ID & different msg name
#filter out for gw
version_msg_pattern = r'.*VERSION|version.*'#added for GW logic
supervision_msg_pattern = r'.*SUPERVISION|supervision.*'#added for GW logic

#RBS node
rbs_sheet_name = 'CAN_FD3_Rbs' #RBS Sheet Pattern

#Message Pattern
NPDU_FC_Pattern=r'.*_TPFC$'
TimeStamp_pattern=r'.*_TimeStamp$'
diag_msg_pattern  = r'.*DIAG|UDS.*'
stbm_msg_pattern  = r'(?:.*SYNC|Sync|sync|FUP|Fup|fup.*)'
vsm_msg_pattern   = r'.*VSM.*'
flt_evt_msg_pattern = r'.*FLT_EVT|FLT_EVENT.*'

#Signal Pattern
#ac_sig_pattern    = r'.*AliveCounter|BLOCK_INDEX|CPT_PROCESS.*' #Alive counter or Block index

bc_sig_pattern_1    = r'.*BlockCounter|BlockCtr.*' #Block counter signal
bc_sig_pattern_2    = r'.*Hdr.*' #Header Block counter message

ac_sig_pattern_1    = r'(?:.*(?:Alive)?_?(?:Counter|Ctr$|Cnt.?$).*(?<!BlockCtr)(?<!CycCnt)(?<!RolingCounter)|_BZ$|_AC$|AC$)|.*_SQC$' #Alive counter :: Public CAN
fn_sig_pattern_3    = r'.*_*FrameNumber.*' #FrameNumber :: Private CAN

ts_sig_pattern_1    = r'.*TimeStamp$'            #Time stamp
ts_sig_pattern_2    = r'.*TspLastMeas$'            #Time stamp

CRC_sig_pattern_0  = r'.*(?:Checksum|_?CRC.?$|CS.?$)(?<!_TCS)'
crc_sig_pattern_1   = r'.*_*CheckSum.*'              #CHKSUM
crc_sig_pattern_2   = r'.*_*CRC.?$'              #CRC
crc_sig_pattern_3   = r'.*_*Status.*'           #CRC

#Message
Msg_ACK_FLT_EVENT= 'FD3_ACK_FLT_EVENT_540'
delay_ACK_FLT_EVENT = '10'


filter_signal_for_sysvar = [ts_sig_pattern_1, ts_sig_pattern_2] #list of signal pattern to exclude default fault injection

filter_sysvar_IL = [ac_sig_pattern_1,CRC_sig_pattern_0,crc_sig_pattern_2,bc_sig_pattern_1,fn_sig_pattern_3,ts_sig_pattern_1,ts_sig_pattern_2]

filter_msg_pattern_list = [diag_msg_pattern,stbm_msg_pattern,flt_evt_msg_pattern]
filter_sig_pattern_list = [ac_sig_pattern_1,fn_sig_pattern_3,bc_sig_pattern_1,CRC_sig_pattern_0,crc_sig_pattern_2]

########---------------CAN-TP Patterns(LGU(Location)/SGU(Object))--------------------###########
#Sys var generation pattern for Npdu
Npdu_sig_patterns = r"\w+_\w+_Obj\d+_\w+"#for location : r"\w+_\w+_Loc\d+_\w+"
 
#ADAS HIL specific part
#Adding the part to get the byte array from the radar model with conditionnal compiling
#As it is needed only for objects, we check for the object pdu
pdu_name_pattern = "Object"#for location : pdu_pattern_write = "Location"
pdu_shortname_pattern = "Obj"#for location : pdu_shortname_pattern = "Loc"
radar_variant_type = ["FC","FL","FR","RL","RR"]
read_sysvar_pattern = "_Object_Obj" #for location : "RXX_Location_Loc"

#panel_scripting
can_network_name_column_name = "network_name"
can_sender_column_name = "sender"
can_message_column_name = "Message"
pdu_type_column_name = "PDU_Type"
signal_column_name = "Signal"
signal_group_column_name = "Signal_Group"
def get_can_fault_inject_property(network_name, message_name, pdu, signal):
    can_fault_inject_property = f"8;16;{network_name}::{message_name};;;{signal}_FaultInject;1;;;-1;;;;;;0"
    return can_fault_inject_property
def get_can_fault_inject_cntcycle_property(network_name, message_name, pdu, signal):
    can_fault_inject_cntcycle_property = f"8;16;{network_name}::{message_name};;;{signal}_FaultInject_CntCycle;1;;;-1;;;;;;0"
    return can_fault_inject_cntcycle_property
def get_can_text_box_property(network_name, sender, message_name, pdu, signal):  
    can_text_box_property = f"8;2;{network_name};{sender};{message_name};{signal};1;{network_name};;-1;;;;;;0"
    return can_text_box_property
def get_can_track_bar_property(network_name, sender, message_name, pdu, signal):
    can_track_bar_property = f"8;2;{network_name};{sender};{message_name};{signal};1;{network_name};;-1;;;;;;0"
    return can_track_bar_property
def get_can_cycle_time_text_bix_property(network_name, message_name, pdu):
    can_cycle_time_text_box_property = f"8;16;{network_name}::{message_name};;;{message_name}_CycleTime;1;;;-1;;;;;;0"
    return can_cycle_time_text_box_property
def get_can_on_off_check_box_property(network_name, message_name, pdu):
    can_on_off_check_box_property = f"8;16;{network_name}::{message_name};;;{message_name}_ON_OFF;1;;;-1;;;;;;0"
    return can_on_off_check_box_property

network_name_mapping = {
    "CAN_ADAS": "OD_ADAS_Public_CANFD",
    "CAN_MPC3": "OD_FV_Public_CAN",
    "CAN_RadarFC": "PF_RA6_SGU_FC",
    "CAN_RadarFL": "PF_RA6_SGU_FL",
    "CAN_RadarFR": "PF_RA6_SGU_FR",
    "CAN_RadarRL": "PF_RA6_SGU_RL",
    "CAN_RadarRR": "PF_RA6_SGU_RR"
}
 
sender_mapping = {"CAN_ADAS": {"DASy": "ADAS", "DMS": "DMS", "IMU": "IMU_MMP2", "Map": "MAP", "Rbs": "MGW"},
                  "CAN_MPC3": {"MPC3": "MGW"},
                  "CAN_RadarFC": {"CRadarFC": "RA6", "Toliman": "VectorSimulationNode"},
                  "CAN_RadarFL": {"CRadarFL": "RA6", "Toliman": "VectorSimulationNode"},
                  "CAN_RadarFR": {"CRadarFR": "RA6", "Toliman": "VectorSimulationNode"},
                  "CAN_RadarRL": {"CRadarRL": "RA6", "Toliman": "VectorSimulationNode" },
                  "CAN_RadarRR": {"CRadarRR": "RA6", "Toliman": "VectorSimulationNode"}}

crc_patternlist =[CRC_sig_pattern_0,crc_sig_pattern_1,crc_sig_pattern_2]
ac_patternlist = [ac_sig_pattern_1]

def generate_target_radar_sysvar(node_name, radar_id):
    write_list = []
 
    write_list.append("    #if ADAS_HIL")
    write_list.append(f"      if(@hil_ctrl::ra6_{node_name[-2:].lower()}_sgu_obj_sim!=0)")#for location : locdata.location_model
    write_list.append("      {")
    write_list.append(f"        dllGetRadar{node_name[-2:].upper()}ByteArray(@hil_ctrl::Handle_RoadObj, byteArray);")
    write_list.append(f"        dllResetByteArrayRadar{node_name[-2:].upper()}(@hil_ctrl::Handle_RoadObj);")
    write_list.append("      }")
    write_list.append("      else")
    write_list.append("      {")
    write_list.append("    #endif")
    return write_list

def generate_Set_Read_Number_of_signals(read_sig_para_dict):
    """


    Args:
      network_name:
      pdu_name:

    Returns:

    """
    network_name = read_sig_para_dict['network_name']
    pdu_name = read_sig_para_dict['pdu']
    node_name = read_sig_para_dict['node_name']
    read_num_sig_list = []
    if pdu_name not in pdu_skip:
        read_num_sig_list.append('on sysvar_update {0}_{1}::Read_No_signals'.format(network_name, pdu_name))
        read_num_sig_list.append('{')
        read_num_sig_list.append('  for (i=1;i<=@this;i++) //enable signal read;')
        read_num_sig_list.append('   {')
        read_num_sig_list.append(f'    snprintf(sysvarElementName, elcount(sysvarElementName), "{read_sysvar_pattern}%d.Read", i );')
        read_num_sig_list.append('    sysSetVariableint(mSysVarNameSpace_{0}_{1},sysvarElementName, 1);'.format(network_name, pdu_name))
        read_num_sig_list.append('   }')
        read_num_sig_list.append('  for (i=@this;i<=500;i++) //disable signal read;')
        read_num_sig_list.append('   {')
        read_num_sig_list.append(f'    snprintf(sysvarElementName, elcount(sysvarElementName),  "{read_sysvar_pattern}%d.Read", i );')
        read_num_sig_list.append('    sysSetVariableInt(mSysVarNameSpace_{0}_{1}, sysvarElementName, 0);'.format(network_name, pdu_name))
        read_num_sig_list.append('   }')
        read_num_sig_list.append('}')

    return read_num_sig_list
########---------------CAN-TP Patterns(LGU(Location)/SGU(Object))--------------------###########

def filterSignalForSysvar(signal_name):
    """
    

    Args:
      signal_name: 

    Returns:

    """
    for pattern in filter_signal_for_sysvar:
        matchObj = re.search( pattern, signal_name, re.M|re.I)
        if(None!=matchObj):
            return 1
    return 0

def filter_column_df(db_df,message_index,sig_index):
    """
    Filters the given DataFrame based on the provided message and signal patterns.

    Args:
        db_df (pandas.DataFrame): The DataFrame to be filtered.
        message_index (str): The column name or index of the message column.
        sig_index (str): The column name or index of the signal column.

    Returns:
        pandas.DataFrame: The filtered DataFrame.
    """
    for msg_pattern in filter_msg_pattern_list:
        db_df = db_df[(db_df[message_index].fillna('').str.contains(msg_pattern, flags=re.IGNORECASE, regex=True) == False) | (db_df[message_index].isna())]  # Filter out Message

    for sig_pattern in filter_sig_pattern_list:
        db_df = db_df[(db_df[sig_index].fillna('').str.contains(sig_pattern, flags=re.IGNORECASE, regex=True) == False) | (db_df[sig_index].isna())]  # Filter out Signal

    return db_df

def filter_sysvarDF_IL(sysvar_df, col_name):
    """
    

    Args:
      sysvar_df: 
      col_name: 

    Returns:

    """
    return sysvar_df[sysvar_df[col_name].str.contains("|".join(filter_sysvar_IL), flags=re.IGNORECASE)]


def match_pattern(string,pattern):
    """
    

    Args:
      string: 
      pattern: 

    Returns:

    """
    matchObj = re.search( pattern, string, re.M|re.I)
    if(None!=matchObj):
        #print("Match Found :: "+" String :"+string+" Pattern :"+pattern)
        return 1
		

def get_message_type(message):
    """
    

    Args:
      message: 

    Returns:

    """
    msg_pattern_1    = r'.*Location|location.*' #Location
    msg_pattern_2    = r'.*Object|object|Obj.*' #Object
    msg_pattern_3    = r'.*Lane|lane.*' #Lane
    msg_pattern_4    = r'.*TrafficSign|trafficSign|Trafficsign|trafficsign.*' #TrafficSign
    msg_pattern_5    = r'.*Road.*' #Road
    msg_pattern_6    = r'.*TrafficLight.*' #TrafficLight
    if(None!=re.search( msg_pattern_1, message, re.M|re.I)):#Pattern :: if it is Location message
        return message.split('_')[0]+"_Location"
    if(None!=re.search( msg_pattern_2, message, re.M|re.I)):#Pattern :: if it is Object message
        return message.split('_')[0]+"_Object"
    if(None!=re.search( msg_pattern_3, message, re.M|re.I)):#Pattern :: if it is Lane message
        return message.split('_')[0]+"_Lane"
    if(None!=re.search( msg_pattern_4, message, re.M|re.I)):#Pattern :: if it is TrafficSign message
        return message.split('_')[0]+"_TrafficSign"
    if(None!=re.search( msg_pattern_5, message, re.M|re.I)):#Pattern :: if it is Road message
        return message.split('_')[0]+"_Road"
    if(None!=re.search( msg_pattern_6, message, re.M|re.I)):#Pattern :: if it is TrafficLight message
        return message.split('_')[0]+"_TrafficLight"

def filter_column_sysvar(msg_name,sig_name):#Filter out 
    """
    

    Args:
      msg_name: 
      sig_name: 

    Returns:

    """
    msg    =  str(msg_name)#message
    sig    =  str(sig_name)#signal
        
    for msg_pattern in filter_msg_pattern_list:
        matchObj = re.search( msg_pattern, msg, re.M|re.I)
        if(None!=matchObj):
            return 1

    for sig_pattern in filter_sig_pattern_list:
        matchObj = re.search( sig_pattern, sig, re.M|re.I)
        if(None!=matchObj):
            return 1     
    return None

def gateway_filter_out_pattern(msg_name, sig_name):  # Filter out
    """
    

    Args:
      msg_name: 
      sig_name: 

    Returns:

    """
    msg = str(msg_name)  # message
    sig = str(sig_name)  # signal

    matchObj = re.search(version_msg_pattern, msg, re.M | re.I)  # VERSION
    if (None != matchObj):
        return 1
    matchObj = re.search(supervision_msg_pattern, msg, re.M | re.I)  # SUPERVISION
    if (None != matchObj):
        return 1
    for msg_pattern in filter_msg_pattern_list:
        matchObj = re.search( msg_pattern, msg, re.M|re.I)
        if(None!=matchObj):
            return 1

    for sig_pattern in filter_sig_pattern_list:
        matchObj = re.search( sig_pattern, sig, re.M|re.I)
        if(None!=matchObj):
            return 1
    return None

def rbs_node_ack(bus_type,input_file):
    """
    

    Args:
      bus_type: 
      input_file: 

    Returns:

    """
    node =[]
    if ((bus_type.upper() == 'ETH')):
        node.append('  pdu {0} Msg_{0};'.format(Msg_ACK_FLT_EVENT))
    elif ((bus_type.upper() == 'CAN') or (bus_type.upper() == 'CANFD')):
        if input_file=="dbc":
            node.append('  message {0} Msg_{0};'.format(Msg_ACK_FLT_EVENT))
        elif input_file=="arxml":
            node.append('  pdu {0} Msg_{0};'.format(Msg_ACK_FLT_EVENT))
    node.append('  msTimer PROJ_DEH_Msg_ACK_Delay_ms;')
    node.append('')
    return node

def rbs_node_ack_onmsg(flt_evt_node):
    """
    

    Args:
      flt_evt_node: 

    Returns:

    """
    node=[]
    node.extend(flt_evt_node)
    flt_evt_node = ['']  # clear data
    node.extend(ACK_FLT_EVENT())
    node.append('')
    return node,flt_evt_node

def AC_SIG_1(para_dict):
    """
    

    Args:
      para_list: 

    Returns:

    """
    namespace = para_dict["namespace"] # namespace->Message name
    signal_name = para_dict["signal_name"]
    sig_length = para_dict["sig_length"]
    bus_type = para_dict["bus_type"]
    input_file = para_dict["input_file"]
    msg_list=[]
    msg_list.append('  word counter_{0}_{1};'.format(namespace,signal_name))
    return msg_list

def BC_SIG_1(para_dict):
    """
    

    Args:
      para_dict: Dictionary containing parameters

    Returns:

    """
    namespace = para_dict["namespace"] # namespace->Message name
    signal_name = para_dict["signal_name"]
    sig_length = para_dict["sig_length"]
    bus_type = para_dict["bus_type"]
    input_file = para_dict["input_file"]
    msg_list=[]
    msg_list.append('  dword bc_{0}_{1};'.format(namespace,signal_name))
    if(None!=re.search( bc_sig_pattern_2, namespace, re.M|re.I)):#Pattern :: if it is Header Block message
        if(None!=re.search( r'^RFC.*', namespace, re.M|re.I)):#Pattern :: #RFC Messages
            if(None!=re.search( r'.*A$', namespace, re.M|re.I)):#Pattern :: #RFC HeaderA Messages
                msg_list.append('  dword bc_{0}_ProtBlockCtr;'.format(get_message_type(namespace)))
        else:
            if(None==re.search( r'.*Center|center|Central|central.*', namespace, re.M|re.I)):#Pattern :: #Center|Central
                msg_list.append('  dword bc_{0}_ProtBlockCtr;'.format(get_message_type(namespace)))
    return msg_list

def TS_SIG_1(para_dict):
    """
    

    Args:
      para_dict: Dictionary containing parameters

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    msg_list=[]
    msg_list.append('  dword ts_{0}_{1};'.format(namespace,signal_name))
    return msg_list

def findEndBit(startbit,bitlength):   # ONLY FOR MOTOROLA
    """
    

    Args:
      startbit: 
      bitlength: 

    Returns:

    """
    count = 1
    while count!=bitlength:
        if (startbit+1) % 8 == 0:
            startbit -= 16
        count += 1
        startbit += 1
    return int(startbit)

def findStartBit(startbit, length):# ONLY FOR MOTOROLA arxml
    """
    

    Args:
      startbit: 
      length: 

    Returns:

    """
    if length<1:
        return int(startbit)
    while length != 1:
        if startbit % 8 == 0:
            startbit += 16
        length -= 1
        startbit -= 1
    return int(startbit)

def Get_DataLength(First_sig_startbit,First_sig_length,Last_sig_startbit,Last_sig_length,byte_order):
    """
    

    Args:
      First_sig_startbit: 
      First_sig_length: 
      Last_sig_startbit: 
      Last_sig_length: 
      byte_order: 

    Returns:

    """
    if ('Moto' in byte_order) or ('moto' in byte_order) or ('rola' in byte_order) or ('Big' in byte_order) or ('big' in byte_order):
        Last_sig_Endbit =   findEndBit(Last_sig_startbit,Last_sig_length)#Last_sig_Endbit   = findEndBit(Last_sig_startbit,Last_sig_length)
    else:
        Last_sig_Endbit =   Last_sig_startbit + Last_sig_length -1
    if(Last_sig_startbit>Last_sig_Endbit):
        Last_sig_Endbit=Last_sig_startbit
    numBytes = (Last_sig_Endbit - First_sig_startbit + 1) / 8 + ((Last_sig_Endbit - First_sig_startbit + 1) % 8 != 0) 
    return int(numBytes)
    
def copyData(var,startbit,bitlength,byte_order):
    """
    

    Args:
      var: 
      startbit: 
      bitlength: 
      byte_order: 

    Returns:

    """
    msg_list=[]
    msg_list.append('')
    if ('Moto' in byte_order) or ('moto' in byte_order) or ('rola' in byte_order) or ('Big' in byte_order) or ('big' in byte_order):
        endbit=int(findEndBit(startbit,bitlength))
        #msg_list.append('      clearBitsInByteArrayBE(data,{0},{1},{2}); //Motorola / Big-endian'.format(startbit, endbit,bitlength))
        msg_list.append('      copyBitsToByteArrayBE({0},data,{1},{2}); //Motorola / Big-endian'.format(var,startbit,bitlength))
    else:
        #msg_list.append('      clearBitsInByteArrayLE(data,{0},{1}); //Intel / little-endian'.format(startbit,bitlength))
        msg_list.append('      copyBitsToByteArrayLE({0},data,{1},{2}); //Intel / little-endian;'.format(var,startbit,bitlength))
    return msg_list

def clearData(startbit,bitlength,byte_order):
    """
    

    Args:
      startbit: 
      bitlength: 
      byte_order: 

    Returns:

    """
    msg_list=[]
    msg_list.append('')
    if ('Moto' in byte_order) or ('moto' in byte_order) or ('rola' in byte_order) or ('Big' in byte_order) or ('big' in byte_order):
        endbit=int(findEndBit(startbit,bitlength))
        msg_list.append('    clearBitsInByteArrayBE(data,{0},{1},{2}); //Motorola / Big-endian'.format(startbit, endbit,bitlength))
    else:
        msg_list.append('    clearBitsInByteArrayLE(data,{0},{1}); //Intel / little-endian'.format(startbit,bitlength))
    msg_list.append('')
    return msg_list

def copySigGrp_Data(First_sig_startbit,First_sig_length,Last_sig_startbit,Last_sig_length,byte_order):
    """
    

    Args:
      First_sig_startbit: 
      First_sig_length: 
      Last_sig_startbit: 
      Last_sig_length: 
      byte_order: 

    Returns:

    """
    msg_list=[]
    if ('Moto' in byte_order) or ('moto' in byte_order) or ('rola' in byte_order) or ('Big' in byte_order) or ('big' in byte_order):
        Last_sig_Endbit =   findEndBit(Last_sig_startbit,Last_sig_length)#Last_sig_Endbit   = findEndBit(Last_sig_startbit,Last_sig_length)
    else:
        Last_sig_Endbit =   Last_sig_startbit + Last_sig_length -1
    if(Last_sig_startbit>Last_sig_Endbit):
        Last_sig_Endbit=Last_sig_startbit
    #print("First_sig_startbit",First_sig_startbit,"Last_sig_startbit",Last_sig_startbit,"Last_sig_Endbit",Last_sig_Endbit,"byte_order",byte_order)
    msg_list.append('    copyByteArrayToByteArray(data,SigGrp_Data,{0},{1});'.format(First_sig_startbit,Last_sig_Endbit))
    msg_list.append('')
    return msg_list

def SigGrp_ARILFaultInjectionDisturbSequenceCounter_onsysvar(para_dict):#Alive counter
    """
    

    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    network_name = para_dict["network_name"]
    signal_grp = signal_grp_info["siggrp"]
   
    msg_list=[]
    msg_list.append('on sysvar_update {2}::{0}::{1}_FaultInject'.format(namespace, signal_name, network_name))
    msg_list.append('{')
    msg_list.append('   long result;')
    msg_list.append('   long type=0;//reserved (should be set to 0).')
    msg_list.append('   long disturbanceMode = 0; //0 :: set to disturbanceValue //2 :: set to Random value //3 :: Offset Signal value is increased by disturbanceValue')
    msg_list.append('   long disturbanceCount=0;  //-1 ::Infinite Disturbance is continuously applied //0 ::Stop An active disturbance is stopped and the SequenceCounter will be calculated again appropriately //n > 0 ::Count Do exactly n Repetition/disturbances')
    msg_list.append('   long disturbanceValue =0;//According to the disturbance mode the SequenceCounter will optionally be set to this value')
    msg_list.append('   ')
    msg_list.append('   long continueMode=2;')
    msg_list.append('   //0 :: The counter will continue as if there had never been a disturbance [0, 1, 2, 6, 6, 5, 6]')
    msg_list.append('   //1 :: The counter will continue by increasing last valid counter [0, 1, 2, 6, 6, 3, 4]')
    msg_list.append('   //2 :: The counter will continue by increasing the last transmitted value [0, 1, 2, 6, 6, 7, 8]')
    msg_list.append('   ')
    msg_list.append('   if (@this == 0)//AC: No Error, calculate AC'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount=0;//0 Stop An active disturbance is stopped and the CRC will be calculated again appropriately')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: No Error");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@this == 1)//AC: Error , set AC = 0'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode   = 0;//Sets the AC fix to the value of parameter disturbanceValue.')
    msg_list.append('      disturbanceValue  = 0;//set AC = 0')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: AC = 0");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@this == 2)//AC: Error , Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode  = 1;//1 Freeze Current signal value is used (disturbanceValue is not used)')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: Freeze");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('}')
    #print (msg_list)
    return msg_list

def SigGrp_ARILFaultInjectionDisturbSequenceCounter(para_dict):#Alive counter
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    network_name = para_dict["network_name"]
    signal_grp = signal_grp_info["siggrp"]

    msg_list=[]
    #msg_list.append('on sysvar_update {2}::{0}::{1}_FaultInject'.format(namespace, signal_name, network_name))
    msg_list.append('{')
    #msg_list.append('   long result;')
    #msg_list.append('   long type=0;//reserved (should be set to 0).')
    #msg_list.append('   long disturbanceMode  =0; //0 :: set to disturbanceValue //2 :: set to Random value //3 :: Offset Signal value is increased by disturbanceValue')
    #msg_list.append('   long disturbanceCount =0;//-1 ::Infinite Disturbance is continuously applied //0 ::Stop An active disturbance is stopped and the SequenceCounter will be calculated again appropriately //n > 0 ::Count Do exactly n Repetition/disturbances')
    #msg_list.append('   long disturbanceValue =0;//According to the disturbance mode the SequenceCounter will optionally be set to this value')
    msg_list.append('   ')
    msg_list.append('   long continueMode=2;')
    msg_list.append('   //0 :: The counter will continue as if there had never been a disturbance [0, 1, 2, 6, 6, 5, 6]')
    msg_list.append('   //1 :: The counter will continue by increasing last valid counter [0, 1, 2, 6, 6, 3, 4]')
    msg_list.append('   //2 :: The counter will continue by increasing the last transmitted value [0, 1, 2, 6, 6, 7, 8]')
    msg_list.append('   ')
    msg_list.append('   if (@{2}::{0}::{1}_FaultInject == 0)//AC: No Error, calculate AC'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount=0;//0 Stop An active disturbance is stopped and the CRC will be calculated again appropriately')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: No Error");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@{2}::{0}::{1}_FaultInject == 1)//AC: Error , set AC = 0'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode   = 0;//Sets the AC fix to the value of parameter disturbanceValue.')
    msg_list.append('      disturbanceValue  = 0;//set AC = 0')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: AC = 0");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@{2}::{0}::{1}_FaultInject == 2)//AC: Error , Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode   = 1;//1 Freeze Current signal value is used (disturbanceValue is not used)')
    msg_list.append('      result=ARILFaultInjectionDisturbSequenceCounter ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue, continueMode);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbSequenceCounter :: {0} :: {1} :: {2} :: Freeze");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('}')
    #print (msg_list)
    return msg_list


def SigGrp_ARILFaultInjectionDisturbChecksum_onsysvar(para_dict):#CRC 
    """
    

    Args:
        para_dict (_type_): _description_

    Returns:
        _type_: _description_
    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    network_name = para_dict["network_name"]
    signal_grp = signal_grp_info["siggrp"]

    msg_list=[]
    msg_list.append('on sysvar_update {2}::{0}::{1}_FaultInject'.format(namespace, signal_name, network_name))
    msg_list.append('{')
    msg_list.append('  long result;')
    msg_list.append('  long type=0;//reserved (should be set to 0).')
    msg_list.append('  long disturbanceMode = 0; //0 :: set to disturbanceValue //2 :: set to Random value //3 :: Offset Signal value is increased by disturbanceValue')
    msg_list.append('  long disturbanceCount=0;  //-1 ::Infinite Disturbance is continuously applied //0 ::Stop An active disturbance is stopped and the CRC will be calculated again appropriately //n > 0 ::Count Do exactly n Repetition/disturbances')
    msg_list.append('   long disturbanceValue =0;//According to the disturbance mode the CRC will optionally be set to this value')
    msg_list.append('   ')
    msg_list.append('   if (@this == 0)//CRC: No Error, calculate CRC')
    msg_list.append('   {')
    msg_list.append('      disturbanceCount=0;//0 Stop An active disturbance is stopped and the CRC will be calculated again appropriately')
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: No Error");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@this == 1)//CRC: Error , set CRC = 0')
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode   = 0;//Sets the CRC fix to the value of parameter disturbanceValue.')
    msg_list.append('      disturbanceValue  = 0;//set CRC = 0')
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: AC = 0");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@this == 2)//CRC: Error , Freeze last valid value')
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = -1;//-1 Infinite Disturbance is continuously applied')
    msg_list.append('      disturbanceMode  = 1;//1 Freeze Current signal value is used (disturbanceValue is not used)')
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: Freeze");'.format(namespace,signal_grp,signal_name))
    msg_list.append('    }')
    msg_list.append('}')
    #print (msg_list)
    return msg_list

def SigGrp_ARILFaultInjectionDisturbChecksum(para_dict):#CRC
    """_summary_

    Args:
        para_dict (_type_): _description_

    Returns:
        _type_: _description_
    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    network_name = para_dict["network_name"]
    signal_grp = signal_grp_info["siggrp"]
    msg_list=[]
    #msg_list.append('on sysvar_update {2}::{0}::{1}_FaultInject'.format(namespace, signal_name, network_name))
    msg_list.append('{')
    #msg_list.append('  long result;')
    #msg_list.append('  long type=0;//reserved (should be set to 0).')
    #msg_list.append('  long disturbanceMode = 0; //0 :: set to disturbanceValue //2 :: set to Random value //3 :: Offset Signal value is increased by disturbanceValue')
    #msg_list.append('  long disturbanceCount =0; //-1 ::Infinite Disturbance is continuously applied //0 ::Stop An active disturbance is stopped and the CRC will be calculated again appropriately //n > 0 ::Count Do exactly n Repetition/disturbances')
    #msg_list.append('  long disturbanceValue =0;//According to the disturbance mode the CRC will optionally be set to this value')
    #msg_list.append('  dword crc[1];')
    #msg_list.append('   ')
    msg_list.append('   if (@{2}::{0}::{1}_FaultInject == 0)//CRC: No Error, calculate CRC'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    #msg_list.append('      disturbanceCount=0;//0 Stop An active disturbance is stopped and the CRC will be calculated again appropriately')
    msg_list.append('      disturbanceCount  = 1;//Once Disturbance is applied')
    msg_list.append('      disturbanceMode   = 0;//Sets the CRC fix to the value of parameter disturbanceValue.')
    msg_list.append('      ARILCalculateCRC("{0}","{1}",data,aPDULength,crc);//Profile 11A'.format(namespace, signal_grp))
    msg_list.append('      disturbanceValue=crc_{0}_{1}=crc[0]^0xFF;'.format(namespace,signal_name))
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: No Error");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@{2}::{0}::{1}_FaultInject == 1)//CRC: Error , set CRC = 0'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = 1;//Once Disturbance is continuously applied')
    msg_list.append('      disturbanceMode   = 0;//Sets the CRC fix to the value of parameter disturbanceValue.')
    msg_list.append('      disturbanceValue  = 0;//set CRC = 0')
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: AC = 0");'.format(namespace,signal_grp,signal_name))
    msg_list.append('   }')
    msg_list.append('   else if (@{2}::{0}::{1}_FaultInject == 2)//CRC: Error , Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('   {')
    msg_list.append('      disturbanceCount  = 1;//Once Disturbance is  applied')
    #msg_list.append('      disturbanceMode  = 1;//1 Freeze Current signal value is used (disturbanceValue is not used)')
    msg_list.append('      disturbanceMode   = 0;//Sets the CRC fix to the value of parameter disturbanceValue.')
    msg_list.append('      disturbanceValue  = crc_{0}_{1};'.format(namespace,signal_name))
    msg_list.append('      result=ARILFaultInjectionDisturbChecksum ({0}, "{1}", type, disturbanceMode, disturbanceCount, disturbanceValue);'.format(namespace,signal_grp))
    msg_list.append('      //write("ARILFaultInjectionDisturbChecksum :: {0} :: {1} :: {2} :: Freeze");'.format(namespace,signal_grp,signal_name))
    msg_list.append('    }')
    msg_list.append('}')
    #print (msg_list)
    return msg_list
	
def initialize_CRC_variable(para_dict):
    """
    

    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    sig_length = para_dict["sig_length"]

    variable_name = "crc" if "_crc" in signal_name.lower() else "chksum"
    if sig_length <= 8:
        return ['  byte {0}_{1}_{2};'.format(variable_name, namespace,signal_name)]
    else:
        return ['  dword {0}_{1}_{2};'.format(variable_name, namespace,signal_name)]
    
def get_data_id(endtoendprotection_info):
    """
    gets dataid from endtoendprotection_info and converts to hex format, if not found returns 0
    Args:
        endtoendprotection_info (str): endtoend protection column value example: 8452::AUTOSAR Profile 5
    """
    dataid = 0
    if endtoendprotection_info:
        e2e_split = endtoendprotection_info.split('::')
        if e2e_split[0].strip():
            try:
                dataid = int(e2e_split[0].strip())
                dataid = hex(dataid) if dataid>0 else 0
            except:
                return 0
    return dataid
    
        
def decide_CRC_logic(para_dict):
    """
    

    Args:
        para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    sig_length = para_dict["sig_length"]
    network_name = para_dict["network_name"]
    is_public_can = para_dict["is_public_can"]
    
    data_lookup = "Data_ID_Lookup" if is_public_can else "Data_ID_Lookup_PRIVATE"
    variable_name = "crc" if "_crc" in signal_name.lower() else "chksum"

    #exception case for mpc3 crc calculation where it uses 2 byte dataID and diff logic
    if "mpc3" in network_name.lower():
        return CRC_MPC3_LOGIC(para_dict,data_lookup, variable_name)

    if sig_length <=8:
        return CRC_CHKSUM_8BIT(para_dict,data_lookup, variable_name)
    else:
        return CRC_CHKSUM_16BIT(para_dict,data_lookup, variable_name)

def CRC_CHKSUM_8BIT(para_dict, data_lookup, variable_name):
    """
    

    Args:
      para_dict: 
      data_lookup: 
      variable_name: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
    endtoendprotection_info = para_dict["endtoendprotection"]

    dataid = get_data_id(endtoendprotection_info)

    msg_list = []
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject != 3)//CRC: user defined value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    }')
    msg_list.append('    if(@{2}::{0}::{1}_FaultInject == 0)//CRC: No Error, calculate CRC'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list.append('      xor = initialization_value;')
    msg_list.append('      for(i = 0; i < DataLength; i++)')
    msg_list.append('      {')
    msg_list.append('        if(i==0)')
    if dataid:
        msg_list.append(f'          xor = CRC8_SAE_J1850_Poly_1D_Lookup[{str(dataid)} ^ xor];')
    else:
        msg_list.append('          xor = CRC8_SAE_J1850_Poly_1D_Lookup[{0}(Msg_id) ^ xor];'.format(data_lookup))
    msg_list.append('        else')
    msg_list.append('          xor = CRC8_SAE_J1850_Poly_1D_Lookup[ data[i] ^ xor ];')
    msg_list.append('      }')
    msg_list.append('      {2}_{0}_{1} = result_XOR_value ^ xor;'.format(namespace, signal_name, variable_name))
    input_var = '{2}_{0}_{1}'.format(namespace, signal_name, variable_name)
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')
    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 1)//CRC: Error, set to Zero'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData('0', startbit, sig_length, byte_order)
    msg_list.append('    }')
    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 2)//CRC: Error, Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')
    # print (msg_list)
    return msg_list


def CRC_CHKSUM_16BIT(para_dict, data_lookup, variable_name):
    """
    

    Args:
      para_dict: 
      data_lookup: 
      variable_name: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
    endtoendprotection_info = para_dict["endtoendprotection"]

    dataid = get_data_id(endtoendprotection_info)

    msg_list = []
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject != 3)//CRC: user defined value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    }')
    msg_list.append('    if(@{2}::{0}::{1}_FaultInject == 0)//CRC: No Error, calculate CRC'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list.append('      crcTemp = CRC16_INIT;')
    msg_list.append('      for(i = 2; i < (DataLength+2); i++)')
    msg_list.append('      {')
    msg_list.append('        if(i < DataLength)')
    msg_list.append('          data_byte = data[i] ;')
    msg_list.append('        else if(i == DataLength)')
    if dataid:
        msg_list.append(f'          data_byte = ({str(dataid)} & 0x00FF);')
    else:
        msg_list.append('          data_byte = ({0}(Msg_id) & 0x00FF);'.format(data_lookup))
    msg_list.append('        else if(i == (DataLength+1))')
    if dataid:
        msg_list.append(f'          data_byte = ({str(dataid)} & 0xFF00) >> 8;')
    else:
        msg_list.append('          data_byte = ({0}(Msg_id) & 0xFF00) >> 8;'.format(data_lookup))
    msg_list.append('        else')
    msg_list.append('          write("Error: DLC exceeded in CRC calculation");')
    msg_list.append('        crcTemp ^= data_byte << 8;')
    msg_list.append('        crcTemp = (crcTemp << (8)) ^ CRC16_CCITT_FALSE_POLY_1021H_Lookup[(crcTemp >> (8)) & (0xFF)];')
    msg_list.append('      }')
    msg_list.append('      crcTemp ^= CRC16_XOR;')
    msg_list.append('      {2}_{0}_{1} = crcTemp;'.format(namespace, signal_name, variable_name))
    input_var = '{2}_{0}_{1}'.format(namespace, signal_name, variable_name)
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')
    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 1)//CRC: Error, set to Zero'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData('0', startbit, sig_length, byte_order)
    msg_list.append('    }')
    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 2)//CRC: Error, Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')
    # print (msg_list)
    return msg_list

def CRC_MPC3_LOGIC(para_dict, data_lookup, variable_name):
    """
    

    Args:
      para_dict: 
      data_lookup: 
      variable_name: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
    total_used_msg_bytes = para_dict["total_used_msg_bytes"]
    endtoendprotection_info = para_dict["endtoendprotection"]
    
    dataid = get_data_id(endtoendprotection_info)

    msg_list = []
    input_var = '{2}_{0}_{1}'.format(namespace, signal_name, variable_name)
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject != 3)//CRC: user defined value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    }')

    if dataid:
        msg_list.append(f'   messagebytes[0] = {str(dataid)};')
    else:
        msg_list.append('   messagebytes[0] = {0}(Msg_id);'.format(data_lookup))
    msg_list.append('   messagebytes[1] = 0x00;')
    msg_list.append('   crc_byte_no = {0};'.format(total_used_msg_bytes))
    msg_list.append('   for(loop_index=0;loop_index < {0} ;loop_index++)'.format(total_used_msg_bytes-1))
    msg_list.append('       messagebytes[loop_index+2] = data[loop_index+1];')
    msg_list.append('   ')
    msg_list.append('    if(@{2}::{0}::{1}_FaultInject == 0)//CRC: No Error, calculate CRC'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list.append('      {0} = CRC_Calc_SAEJ1850(crc_byte_no, messagebytes);'.format(input_var))
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')

    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 1)//CRC: Error, set to Zero'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData('0', startbit, sig_length, byte_order)
    msg_list.append('    }')
    msg_list.append(
        '    else if(@{2}::{0}::{1}_FaultInject == 2)//CRC: Error, Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list = msg_list + copyData(input_var, startbit, sig_length, byte_order)
    msg_list.append('    }')
    # print (msg_list)
    return msg_list


def CNT_ALIVE_1(para_dict):#Alive counter
    """
    

    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
    is_public_can = para_dict["is_public_can"]
    
    #print ("CNT_ALIVE_1 :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject != 3)//AC: user defined value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    }')
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject == 0)//AC: No Error, calculate AC'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list.append('      ++counter_{0}_{1};'.format(namespace,signal_name))
    if is_public_can:
        msg_list.append('      counter_{0}_{1} %={2};'.format(namespace,signal_name,(2**sig_length)-1))
    else:
        msg_list.append('      counter_{0}_{1} %={2};'.format(namespace,signal_name,2**sig_length))

    input_var ='counter_{0}_{1}'.format(namespace, signal_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    msg_list.append('    }')
    msg_list.append('    else if (@{2}::{0}::{1}_FaultInject == 1)//AC: Error sequence: set AC = 0'.format(namespace, signal_name,network_name))
    msg_list.append('    {')
    msg_list= msg_list + copyData('0',startbit,sig_length,byte_order)
    msg_list.append('    }')
    msg_list.append('    else if (@{2}::{0}::{1}_FaultInject == 2)//AC: Error sequence: Freeze last valid value'.format(namespace, signal_name,network_name))
    msg_list.append('    {')
    input_var ='counter_{0}_{1}'.format(namespace, signal_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    msg_list.append('    }')
    #print (msg_list)
    return msg_list


def CNT_BLOCK(para_dict):#Block counter
    """
    

    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]

    #print ("CNT_BLOCK :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject != 3)//BC: user defined value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    }')
    msg_list.append('    if (@{2}::{0}::{1}_FaultInject == 0)//BC: No Error, calculate BC'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    
    if(None!=re.search( bc_sig_pattern_2, namespace, re.M|re.I)):#Pattern :: Header Block counter message
        if(None!=re.search( r'^RFC.*', namespace, re.M|re.I)):#Pattern :: #RFC Messages
            if(None!=re.search( r'.*A$', namespace, re.M|re.I)):#Pattern :: #RFC HeaderA Messages
                msg_list.append('      ++bc_{0}_{1};'.format(namespace, signal_name))
                msg_list.append('      bc_{0}_{1} %=256;'.format(namespace, signal_name))
                msg_list.append('      bc_{2}_ProtBlockCtr = bc_{0}_{1} ;'.format(namespace,signal_name,get_message_type(namespace)))
            else:
                msg_list.append('      bc_{0}_{1} = bc_{2}_ProtBlockCtr ;'.format(namespace,signal_name,get_message_type(namespace)))
        else:
            msg_list.append('      ++bc_{0}_{1};'.format(namespace, signal_name))
            msg_list.append('      bc_{0}_{1} %=16;'.format(namespace, signal_name))
            msg_list.append('      bc_{2}_ProtBlockCtr = bc_{0}_{1} ;'.format(namespace,signal_name,get_message_type(namespace)))            
    else:
        if(None!=re.search( r'.*Center|center|Central|central.*', namespace, re.M|re.I)):#Pattern :: #Center|Central
            msg_list.append('      ++bc_{0}_{1};'.format(namespace, signal_name))
            msg_list.append('      bc_{0}_{1} %=16;'.format(namespace, signal_name))
        else:
            msg_list.append('      bc_{0}_{1} = bc_{2}_ProtBlockCtr ;'.format(namespace,signal_name,get_message_type(namespace)))
        
    input_var ='bc_{0}_{1}'.format(namespace, signal_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    msg_list.append('    }')
    msg_list.append('    else if (@{2}::{0}::{1}_FaultInject == 1)//BC: Error sequence: set BC = 0'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    input_var ='0'
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    msg_list.append('    }')
    msg_list.append('    else if (@{2}::{0}::{1}_FaultInject == 2)//BC: Error sequence: Freeze last valid value'.format(namespace, signal_name, network_name))
    msg_list.append('    {')
    input_var ='bc_{0}_{1}'.format(namespace, signal_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    msg_list.append('    }')
    #print (msg_list)
    return msg_list

def Fun_TimeStamp(para_dict):#Time stamp
    """
    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
  
    #print ("CNT_TIME_STAMP :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    //Msg_{0}.{1} = @{2}::{0}::{1}_FaultInject +(timeNowNS()/1000000);'.format(namespace, signal_name, network_name))
    input_var ='@{2}::{0}::{1}_FaultInject +(timeNowNS()/1000000)'.format(namespace, signal_name, network_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    #print (msg_list)
    return msg_list

def Fun_TspLastMeas(para_dict):#Time stamp
    """
    

    Args:
      para_dict: 

    Returns:

    """
    namespace = para_dict["namespace"]
    signal_name = para_dict["signal_name"]
    signal_grp_info = para_dict["siggrp_info"]
    startbit = para_dict["startbit"]
    sig_length = para_dict["sig_length"]
    byte_order = para_dict["byte_order"]
    network_name = para_dict["network_name"]
    empty_siggrp_counts = signal_grp_info["empty_siggrp_counts"]
    #print ("CNT_TIME_STAMP :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list= msg_list + clearData(startbit,sig_length,byte_order)#Clear old  data
    msg_list.append('    //Msg_{0}.{1} = @{0}::{1}_FaultInject +(timeNowNS()/1000000)*66;'.format(namespace, signal_name))
    input_var ='@{2}::{0}::{1}_FaultInject +(timeNowNS()/1000000)*66'.format(namespace, signal_name,network_name)
    msg_list= msg_list + copyData(input_var,startbit,sig_length,byte_order)
    #print (msg_list)
    return msg_list

def match_flt_evt_pattern(namespace):
    """
    

    Args:
      namespace: 

    Returns:

    """
    msg_56D = [r'.*FD3.*56D.*','0x96']
    msg_56F = [r'.*FDP1.*56F.*','0xAB']
    msg_56E = [r'.*FDP1.*56E.*','0xAC']
    msg_570 = [r'.*FDP1.*570.*','0xAE']
    msg_571 = [r'.*FDP1.*571.*','0xAD']
                       
    matchObj = re.search( msg_56D[0], namespace, re.M|re.I)
    if(None!=matchObj):
        return msg_56D[1]

    matchObj = re.search( msg_56F[0], namespace, re.M|re.I)
    if(None!=matchObj):
        return msg_56F[1]

    matchObj = re.search( msg_56E[0], namespace, re.M|re.I)
    if(None!=matchObj):
        return msg_56E[1]

    matchObj = re.search( msg_570[0], namespace, re.M|re.I)
    if(None!=matchObj):
        return msg_570[1]

    matchObj = re.search( msg_571[0], namespace, re.M|re.I)
    if(None!=matchObj):
        return msg_571[1]
    
    matchObj = re.search( flt_evt_msg_pattern, namespace, re.M|re.I)
    if(None!=matchObj):
        return '0xFF'
    
    return '0x00'

def ACK_FLT_EVENT():
    """ """
    #print ("ACK_FLT_EVENT :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list.append('PROJ_CalcMsg_{0}(Byte ACQ)'.format(Msg_ACK_FLT_EVENT))
    msg_list.append('{')
    if (bus_type.upper() == 'CANFD'):
        msg_list.append('	Msg_{0}.fdf = 1;'.format(Msg_ACK_FLT_EVENT))
        msg_list.append('	Msg_{0}.BRS = 1;'.format(Msg_ACK_FLT_EVENT))
    msg_list.append('	Msg_{0}.dlc = 15;'.format(Msg_ACK_FLT_EVENT))
    msg_list.append('	Msg_{0}.DATA_ACQ_JDD_BSI_2 = ACQ;'.format(Msg_ACK_FLT_EVENT))
    msg_list.append('}')
    msg_list.append('')
    msg_list.append('on timer PROJ_DEH_Msg_ACK_Delay_ms')
    msg_list.append('{')
    msg_list.append('output(Msg_{0});'.format(Msg_ACK_FLT_EVENT))
    msg_list.append('}')
    msg_list.append('')
    #print (msg_list)
    return msg_list

def FLT_EVENT(namespace):
    """
    

    Args:
      namespace: 

    Returns:

    """
    #print ("FLT_EVENT :: " + namespace +"."+ signal_name)
    msg_list=[]
    msg_list.append('on message {0}'.format(namespace))
    msg_list.append('{')
    msg_list.append('  PROJ_CalcMsg_{0}({1});'.format(Msg_ACK_FLT_EVENT,match_flt_evt_pattern(namespace)))
    msg_list.append('  setTimer(PROJ_DEH_Msg_ACK_Delay_ms,{0});// Timer to send message with delay'.format(delay_ACK_FLT_EVENT))
    msg_list.append('}')
    msg_list.append('')
    #print (msg_list)
    return msg_list

def is_empty_or_spaces(input_string):
    """
    

    Args:
      input_string: 

    Returns:

    """
    # Check if the input_string is None or empty
    if input_string is None or len(input_string) == 0:
        return True

    # Remove leading and trailing whitespaces and check if the resulting string is empty
    stripped_string = input_string.strip()
    return len(stripped_string) == 0
    
def df_sort_asc(input_df,col_names,sort_by_col):#Sort in ascending df by column names
    """
    

    Args:
      input_df: 
      col_names: 
      sort_by_col: 

    Returns:

    """
    output_df=pd.DataFrame(data=input_df.values, columns=col_names)
    output_df=output_df.sort_values(by=sort_by_col)
    output_df.columns = range(output_df.columns.size)
    return output_df

def sort_column_by(bus_type,input_file):
    """
    

    Args:
      bus_type: 
      input_file: 

    Returns:

    """
    sort_by =[]
    if((bus_type.upper() == 'ETH')):
        sort_by =['PDU','group','Message','Name']
    elif((bus_type.upper() =='CAN') or (bus_type.upper() =='CANFD')):
        if input_file=="dbc":
            sort_by =['Message ID','Message','Startbit']
        else:
            sort_by = ['Message ID','Message','PDU','Startbit']
    return sort_by

def generate_MsgType(bus_type,input_file,msg_name,pdu_name):
    """
    based on network type pdu or message declaration is returned
    Args:
        bus_type (str): network type eth or can
        input_file (str): dbc or arxml (not used for now)
        msg_name (str): message name
        pdu_name (str): pdu name

    Returns:
        var_list (list): capl declaration of message or pdu
    """
    var_list=[]
    if((bus_type.upper() == 'ETH')):
        var_list.append('  pdu {0} Msg_{0};'.format(pdu_name))
    elif((bus_type.upper() =='CAN') or (bus_type.upper() =='CANFD')):
        var_list.append('  message {0} Msg_{0};'.format(msg_name))
    return var_list

def check_PDU_in_NPDU(pdu_name,npdu_dict):
    """
    

    Args:
      pdu_name: 
      npdu_dict: 

    Returns:

    """
    if len(npdu_dict)!=0:
        for key,value in npdu_dict.items():
            if value[1] == pdu_name:#value[0]->Npdu; value[1]->I signal pdu,Key->Message mapped to them
                return True
    return False

def check_PDU_is_NPDU_FC(pdu_name):
    """
    

    Args:
      pdu_name: 

    Returns:

    """
    if re.search(NPDU_FC_Pattern,pdu_name,re.IGNORECASE):
        return True          
    return False

def map_npdu_to_ipdu_dict(node_df, col_msg, col_pdu ,col_pdu_type, col_payload_pdu, column_indexed = True):
    """
    Maps N-PDU to I-Signal-I-PDU and returns a dictionary of N-PDU to I-Signal-I-PDU mapping.
    It considers complete node_df to create mapping
    Args:
        node_df (DataFrame): DataFrame containing the node data
        col_msg (str): index/name of the column representing the message
        col_pdu (str): index/name of the column representing the PDU
        col_pdu_type (str): index/name of the column representing the PDU type
        col_payload_pdu (str): index/name of the column representing the payload PDU
        column_indexed (bool, optional): Indicates if the DataFrame is column indexed. Defaults to True.

    Returns:
        dict: Dictionary mapping N-PDU to I-Signal-I-PDU
    """
    npdu_dict = {}
    message_dict = {}
    if column_indexed:
       filtered_df = node_df.iloc[1:]
    else:
        colindexes = [i for i in range(len(node_df.columns))]
        node_df.columns = colindexes
        filtered_df = node_df
    for message, message_df in filtered_df.groupby(col_msg):
        pdu_cnt = 0
        N_Pdu = ""
        I_Pdu = ""
        payload_pdu = ""
        pdu_type = str(message_df[col_pdu_type].values[0])
        if "N-PDU" in pdu_type and not(check_PDU_is_NPDU_FC(message_df[col_pdu].values[0])):
            if not is_empty_or_spaces(str(message_df[col_pdu].values[0])):
                N_Pdu = str(message_df[col_pdu].values[0])
            else:
                N_Pdu = str(message_df[col_msg].values[0])
            # payload_pdu.append(str(message_df[col_pdu].values[0]))  # str(message_df[col_pdu].values[0])
            payload_pdu = str(message_df[col_payload_pdu].values[0])
            message_dict[message] = [N_Pdu, payload_pdu, list(message_df.iloc[0])]

    for pdu, pdu_df in filtered_df.groupby(col_pdu):
        for msg, values in message_dict.items():
            if values[1] == pdu:  # payload_pdu
                npdu_dict[msg] = [values[0], pdu, values[2]]

    # Ex: npdu_dict = {RXX_Location_NPdu_Data : [RXX_Location_NPdu_Data, RXX_Location]}
    # print(f'message_dict = {message_dict}')
    # print(f'npdu_dict = {npdu_dict}')
    return npdu_dict


def map_npdu_to_ipdu_dict_sysvar(sysvar_df, col_sender, col_msg, col_pdu ,col_pdu_type, col_payload_pdu, column_indexed = True):
    """
    Maps N-PDU to I-Signal-I-PDU and returns a dictionary of N-PDU to I-Signal-I-PDU mapping.
    It generates the mapping sender wise
    Args:
        node_df (DataFrame): DataFrame containing the node data
        col_msg (str): index/name of the column representing the message
        col_pdu (str): index/name of the column representing the PDU
        col_pdu_type (str): index/name of the column representing the PDU type
        col_payload_pdu (str): index/name of the column representing the payload PDU
        column_indexed (bool, optional): Indicates if the DataFrame is column indexed. Defaults to True.

    Returns:
        dict: Dictionary mapping N-PDU to I-Signal-I-PDU
    """
    npdu_dict = {}
    message_dict = {}
    if column_indexed:
       filtered_df = sysvar_df.iloc[1:]
    else:
        colindexes = [i for i in range(len(sysvar_df.columns))]
        sysvar_df.columns = colindexes
        filtered_df = sysvar_df
    
    for sender, sender_df in filtered_df.groupby(col_sender):
        for message, message_df in sender_df.groupby(col_msg):
            N_Pdu = ""
            payload_pdu = ""
            for pdu_type, pdu_type_df in message_df.groupby(col_pdu_type):
                if "N-PDU" in pdu_type and not(check_PDU_is_NPDU_FC(pdu_type_df[col_pdu].values[0])):
                    if not is_empty_or_spaces(str(pdu_type_df[col_pdu].values[0])):
                        N_Pdu = str(pdu_type_df[col_pdu].values[0])
                    else:
                        N_Pdu = str(pdu_type_df[col_msg].values[0])
                    # payload_pdu.append(str(pdu_type_df[col_pdu].values[0]))  # str(pdu_type_df[col_pdu].values[0])
                    payload_pdu = str(pdu_type_df[col_payload_pdu].values[0])
                    message_dict[message] = [N_Pdu, payload_pdu, list(pdu_type_df.iloc[0])]

    for pdu_type, pdutype_df in filtered_df.groupby(col_pdu_type):
        if 'I-SIGNAL' in pdu_type.upper():
            for pdu, pdu_df in pdutype_df.groupby(col_pdu):
                for msg, values in message_dict.items():
                    if values[1] == pdu:  # payload_pdu
                        npdu_dict[msg] = [values[0], pdu, values[2]]

    # Ex: npdu_dict = {RXX_Location_NPdu_Data : [RXX_Location_NPdu_Data, RXX_Location]}
    # print(f'message_dict = {message_dict}')
    # print(f'npdu_dict = {npdu_dict}')
    return npdu_dict


def check_PDU_in_SecuredPdu(pdu_name,SecuredPdu_dict):
    if len(SecuredPdu_dict)!=0:
        for key, value in SecuredPdu_dict.items():
            if value[1] == pdu_name:#value[0]->SecuredPdu; value[1]->I signal pdu,Key->Message mapped to them
                return True
    return False


def get_message_from_SecuredPdu(pdu_name, SecuredPdu_dict):
    if len(SecuredPdu_dict) != 0:
        for key, value in SecuredPdu_dict.items():
            if value[1] == pdu_name:#value[0]->SecuredPdu; value[1]->I signal pdu,Key->Message mapped to them
                return key
    return False

def map_securedpdu_to_ipdu_dict(node_df, col_msg, col_pdu ,col_pdu_type, col_payload_pdu, column_indexed = True):
    """
    Maps SECURED-PDU to I-Signal-I-PDU and returns a dictionary of SECURED-PDU to I-Signal-I-PDU mapping.
    It considers complete node_df to create mapping
    Args:
        node_df (DataFrame): DataFrame containing the node data
        col_msg (str): index/name of the column representing the message
        col_pdu (str): index/name of the column representing the PDU
        col_pdu_type (str): index/name of the column representing the PDU type
        col_payload_pdu (str): index/name of the column representing the payload PDU
        column_indexed (bool, optional): Indicates if the DataFrame is column indexed. Defaults to True.

    Returns:
        dict: Dictionary mapping SECURED-PDU to I-Signal-I-PDU
    """
    securedPdu_dict = {}
    message_dict = {}
    if column_indexed:
       filtered_df = node_df.iloc[1:]
    else:
        colindexes = [i for i in range(len(node_df.columns))]
        node_df.columns = colindexes
        filtered_df = node_df
    for message, message_df in filtered_df.groupby(col_msg):
        pdu_cnt = 0
        secured_Pdu = ""
        I_Pdu = ""
        payload_pdu = ""
        pdu_type = str(message_df[col_pdu_type].values[0])
        if "SECURED-I-PDU" in pdu_type:
            if not is_empty_or_spaces(str(message_df[col_pdu].values[0])):
                secured_Pdu = str(message_df[col_pdu].values[0])
            else:
                secured_Pdu = str(message_df[col_msg].values[0])
            # payload_pdu.append(str(message_df[col_pdu].values[0]))  # str(message_df[col_pdu].values[0])
            payload_pdu = str(message_df[col_payload_pdu].values[0])
            message_dict[message] = [secured_Pdu, payload_pdu, list(message_df.iloc[0])]
            # print(f'message_dict[message] = {message_dict[message]}')

    for pdu, pdu_df in filtered_df.groupby(col_pdu):
        for msg, values in message_dict.items():
            if values[1] == pdu:  # payload_pdu
                securedPdu_dict[msg] = [values[0], pdu, values[2]]

    # print(f'message_dict = {message_dict}')
    # print(f'securedPdu_dict = {securedPdu_dict}')
    return securedPdu_dict


def map_securedpdu_to_ipdu_dict_sysvar(sysvar_df, col_sender, col_msg, col_pdu ,col_pdu_type, col_payload_pdu, column_indexed = True):
    """
    Maps SECURED-PDU to I-Signal-I-PDU and returns a dictionary of SECURED-PDU to I-Signal-I-PDU mapping.
    It generates mapping senderwise
    Args:
        sysvar_df (DataFrame): DataFrame containing the node data
        col_msg (str): index/name of the column representing the message
        col_pdu (str): index/name of the column representing the PDU
        col_pdu_type (str): index/name of the column representing the PDU type
        col_payload_pdu (str): index/name of the column representing the payload PDU
        column_indexed (bool, optional): Indicates if the DataFrame is column indexed. Defaults to True.

    Returns:
        dict: Dictionary mapping SECURED-PDU to I-Signal-I-PDU
    """
    securedPdu_dict = {}
    message_dict = {}
    if column_indexed:
       filtered_df = sysvar_df.iloc[1:]
    else:
        colindexes = [i for i in range(len(sysvar_df.columns))]
        sysvar_df.columns = colindexes
        filtered_df = sysvar_df

    for sender, sender_df in filtered_df.groupby(col_sender):
        for message, message_df in sender_df.groupby(col_msg):
            secured_Pdu = ""
            payload_pdu = ""
            for pdu_type, pdu_type_df in message_df.groupby(col_pdu_type):
                if "SECURED-I-PDU" in pdu_type:
                    if not is_empty_or_spaces(str(pdu_type_df[col_pdu].values[0])):
                        secured_Pdu = str(pdu_type_df[col_pdu].values[0])
                    else:
                        secured_Pdu = str(pdu_type_df[col_msg].values[0])
                    # payload_pdu.append(str(pdu_type_df[col_pdu].values[0]))  # str(pdu_type_df[col_pdu].values[0])
                    payload_pdu = str(pdu_type_df[col_payload_pdu].values[0])
                    message_dict[message] = [secured_Pdu, payload_pdu, list(pdu_type_df.iloc[0])]

    for pdu_type, pdutype_df in filtered_df.groupby(col_pdu_type):
        if 'I-SIGNAL' in pdu_type.upper():
            for pdu, pdu_df in pdutype_df.groupby(col_pdu):
                for msg, values in message_dict.items():
                    if values[1] == pdu:  # payload_pdu
                        securedPdu_dict[msg] = [values[0], pdu, values[2]]

    # print(f'message_dict = {message_dict}')
    # print(f'securedPdu_dict = {securedPdu_dict}')
    return securedPdu_dict


def get_NPDU_Identifier_dict(node_df, col_msg, col_pdu ,col_pdu_type,col_msg_ID, col_payload_pdu, column_indexed=True):
    """
    Get the NPDU identifier dictionary and NPDU rx identifier dictionary.

    Args:.
        node_df (DataFrame): The DataFrame containing the node data.
        col_msg (str): The column name for the message.
        col_pdu (str): The column name for the PDU.
        col_pdu_type (str): The column name for the PDU type.
        col_msg_ID (str): The column name for the message ID.
        col_payload_pdu (str): The column name for the payload PDU.

    Returns:
        tuple: A tuple containing the NPDU identifier dictionary and NPDU rx identifier dictionary.

    """
    npdu_identifiers_dict = {} #eg: {"NPDU":"ID",...}
    npdu_rx_identifier_dict = {} #eg: {"NPDU":"rx-ID",...}

    npdu_payload_pdu_dict = {}

    if column_indexed:
        filtered_df = node_df.iloc[1:]
    else:
        colindexes = [i for i in range(len(node_df.columns))]
        node_df.columns = colindexes
        filtered_df = node_df

    for pdu_type, pdu_type_df in filtered_df.groupby(col_pdu_type):
        if "N-PDU" in pdu_type:
            for i, row in pdu_type_df.iterrows():
                msg_id = row[col_msg_ID]
                pdu = str(row[col_pdu])
                payload_pdu = str(row[col_payload_pdu])
                if not is_empty_or_spaces(pdu):
                    npdu_identifiers_dict[pdu]=str(msg_id)

                    if payload_pdu not in npdu_payload_pdu_dict:
                        npdu_payload_pdu_dict[payload_pdu] = [{pdu:str(msg_id)}]
                    else:
                        npdu_payload_pdu_dict[payload_pdu].append({pdu:str(msg_id)})

    for payload_pdu, pdu_list in npdu_payload_pdu_dict.items():
        if len(pdu_list) == 2:
            #swap the values
            npdu_rx_identifier_dict[list(pdu_list[0].keys())[0]] = list(pdu_list[1].values())[0]
            npdu_rx_identifier_dict[list(pdu_list[1].keys())[0]] = list(pdu_list[0].values())[0]

    return npdu_identifiers_dict, npdu_rx_identifier_dict


def generate_npdu_write_fielddata(node_name, pdu_name, pdu_df, byte_order):
    write_list = []
    write_list.append("")
    # Small Packet
    write_list.append(f"void Write_OsekTP_{node_name}_{pdu_name}_Small_Packet(byte byteArray[])")
    write_list.append("{")
    write_list.append("    qword raw_value = 255;")
    if "MOTO" in byte_order.upper():
        for i in range(8):
            write_list.append(f"    copyBitsToByteArrayBE(raw_value, byteArray, {i * 8}, 8);")
        write_list.append("    copyBitsToByteArrayBE(2, byteArray, 64, 8);")
        write_list.append("    copyBitsToByteArrayBE(7, byteArray, 72, 8);")
        write_list.append("    for(i = 0; i < 98; i++) \n    {")
        write_list.append("      copyBitsToByteArrayBE(raw_value, byteArray, 80+(8*i), 8); \n    } \n}")
    else:
        for i in range(8):
            write_list.append(f"    copyBitsToByteArrayLE(raw_value, byteArray, {i * 8}, 8);")
        write_list.append("    copyBitsToByteArrayLE(7, byteArray, 64, 8);")
        write_list.append("    copyBitsToByteArrayLE(2, byteArray, 72, 8);")
        write_list.append("    for(i = 0; i < 98; i++) \n    {")
        write_list.append("      copyBitsToByteArrayLE(raw_value, byteArray, 80+(8*i), 8); \n    } \n}")

    # Big Packet
    write_list.append("")
    write_list.append(f"void Write_OsekTP_{node_name}_{pdu_name}_Big_Packet(byte byteArray[])")
    write_list.append("{")
    write_list.append("    qword raw_value = 255;")
    if "MOTO" in byte_order.upper():
        for i in range(8):
            write_list.append(f"    copyBitsToByteArrayBE(raw_value, byteArray, {i * 8}, 8);")
        write_list.append("    copyBitsToByteArrayBE(4, byteArray, 64, 8);")
        write_list.append("    copyBitsToByteArrayBE(12, byteArray, 72, 8);")
        write_list.append("    for(i = 0; i < 2038; i++) \n    {")
        write_list.append("      copyBitsToByteArrayBE(raw_value, byteArray, 80+(8*i), 8); \n    } \n}")
    else:
        for i in range(8):
            write_list.append(f"    copyBitsToByteArrayLE(raw_value, byteArray, {i * 8}, 8);")
        write_list.append("    copyBitsToByteArrayLE(12, byteArray, 64, 8);")
        write_list.append("    copyBitsToByteArrayLE(4, byteArray, 72, 8);")
        write_list.append("    for(i = 0; i < 2038; i++) \n    {")
        write_list.append("      copyBitsToByteArrayLE(raw_value, byteArray, 80+(8*i), 8); \n    } \n}")
    return write_list

def generate_npdu_timer(network_name, node_name, pdu_name, pdu_df):
    """


    Args:
      network_name:
      pdu_name:
      pdu_df:

    Returns:

    """
    npdu_timer_list = []
    npdu_timer_list.append('')
    npdu_timer_list.append('on timer {0}_Timer'.format(pdu_name))
    npdu_timer_list.append('{')
    npdu_timer_list.append('  if (@{0}::{1}::txBuffermode == 0)'.format(network_name, pdu_name))
    npdu_timer_list.append('  {')
    npdu_timer_list.append('    if (count < 20) \n    {')
    npdu_timer_list.append('     Transmit_Pdu_{0}_{1}();'.format(node_name, pdu_name))
    npdu_timer_list.append('     count =count+1;')
    npdu_timer_list.append('     setTimer({0}_Timer,50);'.format(pdu_name))
    npdu_timer_list.append('    }')
    npdu_timer_list.append('    else \n    {\n     count=0;\n    }')
    npdu_timer_list.append('  }')

    npdu_timer_list.append('  else if (@{0}::{1}::txBuffermode == 1)'.format(network_name, pdu_name))
    npdu_timer_list.append('  {')
    npdu_timer_list.append('    if (count < 5) \n    {')
    npdu_timer_list.append('     Transmit_Pdu_{0}_{1}();'.format(node_name, pdu_name))
    npdu_timer_list.append('     count =count+1;')
    npdu_timer_list.append('     setTimer({0}_Timer,50);'.format(pdu_name))
    npdu_timer_list.append('    }')
    npdu_timer_list.append('    else \n    {\n     count=0;\n    }')
    npdu_timer_list.append('  }')
    npdu_timer_list.append('}')
    return npdu_timer_list

def secoc_includes(var_IL, sec_pdu_list):
    """
    

    Args:
      var_IL: 

    Returns:

    """
    node_list=[]
    if(var_IL=='AsrPDUIL'):
        node_list.append('  #pragma library ("C:\\ProgramData\\Vector\\Security Manager\\Modules\\CANoe\\SecMgrCANoeClient.vmodule")')
        # if any([re.match(secoc_PDU_patterns, sec_pdu) for sec_pdu in sec_pdu_list]):
        #    node_list.append('  #include "CAPL\Security.cin" /*For trip counter */')
    return node_list

def generate_SecocVar(bus_type,input_file,namespace):
    """
    

    Args:
      bus_type: 
      input_file: 
      namespace: 

    Returns:

    """
    var_list=[]
    var_list.append('  qword Secoc_{0}_AuthInfo;'.format(namespace))
    var_list.append('  qword Secoc_{0}_Freshness;'.format(namespace))
    return var_list

def generate_Secoc_Fault(pdu, network_name):
    """
    

    Args:
      pdu: 
      network_name: 

    Returns:

    """
    sec_fun = []
    sec_fun.append('')
    sec_fun.append('void cfg_Secoc_{0}(dword dataId, byte payload[], dword payloadLength, qword& authInfoHigh, qword& authInfo, dword authInfoBitLength, qword& freshness, dword freshnessBitLength, dword freshnessValueId)'.format(pdu))
    sec_fun.append('{')
    sec_fun.append('   if (@{2}::{0}::{0}_{1}_FaultInject == 0)//AuthInfo: No Error'.format(pdu, "AuthInfo", network_name))
    sec_fun.append('    {')
    sec_fun.append('       Secoc_{0}_AuthInfo = authInfo; // Copy cmac'.format(pdu))
    sec_fun.append('    }')
    sec_fun.append('   else if (@{2}::{0}::{0}_{1}_FaultInject == 1)//AuthInfo: Error , set to zero'.format(pdu, "AuthInfo", network_name))
    sec_fun.append('    {')
    sec_fun.append('       authInfo = 0; // change cmac')
    sec_fun.append('    }')
    sec_fun.append('   else if (@{2}::{0}::{0}_{1}_FaultInject == 2)//AuthInfo: Error , Freeze last valid value'.format(pdu, "AuthInfo", network_name))
    sec_fun.append('    {')
    sec_fun.append('       authInfo = Secoc_{0}_AuthInfo; // change cmac'.format(pdu))
    sec_fun.append('    }')
    sec_fun.append('   if (@{2}::{0}::{0}_{1}_FaultInject == 0)//No Error'.format(pdu, "Freshness", network_name))
    sec_fun.append('    {')
    sec_fun.append('       Secoc_{0}_Freshness = freshness; // Copy cmac'.format(pdu))
    sec_fun.append('    }')
    sec_fun.append('   else if (@{2}::{0}::{0}_{1}_FaultInject == 1)//Freshness: Error , set to zero'.format(pdu, "Freshness", network_name))
    sec_fun.append('    {')
    sec_fun.append('       freshness = 0; // change cmac')
    sec_fun.append('    }')
    sec_fun.append('   else if (@{2}::{0}::{0}_{1}_FaultInject == 2)//Freshness: Error , Freeze last valid value'.format(pdu, "Freshness", network_name))
    sec_fun.append('    {')
    sec_fun.append('       freshness = Secoc_{0}_Freshness; // change cmac'.format(pdu))
    sec_fun.append('    }')
    sec_fun.append('}')
    return sec_fun

def get_canoe_IL(bus_type="",input_file=""):
    """
    

    Args:
      bus_type:  (Default value = "")
      input_file:  (Default value = "")

    Returns:

    """
    if (bus_type.upper()=="ETH"):
        return 'SomeIP'
    elif ((bus_type.upper() =='CAN') or (bus_type.upper() =='CANFD')):
        if input_file == "dbc":
            return 'CANoeIL'
        elif input_file == "arxml":
            return 'AsrPDUIL'
    else:
        return 'CANoeIL'

def grp_or_pdu_or_msg(bus_type="",input_file=""):
    """
    

    Args:
      bus_type:  (Default value = "")
      input_file:  (Default value = "")

    Returns:

    """
    if ((bus_type.upper() == 'ETH')):
        return 'PDU'
    elif ((bus_type.upper() =='CAN') or (bus_type.upper() =='CANFD')):
        if input_file == "dbc":
            return 'msg'
        elif input_file == "arxml":
            return 'PDU'
    else:
        return 'msg'

def get_includes(var_IL):
    """
    

    Args:
      var_IL: 

    Returns:

    """
    node_list=[]
    #node_list.append('includes')
    #node_list.append('{')
    if(var_IL=='AsrPDUIL'):
        node_list.append('  #pragma library ("C:\\ProgramData\\Vector\\AddOn Packages\\Vector AddOn\\vModules\\AsrPDUIL2.vmodule")')
    elif(var_IL=='CANoeIL'):
        node_list.append('  #pragma library ("C:\\ProgramData\\Vector\\AddOn Packages\\Vector AddOn\\vModules\\CANoeILNLVector.vmodule")')
    elif(var_IL=='SomeIP'):
        node_list.append('  //#pragma library ("C:\\ProgramData\\Vector\\AddOn Packages\\Vector AddOn\\vModules\\AsrPDUIL2.vmodule")')
        node_list.append('  //#pragma library ("C:\\Program Files\\Vector CANoe 16\\Exec64\\CANoeILNL_AUTOSAR_Eth.vmodule")')
    else:
        node_list.append('')
    node_list.append('  #include "CAPL\\DataHandling.cin" /*DataHandling for IL*/')
    node_list.append('  #include "CAPL\\E2E.cin" /*OD Specific for CRC calculation */')
    if(var_IL=='SomeIP'):
        node_list.append('  #include "CAPL\\Service-Helper_Eth.cin" /*SomeIP Handling */')
    #node_list.append('}')   
    return node_list


def get_eth_rbs_includes(node_name):
    eth_rbs_include_list = []
    # if (node_name.upper() == 'RBS') or ('simulatedpeernodes' in node_name.lower()):
    #    eth_rbs_include_list.append(r'  #include "..\TimeSync\Node\EthTsync_Rigil.cin"')
    return eth_rbs_include_list


def get_eth_rbs_onsim(node_name):
    eth_rbs_onsim_list = []
    # if (node_name.upper() == 'RBS') or ('simulatedpeernodes' in node_name.lower()):
    #     eth_rbs_onsim_list.append('  mappingToRigil();')
    return eth_rbs_onsim_list


def get_EthBusName(bus_type, input_file, network_name, node_name):
    """
    used to map alternate names of a network
    """
    return network_name


def get_EthNodeName(bus_type, input_file, network_name, node_name):
    """
    used to map alternate names of a node
    """
    return node_name


def ontmr_variables(para_dict):
    """
    generate ontimer variables declaration
    Args:
        bus_type (str): network type can or eth
        input_file (str): dbc or arxml
        message (str): message name
        pdu (str): pdu name
        network_name (str): network name
        e2e_def (str): e2e definition

    Returns:
        node_list (list): list of generated ontmr var decalation

    """

    bus_type = para_dict["bus_type"]
    input_file = para_dict["input_file"]
    message = para_dict["message"]
    pdu = para_dict["pdu"]
    network_name = para_dict["network_name"]
    e2e_def = para_dict["e2e_def"]
    signal_dict = para_dict["signal_dict"]
    node_list = []

    if ((bus_type.upper() == 'ETH')):
        node_list.append('   ethernetPacket ethPacket_{0};'.format(pdu))
        node_list.append('   byte buffer[2500];')
    elif ((bus_type.upper() == 'CAN') or (bus_type.upper() == 'CANFD')):
        if "mpc3" in network_name.lower():
            node_list.append('   byte messagebytes[10];')
            node_list.append('   byte byte_count=0,crc_byte_no =0;')
            node_list.append('   int loop_index;')

        node_list.append('   int64 i,k;//For looping')
        node_list.append('   byte xor,data_byte;')
        node_list.append('   dword crcTemp;')
        node_list.append('   byte DataLength;')
        node_list.append('   dword Msg_id;')
        if (input_file.upper() != 'DBC'):
            if (e2e_def):
                node_list.append('   long result;')
                node_list.append('   long type=0;//reserved (should be set to 0).')
                node_list.append('   long disturbanceMode  =0; //0 :: set to disturbanceValue //2 :: set to Random value //3 :: Offset Signal value is increased by disturbanceValue')
                node_list.append('   long disturbanceCount =0;//-1 ::Infinite Disturbance is continuously applied //0 ::Stop An active disturbance is stopped and the SequenceCounter/crc will be calculated again appropriately //n > 0 ::Count Do exactly n Repetition/disturbances')
                node_list.append('   long disturbanceValue =0;//According to the disturbance mode the SequenceCounter/crc will optionally be set to this value')
                node_list.append('   dword crc[1];')
        if signal_dict != {}:
            for signal_name, signal_para_list in signal_dict.items():
                signal_byte_order, signal_start_bit, signal_length = signal_para_list
                # print(f'ontmr_variables::signal_name = {signal_name}, signal_byte_order = {signal_byte_order}')
                node_list.append(f'   byte sendString[38]; \n   long copiedBytes; \n   long TxLength; \n   byte {signal_name}_array[38];')
        node_list.append('   ')
        node_list.append('   DataLength = Msg_{0}.DataLength;//Message Data Length'.format(message))
        node_list.append('   Msg_id  = Msg_{0}.id;//Message ID'.format(message))
        if signal_dict != {}:
            for signal_name, signal_para_list in signal_dict.items():
                signal_byte_order, signal_start_bit, signal_length = signal_para_list
                node_list.append(f'   \n   // Initialize {signal_name}_array to zero')
                node_list.append(f'   for (i = 0; i < elcount({signal_name}_array); i++)')
                node_list.append('   {')
                node_list.append(f'     {signal_name}_array[i] = 0;')
                node_list.append('   }')
                node_list.append(f'   if (sysGetVariableData(sysvar::{network_name}::{pdu}::{signal_name}::SignalValue, sendString, copiedBytes) == 0)')
                node_list.append('   { \n     TxLength=copiedBytes;')
                node_list.append(f'     memcpy( {signal_name}_array, sendString, TxLength);')
                node_list.append('   }')
                node_list.append('   // Output the destination array for verification')
                node_list.append(f'   // for (i = 0; i < elcount({signal_name}_array); i++)')
                node_list.append('   // {')
                node_list.append(f'    // write("0x%02X ", {signal_name}_array[i]);')
                node_list.append('   // }')
                node_list.append('   ')
                node_list.append(f'   copyByteArrayToByteArray({signal_name}_array, data, {signal_start_bit}, {signal_start_bit + signal_length});')
        node_list.append('   ')
    return node_list

def ontmr_triggerMsg(pdu_para_list):
    """
    

    Args:
      pdu_para_list: 

    Returns:

    """
    node_list=[]
    bus_type,input_file,namespace,vlan,src_mac,dst_mac,src_ip,dst_ip,src_port,dst_port = pdu_para_list
    
    para_list =[namespace,vlan,src_mac,dst_mac,src_ip,dst_ip,src_port,dst_port]
    
    if((bus_type.upper() == 'ETH')):
        node_list.extend(ethPacket_config(para_list))   
    elif((bus_type.upper() =='CAN') or (bus_type.upper() =='CANFD')):
        if input_file=="dbc":
            node_list.append('   output(Msg_{0});'.format(namespace))
        else:
            node_list.append('   triggerPDU(Msg_{0});'.format(namespace))
    node_list.append('   ')
    return node_list

def byteOrder_to_8byte(value):
    """
    

    Args:
      value: 

    Returns:

    """
    if ( value % 8 == 0 ):
        return value
    else :
        return (((int(value / 8))+1)*8)

def IsNodeCANFdEnabled(node_name,bus_type):
    """
    

    Args:
      node_name: 
      bus_type: 

    Returns:

    """
    if (bus_type.upper() == 'CANFD'):
        return True#If Network is CAN-FD
    else:
        return False#If Network is not CAN-FD

   
def ethPacket_config(para_list):
    """
    

    Args:
      para_list: 

    Returns:

    """
    namespace,vlan,src_mac,dst_mac,src_ip,dst_ip,src_port,dst_port = para_list
    msg_list=[]
    msg_list.append('   ethPacket_{0}.SetVlan(0x8100,{1})'.format(namespace,vlan))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.source=ethGetMacAddressAsNumber("{1}");//source mac'.format(namespace,src_mac))
    msg_list.append('   ethPacket_{0}.destination=ethGetMacAddressAsNumber("{1}");//source mac'.format(namespace,dst_mac))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.ipv4.Init();'.format(namespace))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.ipv4.source.ParseAddress("{1}");//source ip'.format(namespace,src_ip))
    msg_list.append('   ethPacket_{0}.ipv4.destination.ParseAddress("{1}");//source ip'.format(namespace,dst_ip))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.udp.Init();'.format(namespace))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.udp.source={1};//source ip'.format(namespace,src_port))
    msg_list.append('   ethPacket_{0}.udp.destination={1};//source ip'.format(namespace,dst_port))
    msg_list.append('   ')
    msg_list.append('   k=0')
    msg_list.append('   buffer[k++]=Msg_{0}.LongHeaderID>>24;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.LongHeaderID>>16;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.LongHeaderID>>8;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.LongHeaderID;'.format(namespace))
    msg_list.append('   ')
    msg_list.append('   buffer[k++]=Msg_{0}.PduLength>>24;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.PduLength>>16;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.PduLength>>8;'.format(namespace))
    msg_list.append('   buffer[k++]=Msg_{0}.PduLength;'.format(namespace))
    msg_list.append('   ')
    msg_list.append('   for(i=0;i<Pdu_{0}.PduLength;i++);'.format(namespace))
    msg_list.append('   {')
    msg_list.append('     buffer[k++]=Msg_{0}.byte(i);'.format(namespace))
    msg_list.append('   }')
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.udp.SetData( 0, buffer, Msg_{0}.PduLength + 8);//source ip'.format(namespace))
    msg_list.append('   ')
    msg_list.append('   ethPacket_{0}.CompletePacket();'.format(namespace))
    msg_list.append('   output(ethPacket_{0});'.format(namespace))
    msg_list.append('   ')
    #print (msg_list)
    return msg_list



ac_var_dict ={ac_sig_pattern_1:AC_SIG_1,fn_sig_pattern_3:AC_SIG_1}
bc_var_dict ={bc_sig_pattern_1:BC_SIG_1}
ts_var_dict ={}
crc_var_dict ={CRC_sig_pattern_0:initialize_CRC_variable}

ac_dict ={ac_sig_pattern_1:CNT_ALIVE_1,fn_sig_pattern_3:CNT_ALIVE_1}
bc_dict ={bc_sig_pattern_1:CNT_BLOCK}
ts_dict ={ts_sig_pattern_1:Fun_TimeStamp ,ts_sig_pattern_2:Fun_TspLastMeas }
crc_dict ={CRC_sig_pattern_0:decide_CRC_logic}
