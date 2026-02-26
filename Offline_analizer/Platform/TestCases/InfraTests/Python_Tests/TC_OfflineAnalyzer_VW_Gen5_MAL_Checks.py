#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 26.Sept.2024
#this is an example Python testcase using the CANoe COM interface
#modifyed by Christain Tinschert for E3 Project

import sys, os
import matplotlib.pyplot as plt
import pyodbc
sys.path.append(r"..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\..\Python_Testing_Framework\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\Python_Testing_Framework\TraceParser")
sys.path.append(r"..\..\..\Python_Testing_Framework\CommonTestFunctions")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import HTML_Logger

#Offline analysis imports
try:
    import Platform.Python_Testing_Framework.TraceParser.mdf_parser as mdf_parser
    from Platform.Python_Testing_Framework.CommonTestFunctions.offline_common_functions import CommonFunc, Condition
    from Platform.Python_Testing_Framework.ReportGen import plotter, plotter_dash
except:
    import plotter, plotter_dash
    from offline_common_functions import CommonFunc, Condition
    import mdf_parser
import pandas as pd

def get_file_name(file_path):
    """
    Extracts and returns the file name without extension from a given file path.
    """
    return os.path.splitext(os.path.basename(file_path))[0]

def extract_type(measurement_ID):
    """
    Extracts the measurement type from the measurement ID.
    The measurement type is assumed to be the part of the ID after the first underscore.
    """
    if "Gen5_37W_BL" in measurement_ID:
        return "PV5"
    else:
        return "37W"

def convert_signal_value_ms_to_kmh(df):
    """
    Converts the 'Signal Value' column from m/s to km/h in the given DataFrame.
    Returns a new DataFrame with converted values.
    """
    df_converted = df.copy()
    df_converted["Signal Value"] = df_converted["Signal Value"] * 3.6
    return df_converted

def get_start_end_timestamps(df):
    """
    Returns the start and end timestamps from the given DataFrame.
    """
    if df.empty or "Timestamp" not in df.columns:
        raise ValueError("DataFrame is empty or missing 'Timestamp' column.")
    start_timestamp = float(df["Timestamp"].iloc[0])
    end_timestamp = float(df["Timestamp"].iloc[-1])
    return start_timestamp, end_timestamp

def get_signal_statistics(df):
    """
    Returns the average, minimum, maximum, and standard deviation of the 'Signal Value' column in the given DataFrame.
    """
    average = float(df["Signal Value"].mean())
    minimum = float(df["Signal Value"].min())
    maximum = float(df["Signal Value"].max())
    std_dev = float(df["Signal Value"].std())

    return average, minimum, maximum, std_dev

def return_maximum_value(df):
    """
    Returns the maximum value from the 'Signal Value' column in the given DataFrame.
    """
    return int(df["Signal Value"].max())

def eval_percentNegativeTheta_90(df):
    """
    Checks if the 'Signal Value' is above 0.9 for more than 10 consecutive seconds.
    Returns a list of (start_time, end_time) tuples where this condition is met.
    """
    threshold = 0.9 # Threshold for percentNegativeTheta
    min_duration = 10.0  # seconds

    above = df["Signal Value"] > threshold
    result = []
    start_idx = None

    for i in range(len(df)):
        if above.iloc[i]:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                start_time = df["Timestamp"].iloc[start_idx]
                end_time = df["Timestamp"].iloc[i - 1]
                if end_time - start_time >= min_duration:
                    result.append((start_time, end_time))
                start_idx = None

    # Handle case where the last segment goes till the end
    if start_idx is not None:
        start_time = df["Timestamp"].iloc[start_idx]
        end_time = df["Timestamp"].iloc[-1]
        if end_time - start_time >= min_duration:
            result.append((start_time, end_time))

    return result

