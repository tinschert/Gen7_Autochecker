import mdf_parser
import csv_parser
import argparse
import pandas as pd
import sys, os
# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ReportGen.plotter_dash import SignalApp
from ReportGen.plotter import PlotlyVisualizer
from CommonTestFunctions import offline_common_functions as functions


def main():
    # Create the parser
    parser = argparse.ArgumentParser(description="CLI for OfflineAnalyzer.")

    # Add arguments
    parser.add_argument('--input_log_file', type=str, required=True, help='Input file path to the log file [mdf,csv]')
    parser.add_argument('--plot', type=str, required=True, help='Create Plot', choices=['True', 'False'])
    parser.add_argument('--plot_type', type=str, required=True, help='Plot type',
                        choices=['dynamic', 'static'])
    parser.add_argument('--save_html', type=str, required=False, help='Save HTML for static plot', choices=['True', 'False'])

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    input_log_file = args.input_log_file
    plot_req = bool(args.plot)

    # Check if input format is supported
    if input_log_file.endswith('.mf4'):
        # Initialize ChannelFinder with the correct path
        channel_finder = mdf_parser.ChannelFinder(input_log_file)

        # Extract channels data
        channel_dataframes = channel_finder.search_channels()
        channel_list = []
        # Check if channel_df has expected structure
        for channel_df in channel_dataframes:
            # Perform operations on the DataFrame
            # channel_df.at[19, 'Signal Value'] = 3
            # channel_df.at[87, 'Signal Value'] = 2
            # channel_df.at[42, 'Signal Value'] = 7  # Repeated value

            # Check for incrementing pattern
            failed_incr = functions.check_incrementing_pattern(channel_df, channel_df['Maximum'].iloc[0])

            # Set None to a value and check alive counter consistency
            # channel_df.at[50, 'Signal Value'] = None
            failed_cons = functions.check_alive_counter_consistency(channel_df)
            if failed_incr is True and failed_cons is True:
                channel_list.append(channel_df)
    elif input_log_file.endswith(".csv"):
        csv_parser.convert_csv_to_dataframe(input_log_file)

    if plot_req is True:
        if args.plot_type == "dynamic":
            # Create the Dash app
            app = SignalApp(channel_list)
            app = app.create_app()  # Create the Dash app from the instance

            # Run the Dash app
            app.run_server(debug=False)
        elif args.plot_type == "static":
            # Concatenate DataFrames vertically (along rows)
            concatenated_df = pd.concat(channel_list, ignore_index=True)
            visualizer = PlotlyVisualizer(dataframe=concatenated_df)
            visualizer.line_plot(x='Timestamp', y='Signal Value', color='Signal Name', markers=True, save_as_html=args.save_html)


if __name__ == "__main__":
    main()
