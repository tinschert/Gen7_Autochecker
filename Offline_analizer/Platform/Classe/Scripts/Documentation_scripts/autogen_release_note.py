# -*- coding: utf-8 -*-
# @file autogen_release_note.py
# @author ADAS_HIL_TEAM
# @date 08-22-2023

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
from tkinter import ttk
from threading import Thread
import tkinter.messagebox
import sys,os

import subprocess
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
try:
    from Control.logging_config import logger
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
    from logging_config import logger

script_path = os.path.dirname(os.path.abspath(__file__))

README_PATH = script_path + r"\..\..\..\README.md"


REPO_PATHS = {"ADAS_HIL": script_path + r"\..\..\..\..",
              "adas_sim": script_path + r"\..\..\..\..\adas_sim",
              "Restbus": script_path + r"\..\..\..\..\CustomerPrj\Restbus",
              "Platform": script_path + r"\..\..\..",
              "Carmaker": script_path + r"\..\..\..\Carmaker",
              "Rbs_Scripts": script_path + r"\..\Rbs_Scripts"
              }


class releaseNoteAutoGeneration:
    """ Generate relese note for given repo using PR titles"""
    def __init__(self):
        # determine the main window
        self.root = tk.Tk()
        self.root.title("AutoGen Release Note")
        self.root.geometry("900x700+400+60")

        self.customer=self.get_customer(REPO_PATHS["ADAS_HIL"])
        # declaring string variables
        self.source_branch = tk.StringVar()
        self.destination_branch = tk.StringVar()

        custom_font = ("Helvetica", 12)

        #heading label
        tool_compare_label = ttk.Label(self.root, text='RELEASE NOTE AUTOGEN', font=('calibre', 15, 'bold'))
        tool_compare_label.place(x=260,y=15)

        # options
        options_label = ttk.Label(self.root, text='Select Required Repos:', font=('calibre', 13, 'bold'))
        options_label.grid(column=0, row=1, padx=(100, 10), pady=(95, 0), sticky="w")
        if self.customer=="OD":
            self.adas_hil = tk.IntVar()
            self.adas_hil_checkbox = tk.Checkbutton(self.root, text='ADAS_HIL', variable=self.adas_hil, font=custom_font,onvalue=1,
                                                    offvalue=0, anchor="w")
            self.adas_hil_checkbox.grid(column=1, row=1, padx=(20,0), pady=(95,0), sticky="w")
            self.adas_hil.set(1)

            self.adas_sim = tk.IntVar()
            self.adas_sim_checkbox = tk.Checkbutton(self.root, text='adas_sim', variable=self.adas_sim, font=custom_font,onvalue=1,
                                                    offvalue=0, anchor="w")
            self.adas_sim_checkbox.grid(column=1, row=2,padx=(20,0), sticky="WE")

            # self.restbus = tk.IntVar()
            # self.restbus_checkbox = tk.Checkbutton(self.root, text='Restbus', variable=self.restbus,font=custom_font, onvalue=1, offvalue=0,
            #                                        anchor="w")
            # self.restbus_checkbox.grid(column=1, row=3,padx=(20,0), sticky="WE")

            self.platform = tk.IntVar()
            self.platform_checkbox = tk.Checkbutton(self.root, text='Platform', variable=self.platform,font=custom_font, onvalue=1,
                                                    offvalue=0, anchor="w")
            self.platform_checkbox.grid(column=1, row=3, padx=(20,0), sticky="WE")

            self.carmaker = tk.IntVar()
            self.carmaker_checkbox = tk.Checkbutton(self.root, text='Carmaker', variable=self.carmaker,
                                                    font=custom_font, onvalue=1,
                                                    offvalue=0, anchor="w")
            self.carmaker_checkbox.grid(column=1, row=4, padx=(20, 0), sticky="WE")

            self.rbs_scripts = tk.IntVar()
            self.rbs_scripts_checkbox = tk.Checkbutton(self.root, text='Rbs_Scripts', variable=self.rbs_scripts,
                                                    font=custom_font, onvalue=1,
                                                    offvalue=0, anchor="w")
            self.rbs_scripts_checkbox.grid(column=1, row=5, padx=(20, 0), sticky="WE")


        elif self.customer=="FORD":
            self.adas_hil = tk.IntVar()
            self.adas_hil_checkbox = tk.Checkbutton(self.root, text='ADAS_HIL', variable=self.adas_hil,
                                                    font=custom_font, onvalue=1,
                                                    offvalue=0, anchor="w")
            self.adas_hil_checkbox.grid(column=1, row=1, padx=(20, 0), pady=(95, 0), sticky="w")
            # self.adas_hil.set(1)
            #
            # self.adas_sim = tk.IntVar()
            # self.adas_sim_checkbox = tk.Checkbutton(self.root, text='adas_sim', variable=self.adas_sim,
            #                                         font=custom_font, onvalue=1,
            #                                         offvalue=0, anchor="w")
            # self.adas_sim_checkbox.grid(column=1, row=2, padx=(20, 0), sticky="WE")

            self.restbus = tk.IntVar()
            self.restbus_checkbox = tk.Checkbutton(self.root, text='Restbus', variable=self.restbus, font=custom_font,
                                                   onvalue=1, offvalue=0,
                                                   anchor="w")
            self.restbus_checkbox.grid(column=1, row=2, padx=(20, 0), sticky="WE")

            self.platform = tk.IntVar()
            self.platform_checkbox = tk.Checkbutton(self.root, text='Platform', variable=self.platform,
                                                    font=custom_font, onvalue=1,
                                                    offvalue=0, anchor="w")
            self.platform_checkbox.grid(column=1, row=3, padx=(20, 0), sticky="WE")



        # Create the info icon label using Unicode character
        info_icon = f'({chr(0x2139)})'
        info_label_src = tk.Label(self.root, text=info_icon, font=('calibre', 12, 'normal'), fg='#007AFF')
        info_label_dst = tk.Label(self.root, text=info_icon, font=('calibre', 12, 'normal'), fg='#007AFF')
        

        src_branch_input_display_text = """ branch examples:
	 Develop_ADAS_HIL_Platform 
	 origin/Develop_ADAS_HIL_Platform 
	 feature/ADASXIL-0000_branch_name 
	 origin/feature/ADASXIL-0000_branch_name 
	 release/ADAS_HIL_Platform_0.0.0 
	
 commit_id examples:
	 4edef14b 
	 29ea5d248bf2cff251dacd9a504e75ef5b42263f """
        dst_branch_input_display_text = src_branch_input_display_text

        # Bind the info icon to show the tooltip
        info_label_src.bind("<Enter>", lambda event: self.show_tooltip(event, src_branch_input_display_text))
        info_label_src.bind("<Leave>", self.hide_tooltip)
        info_label_dst.bind("<Enter>", lambda event: self.show_tooltip(event, dst_branch_input_display_text))
        info_label_dst.bind("<Leave>", self.hide_tooltip)

        source_branch_label = ttk.Label(self.root, text=r'Latest Branch\Commit_ID:', font=('calibre', 13, 'bold'))
        source_branch_entry = ttk.Entry(self.root, textvariable=self.source_branch, font=('calibre', 10, 'normal'), width=50)
        

        destination_branch_label = ttk.Label(self.root, text=r'Previous Branch\Commit_ID:', font=('calibre', 13, 'bold'))
        destination_branch_entry = ttk.Entry(self.root, textvariable=self.destination_branch, font=('calibre', 10, 'normal'), width=50)

        source_branch_label.grid(column=0, row=6, padx=(100,10),pady=(40,20),sticky="w")
        source_branch_entry.grid(column=1, row=6, padx=(20,0),pady=(40,20), ipady=7)
        info_label_src.grid(column=2, row=6, pady=(20,0))

        destination_branch_label.grid(column=0, row=8, padx=(100,10),pady=(20,20),sticky="w")
        destination_branch_entry.grid(column=1, row=8, padx=(20,0),pady=(20,20), ipady=7)
        info_label_dst.grid(column=2, row=8, pady=(0,0))


        # source_branch_label.place(x=80,y=84)
        # source_branch_entry.place(x=280,y=80,height=30)
        #
        # destination_branch_label.place(x=80,y=73*1.92)
        # destination_branch_entry.place(x=280,y=73*1.9,height=30)

        #button
        style = ttk.Style()
        style.configure('TButton', font=('calibri', 16), foreground='green', )
        self.sub_btn = ttk.Button(self.root, text='Submit', command=lambda: Thread(target=self.submit).start(),style='TButton')
        self.sub_btn.grid(column=1, row=9, padx=(20,10),pady=(20,20), sticky="W")


        #notes
        note1 = ttk.Label(self.root, text='Note: The generated info will be appended to README.md', font=('calibre', 12))
        note2 = ttk.Label(self.root, text='Note: If branch name is different in each repo, then generate one repo at a time.', font=('calibre', 12))
        note3 = ttk.Label(self.root, text='Note: Latest Branch is PR_FROM_branch or New_release_branch.\n          Previous branch is PR_TO_branch or Old_release_branch.\n          origin/ is optional in branch input.', font=('calibre', 12))

        note1.place(x=100,y=500)
        note2.place(x=100,y=540)
        note3.place(x=100,y=580)


    def submit(self):
        """ main function for generation"""
        try:
            self.disable_btns()
            logger.info("-------------Release Note Autogen Start----------------")
            source_branch_name = str(self.source_branch.get()).strip()
            destination_branch_name = str(self.destination_branch.get()).strip()
            if (source_branch_name=='') or (destination_branch_name==''):
                tkinter.messagebox.showerror("Empty Input", f"Enter source and destination branch names/commit_id")
                self.enable_btns()
                logger.error("Enter source and destination branch names/commit_id")
                return
            if (not source_branch_name.startswith("origin/")) and not(self.is_commit_id(source_branch_name)):
                source_branch_name = "origin/" + source_branch_name
            if (not destination_branch_name.startswith("origin/")) and not(self.is_commit_id(destination_branch_name)):
                destination_branch_name = "origin/" + destination_branch_name
            
            logger.info(f"Latest Branch/commit_id -> {source_branch_name}")
            logger.info(f"Previous Branch/commit_id -> {destination_branch_name}")

            required_repos = []
            if self.customer=="OD":
                if self.adas_hil.get():
                    required_repos.append("ADAS_HIL")
                if self.adas_sim.get():
                    required_repos.append("adas_sim")
                # if self.restbus.get():
                #     required_repos.append("Restbus")
                if self.platform.get():
                    required_repos.append("Platform")
                if self.carmaker.get():
                    required_repos.append("Carmaker")
                if self.rbs_scripts.get():
                    required_repos.append("Rbs_Scripts")
            elif self.customer=="FORD":
                if self.adas_hil.get():
                    required_repos.append("ADAS_HIL")
                # if self.adas_sim.get():
                #     required_repos.append("adas_sim")
                if self.restbus.get():
                    required_repos.append("Restbus")
                if self.platform.get():
                    required_repos.append("Platform")

            if required_repos==[]:
                tkinter.messagebox.showerror("Empty Input", f"Select the required repos (atleast one)")
                self.enable_btns()
                raise Exception("Select the required repos (atleast one)")
            errorrs = []
            for repo in required_repos:
                logger.info(f"-------------------------Extracting Info for {repo} repo---------------------------")
                output, errors = self.run_git_log_command(source_branch_name, destination_branch_name, REPO_PATHS[repo])

                if "fatal: ambiguous argument" in errors:
                    errorrs.append(repo)
                    logger.error(f"Check given branch names or commit_id in Repo -> {repo}")
                    continue
                if output:
                    commit_pattern = r'commit [a-fA-F0-9]{40}'
                    ticket_patterns = r"PJSYM-\d+|OD-\d+|ADASXIL-\d+|SOSFORDDAT-\d+"


                    commits = re.split(commit_pattern, output.strip())

                    #print--------
                    for commit in commits:
                        logger.info("-"*40)
                        logger.info(commit)
                    #print--------

                    commits = [commit for commit in commits if "pull request #" in commit.lower()]
                    logger.info(f"Found {len(commits)} Pull requests")
                    result_data = []
                    for commit in commits:
                        tickets = re.findall(ticket_patterns, commit)
                        ticket_list = list(set(tickets))
                        if len(ticket_list)==0:
                            ticket_list = []

                        pr_title = ""
                        for line in commit.split("\n"):
                            if "pull request #" in line.lower():
                                pr_title = line.split(":")[-1].strip()
                                break

                        if ticket_list == []:
                            temp = "\n- " + pr_title
                        else:
                            temp = "\n" + f"- {ticket_list}\t-> " + pr_title

                        result_data.append(temp)

                
                    with open(README_PATH, "a") as file:
                        heading = ("-"*15)+'# '+repo+' #'+("-"*(115-len(repo)))
                        result_data.insert(0,"\n\n"+ heading + '\n')
                        result_data.append('\n' + "-"*len(heading))
                        file.writelines(result_data)
                        file.close()
                    logger.info(f"=================Readme file updated successfully for -> {repo}===================")

                    if errors:
                        self.enable_btns()
                        logger.error(f"Git command returned error -> {errors}")
                        raise Exception(f"Git command returned error -> {errors}")
                else:
                    logger.warning(f"NO COMMITS FOUND for ->{repo}")


            self.enable_btns()
            if errorrs:
                tkinter.messagebox.showerror("Results", f"Error occured for -> {errorrs}")
            else:
                tkinter.messagebox.showinfo("Results", f"Successfully updated release note")
            return True

        except Exception as e:
            tkinter.messagebox.showerror("Error occured", f"Please check console for more details")
            logger.error(f"Error occured -> {e}")
            logger.error("Possible cause for the error:\n1. Repo not found for current project.\n2. Given branch not found in given repo.")
            return
        

    def run_git_log_command(self, source_branch, destination_branch, cwd):
        """
        fetch the from git, runs git log command with givenbranches then returns output and errors

        Args:
          source_branch (str): source branch name
          destination_branch (str): dest branch name
          cwd (str): path of current working dir to run the git command

        Returns:
            1.(str/None) Output of the  git log command, will be None if error occurs
            2.(str) Error if any
        """
        try:
            # Format the git log command with the given branches
            git_command = f"git log {destination_branch}..{source_branch}"

            #fetch
            logger.info("Fetching latest changes -> git fetch")
            fetch = subprocess.run("git fetch", cwd=cwd,shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            fetch_error = fetch.stderr.strip()
            if fetch_error:
                logger.warning(f"Error while fetching -> {fetch_error}")
            logger.info("Fetching Successfull")
            # Run the Git log command and capture the output and errors
            logger.info(f"Executing compare command ->  {git_command}")
            result = subprocess.run(git_command, cwd=cwd,shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Get the output and error messages
            output = result.stdout.strip()
            errors = result.stderr.strip()
            return output, errors
        
        except subprocess.CalledProcessError as e:
            return None, e.stderr.strip()
        
        except Exception as e:
            logger.error(f"Error occured in run_git_log_command -> {e}")
            raise Exception(e)
        
    def is_commit_id(self, string):
        """
        Check if the given string is a valid commit ID.
        A valid commit ID is a hexadecimal string with a length between 7 and 40 characters.
        Args:
            string (str): The string to check.
        Returns:
            bool: True if the string is a valid commit ID, False otherwise.
        """
        # Regex for a 7 to 40-character hexadecimal string
        commit_id_pattern = r'^[a-f0-9]{7,40}$'
        
        return bool(re.match(commit_id_pattern, string))
    
    def show_tooltip(self, event, display_text):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
        label = tk.Label(self.tooltip, text=display_text, background="#b3ffec", relief="solid", borderwidth=1, anchor="w", justify="left")
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def get_customer(self, path):
        """
        get customer name from canoe cfg file name

        Args:
          path (str): path to the main folder where ,cfg is present

        Returns:
            (str): customer name
        """
        for (dirpath, dirnames, filenames) in os.walk(path):
            for file in filenames:
                if file.endswith(".cfg"):
                    return file.split(".")[0].split("_")[1]

    def enable_btns(self):
        """ enables buttons"""
        self.sub_btn.config(state=tk.NORMAL)
    def disable_btns(self):
        """ disbles buttons"""
        self.sub_btn.config(state=tk.DISABLED)
    def __call__(self):
        self.root.mainloop()



if __name__ == "__main__":
    gui = releaseNoteAutoGeneration()
    gui()