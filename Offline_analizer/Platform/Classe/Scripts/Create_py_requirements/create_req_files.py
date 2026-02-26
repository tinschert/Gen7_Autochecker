import yaml
import os


def parse_yaml(target_pc, yaml_file) -> dict:
    """ Main function to create py req files
        Args:
              target_pc: target PC which shall be searched for inside BOM file
              yaml_file: path: Path to the yaml BOM file
        Returns: Dict of libraries required for target PC
         """
    with open(yaml_file, 'r') as file:
        data = yaml.full_load(file)
    try:
        yaml_py_libs = {}
        for key, value in data.items():
            if key == "software":
                for item in value:
                    if item['name'] == "Python Libraries":
                        for py_dict in item['libraries']:
                            if target_pc in py_dict['installed_on']:
                                yaml_py_libs[py_dict['name']] = str(py_dict['version'])

    except Exception as e:
        print(f"General exception --> {e}")
        raise e

    return yaml_py_libs


def create_req_files(path):
    """ Main function to create py req files
    Args:
          path: Path to the yaml BOM file
    Returns: None
     """

    TARGETS = ["GUI_PC", "RT_Rack", "Rendering_PC", "Datalogger", "Single_PC"]
    for target in TARGETS:
        libs = parse_yaml(target, path)
        if libs:
            with open(target + "_py_requirements.txt", 'w') as file:
                for key, value in libs.items():
                    if key != "pip":
                        file.write(f"{key}=={value}\n")
            print(f"Created --> {target}_py_requirements.txt")


if __name__ == "__main__":

    rel_path = r"..\..\..\..\Release"
    yml_files = [f for f in os.listdir(rel_path) if f.endswith(".yml")]
    if yml_files:
        abs_path = os.path.join(rel_path, yml_files[0])
        create_req_files(abs_path)
        print("Finished creating python req files.")
    else:
        print("No .yml files found in Release folder!!!")
