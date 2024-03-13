//////////////////////////Import de bilbiotecas e  afins ////////////////////////////////////

/*
  Bibiliotecas para do protocolo LoRa utilizando o as bilbiotecas do Haltec LoRa Esp V2
*/

#include <Wire.h>
#include "HT_SSD1306Wire.h"
#include "logo.h"
#include "LoRaWan_APP.h"
#include "Arduino.h"

/////////////////////// Defines e Globals /////////////////////////////////
#define LORA_PREAMBLE_LENGTH 8 // Same for Tx and Rx TODO set as variable in GNURadio
#define LORA_SYMBOL_TIMEOUT 0  // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON false
#define LORA_IQ_INVERSION_ON false
#define RX_TIMEOUT_VALUE 1000
#define BUFFER_SIZE 100

/////////////////////// Display e feedback //////////////////////////////

SSD1306Wire ESP_LORA_DISPLAY(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED); // addr , freq , i2c group , resolution , rst

int led_pin = 25;

////////////////////// LoRa Params ////////////////////////
long RF_FREQ = 915000000; // MHz
int TX_OUTPUT_PW = 10;    // dBm
int SF;                   // Spreading Factor [SF7..SF12]
int CR;                   // Coding Rate // [1: 4/5, 2: 4/6, 3: 4/7, 4: 4/8]
int BW;                   // [0: 125 kHz, 1: 250 kHz, 2: 500 kHz, 3: Reserved
bool lora_idle = true;
static RadioEvents_t RadioEvents;

int16_t txNumber;

int16_t rxSize;

/////////////////////////////////// Simulation Parameters
int MAX_MSG;
int msgSend = 0;
char msgToSendTransmit[50];
char msgReceived[50];
String buffer = ""; // a String to hold incoming data
char inputStr[50];
bool msgAvailable;
char *token;
bool canStart = false;
bool done = false;
bool notifyRXMessage = false;

/////////////////////////////////// Function headers /////////////////////////////////
void OnTxDone(void);
void OnTxTimeout(void);
void check_command(void);
void set_radio_params(void);
void set_BW(void);
void radio_init(void);
void OnRxDone( uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr );
/////////////////////////////////// Setup /////////////////////////////////
void setup()
{
    pinMode(led_pin, OUTPUT);
    Mcu.begin();
    // Draw logo on display
    ESP_LORA_DISPLAY.init();
    ESP_LORA_DISPLAY.clear();
    ESP_LORA_DISPLAY.drawXbm(0, 0, width_logo, height_logo, tx_logo_bits);
    delay(100);
    ESP_LORA_DISPLAY.display();
    buffer.reserve(BUFFER_SIZE);
    Serial.begin(57600); 
    radio_init();
    Serial.flush();
}

void set_BW(int BW_mhz)
{
    switch (BW_mhz)
    {
    case 125000:
        BW = 0;
        break;
    case 250000:
        BW = 1;
        break;
    default:
        BW = 2;
        break;
    }
}

void check_command()
{
    if(buffer.indexOf("!") > 0 ){ // Has correct termination
        digitalWrite(led_pin, HIGH);
        if (buffer.indexOf("Start") >= 0)
        {
            canStart = true;
            Serial.println("StartOk!");
            delay(3000);
        }
        else if (buffer.indexOf("Done") >= 0)
        {
            done = true;
            delay(3000);
            Serial.println("DoneOk!");
        }
        else if (buffer.indexOf("Setup") >= 0)
        {
            buffer.toCharArray(inputStr, buffer.length()); // copy buffer without \0
            inputStr[sizeof(msgToSendTransmit) -1 ] = '\0'; // forcing it to be a String
            // The first token should be "Setup"
            token = strtok(inputStr, "#");
            token = strtok(NULL, "#");
            
            if (token)
            {
                CR = atoi(token);
            }
            token = strtok(NULL, "#");
            
            if (token)
            {
                SF = atoi(token);
            }

            // Parse the frequency
            token = strtok(NULL, "#");
            
            if (token)
            {
                int BW_mhz = atol(token);
                set_BW(BW_mhz);
            }

            // Parse max messages
            token = strtok(NULL, "#");
            
            if (token)
            {
                MAX_MSG = atoi(token);
            }

            // Parse the message, which is the last part of the string
            token = strtok(NULL, "#");
            
            if (token)
            {
                TX_OUTPUT_PW = atoi(token);
            }
            
            // Parse the message, which is the last part of the string
            token = strtok(NULL, "#");

            if (token)
            {
                strncpy(msgToSendTransmit, token, sizeof(msgToSendTransmit));
                strcat(msgToSendTransmit, "\n"); 
               
            }
            set_radio_params();
            Serial.println("SetupOk!");
        }
    }
    else{
        Serial.println("Erro!");
    }
    buffer = "";
    msgAvailable = false;
    digitalWrite(led_pin, LOW);
}

void loop()
{
     if (canStart){
      if (!done)
      {
            if(lora_idle)
            {
                lora_idle = false;
                Radio.Rx(0);
            }
            Radio.IrqProcess();
      }
      else
      {  
          canStart = false;
          Serial.write("EndSimOk!\n");
          done=false;
      }
    }
    delayMicroseconds(500);
    if (msgAvailable)
    {
        Serial.println(buffer);
        check_command();
    }
    //delay(100);
}

void radio_init(){
    RadioEvents.TxDone = OnTxDone;
    RadioEvents.TxTimeout = OnTxTimeout;
    Radio.Init(&RadioEvents);
}

void set_radio_params()
{
    Radio.SetChannel(RF_FREQ);
    Radio.SetTxConfig(MODEM_LORA, TX_OUTPUT_PW, 0, BW,
                      SF, CR,
                      LORA_PREAMBLE_LENGTH, LORA_FIX_LENGTH_PAYLOAD_ON,
                      true, 0, 0, LORA_IQ_INVERSION_ON, 3000);
}

void serialEvent()
{
    while (Serial.available())
    {
        // get the new byte:
        char inChar = (char)Serial.read();
        // add it to the inputString:

        // if the incoming character is a newline, set a flag so the main loop can
        // do something about it:
        if (inChar == '\n')
        {
            msgAvailable = true;
        }
        else
        {
            buffer += inChar;
        }
    }
}

/**
 * @brief Função de evento que é disparada ao fim de uma transmissão
 *
 */
void OnTxDone(void)
{
    lora_idle = true;
}

/**
 * @brief Função de evento que é disparada ao fim de uma recepção
 *
 */
void OnTxTimeout(void)
{
    Radio.Sleep();
    lora_idle = true;
}

void OnRxDone( uint8_t *payload, uint16_t size, int16_t rssi, int8_t snr )
{
    rxSize=size;
    memcpy(msgReceived, payload, size );
    Radio.Sleep( );
    Serial.write(msgReceived,size);
    Serial.write('\n');
    notifyRXMessage = true; 
    lora_idle = true;
}