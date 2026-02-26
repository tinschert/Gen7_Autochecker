# -*- coding: utf-8 -*-
# @file pattern_matching_arxml.py
# @author ADAS_HIL_TEAM
# @date 01-05-2023

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


ns = "{http://autosar.org/schema/r4.0}"

# Represents Xpath to signal name information
signals_path = f"{ns}I-SIGNAL-TO-PDU-MAPPINGS/{ns}I-SIGNAL-TO-I-PDU-MAPPING"

# Represents Xpath to PDU group information
pdu_group_path = f"{ns}I-SIGNAL-TO-PDU-MAPPINGS/{ns}I-SIGNAL-TO-I-PDU-MAPPING/{ns}I-SIGNAL-GROUP-REF"

# Represents Xpath to cycle time information
cycle_time_path = f"{ns}I-PDU-TIMING-SPECIFICATIONS/{ns}I-PDU-TIMING/{ns}TRANSMISSION-MODE-DECLARATION/{ns}TRANSMISSION-MODE-TRUE-TIMING/{ns}CYCLIC-TIMING/{ns}TIME-PERIOD/{ns}VALUE"

# Represents Xpath to byte order information
byte_order_path = f"{ns}PACKING-BYTE-ORDER"

# Represents Xpath to start bit information
start_bit_path = f"{ns}START-POSITION"

# Represents Xpath to intial value information
initial_value_path = f"{ns}INIT-VALUE/{ns}NUMERICAL-VALUE-SPECIFICATION/{ns}VALUE"

# Represents Xpath to base type information
base_type_path = f"{ns}NETWORK-REPRESENTATION-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}BASE-TYPE-REF"

# Represents Xpath to computation methods information
compu_methods_path = f'{ns}PHYSICAL-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}COMPU-METHOD-REF'

# Represents Xpath to data methods information
data_methods_path = f'{ns}PHYSICAL-PROPS/{ns}SW-DATA-DEF-PROPS-VARIANTS/{ns}SW-DATA-DEF-PROPS-CONDITIONAL/{ns}DATA-CONSTR-REF'

# Represents Xpath to enumeration information
enums_path = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE'

# Represents Xpath to factors (type 1 Xpath)
factors_path_type_1 = f'{ns}COMPU-PHYS-TO-INTERNAL/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}COMPU-RATIONAL-COEFFS/{ns}COMPU-NUMERATOR/{ns}V[2]'

# Represents Xpath to factors (type 2 Xpath)
factors_path_type_2 = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}COMPU-RATIONAL-COEFFS/{ns}COMPU-NUMERATOR/{ns}V[2]'

# Represents Xpath to offsets (type 1 Xpath)
offsets_path_type_1 = f'{ns}COMPU-PHYS-TO-INTERNAL/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}COMPU-RATIONAL-COEFFS/{ns}COMPU-NUMERATOR/{ns}V[1]'

# Represents Xpath to offsets (type 1 Xpath)
offsets_path_type_2 = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}COMPU-RATIONAL-COEFFS/{ns}COMPU-NUMERATOR/{ns}V[1]'

# Represents Xpath to min value in linear signals
min_value_path = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}LOWER-LIMIT'

# Represents Xpath to max value in linear signals
max_value_path = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE//{ns}UPPER-LIMIT'

# Represents Xpath to min value texttabble signals
texttabble_min_value_path = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE/{ns}LOWER-LIMIT'

# Represents Xpath to max value texttabble signals
texttabble_max_value_path = f'{ns}COMPU-INTERNAL-TO-PHYS/{ns}COMPU-SCALES/{ns}COMPU-SCALE'
