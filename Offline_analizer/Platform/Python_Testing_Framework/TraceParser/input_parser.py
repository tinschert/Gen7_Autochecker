import pandas as pd
from typing import Optional
from pathlib import Path


def create_signal_dataframe(signal_type: str = 'AliveCounter') -> Optional[pd.DataFrame]:
    """
    Create a new DataFrame from the original DataFrame by concatenating
    the 'Signal' and 'Message' columns into a new 'Signal Name' column,
    while keeping the 'Maximum' column unchanged.

    Parameters:
    original_df (pd.DataFrame): The original DataFrame containing 'Signal', 'Message', and 'Maximum'.

    Returns:
    pd.DataFrame: A new DataFrame with 'Signal Name' and 'Maximum'.
    """
    try:
        # Load the Excel file
        input_file = r"..\..\.." + r"\adas_sim\Python_Testing_Framework\sysint_tests\InputTable.xlsx"
        original_df = pd.read_excel(Path(input_file).resolve(), sheet_name=signal_type)  # Replace with your file path

        # Check if the required columns are in the DataFrame
        if not all(col in original_df.columns for col in ['Signal', 'Message', 'Maximum']):
            raise ValueError("Original DataFrame must contain 'Signal', 'Message', and 'Maximum' columns.")

        # Create the new DataFrame
        new_df = pd.DataFrame()
        new_df['SignalName'] = original_df['Message'] + '.' + original_df['Signal']
        new_df['Maximum'] = original_df['Maximum']

        return new_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

