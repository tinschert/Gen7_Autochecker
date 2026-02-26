import dll_bindings as RoadObjDLL
import pandas as pd
import ctypes

signal_list = [
    "Object_SpiHdr_SensorOriginPointX",
    "Object_SpiHdr_SensorOriginPointY",
    "Object_SpiHdr_SensorOriginPointZ",
    "Object_SpiHdr_SensorOrientYaw",
    "Object_ObjHdr_NumValidObjects",
    "Object_Obj1_Px",
    "Object_Obj1_Py",
    "Object_Obj1_Vx",
    "Object_Obj1_Vy",
    "Object_Obj1_OrientationYaw",
    "Object_Obj1_RCS",
    "Object_Obj1_ReferencePoint"
]

number_of_objects_to_read = 3

#TODO: Could be possible to not read all the signals but get a signal name as input and return only the requested value(s)
#TODO: Implement a way for RFC+RFR aswell..
def read_all_signal_values(df: pd.DataFrame, radar_id: str, max_obj_nr: int) -> pd.DataFrame:
    """
    Reads all signals specified in the signal_list local variable from a given DataFrame and returns a new DataFrame with specific signal information.
    Args:
        df (pd.DataFrame): The input DataFrame containing the data to be parsed.
        radar_id (str): A string representing the radar ID.
    Returns:
        pd.DataFrame: A DataFrame containing the signal names and signal values.
    """
    # Make sure the dataframe is valid
    if df.empty:
        raise ValueError("No valid ByteArray!")

    # Create return DataFrame struct
    result = pd.DataFrame(columns=['Signal Name', 'Timestamp', 'Signal Value'])

    # Define a mapping of signal names to their corresponding functions
    signal_functions = {
        "Object_SpiHdr_SensorOriginPointX": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_X,
        "Object_SpiHdr_SensorOriginPointY": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Y,
        "Object_SpiHdr_SensorOriginPointZ": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Z,
        "Object_SpiHdr_SensorOrientYaw": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw,
        "Object_ObjHdr_NumValidObjects": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Num_Valid_Obj,
    }

    # Iterate over the requested signals
    for signal_name in signal_list:
        # Make sure the signals requested are from the correct radar
        if not (radar_id == "RFC" or radar_id == "RFL" or radar_id == "RFR" or radar_id == "RRL" or radar_id == "RRR"):
            print(f"Invalid RA6 SGU sensor name: {radar_id}")
            continue

        # Put together the radar name as well as the signal name to form the full signal definition
        signal = radar_id + "_" + signal_name

        # Header signals are mapped hardcoded above in the signal_functions, which directly can be read
        if signal_name in signal_functions:
            value = float(signal_functions[signal_name](df['Byte Array'].iloc[0]))
            new_row = pd.DataFrame([{'Signal Name': signal, 'Timestamp': df['Timestamp'].iloc[0], 'Signal Value': value}])
            result = pd.concat([result.astype(new_row.dtypes), new_row.astype(result.dtypes)])
        
        # For objects the signal name is split into parts to extract the object number and signal type
        elif signal_name.startswith("Object_Obj"):
            parts = signal_name.split('_') # Split the signal name which could be for example Object_Obj1_Px
            suffix = '_'.join(parts[2:])  # Extract the signal ending
            for obj_nr in range(max_obj_nr):  # Iterate over object numbers from for example 0 to 19 (1 to 20)
                if suffix == "Px":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Distance_X(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "Py":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Distance_Y(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "Vx":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Velocity_X(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "Vy":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Velocity_Y(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "OrientationYaw":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Yaw_Angle(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "RCS":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_RCS(df['Byte Array'].iloc[0], obj_nr))
                elif suffix == "ReferencePoint":
                    value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Reference_Point(df['Byte Array'].iloc[0], obj_nr))
                else:
                    print(f"Invalid RA6 SGU signal suffix: {signal}")
                    continue

                # Create the object signal name
                obj_signal_name = f"{radar_id}_{parts[0]}_{parts[1][:3]}{obj_nr + 1}_{parts[2]}"
                
                # Create a new row for the result DataFrame
                new_row = pd.DataFrame([{'Signal Name': obj_signal_name, 'Timestamp': df['Timestamp'].iloc[0], 'Signal Value': value}])
                result = pd.concat([result.astype(new_row.dtypes), new_row.astype(result.dtypes)])
        else:
            print(f"Invalid RA6 SGU signal name: {signal}")
            continue

    return result


def read_specific_signal_values(df: pd.DataFrame, signals: list) -> pd.DataFrame:
    """
    Reads specified signal values from a given DataFrame and returns a new DataFrame with specific signal information.
    Args:
        df (pd.DataFrame): The input DataFrame containing the data to be parsed.
        signals (list): A list of signal names to be read.
    Returns:
        pd.DataFrame: A DataFrame containing the signal names and signal values.
    """
    # Make sure the dataframe is valid
    if df.empty:
        raise ValueError("No valid ByteArray!")

    # Create return DataFrame struct
    result = pd.DataFrame(columns=['Signal Name', 'Timestamp', 'Signal Value'])

    # Define a mapping of signal names to their corresponding functions
    signal_functions = {
        "Object_SpiHdr_SensorOriginPointX": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_X,
        "Object_SpiHdr_SensorOriginPointY": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Y,
        "Object_SpiHdr_SensorOriginPointZ": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Z,
        "Object_SpiHdr_SensorOrientYaw": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Mounting_Position_Yaw,
        "Object_ObjHdr_NumValidObjects": RoadObjDLL.oa_Read_ByteArray_RA6SGU_Num_Valid_Obj,
    }

    # Iterate over the requested signals
    for signal in signals:
        # Make sure the signals requested are from the correct radar
        if not (signal.startswith("RFC_") or signal.startswith("RFL_") or signal.startswith("RFR_") or signal.startswith("RRL_") or signal.startswith("RRR_")):
            print(f"Invalid RA6 SGU sensor name: {signal}")
            continue

        # Split the signal name into its prefix and the actual signal name since we can use the same functions for all the radars
        prefix, signal_name = signal.split('_', 1)

        # Header signals are mapped hardcoded above in the signal_functions, which directly can be read
        if signal_name in signal_functions:
            value = float(signal_functions[signal_name](df['Byte Array'].iloc[0]))
        
        # For objects the signal name is split into parts to extract the object number and signal type
        elif signal_name.startswith("Object_Obj"):
            parts = signal_name.split('_') # Split the signal name which could be for example Object_Obj1_Px
            obj_nr = int(parts[1][3:]) - 1  # Extract the object number
            suffix = '_'.join(parts[2:])  # Extract the signal ending
            if suffix == "Px":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Distance_X(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "Py":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Distance_Y(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "Vx":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Velocity_X(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "Vy":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Velocity_Y(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "OrientationYaw":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Yaw_Angle(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "RCS":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_RCS(df['Byte Array'].iloc[0], obj_nr))
            elif suffix == "ReferencePoint":
                value = float(RoadObjDLL.oa_Read_ByteArray_RA6SGU_Reference_Point(df['Byte Array'].iloc[0], obj_nr))
            else:
                print(f"Invalid RA6 SGU signal suffix: {signal}")
                continue
        else:
            print(f"Invalid RA6 SGU signal name: {signal}")
            continue
        
        # Create a new row for the result DataFrame
        new_row = pd.DataFrame([{'Signal Name': signal, 'Timestamp': df['Timestamp'].iloc[0], 'Signal Value': value}])

        # To make sure the data frame is not empty and has the same types as defined for 'result', astype converts the data types of the new_row to the data types of the result and wise versa
        result = pd.concat([result.astype(new_row.dtypes), new_row.astype(result.dtypes)])

    return result