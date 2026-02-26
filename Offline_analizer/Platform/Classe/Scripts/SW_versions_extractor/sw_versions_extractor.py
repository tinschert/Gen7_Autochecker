from win32api import GetFileVersionInfo, LOWORD, HIWORD
import os, sys
import subprocess, io
from itertools import chain
#import gitinfo
import socket
import winreg
import psutil
import wmi
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
import logging
import read_yaml

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(filename)s] [%(message)s]')

list_of_sw = {'Vector Canoe': 'CANoeTBE.exe',
              'Vector CANape': 'CANape64.exe'}


def get_canoe_commit() -> list:
    """ Get current canoe commit info
    Args:
    Returns (list):
          Git repo data
    """
    git_repo_summary = gitinfo.get_git_info()
    git_repo_data = [(key, value) for key, value in git_repo_summary.items()]
    return git_repo_data


def get_sw_paths(data):
    """ Get full paths of app for which version shall be retrieved
     Args:
     Returns (list):
         Full software paths
    """

    for index, sw in enumerate(data):
        found = False
        exe = sw['executable']
        prg_files_path = [r"C:\Program Files", r"C:\Program Files (x86)"]
        for path, subdirs, files in chain.from_iterable(os.walk(path) for path in prg_files_path):
            for name in files:
                if name.endswith(exe):
                    sw['path'] = os.path.join(path, name)
                    data[index] = sw
                    found = True
            if not found:
                sw['path'] = None
                data[index] = sw
    return data


def get_version_number(filename):
    """
    Get softawre version of given exe
    Args:
         filename (str) : Name of the exe
    Returns:
        Version of the exe
    """
    try:
        info = GetFileVersionInfo(filename, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
    except:
        return "Unknown version"


def get_hostnames():
    """ Deprecated """
    domains_list = []
    hils_dict = {
        "FE-Z1R59.lr.de.bosch.com": "FE-C-00968.lr.de.bosch.com",
        "FE-C-005CP.lr.de.bosch.com": "LR-C-002FV.lr.de.bosch.com",
        "WE-C-0003R.lr.de.bosch.com": "LR-C-002MR.lr.de.bosch.com",
        "FE-Z1VJ4.fe.de.bosch.com": "ABT-C-000KJ.fe.de.bosch.com",
        # "FE-Z1VJ4.fe.de.bosch.com": "LR-Z10002.fe.de.bosch.com",
        "fe-c-005dl.fe.de.bosch.com": "FE-Z1VXQ.fe.de.bosch.com",
        "ABTZ0NQC.abt.de.bosch.com": "ABT-C-000KK.abt.de.bosch.com"
    }

    win_hostname = socket.gethostname()
    win_ip = socket.gethostbyname(win_hostname)
    domains_list.append(f"Windows GUI PC domain/IP = {win_hostname}[{win_ip}]{new_line}")

    if win_hostname in hils_dict:
        try:
            linux_hostname = hils_dict[win_hostname]
            linux_ip = socket.gethostbyname(linux_hostname)
            domains_list.append(f"Linux PC domain/IP = {linux_hostname}[{linux_ip}]")
            return domains_list
        except Exception as e:
            logging.warning(f"Unable to get Linux IP address --> {e}")
    else:
        logging.warning("Unknown windows GUI PC")


def get_project():
    """
    Get the current project for which the script is executed
    Args:
    Returns (str):
        Name of the project
    """
    main_repo_path = os.path.dirname(os.path.abspath(__file__)) + '/../../../..'
    for (dirpath, dirnames, filenames) in os.walk(main_repo_path):
        for file in filenames:
            if ".cfg" in file:
                found_file = str(file).split(".")[0]
                project = found_file.split('_')[1]
                logging.info(f"Local repository project is --> {project}")
                return project


def get_installed_software():
    software_list = []
    uninstall_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, uninstall_key) as key:
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                subkey_name = winreg.EnumKey(key, i)
                with winreg.OpenKey(key, subkey_name) as subkey:
                    try:
                        software_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        software_list.append(software_name)
                    except FileNotFoundError:
                        pass
    except Exception as e:
        print("Error:", e)

    return software_list


def get_proframe_data(data, target):
    proframe_data = ["\n" + 40 * "#" + " Proframe data " + 40 * "#" + "\n"]
    target_key = list(data['target'][0].keys())
    if target_key[0] == target:
        path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\proFRAME"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            num_subkeys, num_values, last_modified = winreg.QueryInfoKey(key)

            for i in range(num_values):
                value_name, value_data, value_type = winreg.EnumValue(key, i)
                if value_name == "DisplayVersion":
                    if value_data == data['version']:
                        proframe_data.append(f"Solectrix proFrame installed version --> {value_data}\n")
                    else:
                        proframe_data.append(f"[WARNING] Solectrix proFrame installed version --> {value_data}, expected {data['version']}\n")
                elif value_name == "UninstallString":
                    path = value_data.rsplit("\\", 1)[0]
                    path_fixed = path.replace('"','')
                    if path_fixed.lower() == data['target'][0][target].lower():
                        proframe_data.append(f"Solectrix proFrame install path --> {value_data}\n")
                    else:
                        proframe_data.append(f"[WARNING] Solectrix proFrame install path --> {path}, expected {data['target'][0][target]}\n")
            winreg.CloseKey(key)
        except Exception as e:
            print("Error:", e)
        return proframe_data

