# -*- coding: utf-8 -*-
# @file sensor_set_config.py
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
import tkinter
import tkinter.ttk
# from Test_Execution_Tool_HIL import BenchConnectAndSearch
import time


class ConfigSensorSet:
    """ """
    bench_info = {'hostname': '',
                  'username': '',
                  'password': ''}
    conn_info = {}
    cconfig_name = ''
    cconfig_file_backup_path = ''
    backup_folder_path = ''
    sensor_controller_set = {'dasy': {'keyword': 'DASy_sim', 'value': ''},
                             'cradar_fl': {'keyword': 'CRadarFL_sim', 'value': ''},
                             'cradar_fr': {'keyword': 'CRadarFR_sim', 'value': ''},
                             'cradar_rl': {'keyword': 'CRadarRL_sim', 'value': ''},
                             'cradar_rr': {'keyword': 'CRadarRR_sim', 'value': ''},
                             'front_radar': {'keyword': 'FRadar_sim', 'value': ''},
                             'front_video': {'keyword': 'FVideo_sim', 'value': ''},
                             'map_sim': {'keyword': 'Map_sim', 'value': ''},
                             'rbs_sim': {'keyword': 'Rbs_sim', 'value': ''},
                             'veh': {'keyword': 'Vehicle', 'value': ''},
                             'var': {'keyword': 'Variant', 'value': ''},
                             }

    file_content = []
    is_config_saved = False
    backup_folder_exists = False
    backup_file_exists = False
    initial_backup_exists = False

    def __init__(self, connection_object, connection_attribute, **info):
        self.conn_info.update(**info)
        self.bench_info['hostname'] = self.conn_info['hostname']
        self.bench_info['username'] = self.conn_info['username']
        self.bench_info['password'] = self.conn_info['password']

        self.linux_connection_object = connection_object
        self.connect = connection_attribute

        if self.connect.get_transport().is_alive():
            print(f'Connection is good.')
        else:
            print(f'Connection not good.')

        self.variant_path = self.conn_info['variants_path']
        if info['variants_path'] == "" or info['variants_path'] is None:
            print(f"Variants path is empty. Not good")
        # print(f"Variants path is >>> {self.variant_path}")

        self.received_product = self._filter_received_variant()  # assign received variant to internal var
        self.ensure_backup()

        self.sensorSetWindow = tkinter.Toplevel()
        self.sensorSetWindow.title("Sensor set configuration")
        self.sensorSetWindow.geometry('800x400+40+100')
        self.sensorSetWindow['padx'] = 8

        self.initialize_rows_and_columns()

        self.sensor_choices_dict = {'Off': '0', 'Sim': '1', 'Real': '2'}
        self.sensor_choices = []
        for key, val in self.sensor_choices_dict.items():
            self.sensor_choices.append(key)

        self.map_si_choices_dict = {'Off': '0', 'On': '1'}
        self.map_si_choices = []
        for key, val in self.map_si_choices_dict.items():
            self.map_si_choices.append(key)

        self.var_choices_dict = {'a_variant': '0', 'b_variant': '1'}
        self.var_choices = []
        for key, val in self.var_choices_dict.items():
            self.var_choices.append(key)

        self.veh_choices_dict = {'a_variant_veh_0': '0', 'a_variant_veh_1': '1', 'b_variant_veh_0': '2', 'b_variant_veh_1': '3'}
        self.veh_choices = []
        for key, val in self.veh_choices_dict.items():
            self.veh_choices.append(key)

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' SENSORS '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Sensor Set Label frame
        self.sensor_set_label_frame = tkinter.LabelFrame(self.sensorSetWindow, text='SENSORS')
        self.sensor_set_label_frame.grid(row=0, column=0, sticky='wne', columnspan=8, rowspan=2, pady=10, ipady=8)

        ''''''''''''''''''''''''''''''''''' DASY '''''''''''''''''''''''''''''''''''
        # Create DASY Label inside Sensor Set Label frame
        self.dasy_lbl = tkinter.Label(self.sensor_set_label_frame, text="DASY", width=15)
        self.dasy_lbl.grid(row=0, column=0, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for DASY sensor
        self.dasy_strvar = tkinter.StringVar()
        self.dasy_strvar.set(self.sensor_choices[0])
        self.dasy_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.dasy_strvar, *self.sensor_choices)
        self.dasy_dropdown.grid(row=1, column=0, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.dasy_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' Front Radar '''''''''''''''''''''''''''''''''''
        self.front_radar_lbl = tkinter.Label(self.sensor_set_label_frame, text='Front\nRadar', width=15)  # width=25 so width can be added but removed for now
        self.front_radar_lbl.grid(row=0, column=1, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for Front Radar sensor
        self.front_radar_strvar = tkinter.StringVar()
        self.front_radar_strvar.set(self.sensor_choices[0])
        self.front_radar_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.front_radar_strvar, *self.sensor_choices)
        self.front_radar_dropdown.grid(row=1, column=1, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.front_radar_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' CRadar_front_left '''''''''''''''''''''''''''''''''''
        # Create CRadar_front_left Label inside Sensor Set Label frame
        self.cradar_fl_lbl = tkinter.Label(self.sensor_set_label_frame, text="CRadar\nFrontLeft", width=15)
        self.cradar_fl_lbl.grid(row=0, column=2, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for CRadar_front_left sensor
        self.cradar_fl_strvar = tkinter.StringVar()
        self.cradar_fl_strvar.set(self.sensor_choices[0])
        self.cradar_fl_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.cradar_fl_strvar, *self.sensor_choices)
        self.cradar_fl_dropdown.grid(row=1, column=2, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.cradar_fl_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' CRadar_front_right '''''''''''''''''''''''''''''''''''
        # Create CRadar_front_right Label inside Sensor Set Label frame
        self.cradar_fr_lbl = tkinter.Label(self.sensor_set_label_frame, text='CRadar\nFrontRight', width=15)
        self.cradar_fr_lbl.grid(row=0, column=3, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for CRadar_front_right sensor
        self.cradar_fr_strvar = tkinter.StringVar()
        self.cradar_fr_strvar.set(self.sensor_choices[0])
        self.cradar_fr_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.cradar_fr_strvar,
                                                     *self.sensor_choices)
        self.cradar_fr_dropdown.grid(row=1, column=3, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.cradar_fr_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' CRadar_rear_left '''''''''''''''''''''''''''''''''''
        # Create CRadar_rear_left Label inside Sensor Set Label frame
        self.cradar_rl_lbl = tkinter.Label(self.sensor_set_label_frame, text='CRadar\nRearLeft', width=15)
        self.cradar_rl_lbl.grid(row=0, column=4, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for CRadar_rear_left sensor
        self.cradar_rl_strvar = tkinter.StringVar()
        self.cradar_rl_strvar.set(self.sensor_choices[0])
        self.cradar_rl_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.cradar_rl_strvar,
                                                     *self.sensor_choices)
        self.cradar_rl_dropdown.grid(row=1, column=4, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.cradar_rl_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' CRadar_rear_right '''''''''''''''''''''''''''''''''''
        # Create CRadar_rear_right Label inside Sensor Set Label frame
        self.cradar_rr_lbl = tkinter.Label(self.sensor_set_label_frame, text='CRadar\nRearRight', width=15)
        self.cradar_rr_lbl.grid(row=0, column=5, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for CRadar_rear_right sensor
        self.cradar_rr_strvar = tkinter.StringVar()
        self.cradar_rr_strvar.set(self.sensor_choices[0])
        self.cradar_rr_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.cradar_rr_strvar, *self.sensor_choices)
        self.cradar_rr_dropdown.grid(row=1, column=5, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.cradar_rr_dropdown.config(width=8)

        ''''''''''''''''''''''''''''''''''' Front Video '''''''''''''''''''''''''''''''''''
        # Create Front Video Label inside Sensor Set Label frame
        self.front_video_lbl = tkinter.Label(self.sensor_set_label_frame, text='Front\nVideo', width=15)
        self.front_video_lbl.grid(row=0, column=6, sticky='wnes', columnspan=1, rowspan=1)
        # Create entry box and variable for Front Video sensor
        self.front_video_strvar = tkinter.StringVar()
        self.front_video_strvar.set(self.sensor_choices[0])
        self.front_video_dropdown = tkinter.OptionMenu(self.sensor_set_label_frame, self.front_video_strvar, *self.sensor_choices)
        self.front_video_dropdown.grid(row=1, column=6, sticky='ws', columnspan=1, rowspan=1, padx=7)
        self.front_video_dropdown.config(width=8)

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' SIM '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Sensor Set Label frame
        self.sim_label_frame = tkinter.LabelFrame(self.sensorSetWindow, text='SIM')
        self.sim_label_frame.grid(row=2, column=0, sticky='wn', columnspan=4, rowspan=3, ipadx=100, pady=16, ipady=5)
        self.sim_label_frame.columnconfigure(0, weight=1)
        self.sim_label_frame.columnconfigure(1, weight=2)
        self.sim_label_frame.columnconfigure(2, weight=1)
        self.sim_label_frame.columnconfigure(3, weight=2)

        self.sim_label_frame.rowconfigure(0, weight=1)
        self.sim_label_frame.rowconfigure(1, weight=2)
        self.sim_label_frame.rowconfigure(2, weight=1)
        self.sim_label_frame.rowconfigure(3, weight=1)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' Map_Si '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Map_Si Label
        self.map_si_lbl = tkinter.Label(self.sim_label_frame, text='Map_Si', width=10)
        self.map_si_lbl.grid(row=0, column=0, columnspan=1, rowspan=1)
        # Create entry box and variable for Map_Si
        self.map_sim_strvar = tkinter.StringVar()
        self.map_sim_strvar.set(self.map_si_choices[0])
        self.map_si_dropdown = tkinter.OptionMenu(self.sim_label_frame, self.map_sim_strvar, *self.map_si_choices)
        self.map_si_dropdown.grid(row=0, column=1, sticky='w', columnspan=1, rowspan=1)
        self.map_si_dropdown.config(width=3)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' Pass_Si '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Pass_Si Label
        self.pass_si_lbl = tkinter.Label(self.sim_label_frame, text='Pass_Si', width=10)
        self.pass_si_lbl.grid(row=0, column=2, sticky='w', columnspan=1, rowspan=1, )
        # Create entry box and variable for Pass_Si
        self.pass_si_strvar = tkinter.StringVar()
        # self.front_radar_strvar.trace('w', callback=self.on_repo_path_selection_change)
        self.pass_si_strvar.set(self.map_si_choices[0])
        self.pass_si_dropdown = tkinter.OptionMenu(self.sim_label_frame, self.pass_si_strvar, *self.map_si_choices)
        self.pass_si_dropdown.grid(row=0, column=3, sticky='w', columnspan=1, rowspan=1)
        self.pass_si_dropdown.config(width=3)
        self.pass_si_dropdown['state'] = tkinter.DISABLED

        ''''''''''''''''''''''''''''''''''''''''''''''''''' RBS_Si '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create RBS_Si Label
        self.rbs_si_lbl = tkinter.Label(self.sim_label_frame, text='RBS_Si', width=10)
        self.rbs_si_lbl.grid(row=1, column=0, columnspan=1, rowspan=1)
        # Create entry box and variable for RBS_Si
        self.rbs_sim_strvar = tkinter.StringVar()
        self.rbs_sim_strvar.set(self.map_si_choices[0])
        self.rbs_si_dropdown = tkinter.OptionMenu(self.sim_label_frame, self.rbs_sim_strvar, *self.map_si_choices)
        self.rbs_si_dropdown.grid(row=1, column=1, sticky='w', columnspan=1, rowspan=1)
        self.rbs_si_dropdown.config(width=3)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' Remember Config '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Pass_Si Label
        self.remember_conf_lbl = tkinter.Label(self.sim_label_frame, text='Remember\nConfig', width=10)
        self.remember_conf_lbl.grid(row=1, column=2, sticky='w', columnspan=1, rowspan=1, )
        # Create entry box and variable for Remember Config
        self.remember_conf_strvar = tkinter.StringVar()
        self.remember_conf_strvar.set(self.map_si_choices[0])
        self.remember_conf_dropdown = tkinter.OptionMenu(self.sim_label_frame, self.remember_conf_strvar, *self.map_si_choices)
        self.remember_conf_dropdown.grid(row=1, column=3, sticky='wn', columnspan=1, rowspan=1)
        self.remember_conf_dropdown.config(width=3)
        self.remember_conf_dropdown['state'] = tkinter.DISABLED

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''' VARIANT & VEHICLE '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Sensor Set Label frame
        self.var_label_frame = tkinter.LabelFrame(self.sensorSetWindow, text='VARIANT & VEHICLE')
        self.var_label_frame.grid(row=4, column=0, sticky='w', columnspan=6, rowspan=2, ipadx=80, pady=0, ipady=6)
        self.var_label_frame.columnconfigure(0, weight=1)
        self.var_label_frame.columnconfigure(1, weight=2)
        self.var_label_frame.columnconfigure(2, weight=1)
        self.var_label_frame.columnconfigure(3, weight=2)

        self.var_label_frame.rowconfigure(0, weight=1)
        self.var_label_frame.rowconfigure(1, weight=1)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' variant '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create variant Label
        self.var_lbl = tkinter.Label(self.var_label_frame, text='Variant:', width=10)
        self.var_lbl.grid(row=0, column=0, columnspan=1, rowspan=1)
        # Create entry box and variable for variant
        self.var_strvar = tkinter.StringVar()
        self.var_strvar.set(self.var_choices[0])
        self.var_dropdown = tkinter.OptionMenu(self.var_label_frame, self.var_strvar, *self.var_choices)
        self.var_dropdown.grid(row=0, column=1, sticky='w', columnspan=1, rowspan=1)
        self.var_dropdown.config(width=10)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' vehicle '''''''''''''''''''''''''''''''''''''''''''''''''''
        # Create Pass_Si Label
        self.veh_lbl = tkinter.Label(self.var_label_frame, text='Vehicle:', width=10)
        self.veh_lbl.grid(row=1, column=0, columnspan=1, rowspan=1)
        # Create entry box and variable for Pass_Si
        self.veh_strvar = tkinter.StringVar()
        self.veh_strvar.set(self.veh_choices[0])
        self.veh_dropdown = tkinter.OptionMenu(self.var_label_frame, self.veh_strvar, *self.veh_choices)
        self.veh_dropdown.grid(row=1, column=1, sticky='w', columnspan=1, rowspan=1)
        self.veh_dropdown.config(width=20)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' BUTTONS '''''''''''''''''''''''''''''''''''''''''''''''''''
        self.update_config_frame = tkinter.LabelFrame(self.sensorSetWindow, text='Actions')
        self.update_config_frame.grid(row=2, column=5, sticky='wn', columnspan=2, rowspan=3, ipadx=50, pady=15, ipady=3)
        self.var_label_frame.columnconfigure(0, weight=1)
        self.var_label_frame.columnconfigure(1, weight=2)
        self.var_label_frame.columnconfigure(2, weight=1)
        self.var_label_frame.columnconfigure(3, weight=2)
        self.var_label_frame.rowconfigure(0, weight=1)
        self.var_label_frame.rowconfigure(1, weight=2)
        self.var_label_frame.rowconfigure(2, weight=1)
        self.var_label_frame.rowconfigure(3, weight=1)

        self.backup_config_button = tkinter.ttk.Button(self.update_config_frame, text='Read "default" config', command=self._read_backup_cconfig)
        self.backup_config_button.grid(row=0, column=0, ipadx=1, padx=5, pady=5, sticky='w')

        self.save_config_button = tkinter.ttk.Button(self.update_config_frame, text='Save config', command=self._save_cconfig)
        self.save_config_button.grid(row=2, column=0, ipadx=1, padx=5, pady=5, sticky='w')
        # self._read_last_used_cconfig
        self.lstused_config_button = tkinter.ttk.Button(self.update_config_frame, text='Read "last used" config', command=self._read_last_used_cconfig)
        self.lstused_config_button.grid(row=3, column=0, ipadx=1, padx=5, pady=5)

        ''''''''''''''''''''''''''''''''''''''''''''''''''' tkinter var tracing '''''''''''''''''''''''''''''''''''''''''''''''''''
        if self.backup_folder_exists:
            self.read_controllers_config_file_and_get_values(self.cconfig_file_backup_path)
        elif not self.backup_folder_exists:
            self.read_controllers_config_file_and_get_values(self.cconfig_file_path)

        self.dasy_strvar.trace('w', callback=self._on_dasy_selection_change)
        self.cradar_fl_strvar.trace('w', callback=self._on_cradar_fl_selection_change)
        self.cradar_fr_strvar.trace('w', callback=self._on_cradar_fr_selection_change)
        self.cradar_rl_strvar.trace('w', callback=self._on_cradar_rl_selection_change)
        self.cradar_rr_strvar.trace('w', callback=self._on_cradar_rr_selection_change)
        self.front_radar_strvar.trace('w', callback=self._on_front_radar_selection_change)
        self.front_video_strvar.trace('w', callback=self._on_front_video_selection_change)
        self.rbs_sim_strvar.trace('w', callback=self._on_rbs_sim_selection_change)
        self.map_sim_strvar.trace('w', callback=self._on_map_sim_selection_change)
        self.var_strvar.trace('w', callback=self._on_variant_sim_selection_change)
        self.veh_strvar.trace('w', callback=self._on_vehicle_sim_selection_change)

        self.sensor_strvar_tupple = (self.dasy_strvar, self.cradar_fl_strvar, self.cradar_fr_strvar,
                                     self.cradar_rl_strvar, self.cradar_rr_strvar, self.front_radar_strvar, self.front_video_strvar,
                                     self.rbs_sim_strvar, self.map_sim_strvar,
                                     self.veh_strvar, self.var_strvar)
        self.sensor_names_tupple = ('DASy_sim', 'CRadarFL_sim', 'CRadarFR_sim',
                                    'CRadarRL_sim', 'CRadarRR_sim', 'FRadar_sim', 'FVideo_sim',
                                    'Rbs_sim', 'Map_sim',
                                    'Vehicle', 'Variant')
        self.map_sim_strvar_tupple = (self.rbs_sim_strvar, self.map_sim_strvar)
        self.map_sim_names_tupple = ('Rbs_sim', 'Map_sim')
        self.veh_tupple = 'Vehicle'
        self.var_tupple = 'Variant'

    def _set_interfaces_from_tuple(self, *namevars_tupple):
        """
        

        Args:
          *namevars_tupple: 

        Returns:

        """
        index = 0
        for sens_name in namevars_tupple:
            for sensor, sens_key_val in self.sensor_controller_set.items():

                if sens_key_val['keyword'] == sens_name:

                    if sens_name in str(self.var_tupple):
                        for state, val in self.var_choices_dict.items():
                            if val == sens_key_val['value']:
                                self.sensor_strvar_tupple[index].set(state)

                    elif sens_name in str(self.veh_tupple):
                        for state, val in self.veh_choices_dict.items():
                            if val == sens_key_val['value']:
                                self.sensor_strvar_tupple[index].set(state)

                    elif sens_name in str(self.map_sim_names_tupple):
                        for state, val in self.map_si_choices_dict.items():
                            if val == sens_key_val['value']:
                                self.sensor_strvar_tupple[index].set(state)

                    elif sens_name in str(self.sensor_names_tupple):
                        for state, val in self.sensor_choices_dict.items():
                            if val == sens_key_val['value']:
                                self.sensor_strvar_tupple[index].set(state)
            index += 1

    def _set_interfaces(self):
        """ """
        self._set_interfaces_from_tuple(*self.sensor_names_tupple)

    def _save_cconfig(self):
        """ """
        self._change_file_content()
        self.write_to_file()

    def _read_last_used_cconfig(self):
        """ """
        # the backup is loaded already in self.file_content
        if self.cconfig_file_path != '' and self.cconfig_file_path is not None:
            self.read_controllers_config_file_and_get_values(self.cconfig_file_path)
            self._set_interfaces()
        else:
            print(f"No cconfig file found...")

    def _read_backup_cconfig(self):
        """ """
        # the backup is loaded already in self.file_content
        if self.cconfig_file_backup_path != '' and self.cconfig_file_backup_path is not None:
            self.read_controllers_config_file_and_get_values(self.cconfig_file_backup_path)
            self._set_interfaces()
        else:
            print(f"No backup folder with cconfig file found...")

    def print_out_cconfig(self):
        """ """
        print(f'sensor set >>> ')
        for sens, val in self.sensor_controller_set.items():
            print(f'{sens} is set to {val["value"]}')
        print('\n')

    def _on_variant_sim_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['var']['value'] = self.var_choices_dict[self.var_strvar.get()]
        self.print_out_cconfig()

    def _on_vehicle_sim_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['veh']['value'] = self.veh_choices_dict[self.veh_strvar.get()]
        self.print_out_cconfig()

    def _on_rbs_sim_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['rbs_sim']['value'] = self.map_si_choices_dict[self.rbs_sim_strvar.get()]
        self.print_out_cconfig()

    def _on_map_sim_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['map_sim']['value'] = self.map_si_choices_dict[self.map_sim_strvar.get()]
        self.print_out_cconfig()

    def _on_front_video_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['front_video']['value'] = self.sensor_choices_dict[self.front_video_strvar.get()]
        self.print_out_cconfig()

    def _on_front_radar_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['front_radar']['value'] = self.sensor_choices_dict[self.front_radar_strvar.get()]
        self.print_out_cconfig()

    def _on_cradar_rr_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['cradar_rr']['value'] = self.sensor_choices_dict[self.cradar_rr_strvar.get()]
        self.print_out_cconfig()

    def _on_cradar_rl_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['cradar_rl']['value'] = self.sensor_choices_dict[self.cradar_rl_strvar.get()]
        self.print_out_cconfig()

    def _on_cradar_fr_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['cradar_fr']['value'] = self.sensor_choices_dict[self.cradar_fr_strvar.get()]
        self.print_out_cconfig()

    def _on_cradar_fl_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['cradar_fl']['value'] = self.sensor_choices_dict[self.cradar_fl_strvar.get()]
        self.print_out_cconfig()

    def _on_dasy_selection_change(self, *args):
        """
        

        Args:
          *args: 

        Returns:

        """
        self.sensor_controller_set['dasy']['value'] = self.sensor_choices_dict[self.dasy_strvar.get()]
        self.print_out_cconfig()

    def _change_file_content(self):
        """ """
        for key, val in self.sensor_controller_set.items():
            for index in range(0, len(self.file_content)):
                if val['keyword'] in self.file_content[index]:
                    # print(f'Found row containing the keyword: ({val["keyword"]}) and value: ({val["value"]}) type value ({type(val["value"])}) is found!\nRow before change: {self.file_content[index]}')
                    # print(f'Row last element: {self.file_content[index][-2]}')
                    self.file_content[index] = re.sub(r'\d+\n$', val["value"] + '\n', self.file_content[index])
        #             print(f'Row after change?: {self.file_content[index]}')
        # print(f"file content after change >>> {self.file_content}")
        self.is_config_saved = False

    def write_to_file(self):
        """ """
        # print(f"controler_config_folder_path >>> \n{self.cconfig_file_path}")  # self.cconfig_file_path
        file_content_str = ''.join(self.file_content)
        write_command = "echo " + "'" + file_content_str + "'" + " > " + self.cconfig_file_path + "\n"
        stdin, stdout, stderr = self.connect.exec_command(write_command)
        err = stderr.read().decode()
        if len(err) == 0:
            self.is_config_saved = True

    # def _delete_the_backup_folder(self):
    #     backup_path = self._search(self.variant_path, 'backup')
    #     # print(f'backup path found before del? >>> {backup_path}')
    #     if len(backup_path) == 1:
    #         del_command = 'rm -r ' + backup_path[-1] + '\n'
    #         # print(f'del command is?: {del_command}')
    #         stdin, stdout, stderr = self.connect.exec_command(del_command)
    #         output = stdout.read().decode()
    #         err = stderr.read().decode()
    #         err = err.strip()
    #         # print(f'output of del >>> {output}')
    #         # print(f'err of del >>> {err}')
    #     else:
    #         # print(f'Too many backup paths are found')
    #         for bck_path in backup_path:
    #             # print(f"path >>> {bck_path}")

    def read_controllers_config_file_and_get_values(self, path_to_cconf):
        """
        

        Args:
          path_to_cconf: 

        Returns:

        """
        read_command = 'cat ' + path_to_cconf + '\n'
        if path_to_cconf != '':
            self.file_content.clear()
            stdin, stdout, stderr = self.connect.exec_command(read_command)
            output = stdout.read().decode()
            output = output.split('\n')
            # print(f"Read file >>>>\n{output}")
            for line in output:
                # print(f"line >>> {line}")
                self.file_content.append(line + '\n')
                for key, value in self.sensor_controller_set.items():
                    # print(f"sensorset >>> {value}")
                    if value['keyword'] in line:
                        # print(f"{value['keyword']} is in ({line})")
                        value['value'] = line[-1]
            # print(f"initial sensorset values? >>>\n")
            self.print_out_cconfig()

    def _search(self, search_where, search_what, folder_or_file='Folder'):
        """
        

        Args:
          search_where: 
          search_what: 
          folder_or_file:  (Default value = 'Folder')

        Returns:

        """
        if folder_or_file == 'Folder':
            command = 'find ' + search_where + ' ' + '-depth -name ' + search_what + '\n'
        else:
            command = 'find ' + search_where + ' ' + '-depth -name ' + '"' + search_what + '"' + '\n'
        search_results = []
        # print(f'Command to be sent: {command}')
        if search_where != '' and not None:
            stdin, stdout, stderr = self.connect.exec_command(command)
            output = stdout.read().decode()
            output = output.split('\n')

            for row in output:
                if row != '':
                    search_results.append(row)
            # print(f"Results from search >>>\n{search_results}")
            time.sleep(1)
            if len(search_results) == 0:
                return "Nothing found"
            elif len(search_results) > 0:
                return search_results

    def find_available_controller_config_files(self, variants_path):
        """
        

        Args:
          variants_path: 

        Returns:

        """
        to_trim = variants_path + '/include/'  # variants_path is '/home/sya9lr/GIT_Workspace/PSA_Testing/ods_cloe_tests/cloe_tests/conf'
        controllers = self._search(variants_path, 'controllers_conf*.yml')  # list available controllers
        filtered_list = []
        if controllers == "Nothing found" or None:
            return None
        elif controllers != "Nothing found" and not None:
            self.backup_folder_path = to_trim
            for path in controllers:
                path = re.sub(to_trim, '', path)
                filtered_list.append(path)
            # print(f"Config paths?: {controllers}")
            # print(f'Configs? >>> {filtered_list}')
            return controllers

    def _filter_received_variant(self):
        """ """
        mask = re.compile(r'evald_config_develop')
        if len(mask.findall(self.conn_info['product_variant'])) > 0:
            new_var = re.sub(mask, '', self.conn_info['product_variant'])
            if new_var == '.yml':
                # print(f"Filtered variant >>> {new_var}")
                return 'evald_config_develop.yml'
            else:
                # print(f"Filtered variant >>> {new_var}")
                return new_var
        else:
            # print(f"No variant is selected")
            return "Nothing"

    def _copy_cconf_file_to_backup_folder(self, copy_what, paste_where):
        """
        

        Args:
          copy_what: 
          paste_where: 

        Returns:

        """
        command = 'cp ' + copy_what + ' ' + paste_where + '\n'
        stdin, stderr, stdout = self.connect.exec_command(command)
        output = stdout.read().decode()
        output = output.strip()
        # print(output)

    def ensure_backup(self):
        """ """
        return self._backup_sequence()

    def _backup_sequence(self):
        """ """
        self._assign_cconf_name()
        temp_cconf_paths = self._search(self.variant_path + '/include', self.cconfig_name, 'File')

        for path in temp_cconf_paths:
            if '/backup' not in path:
                if self.cconfig_name in path:
                    self.cconfig_file_path = path
                    break
                else:
                    self.cconfig_file_path = ''

        if self.cconfig_file_path != '':
            self._create_backup_folder()
            backupyml_search = self._search(self.backup_folder_path, self.cconfig_name, 'File')
            if backupyml_search == 'Nothing found':
                self.backup_file_exists = False
                self._copy_cconf_file_to_backup_folder(self.cconfig_file_path, self.backup_folder_path)
                self.cconfig_file_backup_path = self.backup_folder_path + '/' + self.cconfig_name
            elif backupyml_search != 'Nothing found':  # this means we have more than one found controller config in /backup, so we select the one with smallest lenght(most probably to be the real one)
                self.backup_file_exists = True
                smallest = ""
                for i in range(0, len(backupyml_search)):  # here we get the smallest one
                    if i == 0:
                        smallest = len(backupyml_search[i])
                        self.cconfig_file_backup_path = backupyml_search[i]
                    else:
                        if len(backupyml_search[i]) < smallest:
                            smallest = len(backupyml_search[i])
                            self.cconfig_file_backup_path = backupyml_search[i]
                print(f"self.cconfig_file_backup_path from _BACKUP_SEQUENCE >>> {self.cconfig_file_backup_path}")
                print(f"self.cconfig_file_path from _BACKUP_SEQUENCE >>> {self.cconfig_file_path}")
        elif self.cconfig_file_path == '':
            print(f"ATTENTION! NO CCONF FILE IS FOUND! ABORT OPERATION!")

    def _assign_cconf_name(self):
        """ """
        if self.received_product != 'Nothing' and self.received_product is not None:
            if self.received_product == 'evald_config_develop.yml':
                self.cconfig_name = 'controllers_config.yml'
            elif self.received_product != 'evald_config_develop.yml':
                self.cconfig_name = 'controllers_config' + self.received_product
        else:
            self.cconfig_name = ''
        # print(f"CCONF NAME FROM FUNCTION _assign_cconf_name == {self.cconfig_name}")

    def _create_backup_folder(self):
        """ """
        command = 'mkdir ' + self.variant_path + '/include/backup\n'
        stdin, stderr, stdout = self.connect.exec_command(command)
        output = stdout.read().decode()
        output = output.strip()
        if 'File exists' in output:
            # print(f'backup exists...')
            self.initial_backup_exists = True
        else:
            # print(f'backup does not exist, folder is created...')
            self.initial_backup_exists = False
        self.backup_folder_path = self.variant_path + '/include/backup'

    def initialize_rows_and_columns(self):
        """ """
        self.sensorSetWindow.columnconfigure(0, weight=1)
        self.sensorSetWindow.columnconfigure(1, weight=1)
        self.sensorSetWindow.columnconfigure(2, weight=1)
        self.sensorSetWindow.columnconfigure(3, weight=1)
        self.sensorSetWindow.columnconfigure(4, weight=1)
        self.sensorSetWindow.columnconfigure(5, weight=1)
        self.sensorSetWindow.columnconfigure(6, weight=1)
        self.sensorSetWindow.columnconfigure(7, weight=1)

        self.sensorSetWindow.rowconfigure(0, weight=2)
        self.sensorSetWindow.rowconfigure(1, weight=1)
        self.sensorSetWindow.rowconfigure(2, weight=2)
        self.sensorSetWindow.rowconfigure(3, weight=1)
        self.sensorSetWindow.rowconfigure(4, weight=2)
        self.sensorSetWindow.rowconfigure(5, weight=2)

    def on_closing(self):
        """ """
        if not self.is_config_saved:
            if not self.initial_backup_exists:
                print(f"initial backup was not present and config is not saved, deleting backup...")
                # self._delete_the_backup_folder()
            elif self.initial_backup_exists:
                print(f"initial backup WAS present and config is not saved, NOT deleting backup...")
        print(f"config saved?: {self.is_config_saved}")
        self.linux_connection_object.close_connection()
        self.sensorSetWindow.destroy()

    def __call__(self):
        self.sensorSetWindow.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.sensorSetWindow.mainloop()
