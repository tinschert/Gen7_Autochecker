import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "\..\Control")
from logging_config import logger
import subprocess

def update_a2l_paths(file_path):
    """
    Update the 'name' attribute in the <VFileName> tag inside the <a2l> tag.

    Args:
    file_path (str): Path to the A2l file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []
        jenkins_path = "D:\\Jenkins\\ADAS_Platform\\CustomerPrj\\XCP\\"
        for line in lines:
            if "<a2l><VFileName" in line:  # Identify lines with <a2l><VFileName>
                if str(jenkins_path) in line:
                    line = line.replace(jenkins_path, "")
            updated_lines.append(line)

        # Write updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)
        file.close()

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            reupdated_lines = []
            for line in lines:
                if "<a2l>" in line and "<seedandkey" in line:
                    line = line.strip()
                    splitted_lines = line.split("</a2l>")
                    splitted_lines[0] += "</a2l>"
                    for split_line in splitted_lines:
                        split_line = split_line.strip()
                        reupdated_lines.append(f"        {split_line}\n")
                else:
                    reupdated_lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(reupdated_lines)

        logger.info(f"Updated 'name' attribute in <a2l> tags in {file_path}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

def commit_and_push(repo_path, commit_message):
    """commit and push all changes in given repo_path

    Args:
        repo_path (str): path of the git repo
    """
    try:
        logger.info(f"Committing and pushing changes in {repo_path} ...")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        logger.info(f"Changes committed and pushed successfully with commit message: {commit_message}")
    except Exception as e:
        logger.error(f"Error occurred while committing and pushing changes in {repo_path} : {e}")
        raise Exception(e)

if __name__ == '__main__':
    commandLineParser = argparse.ArgumentParser(description='updated a2l path in xcp config file and push a2l files to git.')
    commandLineParser.add_argument('--customer_path', action="store", dest="customer_path", required=True,
                                   help="Absolute path to customer folder")
    
    arguments = commandLineParser.parse_args()
    xcp_conig_file_path = arguments.customer_path + r"\\CustomerPrj\\XCP\\XCP_config_gen.xcpcfg"
    update_a2l_paths(xcp_conig_file_path)
    xcp_folder_path = arguments.customer_path + r"\\CustomerPrj\\XCP"
    commit_message = f"added updated a2l files"
    commit_and_push(xcp_folder_path, commit_message)