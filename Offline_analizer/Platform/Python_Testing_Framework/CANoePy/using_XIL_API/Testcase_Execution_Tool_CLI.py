#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 11.Dec.2024

import sys
import subprocess
import os

#changes the current working directory to the folder where the file is (this prevents import issues)
#print(sys.argv[0])
wkspFldr = os.path.dirname(os.path.abspath(sys.argv[0]))
#print(wkspFldr)
os.chdir(wkspFldr)

#gets the git repo root folder as string
def get_git_root(path):
    import git
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    #print(git_root)
    return git_root

#git_repo_dir = os.path.dirname(os.path.abspath(__file__))
#get_git_root(git_repo_dir)

sys.path.append(r"..\..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\sysint_tests")
import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf

#changes the current working directory to the folder where the test .py file is (this prevents import issues)
try:
    #print(sys.argv[1])
    wkspFldr = os.path.dirname(os.path.abspath(sys.argv[1]))
    #print(wkspFldr)
    os.chdir(wkspFldr)
except:
    pass

def Testcase_Execution_Tool_CLI(file_path: str):
    """
    Executes a Python file specified by the given file path.

    Parameters:
    - file_path: str
        The path to the Python file that needs to be executed.

    Raises:
    - FileNotFoundError:
        If the specified file does not exist.
    - ValueError:
        If the specified file is not a Python file (does not end with .py).
    - Exception:
        For any other errors that occur during the execution of the file.
    """

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Check if the file has a .py extension
    if not file_path.endswith('.py'):
        raise ValueError("The specified file must be a Python (.py) file.")

    try:
        # Run the Python file using subprocess
        subprocess.run([r'X:\Tools\venv\Scripts\python.exe', file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to handle command line arguments and execute the specified Python file.

    It checks for the correct number of arguments and calls the Testcase_Execution_Tool_CLI function
    to execute the provided Python file.
    """

    # Check if the correct number of arguments is provided
    if len(sys.argv) == 1:
        #print("Usage: Testcase_Execution_Tool_CLI.exe <path_to_python_file.py>")
        print("Usage 1: python Testcase_Execution_Tool_CLI.py <path_to_python_file.py>")
        print("or : multiple files comma-separated")
        print("Usage 2: python Testcase_Execution_Tool_CLI.py <path_to_python_file1.py>,<path_to_python_file2.py>,<path_to_python_file3.py>....")
        print("or : provide a testcase list in .txt file (filenames only")
        print("Usage 3: python Testcase_Execution_Tool_CLI.py --txt_list <path_to_testcase_list_file.txt>")
        print("or : provide a testcase list in .txt file (full path - Jenkins usecase)")
        print("Usage 4: python Testcase_Execution_Tool_CLI.py --txt_list_full_path <path_to_testcase_list_file.txt>")
        sys.exit(1)

    # Get the file path from command line arguments
    print(sys.argv[0])
    files_list_str = sys.argv[1]
    #if it is a single file provided as argument or list of files with comma
    #if --txt_list parameter is provided then a .txt file is used
    if (files_list_str=="--txt_list"):
        txt_file = sys.argv[2]
        dir_name = os.path.dirname(os.path.abspath(txt_file))
        #print(dir_name)
        f1 = open(txt_file)
        files_list = []
        files_list.clear()
        for el in f1:
            files_list.append(dir_name+"\\"+el.replace("\n",""))
        # Runs the specified Python file
        try:
            for el in files_list:
                print("============================================================================================================================")
                print("Executing test : ", el)
                print("============================================================================================================================")
                Testcase_Execution_Tool_CLI(el)
        except Exception as e:
            print(f"Error: {e}")
            print("File ", el, "NOT found !!!")

    elif (files_list_str=="--txt_list_full_path"):
        txt_file = sys.argv[2]
        #print(dir_name)
        f1 = open(txt_file)
        files_list = []
        files_list.clear()
        for el in f1:
            files_list.append(el.replace("\n",""))
        # Runs the specified Python file
        try:
            for el in files_list:
                print("============================================================================================================================")
                print("Executing test : ", el)
                print("============================================================================================================================")
                Testcase_Execution_Tool_CLI(el)
        except Exception as e:
            print(f"Error: {e}")
            print("File ", el, "NOT found !!!")

    else:
        files_list = files_list_str.split(",")
        print("files_list = ", files_list)
        # Run the specified Python file
        try:
            for el in files_list:
                print(
                    "============================================================================================================================")
                print("Executing test : ", el)
                print(
                    "============================================================================================================================")
                Testcase_Execution_Tool_CLI(el)
        except Exception as e:
            print(f"Error: {e}")
            print("File ", el, "NOT found !!!")

if __name__ == "__main__":
    main()