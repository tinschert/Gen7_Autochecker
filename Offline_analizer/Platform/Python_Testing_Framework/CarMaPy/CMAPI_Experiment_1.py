#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11")
sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11/cmapi")
import cmapi

async def Read_Write_DVA():
    mysimIO = cmapi.SimIO
    await mysimIO.dva_read_async("DM.Gas")
    await mysimIO.dva_write_absolute_value("DM.Gas",1.0,10000,None)
cmapi.Task.run_main_task(Read_Write_DVA())