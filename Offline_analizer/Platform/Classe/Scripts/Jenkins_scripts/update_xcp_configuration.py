# -*- coding: utf-8 -*-
# @file update_xcp_configuration.py
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

"""this is used by jenkins, updates xcp config and reduces a2l as defined in xcp database"""

import argparse
import sys, os
import xml.etree.ElementTree as ET
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import XCP_to_A2L_diff
from file_search import update_database_cycle_times


def get_paths_dasy():
    """ get a2l path from dasy sw folder """
    dasy_sw_path = r"D:\Jenkins\ADAS_Platform\SW_Release\Dasy"
    canape_project_path = ""
    a2l_absolute_path = ""
    sw_flash_path = ""
    if os.path.exists(dasy_sw_path):
        if len(os.listdir(dasy_sw_path)) != 0:
            for root, dirs, files in os.walk(dasy_sw_path):
                for name in dirs:
                    if "measurement_golf" in name.lower():
                        measurement_path = os.path.join(root, name)
                        a2l_folder_path = measurement_path + r"\database\a2l"
                    if "measurement_hil" in name.lower():
                        measurement_path = os.path.join(root, name)
                        canape_project_path = measurement_path + r"\Canape"
                        sw_flash_path = canape_project_path + "\\" + "01_FlashActualDasySwToECU.bat"

            for root, dirs, files in os.walk(a2l_folder_path):
                for name in files:
                    if ".a2l" in name.lower() and "reduced" not in name.lower():
                        a2l_absolute_path = a2l_folder_path + "\\" + name
            return a2l_absolute_path, sw_flash_path
    return None, None


def get_paths_radar_fc():
    """ get a2l path from radar_fc sw folder"""
    front_sw_path = r"D:\Jenkins\ADAS_Platform\SW_Release\RadarFC"

    canape_project_path = ""
    a2l_absolute_path = ""
    sw_flash_path = ""

    try:
        if os.path.exists(front_sw_path):
            if len(os.listdir(front_sw_path)) != 0:
                for root, dirs, files in os.walk(front_sw_path):
                    for name in dirs:
                        if "measurement_golf" in name.lower():
                            measurement_path = os.path.join(root, name)
                            a2l_folder_path = measurement_path + r"\database\a2l"
                        if "measurement_hil" in name.lower():
                            measurement_path = os.path.join(root, name)
                            canape_project_path = measurement_path + r"\Canape"
                            flash_preparation_bat_path = measurement_path + "\\" + "00_HIL_Adapt.bat"
                            sw_flash_path = canape_project_path + "\\" + "01_FlashActualDasySwToECU.bat"

                for root, dirs, files in os.walk(a2l_folder_path):
                    for name in files:
                        if ".a2l" in name.lower() and "reduced" not in name.lower():
                            a2l_absolute_path = a2l_folder_path + "\\" + name
                return a2l_absolute_path, flash_preparation_bat_path, sw_flash_path
        return None, None, None
    except Exception as e:
        logger.error(f"Error occured while getting RadarFC a2l path -> {e}")
        raise Exception(e)


def get_paths_radar_corner():
    """get a2l path from radar_corner sw folder """
    corner_sw_path = r"D:\Jenkins\ADAS_Platform\SW_Release\RadarRear"
    canape_project_path = ""
    a2l_absolute_path = ""
    sw_flash_path = ""
    if os.path.exists(corner_sw_path):
        if len(os.listdir(corner_sw_path)) != 0:
            for root, dirs, files in os.walk(corner_sw_path):
                for name in files:
                    if ".a2l" in name.lower():
                        a2l_absolute_path = os.path.abspath(name)
            return a2l_absolute_path

