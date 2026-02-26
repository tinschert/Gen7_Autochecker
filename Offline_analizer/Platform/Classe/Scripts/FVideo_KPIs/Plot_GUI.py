# -*- coding: utf-8 -*-
# @file Plot_GUI.py
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
from tkinter import ttk,filedialog
from easygui import fileopenbox
from threading import Thread
import tkinter.messagebox
import sys,os
from os import path,mkdir

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from fvideo_kpi import parseTraceGUI

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger




class PlotGraph():
    """ """
    def __init__(self, master, plot_data):
        self.master = master
        self.plot_data = plot_data
        self.colors = ["green", "purple", "yellow", "orange", "brown", "blue"]
        self.cursor_paused = False

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.pack()
        
        
        self.global_annotation_label = {}
        self.global_annotations = {}
        
        

        self.unit=""
        count = 0
        for sig, data in self.plot_data.items():
            self.ax.plot(data[0], data[1], label=sig, color=self.colors[count], marker='.')
            if len(data)==3 and data[2].strip() != "":
                self.unit = data[2]
            count+=1

        plt.xlabel("Time (s)")
        plt.ylabel(self.unit)

        self.vertical_line = self.ax.axvline(x=data[0][0], color='red', linestyle='-', linewidth=0.7)
        
        
        for sig in self.plot_data.keys():
            self.global_annotations[sig] = tk.StringVar()
            self.global_annotation_label[sig] = tk.Label(self.master, textvariable=self.global_annotations[sig])
            self.global_annotation_label[sig].pack()
            
        self.ax.legend()
        
        self.canvas.mpl_connect("motion_notify_event", self.cursor_moved)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)


    def find_nearest_index(self, array, value):
        """
        

        Args:
          array: 
          value: 

        Returns:

        """
        absolute_diff = np.abs(array - value)
        nearest_index = np.argmin(absolute_diff)

        if array[nearest_index]>value:
            return nearest_index-1

        return nearest_index

    def cursor_moved(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        #global x
        if (event.xdata is None) or (self.cursor_paused):
            return

        x = event.xdata
        self.vertical_line.set_xdata(x)

        for sig, data in self.plot_data.items():
            if (x >= min(data[0])) and (x <= max(data[0])):
                nearest_x_index = self.find_nearest_index(data[0], x)
                nearest_timestamp = data[0][nearest_x_index]
                if (x - nearest_timestamp)>0.075:
                    self.global_annotations[sig].set(f'{sig} = -')
                else:
                    self.global_annotations[sig].set(f'{sig} = {round(data[1][nearest_x_index], 3)}')
            else:
                self.global_annotations[sig].set(f'{sig} = -')

        self.canvas.draw_idle()

    def on_button_press(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        if event.button == 3:
            self.cursor_paused = not(self.cursor_paused)


    

class GraphWindow(tk.Toplevel):
    """ """
    def __init__(self, root, title, plot_data):
        super().__init__(root)
        self.root = root
        self.title(title)
        self.graph_gui = PlotGraph(self, plot_data)



class guiWin:
    """ """
    def __init__(self):

        self.graph_buttons = {}
        self.gt_objs = ['object0','object1','object2']
        self.camera_objs = ["VFC_Obj00A", "VFC_Obj01A", "VFC_Obj02A"]
        self.radar_messages = ["RFC_Loc000", "RFC_Loc001"]

        self.groundTruths = ['dxN', 'dyN', 'vxN', 'vyN', 'axN', 'ayN']
        self.cameraSigs = ['_Dx', '_Dy', '_Vx', '_Vy', '_Ax', '_Ay', '_Type','_VisibleView','_Reliability','_Height', '_Length', '_Width', '_HeadingAngle', '_ScaleChange', '_TypeProb']
        self.radarSigs = ['_RadialDistance', '_RadialVelocity']

        self.root = tk.Tk()
        self.root.title("FV_TE_KPI_ANALYSIS")
        self.root.geometry("900x550+500+100")

        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 14, "bold"),padding=[25, 5])

        self.heading_label = ttk.Label(self.root, text="FVideo KPI Analysis", font=("Arial", 20))
        self.heading_label.pack(side=tk.TOP,pady=30)

        self.notebook = ttk.Notebook(self.root)
        
        # Create the three tabs
        self.objects_tab = ttk.Frame(self.notebook)
        self.lanes_tab = ttk.Frame(self.notebook)
        self.traffic_tab = ttk.Frame(self.notebook)

        
        self.notebook.add(self.objects_tab, text="Objects")
        self.notebook.add(self.lanes_tab, text="Lanes")
        self.notebook.add(self.traffic_tab, text="Traffic Signs")

        
        self.notebook.pack(fill=tk.BOTH, expand=True)


        #OBJECTS
        self.obj_frame = ttk.Frame(self.objects_tab)
        self.obj_frame.pack(pady=15)

        self.file_label = ttk.Label(self.obj_frame, text="Select Measurement Files:*  ", font=("Arial", 14), justify='left')
        self.file_label.grid(row=2, column=1,pady=20,sticky='w')

        self.file_entry = ttk.Entry(self.obj_frame, font=("Arial", 11), justify='left',width=29)
        self.file_entry.grid(row = 2, column=2,padx=2,pady=20,ipadx=60,ipady=4.2,sticky='w',columnspan=2)

        self.browse_button = ttk.Button(self.obj_frame, text="Browse Files",command=self.browse_files)
        self.browse_button.grid(row = 2, column=4,sticky='w')


        self.gt_label = ttk.Label(self.obj_frame, text="Select CM Ground Truth:", font=("Arial", 14), justify='left')
        self.gt_label.grid(row = 4, column=1,pady=20,sticky='w')


        self.cm_gts_namespace = tk.StringVar()
        self.drop_down_namespace = ttk.Combobox(self.obj_frame, textvariable=self.cm_gts_namespace, font=("Arial",11), justify='left',width=11)
        self.drop_down_namespace['values'] = self.gt_objs
        self.drop_down_namespace.grid(row = 4, column=2, pady=20,ipady=3.8,  sticky='w')
        #self.drop_down_namespace.bind('<<ComboboxSelected>>',self.updateGT_ComboBox)     #uncomment when gt names are different for each object

        self.cm_gts = tk.StringVar()
        self.drop_down = ttk.Combobox(self.obj_frame, textvariable=self.cm_gts, font=("Arial", 11), justify='left', width = 28)
        self.drop_down['values'] = self.groundTruths  
        self.drop_down.grid(row = 4, column=3, padx=3,pady=20,sticky='w',ipady=3.8)




        self.cam_label = ttk.Label(self.obj_frame, text="Select Camera Signals:*", font=("Arial", 14), justify='left')
        self.cam_label.grid(row = 6, column=1, pady=20,sticky='w')


        self.camera_sigs_namespace = tk.StringVar()
        self.drop_down_cam_namespace = ttk.Combobox(self.obj_frame, textvariable=self.camera_sigs_namespace, font=("Arial", 11), justify='left',width=11)
        self.drop_down_cam_namespace['values'] = self.camera_objs
        self.drop_down_cam_namespace.grid(row = 6, column=2,pady=20,ipady=3.8, sticky='w')
        self.drop_down_cam_namespace.bind('<<ComboboxSelected>>',self.updateCam_ComboBox)

        self.camera_sigs = tk.StringVar()
        self.drop_down_cam = ttk.Combobox(self.obj_frame, textvariable=self.camera_sigs, font=("Arial", 11), justify='left', width = 28)
        #self.drop_down_cam['values'] = self.camera_sigs_list
        self.drop_down_cam.grid(row = 6, column=3, padx=3,pady=20,sticky='w',ipady=3.8)




        self.rad_label = ttk.Label(self.obj_frame, text="Select Radar Signals:", font=("Arial", 14), justify='left')
        self.rad_label.grid(row = 8, column=1, pady=20,sticky='w')


        self.rad_sigs_namespace = tk.StringVar()
        self.drop_down_rad_namespace = ttk.Combobox(self.obj_frame, textvariable=self.rad_sigs_namespace, font=("Arial", 11), justify='left',width=11)
        self.drop_down_rad_namespace['values'] = self.radar_messages
        self.drop_down_rad_namespace.grid(row = 8, column=2,pady=20,ipady=3.8, sticky='w')
        self.drop_down_rad_namespace.bind('<<ComboboxSelected>>',self.updateRad_ComboBox)

        self.radar_sigs = tk.StringVar()
        self.drop_down_rad = ttk.Combobox(self.obj_frame, textvariable=self.radar_sigs, font=("Arial", 11), justify='left', width = 28)
        #self.drop_down_rad['values'] = self.camera_sigs_list
        self.drop_down_rad.grid(row = 8, column=3, padx=3,pady=20,sticky='w',ipady=3.8)
        


        

        
        self.sub_btn = ttk.Button(self.obj_frame, text='Submit', command= self.Submit)
        self.sub_btn.grid(row = 10, column=2,pady=20,sticky='w', ipadx=5,ipady=5)


    def updateGT_ComboBox(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        key = self.cm_gts_namespace.get()
        self.drop_down['values'] = self.gt_mapping_dict[key]

    def updateCam_ComboBox(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        key = self.camera_sigs_namespace.get()
        self.drop_down_cam.set("")
        self.drop_down_cam['values'] = [key+i for i in self.cameraSigs]
        
    def updateRad_ComboBox(self, event):
        """
        

        Args:
          event: 

        Returns:

        """
        key = self.rad_sigs_namespace.get()
        self.drop_down_rad.set("")
        self.drop_down_rad['values'] = [key+i for i in self.radarSigs]

    def browse_files(self):
        """ """
        filenames = filedialog.askopenfilenames(title="Select Measurement files", filetypes=(("Frame Based .mf4", "*.mf4"),("All Files", "*.*")))
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(tk.END, ", ".join(filenames))

    def Submit(self):
        """ """
        self.disableBtns()

        try:
            measurement_files_list = [i.strip() for i in str(self.file_entry.get()).split(",")]
            #gt_source_names = ["CarMaker::RB::Video::FV::"+i for i in  self.cm_gts_namespace.get().split(",")]
            #gt_sysvars = self.cm_gts.get().split(",")
            #gt_namespace_map = list(zip(gt_sysvars,gt_source_names))
            gt_source_names = "CarMaker::RB::Video::FV::" + self.cm_gts_namespace.get()
            gt_sysvars = self.cm_gts.get()
            gt_namespace_map = [gt_sysvars.strip(),gt_source_names.strip()]

            camera_signals = self.camera_sigs.get().split(",")

            radar_signals = self.radar_sigs.get().split(",")

            if measurement_files_list==['']:
                tkinter.messagebox.showerror("Invalid Input", f"Files not selected")
                logger.error("Files Not Selected")
                self.enableBtns()
                return
            
            if gt_sysvars == [''] and camera_signals == ['']:
                tkinter.messagebox.showerror("Invalid Input", f"Inputs are empty")
                logger.error("Inputs are empty")
                self.enableBtns()
                return

            dict_plot_data = parseTraceGUI(measurement_files_list, gt_namespace_map, camera_signals, radar_signals)
            if dict_plot_data == {}:
                tkinter.messagebox.showerror("Not Found", f"Given sigs data not found in trace")
                logger.error("Given sigs data not found in trace")
                self.enableBtns()
                return

            self.root.destroy()
            self.root = tk.Tk()
            self.root.title("Graph Menu")
            self.root.geometry("300x470+500+100")

            style = ttk.Style()
            style.configure('TButton', font=('calibri', 18), foreground='green')

            self.heading_label = ttk.Label(self.root, text="Plots", font=("Arial", 20))
            self.heading_label.pack(side=tk.TOP,pady=30)
            
            for trace_no, trace_data in dict_plot_data.items():
                self.graph_buttons[trace_no] = ttk.Button(self.root, text=trace_no, command=lambda num=trace_no: self.open_graph_window(self.root, num, dict_plot_data[num]), style='TButton')
                self.graph_buttons[trace_no].pack(pady=10)
            self.root.mainloop()

            #self.enableBtns()
        except Exception as e:
            logger.error(f"Error occured -> {e}")
            tkinter.messagebox.showerror("ERROR", f"Error in submit")
            return


    def open_graph_window(self,root,trace_no, plot_data):
        """
        

        Args:
          root: 
          trace_no: 
          plot_data: 

        Returns:

        """
        new_window = GraphWindow(root, trace_no, plot_data)
        new_window.geometry("700x600")  
        new_window.mainloop()


    def disableBtns(self):
        """ """
        self.sub_btn.config(state=tk.DISABLED)
    
    def enableBtns(self):
        """ """
        self.sub_btn.config(state=tk.NORMAL)


    def __call__(self):
        self.root.mainloop()




if __name__ == "__main__":
    gui = guiWin()
    gui()
