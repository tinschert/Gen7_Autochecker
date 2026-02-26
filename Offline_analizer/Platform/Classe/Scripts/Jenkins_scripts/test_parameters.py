# -*- coding: utf-8 -*-
# @file test_parameters.py
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


import re
import codecs
import time
import datetime as dt
from bs4 import BeautifulSoup


class TestParameters:

    def __init__(self, path_to_indexhtml):
    """
    Takes one parameter --> the path to the copied report
            and determines the tc name, rqm ids, general tc status

    Args:

    Returns:

    """
        self.tc_parameters = {"tc_name": "",
                              "tc_sub_cases": {},
                              "tc_state": "",
                              "mf4_name": ""}
        self.path_to_indexhtml = path_to_indexhtml
        self.htmlHandle = open(self.path_to_indexhtml, 'r')
        self.report_soup = BeautifulSoup(self.htmlHandle, "html.parser")

    def close_handle(self):
        """ """
        self.htmlHandle.close()

    def get_test_name_if_obsolete(self):
        """ """
        name = ''
        file = codecs.open(self.path_to_indexhtml, "r", "utf-8")
        name_mask = re.compile(r'-v,\s\w+?.*?.yml')
        for line in file.readlines():
            if len(name_mask.findall(line)) != 0:
                for match in name_mask.findall(line):
                    name = re.sub(r'tc_name==', '', match)
                    name = re.sub(r';', '', name)
                almost_there = name.split('/TC_')[-1]
                tc_name = "TC_" + almost_there.split('.yml')[0]
                self.tc_parameters["tc_name"] = tc_name
            else:
                date_now = str(dt.date.today()) + "_"
                time_now = str(time.strftime("%Hh%Mm%Ss"))
                tc_name = 'obsolete_' + date_now + time_now
                self.tc_parameters["tc_name"] = tc_name

    def invalidate_tc(self):
        """ """
        self.get_test_name_if_obsolete()
        self.tc_parameters["tc_sub_cases"]["XXXXXX"] = "NotValid"
        self.tc_parameters["tc_state"] = "Skipped"
        self.tc_parameters["mf4_name"] = "NotValid"

    def get_tc_name_and_mf4(self):
        """ """
        tc_name = self.report_soup.find(class_="col-name")
        if tc_name is not None:
            tc_name = tc_name.getText().split("/")[-1]
            tc_name = tc_name.split("::")[0]
            tc_name = re.sub("\\.yml", "", tc_name)
            self.tc_parameters["tc_name"] = tc_name
            self.get_mf4_id()
        else:
            self.invalidate_tc()

    def get_mf4_id(self):
        """ """
        self.tc_parameters["mf4_name"] = "TC_" + self.tc_parameters["tc_name"].split("_")[1] + ".mf4"

    def get_tc_sub_rqm_ids(self):
        """ """
        sub_cases = self.report_soup.find_all(class_="col-name")
        sub_statuses = self.report_soup.find_all(class_="col-result")
        for case, status in zip(sub_cases, sub_statuses):
            i_case = case.getText().split("::")[-1]
            try:
                i_case = int(i_case)
            except ValueError:
                i_case = case.getText().split("::")[-2]
            status = status.getText()
            self.tc_parameters["tc_sub_cases"][i_case] = status

    def determine_tc_state(self):
        """ """
        fail_flag = 0
        pass_flag = 0
        for k, v in self.tc_parameters["tc_sub_cases"].items():
            if v == "NotValid":
                break
            else:
                if "Skipped" == v or "Error" == v:
                    self.tc_parameters["tc_state"] = "Skipped"
                    break
                elif "Failed" == v:
                    fail_flag += 1
                elif "Passed" == v:
                    pass_flag += 1
        if fail_flag > 0:
            self.tc_parameters["tc_state"] = "Failed"
        elif fail_flag == 0 and pass_flag > 0:
            self.tc_parameters["tc_state"] = "Passed"
        elif fail_flag == 0 and pass_flag == 0:
            self.tc_parameters["tc_state"] = "Skipped"

    def get_tc_params(self):
        """ """
        self.get_tc_name_and_mf4()
        self.get_tc_sub_rqm_ids()
        self.determine_tc_state()
        self.close_handle()
        return self.tc_parameters

#
# tparams = TestParameters(why_da_f)
# print(tparams.get_tc_params())
