#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <VL53L0X.h>
 
 /*
 #############################################
	Modbus server code adapted from 
	https://github.com/glinvad/ESP6288-Modbus-no-lib 
	by glinvad on github.com
 #############################################
 */


const char* ssid = "TP-Link_8515";				// <----------- input your SSID
const char* password = "60924940";			// <----------- input your Password
// Set your Static IP address
IPAddress local_IP(192, 168, 1, 184);
// Set your Gateway IP address
IPAddress gateway(192, 168, 1, 1);

IPAddress subnet(255, 255, 0, 0);
int ModbusTCP_port = 502;

//////// Requred for I2C connected sensors
const u_int8_t NUMBER_OF_SENSORS = 7;
int xShutPins[NUMBER_OF_SENSORS] = {33, 21, 19, 32, 25, 26, 27};  //mapping af Xshut Pins
int sensorState[7] = {1, 1, 1, 1, 1, 1, 1};
VL53L0X sensor[NUMBER_OF_SENSORS];

//////// Required for Modbus TCP / IP /// 
#define maxInputRegister 20
#define maxHoldingRegister 8
 
#define MB_FC_NONE 0
#define MB_FC_READ_REGISTERS 3 				//implemented
#define MB_FC_WRITE_REGISTER 6 				//implemented
#define MB_FC_WRITE_MULTIPLE_REGISTERS 16 	//implemented


// MODBUS Error Codes
#define MB_EC_NONE 0
#define MB_EC_ILLEGAL_FUNCTION 1
#define MB_EC_ILLEGAL_DATA_ADDRESS 2
#define MB_EC_ILLEGAL_DATA_VALUE 3
#define MB_EC_SLAVE_DEVICE_FAILURE 4

// MODBUS MBAP offsets
#define MB_TCP_TID 0
#define MB_TCP_PID 2
#define MB_TCP_LEN 4
#define MB_TCP_UID 6
#define MB_TCP_FUNC 7
#define MB_TCP_REGISTER_START 8
#define MB_TCP_REGISTER_NUMBER 10
 
byte ByteArray[260];
unsigned int MBHoldingRegister[maxHoldingRegister];
 
//////////////////////////////////////////////////////////////////////////
 
WiFiServer MBServer(ModbusTCP_port);
 
