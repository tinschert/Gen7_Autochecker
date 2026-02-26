# -*- coding: utf-8 -*-
# @file GUI_compareTrace.py
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
from tkinter import ttk
from threading import Thread
import tkinter.messagebox
from compare_trace import compareTrace, extractFiles, manualCompare
import sys,os
from os import path,mkdir
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger

class guiWin:
    """ """
    def __init__(self):
        # determine the main window
        self.root = tk.Tk()
        self.root.title("Compare Trace")
        self.root.geometry("900x470+500+100")

        self.files_loaded = False
        self.hil_mf4 = ""
        self.veh_mf4 = ""

        self.new_hil_mdf = ""
        self.new_veh_mdf = ""
        self.hil_signms = ""
        self.hil_trace_sig_names = ""
        self.com_sig = ""
        self.hil_data = {}
        self.veh_data = {}




        # declaring string variables
        self.hil_trace_file = tk.StringVar()
        self.veh_trace_file = tk.StringVar()
        self.result_file = tk.StringVar()
        self.start_time = tk.StringVar()
        self.end_time = tk.StringVar()

        self.msg_name = tk.StringVar()
        self.sig_name = tk.StringVar()

        #heading label
        tool_compare_label = ttk.Label(self.root, text='Tool Compare', font=('calibre', 14, 'bold'))
        manual_compare_label = ttk.Label(self.root, text='Manual Compare', font=('calibre', 14, 'bold'))

        #Note label
        note_label = ttk.Label(self.root, text='Note: Both MF4 files should be Signal logged', font=('calibre', 11))

        #label for file paths
        hil_trace_label = ttk.Label(self.root, text='HIL Trace File:', font=('calibre', 12, 'bold'))
        hil_trace_entry = ttk.Entry(self.root, textvariable=self.hil_trace_file, font=('calibre', 10, 'normal'), width=30)
        #hil_trace_entry.insert(tk.END, "hil_sig_logged.mf4")

        veh_trace_label = ttk.Label(self.root, text='Vehicle Trace File:', font=('calibre', 12, 'bold'))
        veh_trace_entry = ttk.Entry(self.root, textvariable=self.veh_trace_file, font=('calibre', 10, 'normal'), width=30)
        #veh_trace_entry.insert(tk.END, "vehicle_sig_logged.mf4")

        start_time_label = ttk.Label(self.root, text='Enter Start time:', font=('calibre', 12, 'bold'))
        start_time_entry = ttk.Entry(self.root, textvariable=self.start_time, font=('calibre', 10, 'normal'),width=30)

        end_time_label = ttk.Label(self.root, text='Enter End time:', font=('calibre', 12, 'bold'))
        end_time_entry = ttk.Entry(self.root, textvariable=self.end_time, font=('calibre', 10, 'normal'), width=30)

        msg_label = ttk.Label(self.root, text='Message name:', font=('calibre', 11, 'bold'))
        msg_entry = ttk.Entry(self.root, textvariable=self.msg_name, font=('calibre', 10, 'normal'),width=25)
        #msg_entry.insert(tk.END, "")

        sig_label = ttk.Label(self.root, text='Signal name:', font=('calibre', 11, 'bold'))
        sig_entry = ttk.Entry(self.root, textvariable=self.sig_name, font=('calibre', 10, 'normal'), width=25)
        #sig_entry.insert(tk.END, "")

        tool_compare_label.place(x=160,y=15)
        manual_compare_label.place(x=650,y=15)

        hil_trace_label.place(x=80,y=70)
        hil_trace_entry.place(x=240,y=70,height=30)

        veh_trace_label.place(x=80,y=70*1.8)
        veh_trace_entry.place(x=240,y=70*1.8,height=30)

        start_time_label.place(x=80,y=70*2.6)
        start_time_entry.place(x=240,y=70*2.6,height=30)

        end_time_label.place(x=80, y=70*3.4)
        end_time_entry.place(x=240, y=70*3.4,height=30)

        msg_label.place(x=570, y=70)
        msg_entry.place(x=700, y=70,height=30)

        sig_label.place(x=570, y=70 * 1.65)
        sig_entry.place(x=700, y=70 * 1.6,height=30)

        note_label.place(x=80, y=70*5.6)

        #button
        style = ttk.Style()
        style.configure('TButton', font=('calibri', 16), foreground='green', )
        self.sub_btn = ttk.Button(self.root, text='Compare', command=lambda: Thread(target=self.compare).start(),style='TButton')
        self.sub_btn.place(x=240,y=70*4.4)

        self.sub_btn2 = ttk.Button(self.root, text='Manual', command=lambda: Thread(target=self.manaul).start(),style='TButton')
        self.sub_btn2.place(x=700, y=70*2.4)

        if not(path.exists("Manual_results")):
            mkdir("Manual_results")
        if not(path.exists("Tool_results")):
            mkdir("Tool_results")

    def compare(self):
        """ """
        self.disable_btns()
        interval = [str(self.start_time.get()).strip(), str(self.end_time.get()).strip()]
        if interval==["",""]:
            logger.error(f"Time fields are empty")
            tkinter.messagebox.showerror("Empty Input", f"Time Input fields are empty")
            self.enable_btns()
            raise Exception("Time Input fields are empty")

        try:
            if not(self.files_loaded):
                hil_file = str(self.hil_trace_file.get())
                veh_file = str(self.veh_trace_file.get())
                if not (hil_file.strip()) or not (veh_file.strip()):
                    logger.error(f"File name fields are empty")
                    tkinter.messagebox.showerror("Empty Input", f"File name input fields are empty")
                    self.enable_btns()
                    raise Exception("File name input fields are empty")
                self.hil_data, self.veh_data = extractFiles(hil_file, veh_file)
                self.files_loaded = True

            file_name = compareTrace(self.hil_data, self.veh_data, [float(interval[0]),float(interval[1])])
            tkinter.messagebox.showinfo("Results", f"Compare Successfull ->\n{file_name}")
            self.enable_btns()
        except Exception as e:
            logger.error(f"Error occured -> {e}")
            tkinter.messagebox.showerror("ERROR", f"ERROR occured while processing")


    def manaul(self):
        """ """
        self.disable_btns()
        msg_input=str(self.msg_name.get()).strip()
        sig_input = str(self.sig_name.get()).strip()
        if not(msg_input) or not(sig_input):
            logger.error(f"Msg name or signal name fields are empty")
            tkinter.messagebox.showerror("Empty Input", f"Msg name or signal name fields are empty")
            self.enable_btns()
            raise Exception("Msg name or signal name fields are empty")
        try:
            if not (self.files_loaded):
                hil_file = str(self.hil_trace_file.get())
                veh_file = str(self.veh_trace_file.get())
                if not (hil_file.strip()) or not (veh_file.strip()):
                    logger.error(f"File name fields are empty")
                    tkinter.messagebox.showerror("Empty Input", f"File name input fields are empty")
                    self.enable_btns()
                    raise Exception("File name input fields are empty")
                self.hil_data, self.veh_data = extractFiles(hil_file, veh_file)
                self.files_loaded = True

            file_name = manualCompare(self.hil_data,self.veh_data,msg_input,sig_input)
            tkinter.messagebox.showinfo("Results", f"Compare Successfull ->\n{file_name}")
            self.enable_btns()
        except:
            tkinter.messagebox.showerror("ERROR", f"ERROR occured while processing")

    def enable_btns(self):
        """ """
        self.sub_btn.config(state=tk.NORMAL)
        self.sub_btn2.config(state=tk.NORMAL)
    def disable_btns(self):
        """ """
        self.sub_btn.config(state=tk.DISABLED)
        self.sub_btn2.config(state=tk.DISABLED)
    def __call__(self):
        self.root.mainloop()



if __name__ == "__main__":
    gui = guiWin()
    gui()