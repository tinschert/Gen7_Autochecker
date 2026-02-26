# -*- coding: utf-8 -*-
# @file ssh_client.py
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
from tkinter import messagebox
from invoke.exceptions import UnexpectedExit, ThreadException
import paramiko.ssh_exception
from paramiko import SSHException
from pysftp import Connection, CnOpts, AuthenticationException, ConnectionException
from socket import gaierror


class SSHClient:
    """SFTP Cloe Linux"""

    def __init__(self, **conn_info):
        self.conn_info = dict()
        self.conn_info.update(conn_info)
        self.host = self.conn_info['hostname']
        self.username = self.conn_info['username']
        self.password = self.conn_info['password']
        temp_path = self.conn_info['test_repo_path']
        suffix = '/' + self.conn_info['test_repo_keyword']
        self.path = temp_path.replace(suffix, '')
        self.connection = None
        self.cnopts = CnOpts()
        self.cnopts.hostkeys = None

        self.connect()

    def connect(self):
        """ """
        try:
            self.connection = Connection(
                host=self.host,
                username=self.username,
                password=self.password,
                cnopts=self.cnopts,
                log=True)
            print(f"Login successful!")
            print(f"Connected to {self.host} as {self.username} on port 22")
        except AuthenticationException or OSError:
            self.connection = None
            print(f"Login not successful!")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
        except gaierror or socket.error or TimeoutError or ConnectionException or SSHException:
            self.connection = None
            print(f"Login not successful!")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()

    def change_dir(self, new_path):
        """
        

        Args:
          new_path: 

        Returns:

        """
        try:
            self.connection.chdir(new_path)
        except FileNotFoundError:
            print(f"Dir is not found?!")
        except SSHException or socket.error or ConnectionResetError:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.change_dir(new_path)

    def list_directory(self, new_path):
        """
        List all stored directories in path.

        Args:
          new_path: 

        Returns:

        """
        try:
            return sorted(self.connection.listdir(new_path))
        except SSHException or socket.error or ConnectionResetError:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.list_directory(new_path)
    """ List all stored directories in path. """

    def close_connection(self):
        """ """
        self.connection.close()
        print(f"Disconnected from {self.host}")

    def get_current_working_dir(self):
        """ """
        try:
            return self.connection.pwd
        except socket.error:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.get_current_working_dir()
        except SSHException:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.get_current_working_dir()

    def check_is_file(self, cur_path):
        """
        

        Args:
          cur_path: 

        Returns:

        """
        try:
            return self.connection.isfile(cur_path)
        except SSHException:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.check_is_file(cur_path)

    def check_is_dir(self, cur_path):
        """
        

        Args:
          cur_path: 

        Returns:

        """
        try:
            return self.connection.isdir(cur_path)
        except SSHException:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                self.check_is_dir(cur_path)

    def execute(self, command):
        """
        

        Args:
          command: 

        Returns:

        """
        try:
            return self.connection.execute(command)
        except ConnectionResetError or SSHException or socket.error:
            print(f"socket is closed, attempt to reconnect ..")
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.execute(command)
        except ThreadException:
            print(f'TESTS ARE STOPPED...')

    def call_make_file_clean(self, command):
        """
        

        Args:
          command: 

        Returns:

        """
        try:
            with self.connection.cd(self.path):
                self.connection.execute(f"make {command}")
        except socket.gaierror or ConnectionResetError or SSHException:
            print('NO INTERNET CONNECTION ....')
            retry = messagebox.askretrycancel('Warning', 'Connection has been lost. Try to reconnect your internet and press "retry".')
            if retry:
                self.connect()
                return self.call_make_file_clean(command)
        except UnexpectedExit:
            print('UNEXPECTED EXIT? MAYBE INTERNET CONNECTION PROBLEM?')
        except ThreadException:
            print(f'TESTS ARE STOPPED...')
