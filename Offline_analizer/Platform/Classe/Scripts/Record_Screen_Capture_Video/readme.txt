!!! IMPORTANT !!!
You need to copy this file
\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Record_Screen_Capture_Video.exe

into ADAS HIL GUI PC -> folder :<RBS>\Platform\Classe\Scripts\Record_Screen_Capture_Video
This is a tool that captures the screen using OpenCV Python library.
How to use it. It takes 2 arguments - FPS and Duration.
Example:
python Record_Screen_Capture_Video.py 25 120
/it will record 120 seconds with 25 fps/
If no arguments are given it is defaulting to 10fps and 120 seconds.
File : CANoe-Python_data_exchange_file.txt is used for exchanging data with CANoe.
If CANoe writes a line "CANoe_request:ABORT_CAPTURE" inside this file then capturing will stop immediately.

!!!IMPORTANT!!!
Use file : start_me - out_of_CANoe.bat if you want to run standalone without CANoe.
File start_me.bat is used only from CANoe. Do not use it standalone.

!!! IMPORTANT !!!
You need to copy this file
\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\Record_Screen_Capture_Video.exe

into ADAS HIL GUI PC -> folder :<RBS>\Platform\Classe\Scripts\Record_Screen_Capture_Video