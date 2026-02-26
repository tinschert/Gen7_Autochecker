# -*- coding: utf-8 -*-
# @file TrafficSigns.py
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


import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import numpy as np
from copy import deepcopy
from json import loads as strToDict
import sys,os
from openpyxl import load_workbook

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger

class TrafficSign:
    """Contains calculation and evaluation of measured traffic signs"""
    def __init__(self, trace_file, database_excel_df, evaluation_excel_df, scenario_target_type, iteration) -> None:
        self.database_excel_df = database_excel_df
        self.trace_file = trace_file
        self.output_file = iteration + "_KPIresults.xlsx"
        self.calculated_parameters_dict = {}
        self.object_range = {}
        self.pair_indices = []
        
        self.camera_tolerance_time = 0.1 #seconds -> 100ms
        
        self.evaluation_database = self.getEvaluationInput(evaluation_excel_df, scenario_target_type)

        self.evaluation_results = {}


    def trimData(self, calculated_dx):
        """
        finds start and end index of the TS by trimming dummy values

        Args:
          calculated_dx: 

        Returns:

        """
        object_range = {}
        gt = calculated_dx["gt"]
        cam = calculated_dx["cam"]

        #gt
        count = 1
        start_index = 0
        for i in range(1, len(gt[1])):
            if gt[1][i] != gt[1][i-1]:
                count += 1
            else:
                count = 1
            if count == 2:
                start_index = i 
                break

        end_index = start_index

        for i in range(start_index + 1, len(gt[1])):
            if gt[1][i] == gt[1][i-1]:
                count += 1
            else:
                count = 1
            
            if count == 6:
                end_index = i-4
                break
        

        gt_time_range = [gt[0][start_index], gt[0][end_index]]
        
        gt[0] = gt[0][start_index:end_index]
        gt[1] = gt[1][start_index:end_index]
        object_range["gt"] = [start_index,end_index]


        #find camera start and end timestamps to fit in gt range        
        cam_st_index = 0
        for i,value in enumerate(cam[0]):
            if value>=gt_time_range[0]:
                cam_st_index = i
                break

        cam_end_index = cam_st_index
        for j in range(cam_st_index+1, len(cam[0])):
            if cam[0][j] >= gt_time_range[1]:
                cam_end_index = j-1
                break
        if cam_end_index == cam_st_index:
            cam_end_index = len(cam[0])-1
        
        cam[0] = cam[0][cam_st_index:cam_end_index]
        cam[1] = cam[1][cam_st_index:cam_end_index]
        object_range["cam"] = [cam_st_index,cam_end_index]

        calculated_dx["gt"] = gt
        calculated_dx["cam"] = cam

        if len(calculated_dx["gt"][0])==0 or len(calculated_dx["cam"][0])==0:
            logger.error("Data is Empty after trimming dummy values")

        return object_range, calculated_dx

        

    def findCameraGtPairs(self,calculated_dx):
        """
        for every camera sample corresponding ground truth sample will be paired and indices will be returned

        Args:
          calculated_dx: 

        Returns:
          

        """
        camera_data = calculated_dx["cam"]
        gt_data = calculated_dx["gt"]

        pair_indices = []

        for cam_index, cam_time in enumerate(camera_data[0]):
            temp = {}
            gt_index = self.find_nearest_index(gt_data[0], cam_time)
            if gt_index>=0:
                temp["gt_index"] = gt_index
                temp["cam_index"] = cam_index
                pair_indices.append(deepcopy(temp))

        return pair_indices 


    def getEvaluationInput(self, excel_path, sheet_name):
        """
        

        Args:
          excel_path: 
          sheet_name: 

        Returns:

        """
        
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df = df.iloc[1:]
        df.columns = df.iloc[0]
        df = df.iloc[1:]
        self.parameters_order = list(df["Parameter Name"])
        return_dict = {}
        for i,row in df.iterrows():
            if str(row["script_input"]) == "nan" or str(row["script_input"]).upper()=="NA":
                continue
            temp = "{"+row["script_input"]+"}"
            return_dict[row["Parameter Name"].strip().lower()] = strToDict(temp)
        return return_dict



    def getTraceData(self, signal="", sysvar=[]):
        """
        

        Args:
          signal:  (Default value = "")
          sysvar:  (Default value = [])

        Returns:

        """
        return_list = []      #[timestamp, samples]
        if sysvar==[]:
            #signals
            return_list = [deepcopy(self.trace_file.get(signal)).timestamps, deepcopy(self.trace_file.get(signal)).samples]
            logger.info(f"Extracted -> {signal}")
        else:
            #sysvars
            indices = self.trace_file.whereis(sysvar[0])
            for tup in indices:
                tup = list(tup)
                tup.insert(0,sysvar[0])
                sig = self.trace_file.get(tup[0],tup[1],tup[2])
                if [sig.name, sig.source.name] == sysvar:
                    return_list = [deepcopy(sig.timestamps), deepcopy(sig.samples)]
                    logger.info(f"Extracted -> {sysvar}")
                    break
        return deepcopy(return_list)
    
    def getTraceDataSigBased(self, symbol_name):
        """


        Args:
          signal:  (Default value = "")
          sysvar:  (Default value = [])

        Returns:

        """
        return_list = []  # [timestamp, samples]
        matched_sigs = self.trace_file.search(symbol_name)
        sig = ""
        for match in matched_sigs:
            if match.endswith(symbol_name):
                sig = match
                break

        if sig=="":
            logger.info(f"NOT FOUND -> {symbol_name}")
            return [[],[]]
        return_list = [deepcopy(self.trace_file.get(sig)).timestamps,
                           deepcopy(self.trace_file.get(sig)).samples]

        logger.info(f"Extracted -> {symbol_name}")
        return deepcopy(return_list)
   



    def find_nearest_index(self, array, value) -> int:
        """
        

        Args:
          array: 
          value: 

        Returns:

        """
        if len(array) == 0:
            return -1
        absolute_diff = np.abs(array - value)
        nearest_index = np.argmin(absolute_diff)

        if array[nearest_index]>value:
            return nearest_index-1

        return nearest_index
    


    def removeOutliers(self, data):
        """
        revomes zeros from given signal data
        data is a list [[timestamps],[samples]]

        Args:
          data: 

        Returns:

        """
        required_times = []
        required_values = []
        leng = len(data[0])
        for index in range(leng):
            if int(data[1][index])!=0:
                required_times.append(data[0][index])
                required_values.append(data[1][index])

        required_times= np.array(required_times)
        required_values= np.array(required_values)

        return [required_times,required_values]

    def shiftByOffset(self, values_array, offset):
        """
        

        Args:
          values_array: 
          offset: 

        Returns:

        """
        return values_array + offset


    def shiftTimestamps(self, timestamp_array, shift_time):
        """
        

        Args:
          timestamp_array: 
          shift_time: 

        Returns:

        """
        return timestamp_array + shift_time
    
    def validateTimestamp(self, timestamp_array, tolerance):
        """
        

        Args:
          timestamp_array: 
          tolerance: 

        Returns:

        """
        missing_count = 0
        difference = np.diff(timestamp_array)
        for diff in difference:
            if diff > tolerance:
                missing_count += diff//tolerance
        return missing_count

    
    def comapareDiff(self, gt_value, camera_value, diff):
        """
        

        Args:
          gt_value: 
          camera_value: 
          diff: 

        Returns:

        """
        if "%" in diff:
            max_diff = (float(diff.replace("%",""))/100) * gt_value
            if abs(gt_value-camera_value) > max_diff:
                return False  #failed
        else:
            if abs(gt_value-camera_value) > float(diff):
                return False  #failed
        return True
    
    def compareValue(self, camera_value, expected_value):
        """
        

        Args:
          camera_value: 
          expected_value: 

        Returns:

        """
        
        if isinstance(camera_value, bytes):
            
            camera_value = camera_value.decode("utf-8")
            expr = str(camera_value) + expected_value
            expr = expr.split("==")
            if len(expr)<2:
                return False
            if expr[0].strip() == expr[1].strip():
                return True
            else:
                return False
        expr = str(camera_value) + expected_value
        
        if "cam_value" in expr:
            expr = expected_value.replace("cam_value",str(camera_value))
              
        if eval(expr):
            return True
        return False
    
    def splitOnRangeByDx(self, target_parameter, data, ranges):
        """
        

        Args:
          target_parameter: 
          data: 
          ranges: 

        Returns:

        """
        logger.info(f"In splitOnRangeByDx for -> {target_parameter}")
        for key,value in ranges.items():
            rng = value["range"]
            new_rng = []
            for i in rng:
                if i == "-":
                    new_rng.append(None)
                else:
                    new_rng.append(i)

            ranges[key] = new_rng


        return_result = {"cam":{},"gt":{}}

        gt_dx_timestamps = self.calculated_parameters_dict["dx"]["gt"][0]
        gt_dx_samples = self.calculated_parameters_dict["dx"]["gt"][1]

        cal_dy_gt_timestamps = data["gt"][0]
        cal_dy_gt_samples = data["gt"][1]
        
        #split the arrays by range
        cam_time_index_far = None
        cam_time_index_mid = None
        i = 0
        #far range---------------------------
            #GT
        while gt_dx_samples[i] > ranges["far"][0]:
            i+=1
            if i==len(gt_dx_samples):
                logger.error("Ground Truth data only present in far range or data missing")
                i=i-1
                break
        if i==0:
            logger.warning(f"{target_parameter} GT not found in FAR range")
            gt_dy_timestamp_index_far = None
            return_result["gt"]["far"] = [[],[]]
            return_result["cam"]["far"] = [[],[]]
        else:
            gt_dx_timestamp = gt_dx_timestamps[i]
            gt_dy_timestamp_index_far = np.where(cal_dy_gt_timestamps == gt_dx_timestamp)[0][0]

            return_result["gt"]["far"] = [data["gt"][0][None:gt_dy_timestamp_index_far], 
                                data["gt"][1][None:gt_dy_timestamp_index_far]]
                #camera
            gt_dy_timestamp = cal_dy_gt_timestamps[gt_dy_timestamp_index_far]
            
            cam_time_index_far = self.find_nearest_index(data["cam"][0], gt_dy_timestamp)
            
            if cam_time_index_far < 0:
                return_result["cam"]["far"] = [[],[]]
                logger.warning(f"{target_parameter} Not Present in FAR range  in cam")
            else:
                return_result["cam"]["far"] = [data["cam"][0][None:cam_time_index_far], 
                                data["cam"][1][None:cam_time_index_far]]
            


        #mid range-------------------------
            #GT
        while gt_dx_samples[i] > ranges["mid"][0]:
            i+=1
            if i==len(gt_dx_samples):
                logger.error("Ground Truth data missing while finding mid range or data missing")
                i=i-1
                break

        if i==0:
            logger.warning(f"{target_parameter} GT not found in MID range")
            gt_dy_timestamp_index_mid=None
            return_result["gt"]["mid"] = [[],[]]
            return_result["cam"]["mid"] = [[],[]]
        else:
            gt_dx_timestamp = gt_dx_timestamps[i]
            gt_dy_timestamp_index_mid = np.where(cal_dy_gt_timestamps==gt_dx_timestamp)[0][0]

            return_result["gt"]["mid"] = [data["gt"][0][gt_dy_timestamp_index_far:gt_dy_timestamp_index_mid], 
                                data["gt"][1][gt_dy_timestamp_index_far:gt_dy_timestamp_index_mid]]

                #camera
            gt_dy_timestamp = cal_dy_gt_timestamps[gt_dy_timestamp_index_mid]
            cam_time_index_mid = self.find_nearest_index(data["cam"][0], gt_dy_timestamp)
            if cam_time_index_mid < 0:
                return_result["cam"]["mid"] = [[],[]]
                logger.warning(f"{target_parameter} Not Present in MID range above in cam")
            else:
                return_result["cam"]["mid"] = [data["cam"][0][cam_time_index_far:cam_time_index_mid], 
                                data["cam"][1][cam_time_index_far:cam_time_index_mid]]
            

        #near range-----------------------
            #GT
        return_result["gt"]["near"] = [data["gt"][0][gt_dy_timestamp_index_mid:None], 
                             data["gt"][1][gt_dy_timestamp_index_mid:None]]

            #camera
        return_result["cam"]["near"] = [data["cam"][0][cam_time_index_mid:None], 
                             data["cam"][1][cam_time_index_mid:None]]
        
        
        return return_result
        


        

    def splitOnRange(self, target_parameter, data, ranges) -> dict:
        """
        

        Args:
          target_parameter: 
          data: 
          ranges: 

        Returns:

        """
        "splits the given data into 3 ranges - far,mid,near based on given ranges"

        for key,value in ranges.items():
            rng = value["range"]
            new_rng = []
            for i in rng:
                if i == "-":
                    new_rng.append(None)
                else:
                    new_rng.append(i)

            ranges[key] = new_rng
        
        range_index_gt = {"far":[],"mid":[],"near":[]}
        range_index_cam = {"far":[],"mid":[],"near":[]}

        return_result = {"cam":{},"gt":{}}

        cal_gt_samples = data["gt"][1]

        if len(cal_gt_samples) == 0:
            logger.error(f"Ground truth data is empty to split in {target_parameter}")
            raise Exception(f"Ground truth data is empty to split in {target_parameter}")

        #split the arrays by range

        i = 0
        #far range---------------------------
            #GT
        while cal_gt_samples[i] > ranges["far"][0]:
            i+=1
            if i==len(cal_gt_samples):
                logger.error("Ground Truth data only present in far range or data missing")
                i=i-1
                break

        range_index_gt["far"] = [None,i]
        return_result["gt"]["far"] = [data["gt"][0][range_index_gt["far"][0]:range_index_gt["far"][1]], 
                             data["gt"][1][range_index_gt["far"][0]:range_index_gt["far"][1]]]
            #camera
        gt_time = data["gt"][0][i]
        
        cam_time_index = self.find_nearest_index(data["cam"][0], gt_time)
        
        if cam_time_index < 0:
            range_index_cam["far"] = [None,None]
            return_result["cam"]["far"] = [[],[]]
            logger.warning(f"{target_parameter} Not Present in FAR range  in cam")
        else:
            range_index_cam["far"] = [None,cam_time_index]
            return_result["cam"]["far"] = [data["cam"][0][range_index_cam["far"][0]:range_index_cam["far"][1]], 
                             data["cam"][1][range_index_cam["far"][0]:range_index_cam["far"][1]]]


        #mid range-------------------------
            #GT
        while cal_gt_samples[i] > ranges["mid"][0]:
            i+=1
            if i==len(cal_gt_samples):
                logger.error("Ground Truth data Missing while finding mid range")
                i=i-1
                break
        range_index_gt["mid"] = [range_index_gt["far"][1], i]
        return_result["gt"]["mid"] = [data["gt"][0][range_index_gt["mid"][0]:range_index_gt["mid"][1]], 
                             data["gt"][1][range_index_gt["mid"][0]:range_index_gt["mid"][1]]]

            #camera
        gt_time = data["gt"][0][i]
        cam_time_index = self.find_nearest_index(data["cam"][0], gt_time)
        if cam_time_index < 0:
            range_index_cam["mid"] = [None,None]
            return_result["cam"]["mid"] = [[],[]]
            logger.warning(f"{target_parameter} Not Present in MID range above in cam")
        else:
            range_index_cam["mid"] = [range_index_cam["far"][1],cam_time_index]
            return_result["cam"]["mid"] = [data["cam"][0][range_index_cam["mid"][0]:range_index_cam["mid"][1]], 
                             data["cam"][1][range_index_cam["mid"][0]:range_index_cam["mid"][1]]]


        #near range-----------------------
            #GT
        range_index_gt["near"] = [i, None]
        return_result["gt"]["near"] = [data["gt"][0][range_index_gt["near"][0]:range_index_gt["near"][1]], 
                             data["gt"][1][range_index_gt["near"][0]:range_index_gt["near"][1]]]

            #camera
        range_index_cam["near"] = [cam_time_index, None]
        return_result["cam"]["near"] = [data["cam"][0][range_index_cam["near"][0]:range_index_cam["near"][1]], 
                             data["cam"][1][range_index_cam["near"][0]:range_index_cam["near"][1]]]
        
        
        return return_result

    def cal_DX(self, df) -> dict:
        """this will get signal data from file and
        then apply calculations if needed for data like timeshift, fmu"""

        logger.info(f" ---Dx---")
        temp = {}  # to store keys to identify which is gt and which is camera sig
        dict_dx_data = {}
        for idx, row in df.iterrows():
            # print(row["identifier"])
            if row["identifier"] == "dx_raw_gt":
                temp["gt"] = row["Name"] + "_" + row["Message"].split("::")[-1]
                dict_dx_data["gt"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
                # dict_dx_data["gt"] = self.removeOutliers(dict_dx_data["gt"])
                # GT dx conversion, shifting, etc..

                if row["timeshift"] != "NA":
                    dict_dx_data["gt"][0] = self.shiftTimestamps(dict_dx_data["gt"][0], float(row["timeshift"]))
                if row["offset"] != "NA":
                    dict_dx_data["gt"][1] = self.shiftByOffset(dict_dx_data["gt"][1], float(row["offset"]))

            else:
                temp["cam"] = row["Name"]
                dict_dx_data["cam"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
        if len(temp) != 2:
            logger.error("obj Dx error occured when processing input database")

        return dict_dx_data

    def evaluate_DX(self, calculated_dx):
        "evaluates data based on evaluation excel"
        result_keys = ["total_gt_samples", "total_camera_samples", "camera_missing_samples_count",
                       "total_camera_gt_pairs", "passed_samples", "failed_samples", "result"]
        evaluation_result = {"far": {}, "mid": {}, "near": {}}

        for key in evaluation_result.keys():
            for i in result_keys:
                evaluation_result[key][i] = 0

        split_data = self.splitOnRange("dx", calculated_dx, deepcopy(self.evaluation_database["dx"]))

        # FAR -----------------------------------------------------------------------------
        far_range_gt = split_data["gt"]["far"]  # list [[timestamps], [smaples]]
        far_range_cam = split_data["cam"]["far"]

        evaluation_result["far"]["total_gt_samples"] = len(far_range_gt[0])
        evaluation_result["far"]["total_camera_samples"] = len(far_range_cam[0])
        evaluation_result["far"]["camera_missing_samples_count"] = self.validateTimestamp(far_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(far_range_cam[0])):
            camera_value = far_range_cam[1][i]

            gt_index = self.find_nearest_index(far_range_gt[0], far_range_cam[0][i])
            if gt_index >= 0:
                gt_value = far_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dx"]["far"]["diff"])
                evaluation_result["far"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["far"]["passed_samples"] += 1
                else:
                    evaluation_result["far"]["failed_samples"] += 1

        # MID ------------------------------------------------------------------------------
        mid_range_gt = split_data["gt"]["mid"]  # list [[timestamps], [smaples]]
        mid_range_cam = split_data["cam"]["mid"]

        evaluation_result["mid"]["total_gt_samples"] = len(mid_range_gt[0])
        evaluation_result["mid"]["total_camera_samples"] = len(mid_range_cam[0])
        evaluation_result["mid"]["camera_missing_samples_count"] = self.validateTimestamp(mid_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(mid_range_cam[0])):
            camera_value = mid_range_cam[1][i]

            gt_index = self.find_nearest_index(mid_range_gt[0], mid_range_cam[0][i])
            if gt_index > 0:
                gt_value = mid_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dx"]["mid"]["diff"])
                evaluation_result["mid"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["mid"]["passed_samples"] += 1
                else:
                    evaluation_result["mid"]["failed_samples"] += 1

        # NEAR -----------------------------------------------------------------------------
        near_range_gt = split_data["gt"]["near"]  # list [[timestamps], [smaples]]
        near_range_cam = split_data["cam"]["near"]

        evaluation_result["near"]["total_gt_samples"] = len(near_range_gt[0])
        evaluation_result["near"]["total_camera_samples"] = len(near_range_cam[0])
        evaluation_result["near"]["camera_missing_samples_count"] = self.validateTimestamp(near_range_cam[0],
                                                                                           self.camera_tolerance_time)

        for i in range(len(near_range_cam[0])):
            camera_value = near_range_cam[1][i]

            gt_index = self.find_nearest_index(near_range_gt[0], near_range_cam[0][i])
            if gt_index > 0:
                gt_value = near_range_gt[1][gt_index]

                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dx"]["near"]["diff"])
                evaluation_result["near"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["near"]["passed_samples"] += 1
                else:
                    evaluation_result["near"]["failed_samples"] += 1

        temp_iter = deepcopy(evaluation_result)
        for key, value in temp_iter.items():
            temp = {}
            if (value["total_camera_gt_pairs"]):
                expected = self.evaluation_database["dx"][key]["required_verdict_per"]
                actual = round((value["passed_samples"] / value["total_camera_gt_pairs"]) * 100, 2)
                temp["expected"] = expected
                temp["actual"] = actual
                temp["verdict"] = "PASS" if actual >= expected else "FAIL"
            else:
                temp["expected"] = self.evaluation_database["dx"][key]["required_verdict_per"]
                temp["actual"] = "-"
                temp["verdict"] = "FAIL"
            evaluation_result[key]["result"] = temp

        return evaluation_result

    def cal_DY(self, df) -> dict:
        """this will get signal data from file and
        then apply calculations if needed for data like timeshift, fmu"""

        logger.info(f" ---Dy---")
        temp = {}  # to store keys to identify which is gt and which is camera sig
        dict_dx_data = {}
        for idx, row in df.iterrows():
            # print(row["identifier"])
            if row["identifier"] == "dy_raw_gt":
                temp["gt"] = row["Name"] + "_" + row["Message"].split("::")[-1]
                dict_dx_data["gt"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
                # dict_dx_data["gt"] = self.removeOutliers(dict_dx_data["gt"])
                # GT dx conversion, shifting, etc..
                if row["timeshift"] != "NA":
                    dict_dx_data["gt"][0] = self.shiftTimestamps(dict_dx_data["gt"][0], float(row["timeshift"]))
                if row["offset"] != "NA":
                    dict_dx_data["gt"][1] = self.shiftByOffset(dict_dx_data["gt"][1], float(row["offset"]))

            else:

                temp["cam"] = row["Name"]
                dict_dx_data["cam"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
        if len(temp) != 2:
            logger.error("obj Dy error occured when processing input database")

        if self.object_range:
            gt_rng = self.object_range["gt"]
            dict_dx_data["gt"][0] = dict_dx_data["gt"][0][gt_rng[0]:gt_rng[1]]
            dict_dx_data["gt"][1] = dict_dx_data["gt"][1][gt_rng[0]:gt_rng[1]]

            cam_rng = self.object_range["cam"]
            dict_dx_data["cam"][0] = dict_dx_data["cam"][0][cam_rng[0]:cam_rng[1]]
            dict_dx_data["cam"][1] = dict_dx_data["cam"][1][cam_rng[0]:cam_rng[1]]

        return dict_dx_data

    def evaluate_DY(self, calculated_dy):
        "evaluates data based on evaluation excel"
        logger.info("evaluate_DY ----")
        result_keys = ["total_gt_samples", "total_camera_samples", "camera_missing_samples_count",
                       "total_camera_gt_pairs", "passed_samples", "failed_samples"]
        evaluation_result = {"far": {}, "mid": {}, "near": {}}

        for key in evaluation_result.keys():
            for i in result_keys:
                evaluation_result[key][i] = 0

        split_data = self.splitOnRangeByDx("dy", calculated_dy, deepcopy(self.evaluation_database["dy"]))

        # FAR -----------------------------------------------------------------------------
        far_range_gt = split_data["gt"]["far"]  # list [[timestamps], [smaples]]
        far_range_cam = split_data["cam"]["far"]

        evaluation_result["far"]["total_gt_samples"] = len(far_range_gt[0])
        evaluation_result["far"]["total_camera_samples"] = len(far_range_cam[0])
        evaluation_result["far"]["camera_missing_samples_count"] = self.validateTimestamp(far_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(far_range_cam[0])):
            camera_value = far_range_cam[1][i]

            gt_index = self.find_nearest_index(far_range_gt[0], far_range_cam[0][i])
            if gt_index > 0:
                gt_value = far_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dy"]["far"]["diff"])
                evaluation_result["far"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["far"]["passed_samples"] += 1
                else:
                    evaluation_result["far"]["failed_samples"] += 1

        # MID ------------------------------------------------------------------------------
        mid_range_gt = split_data["gt"]["mid"]  # list [[timestamps], [smaples]]
        mid_range_cam = split_data["cam"]["mid"]

        evaluation_result["mid"]["total_gt_samples"] = len(mid_range_gt[0])
        evaluation_result["mid"]["total_camera_samples"] = len(mid_range_cam[0])
        evaluation_result["mid"]["camera_missing_samples_count"] = self.validateTimestamp(mid_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(mid_range_cam[0])):
            camera_value = mid_range_cam[1][i]

            gt_index = self.find_nearest_index(mid_range_gt[0], mid_range_cam[0][i])
            if gt_index > 0:
                gt_value = mid_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dy"]["mid"]["diff"])
                evaluation_result["mid"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["mid"]["passed_samples"] += 1
                else:
                    evaluation_result["mid"]["failed_samples"] += 1

        # NEAR -----------------------------------------------------------------------------
        near_range_gt = split_data["gt"]["near"]  # list [[timestamps], [smaples]]
        near_range_cam = split_data["cam"]["near"]

        evaluation_result["near"]["total_gt_samples"] = len(near_range_gt[0])
        evaluation_result["near"]["total_camera_samples"] = len(near_range_cam[0])
        evaluation_result["near"]["camera_missing_samples_count"] = self.validateTimestamp(near_range_cam[0],
                                                                                           self.camera_tolerance_time)

        for i in range(len(near_range_cam[0])):
            camera_value = near_range_cam[1][i]

            gt_index = self.find_nearest_index(near_range_gt[0], near_range_cam[0][i])
            if gt_index > 0:
                gt_value = near_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dy"]["near"]["diff"])
                evaluation_result["near"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["near"]["passed_samples"] += 1
                else:
                    evaluation_result["near"]["failed_samples"] += 1

        temp_iter = deepcopy(evaluation_result)
        for key, value in temp_iter.items():
            temp = {}
            if (value["total_camera_gt_pairs"]):
                expected = self.evaluation_database["dy"][key]["required_verdict_per"]
                actual = round((value["passed_samples"] / value["total_camera_gt_pairs"]) * 100, 2)
                temp["expected"] = expected
                temp["actual"] = actual
                temp["verdict"] = "PASS" if actual >= expected else "FAIL"
            else:
                temp["expected"] = self.evaluation_database["dy"][key]["required_verdict_per"]
                temp["actual"] = "-"
                temp["verdict"] = "FAIL"
            evaluation_result[key]["result"] = temp

        return evaluation_result

    def cal_DZ(self, df) -> dict:
        """this will get signal data from file and
        then apply calculations if needed for data like timeshift, fmu"""

        logger.info(f" ---Dz---")
        temp = {}  # to store keys to identify which is gt and which is camera sig
        dict_dx_data = {}
        for idx, row in df.iterrows():
            # print(row["identifier"])
            if row["identifier"] == "dz_raw_gt":
                temp["gt"] = row["Name"] + "_" + row["Message"].split("::")[-1]
                dict_dx_data["gt"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
                # dict_dx_data["gt"] = self.removeOutliers(dict_dx_data["gt"])
                # GT dx conversion, shifting, etc..
                if row["timeshift"] != "NA":
                    dict_dx_data["gt"][0] = self.shiftTimestamps(dict_dx_data["gt"][0], float(row["timeshift"]))
                if row["offset"] != "NA":
                    dict_dx_data["gt"][1] = self.shiftByOffset(dict_dx_data["gt"][1], float(row["offset"]))

            else:

                temp["cam"] = row["Name"]
                dict_dx_data["cam"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
        if len(temp) != 2:
            logger.error("obj Dz error occured when processing input database")

        if self.object_range:
            gt_rng = self.object_range["gt"]
            dict_dx_data["gt"][0] = dict_dx_data["gt"][0][gt_rng[0]:gt_rng[1]]
            dict_dx_data["gt"][1] = dict_dx_data["gt"][1][gt_rng[0]:gt_rng[1]]

            cam_rng = self.object_range["cam"]
            dict_dx_data["cam"][0] = dict_dx_data["cam"][0][cam_rng[0]:cam_rng[1]]
            dict_dx_data["cam"][1] = dict_dx_data["cam"][1][cam_rng[0]:cam_rng[1]]

        return dict_dx_data

    def evaluate_DZ(self, calculated_dz):
        "evaluates data based on evaluation excel"
        logger.info("evaluate_DZ ----")
        result_keys = ["total_gt_samples", "total_camera_samples", "camera_missing_samples_count",
                       "total_camera_gt_pairs", "passed_samples", "failed_samples"]
        evaluation_result = {"far": {}, "mid": {}, "near": {}}

        for key in evaluation_result.keys():
            for i in result_keys:
                evaluation_result[key][i] = 0

        split_data = self.splitOnRangeByDx("dz", calculated_dz, deepcopy(self.evaluation_database["dz"]))

        # FAR -----------------------------------------------------------------------------
        far_range_gt = split_data["gt"]["far"]  # list [[timestamps], [smaples]]
        far_range_cam = split_data["cam"]["far"]

        evaluation_result["far"]["total_gt_samples"] = len(far_range_gt[0])
        evaluation_result["far"]["total_camera_samples"] = len(far_range_cam[0])
        evaluation_result["far"]["camera_missing_samples_count"] = self.validateTimestamp(far_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(far_range_cam[0])):
            camera_value = far_range_cam[1][i]

            gt_index = self.find_nearest_index(far_range_gt[0], far_range_cam[0][i])
            if gt_index > 0:
                gt_value = far_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dz"]["far"]["diff"])
                evaluation_result["far"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["far"]["passed_samples"] += 1
                else:
                    evaluation_result["far"]["failed_samples"] += 1

        # MID ------------------------------------------------------------------------------
        mid_range_gt = split_data["gt"]["mid"]  # list [[timestamps], [smaples]]
        mid_range_cam = split_data["cam"]["mid"]

        evaluation_result["mid"]["total_gt_samples"] = len(mid_range_gt[0])
        evaluation_result["mid"]["total_camera_samples"] = len(mid_range_cam[0])
        evaluation_result["mid"]["camera_missing_samples_count"] = self.validateTimestamp(mid_range_cam[0],
                                                                                          self.camera_tolerance_time)

        for i in range(len(mid_range_cam[0])):
            camera_value = mid_range_cam[1][i]

            gt_index = self.find_nearest_index(mid_range_gt[0], mid_range_cam[0][i])
            if gt_index > 0:
                gt_value = mid_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dz"]["mid"]["diff"])
                evaluation_result["mid"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["mid"]["passed_samples"] += 1
                else:
                    evaluation_result["mid"]["failed_samples"] += 1

        # NEAR -----------------------------------------------------------------------------
        near_range_gt = split_data["gt"]["near"]  # list [[timestamps], [smaples]]
        near_range_cam = split_data["cam"]["near"]

        evaluation_result["near"]["total_gt_samples"] = len(near_range_gt[0])
        evaluation_result["near"]["total_camera_samples"] = len(near_range_cam[0])
        evaluation_result["near"]["camera_missing_samples_count"] = self.validateTimestamp(near_range_cam[0],
                                                                                           self.camera_tolerance_time)

        for i in range(len(near_range_cam[0])):
            camera_value = near_range_cam[1][i]

            gt_index = self.find_nearest_index(near_range_gt[0], near_range_cam[0][i])
            if gt_index > 0:
                gt_value = near_range_gt[1][gt_index]
                result = self.comapareDiff(gt_value, camera_value, self.evaluation_database["dz"]["near"]["diff"])
                evaluation_result["near"]["total_camera_gt_pairs"] += 1
                if result:
                    evaluation_result["near"]["passed_samples"] += 1
                else:
                    evaluation_result["near"]["failed_samples"] += 1

        temp_iter = deepcopy(evaluation_result)
        for key, value in temp_iter.items():
            temp = {}
            if (value["total_camera_gt_pairs"]):
                expected = self.evaluation_database["dz"][key]["required_verdict_per"]
                actual = round((value["passed_samples"] / value["total_camera_gt_pairs"]) * 100, 2)
                temp["expected"] = expected
                temp["actual"] = actual
                temp["verdict"] = "PASS" if actual >= expected else "FAIL"
            else:
                temp["expected"] = self.evaluation_database["dz"][key]["required_verdict_per"]
                temp["actual"] = "-"
                temp["verdict"] = "FAIL"
            evaluation_result[key]["result"] = temp

        return evaluation_result


    def cal_single_parameter(self, df, parameter) -> dict:
        """this will get signal data from file and
        then apply calculations if needed for data like timeshift, fmu"""

        logger.info(f" ---{parameter}---")
        temp = {}  # to store keys to identify which is gt and which is camera sig
        dict_dx_data = {}
        for idx, row in df.iterrows():
            # print(row["identifier"])
            if row["identifier"] == f"{parameter}_raw_gt":
                temp["gt"] = row["Name"] + "_" + row["Message"].split("::")[-1]
                dict_dx_data["gt"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
                # dict_dx_data["gt"] = self.removeOutliers(dict_dx_data["gt"])
                # GT dx conversion, shifting, etc..
                if row["timeshift"] != "NA":
                    dict_dx_data["gt"][0] = self.shiftTimestamps(dict_dx_data["gt"][0], float(row["timeshift"]))
                if row["offset"] != "NA":
                    dict_dx_data["gt"][1] = self.shiftByOffset(dict_dx_data["gt"][1], float(row["offset"]))

            else:

                temp["cam"] = row["Name"]
                dict_dx_data["cam"] = self.getTraceDataSigBased(row["Message"]+"::"+row["Name"])
        if len(temp) not in [1,2]:
            logger.error(f" {parameter} error occured when processing input database")

        if self.object_range:
            cam_rng = self.object_range["cam"]
            dict_dx_data["cam"][0] = dict_dx_data["cam"][0][cam_rng[0]:cam_rng[1]]
            dict_dx_data["cam"][1] = dict_dx_data["cam"][1][cam_rng[0]:cam_rng[1]]

        return dict_dx_data

    def evaluate_single_parameter(self, calculated_parameter, parameter):
        "evaluates data based on evaluation excel"
        result_keys = ["total_camera_samples", "camera_missing_samples_count", "passed_samples", "failed_samples"]
        evaluation_result = {}

        for i in result_keys:
            evaluation_result[i] = 0

        # split_data = self.splitOnRangeByDx("type", calculated_type, deepcopy(self.evaluation_database["type"]))
        split_data = calculated_parameter

        cam = calculated_parameter["cam"]

        evaluation_result["total_camera_samples"] = len(cam[0])
        evaluation_result["camera_missing_samples_count"] = self.validateTimestamp(cam[0], self.camera_tolerance_time)

        for i in range(len(cam[0])):
            camera_value = cam[1][i]

            result = self.compareValue(camera_value, self.evaluation_database[parameter]["value"])
            if result:
                evaluation_result["passed_samples"] += 1
            else:
                evaluation_result["failed_samples"] += 1

        temp = {}
        if (evaluation_result["total_camera_samples"]):
            expected = self.evaluation_database[parameter]["required_verdict_per"]
            actual = (evaluation_result["passed_samples"] / evaluation_result["total_camera_samples"]) * 100
            temp["expected"] = expected
            temp["actual"] = actual
            temp["verdict"] = "PASS" if actual >= expected else "FAIL"
        else:
            temp["expected"] = self.evaluation_database[parameter]["required_verdict_per"]
            temp["actual"] = "-"
            temp["verdict"] = "FAIL"
        evaluation_result["result"] = temp

        return evaluation_result






    def getVerdictExcel(self):
        result_columns = ["Parameter_Name",	"Detection_Range", "Total_Camera_Samples", "Pass_Samples", "Fail_Samples",
                          "Missing/No_Data_Available_Samples",	"Expected [%]",	"Measured [%]",	"Verdict"]
        result_list = []

        for parameter in self.parameters_order:
            parameter = parameter.lower().replace(" ","")
            if parameter not in self.evaluation_results.keys() or not(self.evaluation_results[parameter]):
                continue
            key = parameter
            value = self.evaluation_results[key]
            row = {}
            if len(value)==3:
                for range, data in value.items():
                    row={}
                    row["Parameter_Name"] = key.capitalize()
                    row["Detection_Range"] = range.upper()
                    row["Total_Camera_Samples"] = data["total_camera_gt_pairs"]
                    row["Pass_Samples"] = data["passed_samples"]
                    row["Fail_Samples"] = data["failed_samples"]
                    row["Missing/No_Data_Available_Samples"] = data["camera_missing_samples_count"]
                    row["Expected [%]"] = data["result"]["expected"]
                    try:
                        row["Measured [%]"] = round(float(data["result"]["actual"]),2)
                    except:
                        row["Measured [%]"] = data["result"]["actual"]
                    row["Verdict"] = data["result"]["verdict"]
                    result_list.append(row)
            else:
                row["Parameter_Name"] = key.capitalize()
                row["Total_Camera_Samples"] = value["total_camera_samples"]
                row["Pass_Samples"] = value["passed_samples"]
                row["Fail_Samples"] = value["failed_samples"]
                row["Missing/No_Data_Available_Samples"] = value["camera_missing_samples_count"]
                row["Expected [%]"] = value["result"]["expected"]
                try:
                    row["Measured [%]"] = round(float(value["result"]["actual"]),2)
                except:
                    row["Measured [%]"] = value["result"]["actual"]
                row["Verdict"] = value["result"]["verdict"]
                result_list.append(row)


        df = pd.DataFrame(result_list, columns=result_columns)
        df.to_excel(self.output_file, index=False)

        wb = load_workbook(self.output_file)

        return wb
        #wb.save(self.output_file)