def eval_percentNegativeTheta_10(df, vxvref_df):
    """
    Checks if the 'Signal Value' in df is below threshold for more than min_duration consecutive seconds,
    and only returns intervals where the corresponding vxvref_df 'Signal Value' is not zero for the entire interval.
    Returns a list of (start_time, end_time) tuples.
    """
    threshold = 0.005
    min_duration = 20.0  # seconds

    below = df["Signal Value"] < threshold
    result = []
    start_idx = None

    for i in range(len(df)):
        if below.iloc[i]:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                start_time = df["Timestamp"].iloc[start_idx]
                end_time = df["Timestamp"].iloc[i - 1]
                if end_time - start_time >= min_duration:
                    # Find vxvref values in the same interval
                    mask = (vxvref_df["Timestamp"] >= start_time) & (vxvref_df["Timestamp"] <= end_time)
                    if (vxvref_df.loc[mask, "Signal Value"] != 0).all():
                        result.append((start_time, end_time))
                start_idx = None

    # Handle case where the last segment goes till the end
    if start_idx is not None:
        start_time = df["Timestamp"].iloc[start_idx]
        end_time = df["Timestamp"].iloc[-1]
        if end_time - start_time >= min_duration:
            mask = (vxvref_df["Timestamp"] >= start_time) & (vxvref_df["Timestamp"] <= end_time)
            if (vxvref_df.loc[mask, "Signal Value"] != 0).all():
                result.append((start_time, end_time))

    return result


