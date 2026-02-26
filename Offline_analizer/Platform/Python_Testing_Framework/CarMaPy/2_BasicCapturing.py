#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
#import clr # <- uncomment if you are running a National Instruments Project

sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11")
from ASAM.XIL.Implementation.Testbench import TestbenchFactory
from ASAM.XIL.Interfaces.Testbench.MAPort.Enum.MAPortState import MAPortState
from ASAM.XIL.Interfaces.Testbench.Common.Error.TestbenchPortException import TestbenchPortException
from matplotlib import pyplot as plt

MAPortConfigFile = "Config.xml"

if __name__ == "__main__":
    DemoCapture = None
    CarMaPort = None

    try:
        # Initialise all necessary class instances
        MyTestbenchFactory = TestbenchFactory()
        MyTestbench = MyTestbenchFactory.CreateVendorSpecificTestBench("IPG", "CarMaker", "12.0.2")
        MyMAPortFactory = MyTestbench.MAPortFactory

        print("Creating and Configuring MAPort...")
        CarMaPort = MyMAPortFactory.CreateMAPort("CarMaPort")

        # Start CarMaker instance using a Project directory as Configuration parameter
        CarMaPortConfig = CarMaPort.LoadConfiguration(MAPortConfigFile)
        CarMaPort.Configure(CarMaPortConfig, False)

        # Configure Variables to capture
        print("Creating capture...")
        DemoCapture = CarMaPort.CreateCapture("captureTask")
        DemoVariableList = ["Car.ax", "Car.ay", "Car.az"]
        DemoCapture.Variables = DemoVariableList
        DemoCapture.Downsampling = 50

        # run a couple of TestRuns and capture acceleration data
        TestRuns = ["Examples/BasicFunctions/Driver/BackAndForth",
        	    "Examples/VehicleDynamics/Braking/Braking"]
        i = 0
        for testrun in TestRuns:
            # capture data once the testrun starts
            print("Activate capture...")
            DemoCapture.Start()

            print("Starting simulation...")
            # start the testrun
            if CarMaPort.State is not MAPortState.eSIMULATION_RUNNING:
                CarMaPort.StartSimulation(testrun)

            # Wait for the simulation to end and get the CaptureResult
            print("Waiting for simend and retrieving data...")
            CarMaPort.WaitForSimEnd(120.0)
            Result = DemoCapture.Fetch(False)
            DemoCapture.Stop()
            print("Simulation finished. Saving result to " + CarMaPort.Configuration.Project + f"/graph_{i}.png.")

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
            plt.savefig(f'graph_{i}.png')
            # or show figure on screen
            # plt.show()
            plt.clf()
            i = i+1

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
