import pandas as pd

def convert_csv_to_dataframe(csv_file_path):

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Display the DataFrame
    print(df)
    print("brada")