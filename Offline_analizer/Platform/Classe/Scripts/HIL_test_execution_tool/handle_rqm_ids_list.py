# -*- coding: utf-8 -*-
# @file handle_rqm_ids_list.py
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


class HandleRQMIDs:
    """ """

    def __init__(self, pathtoalist, connection_object, **bench_info):
        self.inputlist_path = pathtoalist
        self.connection = connection_object
        self.rqm_ids = self.populate_rqm_ids_list(self.inputlist_path)
        self.list_with_found_tc_paths = []
        self.yaml_paths_with_duplicate_tc_ids = {}
        self.oem_tag_problems = {'tcs_with_no_oem_tags': [], 'tcs_with_more_than_one_oem_tag': []}
        self.ids_not_found = []
        self.tcs_with_multiple_oem_tags = []

        self.repo_path = bench_info['test_repo_path']
        self.tc_work_folder_name = bench_info['curr_tc_work_fold']
        self.product_variant = bench_info['product_variant']
        self.tc_work_folder_path = self.get_tc_work_folder_path()
        self.host = bench_info['hostname']

        if self.rqm_ids is not None:
            if len(self.rqm_ids) == 0:
                print(f"The given list is empty.")
        elif self.rqm_ids is None:
            print(f"This file does not exist or no file open ....")
        else:
            print(f"List attribute populated.")

        self.sort_input_ids_list()

    def sort_input_ids_list(self):
        """ """
        self.rqm_ids = sorted(list(set(self.rqm_ids)))
        # print(f"input list with removed duplicets >>> {self.rqm_ids}")

    def access_raw_oem_tags_list(self,list_of_raw_oem_tags):
        """
        

        Args:
          list_of_raw_oem_tags: 

        Returns:

        """
        to_trim = re.compile(r'\d+:\s+OEM:\s+')
        if list_of_raw_oem_tags is not None and len(list_of_raw_oem_tags) == 1:
            list_of_raw_oem_tags[-1] = list_of_raw_oem_tags[-1].decode().strip()
            # print(f"EOM tags after decode and trim >>> {list_of_raw_oem_tags[-1]}")
            if len(to_trim.findall(list_of_raw_oem_tags[-1])) != 0:
                tags = re.sub(to_trim, "", list_of_raw_oem_tags[-1])
                # print(f"OEM Tags??? >>> {tags}")
                if tags == '':
                    # print(f"return False. There is an OEM tag, but there are no variants...")
                    return False
                else:
                    tagslist = tags.split(',')
                    for tag in tagslist:
                        if tag in self.product_variant:
                            # print(f"return True. There is an OEM tag and it is >>> {tag}")
                            return True

    def get_raw_oem_tag_values(self, tc_path):
        """
        

        Args:
          tc_path: 

        Returns:

        """
        grep_oem = "grep --include=\\*.yml -rnw '" + tc_path + "' -e 'OEM:'"
        # print(f"grep OEM tag command >>> {grep_oem}")
        output = self.connection.execute(grep_oem)
        # print(f"Grep OEM tag output >>> {output}")
        if len(output) == 0:
            # print(f"No OEM tag found here >>> {tc_path}")
            self.oem_tag_problems['tcs_with_no_oem_tags'].append(tc_path)
            return False
        elif len(output) > 1:
            # print(f"More than one EOM tag is found.")
            self.oem_tag_problems['tcs_with_more_than_one_oem_tag'].append(tc_path)
            return False
        elif len(output) == 1:
            # print(f"Correct. OEM tag found for {tc_path}")
            return self.access_raw_oem_tags_list(output)

    @staticmethod
    def filter_tc_rqm_id(byte_array):
        """
        

        Args:
          byte_array: 

        Returns:

        """
        name_trim_end = re.compile(r':\d+:')
        decoded = byte_array.decode()
        templist = decoded.split("  ")
        # print(f"Filter tc name func >>> decoded and splitted line to list >>> {templist}")
        if len(name_trim_end.findall(templist[0])) != 0:
            tc_name = re.sub(name_trim_end, "", templist[0])
            # print(f"Filter tc name func >>> tc name is >>> {tc_name}")
            return tc_name
        else:
            # print(f"No name could be extracted .. sorry.")
            return None

    @staticmethod
    def filter_tc_name(byte_array):
        """
        

        Args:
          byte_array: 

        Returns:

        """
        name_trim_end = re.compile(r':\d+:')
        decoded = byte_array.decode()
        templist = decoded.split("  ")
        # print(f"Filter tc name func >>> decoded and splitted line to list >>> {templist}")
        if len(name_trim_end.findall(templist[0])) != 0:
            tc_name = re.sub(name_trim_end, "", templist[0])
            return tc_name
        else:
            return None

    def grep_tc_id(self, tc_path):  # grep -rnw '/home/sya9lr/GIT_Workspace/PSA_Testing/ods_cloe_tests/cloe_tests/tcs/aeb/XIL_Tests/2510/TC_1829985_AEx_EgoTurnTgtCross_Pedestrian_Left_P2P__C_HmiDisabledForwardSafetyFunctions.yml' -e 'tc._ID'
        list_with_found_id_tags = []
        command = "grep -rnw '" + tc_path + "' -e 'tc[1-999]_ID:'"
        # print(f"grep tc_ID tag command >>> {command}")
        output = self.connection.execute(command)
        # print(f"Grep tc_ID tag output >>> {output}")
        if len(output) == 1:
        """
        

        Args:
          tc_path):  # grep -rnw '/home/sya9lr/GIT_Workspace/PSA_Testing/ods_cloe_tests/cloe_tests/tcs/aeb/XIL_Tests/2510/TC_1829985_AEx_EgoTurnTgtCross_Pedestrian_Left_P2P__C_HmiDisabledForwardSafetyFunctions.yml' -e 'tc._ID'list_with_found_id_tags:  (Default value = []command = "grep -rnw '" + tc_path + "' -e 'tc[1-999]_ID:'"# print(f"grep tc_ID tag command >>> {command}")output = self.connection.execute(command)# print(f"Grep tc_ID tag output >>> {output}")if len(output)

        Returns:

        """
            if "No such file or directory" in output[-1].decode():
                # print(f"Nothing with the name '{tc_path}', is found. No tags are found.")
                return None
            else:
                for rqm_id in output:
                    rqm_id = rqm_id.decode().strip()
                    list_with_found_id_tags.append(rqm_id)
                    # print(f"Grep tc id >>> Only one ID tag found >>> {id}")
                return list_with_found_id_tags
        elif (len(output) >= 1) & ("No such file or directory" not in output[-1].decode()):
            for raw_id in output:
                raw_id = raw_id.decode().strip()
                list_with_found_id_tags.append(raw_id)
                # print(f"grep tc id >>> raw id is >>> {raw_id}")
            return list_with_found_id_tags

    def grep_tc_name(self, rqm_id, option=''):  # grep3 = "grep --include=\*.yml -rnw '/home/sya9lr/GIT_Workspace/PSA_Testing/ods_cloe_tests/cloe_tests/tcs/aeb/XIL_Tests' -e 'tc._ID: 1829985'"
        command = ''
        if option == 'tc_ID':
        """
        

        Args:
          rqm_id: 
          option:  (Default value = '')

        Returns:

        """
            command = "grep --include=\\*.yml -rnw '" + self.tc_work_folder_path + "' -e 'tc[1-99]_ID: " + rqm_id + "'"
        elif option == 'main_tag':
            command = "grep --include=\\*.yml -rnw '" + self.tc_work_folder_path + "' -e 'tc_id: " + rqm_id + "'"
        elif option == 'id':
            command = "grep --include=\\*.yml -rnw '" + self.tc_work_folder_path + "' -e '.*id: " + rqm_id + "'"
        output = self.connection.execute(command)
        if len(output) == 0:
            return None
        elif len(output) >= 1:
            return output

    def get_tc_work_folder_path(self):
        """ """
        k_word1 = 'obsolete'
        k_word2 = 'retired'
        command = "find  " + self.repo_path + " -type d -name '" + self.tc_work_folder_name + "'"
        output = self.connection.execute(command)
        # print(f"Output from get_tc_work_folder_path >>> {output}")
        if len(output) == 0:
            return None
        elif len(output) > 1:
            for i, path in enumerate(output):
                d_path = path.strip().decode()
                if re.search(k_word1.casefold(), d_path.casefold()) or re.search(k_word2.casefold(), d_path.casefold()):
                    output.pop(i)
            return output[-1].strip().decode()
        elif len(output) == 1:
            return output[-1].strip().decode()

    @staticmethod
    def populate_rqm_ids_list(path):
        """
        

        Args:
          path: 

        Returns:

        """
        temp_list = []
        try:
            with open(path, 'r') as inputlist:
                for id in inputlist:
                    if id != '' and id != '\n':
                        id = id.strip()
                        temp_list.append(id)
            return temp_list
        except FileNotFoundError:
            return None

    def assess_rqm_id_and_result(self, response_list, rqm_id):
        """
        

        Args:
          response_list: 
          rqm_id: 

        Returns:

        """
        temp_duped_tcs_list = []
        if response_list is not None and len(response_list) == 1:  # meaning only one test case is found with matching id is found
            for item in response_list:
                # print(15 * "__" + "correct...only one test is found." + 15 * "__")
                tc_name_and_path = self.filter_tc_name(item)
                is_oem = self.get_raw_oem_tag_values(tc_name_and_path)
                if is_oem is False:
                    pass
                elif is_oem:
                    self.list_with_found_tc_paths.append(tc_name_and_path)
        elif response_list is not None and len(response_list) > 1:  # meaning one tc_ID tag is in multiple test cases
            for duplicate in response_list:
                temp_name = self.filter_tc_name(duplicate)
                temp_duped_tcs_list.append(temp_name)
            duped_tcs_list = list(set(temp_duped_tcs_list))  # removing the duplicate paths
            self.yaml_paths_with_duplicate_tc_ids[rqm_id] = duped_tcs_list
        elif response_list is None or len(response_list) == 0:
            self.ids_not_found.append(rqm_id)

    def analyze_input_rqm_id_list(self):
        """ """
        for rqm_id in self.rqm_ids:
            response = self.grep_tc_name(rqm_id, 'main_tag')
            if response is not None and len(response) >= 1:
                self.assess_rqm_id_and_result(response, rqm_id)
            elif response is None or len(response) == 0:
                alt_response = self.grep_tc_name(rqm_id, 'tc_ID')
                if alt_response is not None and len(alt_response) >= 1:
                    self.assess_rqm_id_and_result(alt_response, rqm_id)
                elif response is None or len(alt_response) == 0:
                    third_response = self.grep_tc_name(rqm_id, 'id')
                    self.assess_rqm_id_and_result(third_response, rqm_id)
        if len(self.list_with_found_tc_paths) > 0:
            output_with_added_files = '_added_list.txt'
            self.list_with_found_tc_paths = list(set(self.list_with_found_tc_paths))
            with open(output_with_added_files, 'w') as out_f:
                for id in self.list_with_found_tc_paths:
                    out_f.write(id + '\n')
        return sorted(self.list_with_found_tc_paths)

