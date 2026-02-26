# -*- coding: utf-8 -*-
# @file script_switch.py
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
#from PIL import ImageTk, Image
#from tkinter.filedialog import *
from tkinter.messagebox import *
#import ADAS_HIL_DCROSS_CDPO_Pipeline as api
import os
import sys
import subprocess
from PIL import ImageTk,Image  
import json


#Variables
current_path = (os.path.abspath(os.getcwd())).replace("\\","/")+"/"
config = {"CDPO":{"RadarFC":{"active_ip":"192.168.0.2","passive_ip":"192.168.0.8"},"conf":"D:/Configs/CDPOconfig.vaset"},"DCROSS":{"RadarFC":{"active_ip":"192.168.0.2","passive_ip":"192.168.0.9"},"conf":"D:/Configs/DCROSSconfig.vaset"},"HIL_Config":{"Current_Config":"CDPO","VXconfig_path":"D:/Tools/VXtools_RB_Radar_Gen5_02_26/VXconfig.exe"}}
active_config="CDPO"
passive_config="DCROSS"
# #path_vxconfig = "C:/Program Files (x86)/Vector VXtools 4.0 SP1/VXconfig.exe"
# path_vxconfig = "C:/Program Files (x86)/Vector VXtools 4.2/VXconfig.exe"
error_missmatch=0
update_ongoing=0
skip_switch=0

#Functions

def process_exists(process_name):
    """
    

    Args:
      process_name: 

    Returns:

    """
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    try:
        #iso8859_2 for getting the weird German symbols like ü in Infra HILs
        output = subprocess.check_output(call).decode('iso8859_2')
        # decode can fail if weird language used for os commands
        # check in last line for process name
        last_line = output.strip().split('\r\n')[-1]
    except:
        # if there is an error, return true so the script can still run
        last_line = process_name
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def load_config():
    """ """
    global current_path
    global config
    try:
        with open(current_path+'settings.json') as f:
            config = json.load(f)
            print("New config loaded")
    except:
        print("Error loading the json file, using default config")
        
def save_config():
    """ """
    global current_path
    global config
    try:
        with open(current_path+'settings.json', 'w') as fp:
            json.dump(config, fp, indent=4)
    except:
        print("Issue saving the configuration in json file")

def update_config(event=0):
    """
    

    Args:
      event:  (Default value = 0)

    Returns:

    """
    global config
    global active_config
    global passive_config
    global error_missmatch
    global update_ongoing
    if update_ongoing==0:
        update_ongoing=1
        print("update")
        load_config()
        if active_config!=config["HIL_Config"]["Current_Config"]:
            if config["HIL_Config"]["Current_Config"]=="CDPO":
                set_cdpo_picture()
                active_config=config["HIL_Config"]["Current_Config"]
            elif config["HIL_Config"]["Current_Config"]=="DCROSS":
                set_dcross_picture()
                active_config=config["HIL_Config"]["Current_Config"]
        if active_config == "CDPO":
            passive_config = "DCROSS"
        else:
            passive_config = "CDPO"
        if (check_active_config(active_config)!=0 or check_passive_config(passive_config)!=0):
            if (check_active_config(passive_config)==0 and check_passive_config(active_config)==0):
                config["HIL_Config"]["Current_Config"]=passive_config
                save_config()
                update_ongoing=0
                update_config()
                update_ongoing=1
                showinfo(title="Switch in the setup detected", message="The detected config did not match the setup of the settings, the settings were updated")
            elif(error_missmatch==0):
                error_missmactch=1
                showerror(title="Mismatch detected", message="The configured setup does not match the current setup, the HIL might not work as intended\nPlease make sure that all Vector boxes are running")
        else:
            error_missmatch=0
        update_ongoing=0

def check_active_config(project):
    """
    

    Args:
      project: 

    Returns:

    """
    global config
    global active_config
    error=0
    for ecu in config[project]:
        if (ecu!="conf"):
            command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["active_ip"])
            print(command)
            returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
            if returnValue != 0:
                error=1
    return error
    
def check_passive_config(project):
    """
    

    Args:
      project: 

    Returns:

    """
    global config
    global active_config
    error=0
    for ecu in config[project]:
        if (ecu!="conf"):
            command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["passive_ip"])
            print(command)
            returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
            if returnValue != 0:
                error=1
    return error

