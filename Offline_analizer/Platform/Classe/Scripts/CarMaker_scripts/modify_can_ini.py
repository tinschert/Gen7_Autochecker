import re

def replace_value_can_ini(can_ini_path):
    with open(can_ini_path, 'r') as file:
        lines = file.readlines()

    with open(can_ini_path, 'w') as file:
        for line in lines:
            # Use regex to find and replace "SystemBufferMemoryMode=x" where x is a digit
            modified_line = re.sub(r'SystemBufferMemoryMode=[0-9]', 'SystemBufferMemoryMode=1', line)
            file.write(modified_line)

can_ini_path = r'C:\ProgramData\Vector\CANoe Family\18 (x64)\CAN.ini' # File path to CAN.ini in CANoe 18
replace_value_can_ini(can_ini_path)