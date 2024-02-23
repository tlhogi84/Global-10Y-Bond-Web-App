# cd C:\Users\Tlhogi\Documents\Grace\Investment Work\4. Sovereign Bonds\Global
# python app.py
# http://127.0.0.1:8050/

from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.css.append_css({'external_url': '/static/reset.css'})

df = pd.read_csv('dash_resource.csv')

#Layouts and fonts:
font_style = {'font-family': 'Gabarito, sans-serif'}
lower_background_color = "black"
lower_style = {'backgroundColor': lower_background_color, 'border': 'none'}

#Page Headers
header_container = html.Div([
    html.Div([
        html.Img(src='/assets/Quandoyen_Banner.png', style={'width': '1000px', 'height': '100px', 'float': 'left'}),
        html.Div('Contact: info@quandoyen.com',
                 style={**font_style, 'font-size': '30px', 'color': 'white', 'position': 'absolute', 'bottom': '3px', 'right': '3px', 'margin': '2px'})
    ],
    style={'position': 'relative', 'background-color': 'black', 'height': '100px', 'width': '100%'})
])

sub_header = html.H2(
    "Historical Global 10-Year Sovereign Bond Yields and Total Returns",
    style={'text-align': 'center', 'color': 'black', 'font-family': 'Gabarito, sans-serif', 'font-size': '20px', 'align-items': 'center'}
)

sub_header_container = html.Div(sub_header, style={'backgroundColor': '#f4d5a9', 'height': '25px', 'width': '100%', 'margin': '0'})


#Charts:
return_chart          = dcc.Graph(id='return_chart',          style={'width': '100%', 'height': '400px'})
yield_vs_return_chart = dcc.Graph(id='yield_vs_return_chart', style={'width': '100%', 'height': '400px'})
inflation_chart       = dcc.Graph(id='inflation_chart',       style={'width': '100%', 'height': '400px'})
yield_chart           = dcc.Graph(id='yield_chart',           style={'width': '100%', 'height': '400px'})

#Selection Tools

country_dropdown = dcc.Dropdown(
    id='country-dropdown',
    options=[{'label': country, 'value': country} for country in df['Country'].unique()],
    value='South Africa',
    style={'width': '300px', **font_style}
)

return_type_radio = dcc.RadioItems(
    id='return-type-radio',
    options=[
        {'label': 'Nominal Returns', 'value': 'Nominal'},
        {'label': 'Real Returns', 'value': 'Real'}
    ],
    value='Real',
    labelStyle={'color': 'white', **font_style}
)

forward_return_dropdown = dcc.Dropdown(
    id='forward-return-dropdown',
    options=[
        {'label': '1-Year Forward', 'value': '1Y'},
        {'label': '5-Year Forward', 'value': '5Y'},
        {'label': '20-Year Forward', 'value': '20Y'}
    ],
    style={'width': '300px', **font_style},
    value='5Y'
)

color_slider = dcc.Slider(
    id='color-slider',
    min=0,
    max=100,
    step=1,
    value=40,
    marks={i: str(i) for i in range(0, 101, 10)},
    tooltip={'placement': 'top'}
)

# Add a new dropdown for selecting additional countries
additional_country_dropdown = dcc.Dropdown(
    id='additional-country-dropdown',
    multi=True,
    options=[
        {'label': country, 'value': country} for country in df['Country'].unique()
    ],
    placeholder="Select more countries",
    style={'width': '300px', **font_style}
)

yield_dropdown = dcc.Dropdown(
    id='yield-dropdown',
    options=[{'label': country, 'value': country} for country in df['Country'].unique()],
    value='South Africa',
    style={'width': '300px', **font_style}
)

#Graph Containers
container_1 = html.Div([
    country_dropdown,
    return_type_radio,
    return_chart
], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '5px', 'margin-left': '4%', **lower_style})

container_2 = html.Div([
    html.Div([
        forward_return_dropdown,
        html.Div([color_slider], style={'max-width': '80%', 'padding-right': '10px'})
    ]),
    yield_vs_return_chart
], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '5px', 'border': 'none', **lower_style})

container_3 = html.Div([
    inflation_chart,
], style={'width': '45%', 'padding': '5px', 'margin-left': '4%', 'margin-top': '37px','display': 'inline-block', 'vertical-align': 'top', **lower_style})

# Remove the yield_dropdown from the layout
container_4 = html.Div([
    additional_country_dropdown,
    yield_chart
], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '5px', 'border': 'none', **lower_style})

app.layout = html.Div(
    style={
        'backgroundColor': lower_background_color,
        'height': '200vh',
        **font_style
    },
    children=[
        header_container,
        sub_header_container,
        html.Div([container_1, container_2], style={'display': 'flex', 'justify-content': 'space-between'}),
        html.Div([container_3, container_4], style={'display': 'flex', 'justify-content': 'space-between'}),
    ]
)

