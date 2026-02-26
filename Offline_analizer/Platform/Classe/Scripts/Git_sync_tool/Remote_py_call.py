# -*- coding: utf-8 -*-
# @file Remote_py_call.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import rpyc
import os,sys
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger
import canoe_client_1
import time
import git
from git import Repo
from git import RemoteProgress
import sys,os
from tqdm import tqdm
import subprocess
import pythoncom


class CloneProgress(RemoteProgress):
    """ """
    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        

        Args:
          op_code: 
          cur_count: 
          max_count:  (Default value = None)
          message:  (Default value = '')

        Returns:

        """
        pbar = tqdm(total=max_count)
        pbar.update(cur_count)

        
class MyService(rpyc.Service):
    """ """

    def on_connect(self, conn):
        """
        

        Args:
          conn: 

        Returns:

        """
        print("Client connected")

    def on_disconnect(self, conn):
        """
        

        Args:
          conn: 

        Returns:

        """
        sys.stdout = None
        print("Client disconnected")
        
    def exposed_redirect(self, stdout):
        """
        

        Args:
          stdout: 

        Returns:

        """
        sys.stdout = stdout
        
    def exposed_copy_mf4(self, project_path):
        """
        

        Args:
          project_path: 

        Returns:

        """
        try:
            logger.info("Copy mf4_rename.exe to local repository")
            shutil.copy(r'\\abtvdfs2.de.bosch.com\ismdfs\iad\verification\ODS\ADAS_HIL_concept\Classe\Install\mf4_rename.exe', project_path)
        except PermissionError as e:
            logger.info(f"Permission denied to access mf4_rename.exe --> {e}")
            raise e
        except Exception as e:
            logger.info(f"Failed to copy mf4_rename.exe --> {e}")
            raise e

    def exposed_copy_platform(self, source, target):
        """
        

        Args:
          source: 
          target: 

        Returns:

        """
        if not os.path.isdir(source):
            raise Exception(f"Platform repository {source} does not exist")
        else:
            if target != '':
                if not os.path.isdir(target):
                    raise Exception(f"Customer branch repository path {target} does not exist")
                else:
                    try:
                        shutil.copytree(source, target,
                                        ignore=shutil.ignore_patterns('CustomerPrj', '*.stcfg', '*.cfg', '.git',
                                                                      '.idea', '.run', '*.local'),
                                        dirs_exist_ok=True)
                        logger.info(f"Latest Platform copied from {source} to {target}")
                    except Exception as e:
                        logger.error(f"Exception raised during copying from from {source} to {target} --> {e}")
                        raise e
                    self.exposed_copy_mf4(target + r"\Platform\Classe\Scripts\Control")

    def exposed_execute_update_sysvartab(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        logger.info(f"Run RBS Scripts from {scripts_abs_path}")
        sys.path.append(scripts_abs_path)
        import update_sysvartab
        update_sysvartab.external_call()

    def exposed_execute_create_nodes(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        sys.path.append(scripts_abs_path)
        import create_nodes
        create_nodes.external_call()

    def exposed_execute_create_sysvar(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        sys.path.append(scripts_abs_path)
        import create_sysvar
        create_sysvar.external_call()

    def exposed_execute_create_ininode(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        sys.path.append(scripts_abs_path)
        import create_ininode
        create_ininode.external_call()

    def exposed_execute_update_ini(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        sys.path.append(scripts_abs_path)
        import update_ini
        update_ini.external_call()

    def exposed_execute_create_gw(self, script_path):
        """
        

        Args:
          script_path: 

        Returns:

        """
        scripts_abs_path = script_path + r"\Platform\Classe\Scripts\Rbs_Scripts"
        sys.path.append(scripts_abs_path)
        import create_gw
        create_gw.external_call()

    def exposed_run_canoe_test(self, cfg_file, path_platform, test_unit):
        """
        

        Args:
          cfg_file: 
          path_platform: 
          test_unit: 

        Returns:

        """
        p = subprocess.Popen(["powershell.exe", path_platform + "\Platform\Classe\Scripts\Git_sync_tool\Clear_cache.ps1"], stdout=sys.stdout)
        p.communicate()
        pythoncom.CoInitialize()
        start_canoe = time.time()
        logger.info("Starting CANoe via COM interface")
        canoeClient = canoe_client_1.CANoeClient()
        try:
            canoeClient.openConfiguration(cfg_file)
            canoe_started = time.time()
            logger.info(f"CANoe loaded for {canoe_started - start_canoe} seconds")
            canoeClient.startMeasurement()
        except Exception as e:
            logger.error(f"Canoe was unable to start --> {e}")
            return 2

        try:
            test_status = canoeClient.executeTestsInTestConfiguration(test_unit)
            return test_status
        except Exception as e:
            logger.error(f"Stop at exception --> {e}")
            return 0
        finally:
            canoeClient.stopMeasurement()
            canoeClient.quitCanoe(False)
            canoeClient = None

    def exposed_get_canoe_cfg(self, target_path):
        """
        

        Args:
          target_path: 

        Returns:

        """
        for (dirpath, dirnames, filenames) in os.walk(target_path):
            for file in filenames:
                if ".cfg" in file:
                    logger.info(f"CANoe configuration path --> {target_path}\\{file}")
                    return file

    def exposed_checkout_repo(self, checkout_branch, local_folder,
                      git_repository=r'https://sya9lr:Adassystestereet#1@sourcecode01.de.bosch.com/scm/pjxil/adas_hil.git'):
        """
        

        Args:
          checkout_branch: 
          local_folder: 
          git_repository:  (Default value = r'https://sya9lr:Adassystestereet#1@sourcecode01.de.bosch.com/scm/pjxil/adas_hil.git')

        Returns:

        """
        # repo.git.action("your command without leading 'git' and 'action'"), example: gitlog - -reverse = > repo.git.log('--reverse')
        try:
            # If the repo is already cloned then we do hard reset - Fetch - Pull - Rebase to the latest updates
            repo = git.Repo(local_folder, search_parent_directories=True)
            logger.info(f"Repo exits in {repo}")
            try:
                # repo.git.stash('--all')
                # logger.info("------------------------Stashing All Untracked Files-----------------------\n" + str(repo.git.status()))
                #repo.git.checkout('-b', 'Platform_Branch', checkout_branch)
                logger.info("------------------------Checking Out Develop Adas Hil Platform Branch-----------------------\n" + str(repo.git.status()))
                if "Your branch is up to date" not in str(repo.git.status()):
                    repo.git.pull("--rebase")
                    logger.info("------------------------Pull Updates-----------------------\n" + str(repo.git.status()))
            except Exception as e:
                logger.warning(f"Checkout stopped due to --> {e}")

        except git.exc.InvalidGitRepositoryError:
            # If the repo does not exist then clone the repo
            try:
                repo = git.Repo.clone_from(git_repository, local_folder, CloneProgress())
                repo.git.checkout('-b', 'Platform_Branch', checkout_branch)
                logger.info(str(repo.git.status()))
            finally:
                pass

    def exposed_commit_push(self, local_folder,commit_msg):
        """
        

        Args:
          local_folder: 
          commit_msg: 

        Returns:

        """
        repo = git.Repo(local_folder, search_parent_directories=True)
        repo.git.add('Platform')
        repo.git.add('Release')
        repo.git.commit('-m'+commit_msg)
        repo.git.push('origin')
        logger.info(str(repo.git.status()))

    def exposed_checkout_branch(self, checkout_branch, local_folder):
        """
        

        Args:
          checkout_branch: 
          local_folder: 

        Returns:

        """
        try:
            repo = git.Repo(local_folder, search_parent_directories=True)
            logger.info(f"Repo exits in {repo}")
            repo.git.stash('--all')
            logger.info("------------------------Stashing All Untracked Files-----------------------\n" + str(repo.git.status()))
            repo.git.checkout('-b', 'Merging_Branch', checkout_branch)
            logger.info("------------------------Checking Out Project Specific Merging Branch-----------------------\n" + str(repo.git.status()))
            repo.git.pull()
            logger.info("------------------------Pull Updates-----------------------\n" + str(repo.git.status()))
        except Exception as e:
            logger.warning(f"Checkout stopped due to --> {e}")

    def exposed_clear_log(self, log_path):
        """
        

        Args:
          log_path: 

        Returns:

        """
        file = open(log_path + "\Platform\Classe\Scripts\Git_sync_tool\Debug.log", "r+")
        file.truncate(0)
        file.close()
        
    def exposed_read_log(self, log_path):
        """
        

        Args:
          log_path: 

        Returns:

        """
        file = open(log_path + "\Platform\Classe\Scripts\Git_sync_tool\Debug.log", 'r')
        print(file.read())
        file.close()


if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    print("DO NOT CLOSE THIS TERMINAL!!!")
    print("RPYC server is listening on port 18861")
    print("Waiting for client connection")
    t = ThreadedServer(MyService, port=18861)
    t.start()
