# -*- coding: utf-8 -*-
# @file execute_client.py
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


import socket
from tkinter.messagebox import askretrycancel
from invoke.exceptions import UnexpectedExit
from fabric import Connection


class ExecClient:
    """ """

    def __init__(self, **conn_info):

        self.conn_info = dict()
        self.conn_info.update(conn_info)
        self.host = self.conn_info['hostname']  # tool team HIL3 location
        self.username = self.conn_info['username']
        self.password = self.conn_info['password']
        temp_path = self.conn_info['test_repo_path']
        suffix = '/' + self.conn_info['test_repo_keyword']
        self.path = temp_path.replace(suffix, '')

        self.connection = Connection(host=self.host, user=self.username, connect_kwargs={"password": self.password})

    def connect(self):
        """ """
        self.connection = Connection(host=self.host, user=self.username, connect_kwargs={"password": self.password})

    def disconnect(self):
        """ """
        self.connection.close()

    def change_dir(self):
        """ """
        dir_list = []
        with self.connection.cd(self.path):
            x = self.connection.run("ls")
            char = x.stdout.split("\n")
            for i in char:
                dir_list.append(i)
        return dir_list

    def get_cwd(self):
        """ """
        with self.connection.cd(self.path):
            print(self.connection.run("pwd"))

    def call_make_file(self, command, evald_config, yaml_test):
        """
        

        Args:
          command: 
          evald_config: 
          yaml_test: 

        Returns:

        """
        try:
            with self.connection.cd(self.path):
                self.connection.run(f"make {command} evald-config={evald_config} evald-testcase={yaml_test} -owc")
                # connection.run(f"make {command} evald-testcase={yaml_test} &>> /home/sya9lr/GIT_Workspace/PSA_Testing/randomLog.txt")
        except socket.gaierror:
            print('NO INTERNET CONNECTION ....')
        except UnexpectedExit:
            print('UNEXPECTED EXIT? MAYBE INTERNET CONNECTION PROBLEM?')

    def call_make_file_clean(self, command):
        """
        

        Args:
          command: 

        Returns:

        """
        try:
            with self.connection.cd(self.path):
                self.connection.run(f"make {command}")
        except socket.gaierror:
            print('NO INTERNET CONNECTION ....')
        except UnexpectedExit:
            print('UNEXPECTED EXIT? MAYBE INTERNET CONNECTION PROBLEM?')

