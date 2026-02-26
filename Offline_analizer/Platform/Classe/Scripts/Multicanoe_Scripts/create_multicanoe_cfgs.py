import os, sys
import subprocess
import pythoncom
import time

try:
    from Control.logging_config import logger
    from Control import canoe_client_1
except ImportError:
    sys.path.append(os.getcwd() + r"\..\Control")
    from logging_config import logger
    import canoe_client_1


def get_canoe_cfg(target_path):
    for file in os.listdir(target_path):
        if ((".cfg" in file) and ("master" not in file.lower()) and ("slave" not in file.lower()) and not(any(char.isdigit() for char in file))):
            logger.info(f"CANoe configuration path --> {target_path}\\{file}")
            return file


def disable_measurement_setup_nodes(config_path):
    Env_found_flag = False
    Meas_disable_str = "CAN Statistics"

    set_flag = False
    array_dsb_ms = []
    array_store_row = []
    temp_str = 0
    count = 0
    string_arr = ["EndOfComment"]
    str_found = False
    with open(config_path, "r+") as f0:
        f = f0.readlines()
        # print("file:"+str(len(f)))
        for d, line in enumerate(f):
            if (str(f[d]) == Meas_disable_str + "\n"):
                temp_str = d
                while (str(f[d]) != "VDAOGBHSStd 14 Begin_Of_Object\n"):
                    if (string_arr[0] in str(f[d])):
                        count = count + 1
                        str_found = True
                        if (count > 1):
                            array_store_row.append(d + 2)
                    d = d + 1
                array_dsb_ms.append(Meas_disable_str + "\n")
                # print("print of print(array_store_row)",array_store_row)
            elif (d in array_store_row):  # and (str_found == True):
                # print("value of set_flag",set_flag)
                # print("value of d, f[d]",d,f[d])
                if set_flag == False:
                    # if Env_found_flag ==True:
                    #    array_dsb_ms.append("1 0\n")
                    # else:
                    array_dsb_ms.append("0\n")
                    logger.info("Disabled Nodes in measrement Setup of CAN statistics Block")

                str_found = False

            else:
                array_dsb_ms.append(f[d])

    with open(config_path, "w") as f1:
        for i in range(0, len(array_dsb_ms)):
            # f1.write(b[i])
            if "End_Of_Object VGlobalConfiguration 1" not in array_dsb_ms[i]:
                f1.write(array_dsb_ms[i])
            else:
                f1.write("End_Of_Object VGlobalConfiguration 1")
                break


