# -*- coding: utf-8 -*-
# @file linux_client.py
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


import invoke.exceptions
from fabric import Connection
from invoke.exceptions import UnexpectedExit, ThreadException
from paramiko.ssh_exception import SSHException, AuthenticationException
from pysftp import ConnectionException
import socket


class ExecClient:
    """ """

    def __init__(self, **conn_info):

        self.conn_info = dict()
        self.conn_info.update(conn_info)
        self.host = self.conn_info['hostname']  # tool team HIL3 location
        self.username = self.conn_info['username']
        self.password = self.conn_info['password']
        self.cloe_repo = self.conn_info['cloe_repo']
        self.connection = None
        self.smoke_test_folder_name = self.conn_info["smoke_tests_folder_name"]
        self.smoke_test_list = []
        self.variant = self.conn_info["variant"]
        self.evald_config = ""

    def connect(self):
        """ """
        try:
            self.connection = Connection(host=self.host, user=self.username, connect_kwargs={"password": self.password})
            print(f"Login successful!")
            print(f"Connected to {self.host} as {self.username} on port 22")
        except AuthenticationException or OSError as e:
            self.connection = None
            print(f"Login not successful!")
            raise e
        except socket.gaierror or socket.error or TimeoutError or ConnectionException or SSHException as e:
            self.connection = None
            print(f"Login not successful!")
            raise e

    def disconnect(self):
        """ """
        self.connection.close()
        print(f"Closing connection..")

    def list_dir(self, l_path=""):
        """
        

        Args:
          l_path:  (Default value = "")

        Returns:

        """
        dir_list = []
        try:
            with self.connection.cd(l_path):
                [dir_list.append(item) for item in self.connection.run("ls").stdout.split('\n') if item != ""]
                return dir_list
        except SSHException or socket.error or ConnectionResetError as e:
            print(f"socket is closed, attempt to reconnect ..")
            raise e
        except invoke.exceptions.UnexpectedExit as e:
            print(f"Bad command ...")
            raise e

    def call_make_file(self, yaml_test, l_path=""):
        """
        

        Args:
          yaml_test: 
          l_path:  (Default value = "")

        Returns:

        """
        try:
            with self.connection.cd(l_path):
                self.connection.run(f"make evald-launch-gui evald-config={self.evald_config} evald-testcase={yaml_test} -owc > /dev/null")
        except socket.gaierror:
            print('NO INTERNET CONNECTION ....')
        except UnexpectedExit:
            print('UNEXPECTED EXIT? MAYBE INTERNET CONNECTION PROBLEM?')

    def get_file(self, remote_path, local_path):
        """
        

        Args:
          remote_path: 
          local_path: 

        Returns:

        """
        try:
            self.connection.get(remote_path, local_path, preserve_mode=False)
        except Exception as e:
            print(f"File not transferred... reason --> {e}")

    def find(self, find_what):  # /home/sya9lr/GIT_Workspace
        """
        

        Args:
          find_what: 

        Returns:

        """
        command = f"find {self.cloe_repo} -depth -name {find_what}"
        try:
            result = self.connection.run(f"{command}")
            if result.__dict__["stderr"] == "":
                return result.stdout.strip()
        except Exception as e:
            print(f"Find command not executed. Reason --> {e}")
            raise e

    def get_smoke_tests_list(self):
        """ """
        smoke_test_location = self.find(self.smoke_test_folder_name)
        for test in self.list_dir(smoke_test_location):
            if ".generic" not in str(test) and str(test).endswith('.yml'):
                self.smoke_test_list.append(smoke_test_location + "/" + test)
        return self.smoke_test_list

    def get_evald_config(self):
        """ """
        conf_loc = self.find("conf")
        for conf in self.list_dir(conf_loc):
            if self.variant in conf:
                self.evald_config = conf_loc + "/" + conf

    def check_oem_tag(self, tc_path):
        """
        

        Args:
          tc_path: 

        Returns:

        """
        command = f'grep -w "OEM" {tc_path}'
        grep_result = self.connection.run(command)
        if self.variant in grep_result.stdout.strip():
            return True
        else:
            return False





