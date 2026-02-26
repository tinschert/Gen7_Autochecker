# -*- coding: utf-8 -*-
# @file Test_Execution_Tool_HIL.py
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


import ctypes
import random
import re
import json
from multiprocessing import Value, Array, Process, freeze_support
from socket import gaierror
from threading import Thread
import os
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk
from paramiko import SSHClient, AutoAddPolicy, SSHException, AuthenticationException
import time
import datetime as dt
try:
    from sensor_set_config import ConfigSensorSet
    from handle_rqm_ids_list import HandleRQMIDs
    import ssh_client
    import execute_client
    import report_handler
except SSHException as exception:
    messagebox.showwarning('warning', f'Error: {exception}')
    sys.exit()

testrun_alive = False
bench_conn_dict = {}
should_the_gui_start = "No"
gui_pid = os.getpid()


class BenchConnectAndSearch:
    """ """

    initial_list = []
    filtered_list = []
    # path = "/home/sya9lr/OD_PSA_Testing_HiL/ods_cloe_tests"
    mf4_log_keywrd = 'measurementsmountfromcanoesystemuser'
    evald_report_keywrd = 'evald_report'

    def __init__(self):
        # self.repo_name = "OD_PSA_Testing_HIL"
        self.tc_name_mask = re.compile(r'TC_\d*_\w*.yml')
        self.bench_connection = SSHClient()
        self.bench_connection.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self, **benchconninfo):
        """
        

        Args:
          **benchconninfo: 

        Returns:

        """
        try:
            self.bench_connection.connect(**benchconninfo, look_for_keys=False, allow_agent=False)
            return self.bench_connection
        except gaierror:
            return gaierror
        except AuthenticationException:
            return AuthenticationException
        except TimeoutError:
            return TimeoutError

    def check_connection(self):
        """ """
        if self.bench_connection.get_transport().is_active():
            # print(f"Connection is alive and good!")
            return True
        elif not self.bench_connection.get_transport().is_active():
            return False

    def close_connection(self):
        """ """
        if self.bench_connection is not None:
            try:
                if self.bench_connection.get_transport().is_active():
                    print(f"Closing connection!")
                    self.bench_connection.close()
            except AttributeError:
                print(f"There is no active connection to disconnect.")

    @staticmethod
    def go_back(path):
        """
        

        Args:
          path: 

        Returns:

        """
        temp = list(path)
        for x in range(len(temp) - 1, 0, -1):
            if temp[-1] != '\\' and temp[-1] != '/':
                pass
            elif x != -1 and (temp[x] == '\\' or temp[x] == '/'):
                temp.pop(x)
                break
            temp.pop(x)
        repo_path_after = ''.join(map(str, temp))
        return repo_path_after

    def list_results_from_search(self, itemtobefound, wheretolook, depth='All folders', healthcheck='No'):
        """
        

        Args:
          itemtobefound: 
          wheretolook: 
          depth:  (Default value = 'All folders')
          healthcheck:  (Default value = 'No')

        Returns:

        """
        search_item = itemtobefound
        path = wheretolook
        searchcommand = ''
        if depth == 'This folder':
            if healthcheck == 'No':
                searchcommand = 'find ' + path + ' -maxdepth 1 -name ' + search_item + '\n'
            elif healthcheck == 'Yes':
                searchcommand = 'find ' + path + ' -maxdepth 1 -wholename ' + search_item + '\n'
        elif depth == 'All folders':
            searchcommand = 'find ' + path + ' -depth -name ' + search_item + '\n'
        stdin, stdout, stderr = self.bench_connection.exec_command(searchcommand)
        output_list = stdout.read().decode()
        output_list = output_list.split('\n')
        if len(output_list) > 0:
            for item in output_list:
                if item == '':
                    output_list.remove(item)
        return output_list

    def find_evald_and_mf4log_folders(self, path):
        """
        

        Args:
          path: 

        Returns:

        """
        # here we need to search for 'mf4_log_keywrd' and 'evald_report_keywrd' folders in the path given as an arg
        # mf4_log:
        repo_path = path
        paths_dict = {'linux_mf4_path': '', 'linux_evald_report_path': ''}
        list_results_mf4 = self.list_results_from_search(self.mf4_log_keywrd, repo_path, 'This folder')
        if len(list_results_mf4) == 1:
            # if its found, assign the path to the paths_dict key for mf4 log
            paths_dict['linux_mf4_path'] = list_results_mf4[-1]
        elif len(list_results_mf4) == 0:
            # if its not found, 'return a not found mf4 log msg
            paths_dict['linux_mf4_path'] = 'No mf4 log folder found! Maybe run "make setup-after-reboot" on the linux host?'
        # evald report:
        list_results_evaldreport = self.list_results_from_search(self.evald_report_keywrd, repo_path, 'This folder')
        # if its found, assign the path to the paths_dict key for evald-report folder
        if len(list_results_evaldreport) == 1:
            paths_dict['linux_evald_report_path'] = list_results_evaldreport[-1]
        elif len(list_results_evaldreport) == 0:
            # if its not found, 'return a not found mf4 log msg'
            paths_dict['linux_evald_report_path'] = "No evald report folder found."
        return paths_dict

    def search_for_repo_paths(self, repokeyword, **conn_info):
        """
        

        Args:
          repokeyword: 
          **conn_info: 

        Returns:

        """
        git_keyword = '.gitattributes'
        searchcommand = 'find /' + ' -depth -name "' + git_keyword + '"\n'

        filtered_output = []

        stdin, stdout, stderr = self.bench_connection.exec_command(searchcommand)
        output = stdout.read().decode()
        output = output.split('\n')

        for path in output:
            if path != '':
                if git_keyword in path:  # remove the git_keyword from the path to get the repo path:
                    path = path.split(git_keyword)[0]
                    print(f'repo path?: {path}')
                    search_results = self.list_results_from_search(repokeyword, path)
                    if len(search_results) == 1:
                        filtered_output.append(search_results[-1])

        return filtered_output

    def search_for_variants_from_repopath(self, repopath):
        """
        

        Args:
          repopath: 

        Returns:

        """
        variants_folder_path = []
        variant_content_raw = []
        if repopath != '':
            varsearchcommand = 'find ' + repopath + ' ' + '-depth -name conf\n'

            stdin, stdout, stderr = self.bench_connection.exec_command(varsearchcommand)
            output = stdout.read().decode()
            output = output.split('\n')

            for row in output:
                if row != '':
                    variants_folder_path.append(row)
            time.sleep(1)

            if len(variants_folder_path) > 0:
                ls_command = 'ls ' + variants_folder_path[0]
                stdin, stdout, stderr = self.bench_connection.exec_command(ls_command)
                output = stdout.read().decode()
                output = output.split('\n')
                for row in output:
                    if row != '':
                        variant_content_raw.append(row)
                variant_content_raw.append(variants_folder_path)

            variant_content_raw = self.filter_raw_variants_list(variant_content_raw)  # filter the raw 'variant' list
            return variant_content_raw  # return a list with all of the items in 'variant' folder from the repo

        elif repopath == '':
            return variant_content_raw

    def get_tc_name_from_line(self, line_from_file):
        """
        

        Args:
          line_from_file: 

        Returns:

        """
        if len(self.tc_name_mask.findall(line_from_file)) != 0:
            for name_match in self.tc_name_mask.findall(line_from_file):
                tc_name = name_match
                # print(f"tc_id match is : {tc_name}")
                return tc_name
        elif len(self.tc_name_mask.findall(line_from_file)) == 0:
            # print("match NOT found")
            tc_name = ""
            return tc_name

    def read_txt_and_init_list(self, listpath):
        """
        

        Args:
          listpath: 

        Returns:

        """
        initial_list = []
        try:
            with open(listpath, 'r') as tclist:
                linesfromfile = tclist.readlines()
                if len(linesfromfile) != 0:
                    for line in linesfromfile:
                        if line != "\n":
                            tc_name = self.get_tc_name_from_line(line.strip())
                            if tc_name != "" and ".yml" in tc_name:
                                # if tc_name != "" and tc_name.endswith(".yml"):
                                initial_list.append(tc_name)
        except FileNotFoundError as err:
            # print(f"File not found! Err is >>> {err}")
            return initial_list
        # print(f"init_list = {initial_list}")
        return initial_list

    @staticmethod
    def extract_tc_by_tcfolder_keyword(listoffounditems, **keyword):
        """
        

        Args:
          listoffounditems: 
          **keyword: 

        Returns:

        """
        finallist = []
        for item in listoffounditems:
            if keyword['curr_tc_work_fold'] in item:
                finallist.append(item)
        return finallist

    @staticmethod
    def filter_init_list(listtobefiltered, **keyword):
        """
        

        Args:
          listtobefiltered: 
          **keyword: 

        Returns:

        """
        filtered_list = []
        try:
            assert len(listtobefiltered) > 0, "THE LIST, GIVEN AS AN IMPUT IS MOST LIKELY EMPTY"
            [filtered_list.append(listitem) for listitem in listtobefiltered if listitem not in filtered_list]
            # for item in filtered_list:
            #     print(f"Filtered list item?: {item}")
            return sorted(filtered_list)
        except AssertionError:
            print(f"The list is most likely empty")
            return filtered_list

    @staticmethod
    def filter_raw_variants_list(variant_list_raw):
        """
        

        Args:
          variant_list_raw: 

        Returns:

        """
        filtered_variants_list = []

        for variant in variant_list_raw:
            if 'evald_config_develop_' in variant:
                filtered_variants_list.append(variant)
            elif type(variant) is list:
                # print(f"this item is probably the path... item == {variant}")
                filtered_variants_list.append(variant)

        return filtered_variants_list


