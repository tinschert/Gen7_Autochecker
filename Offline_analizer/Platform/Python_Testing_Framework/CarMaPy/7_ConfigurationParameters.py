#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
#import clr # <- uncomment if you are running a National Instruments Project

sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11")
from ASAM.XIL.Implementation.Testbench import TestbenchFactory
from ASAM.XIL.Interfaces.Testbench.Common.Error.TestbenchPortException import TestbenchPortException
from ASAM.XIL.Interfaces.Testbench.MAPort.Enum.MAPortState import MAPortState
from matplotlib import pyplot as plt
MAPortConfigFile = "Config.xml"

if __name__ == "__main__":
    CarMaPort = None
    DemoCapture = None

    try:
        # Initialize all necessary class instances
        MyTestbenchFactory = TestbenchFactory()
        MyTestbench = MyTestbenchFactory.CreateVendorSpecificTestBench("IPG", "CarMaker", "12.0.2")
        MyMAPortFactory = MyTestbench.MAPortFactory
        MyWatcherFactory = MyTestbench.WatcherFactory
        MyDurationFactory = MyTestbench.DurationFactory

        print("Creating and Configuring MAPort...")

        CarMaPort = MyMAPortFactory.CreateMAPort("CarMaPort")
        # Start CarMaker instance using a Project directory as Configuration parameter
        CarMaPortConfig = CarMaPort.LoadConfiguration(MAPortConfigFile)
        CarMaPort.Configure(CarMaPortConfig, False)

        # Configure a capture with a DurationWatcher
        # to stop the capturing after 10 seconds
        print("Creating capture...")
        DemoCapture = CarMaPort.CreateCapture("captureTask")
        DemoVariableList = ["Car.ax", "Car.ay", "Car.az"]
        DemoCapture.Variables = DemoVariableList
        DemoCapture.Downsampling = 10
        # DurationWatcher
        print("Adding Start and StopTrigger...")
        DemoStartWatcher = MyWatcherFactory.CreateDurationWatcherByTimeSpan(10.0)
        StartDelay = MyDurationFactory.CreateTimeSpanDuration(-1.0)
        DemoCapture.SetStartTrigger(DemoStartWatcher, StartDelay)
        StopDelay = MyDurationFactory.CreateTimeSpanDuration(1.0)
        DemoStopWatcher = MyWatcherFactory.CreateDurationWatcherByTimeSpan(30.0)
        DemoCapture.SetStopTrigger(DemoStopWatcher, StopDelay)
        DemoCapture.Start()

        print("Downloading parameter sets...")
        CarMaPort.DownloadParameterSets(["Examples/VehicleDynamics/Handling/Racetrack_Hockenheim",
                                          "Examples/Demo_Audi_R8",
                                          "Examples/RT_235_55R18",
                                          "Examples/Caravan"])

        print("Starting simulation...")
        if CarMaPort.State is not MAPortState.eSIMULATION_RUNNING:
            CarMaPort.StartSimulation()

        # Wait for the trigger to stop the capture
        # this is signaled by passing 'True' to the Fetch call
        Result = DemoCapture.Fetch(True)
        # Stop the simulation after capture is stopped
        CarMaPort.StopSimulation()
        print("Simulation finished. Result saved to: " + CarMaPort.Configuration.Project + "/mygraph.png")

        # Visualization of capture result using matplotlib
        XAxisValues = Result.GetSignalGroupValue().XVector.Value

        AccXSignalValue = Result.ExtractSignalValue("Car.ax")
        AccXValues = AccXSignalValue.FcnValues.Value

        AccYSignalValue = Result.ExtractSignalValue("Car.ay")
        AccYValues = AccYSignalValue.FcnValues.Value

        AccZSignalValue = Result.ExtractSignalValue("Car.az")
        AccZValues = AccZSignalValue.FcnValues.Value

        plt.xlabel("Seconds")
        plt.ylabel("m/s^2")
        plt.xlim(min(XAxisValues), max(XAxisValues))
        plt.plot(XAxisValues, AccXValues, 'r')
        plt.plot(XAxisValues, AccYValues, 'g')
        plt.plot(XAxisValues, AccZValues, 'b')
        # save figure to file
        plt.savefig('mygraph.png')

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
