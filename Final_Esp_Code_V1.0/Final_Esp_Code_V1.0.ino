#include<ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#define SCAN_TIME 1000


bool isLEDOn = false;
int maxDevicesToScan = 5;
long lastScanTime;
const int temperatureInputPin = A0;
const int commonChannel = 8;
const int proximityIndicator = 2; 
float temperature = 0.0;

String serverSSID = "Bhak Bhak V1.0"; // This is the common ssid of all the servers.
String serverPassword = "iamtheprimeminister@2035"; // This is the common password for all the servers.

void readData(){
  // For the esp01 version, there will be no data, for the esp12 version we are only using the temperature sensor at analogue zero.
  // In a more expensive verion, the esp12 will also have a pulse sensor which will be connected to an external adc.
  temperature = analogRead(temperatureInputPin) * 0.48828125; // Easy peasy
}


void stopAndEvaluateScan(){
  isLEDOn = false;
  int x = WiFi.scanNetworks(false, false, commonChannel);
  for(int i = 0; i < maxDevicesToScan; i++){
      // Added "a" to the variable names because they were some sort of constants.
      // If the device is another mask, then check for proximity.
      Serial.println(x);
      if(WiFi.SSID(i).equals("CommonMaskSSid")){
        Serial.println("Found a mask.");
        if(WiFi.RSSI(i) > -40){
            isLEDOn = true;
        }
      }
      if(WiFi.SSID(i).equals(serverSSID)){
          Serial.println("Found a server.");
          // If the device is a server, send it the data.
          sendDataToServer();
      }
    }
}


void sendDataToServer(){
  // Send data to the server.
  Serial.println("Sending data to server");
  WiFi.begin(serverSSID, serverPassword);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(50);
    Serial.print(".");
  }
  HTTPClient http;
  http.begin("http://192.168.0.100/lol");
  http.addHeader("Content-Type", "application/x-www-form-urlencoded");
  Serial.println("Data sent : " + String(temperature) + " 0");
  auto result = http.POST(String(temperature) + " 0"); // Need to post the sensor readings here.
  String confirmation = http.getString();
  http.end();
  Serial.println("Data sent. code received is : " + String(result) + " " + confirmation);
}

// Follow this order of functions and then switch back to server
// mode and put on a delay of a 100ms.
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Started");
  WiFi.mode(WIFI_AP_STA);
  int maxConnections = 0;
  WiFi.softAP("CommonMaskSSid", "CommomMaskPassword", commonChannel, false, maxConnections); // Setup hidden access point
}


// Simple flow of functions:
// 1. Read data from the sensors, do not calculate the temperature, leave that on the server.
// 2. Network Scan
//  a. If server found, send data, then check for proximity.
//  b. If no server found, check for proximity.
void loop() {
  // put your main code here, to run repeatedly:
  WiFi.disconnect();
  Serial.println("Reading Data");

  // Read the data from the sensors, this is done in synchronous way. The time spent in this is also accounted in the scan time period delay.
  readData();
  //Starting the scan.
  Serial.println("Scanning the network.");
  stopAndEvaluateScan();
  // Just launch a simple indicator that the mask is in proximity.
  if(isLEDOn){
    Serial.println("------------------------PROXIMITY DETECTED------------------------");
  }else{
    
  }
}