class LoginAndConfig:

    """
    This class is created for logging in to the host linux machine
    and parse the needed information to the GUI that is running the tests.
    The info consists of host info, username, password,
    (repository, report, mf4log) paths and product variant

    Args:

    Returns:

    """

    healthcheck_list = []
    disconnect_btn_state = 'Not pressed'
    config_loaded = False

    empty_fields = []
    output_dict = {'hostname': '',
                   'username': '',
                   'password': '',
                   'test_repo_keyword': '',
                   'local_report_output_path': '',
                   'test_repo_path': '',
                   'curr_tc_work_fold': 'XIL_Tests',
                   'linux_evald_reports_path': '',
                   'linux_mf4_log_path': '',
                   'product_variant': '',
                   'variants_path': ''}
    config_dict = {}
    config_dict.update(output_dict)

    def __init__(self, **host_user_pass):

        self.loginAndConfigWin = tkinter.Tk()
        self.loginAndConfigWin.title("ADAS HIL test execution tool")
        self.loginAndConfigWin.geometry('720x510+40+100')
        self.loginAndConfigWin['padx'] = 8

        self.loginAndConfigWin.columnconfigure(0, weight=1)
        self.loginAndConfigWin.columnconfigure(1, weight=1)
        self.loginAndConfigWin.columnconfigure(2, weight=1)

        self.loginAndConfigWin.rowconfigure(0, weight=1)
        self.loginAndConfigWin.rowconfigure(1, weight=1)
        self.loginAndConfigWin.rowconfigure(2, weight=1)
        self.loginAndConfigWin.rowconfigure(3, weight=1)
        self.loginAndConfigWin.rowconfigure(4, weight=1)
        self.loginAndConfigWin.rowconfigure(5, weight=1)
        self.loginAndConfigWin.rowconfigure(6, weight=1)

        # #####################  SSH frame section ################################################
        # Create SSH Label frame
        self.ssh_frame = tkinter.LabelFrame(self.loginAndConfigWin, text='Linux Cloe SSH connection')
        self.ssh_frame.grid(row=0, column=0, sticky='we', columnspan=3, rowspan=1, ipady=1)

        # Create SSH Label inside SSH Label frame
        self.ssh_host_label = tkinter.Label(self.ssh_frame, text="SSH Host")
        self.ssh_host_label.grid(row=0, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of SSH Host
        self.ssh_host_var = tkinter.StringVar()
        self.ssh_host_var.set('ABTZ0ODS.LR.DE.BOSCH.COM')
        self.ssh_host_entry = tkinter.Entry(self.ssh_frame, textvariable=self.ssh_host_var, width=25)
        self.ssh_host_entry.grid(row=0, column=1, sticky='w', columnspan=2, rowspan=1)

        # Create Username Label inside SSH Label frame
        self.ssh_username = tkinter.Label(self.ssh_frame, text="Username")
        self.ssh_username.grid(row=1, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of Username
        self.ssh_user_var = tkinter.StringVar()
        self.ssh_user_var.set('sya9lr')
        self.ssh_user_entry = tkinter.Entry(self.ssh_frame, textvariable=self.ssh_user_var, width=25)
        self.ssh_user_entry.grid(row=1, column=1, sticky='w', columnspan=2, rowspan=1)

        # Create Password Label inside SSH Label frame
        self.ssh_password = tkinter.Label(self.ssh_frame, text="Password")
        self.ssh_password.grid(row=2, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of Password
        self.ssh_pass_var = tkinter.StringVar()
        self.ssh_pass_var.set('')  # Adassystestereet#1
        self.ssh_pass_entry = tkinter.Entry(self.ssh_frame, textvariable=self.ssh_pass_var, show="*", width=25)
        self.ssh_pass_entry.grid(row=2, column=1, sticky='w', columnspan=2, rowspan=1)

        # Create Connect button
        self.button_connect = tkinter.ttk.Button(self.ssh_frame, text='Connect', command=self.attempt_connection_to_host)
        self.button_connect.grid(row=3, column=0, sticky='w', ipady=2)

        # Create Disconnect button
        self.button_disconnect = tkinter.ttk.Button(self.ssh_frame, text='Disconnect', command=self.disconnect)
        self.button_disconnect.grid(row=3, column=1, sticky='w', ipady=2)

        # #####################  USER SPECIFIC INFO ################################################
        # Create user specific info
        self.user_specific_info = tkinter.LabelFrame(self.loginAndConfigWin, text='Input needed from user')
        self.user_specific_info.grid(row=1, column=0, sticky='wne', columnspan=3, rowspan=1, ipady=3)

        # Create repo keyword Label inside USER SPECIFIC INFO Label frame
        self.repo_keyword = tkinter.Label(self.user_specific_info, text="Test repo keyword")
        self.repo_keyword.grid(row=0, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of repo keyword
        self.repo_keyword_var = tkinter.StringVar()
        self.repo_keyword_var.set('cloe_tests')
        self.repo_keyword_entry = tkinter.Entry(self.user_specific_info, textvariable=self.repo_keyword_var, width=25)
        self.repo_keyword_entry.grid(row=0, column=1, sticky='w', columnspan=2, rowspan=1)

        # Create local report folder path Label inside SSH Label frame
        self.local_report_folderpath = tkinter.Label(self.user_specific_info, text="Local windows report path")
        self.local_report_folderpath.grid(row=1, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of local report folder path
        self.local_report_folderpath = tkinter.StringVar()
        self.local_report_folderpath_entry = tkinter.Entry(self.user_specific_info, textvariable=self.local_report_folderpath, width=25)
        self.local_report_folderpath_entry.grid(row=1, column=1, sticky='w', columnspan=2, rowspan=1)

        # Create local report folder path Label inside SSH Label frame
        self.tcs_from_list_lbl = tkinter.Label(self.user_specific_info, text="TC folder name")
        self.tcs_from_list_lbl.grid(row=2, column=0, columnspan=1, rowspan=1)

        # Create Add TCs from list entry box and variable for the input of local report folder path
        self.tcs_from_list_var = tkinter.StringVar()
        self.tcs_from_list_entry = tkinter.Entry(self.user_specific_info, textvariable=self.tcs_from_list_var, width=25)
        self.tcs_from_list_entry.grid(row=2, column=1, sticky='w', columnspan=2, rowspan=1)

        # #####################  AUTO-FILLED INFO AFTER USER SPECIFIC INFO ################################################
        # Create user specific info
        self.auto_filled_info = tkinter.LabelFrame(self.loginAndConfigWin, text='Auto-filled info after login')
        self.auto_filled_info.grid(row=2, column=0, sticky='wne', columnspan=3, rowspan=1, ipady=5)

        # Create repo path Label inside AUTO-FILLED INFO Label frame
        self.repo_path_lbl = tkinter.Label(self.auto_filled_info, text="Test repo path")
        self.repo_path_lbl.grid(row=0, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of repo path
        self.choices_repo_path = ['',
                                  '',
                                  '']
        self.repo_path_var = tkinter.StringVar()
        # self.repo_path_var.trace('w', callback=self.on_repo_path_selection_change)
        self.repo_path_var.set('Please, establish connection to a host.')
        self.repo_path_entry = tkinter.OptionMenu(self.auto_filled_info, self.repo_path_var, self.choices_repo_path[0], *self.choices_repo_path)
        self.repo_path_entry.grid(row=0, column=1, sticky='ws', columnspan=2, rowspan=1)
        self.repo_path_entry.config(width=80)

        # Create product variant Label inside SSH Label frame
        self.choices_product_var = ['',
                                    '',
                                    '']
        self.product_var_lbl = tkinter.Label(self.auto_filled_info, text="Product variant")
        self.product_var_lbl.grid(row=1, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of product variant
        self.product_var = tkinter.StringVar()
        self.product_var.set('Please, establish connection to a host.')
        self.product_var_entry = tkinter.OptionMenu(self.auto_filled_info, self.product_var, self.choices_product_var[0], *self.choices_product_var)
        self.product_var_entry.grid(row=1, column=1, sticky='ws', columnspan=2, rowspan=1)
        self.product_var_entry.config(width=80)

        # Create linux report folder path Label inside SSH Label frame
        self.linux_folderpath_lbl = tkinter.Label(self.auto_filled_info, text="Linux evalD report path")
        self.linux_folderpath_lbl.grid(row=2, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of linux report folder
        self.linux_report_folderpath = tkinter.StringVar()
        self.linux_report_folderpath.set('Will be auto-filled after selecting a test repo path...')
        self.linux_report_folderpath_entry = tkinter.Entry(self.auto_filled_info, textvariable=self.linux_report_folderpath, width=80)
        self.linux_report_folderpath_entry.grid(row=2, column=1, sticky='ws', columnspan=2, rowspan=1)

        # Create linux mf4 log path Label inside SSH Label frame
        self.linux_mf4log_path_lbl = tkinter.Label(self.auto_filled_info, text="Linux mf4 log path")
        self.linux_mf4log_path_lbl.grid(row=3, column=0, columnspan=1, rowspan=1)

        # Create entry box and variable for the input of linux mf4 log path
        self.linux_mf4log_path = tkinter.StringVar()
        self.linux_mf4log_path.set('Will be auto-filled after selecting a test repo path...')
        self.linux_mf4log_path_entry = tkinter.Entry(self.auto_filled_info, textvariable=self.linux_mf4log_path, width=80)
        self.linux_mf4log_path_entry.grid(row=3, column=1, sticky='ws', columnspan=2, rowspan=1)

        # #####################  'ACTIONS' BUTTONS PART ################################################
        # Create 'ACTIONS' frame
        self.buttons_frame = tkinter.LabelFrame(self.loginAndConfigWin, text='ACTIONS')
        self.buttons_frame.grid(row=4, column=0, sticky='w', columnspan=2, rowspan=1)

        # Create load config button and put into 'ACTIONS' frame
        self.button_load_config = tkinter.ttk.Button(self.buttons_frame, text='LOAD CONFIG', command=self.load_config)
        self.button_load_config.grid(row=0, column=0, sticky='w', ipady=2)

        # Create 'load config' button and put into 'ACTIONS' frame
        self.button_start_gui = tkinter.ttk.Button(self.buttons_frame, text='START GUI', command=self.start_gui)
        self.button_start_gui.grid(row=0, column=1, sticky='wn', rowspan=2, ipady=20, padx=40, pady=5)

        # Create 'START GUI' button and put into 'ACTIONS' frame
        self.button_save_config = tkinter.ttk.Button(self.buttons_frame, text='SAVE CONF', command=self.save_config)
        self.button_save_config.grid(row=1, column=0, sticky='w', ipady=2, ipadx=5)

        # #####################  'CONFIGURE SENSOR SET' BUTTONS PART ################################################
        # Create 'SENSOR SET' frame
        self.sensor_set_frame = tkinter.LabelFrame(self.loginAndConfigWin, text='SENSORS')
        self.sensor_set_frame.grid(row=4, column=2, sticky='w', columnspan=1, rowspan=1, ipadx=25, pady=5)

        # Create a 'config sensor set' button and put into 'ACTIONS' frame
        self.button_sensor_set = tkinter.ttk.Button(self.sensor_set_frame, text='CONFIGURE\nSENSOR SET', command=self.configure_sensor_set)
        self.button_sensor_set.grid(row=0, column=0, sticky='w', rowspan=2, ipady=20, padx=5, pady=5)
        self.button_sensor_set['state'] = tkinter.DISABLED

        self.connect_to_linux = BenchConnectAndSearch()
        self.repo_path_var.trace('w', callback=self.on_repo_path_selection_change)
        self.product_var.trace('r', callback=self.sensor_set_button_state)

        #  OTHER VARIABLES
        # PASSPOPUP
        self.pass_popup = object

    def disconnect(self):
        """ """
        self.disconnect_btn_state = 'Pressed'
        self.connect_to_linux.close_connection()
        self.repo_path_var.set('Please, establish connection to a host.')
        self.product_var.set('Please, establish connection to a host.')
        self.linux_report_folderpath.set('Will be auto-filled after selecting a test repo path...')
        self.linux_mf4log_path.set('Will be auto-filled after selecting a test repo path...')
        self.button_sensor_set['state'] = tkinter.DISABLED

    def sensor_set_button_state(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        product = self.product_var.get()
        if 'Please, establish' in product or 'Choose a variant' in product or 'Variants' in product:
            self.button_sensor_set['state'] = tkinter.DISABLED
        elif 'evald' in product:
            self.button_sensor_set['state'] = tkinter.ACTIVE

    def configure_sensor_set(self):
        """ """
        # print(f"Call the SensorSet() class here...")
        self.output_dict['product_variant'] = self.product_var.get()
        # print(f"send dict to ConfigSensorSet class >>> {self.output_dict}")
        conn_info = self.get_bench_conn_info()
        linux_connection_obj = self.connect_to_linux.connect(**conn_info)
        cconfig = ConfigSensorSet(self.connect_to_linux, linux_connection_obj, **self.output_dict)
        cconfig()

    def password_popup(self):
        """ """
        pass_window = tkinter.Toplevel()
        pass_window.title("PASS ENTRY")
        pass_window.geometry('250x150+80+200')
        pass_window['padx'] = 8

        pass_window.columnconfigure(0, weight=1)
        pass_window.columnconfigure(1, weight=1)

        pass_window.rowconfigure(0, weight=1)
        pass_window.rowconfigure(1, weight=1)
        # Create a label
        label = Label(pass_window, text="Please enter the user's password")
        label.grid(row=0, column=0)
        # Create entry box for the pass
        pass_var = tkinter.StringVar()
        pass_var.set('')
        pass_entry = tkinter.Entry(pass_window, textvariable=pass_var, show="*", width=25)
        pass_entry.grid(row=1, column=0, sticky='w', rowspan=1)

        def getpass():
            """ """
            if pass_entry.get() != '':
                self.output_dict['password'] = pass_entry.get()
                self.ssh_pass_var.set(self.output_dict['password'])
                pass_window.destroy()
            elif pass_entry.get() == '':
                messagebox.showwarning('Empty password field', 'Password field is empty!')
        # Create 'accept' button
        button = Button(pass_window, text="Enter", command=getpass)
        button.grid(row=1, column=1)
        button.bind('<Return>', getpass)
        pass_window.grab_set()
        pass_window.wait_window(pass_window)

    def configuration_validity_check(self):
        """ """
        # pt1 - try to connect with the credentials
        self.healthcheck_list.clear()
        is_conn_valid = self.connect()
        if is_conn_valid == AuthenticationException or \
            is_conn_valid == gaierror or \
                is_conn_valid == TimeoutError:
            return is_conn_valid
        # pt2 - validate the paths with a search function
        for key, val in self.output_dict.items():
            if key == 'test_repo_path' or key == 'linux_evald_reports_path' or key == 'linux_mf4_log_path':
                res = self.connect_to_linux.list_results_from_search(val, val, depth='This folder', healthcheck='Yes')
                if len(res) == 0:
                    self.healthcheck_list.append(val)
        self.disconnect()
        if len(self.healthcheck_list) > 0:
            return False
        elif len(self.healthcheck_list) == 0:
            return True

    def load_config(self):
        """ """
        self.config_loaded = True
        # first load the config file
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a .JSON config file",
                                              filetypes=(("Json File", "*.json"),),)
        try:
            with open(filename, 'r') as config_file:
                data_from_conf = json.load(config_file)
            # print(f"DATA FROM LOADED FILE >>>>>>>>>>>> {data_from_conf}")
            self.output_dict = data_from_conf
            self.password_popup()
            self.set_entries_from_config()
            self.config_loaded = True
        except FileNotFoundError:
            print(f"No config file is selected...")
            self.config_loaded = False

    def save_config(self):
        """ """
        self.get_entries_info()
        temp_pass_var = self.output_dict['password']
        self.output_dict['password'] = ''
        filename = filedialog.asksaveasfilename(initialdir="/",
                                                title="Select a File",
                                                defaultextension=json,
                                                filetypes=(("JSON files", "*.json*"),))
        with open(filename, 'w') as config:
            json.dump(self.output_dict, config)
        self.output_dict['password'] = temp_pass_var

    def set_entries_from_config(self):
        """ """
        self.ssh_host_var.set(self.output_dict['hostname'])
        self.ssh_user_var.set(self.output_dict['username'])
        self.ssh_pass_var.set(self.output_dict['password'])
        self.repo_keyword_var.set(self.output_dict['test_repo_keyword'])
        self.local_report_folderpath.set(self.output_dict['local_report_output_path'])
        self.tcs_from_list_var.set(self.output_dict['curr_tc_work_fold'])
        self.repo_path_var.set(self.output_dict['test_repo_path'])
        self.product_var.set(self.output_dict['product_variant'])
        self.linux_report_folderpath.set(self.output_dict['linux_evald_reports_path'])
        self.linux_mf4log_path.set(self.output_dict['linux_mf4_log_path'])

    def stringvar_to_keyval(self, keyname, strvar_value):
        """
        

        Args:
          keyname: 
          strvar_value: 

        Returns:

        """
        self.output_dict[keyname] = strvar_value
        if self.output_dict[keyname] == '':
            self.empty_fields.append(keyname)
        if keyname == 'local_report_output_path' and self.output_dict[keyname] != '' and not self.output_dict[keyname].endswith('\\', -1):
            self.output_dict[keyname] = self.output_dict[keyname] + '\\'

    def get_entries_info(self):
        """ """
        self.stringvar_to_keyval('hostname', self.ssh_host_var.get())
        self.stringvar_to_keyval('username', self.ssh_user_var.get())
        self.stringvar_to_keyval('password', self.ssh_pass_var.get())
        self.stringvar_to_keyval('test_repo_keyword', self.repo_keyword_var.get())
        self.stringvar_to_keyval('local_report_output_path', self.local_report_folderpath.get())
        self.stringvar_to_keyval('test_repo_path', self.repo_path_var.get())
        self.stringvar_to_keyval('linux_evald_reports_path', self.linux_report_folderpath.get())
        self.stringvar_to_keyval('linux_mf4_log_path', self.linux_mf4log_path.get())
        self.stringvar_to_keyval('product_variant', self.product_var.get())
        self.stringvar_to_keyval('curr_tc_work_fold', self.tcs_from_list_var.get())

    def start_gui(self):
        """ """
        global bench_conn_dict, should_the_gui_start

        self.empty_fields.clear()
        self.get_entries_info()

        assert self.output_dict['test_repo_path'] != 'Please, establish connection to a host.', messagebox.showwarning('warning', f'No connection to a host?')
        assert self.output_dict['test_repo_path'] != 'Select a repository path', messagebox.showwarning('warning', f'Select a repo path please!')
        assert self.output_dict['product_variant'] != 'Variants...', messagebox.showwarning('warning', f'Select a variant please!')
        assert self.output_dict['local_report_output_path'] != '', messagebox.showwarning('warning', f'Local report folder path is empty!')
        assert '/' not in self.output_dict['local_report_output_path'], messagebox.showwarning('warning',
                                                                                               f'Local report folder path should be a windows path!')
        assert self.output_dict['curr_tc_work_fold'] != '', messagebox.showwarning('warning', f'TC folder name is empty.\n'
                                                                                              f'This info is needed for "add TCs from txt list" option.\n'
                                                                                              f'Its Important! By default you should put the folder in the test repository that contains your tests\n'
                                                                                              f'In XIL repo, this should be "XIL_Tests"')
        assert self.output_dict['test_repo_keyword'] != '', messagebox.showwarning('warning', f'Test repo keyword is empty! Better keep it as "cloe_tests"')
        if self.output_dict['linux_evald_reports_path'] == 'Not found...':
            messagebox.showinfo('Caution', f'Linux evalD report folder is not found.\n'
                                           f'Maybe you need to execute "setup-after-reboot" on the GUI')
        if self.output_dict['linux_mf4_log_path'] == 'Not found...':
            messagebox.showinfo('Caution', f'Linux evalD report folder is not found.\n'
                                           f'Maybe you need to execute "setup-first-time" on the GUI')
        assert len(self.empty_fields) == 0, messagebox.showwarning('warning', f'These fields: {self.empty_fields}\nAre empty!!! Please fill them and try again.')
        validity = self.configuration_validity_check()
        assert validity is not AuthenticationException, messagebox.showwarning('warning', f'Credentials error:\nWrong USER name or PASSWORD.')
        assert validity is not gaierror, messagebox.showwarning('warning', f'Credentials error:\nWrong HOST name or no internet connection...')
        assert validity is not TimeoutError, messagebox.showwarning('warning', f'Connection attempt timeout...')
        assert validity is True, messagebox.showwarning('warning', f'Paths validity checks: {self.healthcheck_list}\nThese paths are not valid.\nPlease reconnect and select valid ones.')
        bench_conn_dict.update(self.output_dict)
        self.loginAndConfigWin.destroy()
        should_the_gui_start = "Yes"

    @staticmethod
    def generalize_repo_path(path):
        """
        

        Args:
          path: 

        Returns:

        """
        gen_path = path.split('/')
        gen_path.pop(-1)
        gen_path.pop(-1)
        gen_path = '/'.join(gen_path)
        return gen_path

    def on_repo_path_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        if not self.config_loaded and self.disconnect_btn_state == 'Not pressed':
            temp_dict = {'linux_mf4_path': '', 'linux_evald_report_path': ''}
            choice = self.repo_path_var.get()
            if choice != 'Select a repository path' and choice != 'No repo, containing the repo keyword has been found!' and choice != 'Please, establish a connection to a host.':
                variants_list = self.connect_to_linux.search_for_variants_from_repopath(choice)
                for item in variants_list:
                    if type(item) is list:
                        temp_str = ''.join(map(str, item))
                        self.output_dict['variants_path'] = temp_str
                        variants_list.remove(item)
                # print(f"available variants after change of repo path = {variants_list}")
                self.populate_variants(variants_list)
                gen_repo_path = self.generalize_repo_path(choice)
                # print(f"Generalized path >>> {gen_repo_path}")
                temp_dict.update(self.connect_to_linux.find_evald_and_mf4log_folders(gen_repo_path))
                # print(f"TEMP_DICT after evald and mf4 paths search func >>> {temp_dict}")
                if temp_dict is not None and temp_dict['linux_mf4_path'] != '':
                    self.output_dict['linux_mf4_log_path'] = temp_dict['linux_mf4_path']
                    if temp_dict['linux_evald_report_path'] != '':
                        self.output_dict['linux_evald_reports_path'] = temp_dict['linux_evald_report_path']
                self.populate_evald_mf4log_paths(**self.output_dict)

    def populate_evald_mf4log_paths(self, **report_and_mf4_paths):
        """
        

        Args:
          **report_and_mf4_paths: 

        Returns:

        """
        if report_and_mf4_paths['linux_mf4_log_path'] == '':
            self.linux_mf4log_path.set('Not found...')
        elif report_and_mf4_paths['linux_mf4_log_path'] != '':
            self.linux_mf4log_path.set(report_and_mf4_paths['linux_mf4_log_path'])
        if report_and_mf4_paths['linux_evald_reports_path'] == '':
            self.linux_report_folderpath.set('Not found...')
        elif report_and_mf4_paths['linux_evald_reports_path'] != '':
            self.linux_report_folderpath.set(report_and_mf4_paths['linux_evald_reports_path'])

    def populate_repo_path(self, repo_paths_list):
        """
        

        Args:
          repo_paths_list: 

        Returns:

        """
        self.choices_repo_path.clear()  # clear the inital choices list
        self.choices_repo_path = repo_paths_list
        menu = self.repo_path_entry["menu"]
        menu.delete(0, "end")
        if len(repo_paths_list) >= 1:
            for path in self.choices_repo_path:
                menu.add_command(label=path,
                                 command=lambda value=path: self.repo_path_var.set(value))
            self.repo_path_var.set('Select a repository path')
            self.product_var.set('Choose a variant after selecting a repository path')
        else:
            self.repo_path_var.set('No repo, containing the repo keyword has been found!')

    def populate_variants(self, variants_list):
        """
        

        Args:
          variants_list: 

        Returns:

        """
        self.choices_product_var.clear()  # clear the inital choices list
        self.choices_product_var = variants_list
        menu = self.product_var_entry["menu"]
        menu.delete(0, "end")
        if len(variants_list) >= 1:
            for path in self.choices_product_var:
                menu.add_command(label=path,
                                 command=lambda value=path: self.product_var.set(value))
            # self.choices_product_var.set(self.choices_repo_path[0])
            self.product_var.set('Variants...')

    def this_destroys_the_main_win(self):
        """ """
        self.loginAndConfigWin.destroy()
        MainWin()

    def connect(self):
        """ """
        conn_info = self.get_bench_conn_info()  # we get the user info here
        connection_object = self.connect_to_linux.connect(**conn_info)  # create a connection with the HOST machine
        if connection_object == gaierror:  # 'host issue'  "pass or user issue"
            return gaierror
        elif connection_object == AuthenticationException:
            return AuthenticationException
        elif connection_object == TimeoutError:
            return TimeoutError
        else:
            return connection_object

    def attempt_connection_to_host(self):
        """ """
        self.config_loaded = False
        if self.ssh_pass_entry.get() != '':
            self.disconnect_btn_state = 'Not pressed'
            conn_info = self.get_bench_conn_info()  # we get the user info here
            connection_object = self.connect()  # create a connection with the HOST machine
            if connection_object != AuthenticationException and \
                    connection_object != TimeoutError and \
                    connection_object != gaierror:
                # after we are connected, we need to use the repo-keyword to search and find the possible repo paths
                self.linux_report_folderpath.set('Will be auto-filled after selecting a test repo path...')
                self.linux_mf4log_path.set('Will be auto-filled after selecting a test repo path...')
                ods_repo_paths = self.connect_to_linux.search_for_repo_paths(self.repo_keyword_var.get(), **conn_info)  # this finds the available repos and returns a list with the paths to the repos
                if len(ods_repo_paths) > 0:
                    self.populate_repo_path(ods_repo_paths)
                else:
                    self.repo_path_var.set('No repo, containing the repo keyword has been found!')
                    self.product_var.set('...')
            elif connection_object == AuthenticationException:
                messagebox.showwarning('Password or user issue!', 'Username or password are wrong?')
            elif connection_object == gaierror:
                messagebox.showwarning('Host name issue!', 'Hostname is wrong?')
            elif connection_object == TimeoutError:
                messagebox.showwarning('Timeout', 'Connection attempt timeout...')
        elif self.ssh_pass_entry.get() == '':
            messagebox.showwarning('Empty password field', 'Password field is empty!')

    def get_bench_conn_info(self):
        """ """
        bench_conn_info = {'hostname': self.ssh_host_entry.get(), 'username': self.ssh_user_entry.get(), 'password': self.ssh_pass_entry.get()}
        return bench_conn_info

    def on_closing(self):
        """ """
        global should_the_gui_start
        should_the_gui_start = "No"
        self.loginAndConfigWin.destroy()

    def __call__(self):
        self.loginAndConfigWin.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.loginAndConfigWin.mainloop()


class ExplorerTreeview(tkinter.ttk.Treeview):
    """ """

    columns = ('Files and folders',)

    def __init__(self, root_frame, tc_helper_obj):
        super().__init__()

        self.root = root_frame

        self.explorer_tree = tkinter.ttk.Treeview(self.root, columns=1, selectmode='extended')
        self.explorer_tree.grid(row=1, column=0, rowspan=2, sticky='we', columnspan=3, ipadx=200)  # row=1, column=0, sticky='nsew', rowspan=1, columnspan=3

        self.sel_listScroll_x = tkinter.Scrollbar(self.root, orient=tkinter.HORIZONTAL, command=self.explorer_tree.xview)
        self.sel_listScroll_x.grid(row=3, column=0, sticky='ewn', columnspan=3)
        self.explorer_tree['xscrollcommand'] = self.sel_listScroll_x.set

        self.listScroll_y = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
        self.listScroll_y.grid(row=1, column=4, sticky='nsw', rowspan=2)

        self.listScroll_y.config(command=self.explorer_tree.yview)
        self.explorer_tree.configure(yscrollcommand=self.listScroll_y.set)
        self._iid = 0

        self.tc_helper = tc_helper_obj

        self.explorer_tree['columns'] = self.columns
        self.explorer_tree.column("#0", width=0, stretch=NO)
        self.explorer_tree.column(self.columns[0], minwidth=245, width=245, anchor=W, stretch=YES)  # old width=245

        self.explorer_tree.heading("#0", text="", anchor=CENTER)
        self.explorer_tree.heading(self.columns[0], text=self.columns[0], anchor=W)

    def update_explorer(self, tc_list):
        """
        

        Args:
          tc_list: 

        Returns:

        """
        if len(tc_list) > 0:
            for i in range(0, len(tc_list)):
                if type(tc_list[i]) is str:
                    self.explorer_tree.insert(parent='', index='end', text='', values=(tc_list[i],))
                    self._iid += 1

    def get_list_of_children(self):
        """ """
        return self.explorer_tree.get_children()

    def get_index(self, line):
        """
        

        Args:
          line: 

        Returns:

        """
        return self.explorer_tree.index(line)

    def get_item_values(self, item_from_selection):
        """
        

        Args:
          item_from_selection: 

        Returns:

        """
        tc_name = self.explorer_tree.item(item_from_selection, 'values')
        tc_name = tc_name[0]
        return tc_name

    def get_selection(self):
        """ """
        curr_sel = self.explorer_tree.selection()
        return curr_sel

    def get_tree_object(self):
        """ """
        return self.explorer_tree

    def clear_explorer(self):
        """ """
        get_items = self.get_list_of_children()
        for item in get_items:
            self.explorer_tree.delete(item)


class TCTreeview(tkinter.ttk.Treeview):
    """ """
    columns = ('Test name', 'Status')
    tc_list = []

    def __init__(self, root_frame, tc_helper_obj, treeview_event, possible_statuses, synch_index, synch_status):
        super().__init__()

        self.root = root_frame
        self.tcs_tree = tkinter.ttk.Treeview(self.root, columns=2, selectmode='extended')
        self.tcs_tree.grid(row=0, column=0, rowspan=2, columnspan=3, ipadx=200)  # row=5, column=0, sticky='nsew', rowspan=1, columnspan=3)

        self.sel_listScroll_x = tkinter.Scrollbar(self.root, orient=tkinter.HORIZONTAL, command=self.tcs_tree.xview)
        self.sel_listScroll_x.grid(row=3, column=0, sticky='ewn', columnspan=3)
        self.tcs_tree['xscrollcommand'] = self.sel_listScroll_x.set

        self.listScroll_y = tkinter.Scrollbar(self.root, orient=tkinter.VERTICAL)
        self.listScroll_y.grid(row=0, column=4, sticky='nsw', rowspan=2)

        self.listScroll_y.config(command=self.tcs_tree.yview)
        self.tcs_tree.configure(yscrollcommand=self.listScroll_y.set)

        self.possible_statuses = possible_statuses
        self.synch_index = synch_index
        self.synch_status = synch_status
        self._cur_selection = []
        self.tc_helper = tc_helper_obj
        self.treeview_event = treeview_event
        self._iid = 0
        # Define columns
        self.tcs_tree['columns'] = self.columns
        self.tcs_tree.column("#0", width=0, stretch=NO)
        self.tcs_tree.column(self.columns[0], minwidth=50, width=150, anchor=W, stretch=YES)
        self.tcs_tree.column(self.columns[-1], width=95, anchor=W, stretch=NO)

        # Create headings
        self.tcs_tree.heading("#0", text="", anchor=CENTER)
        self.tcs_tree.heading(self.columns[0], text=self.columns[0], anchor=W)
        self.tcs_tree.heading(self.columns[-1], text=self.columns[-1], anchor=W)

        self.treeview_event.add_subscribers_to_event(self.update_tc_status_from_event)

    def get_tc_status_by_item(self, item):
        """
        

        Args:
          item: 

        Returns:

        """
        tc_status = self.tcs_tree.item(item)['values']
        tc_status = tc_status[1]
        return tc_status

    def get_tc_name_by_item(self, item):
        """
        

        Args:
          item: 

        Returns:

        """
        tc_name = self.tcs_tree.item(item, 'values')
        tc_name = tc_name[0]
        return tc_name

    def get_current_selection(self):
        """ """
        return self.tcs_tree.selection()

    def get_index(self, line):
        """
        

        Args:
          line: 

        Returns:

        """
        return self.tcs_tree.index(line)

    def get_list_of_children(self):
        """ """
        return self.tcs_tree.get_children()

    def remove_record(self):
        """ """
        children_list = self.get_current_selection()
        for i in range(len(children_list) - 1, -1, -1):
            index = self.get_index(children_list[i])
            self.tc_helper.remove_item(index)
            self.tcs_tree.delete(children_list[i])

    def tc_insert(self, tc):
        """
        

        Args:
          tc: 

        Returns:

        """
        if len(tc) > 0:
            self.tcs_tree.insert(parent='', index='end', text='', values=(tc, "Not started"))

    def update_tc_status(self, line, value):
        """
        

        Args:
          line: 
          value: 

        Returns:

        """
        self.tcs_tree.set(line, self.columns[-1], value)

    def update_tc_status_from_event(self):
        """ """
        for row in self.get_list_of_children():
            row_index = self.get_index(row)
            if row_index == self.synch_index.value:
                self.update_tc_status(row, self.synch_status.value.decode())
                break

    def re_init_tcs_to_not_started(self):
        """ """
        for row in self.get_list_of_children():
            self.update_tc_status(row, self.possible_statuses[0].decode())


class TCHelper:
    """ """
    max_col_len = 245

    def __init__(self):
        self._execlist = []
        self.tc_status_list = []
        self._current_index = 0
        self._size = None

    def get_last_status(self):
        """ """
        if len(self.tc_status_list) == 1:
            return self.tc_status_list[0]
        elif len(self.tc_status_list) > 1:
            return self.tc_status_list[-1]

    def set_current_tc_status(self, index, value):
        """
        

        Args:
          index: 
          value: 

        Returns:

        """
        self.tc_status_list[index] = value

    def get_tc_status_list(self):
        """ """
        return self.tc_status_list

    def clear_tc_status_list(self):
        """ """
        self.tc_status_list.clear()

    def get_current_running_tc_index(self):
        """ """
        return self._current_index

    def update_index(self, val):
        """
        

        Args:
          val: 

        Returns:

        """
        self._current_index = val

    def append(self, tc):
        """
        

        Args:
          tc: 

        Returns:

        """
        self._execlist.append(tc)
        self.tc_status_list.append('Not started')
        if len(self._execlist) == 1:
            self._size = 0
        elif len(self._execlist) > 1:
            self._size += 1
        # self.see_exec_list()

    def remove_item(self, index):
        """
        

        Args:
          index: 

        Returns:

        """
        if self._size > 0:
            self._execlist.pop(index)
            self.tc_status_list.pop(index)
            self._size -= 1
        elif self._size == 0:
            self._execlist.pop(index)
            self.tc_status_list.pop(index)
        # self.see_exec_list()

    @staticmethod
    def make_path_fit(path):
        """
        

        Args:
          path: 

        Returns:

        """
        new_fit = path.split('/')
        testname = new_fit[-1]
        return testname

    def see_exec_list(self):
        """ """
        for item in self._execlist:
            print('\t\t\t' + item)
        for status in self.tc_status_list:
            print('\t\t\t' + status)

    def get(self, index):
        """
        

        Args:
          index: 

        Returns:

        """
        return self._execlist[index]

    def get_test_list(self):
        """ """
        return self._execlist

    def get_size(self):
        """ """
        return self._size

    def get_max_col_len(self):
        """ """
        return self.max_col_len


class Event(object):
    """ """

    def __init__(self):
        self.__eventhandlers = []

    def __iadd__(self, handler):
        self.__eventhandlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__eventhandlers.remove(handler)
        return self

    def __call__(self, *args, **keywargs):
        # print(f'\tHARD DEBUG >>>> Event class >>> EVENT IS RAISED')
        for eventhandler in self.__eventhandlers:
            eventhandler(*args, **keywargs)


class TCStatusEvent:
    """ """

    def __init__(self):
        self.the_event = Event()

    def raise_event(self):
        """ """
        self.the_event()

    def add_subscribers_to_event(self, method):
        """
        

        Args:
          method: 

        Returns:

        """
        self.the_event += method


class MainWin:
    """ """

    paths_2_sel_yml_files = []
    selection_items = []
    skipped_tests_by_var = []
    is_search_invoked = False
    force_stop_tc_run = False
    testrun_alive = False
    cwf = ''
    possible_statuses = [b'Not started', b'Running', b'Stopped', b'Passed', b'Failed', b'Skipped', b'Wrapping up..']

    def __init__(self, **main_config_info):
        shared_mem_index = Value('i', 0)
        shared_mem_status = Array('c', self.possible_statuses[-1])

        self.synch_index = shared_mem_index
        self.synch_status = shared_mem_status

        self.tc_name_mask = re.compile(r'TC_\d*_\w*\.yml')
        self.config_info = dict()
        self.bench_info = dict()
        self.config_info.update(main_config_info)
        self.bench_info.update(self.get_bench_conn_info())

        self.host = main_config_info['hostname']  # tool team HIL3 location
        self.username = main_config_info['username']
        self.password = main_config_info['password']
        temp_path = self.config_info['test_repo_path']
        suffix = '/' + self.config_info['test_repo_keyword']
        self.path = temp_path.replace(suffix, '')

        self.tool_results_folder_path = main_config_info['local_report_output_path']
        self.local_evald_rf_path = self.tool_results_folder_path + "evald_report\\"
        self.linux_evald_rf_path = main_config_info['linux_evald_reports_path']

        self.mainWin = tkinter.Tk()
        self.mainWin.title("ADAS HIL test execution tool")
        self.mainWin.geometry('840x810+40+100')
        self.mainWin['padx'] = 8

        # Sftp is used by all gui parts except 'search' functionality
        self.sftp = ssh_client.SSHClient(**self.config_info)
        self.connection_object = self.sftp.connection
        self.cwf = self.path
        # Init BenchConnectAndSearch object to give to the 'search' functionality
        self.search_obj = BenchConnectAndSearch()
        self.search_obj_connection = self.search_connect()
        self.mainSearch_obj = Search(self.search_obj_connection, self.config_info['test_repo_path'])

        self.explorer_list = []

        self.mainWin.columnconfigure(0, weight=1)
        self.mainWin.columnconfigure(1, weight=1)
        self.mainWin.columnconfigure(2, weight=1)
        self.mainWin.columnconfigure(3, weight=1)
        self.mainWin.columnconfigure(4, weight=1)
        self.mainWin.columnconfigure(5, weight=1)
        self.mainWin.rowconfigure(0, weight=1)
        self.mainWin.rowconfigure(1, weight=1)
        self.mainWin.rowconfigure(2, weight=1)
        self.mainWin.rowconfigure(3, weight=1)
        self.mainWin.rowconfigure(4, weight=1)
        self.mainWin.rowconfigure(5, weight=1)
        self.mainWin.rowconfigure(6, weight=1)
        self.mainWin.rowconfigure(7, weight=1)
        self.mainWin.rowconfigure(8, weight=1)

        self.label = tkinter.Label(self.mainWin,
                                   text="FILE EXPLORER:")
        self.label.grid(row=1, column=0, columnspan=2, sticky='w')

        self.main_frame = tkinter.LabelFrame(self.mainWin)
        self.main_frame.grid(row=3, column=0, sticky='wnes', columnspan=5, rowspan=5)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.columnconfigure(4, weight=1)

        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.rowconfigure(4, weight=1)

        '''''''''''''''''''''''''''''''''' SSH frame section '''''''''''''''''''''''''''''''''''
        # Create SSH Label frame
        self.ssh_frame = tkinter.LabelFrame(self.mainWin, text='Linux Cloe SSH connection')
        self.ssh_frame.grid(row=0, column=0, sticky='wns', columnspan=3, rowspan=1, padx=5)

        # Create SSH Label inside SSH Label frame
        self.ssh_host_label = tkinter.Label(self.ssh_frame, text="SSH Host:")
        self.ssh_host_label.grid(row=0, column=0, sticky='w', columnspan=1, rowspan=1)

        self.ssh_host_entry_label = tkinter.Label(self.ssh_frame, text=self.config_info['hostname'])
        self.ssh_host_entry_label.grid(row=0, column=2, sticky='w',columnspan=1, rowspan=1, padx=15)

        # #Create Username Label inside SSH Label frame
        self.ssh_username = tkinter.Label(self.ssh_frame, text="Username:")
        self.ssh_username.grid(row=1, column=0, sticky='w', columnspan=1, rowspan=1)

        self.ssh_user_entry_label = tkinter.Label(self.ssh_frame, text=self.config_info['username'])
        self.ssh_user_entry_label.grid(row=1, column=2, sticky='w',columnspan=1, rowspan=1, padx=15)

        # Create Variant Label inside SSH Label frame
        self.variant_label = tkinter.Label(self.ssh_frame, text="Variant:")
        self.variant_label.grid(row=2, column=0, sticky='w', columnspan=1, rowspan=1)

        variant = self.config_info['product_variant']
        variant = re.sub('evald_config_develop_', '', variant)
        variant = re.sub('_hil\\.yml', '', variant)
        self.variant_label_entry = tkinter.Label(self.ssh_frame, text=variant)
        self.variant_label_entry.grid(row=2, column=2, sticky='w', columnspan=1, rowspan=1, padx=15)

        '''''''''''''''''''''''''''''''''' SEARCH frame section '''''''''''''''''''''''''''''''''''
        # Create SSH Label frame
        self.search_frame = tkinter.LabelFrame(self.mainWin, text='Search')
        self.search_frame.grid(row=0, column=2, sticky='wns', columnspan=3, rowspan=1, ipadx=10)

        # Create 'Search by' Label inside SSH Label frame
        self.searchby_lbl = tkinter.Label(self.search_frame, text="Search by:")
        self.searchby_lbl.grid(row=0, column=0, sticky='w', columnspan=1, rowspan=1)

        self.search_btn = tkinter.ttk.Button(self.search_frame, text='SEARCH', command=self.engage_search)
        self.search_btn.grid(row=0, column=2, columnspan=1, rowspan=1, padx=7, ipady=2)  # ipady=2, ipadx=1, padx=10, pady=7
        # self.search_btn['state'] = tkinter.DISABLED

        # Create entry box and variable for the input of product variant
        self.searchwhat_choices = ['File name', 'Folder name', 'File content']
        self.searchwhat_var = tkinter.StringVar()
        self.searchwhat_var.set('Choose option')
        self.searchwhat_optionmenu = tkinter.OptionMenu(self.search_frame, self.searchwhat_var, *self.searchwhat_choices)
        self.searchwhat_optionmenu.grid(row=0, column=1, sticky='ws', columnspan=1, rowspan=1)
        self.searchwhat_optionmenu.config(width=13)

        # Create 'keyword' Label inside search Label frame
        self.search_keywrd_lbl = tkinter.Label(self.search_frame, text="Keyword:")
        self.search_keywrd_lbl.grid(row=1, column=0, columnspan=1, rowspan=1, pady=3)

        # Create entry box and variable for the input of linux report folder
        self.searchbox_var = tkinter.StringVar()
        self.searchbox_var.set('')
        self.searchbox_entry = tkinter.Entry(self.search_frame, textvariable=self.searchbox_var, width=33)
        self.searchbox_entry.grid(row=1, column=1, sticky='w', columnspan=2, rowspan=1, padx=2, pady=5, ipady=3)

        '''''''''''''''''''''''''''''''''' Explorer and selected tests section '''''''''''''''''''''''''''''''''''

        # Frame for file xplorer
        self.file_xplr_frame = tkinter.LabelFrame(self.main_frame, text='Explorer')
        self.file_xplr_frame.grid(row=1, column=0, sticky='w', columnspan=3)
        # Frame for the selected items
        self.selected_items_frame = tkinter.LabelFrame(self.main_frame, text='Selected .yml test cases')
        self.selected_items_frame.grid(row=4, column=0, sticky='w', columnspan=3, rowspan=3)
        # Frame for the folder path
        self.folder_path = tkinter.LabelFrame(self.main_frame, text='Selected items')
        self.folder_path.grid(row=7, column=0, sticky='w', columnspan=2)

        # EXPERIMENTAL PART BEGIN
        self.treeview_event = TCStatusEvent()
        self.tc_helper = TCHelper()
        self.sftp.change_dir(self.path)
        self.list_of_dir_items = self.sftp.list_directory(self.path)
        self.fileList = ExplorerTreeview(self.file_xplr_frame, self.tc_helper)
        self.fileList.update_explorer(self.list_of_dir_items)
        self.fileSelectionList = TCTreeview(self.selected_items_frame, self.tc_helper, self.treeview_event, self.possible_statuses, self.synch_index, self.synch_status)

        explorer_tree_obj = self.fileList.get_tree_object()
        explorer_tree_obj.bind('<Double-1>', self.selected_items)

        # Frame for left buttons
        self.option_frame_left = tkinter.LabelFrame(self.main_frame, text='Actions')
        self.option_frame_left.grid(row=3, column=0, sticky='w', padx=0, ipady=5)

        # Frame for right buttons
        self.option_frame_right = tkinter.LabelFrame(self.main_frame, text='Actions')
        self.option_frame_right.grid(row=4, column=4, sticky='nw', padx=0, pady=3, rowspan=4)

        # ################ Create DropDown menu for selecting make file options ################
        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(self.option_frame_right)
        # Tupple with options
        self.choices = ('evald-launch-gui',
                        'evald-launch-notresim')

        # Apparently the StringVar object that will hold the default value for the popup menu just needs to be defined
        # The assigning of the default value for the menu to the StringVar object is done by giving it as a third argument when creating the OptionMenu object
        self.popupMenu = tkinter.ttk.OptionMenu(self.option_frame_right, self.tkvar, self.choices[0], *self.choices)
        self.popupMenu.grid(row=3, column=5, sticky='s', ipady=2, ipadx=1, padx=10, pady=7)
        self.popupMenu.config(width=15)
        self.tkvar.trace('w', self.change_dropdown)
        ##########################################################################################

        '''''''''''''''''''''''''''''''''' "Back" button and "Current working path" label '''''''''''''''''''''''''''''''''''
        self.back_and_cwf_frame = tkinter.LabelFrame(self.main_frame)
        self.back_and_cwf_frame.grid(row=0, column=0, sticky='we', rowspan=1, columnspan=3)
        # Button for going back
        self.go_back_btn = tkinter.ttk.Button(self.back_and_cwf_frame, text='<<<BACK', command=self.go_back)
        self.go_back_btn.grid(row=0, column=0, sticky='w', ipady=2)

        # Label to show the current dir position
        self.current_dir_lbl_strvar = tkinter.StringVar()
        self.current_dir_lbl_strvar.set(self.cwf)
        self.current_dir_lbl = tkinter.Label(self.back_and_cwf_frame, text=self.sftp.get_current_working_dir())
        self.current_dir_lbl.grid(row=0, column=1)
        '''''''''''''''''''''''''''''''''' "Back" button and "Current working path" label END '''''''''''''''''''''''''''''''''''
        # Left buttons
        self.file_browse = tkinter.ttk.Button(self.option_frame_left, text='Add Test', command=self.add_items)
        self.file_browse.grid(row=0, column=0, sticky='w', ipady=2, padx=10)
        self.file_browse = tkinter.ttk.Button(self.option_frame_left, text='Delete Test',
                                              command=self.clear_selection_box)
        self.file_browse.grid(row=0, column=1, sticky='w', ipady=2, padx=10)
        self.add_tests_from_list = tkinter.ttk.Button(self.option_frame_left, text='Add Test From TXT list', command=self.browse_for_txt_file_and_get_list)
        self.add_tests_from_list.grid(row=0, column=2, sticky='w', ipady=2, padx=10)
        self.add_tests_from_list.config(width=25)
        self.add_tests_from_rqmlist = tkinter.ttk.Button(self.option_frame_left, text='Add Test From RQM TXT list',
                                                         command=self.browse_for_txt_file_and_get_rqm_list)
        self.add_tests_from_rqmlist.grid(row=0, column=3, sticky='w', ipady=2, padx=10)
        self.add_tests_from_rqmlist.config(width=25)

        # Right buttons
        self.terminal = tkinter.ttk.Button(self.option_frame_right, text='Terminal', command=self.pseudo_terminal)
        self.terminal.grid(row=0, column=5, sticky='w', ipady=2, ipadx=1, padx=10, pady=7)
        self.terminal['state'] = tkinter.DISABLED
        self.stop_test_run = tkinter.ttk.Button(self.option_frame_right, text='Stop Tests', command=self.stop_tests)
        self.stop_test_run.grid(row=1, column=5, sticky='w', ipady=2, ipadx=1, padx=10, pady=7)
        self.stop_test_run['state'] = tkinter.DISABLED
        self.launch_evalD = tkinter.ttk.Button(self.option_frame_right, text='Execute', command=self.launch_tests)
        self.launch_evalD.grid(row=2, column=5, sticky='w', ipady=2, ipadx=1, padx=10, pady=7)

        # other
        self.tc_RUN = None
        self.search_results_list = ''
        self.max_len = 105
        self.start_evald_thread = None
        self.read_shared_mem_thread = None

        # right click binding
        self.indv_tc_run = False
        self.rc_menu = Menu(self.fileSelectionList, tearoff=False)
        self.rc_menu.add_command()

    def raise_treeview_event(self):
        """ """
        self.treeview_event.raise_event()

    def wrap_displayed_text_if_long(self, rand_string):
        """
        

        Args:
          rand_string: 

        Returns:

        """
        rand_string_len = len(rand_string)
        wrapped_path = ''
        if rand_string_len <= self.max_len:
            return rand_string
        elif rand_string_len > self.max_len:
            delta = rand_string_len - self.max_len
            for i in range(delta, rand_string_len):
                if i == delta or i == (delta + 1) or i == (delta + 2):
                    wrapped_path += '.'
                else:
                    wrapped_path += rand_string[i]
            return wrapped_path

    def engage_search(self):
        """ """
        if self.searchwhat_var.get() == 'Choose option':
            messagebox.showinfo('Search by what?', 'Please, select a "Search by" option')
        else:
            if self.searchbox_var.get() != '':
                self.search_results_list = ''
                self.clear_browser_box()
                self.cwf = self.sftp.get_current_working_dir()
                self.current_dir_lbl['text'] = 'SEARCH RESULTS'
                self.is_search_invoked = True

                if self.searchwhat_var.get() == 'File name':
                    self.search_results_list = self.mainSearch_obj.search_by_file_or_folder_name(self.searchbox_var.get(), 'File')
                elif self.searchwhat_var.get() == 'Folder name':
                    self.search_results_list = self.mainSearch_obj.search_by_file_or_folder_name(self.searchbox_var.get(), 'Folder')
                elif self.searchwhat_var.get() == 'File content':
                    self.search_results_list = self.mainSearch_obj.search_by_file_content(self.searchbox_var.get())

                if self.search_results_list == 'Nothing found':
                    self.fileList.update_explorer(self.search_results_list)
                elif self.search_results_list != 'Nothing found' and not None:
                    # for result in self.search_results_list:
                    self.fileList.update_explorer(self.search_results_list)

            elif self.searchbox_var.get() == '':
                messagebox.showinfo('Search field', 'Search field is empty!')

    def get_bench_conn_info(self):
        """ """
        bench_conn_info = {'hostname': self.config_info['hostname'], 'username': self.config_info['username'], 'password': self.config_info['password']}
        return bench_conn_info

    def search_connect(self):
        """ """
        return self.search_obj.connect(**self.bench_info)

    def filter_by_eom(self, fullyamlpath):
        """
        

        Args:
          fullyamlpath: 

        Returns:

        """
        list_of_read_lines = self.sftp.execute('cat ' + fullyamlpath)
        tagsmask = re.compile(r'OEM:')
        for line in list_of_read_lines:
            line = line.decode('utf-8')
            if len(tagsmask.findall(line)) > 0:
                line = re.sub(tagsmask, '', line)
                line = line.strip()
                variantslist = line.split(',')
                for variant in variantslist:
                    if variant in self.config_info['product_variant']:
                        return True
        return False

    @staticmethod
    def get_tc_name_from_line_main_gui(mask, line_from_file):
        """
        

        Args:
          mask: 
          line_from_file: 

        Returns:

        """
        if len(mask.findall(line_from_file)) != 0:
            for name_match in mask.findall(line_from_file):
                tc_name = name_match
                return tc_name
        elif len(mask.findall(line_from_file)) == 0:
            tc_name = ""
            return tc_name

    def browse_for_txt_file_and_get_rqm_list(self):
        """ """
        # read the list
        filename_path = filedialog.askopenfilename(initialdir="/",
                                                   title="Select a File",
                                                   filetypes=(("Text files",
                                                              "*.txt*"),
                                                              ("all files",
                                                              "*.*")))
        if filename_path != '':
            handle_ids = HandleRQMIDs(filename_path, self.connection_object, **self.config_info)
            final_tc_list = handle_ids.analyze_input_rqm_id_list()
            if len(final_tc_list) > 0:
                for full_yaml_path in final_tc_list:
                    tc_name = self.get_tc_name_from_line_main_gui(self.tc_name_mask, full_yaml_path)  # get the tc name from the full path
                    if tc_name != "":
                        self.fileSelectionList.tc_insert(tc_name)
                        self.tc_helper.append(full_yaml_path)
                if len(handle_ids.oem_tag_problems['tcs_with_no_oem_tags']) > 0 or \
                        len(handle_ids.oem_tag_problems['tcs_with_more_than_one_oem_tag']) > 0 or \
                        len(handle_ids.yaml_paths_with_duplicate_tc_ids) > 0 or \
                        len(handle_ids.ids_not_found) > 0:
                    messagebox.showinfo('INFO', f'Attention...\n'
                                                f'These files were skipped because they dont contain the right variant, are missing,\n'
                                                f'or their internal TC ids are duplicated\n'
                                                f'Note: TCs with duplicated internal ids are not addded in the TC selection\n\n'
                                                f'No OEM tag or wrong tag >>> \n{handle_ids.oem_tag_problems["tcs_with_no_oem_tags"]}\n\n'
                                                f'More than one OEM tag >>> \n{handle_ids.oem_tag_problems["tcs_with_more_than_one_oem_tag"]}\n\n'
                                                f'TCs, containing the same ID >>> \n{handle_ids.yaml_paths_with_duplicate_tc_ids}\n'
                                                f'Not found TC IDs from uploaded list >>> \n{handle_ids.ids_not_found}\n')
                    with open('rqm_list_addition.txt', 'w') as bugged_tcs_file_report:
                        bugged_tcs_file_report.write('tcs_with_no_oem_tags:\n')
                        for no_eom_tc in handle_ids.oem_tag_problems["tcs_with_no_oem_tags"]:
                            bugged_tcs_file_report.write(no_eom_tc + '\n')
                        bugged_tcs_file_report.write('tcs_with_more_than_one_oem_tag:\n')
                        for plus_eom_tc in handle_ids.oem_tag_problems["tcs_with_more_than_one_oem_tag"]:
                            bugged_tcs_file_report.write(plus_eom_tc + '\n')
                        bugged_tcs_file_report.write('yaml_paths_with_duplicate_tc_ids:\n')
                        for rqm_id, duplicate_yml in handle_ids.yaml_paths_with_duplicate_tc_ids.items():
                            bugged_tcs_file_report.write('RQM ID: ' + rqm_id + '\n')
                            for dup in duplicate_yml:
                                bugged_tcs_file_report.write('TC: ' + dup + '\n')
                        bugged_tcs_file_report.write('ids_not_found:\n')
                        for rqm_id in handle_ids.ids_not_found:
                            bugged_tcs_file_report.write(rqm_id + '\n')
            else:
                messagebox.showinfo('INFO', f'List is empty...')
        else:
            messagebox.showinfo('INFO', f'No file has been opened...')

    def browse_for_txt_file_and_get_list(self):
        """ """

        final_tc_list = []
        problematic_tcs = {'same_tc_name': [], 'oem_tag_err': [], 'not_found_tcs': []}
        hst_usr_pss = {'hostname': self.config_info['hostname'], 'username': self.config_info['username'],
                       'password': self.config_info['password']}
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("Text files",
                                                          "*.txt*"),
                                                         ("all files",
                                                          "*.*")))
        bench_conn = BenchConnectAndSearch()
        tests_from_inputlist = bench_conn.read_txt_and_init_list(filename)
        if len(tests_from_inputlist) > 0:
            filteredlist = bench_conn.filter_init_list(tests_from_inputlist)
            bench_conn.connect(**hst_usr_pss)
            for listitem in filteredlist:
                results = bench_conn.list_results_from_search(listitem, self.config_info['test_repo_path'])  # list of results from the search
                temp_results = bench_conn.extract_tc_by_tcfolder_keyword(results, **self.config_info)
                for test_case_path in temp_results:
                    if len(temp_results) == 1:  # in case we have one result from name search
                        if self.filter_by_eom(test_case_path):
                            self.tc_helper.append(test_case_path)

                            tcname = bench_conn.get_tc_name_from_line(test_case_path)
                            if tcname != '':
                                self.fileSelectionList.tc_insert(tcname)
                        if not self.filter_by_eom(test_case_path):
                            problematic_tcs['oem_tag_err'].append(test_case_path)
                    elif len(temp_results) > 1:  # in case we have multiple results, we add them if they have an oem tag, but we also add them to the dict with problematic TCs, just for traceability
                        if self.filter_by_eom(test_case_path):
                            self.tc_helper.append(test_case_path)
                            problematic_tcs['same_tc_name'].append(test_case_path)
                            tcname = bench_conn.get_tc_name_from_line(test_case_path)
                            if tcname != '':
                                # here we add the full path because there are multiple tests with the same name located in different folders. Thats why we they will appear in the selection with their full path.
                                self.fileSelectionList.tc_insert(self.wrap_displayed_text_if_long(test_case_path))
                        if not self.filter_by_eom(test_case_path):
                            problematic_tcs['oem_tag_err'].append(test_case_path)
                    elif len(temp_results) == 0:  # in case there is no tc path found found
                        problematic_tcs['not_found_tcs'].append(test_case_path)
            if len(problematic_tcs['not_found_tcs']) > 0 or len(problematic_tcs['same_tc_name']) > 0 or len(problematic_tcs['oem_tag_err']) > 0:
                messagebox.showinfo('INFO', f'Attention...\n'
                                            f'These files were skipped because they dont contain the right variant, or are missing.\n'
                                            f'Also, you have TC names in the list that are duplicates. If they have the right oem tag, they will be added. Otherwise not, but you will see them here:\n'
                                            f'No OEM tag or wrong tag >>> {problematic_tcs["oem_tag_err"]}\n'                                            
                                            f'Duplicates, but added in the test selection >>> {problematic_tcs["same_tc_name"]}')
        else:
            messagebox.showinfo('INFO', f'No file has been opened, or file not found...')

    def disconnect_ssh(self):
        """ """
        self.sftp.close_connection()

    def list_dir(self, dir):
        """
        

        Args:
          dir: 

        Returns:

        """
        return self.sftp.list_directory(dir)

    def get_current_dir(self):
        """ """
        return self.sftp.get_current_working_dir()

    def change_dir(self, path):
        """
        

        Args:
          path: 

        Returns:

        """
        self.sftp.change_dir(path)

    def execute(self, command):
        """
        

        Args:
          command: 

        Returns:

        """
        self.sftp.execute(command)

    def update_explorer(self, directory):
        """
        

        Args:
          directory: 

        Returns:

        """
        self.change_dir(directory)
        dir_content = self.list_dir(directory)
        self.fileList.update_explorer(sorted(dir_content))

    def clear_browser_box(self):
        """ """
        self.fileList.clear_explorer()

    def selected_items(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        selected_indices = self.fileList.get_selection()
        for row in selected_indices:
            selection = self.fileList.get_item_values(row)
            if self.is_search_invoked:
                temp_init_dir = str(selection)
            else:
                temp_init_dir = self.cwf + '/' + str(selection)
            if not self.is_search_invoked:
                if self.sftp.check_is_dir(temp_init_dir):
                    self.current_dir_lbl['text'] = self.wrap_displayed_text_if_long(temp_init_dir)
                    self.change_dir(temp_init_dir)
                    self.cwf = self.sftp.get_current_working_dir()
                    self.clear_browser_box()
                    self.fileList.update_explorer(self.list_dir(temp_init_dir))
                selection = ""
            elif self.is_search_invoked:
                if not self.sftp.check_is_file(selection):
                    self.cwf = selection
                    self.current_dir_lbl['text'] = self.wrap_displayed_text_if_long(self.cwf)
                    self.clear_browser_box()
                    self.fileList.update_explorer(self.list_dir(selection))
                    self.is_search_invoked = False

    def add_items(self):
        """ """
        for row in self.fileList.get_selection():
            tcname = self.fileList.get_item_values(row)
            temp_file_path = '/' + tcname
            if not self.is_search_invoked:
                temp_file_path = self.cwf + '/' + tcname
            elif self.is_search_invoked:
                temp_file_path = tcname
                tcname = self.tc_helper.make_path_fit(tcname)
            if ".generic" not in str(tcname) and str(tcname).endswith('.yml'):
                if self.filter_by_eom(temp_file_path):
                    self.tc_helper.append(temp_file_path)
                    index = self.fileList.get_index(row)
                    self.fileSelectionList.tc_insert(tcname)

    def clear_selection_box(self):
        """ """
        self.fileSelectionList.remove_record()

    def go_back(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        if not self.is_search_invoked:
            initial_directory = self.cwf
            temp = list(initial_directory)
            if self.sftp.check_is_dir(initial_directory):
                for x in range(len(temp) - 1, 0, -1):
                    if temp[-1] != '\\' and temp[-1] != '/':
                        pass
                    elif x != -1 and (temp[x] == '\\' or temp[x] == '/'):
                        temp.pop(x)
                        break
                    temp.pop(x)
                initial_directory = ''.join(map(str, temp))
                self.cwf = initial_directory
                self.current_dir_lbl['text'] = self.wrap_displayed_text_if_long(initial_directory)
                self.clear_browser_box()
                self.update_explorer(initial_directory)
        elif self.is_search_invoked:
            self.clear_browser_box()
            self.current_dir_lbl['text'] = self.wrap_displayed_text_if_long(self.cwf)
            self.update_explorer(self.cwf)
            self.is_search_invoked = False

    def stop_tests(self):
        """ """
        self.synch_status.value = self.possible_statuses[2]
        self.raise_treeview_event()
        self.sftp.call_make_file_clean("docker-clean")
        self.tc_RUN.terminate_test_run()
        self.force_stop_tc_run = True
        self.testrun_alive = False
        self.stop_test_run['state'] = tkinter.DISABLED
        self.launch_evalD['state'] = tkinter.NORMAL

    def run_individual_test_case(self,):
        """ """
        self.indv_tc_run = True
        self.launch_tests()
        pass

    def launch_tests(self):
        """ """
        chosen_command = self.tkvar.get()
        testcases_list = self.tc_helper.get_test_list()
        if testcases_list == '' or len(testcases_list) == 0:
            messagebox.showwarning('warning', 'No tests are selected')
            self.stop_test_run['state'] = tkinter.DISABLED
            self.launch_evalD['state'] = tkinter.NORMAL
        else:
            self.fileSelectionList.re_init_tcs_to_not_started()
            self.testrun_alive = True
            self.synch_index.value = 0
            self.synch_status.value = self.possible_statuses[0]
            self.raise_treeview_event()
            tc_run = TestRun(testcases_list, chosen_command, self.tc_helper, self.synch_index, self.synch_status, self.possible_statuses, **self.config_info)
            tc_run.start_multiproc_test_run()
            self.tc_RUN = tc_run
            self.stop_test_run['state'] = tkinter.NORMAL
            self.launch_evalD['state'] = tkinter.DISABLED
            monitor_thread = Thread(target=self.is_testrun_alive, name="Thread for teststatus monitoring")
            monitor_thread.start()
            self.read_shared_mem_thread = Thread(target=self.read_shared_memory, name="DEBUG, READ SHARED MEMO THREAD FROM MAIN WIN...")
            self.read_shared_mem_thread.start()

    def is_testrun_alive(self):
        """ """
        while True:
            self.testrun_alive = self.tc_RUN.monitor_by_alive_status(self.force_stop_tc_run)
            if not self.testrun_alive:
                self.stop_test_run['state'] = tkinter.DISABLED
                self.launch_evalD['state'] = tkinter.NORMAL
                self.force_stop_tc_run = False
                # self.kill_launch_tests_thread()
                break

    def read_shared_memory(self):
        """ """
        last_index = -1
        last_status = b''
        while True:
            if last_index != self.synch_index.value:
                last_index = self.synch_index.value
                last_status = self.synch_status.value
                self.raise_treeview_event()
            else:
                if last_status not in self.synch_status.value and self.synch_status.value != b'Finished':
                    last_status = self.synch_status.value
                    self.raise_treeview_event()
            if self.synch_status.value == b'Stopped' or self.synch_status.value == b'Finished':
                break
            time.sleep(1)

    def thread_launch_tests(self):
        """ """
        self.start_evald_thread = Thread(target=self.launch_tests, name="THREAD FOR RUNNING YAML TESTS")
        self.start_evald_thread.start()
        self.read_shared_mem_thread = Thread(target=self.read_shared_memory, name="DEBUG, READ SHARED MEMO THREAD FROM MAIN WIN...")
        self.read_shared_mem_thread.start()
        self.stop_test_run['state'] = tkinter.NORMAL
        self.launch_evalD['state'] = tkinter.DISABLED

    def kill_launch_tests_thread(self):
        """ """
        self.start_evald_thread.join()

    # on change dropdown value
    def change_dropdown(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        return self.tkvar.get()

    def start_terminal(self):
        """ """
        pseudo_terminal = Thread(target=self.pseudo_terminal, name='Terminal Thread')
        pseudo_terminal.setDaemon(True)
        pseudo_terminal.start()

    @staticmethod
    def pseudo_terminal():
        """ """
        terminal = Terminal()
        terminal()

    def on_closing(self):
        """ """
        self.search_obj.close_connection()
        self.sftp.close_connection()
        self.mainWin.destroy()

    def __call__(self):
        self.mainWin.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainWin.mainloop()


class Search:
    """ """

    def __init__(self, connection_object, test_repo_path):
        self.connection = connection_object
        self.repo_path = test_repo_path

    def search_by_file_or_folder_name(self, search_what, folder_or_file='Folder'):
        """
        

        Args:
          search_what: 
          folder_or_file:  (Default value = 'Folder')

        Returns:

        """
        command = ''
        if folder_or_file == 'Folder':
            command = 'find ' + self.repo_path + ' ' + '-depth -name ' + search_what + '\n'
        elif folder_or_file == 'File':
            command = 'find ' + self.repo_path + ' ' + '-depth -name ' + '"*' + search_what + '*"' + '\n'
        search_results = []

        if search_what != '' and not None:
            stdin, stdout, stderr = self.connection.exec_command(command)
            output = stdout.read().decode()
            output = output.split('\n')

            for row in output:
                if row != '':
                    search_results.append(row)
            time.sleep(1)
            if len(search_results) == 0:
                search_results.append("NO RESULTS FOR '" + search_what + "'")
                return search_results
            elif len(search_results) > 0:
                return search_results
        else:
            return None

    def search_by_file_content(self, search_keyword):  # grep -r "1339347" /home/sya9lr/GIT_Workspace/OD_PSA_Testing/ods_cloe_tests/cloe_tests
        if search_keyword != '':
        """
        

        Args:
          search_keyword: 

        Returns:

        """
            command = 'grep -r ' + '"' + search_keyword + '" ' + self.repo_path + '\n'
            stdin, stdout, stderr = self.connection.exec_command(command)
            grepoutput = stdout.read().decode()
            grepoutput = grepoutput.split('\n')
            search_results = []

            for item in grepoutput:
                row = item.split(': ')
                for needed_val in row:
                    if '/home' in needed_val:  # means item is the location of the found result
                        search_results.append(needed_val)
            if len(search_results) == 0:
                search_results.append("NO RESULTS FOR '" + search_keyword + "'")
                return search_results
            elif len(search_results) > 0:
                return search_results
        else:
            return None


class TestRun(Process):
    """ """

    def __init__(self, yamltestcaseslist, command, tc_helper, synch_index, synch_status, possible_statuses, **conn_info):
        super().__init__()

        tcrun_pid = os.getpid()
        print(f'Process ID >>> ( {tcrun_pid} )')
        self.synch_index = synch_index
        self.synch_status = synch_status
        self.possible_statuses = possible_statuses

        self.tc_helper = tc_helper
        self.yaml_cases = yamltestcaseslist
        self.command_from_gui = command
        self.conn_info = dict()
        self.conn_info.update(conn_info)

        temp_path = self.conn_info['test_repo_path']
        suffix = '/' + self.conn_info['test_repo_keyword']
        self.path = temp_path.replace(suffix, '')
        self.tool_results_folder_path = self.conn_info['local_report_output_path']
        self.stop_tests = 'False'
        self.evald_config = self.conn_info['variants_path'] + '/' + self.conn_info['product_variant']
        self.date_now = str(dt.date.today()) + "_"
        self.time_now = str(time.strftime("%Hh%Mm%Ss"))

        self.make_proc = Process(target=self.launch_make, name="START TESTS MULTIPROCESS")

    def terminate_test_run(self):
        """ """
        if self.make_proc.is_alive():
            self.make_proc.terminate()

    def monitor_by_alive_status(self, stop_testrun):
        """
        

        Args:
          stop_testrun: 

        Returns:

        """
        if self.make_proc.is_alive() and stop_testrun is False:
            return True
        elif self.make_proc.is_alive() and stop_testrun is True:
            self.terminate_test_run()
            return False
        elif not self.make_proc.is_alive():
            return False

    def start_multiproc_test_run(self):
        """ """
        self.make_proc.start()

    def launch_make(self):
        """ """
        bench_conn = execute_client.ExecClient(**self.conn_info)
        rh = report_handler.ReportHandler(**self.conn_info)
        command = self.command_from_gui
        testrun_name = "tc_run_" + self.date_now + self.time_now
        rh.create_test_run_folder(self.tool_results_folder_path, testrun_name)
        for i in range(0, self.tc_helper.get_size() + 1):
            skip_cnt = 3
            while skip_cnt > 1:
                self.tc_helper.update_index(i)
                yaml_path = self.tc_helper.get(i)
                self.synch_index.value = i
                self.synch_status.value = self.possible_statuses[1]
                bench_conn.call_make_file(command, self.evald_config, yaml_path)
                self.synch_status.value = self.possible_statuses[-1]
                time.sleep(1.5)
                rh.handle_report(testrun_name, yaml_path)
                test_status = rh.get_current_test_status()
                self.synch_status.value = test_status.encode()
                time.sleep(1.5)
                if test_status == 'Skipped':
                    skip_cnt -= 1
                else:
                    break
        self.synch_status.value = b'Finished'
        bench_conn.disconnect()


class Terminal(Process):
    """ """

    timeout_flag = 0
    timeout_threshold = 3000
    log_file = 'D:\\ADAS_HIL\\Platform\\Classe\\Scripts\\HIL_test_exectuion_tool\\experimental_log.txt'
    terminal_log = '/home/sya9lr/GIT_Workspace/PSA_Testing/randomLog.txt'

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.geometry("650x340")
        self.frame = tkinter.Frame(self.root)
        self.frame.pack(expand=True, fill=tkinter.BOTH)
        self.label = tkinter.Label(self.frame, text="Pesho's terminal")
        self.label.pack(anchor='w')

        self.sftp = ssh_client.SSHClient()

        Process.__init__(self)
        self.start_terminal = Process(target=self.start, name="START TERMINAL MULTIPROCESS")

        self.terminal_field = Text(self.frame, undo=True, height=5, width=52)
        self.terminal_field.pack(expand=True, fill=tkinter.BOTH)
        # self.terminal_field.insert(tkinter.END, "What")
        self.update_terminal_thread = Thread(target=self.terminal_consumer)
        self.update_terminal_thread.start()

    def start(self):
        """ """
        self.start_terminal.start()

    def terminal_consumer(self):
        """ """
        pass
        # terminal_win.thread_fill_terminal()
        # remote_file = self.sftp.sftp_client.open(self.terminal_log, 'r', bufsize=1)
        # # with open(remote_file, 'r') as log:
        # while True:
        #     line = remote_file.readline()
        #     if line != '':  # we need the number of elements in the string here, to know where to move the cursor
        #         try:
        #             self.terminal_field.insert(tkinter.END, line)
        #             self.terminal_field.see(tkinter.END)
        #             self.timeout_flag = 0
        #         except TclError as e:
        #             print(f"Terminal has probably been shutdown, catching this exception gracefully: {e}")
        #             break
        # elif line == '':  # if the line is '' this means we are probably at the end of the file
        #     #time.sleep(0.01)
        #     #time.sleep(0.5)
        #     self.timeout_flag += 1
        #     try:
        #         self.terminal_field.insert(tkinter.END, "waiting for log file to not be empty...\n")
        #         self.terminal_field.see(tkinter.END)
        #     except TclError as e:
        #         print(f"Terminal has probably been shutdown, catching this exception gracefully: {e}")
        #         break

    def on_closing(self):
        """ """
        self.root.destroy()

    def __call__(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


if __name__ == '__main__':
    # freeze_support()

    login_and_config = LoginAndConfig()
    login_and_config()
    config_info = {}
    config_info.update(bench_conn_dict)

    if should_the_gui_start == "Yes":
        gui = MainWin(**config_info)
        gui()
