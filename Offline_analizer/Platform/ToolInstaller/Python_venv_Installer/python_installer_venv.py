import yaml
import os
import shutil
import subprocess
import sys

def find_libraries_installed_on_gui_pc(file_path):
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        libraries_on_gui_pc = []

        if 'software' in data:
            for software in data['software']:
                if 'libraries' in software:
                    for library in software['libraries']:
                        if 'installed_on' in library:
                            libraries_on_gui_pc.append({
                                'library_name': library['name'],
                                'version': library['version'],
                                'installation_source': library['installation_source']
                            })
        return libraries_on_gui_pc
    except FileNotFoundError:
        print(f"Error: File '{file_path}' was not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error loading the YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

def copy_file(source_path):
    try:
        if os.path.isfile(source_path):
            current_directory = os.path.dirname(os.path.realpath(__file__))
            destination_item = os.path.join(current_directory, os.path.basename(source_path))
            shutil.copy2(source_path, destination_item)
            print(f"File '{source_path}' was copied to '{current_directory}'.")
        else:
            print(f"Warning: {source_path} is not a valid file.")
    except Exception as e:
        print(f"Error copying the file: {e}")

def create_venv():
    try:
        venv_dir = r'X:\tools\venv'
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment in '{venv_dir}'...")
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        else:
            print(f"Virtual environment already exists in '{venv_dir}'.")
    except Exception as e:
        print(f"Error creating the virtual environment: {e}")
        sys.exit(1)

def install_libraries_in_venv(libraries):
    try:
        venv_python = r'X:\tools\venv\Scripts\python.exe'
        if not os.path.exists(venv_python):
            print(f"Error: The virtual environment was not created correctly.")
            sys.exit(1)
        
        current_directory = os.path.dirname(os.path.realpath(__file__))
        for item in os.listdir(current_directory):
            if item.endswith(".whl"):
                wheel_file = os.path.join(current_directory, item)
                print(f"Installing library from '{wheel_file}'...")
                subprocess.check_call([venv_python, "-m", "pip", "install", wheel_file])
        
        for lib in libraries:
            install_source = lib['installation_source']
            if install_source.startswith('pip install'):
                lib_name_version = f"{lib['library_name']}=={lib['version']}"
                print(f"Installing library with pip: {lib_name_version}...")
                subprocess.check_call([venv_python, "-m", "pip", "install", lib_name_version])
    except Exception as e:
        print(f"Error installing libraries: {e}")
        sys.exit(1)

def get_next_version(version_argument=None):
    version_file = r'X:\tools\venv\version.txt'
    
    if version_argument:
        print(f"Using provided version argument: {version_argument}")
        
        # Write the provided version to version.txt
        try:
            with open(version_file, 'w') as f:
                f.write(version_argument)
            print(f"Version {version_argument} written to {version_file}")
        except Exception as e:
            print(f"Error writing version to file: {e}")
            sys.exit(1)
        
        return version_argument
    
    # Check if the version file exists
    if os.path.exists(version_file):
        try:
            with open(version_file, 'r') as f:
                current_version = f.read().strip()
                print(f"Current version in file: {current_version}")

                # Check if version format is valid
                version_parts = current_version.split('.')
                if len(version_parts) == 3 and all(part.isdigit() for part in version_parts):
                    # Increment the last part of the version
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    new_version = '.'.join(version_parts)
                    print(f"New version: {new_version}")
                    
                    # Save the new version back to version.txt
                    with open(version_file, 'w') as f:
                        f.write(new_version)
                    return new_version
                else:
                    print("Error: Version format in version.txt is invalid. Expected format is 'X.Y.Z'.")
                    sys.exit(1)
        except Exception as e:
            print(f"Error reading version file: {e}")
            sys.exit(1)
    else:
        print(f"Error: {version_file} does not exist.")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the path to the YAML file as an argument.")
        sys.exit(1)
    
    file_path = sys.argv[1]
    libraries = find_libraries_installed_on_gui_pc(file_path)
    
    if libraries:
        for lib in libraries:
            print(f"Library Name: {lib['library_name']}")
            print(f"Version: {lib['version']}")
            print(f"Installation Source: {lib['installation_source']}")
            copy_file(lib['installation_source'])
        create_venv()
        install_libraries_in_venv(libraries)
    else:
        print("No libraries found on GUI_PC.")
    
    # Handle versioning
    if len(sys.argv) > 2:
        version_argument = sys.argv[2]
        if version_argument == "no_version_argument":
            version_argument = None
        version = get_next_version(version_argument)
    else:
        version = get_next_version()
    
    print(f"Final version: {version}")

if __name__ == "__main__":
    main()
