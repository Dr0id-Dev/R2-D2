#include <SPI.h>
#include <mcp_can.h>
#include <DFPlayer_Mini_Mp3.h>
#include <SoftwareSerial.h>

// Define CAN bus and DFPlayer Mini pins
#define CAN0_INT 2
MCP_CAN CAN0(10); // CS pin for MCP2515

// Define SoftwareSerial pins for DFPlayer Mini
SoftwareSerial mp3Serial(10, 11); // RX, TX

void setup() {
    Serial.begin(115200);
    mp3Serial.begin(9600); // Set DFPlayer Mini baud rate to 9600

    // Initialize CAN bus at 1 Mbps
    if (CAN0.begin(MCP_ANY, 1000, MCP_8MHZ) == CAN_OK) {
        Serial.println("CAN bus initialized");
    } else {
        Serial.println("CAN bus initialization failed");
        while (1);
    }
    CAN0.setMode(MCP_NORMAL);
    pinMode(CAN0_INT, INPUT);

    // Initialize DFPlayer Mini
    mp3_set_serial(mp3Serial); // Set the serial for DFPlayer Mini
    delay(500);
    mp3_set_volume(20); // Set volume (0-30)
    Serial.println("DFPlayer Mini ready");
}

void loop() {
    // Check if a CAN message is received
    if (!digitalRead(CAN0_INT)) {
        long unsigned int rxId;
        unsigned char len = 0;
        unsigned char rxBuf[8];

        // Read the CAN message
        CAN0.readMsgBuf(&rxId, &len, rxBuf);

        Serial.print("ID: ");
        Serial.print(rxId, HEX);
        Serial.print(" Data: ");
        for (int i = 0; i < len; i++) {
            Serial.print(rxBuf[i], HEX);
            Serial.print(" ");
        }
        Serial.println();

        // Parse the CAN message to determine which MP3 file to play
        // For example, let's assume rxBuf[0] indicates the file number to play
        int fileNumber = rxBuf[0]; // Extract file number from the first byte of the CAN message

        if (fileNumber >= 1 && fileNumber <= 255) {
            Serial.print("Playing MP3 file: ");
            Serial.println(fileNumber);
            mp3_play(fileNumber); // Play the corresponding MP3 file (e.g., "0001.mp3" for fileNumber = 1)
        }
    }
}
