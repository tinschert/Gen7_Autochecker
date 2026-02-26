import yaml
import os

def find_yaml_file(directory):
    """Sucht die erste .yml-Datei in einem Verzeichnis."""
    if not os.path.exists(directory):
        return None
    
    for file in os.listdir(directory):
        if file.endswith(".yml"):
            return os.path.join(directory, file)
    
    return None

def find_python_env(yaml_file):
    """Liest die YAML-Datei aus und sucht nach dem Python Virtual Environment."""
    if not yaml_file or not os.path.exists(yaml_file):
        print("YAML file not found")
        return
    
    with open(yaml_file, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    
    for item in data.get("additional_files", []):
        if item.get("name") == "Python virtual Environment for ADAS HIL scripts":
            version = item.get("version", "Unknown")
            installation_source = item.get("installation_source", "Unknown")
            print(f"{version},{installation_source}")
            return
    
    print("Not Found,Not Found")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    release_dir = os.path.normpath(os.path.join(script_dir, "..", "..", "..", "..", "Release"))
    yaml_file = find_yaml_file(release_dir)
    find_python_env(yaml_file)