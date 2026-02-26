import cv2
import numpy as np
import pyautogui
import sys
import time

ABORT_CODE = 1
NO_ABORT_CODE = 0

def Exchange_Status_With_CANoe(file_path):
   """
   Description: This function reads from a text file and sends a signal to stop main function execution if conditions are met
   Args:
     file_path- path to text file as string
   Returns:
     ABORT_CODE- integer value
   """   
   try:
      f1 = open(file_path, "r")
      for el in f1:
          if el.find(":STOP_CAPTURE")>=0:
              print("Aborting capture due to request from CANoe (CarMaker simulation finished)...")
              return ABORT_CODE
          else:
              #print("!!!DEBUG!!! Continue capture")
              return NO_ABORT_CODE
      f1.close()
   except:
      print("Can not read file : CANoe-Python_data_exchange_file.txt")

def GetScenarioName_From_CANoe_Exchange_File(file_path):
    """
    Description: This function reads from a text file and extracts a string from it`
    Args:
      file_path- path to text file as string
    Returns:
      temp_list- string read from the text file
    """   
    f2 = open(file_path, "r")
    for el in f2:
        temp_list=el.split(":")
    f2.close()
    return temp_list[0].replace("\\","_")



def main():
    """
    Description: This function changes the focus window to IPGMoive and writes a video in MP4 format as long as CarMaker is running
    """   
    scenario_name=GetScenarioName_From_CANoe_Exchange_File("CANoe-Python_data_exchange_file.txt")
    #Make IPGMove the foreground window
    w=pyautogui.getWindowsWithTitle("IPGMovie")[0]
    w.activate()
    w.maximize()
    #Move the camera slightly up
    pyautogui.moveTo(w.midtop.x,w.midleft.y)
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.moveTo(w.midtop.x-100,w.midleft.y-380)
    pyautogui.mouseUp()
    SCREEN_SIZE = tuple(pyautogui.size())

    if (len(sys.argv)>1):
        fps=float(sys.argv[1])
        print("argument 1 (fps) = ",fps)
        record_seconds = int(sys.argv[2])
        print("argument 2 (duration) = ", record_seconds)
    else:
        fps = 10.0
        record_seconds = 120

    new_filename=scenario_name+f".mp4"
    out = cv2.VideoWriter(new_filename, 0x7634706d, fps, (SCREEN_SIZE))

    for i in range(int(record_seconds * fps)):
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        if (Exchange_Status_With_CANoe("CANoe-Python_data_exchange_file.txt")==ABORT_CODE):
            break

    cv2.destroyAllWindows()
    out.release()

if __name__ == "__main__":
    main()