# -*- coding: utf-8 -*-
# @file Git_Clone.py
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


import git
from git import Repo
from git import RemoteProgress
import sys,os
from tqdm import tqdm
from logging_config import logger


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

def checkout_repo(checkout_branch, local_folder,
                  git_repository=r'https://sya9lr:Adassystestereet#1@sourcecode01.de.bosch.com/scm/pjph/test_canoe_multiecu_hil.git'):
    """
    

    Args:
      checkout_branch: 
      local_folder: 
      git_repository:  (Default value = r'https://sya9lr:Adassystestereet#1@sourcecode01.de.bosch.com/scm/pjph/test_canoe_multiecu_hil.git')

    Returns:

    """
    # repo.git.action("your command without leading 'git' and 'action'"), example: gitlog - -reverse = > repo.git.log('--reverse')
    try:
        # If the repo is already cloned then we do hard reset - Fetch - Pull - Rebase to the latest updates
        repo = git.Repo(local_folder, search_parent_directories=True)
        logger.info(f"Repo exits in {repo}")
        try:
            repo.git.stash('--all')
            logger.info("------------------------Stashing All Untracked Files-----------------------\n" + str(repo.git.status()))
            repo.git.checkout('-b', 'Platform_Branch', checkout_branch)
            logger.info("------------------------Checking Out Develop Adas Hil Platform Branch-----------------------\n" + str(repo.git.status()))
            repo.git.pull()
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

def commit_push(local_folder,commit_msg):
    """
    

    Args:
      local_folder: 
      commit_msg: 

    Returns:

    """
    repo = git.Repo(local_folder, search_parent_directories=True)
    repo.git.add('Platform')
    repo.git.add('Release')
    repo.git.commit('-m' + commit_msg)
    repo.git.push('origin')
    logger.info(str(repo.git.status()))

def checkout_branch(checkout_branch,local_folder):
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

#git_url_sysuser = r'https://USERNAME:PASSWORD@sourcecode01.de.bosch.com/scm/pjph/test_canoe_multiecu_hil.git'
#local_folder = r'C:\Users\HAF3SH\Desktop\Trial2' #from GUI
#checkout_branch = r'origin/Develop_ADAS_HIL_Platform' #from GUI
#localbranch = r'Develop_ADAS_HIL_Platform'
#folder = r'New Text Document.txt'


#checkout_repo(checkout_branch,local_folder,git_url_sysuser)
