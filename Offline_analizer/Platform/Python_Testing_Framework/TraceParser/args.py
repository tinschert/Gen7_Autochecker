import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Argument Parser for Offline Analyzer")

    # Define arguments
    parser.add_argument("--log_file_path", type=str, required=True, help="Path to the log file")
    parser.add_argument("--dem_header_path", type=str, help="Path to the DEM_HEADER_FILE")
    parser.add_argument("--dem_exclusion_list", type=str, help="Path to the DEM_EXCLUSION_LIST")
    parser.add_argument("--ivisu_exe_path", type=str, help="Path to the iVisu exe file to use in case of extraction from mf4 to bytesoup csvs files")

    # Parse arguments
    return parser.parse_args()