def resource_path(relative_path):
    """
    

    Args:
      relative_path: 

    Returns:

    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    #print("test")
    print(base_path)
    return os.path.join(base_path, relative_path)

def switch_vcanconf(project):
    """
    

    Args:
      project: 

    Returns:

    """
    command = "WMIC /NODE:\"192.168.1.5\" /user:Administrator /password:\"\" process call create \"vcanconf -impApplCfg -filePathAndName:\"\"{0}\"\"\"".format(config[project]["conf"])
    print(command)
    #returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))), stdout=sys.stdout, stderr=sys.stderr)
    returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
    return returnValue

def switch_to_passive(project, ecu):
    """
    

    Args:
      project: 
      ecu: 

    Returns:

    """
    returnValue = 0
    command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["active_ip"])
    print(command)
    is_active = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
    if is_active == 0:
        command = "\"{0}\" -net {1} -a {2}".format(config["HIL_Config"]["VXconfig_path"],config[project][ecu]["active_ip"],config[project][ecu]["passive_ip"])
        print(command)
        returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
        if returnValue == 0:
            command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["passive_ip"])
            print(command)
            returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
        
    return returnValue

def switch_to_active(project, ecu):
    """
    

    Args:
      project: 
      ecu: 

    Returns:

    """
    returnValue = 0
    command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["passive_ip"])
    print(command)
    is_passive = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
    if is_passive == 0:
        command = "\"{0}\" -net {1} -a {2}".format(config["HIL_Config"]["VXconfig_path"],config[project][ecu]["passive_ip"],config[project][ecu]["active_ip"])
        print(command)
        returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
        if returnValue == 0:
            command = "ping -n 1 {0} | findstr /r /c:\"[0-9] *ms\"".format(config[project][ecu]["active_ip"])
            print(command)
            returnValue = subprocess.call(command, shell=True, cwd=os.path.join(os.path.dirname(os.path.realpath(__file__))))
    return returnValue

def switch_config_hil(project):
    """
    

    Args:
      project: 

    Returns:

    """
    global active_config
    global error_missmatch
    error_missmatch=0
    old_project = active_config
    error=0
    if (process_exists("CANoe64.exe") or process_exists("CANape64.exe")):
        if (askyesno(title="CANoe or CANape running", message="It is recommended to close CANoe and CANape to ensure a clean switch between configs.\nAre you sure that you want to continue ?")==0):
            error=2
    for ecu in config[old_project]:    
        if (ecu!="conf" and error==0):
            error = switch_to_passive(old_project, ecu)
    for ecu in config[project]:
        if (ecu!="conf" and error==0):
            error = switch_to_active(project, ecu)
    if error==0:
        error = switch_vcanconf(project)
    else:
        print("Error switching config")
        showerror(title="Error switching config", message="An error occured")
    return error
    
def set_cdpo_picture():
    """ """
    global img
    global canvas
    global image_container
    canvas.config(height=302,width=553)
    img = ImageTk.PhotoImage(Image.open(resource_path("CDPO.png")))
    canvas.itemconfig(image_container,image=img)

def set_dcross_picture():
    """ """
    global img
    global canvas
    global image_container
    canvas.config(height=302,width=553)
    img = ImageTk.PhotoImage(Image.open(resource_path("DCROSS.png")))
    canvas.itemconfig(image_container,image=img)
    
def setup_cdpo():
    """ """
    global active_config
    global config
    global skip_switch
    update_config()
    if (check_active_config(active_config)!=0 or check_passive_config(passive_config)!=0):
        if (askyesno(title="Unexpected config", message="Cannot detect current setup of the HIL, please make sure that the vector boxes are running\n Do you want to force the setup of the config ?")==0):
            skip_switch=1
    elif active_config=="CDPO":
        if (askyesno(title="Already configured to CDPO", message="The HIL is already configured to CDPO, do you want to reset the CDPO configuration ?")==0):
            skip_switch=1
    if skip_switch==0:
        if switch_config_hil("CDPO")==0:
            set_cdpo_picture()
            showinfo(title="Message", message="Config switched to CDPO successfully!")
            active_config="CDPO"
            config["HIL_Config"]["Current_Config"]=active_config
            save_config()
    else:
        skip_switch=0

def setup_dcross():
    """ """
    global active_config
    global config
    global skip_switch
    update_config()
    if (check_active_config(active_config)!=0 or check_passive_config(passive_config)!=0):
        if (askyesno(title="Unexpected config", message="Cannot detect current setup of the HIL, please make sure that the vector boxes are running\n Do you want to force the setup of the config ?")==0):
            skip_switch=1
    elif active_config=="DCROSS":
        if (askyesno(title="Already configured to DCROSS", message="The HIL is already configured to DCROSS, do you want to reset the DCROSS configuration ?")==0):
            skip_switch=1
    if skip_switch==0:
        if switch_config_hil("DCROSS")==0:
            set_dcross_picture()
            showinfo(title="Message", message="Config switched to DCROSS successfully!")
            active_config="DCROSS"
            config["HIL_Config"]["Current_Config"]=active_config
            save_config()
    else:
        skip_switch=0
#main

if __name__=="__main__":

    #init window
    root = tk.Tk()
    root.title("ADAS HIL Config")
    try:
        root.iconbitmap(resource_path("classe.ico"))
    except:
        print("Cannot load icon")
    frame_current_config = tk.LabelFrame(root, text="Current Config")
    frame_current_config.pack(fill=tk.BOTH, expand=True)
    #canvas = tk.Canvas(frame_current_config, height=142, width = 644)
    canvas = tk.Canvas(frame_current_config, height=302, width = 553)
    canvas.pack(expand=True, anchor=tk.CENTER)
    #img = ImageTk.PhotoImage(Image.open("DCROSS.png"))
    img = ImageTk.PhotoImage(Image.open(resource_path("CDPO.png")))
    image_container = canvas.create_image(2,2,anchor=tk.NW,image=img)
    command_frame = tk.Frame(root)
    command_frame.pack(expand=True , fill=tk.X)
    set_cdpo_button = tk.Button(command_frame, text="Setup for CDPO", command= setup_cdpo, padx=50)
    set_cdpo_button.pack(side=tk.LEFT, padx=50, pady=10)
    set_dcross_button = tk.Button(command_frame, text="Setup for DCROSS", command= setup_dcross, padx=50)
    set_dcross_button.pack(side=tk.RIGHT, padx=50, pady=10)
    #root.bind('<Enter>', update_config)
    canvas.bind('<Enter>', update_config)
    #init config
    update_config()
    
    root.mainloop()
    