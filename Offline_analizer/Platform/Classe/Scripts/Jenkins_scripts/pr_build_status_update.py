# -*- coding: utf-8 -*-
# @file pr_build_status_update.py
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

"""updates the build status in bit bucket pull request for the latest commit id"""
import argparse
import sys,os
import requests
import regex as re
from yaml import Loader,load
from urllib.parse import quote_plus as covert_str_to_url_format
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger


build_status_upadte_url  = "https://sourcecode01.de.bosch.com/rest/api/1.0/projects/PJXIL/repos/adas_hil/commits/<commit_id>/builds"

#to get latest commit id
branch_commits_url = r"https://sourcecode01.de.bosch.com/rest/api/1.0/projects/PJXIL/repos/adas_hil/commits?until=<branch_name>&merges=include"

def getLatestCommitId(bitbucket_rest_url, auth):
    """
    gets latest commit id in the given bit bucket branch url

    Args:
      bitbucket_rest_url (str): rest api url to the bitbucket commit window
      auth (tuple): authentication (username, http access token)

    Returns:
        str: returns latest commit id
    """
    try:
        response_data = requests.get(url=bitbucket_rest_url, auth=auth)
        if response_data.status_code!=200:
            raise Exception(f"{response_data.status_code}, Could not get commit data from {bitbucket_rest_url}")
        latest_commit_info = response_data.json()["values"][0]
        
        commit_id = latest_commit_info["id"]
        committer_name = latest_commit_info['author'].get('displayName', '')
        message = latest_commit_info["message"]
        logger.info(f"Got latest commit from {committer_name} -> {commit_id}\nCommit Message: {message}")
        return commit_id
        
    except Exception as e:
        logger.error(f"Error while getting latest commit id -> {e}")
        logger.info(f"Continuing with commit id from PR")
        return False


def updateBitbucketBuildStatus(bitbucket_commit_build_url, build_no, build_console_url, status, testResults, auth_bitbucket):
    """
    updates the build status in bit bucket pull request for the latest commit id

    Args:
      bitbucket_commit_build_url (str): url to the commit list for the given PR
      build_no (int): jenkins build number
      build_console_url (str): jenkins build console url
      status (str): Status of the build
      testResults (str): Result of the tests executed


    """
    try:
        logger.info("---------------Update Build Status------------------")
        logger.info(f"bitbucket_commit_build_url: {bitbucket_commit_build_url}")
        logger.info(f"build_console_url: {build_console_url}")
        data = {"key":"Build - "+str(build_no),
                "state":status,
                "url":build_console_url,
                "testResults":testResults
                }
        response = requests.post(bitbucket_commit_build_url, json=data, auth=auth_bitbucket)
        response.raise_for_status()
        logger.info(f"Build Status updated Successfully with:\n{data}")
    except Exception as e:
        logger.error(f"Error while updating build status -> {e}")
        raise Exception(e)

    
def printPRinfo(pr_info):
    """
    just prints the PR information so that jenkins can extract this info to send in mail

    Args:
      pr_info (dict): Pull request information


    """
    adas_hil_pr_url = r"https://sourcecode01.de.bosch.com/projects/PJXIL/repos/adas_hil/pull-requests/<pr-id>/overview"  #replace <pr-id> with pr_id
    try:
        pr_url = adas_hil_pr_url.replace("<pr-id>", str(pr_info["pr_id"]))
        title = pr_info["title"]
        source_branch_name = pr_info["source_branch"]
        author = pr_info["author"]
        logger.info(f"PR_INFO:#:Pull Request Link: {pr_url}:#:")
        logger.info(f"PR_INFO:#:Title: {title}:#:")
        logger.info(f"PR_INFO:#:Source Branch: {source_branch_name}:#:")
        logger.info(f"PR_INFO:#:Author: {author}:#:")
    except Exception as e:
        logger.error(f"error while printing PR info -> {e}")
        raise Exception(e)

if __name__ == "__main__":
    try:
        commandLineParser = argparse.ArgumentParser(description='Update jenkins build status in bitbucket')
        commandLineParser.add_argument('--pr_info', action="store", dest="pr_info", required=True, help="latest commit id of the the pr")
        commandLineParser.add_argument('--build_no', action="store", dest="build_no", required=True, help="jenkins build number for the pr")
        commandLineParser.add_argument('--build_console_url', action="store", dest="build_console_url", required=True, help="Url for the build console")
        commandLineParser.add_argument('--status', action="store", dest="status", required=True, help="status of the build INPROGRESS|SUCCESSFUL|FAILED")
        commandLineParser.add_argument('--testResults', action="store", dest="testResults", required=False,default="", help="total passed, total failed, skipped etc")
        commandLineParser.add_argument('--bitbucket_username', action="store", dest="bitbucket_username", required=True, help="user name for rest api")
        commandLineParser.add_argument('--bitbucket_token', action="store", dest="bitbucket_token", required=True, help="http toke for bitbucket auth")


        arguments = commandLineParser.parse_args()

        auth_bitbucket = (arguments.bitbucket_username, arguments.bitbucket_token)

        pr_info = arguments.pr_info

        pr_info = load(pr_info, Loader=Loader)
        
        #replace space
        pr_info["title"] = pr_info["title"].replace("#space#", " ")
        pr_info["author"] = pr_info["author"].replace("#space#", " ")
        
        source_branch_name = pr_info["source_branch"]
        #take latest commit_id after merge commit
        latest_commit_id = getLatestCommitId(branch_commits_url.replace("<branch_name>", covert_str_to_url_format(source_branch_name)), auth_bitbucket)

        if latest_commit_id:
            commit_id = latest_commit_id
        else:
            commit_id = pr_info["commit_id"]

        build_no = arguments.build_no
        build_console_url = arguments.build_console_url + r"/consoleFull"
        status = arguments.status
        testResults = arguments.testResults
        if status == "INPROGRESS":
            printPRinfo(pr_info)

        if testResults!="":
            testResults = load(pr_info, Loader=Loader)

    except Exception as e:
        logger.error(f"Error while reading arguements in build status update -> {e}")
        raise Exception(e)

    updateBitbucketBuildStatus(build_status_upadte_url.replace("<commit_id>",commit_id), build_no, build_console_url, status, testResults, auth_bitbucket)