def create_cfgs(adas_hil_folder_path, main3_needed, cfg_ini_file_paths):
    cfg_name = get_canoe_cfg(adas_hil_folder_path)
    if main3_needed:
        cfg_name = cfg_name.replace(".cfg", "_3") + ".cfg"
    main_cfg_path = adas_hil_folder_path + cfg_name
    measurement_nodes_disable_cgf_list = []

    p = subprocess.Popen(
        ["powershell.exe", adas_hil_folder_path + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
        stdout=sys.stdout)
    p.communicate()
    pythoncom.CoInitialize()

    canoeClient = canoe_client_1.CANoeClient()

    for multicanoe_ini in cfg_ini_file_paths:

        canoeClient.openConfiguration(main_cfg_path, skip_cfg_check=True)

        configuration_name = ""

        disable_networks = []
        enable_networks = []

        enable_nodes = []
        disable_nodes = []

        measurement_node_disable = False
        with open(multicanoe_ini, "r") as ini_file:
            for line in ini_file.readlines():
                if "configuration_name=" in line:
                    configuration_name = line.split("=")[-1].strip()

                elif "Node_Enable=" in line:
                    nodes = line.split("=")[-1].strip().split(",")
                    enable_nodes.extend(nodes)
                    enable_nodes = [i.strip() for i in enable_nodes]

                elif "Node_Disable=" in line:
                    nodes = line.split("=")[-1].strip().split(",")
                    disable_nodes.extend(nodes)
                    disable_nodes = [i.strip() for i in disable_nodes]

                elif "Network_Enable=" in line:
                    networks = line.split("=")[-1].strip().split(",")
                    enable_networks.extend(networks)
                    enable_networks = [j.strip() for j in enable_networks]

                elif "Network_Disable=" in line:
                    networks = line.split("=")[-1].strip().split(",")
                    disable_networks.extend(networks)
                    disable_networks = [j.strip() for j in disable_networks]

                elif "disable_measurement_setup_nodes=" in line:
                    temp = line.split("=")[-1].strip().lower()
                    measurement_node_disable = True if "true" in temp else False

        if not (configuration_name):
            logger.warning(f"configuration_name not present in ini file -> {multicanoe_ini}")
            continue
        if main3_needed:
            configuration_name = configuration_name.replace(".cfg", "_3") + ".cfg"
        logger.info(f"Started creating -> {configuration_name}")
        # canoeClient.saveas_cfg(adas_hil_folder_path + r"\\" + configuration_name)
        canoeClient.save_cfg(adas_hil_folder_path + r"\\" + configuration_name)
        time.sleep(1)
        # canoeClient.openConfiguration(adas_hil_folder_path + r"\\" + configuration_name, skip_cfg_check=True)

        if measurement_node_disable:
            measurement_nodes_disable_cgf_list.append(adas_hil_folder_path + r"\\" + configuration_name)

        canoeClient.activate_node(enable_nodes)
        canoeClient.deactivate_node(disable_nodes)

        canoeClient.deactivate_network(disable_networks)
        canoeClient.activate_network(enable_networks)

        canoeClient.save_cfg()
        time.sleep(1)

        logger.info(f"CREATED -> {configuration_name}")

    canoeClient.quitCanoe(False)

    for cfg in measurement_nodes_disable_cgf_list:
        #print(cfg)
        disable_measurement_setup_nodes(cfg)


def createCfg3(quit_canoe=True):
    """
    takes 2.0 cfg as input and creates 3.0 cfg with given changes in 3.0ini file
    Returns:

    """
    try:
        script_path = os.path.dirname(os.path.abspath(__file__))
        adas_hil_folder_path = script_path + r"\..\..\..\..\\"
        ini_path = adas_hil_folder_path + r"\\CustomerPrj\\MultiCANoe\\Multicanoe_main_3\\canoe_cfg_parameter_main3.ini"

        main_cfg_path = adas_hil_folder_path + get_canoe_cfg(adas_hil_folder_path)

        user_files_list = []
        with open(ini_path, "r") as ini_file:
            for line in ini_file.readlines():
                if "configuration_name=" in line:
                    configuration_name = line.split("=")[-1].strip()

                elif "user_files=" in line.lower():
                    usrfiles = line.split("=")[-1].strip().split(",")
                    user_files_list.extend(usrfiles)
                    user_files_list = [i.strip() for i in user_files_list]

        p = subprocess.Popen(
            ["powershell.exe", adas_hil_folder_path + r"\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"],
            stdout=sys.stdout)
        p.communicate()
        pythoncom.CoInitialize()

        canoeClient = canoe_client_1.CANoeClient()

        canoeClient.openConfiguration(main_cfg_path, skip_cfg_check=True)
        time.sleep(1)
        canoeClient.save_cfg(adas_hil_folder_path + r"\\" + configuration_name)
        time.sleep(1)

        userfiles_new_path = adas_hil_folder_path + r"\Platform\Classe\Scripts\Orchestration_scripts\\"
        userfiles_new_path = os.path.abspath(userfiles_new_path)
        if user_files_list:
            result = canoeClient.removeUserFile(user_files_list)
            if result==False:
                raise Exception(f"Error while removing files")
            user_files_list = [userfiles_new_path+"\\"+file for file in user_files_list]
            result2 = canoeClient.addUserFile(user_files_list)
            if result2==False:
                raise Exception(f"Error while adding files")

        # change capl file for cm_control
        canoeClient.changeFileOfNode("cm_control", os.path.abspath(adas_hil_folder_path + r"\Platform\Carmaker\Nodes\cm_control_3.can"))

        canoeClient.save_cfg()
        time.sleep(1)

        logger.info(f"CREATED -> {configuration_name}")

        if quit_canoe:
            canoeClient.quitCanoe(False)

    except Exception as e:
        logger.error(f"Error while creating main cfg 3.0 -> {e}")
        raise Exception(f"Error while creating main cfg 3.0 -> {e}")


def create_multicanoe_main(main3_needed=False):
    try:
        script_path = os.path.dirname(os.path.abspath(__file__))
        adas_hil_folder_path = script_path + r"\..\..\..\..\\"
        cus_folder_path = adas_hil_folder_path + r"\\CustomerPrj\\MultiCANoe"

        # main_cfg_path = adas_hil_folder_path + get_canoe_cfg(adas_hil_folder_path)

        cfg_ini_file_paths = []

        for (dirpath, dirnames, filenames) in os.walk(cus_folder_path):
            for file in filenames:
                if ".ini" in file.lower() and "main" not in file.lower():
                    cfg_ini_file_paths.append(dirpath + r"\\" + file)

        create_cfgs(adas_hil_folder_path, main3_needed, cfg_ini_file_paths)
    except Exception as e:
        logger.error(f"Error while creating multicanoe -> {e}")
        raise Exception(f"Error while creating multicanoe -> {e}")








