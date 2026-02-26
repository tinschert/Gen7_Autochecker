# -*- coding: utf-8 -*-
# @file ds2824_control.py
# @author ADAS_HIL_TEAM
# @date 09-12-2023

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
import sys
import time


# This python script toggles relay 1 on a dS module each time it is run.
# The dS module must be setup to binary mode on the TCP/IP config page.
# Set the IP address and Port number for the dS module, below.


def main():
    """ """
    if len(sys.argv) > 1:
        command_to_execute = str(sys.argv[1])
        print("command_to_execute (raw) = ", command_to_execute)
        command_to_execute = command_to_execute.replace("_", " ")
        print("command_to_execute = ", command_to_execute)
    else:
        command_to_execute = ""
        print("!!!MISSING ARGUMENTS like <SR_1_on>")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    IP_ADDRESS = "192.168.0.123"  # raw_input("Enter IP: ")
    PORT = 17123  # int(raw_input("Enter port: "))
    cnt = 0
    if command_to_execute != "":
        # Try to connect to the module
        try:
            print("Connecting")
            # s.close()
            s.connect((IP_ADDRESS, PORT))
        except:
            print("can not connect")
            s.close()
            cnt = cnt + 1

        try:
            # s.sendall(b'SR 17 on')
            if command_to_execute.find("all on") >= 0:
                for el in range(24):
                    str_to_send = "SR " + str(el + 1) + " on"
                    # print(str_to_send)
                    s.sendall(str_to_send.encode())
                    time.sleep(0.01)
            else:
                if command_to_execute == "all off":
                    for el in range(24):
                        str_to_send = 'SR ' + str(el + 1) + ' off'
                        # print(str_to_send)
                        iRet = s.sendall(str_to_send.encode())
                        print(iRet)
                        time.sleep(0.01)
                else:
                    s.sendall(command_to_execute.encode())
                    time.sleep(0.01)
        except:
            print("can not send on TCP")
            cnt = cnt + 1

        try:
            s.close()
        except:
            pass

        if cnt == 0:
            print("Successfully Done")

        print("Return Code = ", cnt)
        return cnt


if __name__ == "__main__":
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    main()
