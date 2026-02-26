# -*- coding: utf-8 -*-
# @file pullrequest_monitor.py
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

"""this mainly monitors if any PR is present in the given repo, if yes triggers a jenkins job for that PR"""

import argparse
import sys,os,time
import requests
import regex as re
from json import dumps
from yaml import Loader,load
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + r"\..\Control")
from logging_config import logger

#bitbucket
adas_hil_pr_url = "https://sourcecode01.de.bosch.com/rest/api/1.0/projects/PJXIL/repos/adas_hil/pull-requests"

#jenkins
jenkins_url = r"https://rb-jmaas.de.bosch.com/ADAS_HIL_Platform_Integration/job/<jenkins_job_name>/buildWithParameters?"


def monitorPR(targrt_branch, jenkins_job_url,parameters, auth_bitbucket, auth_jenkins):
    """
    monitors if any PR is present in the given repo, if yes triggers a jenkins job for that PR

    Args:
      targrt_branch (str): target PR branch name
      jenkins_job_url (str): jenkins job URL to trigger
      parameters (dict): parameters to send to the jenkins job

    """
    logger.info("-------------------------------START Monitoring Pull Requests---------------------------------")
    try:
        pr_data_response = requests.get(url=adas_hil_pr_url, auth=auth_bitbucket)

        if pr_data_response.status_code!=200:
            logger.error(f"Pull request GET returned status -> {pr_data_response.status_code}")
            raise Exception(f"Pull request GET returned status -> {pr_data_response.status_code}")
        
        logger.info(r"Received Pull Request data from Bitbucket")
        pr_found = False
        for pr in pr_data_response.json()["values"]:
            source_branch = pr["fromRef"]["displayId"]
            dest_branch = pr["toRef"]["displayId"]
            if not re.search(targrt_branch, dest_branch):
                continue
            
            latest_commit = pr["fromRef"]["latestCommit"]
            author_email = pr['author']['user']['emailAddress']
            author_name = pr['author']['user']['displayName']
            outcome = pr['properties']['mergeResult']['outcome']
            pr_id = pr["id"]
            pr_title = pr['title']

            reviewers_mail_address = []
            for reviewer in pr["reviewers"]:
                reviewers_mail_address.append(reviewer['user']['emailAddress'])

            logger.info(f"+++++++++++++++++ PR-{pr_id} +++++++++++++++++")    
            logger.info(f"Pull Request found:  {source_branch} --> {dest_branch}")
            logger.info(f"Author: {author_name}")

            if outcome.upper() != "CLEAN":
                logger.error(f"{source_branch} -> Pull request Not Mergable -> {outcome}")
                continue

            logger.info(f"PR is mergable: {outcome}")
            logger.info(f"Latest commit ID: {latest_commit}")

            #prepare PR information dict
            pr_info = {'pr_id':pr_id,
                       'title':pr_title.replace(" ","#space#"),
                       'commit_id':latest_commit,
                       'author':author_name.replace(" ","#space#"),
                       'author_email':author_email,
                       'source_branch':source_branch,
                       'dest_branch':dest_branch
                       }

            buildParameters = {"SOURCE_BRANCH":source_branch,
                               "DESTINATION_BRANCH":dest_branch,
                               "PR_INFO":dumps(pr_info),
                               "MAIL_RECIPIENTS":author_email+","+",".join(reviewers_mail_address)
                               }
            
            buildParameters.update(parameters)
            
            response = requests.post(jenkins_job_url, auth=auth_jenkins, data=buildParameters, verify=False)
            response.raise_for_status()
            logger.info(f"Job triggered successfully for PR {pr_id}")
            pr_found = True
            time.sleep(30)

        if not(pr_found):
            logger.info(f"No Pull requests Found for {targrt_branch}")
        
        logger.info("-------------------------------END Monitoring Pull Requests---------------------------------")    
        

    except Exception as e:
        logger.error(f"Error occured in monitorPR -> {e}")
        raise Exception(f"Error occured in monitorPR -> {e}")





if __name__ == "__main__":
    try:
        commandLineParser = argparse.ArgumentParser(description='Trigger jenkins on pull request')
        commandLineParser.add_argument('--target_branch', action="store", dest="target_branch", required=True, help="Target branch to monitor PR")
        commandLineParser.add_argument('--jenkins_job_name', action="store", dest="jenkins_job_name", required=True, help="Target branch to monitor PR")
        commandLineParser.add_argument('--parameters', action="store", dest="parameters", required=True, help="Parameters for PR build")
        commandLineParser.add_argument('--bitbucket_username', action="store", dest="bitbucket_username", required=True, help="user name for rest api")
        commandLineParser.add_argument('--bitbucket_token', action="store", dest="bitbucket_token", required=True, help="http token for bitbucket auth")
        commandLineParser.add_argument('--jenkins_token', action="store", dest="jenkins_token", required=True, help="http token for jenkins auth")
        

        arguments = commandLineParser.parse_args()

        auth_bitbucket = (arguments.bitbucket_username, arguments.bitbucket_token)
        auth_jenkins = (arguments.bitbucket_username, arguments.jenkins_token)

        target_branch = arguments.target_branch
        jenkins_job_name = arguments.jenkins_job_name
        para_arguement = arguments.parameters

        parameters = load(para_arguement,Loader=Loader)
    except Exception as e:
        logger.error(f"Error while reading arguements -> {e}")
        raise Exception(e)

    monitorPR(target_branch, jenkins_url.replace("<jenkins_job_name>", jenkins_job_name), parameters, auth_bitbucket, auth_jenkins)
