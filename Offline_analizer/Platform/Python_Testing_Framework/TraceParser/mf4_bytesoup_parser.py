import os
import pandas as pd
import shutil
import xml.etree.ElementTree as ET

def get_iVisu(version, temp_folder):
    if os.path.exists("D:/"):
        if os.path.exists(f"D:/Tools/iVisu_{version}/iVisu/windows/ivisu.exe"):
            return f"D:/Tools/iVisu_{version}/iVisu/windows/ivisu.exe", 0
        else:
            if os.path.exists("D:/Tools"):
                return copy_iVisu(f"D:/Tools/", version), 0
            else:
                os.mkdir("D:/Tools")
                return copy_iVisu(f"D:/Tools/", version), 0
    else:
        return copy_iVisu(temp_folder, version), 1

def copy_iVisu(dest_path, version=None):
    if version is not None:
        ivisu_source =  f"//abtvdfs2.de.bosch.com/ismdfs/iad/verification/ODS/ADAS_HIL_concept/Classe/Install/iVisu_{version}.zip"
        if os.path.exists(ivisu_source):
            shutil.copy2(ivisu_source, dest_path+f"iVisu_{version}.zip")
            shutil.unpack_archive(dest_path+f"/iVisu_{version}.zip", dest_path)
            os.remove(dest_path+f"iVisu_{version}.zip")
            if os.path.exists(dest_path+f"iVisu_{version}/iVisu/windows/ivisu.exe"):
                return dest_path+f"iVisu_{version}/iVisu/windows/ivisu.exe"
            else: 
                return None
        else:
            return None
    else:
        return None

def remove_iVisu(ivisu_path, version=None):
    if version is not None:
        shutil.rmtree(ivisu_path+f"/iVisu_{version}")
        #os.rmdir(ivisu_path+f"iVisu_{version}")

def copy_iVisu_folder(dest_path, version=None):
    if version is not None:
        ivisu_source =  f"//abtvdfs2.de.bosch.com/ismdfs/iad/verification/ODS/ADAS_HIL_concept/Classe/Install/iVisu_{version}"
        print(ivisu_source)
        if os.path.exists(ivisu_source):
            shutil.copytree(ivisu_source, dest_path)
            return dest_path
        else:
            return None
    else:
        ivisu_source = "//abtvdfs2.de.bosch.com/ismdfs/iad/verification/ODS/ADAS_HIL_concept/Classe/Install/iVisu"
        if os.path.exists(ivisu_source):
            shutil.copytree(ivisu_source, dest_path)
            return dest_path
        else:
            return None

def get_hash_csv_name(temp_directory):
    hash_table = {}
    # parsing csv has proven to be unreliable -- txt much more robust
    # if os.path.exists(temp_directory+"activity_log.csv"):
    #     ivisu_activity_log = pd.read_csv(os.path.join(temp_directory, "activity_log.csv"), encoding="utf-8", on_bad_lines="skip")
    #     for line in ivisu_activity_log:
    #         print(line)
    #         if ".csv' is too long - replaced with '" in line:
    #             parts = line.split("'")
    #             hash_table[parts[1]] = parts[3]
    if os.path.exists(temp_directory+"ivisu_output.txt"):
        with open(temp_directory+"ivisu_output.txt", 'r') as ivisu_output:
            for line in ivisu_output:
                if ".csv' is too long - replaced with '" in line:
                    parts = line.split("'")
                    hash_table[parts[1]] = parts[3]
    return hash_table

#def concatenate_csvs(directory="."):
def concatenate_csvs(directory="."):
    # Find all CSV files in the directory
    csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
    
    if not csv_files:
        return None
    
    dataframes = {}
    for f in csv_files:
        try:
            df = pd.read_csv(os.path.join(directory, f), sep=None, engine='python', encoding="utf-8", on_bad_lines="skip", header=1)
            dataframes[f] =df
        except Exception as e:
            print(f"Error reading {f}: {e}")
    
    if not dataframes:
        return None
    
    return dataframes

def wrapper(dataframes, wrapper_name=""):
    for key in dataframes.keys():
        if wrapper_name in key:
            return key
    return None
    
def get_signal(df, signal_name=""):
    try:
        signal_data = df.filter(items=["Time Stamp in ns", signal_name])
        signal_data = signal_data.rename(columns={"Time Stamp in ns":"Timestamp", signal_name:"Signal Value"})
        #convert timestamp to ms
        signal_data["Timestamp"] = signal_data["Timestamp"].div(1000000)
        signal_data["Signal Name"]=signal_name
        return signal_data
    except Exception as e:
        return None
    
def extract_ford_mf4(input_path, xml_path, ivisu_version, iVisu_path=None):
    if os.path.exists(input_path) and os.path.exists(xml_path):
        # Get current temporary directory
        current_directory = os.getcwd()+"/"
        # Create temp folder at current directory
        if not os.path.exists(current_directory+"Temp"):
            os.makedirs(current_directory+"Temp", exist_ok=True)
        temp_directory = current_directory+"Temp/"
        # Get iVisu (find or download temporarly)
        if iVisu_path is not None:
            ivisu_exe = iVisu_path
            is_ivisu_temporary = 0
        else:
            ivisu_exe, is_ivisu_temporary= get_iVisu(ivisu_version, temp_directory)

        settings_xml = xml_path
        # Get the directory of the input file
        input_directory = os.path.dirname(input_path)
        mf4_path = input_path
        if os.path.splitext(input_path)[1]==".zip":
            shutil.unpack_archive(input_path, temp_directory)
            for file in os.listdir(temp_directory):
                if file.endswith(".mf4"):
                    mf4_path = os.path.join(temp_directory, file)
        # Create a new folder called "csv_export" in the temp directory
        csv_export_directory = os.path.join(temp_directory, "csv_export")
        os.makedirs(csv_export_directory, exist_ok=True)

        # Parse the XML file
        tree = ET.parse(settings_xml)
        root = tree.getroot()

        # Find the logging_directory element and modify the full_directory_name attribute 
        for logging_directory in root.iter('logging_directory'):
            logging_directory.set('full_directory_name', csv_export_directory)

        # Save the modified XML file
        modified_settings_xml = temp_directory+"/modified.xml"
        tree.write(modified_settings_xml)
        os.system(f"cd Temp & {ivisu_exe} -s {modified_settings_xml} -i {mf4_path} --auto-close --log-interface-data-to-csv --platform offscreen > ivisu_output.txt 2>&1")
        # if is_ivisu_temporary:
        #     remove_iVisu(temp_directory, ivisu_version)

        # get dataframes
        csvs = concatenate_csvs(csv_export_directory)

        hash_table = get_hash_csv_name(temp_directory)
        #print(hash_table)
        if hash_table:
            for key in hash_table.keys():
                csvs[key] = csvs[hash_table[key]]

        # delete temp folder
        shutil.rmtree(temp_directory)

        #return the dataframes
        return csvs
    else:
        print("No recording found")
        return None

if __name__ == "__main__":
    df = concatenate_csvs()
    print(df)
