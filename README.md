Bruno Biletsky   - RM: 554739

Enrico Ricarte   - RM: 558571

Victor Freire    - RM: 556191

Matheus Gushi    - RM: 556935

Pedro Ferrari    - RM: 554887

Link da simulação: https://wokwi.com/projects/407642666126106625
# Sistema de Monitoramento da Luminosidade, Temperatura e Umidade

Este projeto consiste em um sistema embarcado desenvolvido para monitorar  e controlar (localmente e à distancia) diversos aspectos do ESP32, utilizando a plataforma FIWARE para enviar os dados à NUVEM (para acessá-los de qualquer lugar), sensores. O código foi escrito em C++ para a plataforma Arduino.

## Componentes Utilizados
- **Plataforma FIWARE**:  Plataforma de infraestrutura aberta que será utilizada para captar e armazenar dados de temperatura e luminosidade dos sensores (permitindo acessar os dados de qualquer lugar a qualquer momento)
- **Serviço de computação em NUVEM**: Amazon Web Services (AWS)
- **ESP32**: Plataforma de desenvolvimento para sistemas embarcados com WI-FI integrado.
- **Sensores**:
  - Sensor DHT22: Utilizado para medir temperatura ambiente.
  - Sensor de luz.
  
## Funcionalidades Principais

### Envio de Dados em Tempo Real para a Nuvem 

![bitwise_diagrama_fiware](https://github.com/user-attachments/assets/a3dc91eb-b904-4c91-b249-e9147806a2fa)

#### Descrição do Sistema
Todos os dados de temperatura, Umidade e luminosidade captado pelo sistema é enviado em tempo real para a nuvem, utilizando a plataforma FIWARE. Esta funcionalidade é essencial para monitorar e analisar as condições, sendo assim criamos um DASHBOARD DINÂMICO desses dados.

#### Como a Plataforma FIWARE Funciona
A plataforma FIWARE é uma infraestrutura aberta que facilita a criação de aplicações inteligentes em diversas áreas, incluindo a Internet das Coisas (IoT). No contexto deste projeto, FIWARE é utilizada para captar e armazenar dados de temperatura e luminosidade dos sensores, sendo assim, através do POSTMAN podemos acessar em tempo real os dados captados pelos sensores, além de posteriormente possibilitar a criação de gráficos (dashboard histórico) para analisar os dados captados durante uma corrida ou até mesmo para verificá-los em tempo real através de um dashboard dinâmico.

#### Envio para a Nuvem
1. **Conexão**: O ESP32 se conecta à internet através de um módulo Wi-Fi ou Ethernet.

2. **Protocolo**: Utilizando protocolos como MQTT, os dados são enviados para o FIWARE Orion Context Broker.

#### Armazenamento e Processamento
1. **Orion Context Broker**: Este componente central do FIWARE recebe os dados e os armazena como entidades contextuais.

2. **Persistência**: Para armazenamento a longo prazo, os dados são enviados para um banco de dados MongoDB.

#### Análise e Visualização
1. **Ferramentas de Análise**: Após as informações serem armazenadas no MongoDB, podemos utilizar outras ferramentas para a coleta de dados históricos e a representação deles em dashboards estáticos (dados históricos) ou dinâmicos (atualizado em tempo real).

2. **Dashboard Dinâmico**: Utilizamos o STH-Comet para criar um Dashboard dinâmico que atualiza em tempo real. Feito com código python e inserido, por nós, diretamente na Virtual Machine da AWS.

### Monitoramento de Parâmetros

O sistema monitora continuamente a temperatura, luminosidade e umidade do ambiente utilizando o sensor DHT22 e LDR.


## Configuração e Uso

Para configurar e utilizar este sistema:

1. **Hardware**: Conecte os componentes conforme especificado no código (sensores, etc.).
  
2. **Software**: Crie um sistema FIWARE utilizando um serviço de CLOUD COMPUTING da usa preferência, nós utilizamos Amazon Web Services (AWS), para poder captar os dados dos sensores e armazená-los em um banco de dados. Carregue o código para a placa ESP32 utilizando a IDE Arduino. Certifique-se de ajustar quaisquer configurações necessárias no código, como o login e senha da sua coneção com a internet.

3. **Dashboard (Python)**: Crie um arquivo python para ser executado pelo serviço que você criará. Dessa forma você poderá criar seu Dashboard dinâmico usando dados do STH-Comet.

3.1 **Passos Detalhados**: Basta seguir os passos exemplificados na imagem e no link do vídeo a seguir: ![image](https://github.com/user-attachments/assets/a15234b1-cfb5-4a1e-96ab-938f6f7e2ef4) 

4. **Funcionamento**: Após carregar o código, o sistema começará a funcionar automaticamente. Através de uma API, você poderá acessar os dados enviados para sua plataforma FIWARE e trabalhar com os dados contidos no MongoDB. Além disso, com o serviço ativo os dashboards dinamicos poderão ser acessados através da URL http://IP-DA-VM:8050.
