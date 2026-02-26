# -*- coding: utf-8 -*-
# @file Clone_Testing_Repo_on_GUI_PC.py
# @author ADAS_HIL_TEAM
# @date 09-11-2023

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


import rpyc
import time
import subprocess
import sys
import os
import shutil
import distutils.log
from distutils.dir_util import copy_tree
from pathlib import Path

def copy_cm_project(src, dest):
    """
    

    Args:
      src: 
      dest: 

    Returns:

    """
    try:
        #print(f"Start copying CarMaker project from testing repo to ADAS_SIM")
        distutils.log.set_verbosity(distutils.log.DEBUG)
        copy_tree(src, dest, update=1, verbose=0)
        print(f"...done")
    except PermissionError as e:
        print(f"Permission denied --> {e}")
        raise e
    except Exception as e:
        print(f"Failed to copy to ADAS SIM --> {e}")
        raise e

def Read_Repo_Name_From_Settings_File():
    """ """
   repo_name=""
   f1 = open("settings.txt", "r")
   try:
      for el in f1:
         if (el.find("testing_repo_to_checkout:")>=0):
            idx0=el.find("testing_repo_to_checkout:")+len("testing_repo_to_checkout:")
            repo_name = el[idx0:]
            repo_name=repo_name.replace("\n","")#remove line ending (EOL)
            print("Repository_Name read from settings.txt = ",repo_name)
   except:
      print("Error : no such repository ... defaulting to repo : ssh://git@sourcecode01.de.bosch.com:7999/forddat3vv/fd3_drv_prk_adas_xil_tests.git")
      repo_name = f"ssh://git@sourcecode01.de.bosch.com:7999/forddat3vv/fd3_drv_prk_adas_xil_tests.git"
   f1.close()
   return repo_name

def Read_Branch_Name_From_Settings_File():
    """ """
   br_name=""
   f1 = open("settings.txt", "r")
   try:
      for el in f1:
         if (el.find("branch_name_to_checkout:")>=0):
            idx0=el.find("branch_name_to_checkout:")+len("branch_name_to_checkout:")
            br_name = el[idx0:]
            br_name = br_name.replace("\n", "")  # remove line ending (EOL)
            print("Branch_Name read from settings.txt = ",br_name)
   except:
      print("Error : no such branch ... defaulting to repo : develop")
      br_name = "develop"
   f1.close()
   return br_name

def onerror(func, path, exc_info):
    """
    

    Args:
      func: 
      path: 
      exc_info: 

    Returns:

    """
   import stat
   # Is the error an access error?
   if not os.access(path, os.W_OK):
      os.chmod(path, stat.S_IWUSR)
      func(path)
   else:
      raise

def calculate_path_to_adas_sim_folder():
    """ """
   temp_str=""
   script_path = os.getcwd()
   #print("!!!DEBUG 8 script_path = ", script_path)
   list1=script_path.split(f"\\")
   #print(list1)
   len_list1=len(list1)
   #print(len_list1)
   for el in range(len_list1-4):
      temp_str=temp_str+list1[el]+"\\"
   temp_str=temp_str+"adas_sim\CM_Projects\CANoe_Test"
   #print("QWERTY",temp_str)
   return(temp_str)

def Exchange_Status_With_CANoe(string_to_write,file_path):
    """
    

    Args:
      string_to_write: 
      file_path: 

    Returns:

    """
   try:
      os.remove(file_path + "\\CANoe-Python_data_exchange_file.txt")
      f2 = open(file_path + "\\CANoe-Python_data_exchange_file.txt", "w+")
      f2.write(string_to_write)
      print("Data written to CANoe exchange file : ",string_to_write)
      f2.close()
   except:
      print("Can not write into file : CANoe-Python_data_exchange_file.txt")


############################################################################################################################################################################################################
##  M A I N  ###############################################################################################################################################################################################
############################################################################################################################################################################################################
def main_sequence():
    """ """
   py_file_path=os.getcwd()
   Exchange_Status_With_CANoe("status:CM_project_synchronization_NOT_done",py_file_path)
   dest_folder = calculate_path_to_adas_sim_folder()
   #print("!!!DEBUG 9 dest_folder = ", dest_folder)
   directory = f"Testing_Repo"
   parent_dir = f"c:\\"
   path = os.path.join(parent_dir, directory)
   #repository_name = "ssh://git@sourcecode01.de.bosch.com:7999/forddat3vv/fd3_drv_prk_adas_xil_tests.git"
   #branch_name = "develop"
   repository_name = Read_Repo_Name_From_Settings_File()
   branch_name = Read_Branch_Name_From_Settings_File()
   #print("!!!DEBUG 5 repository_name = ",repository_name)
   #print("!!!DEBUG 6 branch_name = ", branch_name)

   try:
      shutil.rmtree(path, ignore_errors = False,onerror=onerror)
      #print("Directory ",path,"is removed successfully")
      print("Directory ", path, "is cleaned successfully")
   except OSError as x:
      #print("Error occured: %s : %s" % (path, x.strerror))
      pass


   try:
       os.chdir(f"c:\\")
   except:
      print("Cannot change directory to c:\\")
      pass

   print("Cloning repository : ",repository_name,"... (please wait...)")

   result = subprocess.run(f"git clone "+repository_name+" --no-checkout "+directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   #print("!!!DEBUG 1 result = ",result)

   try:
       os.chdir(path)
   except:
      print("Cannot change path")
      pass



   result = subprocess.run(f"git sparse-checkout init --cone", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   #print("!!!DEBUG 2 result = ",result)
   result = subprocess.run(f"git sparse-checkout set cm_project", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   #print("!!!DEBUG 3 result = ",result)
   print("...done")
   print("Checking out branch : ",branch_name,"... (please wait...)")
   result = subprocess.run(f"git checkout "+branch_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   print("...done")
   #print("!!!DEBUG 4 result = ",result)
   print("Start copying from ",path,"\\cm_project to ",dest_folder)
   copy_cm_project(path+"\\cm_project",dest_folder)
   Exchange_Status_With_CANoe("status:CM_project_synchronization_DONE",py_file_path)

if __name__ == "__main__":

   main_sequence()
   #Exchange_Status_With_CANoe("status:CM_project_synchronization_DONE",py_file_path)
   #Exchange_Status_With_CANoe("QWERTY")
