import pandas as pd
import plotly.express as px
from dataclasses import dataclass


@dataclass
class PlotlyVisualizer:
    dataframe: pd.DataFrame

    def line_plot(self, x: str, y: str, title: str = 'Line Plot', color: str = 'Signal Name', hover_name: str = None, markers: bool = False, save_as_html: bool = False, path: str = None):
        """
        Create a line plot with markers and a basic range slider.

        :param x: The column name for the x-axis.
        :param y: A list of column names for the y-axis.
        :param title: Title of the plot.
        :param color: The column name for the color differentiation.
        :param hover_name: Show signal when hover with mouse.
        :param markers: If True, display markers on the lines.
        :param save_as_html: If True, save the plot as an HTML file.
        """

        # Check if Signal Value column has a string value
        if self.dataframe["Signal Value"].dtype == "object":
            # Convert all values to strings
            self.dataframe["Signal Value"] = self.dataframe["Signal Value"].astype(str)

        fig = px.line(self.dataframe, x=x, y=y, color=color, title=title, hover_name=hover_name, markers=markers)

        # Add a range slider to the x-axis
        fig.update_xaxes(rangeslider_visible=True)

        # Adjust the layout to ensure the legend is at the bottom
        fig.update_layout(
            legend=dict(orientation='h', yanchor='top', y=-0.3, xanchor='center', x=0.5),
            margin=dict(l=40, r=40, t=40, b=100)  # Adjust bottom margin for the range slider
        )

        if save_as_html:
            filename = f"{title.replace(' ', '_').lower()}.html"
            # Find the index of the last backslash
            tc_name_only = path.split("\\")[1]
            last_backslash_index = tc_name_only.rfind(".")
            # Slice the string up to the last backslash
            folder_path = tc_name_only[:last_backslash_index]
            fig.write_html(fr"Reports\plots\{folder_path}_{filename}")
            print(f"Plot saved as {filename}")
        else:
            fig.show()