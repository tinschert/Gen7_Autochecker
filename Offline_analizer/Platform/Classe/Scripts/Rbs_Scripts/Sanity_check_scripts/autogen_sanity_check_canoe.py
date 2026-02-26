import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\..\Control")
import canoe_client_1
from logging_config import logger
import subprocess, time
import pythoncom

import argparse



def run_canoe(canoe_cfg_path, adas_hil_repo_path):
    p = subprocess.Popen(["powershell.exe", adas_hil_repo_path + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()
    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    write_errors_path = adas_hil_repo_path + r"\write_window.txt"
    try:
        canoeClient.openConfiguration(canoe_cfg_path)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        time.sleep(1)
        canoeClient.enable_write_window_log(write_errors_path)
        CAPL = canoeClient.CANoe.CAPL
        try:
            time.sleep(5)
            logger.info("Start of compilation")
            CAPL.Compile()
            logger.info("End of compilation")
        except:
            pass
        result_object = CAPL.CompileResult
        result_status = result_object.Result
        if result_status==0:
            logger.info(f"Compilation SUCCESS for {canoe_cfg_path}")
        else:
            result_error = result_object.ErrorMessage
            logger.error(f"Compilation FAILED for {canoe_cfg_path}")
            logger.error(result_error)
            raise Exception(f"COMPILATION FAILED:\n\t{result_error.replace('\n', '\n\t\t')}")
        canoeClient.quitCanoe(False)
    except Exception as e:
        logger.error(f"Stop at exception --> {e}")
        canoeClient.quitCanoe(False)
        raise e


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Config path')

    commandLineParser.add_argument('--canoe_cfg_path', action="store", dest="canoe_cfg_path", required=True, help="path to canoe cfg")
    commandLineParser.add_argument('--adas_hil_repo_path', action="store", dest="adas_hil_repo_path", required=True, help="path to canoe cfg")

    arguments = commandLineParser.parse_args()

    run_canoe(arguments.canoe_cfg_path, arguments.adas_hil_repo_path)
    
    







