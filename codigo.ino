#include <WiFi.h>              // Inclui a biblioteca para conexão WiFi
#include <PubSubClient.h>      // Inclui a biblioteca para comunicação MQTT
#include "DHT.h"               // Inclui a biblioteca para o sensor DHT

// Define os tópicos de comunicação MQTT
const char* TOPICPREFIX      = "lampbit";                      // Prefixo dos tópicos
const char* TOPICO_SUBSCRIBE = "/TEF/lampbit/cmd";            // Tópico para receber comandos
const char* TOPICO_PUBLISH_1 = "/TEF/lampbit/attrs";          // Tópico para publicar estado
const char* TOPICO_PUBLISH_LUMI = "/TEF/lampbit/attrs/l";     // Tópico para publicar luminosidade
const char* TOPICO_PUBLISH_TEMP = "/TEF/lampbit/attrs/t";     // Tópico para publicar temperatura
const char* TOPICO_PUBLISH_HUMID = "/TEF/lampbit/attrs/h";    // Tópico para publicar umidade

const bool  Simulation  = true;                                 // Define se está em modo simulação
const char* SSID        = Simulation ? "Wokwi-GUEST" : "FIAP-IBM"; // Nome da rede WiFi
const char* PASSWORD    = Simulation ? "" : "Challenge@24!";   // Senha da rede WiFi
const char* BROKER_MQTT = "18.117.118.157";                     // Endereço do broker MQTT
const int   BROKER_PORT = 1883;                                 // Porta do broker MQTT
const char* ID_MQTT     = "fiware_bit";                        // ID do cliente MQTT
const int   LED_PIN     = 2;                                   // Pino do LED

DHT dht(32, Simulation ? DHT22 : DHT11);                       // Inicializa o sensor DHT

WiFiClient espClient;                                          // Cliente WiFi
PubSubClient MQTT(espClient);                                  // Cliente MQTT
char estadoSaida = '0';                                       // Estado da saída do LED

void setup() {
    Serial.begin(115200);                                      // Inicia a comunicação serial
    pinMode(LED_PIN, OUTPUT);                                  // Configura o pino do LED como saída
    digitalWrite(LED_PIN, LOW);                                // Inicializa o LED apagado

    WiFi.begin(SSID, PASSWORD);                                // Conecta à rede WiFi
    dht.begin();                                              // Inicializa o sensor DHT

    while (WiFi.status() != WL_CONNECTED) {                   // Aguarda a conexão WiFi
        delay(100);
        // Serial.print(".");                                   // (opcional) imprime ponto enquanto conecta
    }
    Serial.println("\nConectado à rede WiFi");                 // Confirma a conexão
    Serial.print("IP: ");                                      // Imprime o IP local
    Serial.println(WiFi.localIP());

    MQTT.setServer(BROKER_MQTT, BROKER_PORT);                 // Define o servidor MQTT
    MQTT.setCallback(mqtt_callback);                           // Define a função de callback MQTT

    while (!MQTT.connected()) {                                 // Aguarda conexão com o broker MQTT
        if (MQTT.connect(ID_MQTT)) {                           // Tenta conectar
            MQTT.subscribe(TOPICO_SUBSCRIBE);                 // Assina o tópico de comandos
            MQTT.publish(TOPICO_PUBLISH_1, "s|on");          // Publica estado inicial
        } else {
            Serial.println("Falha ao conectar ao MQTT, tentando novamente em 2s"); // Erro na conexão
            delay(2000);                                       // Espera 2 segundos antes de tentar novamente
        }
    }

    for (int i = 0; i < 10; i++) {                             // Pisca o LED 10 vezes
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));         // Alterna o estado do LED
        delay(200);                                            // Aguarda 200ms
    }
}

void loop() {
    if (!MQTT.connected()) {                                   // Verifica se está conectado ao MQTT
        while (!MQTT.connected()) {                             // Tenta reconectar
            if (MQTT.connect(ID_MQTT)) {                      // Tenta conectar
                MQTT.subscribe(TOPICO_SUBSCRIBE);            // Reassina o tópico de comandos
            } else {
                delay(2000);                                   // Espera 2 segundos antes de tentar novamente
            }
        }
    }
    MQTT.loop();                                              // Mantém a conexão MQTT ativa

    handleDHT();                                             // Lida com o sensor DHT
    handleLuminosity();                                      // Lida com a luminosidade
    enviarEstadoOutputMQTT();                                // Envia o estado do LED via MQTT
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String msg;                                               // Cria uma string para a mensagem recebida
    for (unsigned int i = 0; i < length; i++) {              // Constrói a string a partir do payload
        msg += (char)payload[i];
    }

    // Verifica se a mensagem é um comando para acender ou apagar o LED
    if (msg == String(TOPICPREFIX)+"@on|") {
        digitalWrite(LED_PIN, HIGH);                          // Acende o LED
        estadoSaida = '1';                                    // Atualiza o estado
    } else if (msg == String(TOPICPREFIX)+"@off|") {
        digitalWrite(LED_PIN, LOW);                           // Apaga o LED
        estadoSaida = '0';                                    // Atualiza o estado
    }
}

void enviarEstadoOutputMQTT() {
    String status = (estadoSaida == '1') ? "s|on" : "s|off"; // Define o status do LED
    MQTT.publish(TOPICO_PUBLISH_1, status.c_str());        // Publica o estado do LED
    Serial.println("Estado do LED enviado ao broker!");      // Confirma o envio
    delay(1000);                                             // Espera 1 segundo
}

void handleDHT() {
    float temp = dht.readTemperature();                      // Lê a temperatura do sensor
    float humid = dht.readHumidity();                        // Lê a umidade do sensor
    MQTT.publish(TOPICO_PUBLISH_TEMP, String(temp).c_str()); // Publica a temperatura
    MQTT.publish(TOPICO_PUBLISH_HUMID, String(humid).c_str()); // Publica a umidade

    Serial.println("Temperatura: "+String(temp));           // Imprime a temperatura no serial
    Serial.println("Umidade: "+String(humid));              // Imprime a umidade no serial
}

void handleLuminosity() {
    int sensorValue = analogRead(34);                        // Lê o valor do sensor de luminosidade
    int luminosidade = map(sensorValue, 0, 4095, 0, 100);    // Mapeia o valor para uma escala de 0 a 100
    String mensagem = String(luminosidade);                  // Cria uma string com a luminosidade
    MQTT.publish(TOPICO_PUBLISH_LUMI, mensagem.c_str());    // Publica a luminosidade
    Serial.print("Luminosidade: ");                          // Imprime a luminosidade no serial
    Serial.println(mensagem);
}
