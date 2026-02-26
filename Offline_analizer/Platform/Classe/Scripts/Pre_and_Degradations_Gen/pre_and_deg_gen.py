# -*- coding: utf-8 -*-
# @file pre_and_deg_gen.py
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


preconditions_signal = "FDX_in_HIL_specific_input_triggers::FDX_in_hil_fct_preconditions"
degradations_signal = "FDX_in_HIL_specific_input_triggers::FDX_in_hil_failure_injection"
max_signal_number = 256
preconditions_path = r"..\..\Nodes\CusPrjFunctions\Preconditions_Template.can"
degradations_path = r"..\..\Nodes\CusPrjFunctions\Degradation_Template.can"


def generate_preconditions() -> list:
    """
    preconditions_head  = f'''/*@!Encoding:1252*/
    /**
     * @file Preconditions.can
     * @author Rafael Herrera
     * @date 06.12.2021
     * @brief Handles the precondition mapping from FDX
     */
    
    includes
    {{
    }}
    
    variables
    {{
    }}
    
    on start
    {{
    }}
    
    /**
     * @brief:
     *
     *
     */
    
    on sysvar_update {preconditions_signal}
    {{
    switch (@{preconditions_signal})
    {{
        case 0: // No preconditions needed
            break;

    Args:

    Returns:

    """

    preconditions__tail = """
        default: // No preconditions needed
            break;
    }
}
"""
    preconditions = [preconditions_head]
    for index in range(1,max_signal_number):
        preconditions_body = f"""
        case {index}: // User defined
            @Customer_Prj::hil_fct_preconditions_{index} = 1;
            break;"""
        preconditions.append(preconditions_body)
    preconditions.append(preconditions__tail)
    return preconditions

def generate_degradations() -> list:
    """
    degradations_head  = f'''/*@!Encoding:1252*/
    /**
     * @file Degradation.can
     * @author Rafael Herrera
     * @date 06.12.2021
     * @brief Handles the degradation failure injection mapping from FDX
     */
    
    includes
    {{
    }}
    
    variables
    {{
    }}
    
    on start
    {{
    }}
    
    /**
     * @brief:
     *
     *
     */
    
    on sysvar_update {degradations_signal}
    {{
    switch (@{degradations_signal})
    {{
        case 0: // No preconditions needed
            break;

    Args:

    Returns:

    """

    degradations_tail = """
        default: // No degradation needed
            break;
    }
}
"""
    degradations = [degradations_head]
    for index in range(1,max_signal_number):
        degradations_body = f"""
        case {index}: // User defined
            @Customer_Prj::hil_failure_injection_{index} = 1;
            break;"""
        degradations.append(degradations_body)
    degradations.append(degradations_tail)
    return degradations

def write_file(path,data):
    """
    

    Args:
      path: 
      data: 

    Returns:

    """
    try:
        with open(path, 'w') as file:
            file.write(''.join(data))
            file.close()
        print(path + ' updated successfully.')
    except Exception as e:
        print(f"Unalbe to create file --> {e}")

if __name__ == "__main__":
    write_file(preconditions_path,generate_preconditions())
    write_file(degradations_path,generate_degradations())