def get_pc_info():
    # Get CPU information
    pc_info = []

    cpu_info = {
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max frequency": f"{psutil.cpu_freq().max:.2f}Mhz",
        "Min frequency": f"{psutil.cpu_freq().min:.2f}Mhz",
        "Current frequency": f"{psutil.cpu_freq().current:.2f}Mhz",
        "CPU usage per core": psutil.cpu_percent(interval=1, percpu=True)
    }

    pc_info.append("############## PC INFO ###################\n")
    pc_info.append(f"PC name: {socket.gethostname()}\n")
    for key, value in cpu_info.items():
        pc_info.append("CPU Information:\n")
        pc_info.append(f"{key}: {value}\n")

    # Get memory information
    memory_info = {
        "Total": f"{psutil.virtual_memory().total / (1024 ** 3):.2f}GB",
        "Available": f"{psutil.virtual_memory().available / (1024 ** 3):.2f}GB",
        "Used": f"{psutil.virtual_memory().used / (1024 ** 3):.2f}GB",
        "Percentage": f"{psutil.virtual_memory().percent}%"
    }

    pc_info.append("\nMemory Information:\n")
    for key, value in memory_info.items():
        pc_info.append(f"{key}: {value}\n")

    # Get disk information
    disk_info = psutil.disk_usage('/')
    pc_info.append("\nDisk Information:\n")
    pc_info.append(f"Total: {disk_info.total / (1024 ** 3):.2f}GB\n")
    pc_info.append(f"Used: {disk_info.used / (1024 ** 3):.2f}GB\n")
    pc_info.append(f"Free: {disk_info.free / (1024 ** 3):.2f}GB\n")
    pc_info.append(f"Percentage: {disk_info.percent}%\n")

    # Get network interfaces and their addresses
    net_interfaces = psutil.net_if_addrs()
    pc_info.append("\nNetwork Information:\n")
    for key, value in net_interfaces.items():
        pc_info.append(f"{key}: {value}\n")

    return pc_info


def get_windows_share_info():
    # Create a connection to the WMI service on the local machine
    c = wmi.WMI()

    # Query shared folders
    shared_folders = c.Win32_Share()
    shared_info = ['\n' + 20 * '#' + " Shared Folders " + 20 * '#' + '\n']
    # Print shared folder information
    for folder in shared_folders:
        shared_info.append(f"Name: {folder.Name}\n")
        shared_info.append(f"Path: {folder.Path}\n")
        shared_info.append(f"Description: {folder.Description}\n")
        shared_info.append(f"Status: {folder.Status}\n\n")

    return shared_info


def check_additional_files_paths(targets: list) -> list:
    """ Check addtional files path on target """
    try:
        check_path_list = []
        for target in targets:
            file_path = target['path'] + "\\" + target['name']
            if os.path.exists(file_path):
                check_path_list.append(file_path + " --> OK\n")
            else:
                check_path_list.append(file_path + " --> File Not Found!!!\n")
        return check_path_list
    except Exception as e:
        logging.error(e)