void setup() {
	Wire.begin();
	Serial.begin(115200);

	if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  	}

	pinMode(14,OUTPUT);
	digitalWrite(14,LOW);

	for (int i = 0; i < NUMBER_OF_SENSORS; i++)
	{
		pinMode(xShutPins[i],OUTPUT);
		digitalWrite(xShutPins[i],LOW);
		Serial.print("IO:");
		Serial.print(i);
		Serial.println(" set");

	}
	
	for (int i = 0; i < NUMBER_OF_SENSORS; i++)
	{ 
		digitalWrite(xShutPins[i],HIGH);
		delay(100);
		if (sensor[i].init() != true) {
		Serial.println("Problems initialising ToF sensor");
		Serial.print(i);

	} else{
		Serial.print("Sensor");
		Serial.print(i);
		Serial.println(" initialised");
		delay(100); 
		sensor[i].setAddress((uint8_t)0x30+i);
		//sensor[i].setMeasurementTimingBudget(100000);

	}
		delay(50);

	}
	
	delay(2000);
	
	WiFi.begin(ssid, password);
	
	delay(100) ;
	
	Serial.println(".");
	
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.print(".");
	}
	
	MBServer.begin();
	
	Serial.println("Connected ");
	Serial.print("ESP8266 Slave Modbus TCP/IP ");
	Serial.print(WiFi.localIP());
	Serial.print(":");
	Serial.println(String(ModbusTCP_port));
	Serial.println("Modbus TCP/IP Online");
}
 
 
void loop() {
	// Check if a client has connected // Modbus TCP/IP
	WiFiClient client = MBServer.available();
	if (!client) {
		return;
	}
	
	boolean flagClientConnected = 0;
	byte byteFN = MB_FC_NONE;
 
	int Start;
	int WordDataLength;
	int ByteDataLength;
	int MessageLength;
 
	// Modbus TCP/IP
	while (client.connected()){
		if(client.available()){
			flagClientConnected = 1;
			int i = 0;
			while(client.available()){
				ByteArray[i] = client.read();
				i++;
			}
		client.flush();

		for (int i = 0; i < NUMBER_OF_SENSORS; i++)
  			{
			int tempDist = sensor[i].readRangeSingleMillimeters();
			Serial.print("Sensor ");
			Serial.print(i);
			Serial.print(": ");
			if (tempDist < 70)
			{
			sensorState[i] = 1;
			}else 
			{
			sensorState[i] = 0;
			}
			Serial.print(tempDist);
			Serial.println(" mm");
			delay(20);

			}
		Serial.println("");

		Serial.print(sensorState[4]);
		Serial.print(" | ");
		Serial.print(sensorState[5]);
		Serial.print(" | ");
		Serial.print(sensorState[6]);
		Serial.println(" | ");
		Serial.println("------------");
		Serial.print(sensorState[0]);
		Serial.print(" | ");
		Serial.print(sensorState[1]);
		Serial.print(" | ");
		Serial.print(sensorState[2]);
		Serial.print(" | ");
		Serial.print(sensorState[3]);
		Serial.println(" | ");
	
	/////// Holding Register [0] A [9] = 10 Holding Registers Writing
 	MBHoldingRegister[0] = sensorState[0];
	MBHoldingRegister[1] = sensorState[1];
	MBHoldingRegister[2] = sensorState[2];
	MBHoldingRegister[3] = sensorState[3];
	MBHoldingRegister[4] = sensorState[4];
	MBHoldingRegister[5] = sensorState[5];
	MBHoldingRegister[6] = sensorState[6];
 
 
	///// Holding Register [10] A [19] = 10 Holding Registers Reading
	int TempVal;
	
	//// debug
 
	
	Serial.print("register: [");
	Serial.print(7);
	Serial.print("] Drill status:");
	Serial.print(TempVal);
	Serial.println("");
 
	//// end code
 
 
	//// rutine Modbus TCP
	Serial.print("Byte array: ");
	for (int i = 0; i < 260; i++)
	{
		Serial.print(ByteArray[i]);
		Serial.print(" ");

	}
	Serial.println("");
	
	byteFN = ByteArray[MB_TCP_FUNC];
	//Serial.println(byteFN);
	Start = word(ByteArray[MB_TCP_REGISTER_START],ByteArray[MB_TCP_REGISTER_START+1]);
	Serial.println(Start);
	WordDataLength = word(ByteArray[MB_TCP_REGISTER_NUMBER],ByteArray[MB_TCP_REGISTER_NUMBER+1]);
	Serial.println(WordDataLength);
	}
	
 
	// Handle request

	switch(byteFN) {
		case MB_FC_NONE:
		break;
 
	case MB_FC_READ_REGISTERS: // 03 Read Holding Registers
		ByteDataLength = WordDataLength * 2;
		ByteArray[5] = ByteDataLength + 3; //Number of bytes after this one.
		ByteArray[8] = ByteDataLength; //Number of bytes after this one (or number of bytes of data).
		for(int i = 0; i < WordDataLength; i++){
			ByteArray[ 9 + i * 2] = highByte(MBHoldingRegister[Start + i]);
			ByteArray[10 + i * 2] = lowByte(MBHoldingRegister[Start + i]);
		}
		MessageLength = ByteDataLength + 9;
		client.write((const uint8_t *)ByteArray,MessageLength);
 
		byteFN = MB_FC_NONE;
 
		break;

	case MB_FC_WRITE_REGISTER: // 06 Write Holding Register
		MBHoldingRegister[Start] = word(ByteArray[MB_TCP_REGISTER_NUMBER],ByteArray[MB_TCP_REGISTER_NUMBER+1]);
		ByteArray[5] = 6; //Number of bytes after this one.
		MessageLength = 12;
		client.write((const uint8_t *)ByteArray,MessageLength);
		byteFN = MB_FC_NONE;
		break;
 
/*	case MB_FC_WRITE_MULTIPLE_REGISTERS: //16 Write Holding Registers
		ByteDataLength = WordDataLength * 2;
		ByteArray[5] = ByteDataLength + 3; //Number of bytes after this one.
		for(int i = 0; i < WordDataLength; i++){
			MBHoldingRegister[Start + i] = word(ByteArray[ 13 + i * 2],ByteArray[14 + i * 2]);
		}
		MessageLength = 12;
		client.write((const uint8_t *)ByteArray,MessageLength); 
		byteFN = MB_FC_NONE;
 
		break; */
		}

	if (MBHoldingRegister[7] == 1)
	{
		digitalWrite(14,HIGH);
	}else 
	{
		digitalWrite(14,LOW);
	}
	}
}