import os
from pathlib import Path
import sys
from rbs_and_canoe_tests import get_canoe_cfg

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import subprocess
import pythoncom
import time
import canoe_client_1


if __name__ == '__main__':
    script_path = os.path.abspath(__file__)
    script_path_obj = Path(script_path)
    desired_path = list(script_path_obj.parts)[:script_path_obj.parts.index("Platform")]
    customer_path = Path(*desired_path)

    copy_folder_script_finished_file_path = r"D:\CarMaker_Shared\canoe_start_ready.txt"
    if os.path.exists(copy_folder_script_finished_file_path):
        os.remove(copy_folder_script_finished_file_path)
        logger.info(f"file already exists {copy_folder_script_finished_file_path} has been deleted now.")
    canoe_cfg = get_canoe_cfg(customer_path)
    cfg_full_path = customer_path / canoe_cfg
    p = subprocess.Popen(["powershell.exe", str(customer_path) + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    try:
        canoeClient.openConfiguration(cfg_full_path)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        # Wait until copy_folder_script_finished_file_path is created and contains '1'
        while True:
            if os.path.exists(copy_folder_script_finished_file_path):
                with open(copy_folder_script_finished_file_path, 'r') as file:
                    content = file.read().strip()
                    if content == '1':
                        logger.info(f"{copy_folder_script_finished_file_path} contains '1'. virtual environment deployment is done!!")
                        break
            time.sleep(30)  # Check every 30 seconds
    except Exception as e:
        logger.error(f"An error occurred : {str(e)}")
        raise
    finally:
        canoeClient.quitCanoe(False)
        canoeClient = None
