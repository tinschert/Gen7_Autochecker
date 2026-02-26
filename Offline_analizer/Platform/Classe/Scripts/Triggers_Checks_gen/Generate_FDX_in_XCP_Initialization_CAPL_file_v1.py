# -*- coding: utf-8 -*-
# @file Generate_FDX_in_XCP_Initialization_CAPL_file_v1.py
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
#from fuzzywuzzy import fuzz
import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
#fdx_xls_file = easygui.fileopenbox("Select the <<variant_develop.yml>> file /used for common triggers extraction/: ")
variant_develop_YML_file = r"D:\My_PYTHON_tools\ADAS_HIL_tools_1\variant_develop_hil.yml"
#A2L_file = easygui.fileopenbox("Select the .A2L file /used to extract the XCP names/ : ")
A2L_file = r"C:\Users\NEV1SF4\Desktop\HIL-3_transfer_files\RadarFC_RC12.a2l"
output_file = 'FDX_in_to_XCP_Initialization.can'

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

def Read_Variant_Develop_YML_File():
    """ """
    f1 = open(variant_develop_YML_file, "r")
    for x in f1:
        trigger_name_plus_value_list=x.split('"default_controller/stimuli_prm_sr_TDaddyInterface_prm_sr_FctParam_sr_CCal_", "')
        if len(trigger_name_plus_value_list)==2:
            trigger_name_plus_value_string=trigger_name_plus_value_list[1]
            #print(trigger_name_plus_value_string)
            #trigger name in temp_list2[0]
            temp_list2=trigger_name_plus_value_list[1].split(": ")
            # trigger value in temp_list3[0]
            temp_list3=temp_list2[1].split("}},")
            triggers_list.append([temp_list2[0].replace('"',''),temp_list3[0]])
    f1.close()


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
    #    print(el[1])
    #!!!IMPORTANT!!!
    #The reduced name is in Reduced_A2L_Items_Names[1], the full name is in Reduced_A2L_Items_Names[0]

    Read_Variant_Develop_YML_File()
    #prints the variant_develop_YML common triggers list
    #for el in triggers_list:
    #     print(el)


    #print(Reduced_A2L_Items_Names)

    #WRITE TO OUTPUT CAPL file
    out_file.write("includes\n{\n\n}\nvariables\n{\n\n}\n\n")
    #ignore list -> all the radar and video objects injection items
    ignore_list=["_m_axN", "_m_vyN","_m_vxN","_m_dzN","_m_dyN","_m_dxN","_m_dWidthN","_m_dLengthN","_m_ayN","_m_alpPiYawAngleN","_timeStamp","_m_current","_width","_length"]

    #for el_FDX_trigger in triggers_list:
    #    print (el_FDX_trigger[0])

    #for el_a2l in Reduced_A2L_Items_Names:
    #    print(el_a2l[1])

    for el_FDX_trigger in triggers_list:
        for el_a2l in Reduced_A2L_Items_Names:
            if len(el_a2l[1])>5:
                if el_a2l[1] not in ignore_list:
                    #print(el_a2l[1])
                    if el_FDX_trigger[0].find(el_a2l[1].replace("_m","m"))>=0:
                        #print(el_a2l[1]+" found in "+el_FDX_trigger[0])
                        #print(el_a2l[1]+" found in "+el_FDX_trigger[0])
                        #auto-code-generation here:
                        print(" @sysvar::XCP::RadarFC::"+el_a2l[0].replace(".","::")+"="+el_FDX_trigger[1]+";\n")
                        out_file.write(" @sysvar::XCP::RadarFC::"+el_a2l[0].replace(".","::")+"="+el_FDX_trigger[1]+";\n")
                        #print("\n")
                        #out_file.write("\n")
    out_file.close()
if __name__ == "__main__":

    main()