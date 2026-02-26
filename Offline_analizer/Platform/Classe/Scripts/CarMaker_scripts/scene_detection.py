from movienxapi.Util import Logger
from movienxapi import Info
from movienxapi.ViewManagement import View
from movienxapi.Util import apo
from movienxapi.SceneAccess import Scene
import os
from datetime import datetime


def create_log_file(message):
    """Create a log file with the current date and time.
    If log_dir doesn't exist, use default_dir."""

    if os.path.exists(r"X:"):
        path = r"X:"
    else:
        path = fr"D:\CarMaker_Shared"

    # Create a log filename with the current datetime
    log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
    log_file_path = os.path.join(path, log_filename)

    """Write a log message to the specified log file."""
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


def set_status_in_file(name, state):
    if os.path.exists(r"X:"):
        path = fr"X:\{name}"
    else:
        path = fr"D:\CarMaker_Shared\{name}"

    # Write current Rendering PC status in file
    with open(path, mode='w') as file:
        file.write(str(state))


def testrun_start_at_begin():
    status = True
    Logger.info("Callback SceneLoadAtBegin triggered.")
    set_status_in_file("movienx_scene_status.txt", "0")

    if apo.is_connected():
        Logger.info(f"Connected host and pid: {apo.get_host()}:{apo.get_pid()}")
        Logger.info(f"Apo Data Rate: {apo.get_data_rate()}")
    else:
        Logger.error(f"No servers found on host {apo.get_host()} with {apo.get_pid()}")
        create_log_file(f"No servers found on host {apo.get_host()} with {apo.get_pid()}")
        status = False

    # Get test case name
    scene = Scene.get_testrun_file_path()
    if scene:
        Logger.info(f"Loaded {scene}")
    else:
        Logger.error(f"Can't load {scene}.")
        create_log_file(f"Test case {scene} was not loaded!!!")
        status = False

    # Get Camera main view
    main_view = View.get(0)
    if main_view.is_present():
        Logger.info("Main View detected!")
    else:
        Logger.error("Main View not present!")
        create_log_file(f"Main view {main_view} was not loaded!!!")
        status = False

    if status is True:
        set_status_in_file("movienx_scene_status.txt", "1")
    else:
        set_status_in_file("movienx_scene_status.txt", "2")


def testrun_end():
    set_status_in_file("movienx_scene_status.txt", "0")



