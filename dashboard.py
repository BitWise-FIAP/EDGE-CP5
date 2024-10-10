import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from datetime import datetime
import pytz

# Constantes para IP e porta
IP_ADDRESS = "18.117.118.157"
PORT_STH = 8666
DASH_HOST = "0.0.0.0"  # Permite acesso a partir de qualquer IP

# Função para obter dados de luminosidade da API
def get_luminosity_data(lastN):
    url = f"http://{IP_ADDRESS}:{PORT_STH}/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:bit/attributes/luminosity?lastN={lastN}"
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    response = requests.get(url, headers=headers)  # Faz a requisição à API
    if response.status_code == 200:
        data = response.json()  # Converte a resposta em JSON
        try:
            values = data['contextResponses'][0]['contextElement']['attributes'][0]['values']  # Extrai os valores de luminosidade
            return values
        except KeyError as e:
            print(f"Key error: {e}")  # Imprime erro caso a chave não seja encontrada
            return []
    else:
        print(f"Error accessing {url}: {response.status_code}")  # Imprime erro em caso de falha na requisição
        return []

# Função para converter timestamps de UTC para horário de Lisboa
def convert_to_lisbon_time(timestamps):
    utc = pytz.utc
    lisbon = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário de Lisboa
    converted_timestamps = []
    for timestamp in timestamps:
        try:
            timestamp = timestamp.replace('T', ' ').replace('Z', '')  # Formata o timestamp
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).astimezone(lisbon)
        except ValueError:
            # Trata o caso onde os milissegundos não estão presentes
            converted_time = utc.localize(datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')).astimezone(lisbon)
        converted_timestamps.append(converted_time)  # Adiciona o timestamp convertido à lista
    return converted_timestamps

# Define o valor de lastN
lastN = 10  # Obtém os 10 pontos mais recentes a cada intervalo

app = dash.Dash(__name__)  # Inicializa o aplicativo Dash

# Layout do aplicativo
app.layout = html.Div([
    html.H1('Data Viewer'),  # Título do aplicativo
    dcc.Graph(id='luminosity-graph'),  # Gráfico de luminosidade
    dcc.Graph(id='humidity-graph'),  # Gráfico de umidade
    dcc.Graph(id='temperature-graph'),  # Gráfico de temperatura
    dcc.Store(id='luminosity-data-store', data={'timestamps': [], 'luminosity_values': []}),  # Armazena dados de luminosidade
    dcc.Store(id='humidity-data-store', data={'timestamps': [], 'humidity_values': []}),  # Armazena dados de umidade
    dcc.Store(id='temperature-data-store', data={'timestamps': [], 'temperature_values': []}),  # Armazena dados de temperatura
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # Intervalo de 10 segundos
        n_intervals=0
    )
])

# Callback para atualizar o armazenamento de dados de luminosidade
@app.callback(
    Output('luminosity-data-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('luminosity-data-store', 'data')
)
def update_data_store(n, stored_data):
    # Obtém dados de luminosidade
    data_luminosity = get_luminosity_data(lastN)

    if data_luminosity:
        # Extrai valores e timestamps
        luminosity_values = [float(entry['attrValue']) for entry in data_luminosity]  # Garante que os valores sejam floats
        timestamps = [entry['recvTime'] for entry in data_luminosity]

        # Converte timestamps para horário de Lisboa
        timestamps = convert_to_lisbon_time(timestamps)

        stored_data['timestamps'].extend(timestamps)  # Adiciona novos timestamps
        stored_data['luminosity_values'].extend(luminosity_values)  # Adiciona novos valores de luminosidade

        return stored_data  # Retorna os dados atualizados

    return stored_data  # Retorna os dados armazenados se não houver novos

# Callback para atualizar o gráfico de luminosidade
@app.callback(
    Output('luminosity-graph', 'figure'),
    Input('luminosity-data-store', 'data')
)
def update_luminosity_graph(stored_data):
    if stored_data['timestamps'] and stored_data['luminosity_values']:
        mean_luminosity = sum(stored_data['luminosity_values']) / len(stored_data['luminosity_values'])  # Calcula a média de luminosidade

        trace_luminosity = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['luminosity_values'],
            mode='lines+markers',
            name='Luminosity',
            line=dict(color='orange')  # Cor da linha do gráfico de luminosidade
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_luminosity, mean_luminosity],
            mode='lines',
            name='Mean Luminosity',
            line=dict(color='blue', dash='dash')  # Linha da média de luminosidade
        )

        fig_luminosity = go.Figure(data=[trace_luminosity, trace_mean])  # Cria a figura do gráfico
        fig_luminosity.update_layout(
            title='Luminosity Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Luminosity',
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_luminosity  # Retorna o gráfico

    return {}  # Retorna um dicionário vazio se não houver dados

# Callback para atualizar o gráfico de umidade
@app.callback(
    Output('humidity-graph', 'figure'),
    Input('humidity-data-store', 'data')
)
def update_humidity_graph(stored_data):
    if stored_data['timestamps'] and stored_data['humidity_values']:
        mean_humidity = sum(stored_data['humidity_values']) / len(stored_data['humidity_values'])  # Calcula a média de umidade

        trace_humidity = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['humidity_values'],
            mode='lines+markers',
            name='Humidity',
            line=dict(color='blue')  # Cor da linha do gráfico de umidade
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_humidity, mean_humidity],
            mode='lines',
            name='Mean Humidity',
            line=dict(color='red', dash='dash')  # Linha da média de umidade
        )

        fig_humidity = go.Figure(data=[trace_humidity, trace_mean])  # Cria a figura do gráfico
        fig_humidity.update_layout(
            title='Humidity Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Humidity',
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_humidity  # Retorna o gráfico

    return {}  # Retorna um dicionário vazio se não houver dados

# Callback para atualizar o gráfico de temperatura
@app.callback(
    Output('temperature-graph', 'figure'),
    Input('temperature-data-store', 'data')
)
def update_temperature_graph(stored_data):
    if stored_data['timestamps'] and stored_data['temperature_values']:
        mean_temperature = sum(stored_data['temperature_values']) / len(stored_data['temperature_values'])  # Calcula a média de temperatura

        trace_temperature = go.Scatter(
            x=stored_data['timestamps'],
            y=stored_data['temperature_values'],
            mode='lines+markers',
            name='Temperature',
            line=dict(color='green')  # Cor da linha do gráfico de temperatura
        )
        trace_mean = go.Scatter(
            x=[stored_data['timestamps'][0], stored_data['timestamps'][-1]],
            y=[mean_temperature, mean_temperature],
            mode='lines',
            name='Mean Temperature',
            line=dict(color='purple', dash='dash')  # Linha da média de temperatura
        )

        fig_temperature = go.Figure(data=[trace_temperature, trace_mean])  # Cria a figura do gráfico
        fig_temperature.update_layout(
            title='Temperature Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Temperature',
            hovermode='closest'  # Modo de hover mais próximo
        )

        return fig_temperature  # Retorna o gráfico

    return {}  # Retorna um dicionário vazio se não houver dados

# Inicializa o servidor do aplicativo
if __name__ == '__main__':
    app.run_server(debug=True, host=DASH_HOST, port=8050)