def generate_html_from_list(strings):
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HIL INFO</title>
    </head>
    <body>
        <h1>ADAS_HIL_INFO</h1>
        <ul>
            {}
        </ul>
    </body>
    </html>
    """

    list_items = ""
    for string in strings:
        if "WARNING" in string or "NOT FOUND!" in string:
            list_items += f'<li style="color:red;">{string}</li>\n'
        else:
            list_items += f'<li>{string}</li>\n'

    html_content = html_template.format(list_items)
    return html_content


def main_sequence(target, customer, yaml):
    text = []
    new_line = "\n"

    try:
        ''' Retrieve PC INFO '''
        pc_info = get_pc_info()
        text.extend(pc_info)
        share_info = get_windows_share_info()
        text.extend(share_info)

        data_vector_sw, data_py_libs, data_sw, data_additional_files = read_yaml.parse_yaml(target, yaml)
        # """ Retrieve project """
        # text.append(40 * "#" + " Current project " + 40 * "#" + "\n")
        # project_name = get_project()
        # text.append(f"Project is {project_name}{new_line}")

        """ Retrieve Vector software versions """
        logging.info("Retrieve Vector software installation paths and versions")
        if data_vector_sw:
            data = get_sw_paths(data_vector_sw)
            text.append("\n" + 40 * "#" + " Vector Software " + 40 * "#" + "\n")
            for entry in data:
                if entry['path'] is not None:
                    version = ".".join([str(i) for i in get_version_number(entry['path'])])
                    main_version = version.split('.')[:3]
                    if main_version == entry['version'].split('.')[:3]:
                        text.append(f"{entry['name']} = {entry['path']} [{".".join(main_version)}]{new_line}")
                    else:
                        text.append(
                            f"[WARNING] {entry['name']} = {entry['path']} .Expected version [{entry['version']}], found {version}{new_line}")
                else:
                    text.append(f"{entry['name']} = {entry['path']} --> WARNING [CanoeTBE version not installed]{new_line}")

        """ Retrieve Python Version and Libraries """
        lib_list = {}
        logging.info("Retrieve Python version and libraries")
        text.append("\n" + 40 * "#" + " Python Version and Libraries " + 40 * "#" + "\n")
        python_version_major = 3
        python_version_minor = 12
        python_version_micro = 4
        py_version_major = sys.version_info.major
        py_version_minor = sys.version_info.minor
        py_version_micro = sys.version_info.micro
        if python_version_major != py_version_major:
            text.append("[ERROR] --> NO PYTHON 3 VERSION INSTALLED")
        elif python_version_minor != py_version_minor or python_version_micro != py_version_micro:
            text.append(f"[WARNING] --> Wrong python version.Expected {python_version_major}.{python_version_minor}.{python_version_micro}, found /"
                        f"{sys.version}{new_line}.Libraries will not be extracted until correct Python version is detected!!!")
        else:
            text.append(f"Current Python Version: {sys.version}{new_line}")
            process = subprocess.Popen([r"X:\Tools\venv\Scripts\python.exe", "-m", "pip", "list", "--format=freeze"], stdout=subprocess.PIPE)
            for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
                lib = line.split("==")[0]
                ver = line.split("==")[1].split("\n")[0]
                lib_list[lib] = ver

            """  Compare yaml py libs extract against target PC libraries """
            for key in data_py_libs:
                if key in list(lib_list.keys()):
                    if data_py_libs[key] == lib_list[key]:
                        version = lib_list[key]
                        text.append(key + "==" + version + "\n")
                    else:
                        version = lib_list[key]
                        version_yaml = data_py_libs[key]
                        text.append(f"{key}=={version} [WARNING --> Expected {version_yaml}]\n")
                else:
                    text.append(f"{key} == NOT FOUND!\n")

        """ Check additional files paths """
        text.append("\n" + 40 * "#" + " Additional files path check " + 40 * "#" + "\n")
        add_paths = check_additional_files_paths(data_additional_files)
        text.extend(add_paths)
        text.append(new_line)

        ''' Retrieve custom installed software '''
        if customer == "FORD":
            for sw in data_sw:
                if sw['name'] == "Solectrix proFrame":
                    proframe_info = get_proframe_data(sw, target)
                    text.extend(proframe_info)

        ''' Retrieve installed software '''

        installed_software = get_installed_software()
        text.append(f"\n############## Installed SW on {target} PC #################\n")
        for software in installed_software:
            text.append(software + '\n')

        """ Retrieve Canoe Repo current working commit """
        # logger.info("Retrieve Canoe repo current working commit information")
        # text.append("\n" + 40 * "#" + " CANoe repo commit " + 40 * "#" + "\n")
        # repo_data = get_canoe_commit()
        # for data in repo_data:
        #     text.append(f'{data[0]} = {data[1]}{new_line}')

        # """ Retrieve Windows GUI pc domain/IP and linux domain/IP address """
        # logger.info("Retrieve Windows GUI pc domain/IP and linux domain/IP address")
        # text.append("\n" + 40 * "#" + " GUI PC and Linux PC hostnames/ip " + 40 * "#" + "\n")
        # hosts_data = get_hostnames()
        # text.extend(hosts_data)

        """ Write the log file """
        logging.info("Write the log file")
        test_to_write = "".join(text)
        dir_path = r"C:\HIL_INFO"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(r"C:\HIL_INFO\ADAS_HIL_info.txt", "w", encoding="utf-8") as f:
            f.write(test_to_write)
        logging.info(r"Please find the log in C:\HIL_INFO\ADAS_HIL_info.txt")

        html_content = generate_html_from_list(text)

        with open(r"C:\HIL_INFO\ADAS_HIL_INFO.html", "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        logging.info("HTML file generated successfully.")

        return True
    except Exception as e:
        logging.error(f"Runtime error --> {e}")
        traceback.format_exc()
        return False


if __name__ == "__main__":
    main_sequence("PC")