def changeRelativeA2lPathToAbsolute(xcpconfig):
    """
    Com interface cannot load xcp_config if a2l path is Relative,
    So this function is used to convert relative a2l path to absoulte path

    Args:
      xcpconfig (str): path of xcp config file

    """
    try:
        abs_path = r"D:\Jenkins\ADAS_Platform\CustomerPrj\XCP"
        updated_content = []
        with open(xcpconfig) as f:
            lines = f.readlines()
            for line in lines:
                if line.strip().startswith("<a2l>"):
                    root = ET.fromstring(line)
                    a2l_path = root.find("./VFileName").get("name")
                    if os.path.isabs(a2l_path):
                        updated_content.append(line)
                    else:
                        # change relative path to absolute
                        root.find("./VFileName").set("name", abs_path + "\\" + a2l_path)
                        modified_line = ET.tostring(root).decode()
                        # add indentation
                        modified_line = line.split("<")[0] + modified_line
                        updated_content.append(modified_line)
                else:
                    updated_content.append(line)

            f.close()
        with open(xcpconfig, 'w') as f:
            f.writelines(updated_content)
            f.close()
        logger.info(f"Processed xcp config file for relative a2l paths")
    except Exception as e:
        logger.error(f"Error while converting relative path to absolute in xcp config file -> {e}")
        raise Exception(e)



