##############################################################################################################
#   Date        Author              Change History
#   NA          Jim Fron            Created for RALO 0.14
#   05.05.23    Parin K.            Updated for RALO 1.2
#   05.11.23    Parin K.            Added the Datetime
#   30.06.23    Plamen P.& Pablo F. Complete rework for HIL automation
#   07.05.23    Parin K.            Changed the sys.path.append to 1.3
#   18.07.23    Pablo F.            Update to 1.3 for HIL automation
#   21.08.23    Anton R.            Update to 1.4 for HIL automation
#   16.11.23    Anton R.            Update to 1.5 for HIL automation
#   20.03.24    Pablo F.            Update to 1.6 for HIL automation
#   11.04.24    Plamen P.& Pablo F. Complete rework for HIL automation including Env Variables
#   07.06.24    Plamen P.& Pablo F. Bugfix for Environment Variables
##############################################################################################################
# !/usr/bin/env python3


# Add location of the HMI Control modules to the search path
import sys, os
from datetime import datetime
import time


def set_status_in_file(path, state):
    with open(path, mode='w') as file:
        file.write(state)

def conduct_measurement(filename, target, ralo_version):
    try:
        os.environ["PATH"] += f"C:/Program Files/ETAS/RALO{ralo_version}/bin"
        sys.path.append(f"C:\\Program Files\\ETAS\\RALO{ralo_version}\\usr\\lib\\python3\\dist-packages")
        time.sleep(1)
        import pyhmicontrolclient as hcc
        print("Script Start: " + str(datetime.now()))
        # Read a Measurement Configuration from File
        reader = hcc.MeasurementConfigurationReader()
        mconfig = reader.read(filename)

        mcontrol = hcc.MeasurementControl()
        # List of Services
        datasources = mcontrol.discoverSources()

        if len(datasources) != 0:
            src = datasources[0]
            svcl = mcontrol.getAvailableServices(src)
            for svc in svcl:
                print(svc)
        else:
            # If the lenght of datasources is "0" it means that the measurement is invalid
            set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "2")
            raise
        # Set the recording path and filename template for the measurement
        datasinks = mcontrol.discoverSinks()
        # Resolve the MT network topology and check if all resources are available
        mcontrol.resolve(mconfig)

        # Generate a measurement session from the measurement configuration
        session = mcontrol.initSession(mconfig)
        print("InitSession called: " + str(datetime.now()))

        # Start the measurement
        session.start()
        x = mcontrol.getAvailableSessions()
        print("startSession called: " + str(datetime.now()))
        if target == 'vGETK':
            mcontrol.detach(session)
        set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "1")
        input("Recording...")
    except Exception as e:
        print("error occurred during operation:")
        print(e)
        set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "2")
        raise


def stop_measurement(ralo_version):
    # Stop the measurement
    os.environ["PATH"] += f"C:/Program Files/ETAS/RALO{ralo_version}/bin"
    sys.path.append(f"C:\\Program Files\\ETAS\\RALO{ralo_version}\\usr\\lib\\python3\\dist-packages")
    time.sleep(1)
    import pyhmicontrolclient as hcc
    mcontrol = hcc.MeasurementControl()
    uuids = mcontrol.discoverActiveSessions()
    if uuids:
        print(f"Found UUID --> {uuids[0]}")
        # Terminate the measurement and remove the session object
        if uuids:
            mcontrol.terminate(uuids[0])
            print("TerminateSession called: " + str(datetime.now()))
    else:
        print(f"No UUID Found")
        set_status_in_file(r"D:\vGETK_Trace\vGETK_Scripts_Datalogger\vGETK_status.txt", "2")
        return



if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} json-file start/stop")
        exit(-1)

    filename = sys.argv[1]
    action = sys.argv[2]
    target = sys.argv[3]
    ralo_version = sys.argv[4]
    if action == "start":
        conduct_measurement(filename, target, ralo_version)
    elif action == "stop":
        stop_measurement(ralo_version)
    else:
        print("Wrong parameter!!! Use start or stop.")