@app.callback(
    Output('return_chart', 'figure'),
    Output('yield_vs_return_chart', 'figure'),
    Output('inflation_chart', 'figure'),
    Output('yield_chart', 'figure'),
    Input('country-dropdown', 'value'),
    Input('return-type-radio', 'value'),
    Input('forward-return-dropdown', 'value'),
    Input('color-slider', 'value'),
    Input('additional-country-dropdown', 'value')
)
def update_charts(selected_country, return_type, forward_return_period, color_level, additional_countries=None):
    filtered_data = df[df['Country'] == selected_country]

    fig_returns = go.Figure()

    if forward_return_period is not None:
        for period in ['1Y', '5Y', '20Y']:
            if return_type == 'Nominal':
                r_return = f'{period} N_Return'
                line_color = 'grey' if period == '1Y' else 'black' if period == '5Y' else '#d78f49'
            else:
                r_return = f'{period} R_Return'
                line_color = 'grey' if period == '1Y' else 'black' if period == '5Y' else '#d78f49'

            fig_returns.add_trace(go.Scatter(x=filtered_data['TIME'], y=filtered_data[r_return],
                                          mode='lines', name=f'{period} Return',
                                          line=dict(color=line_color)))

        fig_returns.update_layout(
            title=dict(text=f'{return_type} Historical Returns: {selected_country}',
                       font=dict(color='black', family='Gabarito, sans-serif', size=15)),
            yaxis_title='Return (%)',
            xaxis_title='TIME',
            width=550,
            height=350,
            margin=dict(l=1, r=5, t=50, b=50),
            legend=dict(orientation='h', y=1.08),
            plot_bgcolor='white',
            paper_bgcolor='white',
            autosize=True
        )

        fig_returns.update_yaxes(tickformat=".0%")
    else:
        fig_returns = go.Figure()

    if forward_return_period is not None:
        forward_column = f'Forward {forward_return_period} {return_type[0]}_Return'

        fig_scatter = go.Figure()

        fig_scatter.add_trace(go.Scatter(
            x=filtered_data['Yield (y)'] / 100,
            y=filtered_data[forward_column],
            mode='markers',
            marker=dict(color='black')
        ))

        fig_scatter.update_layout(
            title=dict(text=f'Yield vs {forward_return_period} Forward {return_type} Returns: {selected_country}',
                       font=dict(color='black', family='Gabarito, sans-serif', size=15)),
            xaxis_title='Yield (%)',
            yaxis_title=f'{forward_return_period} Forward Return (%)',
            width=550,
            height=350,
            margin=dict(l=1, r=5, t=50, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            autosize=True
        )

        data_length = len(filtered_data)
        if data_length > 0 and color_level > 0:
            recent_data = filtered_data.tail(int(data_length * (color_level / 100)))
            fig_scatter.add_trace(go.Scatter(
                x=recent_data['Yield (y)'] / 100,
                y=recent_data[forward_column],
                mode='markers',
                marker=dict(color='#d78f49')
            ))

        fig_scatter.update_xaxes(tickformat=".0%")
        fig_scatter.update_yaxes(tickformat=".0%")
    else:
        fig_scatter = go.Figure()

    # Update the inflation chart
    inflation_data = df[df['Country'] == selected_country]
    inflation_chart = go.Figure()

    # Create a dictionary for mapping periods to line colors
    period_colors = {
        '1Y': 'grey',
        '5Y': 'black',
        '20Y': '#d78f49'}

    # Add traces to inflation chart (1Y, 5Y, 20Y inflation rates)
    for period in ['1Y', '5Y', '20Y']:
        inflation_rate = f'{period} Inflation'
        inflation_chart.add_trace(go.Scatter(x=inflation_data['TIME'], y=inflation_data[inflation_rate],
                                        mode='lines', name=f'{period} Inflation',
                                        line=dict(color=period_colors.get(period, 'black'))))

    inflation_chart.update_layout(
        title=dict(text=f'Inflation Over Time: {selected_country}',
                   font=dict(color='black', family='Gabarito, sans-serif', size=15)),
        yaxis_title='Inflation Rate (%)',
        xaxis_title='TIME',
        width=550,
        height=350,
        margin=dict(l=1, r=5, t=50, b=50),
        legend=dict(orientation='h', y=1.08),
        plot_bgcolor='white',
        paper_bgcolor='white',
        autosize=True
    )
    inflation_chart.update_yaxes(tickformat=".0%")

    # Create a list of countries to plot for the yield graph, including the selected and additional countries
    countries_to_plot = [selected_country]
    if additional_countries:
        countries_to_plot.extend(additional_countries)

    yield_chart_data = df[df['Country'].isin(countries_to_plot)]

    fig_yield = go.Figure()

    sample_colors = ['black', 'grey', '#d78f49','#5f868e', '#38761d']
    colors = {country: sample_colors[i % len(sample_colors)] for i, country in enumerate(countries_to_plot)}
    
    for country in countries_to_plot:
        country_data = yield_chart_data[yield_chart_data['Country'] == country]
        fig_yield.add_trace(go.Scatter(
            x=country_data['TIME'],
            y=country_data['Yield (y)']/100,
            mode='lines',
            name=f'{country}',
            line=dict(color=colors[country])  # Assign the appropriate color
        ))

    fig_yield.update_layout(
        title=dict(text='10-Year Bond Yield', font=dict(color='black', family='Gabarito, sans-serif', size=15)),
        yaxis_title='Yield (%)',
        xaxis_title='TIME',
        width=550,
        height=350,
        margin=dict(l=1, r=5, t=50, b=50),
        legend=dict(orientation='h', y=1.08),
        plot_bgcolor='white',
        paper_bgcolor='white',
        autosize=True
    )
    fig_yield.update_yaxes(tickformat=".0%")

    return fig_returns, fig_scatter, inflation_chart, fig_yield

if __name__ == '__main__':
    app.run(debug=True)