def write_to_access_database(
    measurement_ID, measurement_type, timestamp_start, timestamp_end, measurement_duration,
    avrg_vxvref, min_vxvref, max_vxvref, std_dev_vxvref,
    max_OOS_Az, max_OOS_El, negativeTheta, Check_Doppler_EME_Phispread, numLargerSOS_intervalls,
    negativeTheta_comment, filterPhiSpread_check, negativeTheta_count, doppler_critical_count, doppler_check, numLargerSOS_count):
    """
    Writes or updates the measurement data in the Access database.
    If the measurement_ID already exists, update the row. Otherwise, insert a new row.
    """
    import pyodbc

    conn = None
    cursor = None

    conn_str = (
        r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=\\abtvdfs1.de.bosch.com\ismdfs\ida\abt\radar\VW_MRR5E3\Delete_never\VW_Data_checks\Q7_MAL_Campain.accdb;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Check if measurement_ID already exists
        cursor.execute("SELECT COUNT(*) FROM measurements WHERE measurement_ID = ?", (measurement_ID,))
        exists = cursor.fetchone()[0]

        if exists:
            # Update the existing row
            cursor.execute(
                """
                UPDATE measurements SET
                    measurement_type = ?,
                    timestamp_start = ?,
                    timestamp_end = ?,
                    measurement_duration = ?,
                    avrg_vxvref = ?,
                    min_vxvref = ?,
                    max_vxvref = ?,
                    std_dev_vxvref = ?,
                    max_OOS_Az = ?,
                    max_OOS_El = ?,
                    negativeTheta = ?,
                    Check_Doppler_EME_Phispread = ?,
                    numLargerSOS_intervalls = ?,
                    negativeTheta_comment = ?,
                    filterPhiSpread_check = ?,
                    negativeTheta_count = ?,
                    doppler_critical_count = ?,
                    doppler_check = ?,
                    numLargerSOS_count = ?
                WHERE measurement_ID = ?
                """,
                (
                    measurement_type, timestamp_start, timestamp_end, measurement_duration, avrg_vxvref, min_vxvref,
                    max_vxvref, std_dev_vxvref, max_OOS_Az, max_OOS_El,
                    negativeTheta, Check_Doppler_EME_Phispread, numLargerSOS_intervalls,
                    negativeTheta_comment, filterPhiSpread_check, negativeTheta_count, doppler_critical_count, doppler_check,
                    numLargerSOS_count, measurement_ID
                )
            )
        else:
            # Insert a new row
            cursor.execute(
                """
                INSERT INTO measurements (
                    measurement_ID, measurement_type, timestamp_start, timestamp_end, measurement_duration,
                    avrg_vxvref, min_vxvref, max_vxvref, std_dev_vxvref,
                    max_OOS_Az, max_OOS_El, negativeTheta, Check_Doppler_EME_Phispread,
                    numLargerSOS_intervalls, negativeTheta_comment, filterPhiSpread_check,
                    negativeTheta_count, doppler_critical_count, doppler_check, numLargerSOS_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    measurement_ID, measurement_type, timestamp_start, timestamp_end, measurement_duration, avrg_vxvref,
                    min_vxvref, max_vxvref, std_dev_vxvref, max_OOS_Az, max_OOS_El,
                    negativeTheta, Check_Doppler_EME_Phispread, numLargerSOS_intervalls,
                    negativeTheta_comment, filterPhiSpread_check, negativeTheta_count, doppler_critical_count, doppler_check,
                    numLargerSOS_count
                )
            )
        conn.commit()

    except Exception as e:
        print(f"Database operation failed: {e}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def check_filterPhiSpread_critical(phispread_df, intervals):
    """
    Checks if 'Signal Value' exceeds 2 in each of the given timestamp intervals.
    Returns a list of comments: 'filterPhiSpread critical' or 'filterPhiSpread not critical' for each interval.
    """
    comments = []
    for start, end in intervals:
        # Convert to float in case of numpy types
        start = float(start)
        end = float(end)
        mask = (phispread_df["Timestamp"] >= start) & (phispread_df["Timestamp"] <= end)
        if (phispread_df.loc[mask, "Signal Value"] > 2).any():
            comments.append("filterPhiSpread critical")
        else:
            comments.append("filterPhiSpread not critical")
    if len(comments) == 1:
        return comments[0]
    return comments

def sync_and_abs_diff(Signal_df, Stable_position_df):
    """
    Synchronizes two dataframes on 'Timestamp' and returns a new dataframe
    with the absolute difference of their 'Signal Value' columns.
    """
    # Merge on Timestamp (inner join to keep only common timestamps)
    merged = pd.merge(
        Signal_df[["Timestamp", "Signal Value"]],
        Stable_position_df[["Timestamp", "Signal Value"]],
        on="Timestamp",
        suffixes=('_signal', '_stable')
    )
    # Calculate absolute difference
    merged["Abs_Diff"] = (merged["Signal Value_signal"] - merged["Signal Value_stable"]).abs()
    return merged[["Timestamp", "Abs_Diff"]]

def find_intervals_above_threshold(df, threshold=0.0523599):
    """
    Finds intervals where 'Abs_Diff' is >= threshold.
    Returns a list of (start_timestamp, end_timestamp) tuples.
    """
    above = df["Abs_Diff"] >= threshold
    intervals = []
    start_idx = None

    for i, is_above in enumerate(above):
        if is_above:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                start_time = df["Timestamp"].iloc[start_idx]
                end_time = df["Timestamp"].iloc[i - 1]
                intervals.append((start_time, end_time))
                start_idx = None

    # Handle case where the last interval goes till the end
    if start_idx is not None:
        start_time = df["Timestamp"].iloc[start_idx]
        end_time = df["Timestamp"].iloc[-1]
        intervals.append((start_time, end_time))

    return intervals

def check_EME_PhiSpread(intervals_Doppler, abs_diff_EME_data, filterPhiSpread):
    """
    Checks EME and PhiSpread thresholds within Doppler intervals.
    Returns a list of strings describing the result for each Doppler interval.
    """
    results = []
    if not intervals_Doppler:
        return ["Doppler check passed"]

    EME_THRESHOLD = 0.0261799
    PHISPREAD_THRESHOLD = 8

    for start, end in intervals_Doppler:
        # Select data in the current interval
        eme_in_interval = abs_diff_EME_data[
            (abs_diff_EME_data["Timestamp"] >= start) & (abs_diff_EME_data["Timestamp"] <= end)
        ]
        phi_in_interval = filterPhiSpread[
            (filterPhiSpread["Timestamp"] >= start) & (filterPhiSpread["Timestamp"] <= end)
        ]

        eme_critical = (eme_in_interval["Abs_Diff"] > EME_THRESHOLD).any()
        phi_critical = (phi_in_interval["Signal Value"] >= PHISPREAD_THRESHOLD).any()

        if not eme_critical and not phi_critical:
            results.append(f"{start} - {end} Doppler critical")
        elif phi_critical and not eme_critical:
            results.append(f"{start} - {end} Doppler Phispread critical")
        elif eme_critical and not phi_critical:
            results.append(f"{start} - {end} Doppler and EME Critical")
        elif eme_critical and phi_critical:
            results.append(f"{start} - {end} Doppler EME and Phispread Critical")

    return results

def numLargerSOS_check(numLargerSOS_df, vxvref_df):
    """
    Checks if 'numLargerSOS' is below the threshold for more than min_duration seconds.
    Only returns intervals where vxvref_df 'Signal Value' is never zero in the interval.
    Returns a tuple: (result, count).
    """
    threshold = 15
    min_duration = 10  # seconds

    below = numLargerSOS_df["Signal Value"] < threshold
    results = []
    start_idx = None

    for i in range(len(numLargerSOS_df)):
        if below.iloc[i]:
            if start_idx is None:
                start_idx = i
        else:
            if start_idx is not None:
                start_time = numLargerSOS_df["Timestamp"].iloc[start_idx]
                end_time = numLargerSOS_df["Timestamp"].iloc[i - 1]
                if end_time - start_time >= min_duration:
                    # Check vxvref_df in this interval
                    mask = (vxvref_df["Timestamp"] >= start_time) & (vxvref_df["Timestamp"] <= end_time)
                    if (vxvref_df.loc[mask, "Signal Value"] != 0).all():
                        results.append(f"{start_time} - {end_time} largerSOS number")
                start_idx = None

    # Handle case where the last segment goes till the end
    if start_idx is not None:
        start_time = numLargerSOS_df["Timestamp"].iloc[start_idx]
        end_time = numLargerSOS_df["Timestamp"].iloc[-1]
        if end_time - start_time >= min_duration:
            mask = (vxvref_df["Timestamp"] >= start_time) & (vxvref_df["Timestamp"] <= end_time)
            if (vxvref_df.loc[mask, "Signal Value"] != 0).all():
                results.append(f"{start_time} - {end_time} largerSOS number")

    count = len(results)
    if not results:
        return "pass", 0
    return results, count

# Define a constant for log files, could be a single log or a directory
LOG = r"C:\TOOLS\MAL_Check_PV5_37W\Temp_Folder" # Single log example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\20241021_Delta1_22.5.0_ACC_Smoke_Test.MF4" # Path example
#LOG = r"C:\Users\pep3sf4\Desktop\Test_mf4\SPA_Demo_20241218_101337_001.mf4"

def TC_ACC_Test(input_log):

    HTML_Logger.setup(__file__, "CANoePy Testcase", filename=HTML_Logger.generate_report_name())  # create the HTML report

    ################ Offline analysis section #############################
    trace = CommonFunc() # Create testing functions object, shall be instantiated once per test
    output = mdf_parser.ChannelFinder(input_log) # Parse passed mdf file
    # input from jenkins a trace or folder and from the online analyzer *** 
    output.list_channels() # If needed user can check all available channels objects

    channels = output.get_channels(["_DspCopyDataPacket._CopyDspMnpDataPacket._vxvRef",
                                    "_g_Common_VAG_Infrastructure_Resource_Management_rbPDM_rbPDM_Runnable_m_pRPers_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._DataItemBuffer_st._m_malOutOfProfileAndSpecCause._m_azOutOfSpecCause",
                                    "_g_Common_VAG_Infrastructure_Resource_Management_rbPDM_rbPDM_Runnable_m_pRPers_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._DataItemBuffer_st._m_malOutOfProfileAndSpecCause._m_elOutOfSpecCause", 
                                    "_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_input._elDSPMAL._m_percentNegativeTheta",
                                    "_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elCompensation._m_filterPhiSpread",
                                    "_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elEMEIndicator._m_estimation._m_val._m_value",
                                    "_g_Common_VAG_1R1V_Dsp_dsp_dsp_m_LocationInterface_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._m_SensState._Misalignment_st._numLargerSOS",
                                    "_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elIndicator._m_estimation._m_val._m_value",
                                    "_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elOutOfSpec._m_stablePosition._m_value"]) # Provide channels of interest as a string list. Functions will return mdf channel objects
    # function needed to get all channels defined in the python file ***

    # Get Dataframe for signal of provided range
    # FLOATING point example
    measurement_ID = get_file_name(input_log)  # Get the file name for the measurement ID
    measurement_type = extract_type(measurement_ID)  # Extract the measurement type from the file name
    vxvref_data = trace.get_signal_value(channels["_DspCopyDataPacket._CopyDspMnpDataPacket._vxvRef"], 0, 0)
    vxvref_kmh_data = convert_signal_value_ms_to_kmh(vxvref_data)
    timestamp_start, timestamp_end = get_start_end_timestamps(vxvref_kmh_data)
    measurement_duration = timestamp_end - timestamp_start  # Calculate the measurement duration
    avrg_vxvref, min_vxvref, max_vxvref, std_dev_vxvref = get_signal_statistics(vxvref_kmh_data) # Get statistics for the vxvRef signal

    OOS_Az_Data = trace.get_signal_value(channels["_g_Common_VAG_Infrastructure_Resource_Management_rbPDM_rbPDM_Runnable_m_pRPers_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._DataItemBuffer_st._m_malOutOfProfileAndSpecCause._m_azOutOfSpecCause"], 0, 0) # 0,0 - all range, x,0 - from x:end, 0,x - beginning:x , x,x - defined range
    max_OOS_Az = return_maximum_value(OOS_Az_Data)

    OOS_El_Data = trace.get_signal_value(channels["_g_Common_VAG_Infrastructure_Resource_Management_rbPDM_rbPDM_Runnable_m_pRPers_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._DataItemBuffer_st._m_malOutOfProfileAndSpecCause._m_azOutOfSpecCause"], 0, 0)
    max_OOS_El = return_maximum_value(OOS_El_Data)

    filterPhiSpread = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elCompensation._m_filterPhiSpread"], 0, 0)

    percentNegativeTheta_Data = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_input._elDSPMAL._m_percentNegativeTheta"], 0, 0)
    result_negativeTheta_90 = eval_percentNegativeTheta_90(percentNegativeTheta_Data)  # Evaluate percentNegativeTheta condition
    result_negativeTheta_10 = eval_percentNegativeTheta_10(percentNegativeTheta_Data,vxvref_data)  # Evaluate percentNegativeTheta condition

    if len(result_negativeTheta_90) == 0 and len(result_negativeTheta_10) == 0:
        negativeTheta = "pass"
        filterPhiSpread_check = "No percentNegativeTheta detected"
    else:
        negativeTheta = "fail"

    if negativeTheta == "fail":
        negativeTheta_count = len(result_negativeTheta_90) + len(result_negativeTheta_10)
        if len(result_negativeTheta_90) > 0:
            negativeTheta_comment = ("percentNegativeTheta > 0.9 for more than 10 seconds: " + str((result_negativeTheta_90)))
            filterPhiSpread_check = str(check_filterPhiSpread_critical(filterPhiSpread, result_negativeTheta_90))
        elif len(result_negativeTheta_10) > 0:
            negativeTheta_comment = ("percentNegativeTheta < 0.05 for more than 10 second: " + str((result_negativeTheta_10)))
            filterPhiSpread_check = str(check_filterPhiSpread_critical(filterPhiSpread, result_negativeTheta_10))
    else:
        negativeTheta_comment = "No violations found for percentNegativeTheta"
        filterPhiSpread_check = "No percentNegativeTheta detected"
        negativeTheta_count = 0

    numLargerSOS_data = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Dsp_dsp_dsp_m_LocationInterface_out_local.TChangeableMemPool._._._m_arrayPool._1_._elem._m_SensState._Misalignment_st._numLargerSOS"], 0, 0)
    numLargerSOS_result, numLargerSOS_count  = numLargerSOS_check(numLargerSOS_data, vxvref_data)
    numLargerSOS_intervalls = str(numLargerSOS_result)
    
    Doupler_elIndicator_data = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elIndicator._m_estimation._m_val._m_value"], 0, 0)
    EME_Indicator_data = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elEMEIndicator._m_estimation._m_val._m_value"], 0, 0)
    Stable_Position_data = trace.get_signal_value(channels["_g_Common_VAG_1R1V_Cal_MalRunnable_MalRunnable.PerRunnable._._m_controller._m_state._elOutOfSpec._m_stablePosition._m_value"], 0, 0)

    abs_diff_Doppler_data = sync_and_abs_diff(Doupler_elIndicator_data, Stable_Position_data)
    abs_diff_EME_data = sync_and_abs_diff(EME_Indicator_data, Stable_Position_data)

    intervals_Doppler = find_intervals_above_threshold(abs_diff_Doppler_data)
    doppler_critical_count = len(intervals_Doppler)
    if len(intervals_Doppler) == 0:
        doppler_check = "pass"
    else:
        doppler_check = "fail"

    Check_Doppler_EME_Phispread = str(check_EME_PhiSpread(intervals_Doppler, abs_diff_EME_data, filterPhiSpread))

    write_to_access_database(measurement_ID, measurement_type, timestamp_start, timestamp_end ,measurement_duration,
                             avrg_vxvref,min_vxvref, max_vxvref, std_dev_vxvref,max_OOS_Az,max_OOS_El,negativeTheta,
                             Check_Doppler_EME_Phispread, numLargerSOS_intervalls, negativeTheta_comment,filterPhiSpread_check,
                             negativeTheta_count, doppler_critical_count,doppler_check,numLargerSOS_count)  # Write the measurement ID and timestamps to the Access database
    print("scirpt done!")


if __name__ == "__main__":
    # Check if the path is a directory
    if os.path.isdir(LOG):
        logs = list(CommonFunc.find_mf4_files(LOG))
        for log in logs:
            TC_ACC_Test(log)
    else:
        TC_ACC_Test(LOG)
