import argparse
import sys,os, subprocess, time

controls_path = os.path.dirname(os.path.abspath(__file__)) + r"\..\..\..\..\Platform\Classe\Scripts\Control"
sys.path.append(controls_path)
from logging_config import logger
import canoe_client_1

import pythoncom

ecu_sysvar_mapping = {'delta1': ['adas_1_sim'],
                      'delta5': ['adas_2_sim'],
                      'mpc': ['fvideo_sim'],
                      'alpha2': ['radar_fc_obj_sim'],
                      'gamma1':['radar_fc_loc_sim'],
                      'cr5':['radar_fl_sim', 'radar_fr_sim', 'radar_rl_sim', 'radar_rr_sim']}


def logWriteWindowErrors(txt_file_path):
    """
    prints the logged write window errors to jenkins console

    Args:
      txt_file_path (str): path to logged txt file

    """
    if os.path.exists(txt_file_path):
        with open(txt_file_path,"r") as file:
            lines = file.readlines()
            if len(lines)>0:
                for line in lines:
                    logger.warning(f"WRITE_WINDOW::- {line.strip()}::")
            file.close()


def reset_vx(repo_path):
    """
    Reset VX by running Hard_Reboot_VX.bat
    """
    try:
        bat_path = os.path.join(repo_path, 'CustomerPrj', 'Classe', 'Scripts', 'Reset_VXbox')
        logger.info("-----Start running Hard_Reboot_VX.bat--------")
        p = subprocess.Popen(["Hard_Reboot_VX.bat"], shell=True, cwd=bat_path, stdout=sys.stdout)
        p.communicate()
        time.sleep(5)
        logger.info("-----END running Hard_Reboot_VX.bat--------")
    except Exception as e:
        logger.error(f"failed to Reset VX, error -> {e}")
        raise Exception(e)
    
def flash_od_baseline(flash_path, ecus):
    """runs flash baseline script in given path"""
    try:
        if not(os.path.exists(flash_path)):
            raise Exception(f'Given Baseline flash path does not exist -> {flash_path}')
        command = rf"X:\Tools\venv\Scripts\python.exe flashbaseline.py --HIL \"{ecus}\""
        logger.info(f"----------START Flashing Script-------------")
        p = subprocess.run(command, shell=True, cwd=flash_path, stdout=sys.stdout, stderr=sys.stderr)

    except Exception as e:
        logger.error(f"failed to flash_od_baseline, error -> {e}")
        raise Exception(e)
    

def validate_flashing(flash_path):
    """validate if flashing succeded"""
    try:
        logs_path = os.path.join(flash_path,'_logs')
        log_files_list = [f for f in os.listdir(logs_path) if f.endswith('.txt')]
        log_files_list = [i for i in log_files_list if 'overall' not in i.lower()]
        failed_flashing = []
        for log in log_files_list:
            log_file = os.path.join(logs_path, log)
            try:
                with open(log_file, 'r', encoding='utf-16') as f:
                    lines = f.readlines()
            except UnicodeError as e:
                try:
                    with open(log_file, 'r', encoding='ascii') as f:
                        lines = f.readlines()
                except UnicodeError as e:
                    logger.error(f'Could not read -> {log} , ERROR-> {e}')
                    continue
            last_15_lines = lines[-15:]
            flashing_success = False
            for line in last_15_lines:
                if ('FLASHING SUCCEDED' in line.upper()) or ('flashing successful' in line.lower()):
                    logger.info(f'FLASHING_INFO#:# {log} -> flashing success #:#')
                    flashing_success = True
                    break
            if not(flashing_success):
                failed_flashing.append(log)
                logger.error(f'FLASHING_FAILED#:# {log} -> flashing failed #:#')
                continue
        
        if failed_flashing:
            raise Exception(f'Flashing failed -> {failed_flashing}')
        else:
            logger.info("----------------FLASHING SUCCESSFUL--------------")
    except Exception as e:
        logger.error(f'Error while validating flashing -> {e}')
        raise Exception(e)
    



    

def main(repo_path, flash_path, ecus):
    p = subprocess.Popen(["powershell.exe", repo_path + "\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
                         stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()
    start_canoe = time.time()

    cfg_path = os.path.join(repo_path, 'RBS_OD.cfg')
    write_errors_path = os.path.join(repo_path, 'write_window.txt')

    reset_vx(repo_path)

    logger.info("Starting CANoe via COM interface")
    canoeClient = canoe_client_1.CANoeClient()
    try:
        canoeClient.openConfiguration(cfg_path)
        canoe_started = time.time()
        logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
        canoeClient.enable_write_window_log(write_errors_path)
        logger.info("Deactivating XCP Devices...")
        xcp_ecus = canoeClient.CANoe.Configuration.GeneralSetup.XCPSetup.ECUs
        for i in range(1, xcp_ecus.Count + 1):
            xcp_ecus.Item(i).Active = False
            time.sleep(0.5)
        logger.info("Deactivated XCP Devices")
        canoeClient.startMeasurement()
        time.sleep(5)

        canoeClient.setVariableToValue("hil_ctrl", "hil_mode", 2)
        time.sleep(2)

        for ecu in ecus.split(" "):
            ecu = ecu.strip().lower()
            for var in ecu_sysvar_mapping.get(ecu, []):
                canoeClient.setVariableToValue("hil_ctrl", var, 2)
                time.sleep(1)

        time.sleep(2)
        flash_od_baseline(flash_path, ecus)

        validate_flashing(flash_path)

    except Exception as e:
        logWriteWindowErrors(write_errors_path)
        logger.error(f"Stop at exception --> {e}")
        raise e
    finally:
        canoeClient.stopMeasurement()
        canoeClient.quitCanoe(False)
        canoeClient = None


if __name__ == '__main__':
    # parse command line arguments
    commandLineParser = argparse.ArgumentParser(description='Flash baseline')

    commandLineParser.add_argument('--ecus', action="store", dest="ecus", required=True,
                                   help="ecu args to be flashed")
    
    commandLineParser.add_argument('--flashing_path', action="store", dest="flashing_path", required=True,
                                   help="Absolute path to flash baseline folder")

    commandLineParser.add_argument('--repo_path', action="store", dest="repo_path", required=True,
                                   help="Absolute path to repo folder")
    arguments = commandLineParser.parse_args()

    ecus = str(arguments.ecus).strip()
    if not(ecus):
        logger.warning("-------No ECUs were given as arguement for flashing-----------")
    else:
        main(arguments.repo_path, arguments.flashing_path, ecus)


    
