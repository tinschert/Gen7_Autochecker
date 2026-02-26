# bokeh_plot.py
from dataclasses import dataclass
import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import Slider, CustomJS, Label, Div
from bokeh.layouts import column, row
from bokeh.io import curdoc

@dataclass
class BokehPlot:
    dataframes: list  # List of DataFrames to plot
    colors: list      # List of colors for each line
    title: str = "Offline Evalulation"
    x_axis_label: str = "Timestamp"
    y_axis_label: str = "Signal Value"
    width: int = 1000
    height: int = 600
    save_to_html: bool = False  # Option to save as HTML

    def create_plot(self):
        # Create a figure
        p = figure(title=self.title,
                   x_axis_label=self.x_axis_label,
                   y_axis_label=self.y_axis_label,
                   width=self.width, height=self.height)

        # Store vertical lines, labels, sliders, and value divs
        vlines = []
        labels = []
        sliders = []
        value_divs = []

        # Plot each DataFrame and create sliders
        for i, (df, color) in enumerate(zip(self.dataframes, self.colors)):
            label = df['Signal Name'][0] if 'Signal Name' in df.columns and len(df['Signal Name']) > 0 else f"Unnamed Data {i+1}"
            line = p.line(df['Timestamp'], df['Signal Value'], legend_label=label, line_width=2, color=color)

            # Add a vertical line for each DataFrame
            vline = p.line([df['Timestamp'].iloc[0], df['Timestamp'].iloc[0]], [0, max(df['Signal Value'])], line_color='red', line_dash='dashed')
            vlines.append(vline)

            # Create a label for the corresponding vertical line
            v_label = Label(x=df['Timestamp'].iloc[0], y=15, text='Value:', text_color='black')
            p.add_layout(v_label)
            labels.append(v_label)

            # Create a slider for this DataFrame
            slider = Slider(start=df['Timestamp'].min(), end=df['Timestamp'].max(), value=df['Timestamp'].iloc[0], step=0.1, title=f"{label} X Position")
            sliders.append(slider)

            # Create a Div to display the y-value next to the slider
            value_div = Div(text='Value: ', width=100)
            value_divs.append(value_div)

            # JavaScript callback for the slider
            callback = CustomJS(args=dict(vline=vline, label=v_label, slider=slider, value_div=value_div, data=df.to_dict(orient='records')), code="""
                const value = slider.value;
                vline.data_source.data['x'] = [value, value];
                vline.data_source.change.emit();

                let closestY = null;
                for (let i = 0; i < data.length; i++) {
                    if (data[i].x === value) {
                        closestY = data[i].y;
                        break;
                    }
                }

                label.x = value;
                label.y = closestY !== null ? closestY : 0;
                label.text = 'Value: ' + (closestY !== null ? closestY : 'N/A');

                // Update the value displayed in the Div
                value_div.text = 'Value: ' + (closestY !== null ? closestY : 'N/A');
            """)

            slider.js_on_change('value', callback)

        # Create a layout with the plot and sliders+divs
        slider_rows = [row(sliders[i], value_divs[i]) for i in range(len(sliders))]
        layout = column(p, *slider_rows)

        # If save_to_html is True, save the plot to an HTML file
        if self.save_to_html:
            output_file("bokeh_plot.html")  # Specify the output HTML file name
            save(p)  # Save the plot to the HTML file
        else:
            # Add the layout to the current document for server usage
            curdoc().add_root(layout)
            curdoc().title = self.title