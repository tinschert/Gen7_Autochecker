#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
import clr # <- uncomment if you are running a National Instruments Project
import os
manifest_file_path=r"C:\ProgramData\ASAM\XIL\Implementation\IPG_ImplementationManifest.imf"
if os.path.exists(manifest_file_path):
   print("The MANIFEST file exists under : C:\ProgramData\ASAM\XIL\Implementation ")
else:
   print("The file does not exist under : C:\ProgramData\ASAM\XIL\Implementation")
   print("Copy IPG_ImplementationManifest.imf to C:\ProgramData\ASAM\XIL\Implementation")
   print("/this is required in order XIL API to work/")
   os.popen('copy IPG_ImplementationManifest.imf C:\ProgramData\ASAM\XIL\Implementation\IPG_ImplementationManifest.imf')


sys.path.append(r"C:\IPG\carmaker\win64-12.0.2\Python\python3.11")
from ASAM.XIL.Implementation.Testbench import TestbenchFactory
from ASAM.XIL.Interfaces.Testbench.MAPort.Enum.MAPortState import MAPortState
from ASAM.XIL.Interfaces.Testbench.Common.Error.TestbenchPortException import TestbenchPortException

MAPortConfigFile = "Config.xml"

if __name__ == "__main__":
    MAPort = None

    # Initialize all necessary class instances
    MyTestbenchFactory = TestbenchFactory()
    MyTestbench = MyTestbenchFactory.CreateVendorSpecificTestBench("IPG", "CarMaker", "12.0.2")
    MyMAPortFactory = MyTestbench.MAPortFactory
    MyWatcherFactory = MyTestbench.WatcherFactory

    print("Creating and Configuring MAPort...")
    MAPort = MyMAPortFactory.CreateMAPort("MAPort")

    # Start CarMaker instance using a Project directory as Configuration parameter
    MAPortConfig = MAPort.LoadConfiguration(MAPortConfigFile)
    MAPort.Configure(MAPortConfig, False)

    print("Starting simulation...")
    #if MAPort.State is not MAPortState.eSIMULATION_RUNNING:
    MAPort.StartSimulation("Examples/BasicFunctions/Driver/BackAndForth")

    # Overwrite the Steering angle during simulation at different times
    MAPort.WaitForTime(10.0, 30.0)
    # change steering angle
    print("SteerAng after 10s: " + str(MAPort.Read("DM.Steer.Ang")))
    print("Setting steer angle to 1 rad for 100ms")
    MAPort.Write("DM.Steer.Ang", 1.0, 100)
    MAPort.WaitForTime(10.1, 30.0)
    print("New SteerAngle after write: " + str(MAPort.Read("DM.Steer.Ang")))

    MAPort.WaitForTime(20.0, 30.0)
    # change steering angle without pause
    print("SteerAngle after 20s: " + str(MAPort.Read("DM.Steer.Ang")))
    print("Setting steer angle to -2 rad for 100ms")
    MAPort.Write("DM.Steer.Ang", -2.0, 100)
    MAPort.WaitForTime(20.1, 30.0)
    print("New steering angle after write: " + str(MAPort.Read("DM.Steer.Ang")))

    # Stop simulation
    MAPort.StopSimulation()

