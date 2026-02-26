# -*- coding: utf-8 -*-
# @file bus_object_mapping.py
# @author ADAS_HIL_TEAM
# @date 10-04-2022

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2022-2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RoadObj_gen'))
from RoadObj_gen.RoadObj_gen_Map_Classe import *
from RoadObj_gen.RoadObj_gen_Map_CM import *
from RoadObj_gen.RoadObj_gen_Inject_RFC import *
from RoadObj_gen.RoadObj_gen_Inject_RFL import *
from RoadObj_gen.RoadObj_gen_Inject_RFR import *
from RoadObj_gen.RoadObj_gen_Inject_RRL import *
from RoadObj_gen.RoadObj_gen_Inject_RRR import *
from RoadObj_gen.RoadObj_gen_Inject_VFC import *

#Mapping files
update_Map_Classe(file_path='../../Classe/Nodes/RoadObjects/Map_Classe.cin', num_objects=9)
update_Map_CM(file_path='../../Classe/Nodes/RoadObjects/Map_CM.cin', num_objects=9)

#Injection files
update_Inject_RFC(file_path='../../Classe/Nodes/RoadObjects/Inject_Radar_FC.cin', num_objects=9)
update_Inject_VFC(file_path='../../Classe/Nodes/RoadObjects/Inject_FVideo.cin', num_objects=9)
update_Inject_RFL(file_path='../../Classe/Nodes/RoadObjects/Inject_Radar_FL.cin', num_objects=9)
update_Inject_RFR(file_path='../../Classe/Nodes/RoadObjects/Inject_Radar_FR.cin', num_objects=9)
update_Inject_RRL(file_path='../../Classe/Nodes/RoadObjects/Inject_Radar_RL.cin', num_objects=9)
update_Inject_RRR(file_path='../../Classe/Nodes/RoadObjects/Inject_Radar_RR.cin', num_objects=9)