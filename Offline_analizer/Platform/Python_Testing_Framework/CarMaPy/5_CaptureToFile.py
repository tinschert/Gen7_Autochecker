#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
#import clr # <- uncomment if you are running a National Instruments Project

sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.7")
from ASAM.XIL.Implementation.Testbench import TestbenchFactory
from ASAM.XIL.Interfaces.Testbench.MAPort.Enum.MAPortState import MAPortState
from ASAM.XIL.Interfaces.Testbench.Common.Error.TestbenchPortException import TestbenchPortException

MAPortConfigFile = "Config.xml"

if __name__ == "__main__":
    DemoCapture = None
    CarMaPort = None

    try:
        # Initialise all necessary class instances
        MyTestbenchFactory = TestbenchFactory()
        MyTestbench = MyTestbenchFactory.CreateVendorSpecificTestBench("IPG", "CarMaker", "12.0.2")
        MyMAPortFactory = MyTestbench.MAPortFactory
        MyCapturingFactory = MyTestbench.CapturingFactory
        MyWatcherFactory = MyTestbench.WatcherFactory
        MyDurationFactory = MyTestbench.DurationFactory

        print("Creating and Configuring MAPort...")
        CarMaPort = MyMAPortFactory.CreateMAPort("CarMaPort")

        # Start CarMaker instance using a MAPortConfig .xml file
        CarMaPortConfig = CarMaPort.LoadConfiguration(MAPortConfigFile)
        CarMaPort.Configure(CarMaPortConfig, False)

        # Configure Variables to capture
        print("Creating capture with FileWriter...")
        DemoCapture = CarMaPort.CreateCapture("captureTask")
        DemoVariableList = ["Car.ax", "Car.ay", "Car.az", "DM.Steer.Ang"]
        DemoCapture.Variables = DemoVariableList
        DemoCapture.Downsampling = 50
        # create mdffilewriter
        DemoCaptureWriter = MyCapturingFactory.CreateCaptureResultMDFWriterByFileName("MDFFile")

        # set capture with conditions
        print("Adding Start and StopTrigger...")
        StartDelay = MyDurationFactory.CreateTimeSpanDuration(-2.0)
        DemoStartWatcher = MyWatcherFactory.CreateDurationWatcherByTimeSpan(10.0)
        DemoCapture.SetStartTrigger(DemoStartWatcher, StartDelay)
        DemoStopWatcher = MyWatcherFactory.CreateDurationWatcherByTimeSpan(20.0)
        StopDelay = MyDurationFactory.CreateTimeSpanDuration(2.0)
        DemoCapture.SetStopTrigger(DemoStopWatcher, StopDelay)
        DemoCapture.Start(DemoCaptureWriter)

        print("Starting simulation...")
        # start the testrun
        if CarMaPort.State is not MAPortState.eSIMULATION_RUNNING:
            CarMaPort.StartSimulation("Examples/BasicFunctions/Driver/BackAndForth")

        CarMaPort.WaitForSimEnd(120.0)
        print("Simulation finished. MDF File saved to: " + CarMaPort.Configuration.Project + "/MDFFile.mf4")

    except TestbenchPortException as ex:
        print("TestbenchPortException occured:")
        print("VendorCodeDescription: %s" % ex.VendorCodeDescription)

    finally:
        if DemoCapture != None:
            DemoCapture.Dispose()
            DemoCapture = None
        if CarMaPort != None:
            CarMaPort.Dispose()
            CarMaPort = None