def update_xcpconfig(a2l_front_loc, a2l_front_obj, a2l_rear, customer, a2l_dasy=None, a2l_dasy_delta1=None,
                     a2l_dasy_delta5=None):
    """
    updates xcp config file and reduces a2l

    Args:
      a2l_front_loc (str): a2l path
      a2l_front_obj (str): a2l path
      a2l_rear (str): a2l path
      customer (str): customer name
      a2l_dasy (str):  (Default value = None) a2l path
      a2l_dasy_delta1 (str):  (Default value = None) a2l path
      a2l_dasy_delta5 (str):  (Default value = None) a2l apth

    """
    def generate_dasy(xcp, a2l_dasy, dasy_sheet, ecu, a2l_type, customer, excel_file_xcp):
        """
        updates xcp config and reduce a2l for dasy
        Args:
          xcp (object): instance of xcp update class
          a2l_dasy (str): dasy a2l
          dasy_sheet (str): sheet name in the xcp database excel
          ecu (str): ecu name
          a2l_type (str): a2l type
          customer (str): customer
          excel_file_xcp (str): xcp excel path

        """
        logger.info(f"###### Start procedure for {a2l_type} #######")
        xcp.delete_signals(xcpconfig, a2l_dasy, ecu, customer, lean_choise)
        ecu_index_dasy = xcp.find_ECU(xcpconfig, ecu)
        logger.info("Updating XCP_Database.xlsx cycle times for DASy")
        update_database_cycle_times(dasy_sheet, a2l_dasy, xcpconfig, ecu_index_dasy, ecu)
        logger.info("Extract Dasy data from XCP_Database.xlsx")
        xcp_dasy = xcp.parseXCP(dasy_sheet, excel_file_xcp)
        logger.info(f"Start parsing full XCP list from  {a2l_dasy}")
        a2l_dasy_list = xcp.extract_A2l(a2l_dasy)
        logger.info("Compare Dasy XCP_Database.xlsx XCP entries against A2L file")
        xcp.parseA2l(a2l_dasy, xcp_dasy, a2l_dasy_list)
        if xcp.a2lfile_missvar != {}:
            raise Exception("Missing XCP variables")

        if xcp_dasy:
            logger.info("Updating XCP configuration file for DASy")
            """" Get the index for DASy ECU"""
            for missing_xcp in reversed(xcp_dasy):
                xcp.add_XCP(xcpconfig, missing_xcp, ecu_index_dasy, "Dasy")
            logger.info("Finished updating XCP configuration file for DASy")
            complete_list_dasy = xcp.parseXCPconfig2(xcpconfig, ecu_index_dasy)
            if lean_choise and a2l_dasy is not None:
                xcp.reduce_A2l(a2l_dasy, complete_list_dasy, a2l_type, customer)

    try:
        lean_choise = True
        xcp_fl, xcp_fr, xcp_rl, xcp_rr = [], [], [], []
        ecus = ["RadarFC_Loc", "RadarFC_Obj", "DASY_BASE_01", "RadarFL", "RadarFR", "RadarRL", "RadarRR"]
        xcpconfig = os.path.abspath(os.path.join(os.getcwd(), r"../../../../CustomerPrj/XCP/XCP_config_gen.xcpcfg"))
        dict_rear = {"xcp_RadarFL": "RadarFL", "xcp_RadarFR": "RadarFR", "xcp_RadarRL": "RadarRL",
                     "xcp_RadarRR": "RadarRR"}
        excel_file_xcp = os.path.abspath(os.path.join(os.getcwd(), r"../../../../CustomerPrj/XCP/XCP_Database.xlsx"))
        filepath = os.path.abspath(os.path.join(os.getcwd(), r"../Control/Missing_XCP_variables_in_A2L.txt"))
        ################# Common part #############################################

        with open(filepath, 'w') as file:
            file.close()

        a2l_list = []
        if a2l_front_loc is not None:
            a2l_list.append(a2l_front_loc)
        elif a2l_front_obj is not None:
            a2l_list.append(a2l_front_obj)
        elif a2l_rear is not None:
            a2l_list.append(a2l_rear)
        elif a2l_dasy is not None:
            a2l_list.append(a2l_dasy)

        xcp = XCP_to_A2L_diff.XCPConfigurator("")  # create object

        ############### DaSy Section ##################################
        if a2l_dasy:
            dasy_sheet = "xcp_Dasy"
            ecu = "ACP_FD3"
            a2l_type = "ACP_FD3"
            generate_dasy(xcp, a2l_dasy, dasy_sheet, ecu, a2l_type, customer, excel_file_xcp)

        if a2l_dasy_delta1:
            dasy_sheet = "xcp_DPCdelta1"
            ecu = "DPCdelta1"
            a2l_type = "DPCDelta1"
            generate_dasy(xcp, a2l_dasy_delta1, dasy_sheet, ecu, a2l_type, customer, excel_file_xcp)

        if a2l_dasy_delta5:
            dasy_sheet = "xcp_DPCdelta5"
            ecu = "DPCdelta5"
            a2l_type = "DPCDelta5"
            generate_dasy(xcp, a2l_dasy_delta5, dasy_sheet, ecu, a2l_type, customer, excel_file_xcp)

        ############### End DaSy Section ##################################

        ############### RadarFC Locations Section ##################################

        if a2l_front_loc:
            tag = "RadarFC_Loc"
            a2l_type = "RadarFC_Locations_Gamma"
            logger.info(f"###### Start procedure for {a2l_type} #######")
            xcp.delete_signals(xcpconfig, a2l_front_loc, tag, customer, lean_choise)
            """" Get the index for Front Radar ECU"""
            ecu_index_front = xcp.find_ECU(xcpconfig, "RadarFC_Loc")
            logger.info("Updating XCP_Database.xlsx cycle times for RadarFC Locations")
            update_database_cycle_times("xcp_RPCgamma1", a2l_front_loc, xcpconfig, ecu_index_front, tag)
            logger.info("Extract RadarFC Locations data from XCP_Database.xlsx")
            xcp_fc_loc = xcp.parseXCP("xcp_RPCgamma1", excel_file_xcp)
            logger.info(f"Start parsing full XCP list from  {a2l_front_loc}")
            a2l_front_loc_list = xcp.extract_A2l(a2l_front_loc)
            logger.info("Compare Dasy XCP_Database.xlsx XCP entries against A2L file")
            xcp.parseA2l(a2l_front_loc, xcp_fc_loc, a2l_front_loc_list)
            if xcp.a2lfile_missvar != {}:
                raise Exception("Missing XCP variables")

            if xcp_fc_loc:
                logger.info("Updating XCP configuration file for RadarFC Locations")
                for missing_xcp in reversed(xcp_fc_loc):
                    xcp.add_XCP(xcpconfig, missing_xcp, ecu_index_front, "Radar")
                logger.info("Finished updating XCP configuration file for RadarFC Locations")
                complete_list_front = xcp.parseXCPconfig2(xcpconfig, ecu_index_front)
                if lean_choise and a2l_front_loc is not None:
                    xcp.reduce_A2l(a2l_front_loc, complete_list_front, a2l_type, customer)
            ############### End RadarFC Locations Section ##################################

            ############### RadarFC Objects Section ##################################

        if a2l_front_obj:
            if customer != "FORD":
                tag = "RadarFC_Obj"
                a2l_type = "RadarFC_Objects_Alpha"
                sheet_name = "xcp_RPCalpha2"
            else:
                tag = "RadarFC"
                a2l_type = "RadarFC_Objects"
                sheet_name = "xcp_RadarFC"
            logger.info(f"###### Start procedure for {a2l_type} #######")
            xcp.delete_signals(xcpconfig, a2l_front_obj, tag, customer, lean_choise)
            ecu_index_front = xcp.find_ECU(xcpconfig, tag)
            """ Update excel database cycle times """
            logger.info("Updating XCP_Database.xlsx cycle times for RadarFC Objects")
            update_database_cycle_times(sheet_name, a2l_front_obj, xcpconfig, ecu_index_front, tag)
            logger.info("Extract RadarFC Locations data from XCP_Database.xlsx")
            xcp_fc_obj = xcp.parseXCP(sheet_name, excel_file_xcp)
            logger.info(f"Start parsing full XCP list from  {a2l_front_obj}")
            a2l_front_obj_list = xcp.extract_A2l(a2l_front_obj)
            logger.info("Compare Dasy XCP_Database.xlsx XCP entries against A2L file")
            xcp.parseA2l(a2l_front_obj, xcp_fc_obj, a2l_front_obj_list)
            if xcp.a2lfile_missvar != {}:
                raise Exception("Missing XCP variables")

            for missing_xcp in reversed(xcp_fc_obj):
                xcp.add_XCP(xcpconfig, missing_xcp, ecu_index_front, "Radar")
            logger.info("Finished updating XCP configuration file for RadarFC")
            complete_list_front = xcp.parseXCPconfig2(xcpconfig, ecu_index_front)
            if lean_choise and a2l_front_obj is not None:
                xcp.reduce_A2l(a2l_front_obj, complete_list_front, a2l_type, customer)

        ############### END RadarFC Objects Section ##################################

        ############### Radar Rear Section ##################################

        if a2l_rear:
            logger.info(f"###### Start procedure for RearRadar(s) #######")
            logger.info(f"Start parsing full XCP list from  {a2l_rear}")
            a2l_rear_list = xcp.extract_A2l(a2l_rear)
            reduced = False
            for sheet, rear_ecu in dict_rear.items():
                logger.info(f"###### Updating for {rear_ecu} #######")
                logger.info("Extract Rear Radar data from XCP_Database.xlsx")
                xcp_rr = xcp.parseXCP(sheet, excel_file_xcp)
                if xcp_rr:
                    xcp.delete_signals(xcpconfig, a2l_rear, rear_ecu, customer, lean_choise)
                    ecu_index_rear = xcp.find_ECU(xcpconfig, rear_ecu)
                    logger.info("Updating XCP_Database.xlsx cycle times for Radar Rear")
                    update_database_cycle_times(rear_ecu, a2l_rear, xcpconfig, ecu_index_rear, tag)
                    logger.info("Compare RearRadar XCP_Database.xlsx XCP entries against A2L file")
                    xcp.parseA2l(a2l_rear, xcp_rr, a2l_rear_list)
                    if xcp.a2lfile_missvar != {}:
                        raise Exception("Missing XCP variables")
                    if ecu_index_rear is not None:
                        ecu_index_rear = xcp.find_ECU(xcpconfig, rear_ecu)
                        logger.info(f"Updating XCP configuration file for {rear_ecu}")
                        for missing_xcp in reversed(xcp_rr):
                            xcp.add_XCP(xcpconfig, missing_xcp, ecu_index_rear, "Radar")
                        logger.info(f"Finished updating XCP configuration file for {rear_ecu}")
                        complete_list_rear = xcp.parseXCPconfig2(xcpconfig, ecu_index_rear)
                        if complete_list_rear is not None and reduced is False:
                            if lean_choise and a2l_rear is not None:
                                xcp.reduce_A2l(a2l_rear, complete_list_rear, "RadarCorner", customer)
                                reduced = True
                else:
                    logger.info(f"No XCP entries in XCP_Database.xlsx")

        #change relative a2l paths to absolute if any
        changeRelativeA2lPathToAbsolute(xcpconfig)

    except Exception as e:
        logger.error(f"Failed to update xcpconfiguration --> {e}")
        raise e


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Automated fix of A2L file with Canape.')
    commandLineParser.add_argument('--a2l_dasy', action="store", dest="a2l_dasy", required=False, default=None,
                                   help="Absolute path to customer DASy or Toliman A2L")
    commandLineParser.add_argument('--dasy_variant', action="store", dest="dasy_variant", required=False,
                                   default="",
                                   help="Dasy variant")

    commandLineParser.add_argument('--a2l_FC_radar_locations', action="store", dest="a2l_front_loc", required=False,
                                   default="-",
                                   help="Absolute path to customer RadarFC Locations A2L")
    commandLineParser.add_argument('--a2l_FC_radar_objects', action="store", dest="a2l_front_obj", required=False,
                                   default="-",
                                   help="Absolute path to customer RadarFC Objects A2L")
    commandLineParser.add_argument('--a2l_corner_radar', action="store", dest="a2l_rear", required=False, default="-",
                                   help="Absolute path to customer Radar Rear A2L")
    commandLineParser.add_argument('--customer', action="store", dest="customer", required=False, default="-",
                                   help="Customer project")
    arguments = commandLineParser.parse_args()

    dasy_a2l_path_arg = arguments.a2l_dasy

    #for OD dasy variant handling
    dasy_variant_arg = arguments.dasy_variant
    dasy_delta1_a2l_path_arg = None
    dasy_delta5_a2l_path_arg = None

    if (dasy_a2l_path_arg == None and arguments.a2l_front_obj == "RPC_ALPHA_TAKE_FROM_ZIP") or (dasy_a2l_path_arg == "-"):
        # dasy a2l not required for testing RPC Alpha only Radar a2l is need to be updated
        dasy_a2l_path = None
    elif dasy_a2l_path_arg is not None and str(dasy_a2l_path_arg).strip() != "":
        #Ford toliman a2l path is directly given from jenkins, no extraction is needed
        dasy_a2l_path = dasy_a2l_path_arg
    else:
        dasy_a2l_path = None
        #OD dasy variants
        if dasy_variant_arg.lower() == "dpcdelta1":
            dasy_delta1_a2l_path_arg, _ = get_paths_dasy()
        elif dasy_variant_arg.lower() == "dpcdelta5":
            dasy_delta5_a2l_path_arg, _ = get_paths_dasy()


    radar_fc_a2l_path_loc = arguments.a2l_front_loc
    if radar_fc_a2l_path_loc.strip() == "-":
        radar_fc_a2l_path_loc = None

    radar_fc_a2l_path_obj = arguments.a2l_front_obj
    if radar_fc_a2l_path_obj.strip() == "-":
        radar_fc_a2l_path_obj = None
    elif radar_fc_a2l_path_obj == "RPC_ALPHA_TAKE_FROM_ZIP":
        radar_fc_a2l_path_obj, _, _ = get_paths_radar_fc()

    radar_corner_a2l_path = arguments.a2l_rear
    if radar_corner_a2l_path.strip() == "-":
        radar_corner_a2l_path = None

    customer = arguments.customer

    update_xcpconfig(radar_fc_a2l_path_loc, radar_fc_a2l_path_obj, radar_corner_a2l_path, customer, dasy_a2l_path,
                     dasy_delta1_a2l_path_arg, dasy_delta5_a2l_path_arg)