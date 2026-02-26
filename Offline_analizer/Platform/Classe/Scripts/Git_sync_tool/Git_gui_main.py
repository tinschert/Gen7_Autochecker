# -*- coding: utf-8 -*-
# @file Git_gui_main.py
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


import tkinter as tk
import shutil
import os,sys
import tkinter.messagebox
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import canoe_client_1
from threading import Thread
from Git_Clone import checkout_repo
import time
import rpyc
import wmi_client
from tkinter import ttk
import pythoncom
import subprocess


class MainWin:
    """ """
    def __init__(self):
        # determine the main window
        self.root = tk.Tk()
        self.root.title("GIT Sync Tool")
        self.root.geometry("1100x400")

        # declaring string variables
        self.git_branch_platform = tk.StringVar()
        self.platform_folder_path = tk.StringVar()
        self.git_branch_psa = tk.StringVar()
        self.git_branch_toyota = tk.StringVar()
        self.git_branch_ford = tk.StringVar()
        self.git_branch_od = tk.StringVar()
        self.git_branch_psa_dcross = tk.StringVar()
        self.psa_folder_path = tk.StringVar()
        self.toyota_folder_path = tk.StringVar()
        self.ford_folder_path = tk.StringVar()
        self.od_folder_path = tk.StringVar()
        self.psa_dcross_folder_path = tk.StringVar()
        self.commit_msg = tk.StringVar()
        self.test_unit_name = tk.StringVar()

        # datatype of menu text
        self.clicked_psa = tk.StringVar()
        self.clicked_toyota = tk.StringVar()
        self.clicked_ford = tk.StringVar()
        self.clicked_od = tk.StringVar()
        self.clicked_psa_dcross = tk.StringVar()
        self.clicked_connection = tk.StringVar()
        self.mf4path = r'\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\mf4_rename.exe'
        self.rel_path_rbs = r"\Platform\Classe\Scripts\Rbs_Scripts"
        self.mf4_rel_path = r"\Platform\Classe\Scripts\Control"

        # Dropdown menu options
        options = [
            "FE-C-005CP.lr.de.bosch.com (HIL02)",
            "FE-Z1R59.lr.de.bosch.com (HIL03)",
            "LR-C-0000C.lr.de.bosch.com (HIL04)",
            "WE-C-0003R.lr.de.bosch.com (HIL05)",
            "localhost (HIL)"
        ]
        
        options_type = [
            "Remote",
            "Local",
        ]

        # # initial menu text
        # self.clicked_psa.set("Select PSA HIL")
        # self.clicked_toyota.set("Select Toyota HIL")
        # self.clicked_ford.set("Select Ford HIL")
        # self.clicked_od.set("Select OD HIL")
        # self.clicked_connection.set("Remote")

        # Create Dropdown menu for HIL benches
        drop_psa = ttk.OptionMenu(self.root, self.clicked_psa, "Select PSA HIL", *options)
        drop_toyota = ttk.OptionMenu(self.root, self.clicked_toyota, "Select Toyota HIL", *options)
        drop_ford = ttk.OptionMenu(self.root, self.clicked_ford, "Select Ford HIL", *options)
        drop_od = ttk.OptionMenu(self.root, self.clicked_od, "Select OD HIL", *options)
        drop_psa_dcross = ttk.OptionMenu(self.root, self.clicked_psa_dcross, "Select PSA DCROSS HIL", *options)

        #Create Dropdown menu for execution type
        drop_connection = ttk.OptionMenu(self.root, self.clicked_connection, "Remote", *options_type)

        # creating a label for
        # name using widget Label
        hil_label = ttk.Label(self.root, text='HIL', font=('calibre', 12, 'bold'))

        # creating a label for Platform branch
        platform_label = tk.Label(self.root, text='Platform Branch', font=('calibre', 12, 'bold'))
        platform_entry_git = ttk.Entry(self.root, textvariable=self.git_branch_platform, font=('calibre', 10, 'normal'), width=30)
        platform_entry_git.insert(tk.END, "origin/Develop_ADAS_HIL_Platform")
        platform_entry_dir_path = ttk.Entry(self.root, textvariable=self.platform_folder_path, font=('calibre', 10, 'normal'), width=30)
        platform_entry_dir_path.insert(tk.END, r"D:\ADAS_Platform")

        # creating a label for PSA Branch
        psa_label = ttk.Label(self.root, text='PSA Branch', font=('calibre', 12, 'bold'))
        psa_entry = ttk.Entry(self.root, textvariable=self.git_branch_psa, font=('calibre', 10, 'normal'), width=30)
        psa_entry.insert(tk.END, "Git path")
        psa_entry_dir_path = ttk.Entry(self.root, textvariable=self.psa_folder_path, font=('calibre', 10, 'normal'), width=30)
        psa_entry_dir_path.insert(tk.END, "Customer local folder path")

        # creating a label for Toyota branch
        toyota_label = ttk.Label(self.root, text='Toyota Branch', font=('calibre', 12, 'bold'))
        toyota_entry = ttk.Entry(self.root, textvariable=self.git_branch_toyota, font=('calibre', 10, 'normal'), width=30)
        toyota_entry.insert(tk.END, "Git path")
        toyota_entry_dir_path = ttk.Entry(self.root, textvariable=self.toyota_folder_path, font=('calibre', 10, 'normal'), width=30)
        toyota_entry_dir_path.insert(tk.END, "Customer local folder path")

        # creating a label for Ford branch
        ford_label = ttk.Label(self.root, text='Ford Branch', font=('calibre', 12, 'bold'))
        ford_entry = ttk.Entry(self.root, textvariable=self.git_branch_ford, font=('calibre', 10, 'normal'), width=30)
        ford_entry.insert(tk.END, "Git path")
        ford_entry_dir_path = ttk.Entry(self.root, textvariable=self.ford_folder_path, font=('calibre', 10, 'normal'), width=30)
        ford_entry_dir_path.insert(tk.END, "Customer local folder path")

        # creating a label for OD branch
        od_label = ttk.Label(self.root, text='OD Branch', font=('calibre', 12, 'bold'))
        od_entry = ttk.Entry(self.root, textvariable=self.git_branch_od, font=('calibre', 10, 'normal'), width=30)
        od_entry.insert(tk.END, "Git path")
        od_entry_dir_path = ttk.Entry(self.root, textvariable=self.od_folder_path, font=('calibre', 10, 'normal'), width=30)
        od_entry_dir_path.insert(tk.END, "Customer local folder path")

        # creating a label for PSA Branch
        psa_dcross_label = ttk.Label(self.root, text='PSA DCROSS Branch', font=('calibre', 12, 'bold'))
        psa_dcross_entry = ttk.Entry(self.root, textvariable=self.git_branch_psa_dcross, font=('calibre', 10, 'normal'), width=30)
        psa_dcross_entry.insert(tk.END, "Git path")
        psa_dcross_entry_dir_path = ttk.Entry(self.root, textvariable=self.psa_dcross_folder_path, font=('calibre', 10, 'normal'), width=30)
        psa_dcross_entry_dir_path.insert(tk.END, "Customer local folder path")

        # creating a button using the widget
        # Button that will call the submit function
        style = ttk.Style()
        style.configure('TButton',font=('calibri', 12),foreground='green',)
        self.sub_btn = ttk.Button(self.root, text='Execute', command=lambda:Thread(target=self.submit).start(),style='TButton')

        commit_msg_label = ttk.Label(self.root, text='Commit Message', font=('calibre', 12, 'bold'))
        gui_commit_msg = ttk.Entry(self.root, textvariable=self.commit_msg, font=('calibre', 10, 'normal'), width=50)
        gui_commit_msg.insert(tk.END, "Enter Commit Message")

        test_unit_label = ttk.Label(self.root, text='Classe Test Unit', font=('calibre', 12, 'bold'))
        test_unit_msg = ttk.Entry(self.root, textvariable=self.test_unit_name, font=('calibre', 10, 'normal'), width=50)
        test_unit_msg.insert(tk.END, "Populate test unit")

        # placing the label and entry in
        # the required position using grid method
        hil_label.grid(row=0, column=1)
        drop_psa.grid(row=2, column=1, pady=5)
        drop_toyota.grid(row=3, column=1)
        drop_ford.grid(row=4, column=1, pady=5)
        drop_od.grid(row=5, column=1)
        drop_psa_dcross.grid(row=6, column=1)
        drop_connection.grid(row=7, column=0)
        platform_label.grid(row=1, column=0)
        platform_entry_git.grid(row=1, column=2, padx=10)
        platform_entry_dir_path.grid(row=1, column=3)
        psa_label.grid(row=2, column=0)
        psa_entry.grid(row=2, column=2)
        psa_entry_dir_path.grid(row=2, column=3, padx=20)
        toyota_label.grid(row=3, column=0)
        toyota_entry.grid(row=3, column=2)
        toyota_entry_dir_path.grid(row=3, column=3)
        ford_label.grid(row=4, column=0)
        ford_entry.grid(row=4, column=2)
        ford_entry_dir_path.grid(row=4, column=3)
        od_label.grid(row=5, column=0)
        od_entry.grid(row=5, column=2)
        od_entry_dir_path.grid(row=5, column=3)
        psa_dcross_label.grid(row=6, column=0)
        psa_dcross_entry.grid(row=6, column=2)
        psa_dcross_entry_dir_path.grid(row=6, column=3)
        commit_msg_label.grid(row=7, column=0)
        gui_commit_msg.grid(row=7, column=2,pady=5, ipadx=5, ipady=5, columnspan=2)
        test_unit_label.grid(row=8, column=0)
        test_unit_msg.grid(row=8, column=2, pady=5, ipadx=5, ipady=5, columnspan=2)
        self.sub_btn.grid(row=9, column=2,pady=10, ipadx=10, ipady=15)

    # Function for Execute button
    def submit(self):
        """ """
        self.sub_btn.config(state=tk.DISABLED)
        git_platform = self.git_branch_platform.get()
        git_psa = self.git_branch_psa.get()
        git_ford = self.git_branch_ford.get()
        git_toyota = self.git_branch_toyota.get()
        git_od = self.git_branch_od.get()
        git_psa_dcross = self.git_branch_psa_dcross.get()
        path_platform = self.platform_folder_path.get()
        path_psa = self.psa_folder_path.get()
        path_ford = self.ford_folder_path.get()
        path_toyota = self.toyota_folder_path.get()
        path_od = self.od_folder_path.get()
        path_psa_dcross = self.psa_dcross_folder_path.get()
        commit_message = self.commit_msg.get()
        projects_path = [path_psa, path_ford, path_toyota, path_od, path_psa_dcross]
        customer_tags = ["PSA", "FORD", "Toyota", "OD", "PSA DCROSS"]
        projects_branches = [git_psa, git_ford, git_toyota, git_od, git_psa_dcross]
        combined_project_branch = list(zip(customer_tags, projects_branches, projects_path))
        hil_psa = self.clicked_psa.get().split(" ")[0]
        hil_toyota = self.clicked_toyota.get().split(" ")[0]
        hil_ford = self.clicked_ford.get().split(" ")[0]
        hil_od = self.clicked_od.get().split(" ")[0]
        hil_psa_dcross = self.clicked_psa_dcross.get().split(" ")[0]
        test_unit = self.test_unit_name.get()

        logger.info(f"Platform branch to clone --> {git_platform}")
        logger.info(f"Platform path --> {path_platform}")

        for customer, project_branch, project_path in combined_project_branch:
            if project_branch == 'Git branch':
                branch = "not populated"
            else:
                branch = project_branch
            if project_path == 'Customer local folder path':
                path = "not populated"
            else:
                path = project_path

            logger.info(f"{customer} git branch --> {branch}")
            logger.info(f"{customer} repository path --> {path}")

        if self.clicked_connection.get() == "Local":
            checkout_repo(git_platform, path_platform)
            for target in projects_path:
                if target != 'Customer local folder path':
                    self.copy_platform(path_platform, target)
                    self.execute_rbs_scripts(target)
                    canoe_cfg = self.get_canoe_cfg(target)
                    self.run_canoe_test(canoe_cfg)
            self.sub_btn.config(state=tk.NORMAL)
        else:
            self.main_sequence("PSA", hil_psa, path_psa, git_psa, path_platform, git_platform, commit_message, test_unit)
            self.main_sequence("Toyota", hil_toyota, path_toyota, git_toyota, path_platform, git_platform, commit_message, test_unit)
            self.main_sequence("Ford", hil_ford, path_ford, git_ford, path_platform, git_platform, commit_message, test_unit)
            self.main_sequence("OD", hil_od, path_od, git_od, path_platform, git_platform, commit_message, test_unit)
            self.main_sequence("PSA DCROSS", hil_psa_dcross, path_psa_dcross, git_psa_dcross, path_platform, git_platform, commit_message, test_unit)
            self.sub_btn.config(state=tk.NORMAL)

    def main_sequence(self, customer, hil, target, git_project, path_platform, git_platform,message, test_unit):
        """
        

        Args:
          customer: 
          hil: 
          target: 
          git_project: 
          path_platform: 
          git_platform: 
          message: 
          test_unit: 

        Returns:

        """
        if "Select" not in hil and target != 'Customer local folder path':
            ''' Start remote server via WMI'''
            # x_server = wmi_client.RemoteConnection(hil)
            # settings = x_server.connect_to_host()
            # x_server.run_command('cmd.exe /k' + path_platform + r'\Platform\Classe\Scripts\Git_sync_tool\Start_server.bat', settings)
            # time.sleep(5)

            ''' Connecto to the remote python server'''
            try:
                c = rpyc.connect(hil, 18861, config={"allow_public_attrs": True})
                #c = rpyc.connect("localhost", 18861, config={"allow_public_attrs": True})
            except Exception as e:
                logger.error(f"Server is down.Please check if server is running on {hil} HIL")
                logger.error(f"Sever path --> D:\ADAS_Platform\Platform\Classe\Scripts\Git_sync_tool\Start_server.bat")
                raise e
            c._config['sync_request_timeout'] = None  # No timeout

            try:
                ''' Main sequence to execute'''
                logger.info(f"Start git sync for {git_platform}")
                c.root.exposed_clear_log(path_platform)
                c.root.exposed_redirect(sys.stdout)
                c.root.exposed_checkout_repo(git_platform, path_platform)
                #c.root.exposed_checkout_branch(git_project, target)
                c.root.exposed_read_log(path_platform)
                c.root.exposed_clear_log(path_platform)
                time.sleep(2)
                
                logger.info("Start copying of Platform and mf4_rename.Please wait!")
                c.root.exposed_copy_platform(path_platform, target)
                c.root.exposed_read_log(path_platform)
                time.sleep(2)

                logger.info("Start executing RBS scripts sequence")
                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_update_sysvartab(target)
                c.root.exposed_read_log(path_platform)

                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_create_nodes(target)
                c.root.exposed_read_log(path_platform)

                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_create_sysvar(target)
                c.root.exposed_read_log(path_platform)

                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_create_ininode(target)
                c.root.exposed_read_log(path_platform)

                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_update_ini(target)
                c.root.exposed_read_log(path_platform)

                c.root.exposed_clear_log(path_platform)
                c.root.exposed_execute_create_gw(target)
                c.root.exposed_read_log(path_platform)

                logger.info("Executing CANoe Integration tests.Please wait!")
                c.root.exposed_clear_log(path_platform)
                canoe_cfg = c.root.exposed_get_canoe_cfg(target)
                conf_full_path = target + "\\" + canoe_cfg
                test_status = c.root.exposed_run_canoe_test(conf_full_path, path_platform, test_unit)
                c.root.exposed_read_log(path_platform)
                if test_status == 1:
                    c.root.exposed_clear_log(path_platform)
                    c.root.exposed_commit_push(target,self.commit_msg)
                    c.root.exposed_read_log(path_platform)
                    tkinter.messagebox.showinfo("Integration tests", f"{customer} CanOE integration tests PASSED")
                elif test_status == 2:
                    tkinter.messagebox.showerror("Canoe",
                                                 f"CanOE is not started.Please check the exception info!")
                else:
                    tkinter.messagebox.showerror("Integration tests",
                                                 f"CanOE integration tests FAILED. Please check the report on {customer} HIL!")
            except Exception as e:
                logger.error(f"Execution stopped due to --> {e}")
            finally:
                time.sleep(5)  # Wait all IO operations to finish
                logger.info(f"Close client connection to {hil}")
                c.close()  # Close connection
                del c  # destroy the object
        else:
            logger.warning(f"{customer } HIL not selected or Customer project path is not populated")

    def copy_mf4(self, project_path):
        """
        

        Args:
          project_path: 

        Returns:

        """
        try:
            logger.info("Copy mf4_rename.exe to local repository")
            shutil.copy(self.mf4path, project_path)
        except PermissionError as e:
            logger.error(f"Permission denied to access mf4_rename.exe --> {e}")
            raise e
        except Exception as e:
            logger.error(f"Failed to copy mf4_rename.exe --> {e}")
            raise e

    def copy_platform(self, source, target):
        """
        

        Args:
          source: 
          target: 

        Returns:

        """
        if not os.path.isdir(source):
            raise Exception(f"Platform repository {source} does not exist")
        else:
            if target != '':
                if not os.path.isdir(target):
                    raise Exception(f"Customer branch repository path {target} does not exist")
                else:
                    try:
                        shutil.copytree(source, target,
                                        ignore=shutil.ignore_patterns('CustomerPrj', '*.stcfg', '*.cfg', '.git', '.idea', '.run'),
                                        dirs_exist_ok=True)
                        logger.info(f"Latest Platform copied from {source} to {target}")
                    except Exception as e:
                        logger.error(f"Exception raised during copying from from {source} to {target} --> {e}")
                        raise e
                    self.copy_mf4(target + self.mf4_rel_path)

    def execute_rbs_scripts(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        if script_path != '':
            scripts_abs_path = script_path + self.rel_path_rbs
            logger.info(f"Run RBS Scripts from {scripts_abs_path}")
            sys.path.append(scripts_abs_path)
            import update_sysvartab
            import create_sysvar
            import create_nodes
            import create_ininode
            import update_ini
            import create_gw
            update_sysvartab.external_call()
            create_nodes.external_call()
            create_sysvar.external_call()
            create_ininode.external_call()
            update_ini.external_call()
            create_gw.external_call()

    def run_canoe_test(self, cfg_file):
        """
        

        Args:
          cfg_file: 

        Returns:

        """
        start_canoe = time.time()
        logger.info("Starting CANoe via COM interface")
        canoeClient = canoe_client_1.CANoeClient()
        canoeClient.openConfiguration(cfg_file)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        canoeClient.startMeasurement()
        test_status = canoeClient.executeTestsInTestConfiguration()
        canoeClient.stopMeasurement()
        canoeClient = None
        if test_status == 1:
            tkinter.messagebox.showinfo("Integration tests", "CanOE integration tests PASSED")
        else:
            tkinter.messagebox.showerror("Integration tests", "CanOE integration tests FAILED. Please check the report!")
            
    def run_canoe_test_scheduler(self, cfg_file, path_platform):
        """
        

        Args:
          cfg_file: 
          path_platform: 

        Returns:

        """
        p = subprocess.Popen(
            ["powershell.exe", path_platform + "\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
            stdout=sys.stdout)
        p.communicate()
        pythoncom.CoInitialize()
        start_canoe = time.time()
        logger.info("Starting CANoe via COM interface")
        canoeClient = canoe_client_1.CANoeClient()
        try:
            canoeClient.openConfiguration(cfg_file)
            canoe_started = time.time()
            logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
            canoeClient.startMeasurement()
            test_status = canoeClient.executeTestsInTestConfiguration()
            return test_status
        except Exception as e:
            logger.error(f"Stop at exception --> {e}")
            return 0
        finally:
            canoeClient.stopMeasurement()
            canoeClient.quitCanoe(False)
            canoeClient = None

    def get_canoe_cfg(self, target_path):
        """
        

        Args:
          target_path: 

        Returns:

        """
        for (dirpath, dirnames, filenames) in os.walk(target_path):
            for file in filenames:
                if ".cfg" in file:
                    logger.info(f"CANoe configuration path --> {target_path}\\{file}")
                    return file

    def __call__(self):
        self.root.mainloop()


if __name__ == "__main__":
    APP = MainWin()
    APP()
