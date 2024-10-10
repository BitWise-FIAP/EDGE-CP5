import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz

# Constants for IP and port
IP_ADDRESS = "18.117.118.157"
PORT_STH = 8666
DASH_HOST = "0.0.0.0"  # Set this to "0.0.0.0" to allow access from any IP


# Function to get luminosity data from the API
def get_luminosity_data(lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:bit/attributes/luminosity?lastN={lastN}"
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
            return values
        except KeyError as e:
            print(f"Key error: {e}")
            return []
    else:
        print(f"Error accessing {url}: {response.status_code}")
        return []


# Function to convert UTC timestamps to Lisbon time
def convert_to_lisbon_time(timestamps):
    utc = pytz.utc
    lisbon = pytz.timezone('America/Sao_Paulo')
    converted_timestamps = []
    for timestamp in timestamps:
        try:
            timestamp = timestamp.replace('T', ' ').replace('Z', '')
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).astimezone(lisbon)
        except ValueError:
            # Handle case where milliseconds are not present
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).astimezone(lisbon)
        converted_timestamps.append(converted_time)
    return converted_timestamps


# Set lastN value
lastN = 10  # Get 10 most recent points at each interval

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Data Viewer'),
    dcc.Graph(id='luminosity-graph'),
    dcc.Graph(id='humidity-graph'),  # New humidity graph
    dcc.Graph(id='temperature-graph'),  # New temperature graph
    dcc.Store(id='luminosity-data-store', data={'timestamps': [], 'luminosity_values': []}),
    dcc.Store(id='humidity-data-store', data={'timestamps': [], 'humidity_values': []}),  # New store for humidity
    dcc.Store(id='temperature-data-store', data={'timestamps': [], 'temperature_values': []}),  # New store for temperature
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # in milliseconds (10 seconds)
        n_intervals=0
    )
])


@app.callback(
    Output('luminosity-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('luminosity-data-store', 'data')
)
def update_data_store(n, stored_data):
    # Get luminosity data
    data_luminosity = get_luminosity_data(lastN)

    if data_luminosity:
        # Extract values and timestamps
        luminosity_values = [float(entry['attrValue']) for entry in data_luminosity]  # Ensure values are floats
        timestamps = [entry['recvTime'] for entry in data_luminosity]

        # Convert timestamps to Lisbon time
        timestamps = convert_to_lisbon_time(timestamps)

        stored_data['timestamps'].extend(timestamps)
        stored_data['luminosity_values'].extend(luminosity_values)

        return stored_data

    return stored_data


@app.callback(
    Output('luminosity-graph', 'figure'),
    Input('luminosity-data-store', 'data')
)
def update_luminosity_graph(stored_data):
    if stored_data['timestamps'] and stored_data['luminosity_values']:
        mean_luminosity = sum(stored_data['luminosity_values']) / len(stored_data['luminosity_values'])

        trace_luminosity = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['luminosity_values'],
            mode='lines+markers',
            name='Luminosity',
            line=dict(color='orange')
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_luminosity, mean_luminosity],
            mode='lines',
            name='Mean Luminosity',
            line=dict(color='blue', dash='dash')
        )

        fig_luminosity = go.Figure(data=[trace_luminosity, trace_mean])
        fig_luminosity.update_layout(
            title='Luminosity Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Luminosity',
            hovermode='closest'
        )

        return fig_luminosity

    return {}


@app.callback(
    Output('humidity-graph', 'figure'),
    Input('humidity-data-store', 'data')
)
def update_humidity_graph(stored_data):
    if stored_data['timestamps'] and stored_data['humidity_values']:
        mean_humidity = sum(stored_data['humidity_values']) / len(stored_data['humidity_values'])

        trace_humidity = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['humidity_values'],
            mode='lines+markers',
            name='Humidity',
            line=dict(color='blue')
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_humidity, mean_humidity],
            mode='lines',
            name='Mean Humidity',
            line=dict(color='red', dash='dash')
        )

        fig_humidity = go.Figure(data=[trace_humidity, trace_mean])
        fig_humidity.update_layout(
            title='Humidity Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Humidity',
            hovermode='closest'
        )

        return fig_humidity

    return {}


@app.callback(
    Output('temperature-graph', 'figure'),
    Input('temperature-data-store', 'data')
)
def update_temperature_graph(stored_data):
    if stored_data['timestamps'] and stored_data['temperature_values']:
        mean_temperature = sum(stored_data['temperature_values']) / len(stored_data['temperature_values'])

        trace_temperature = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['temperature_values'],
            mode='lines+markers',
            name='Temperature',
            line=dict(color='green')
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_temperature, mean_temperature],
            mode='lines',
            name='Mean Temperature',
            line=dict(color='purple', dash='dash')
        )

        fig_temperature = go.Figure(data=[trace_temperature, trace_mean])
        fig_temperature.update_layout(
            title='Temperature Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Temperature',
            hovermode='closest'
        )

        return fig_temperature

    return {}


if __name__ == '__main__':
    app.run_server(debug=True, host=DASH_HOST, port=8050)
