# -*- coding: utf-8 -*-
# @file Ralo_client_stop.py
# @author ADAS_HIL_TEAM
# @date 09-11-2023

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


import time
from util import establish_connection
import sys

""" vGETK RPYC Server Ver 2.5
    Last Modification 04.09.2023 - Update support of dynamic RALO version"""

def stop_measurement(ralo_version):
    """
    

    Args:
      ralo_version: 

    Returns:

    """
    c = establish_connection()
    try:
        print("Stop Measurement")
        c.root.exposed_stop_ralo(ralo_version)
        # time.sleep(5)
        print("Stopping...")
    except Exception as e:
        print(f"Unable to stop measurement --> {e}")
    finally:
        time.sleep(15)
        c.root.exposed_stop_measurement()
        time.sleep(5)  # Wait all IO operations to finish
        print(f"Close client connection to the Datalogger")
        c.close()  # Close connection
        del c  # destroy the object


if __name__ == "__main__":
    assert sys.argv[1] != 0, "RALO version is not populated"
    stop_measurement(sys.argv[1])

    