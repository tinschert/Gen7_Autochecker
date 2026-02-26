import yaml
import traceback


def parse_yaml(target_pc, yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.full_load(file)

    vector_target_list = {'Vector CANoe': 'CANoeTBE.exe',
                      'Vector CANape': 'CANape64.exe'}

    yaml_sw_target_list = ("CarMaker Complete Pack", "Vector CANoe CarMaker AddOn", "Solectrix proFrame")

    try:
        yaml_vector_sw = []
        yaml_py_libs = {}
        yaml_sw = []
        yaml_additional_files = []

        for key,value in data.items():
            if key == "software":
                for item in value:
                    if item['name'] != "Python Libraries":
                        if item['name'] in vector_target_list.keys():
                            custom_dict = {'name': item['name'], 'executable': vector_target_list[item['name']], 'version': item['version'], 'target': item['installed_on']}
                            if target_pc in custom_dict['target']:
                                yaml_vector_sw.append(custom_dict)
                        elif item['name'] in yaml_sw_target_list:
                            cm_custom_dict = {'name': item['name'], 'version': item['version'], 'target': item['installed_on']}
                            if target_pc in list(cm_custom_dict['target'][0].keys()):
                                yaml_sw.append(cm_custom_dict)
                    elif item['name'] == "Python Libraries":
                        for py_dict in item['libraries']:
                            if target_pc in py_dict['installed_on']:
                                yaml_py_libs[py_dict['name']] = str(py_dict['version'])
            elif key == "additional_files":
                for item in value:
                    if isinstance(item['installed_on'][0], dict):
                        target_keys = item['installed_on'][0].keys()
                        if target_pc in target_keys:
                            yaml_add_files_dict = {'name': item['name'], 'target': target_pc, 'path': item['installed_on'][0][target_pc]}
                            if yaml_add_files_dict['path']:
                                yaml_additional_files.append(yaml_add_files_dict)

    except Exception as e:
        traceback.print_exc()

    return yaml_vector_sw, yaml_py_libs, yaml_sw, yaml_additional_files
