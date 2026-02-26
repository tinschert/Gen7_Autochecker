import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
from dataclasses import dataclass


@dataclass
class SignalApp:
    dataframes: list

    def create_app(self):
        app = Dash(__name__)
        app.layout = self.create_layout()
        self.register_callbacks(app)
        return app

    def create_layout(self):
        # Calculate overall min and max timestamps for the RangeSlider
        all_timestamps = pd.concat([df['Timestamp'] for df in self.dataframes])
        overall_min = all_timestamps.min()
        overall_max = all_timestamps.max()

        return html.Div([
            dcc.Graph(id='signal-plot'),
            html.Div(id='range-slider-container', children=[
                dcc.RangeSlider(
                    id='range-slider',
                    min=overall_min,
                    max=overall_max,
                    value=[overall_min, overall_max],
                    marks={str(ts): str(ts) for ts in all_timestamps.unique()},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                html.Div(id='range-slider-output', style={'textAlign': 'center'})
            ], style={'margin-bottom': '20px'}),
            html.Div(id='sliders-container', children=[
                html.Div([
                    dcc.Slider(
                        id=f'slider-{i}',
                        min=self.dataframes[i]['Timestamp'].min(),
                        max=self.dataframes[i]['Timestamp'].max(),
                        step=None,
                        value=self.dataframes[i]['Timestamp'].min(),
                        marks={str(ts): str(ts) for ts in self.dataframes[i]['Timestamp'].unique()},
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
                    html.Div(id=f'slider-output-{i}', style={'textAlign': 'center'})
                ], style={'margin-bottom': '20px'})
                for i in range(len(self.dataframes))
            ])
        ])

    def register_callbacks(self, app):
        @app.callback(
            Output('signal-plot', 'figure'),
            [Input(f'slider-{i}', 'value') for i in range(len(self.dataframes))] +
            [Input('range-slider', 'value')]
        )
        def update_graph(*selected_values):
            fig = go.Figure()

            colors = ['blue', 'orange', 'green', 'red', 'purple', 'cyan']

            # Get the range values from the RangeSlider
            range_min, range_max = selected_values[-1]  # Last value corresponds to the RangeSlider

            for i, (df, selected_value) in enumerate(zip(self.dataframes, selected_values[:-1])):
                # Filter based on the range from the RangeSlider
                filtered_df = df[(df['Timestamp'] >= range_min) &
                                  (df['Timestamp'] <= range_max)]

                # Add the signal trace to the plot
                fig.add_trace(go.Scatter(
                    x=filtered_df['Timestamp'],
                    y=filtered_df['Signal Value'],
                    mode='lines',
                    name=df['Signal Name'].iloc[0],
                    text=filtered_df['Signal Value'].fillna('NaN'),
                    hoverinfo='text',
                    line=dict(color=colors[i % len(colors)]),
                    marker=dict(color=colors[i % len(colors)])
                ))

                # Draw a vertical line at the selected timestamp for each signal
                selected_timestamp = selected_value
                if not filtered_df.empty:
                    fig.add_shape(type="line",
                                  x0=selected_timestamp, x1=selected_timestamp,
                                  y0=0, y1=max(filtered_df['Signal Value'].max(), 10),
                                  line=dict(color=colors[i % len(colors)], width=2, dash="dash"))

            fig.update_layout(
                title='Signal Values Over Time',
                xaxis_title='Timestamp',
                yaxis_title='Signal Value',
                showlegend=True,
                yaxis=dict(range=[0, max(df['Signal Value'].max() for df in self.dataframes) + 1])
            )

            return fig

        @app.callback(
            [Output(f'slider-output-{i}', 'children') for i in range(len(self.dataframes))],
            [Input(f'slider-{i}', 'value') for i in range(len(self.dataframes))]
        )
        def update_slider_outputs(*selected_values):
            outputs = []
            for i, selected_value in enumerate(selected_values):
                signal_value = self.dataframes[i].loc[self.dataframes[i]['Timestamp'] == selected_value, 'Signal Value']
                signal_value = signal_value.iloc[0] if not signal_value.empty else np.nan
                signal_name = self.dataframes[i]['Signal Name'].iloc[0]

                if pd.isna(signal_value):
                    outputs.append(f'{signal_name} | Timestamp: {selected_value} - Signal Value: NaN')
                else:
                    outputs.append(f'{signal_name} | Timestamp: {selected_value} - Signal Value: {signal_value}')

            return outputs

        @app.callback(
            Output('range-slider-output', 'children'),
            Input('range-slider', 'value')
        )
        def update_range_slider_output(selected_range):
            return f'Selected Range: {selected_range[0]} to {selected_range[1]}'

