#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Wifi_name";
const char* password = "wifi_password";

// IP OF THE NURSE STATION ESP32
String nurseStationIP = "";

// CHANGE THESE FOR EACH BED
String roomNumber = "102";
String patientName = "Charlie";

#define CALL_PIN 4
#define ACK_PIN 15
#define CANCEL_PIN 13

#define BUZZER_PIN 15

#define RED_PIN 33
#define GREEN_PIN 26
#define BLUE_PIN 25

#define TOUCH_THRESHOLD 500

bool activeCall = false;

void setRed()
{
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, HIGH);
    digitalWrite(BLUE_PIN, HIGH);
}

void setCyan()
{
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);
}

void setYellow()
{
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, HIGH);
}

void setWhite()
{
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);
}
void sendCall()
{
    if (WiFi.status() != WL_CONNECTED)
        return;

    HTTPClient http;

    String url =
        "http://" + nurseStationIP +
        "/call?room=" + roomNumber +
        "&patient=" + patientName +
        "&request=Nurse%20Call";

    http.begin(url);

    int code = http.GET();

    Serial.print("CALL Response: ");
    Serial.println(code);

    http.end();
}

void sendAck()
{
    if (WiFi.status() != WL_CONNECTED)
        return;

    HTTPClient http;

    String url =
        "http://" + nurseStationIP +
        "/ack?room=" + roomNumber;

    http.begin(url);

    int code = http.GET();

    Serial.print("ACK Response: ");
    Serial.println(code);

    http.end();
}

void sendCancel()
{
    if (WiFi.status() != WL_CONNECTED)
        return;

    HTTPClient http;

    String url =
        "http://" + nurseStationIP +
        "/cancel?room=" + roomNumber;

    http.begin(url);

    int code = http.GET();

    Serial.print("CANCEL Response: ");
    Serial.println(code);

    http.end();
}
void setup()
{
    Serial.begin(115200);

    pinMode(BUZZER_PIN, OUTPUT);

    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);

    setWhite();

    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi Connected!");
    Serial.print("Patient Unit IP: ");
    Serial.println(WiFi.localIP());

    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
}
void loop()
{
    // Reconnect WiFi if disconnected
    if (WiFi.status() != WL_CONNECTED)
    {
        WiFi.disconnect();
        WiFi.begin(ssid, password);

        while (WiFi.status() != WL_CONNECTED)
        {
            delay(500);
        }
    }

    // ================= CALL =================

    if (touchRead(CALL_PIN) < TOUCH_THRESHOLD)
    {
        if (!activeCall)
        {
            Serial.println("CALL pressed");

            sendCall();

            activeCall = true;

            setCyan();

            digitalWrite(BUZZER_PIN, HIGH);
            delay(500);
            digitalWrite(BUZZER_PIN, LOW);
        }

        while (touchRead(CALL_PIN) < TOUCH_THRESHOLD)
        {
            delay(10);
        }
    }

    // ================= ACK =================

    if (touchRead(ACK_PIN) < TOUCH_THRESHOLD)
    {
        if (activeCall)
        {
            Serial.println("ACK pressed");

            sendAck();

            setYellow();
        }

        while (touchRead(ACK_PIN) < TOUCH_THRESHOLD)
        {
            delay(10);
        }
    }

    // ================= CANCEL =================

    if (touchRead(CANCEL_PIN) < TOUCH_THRESHOLD)
    {
        if (activeCall)
        {
            Serial.println("CANCEL pressed");

            sendCancel();

            activeCall = false;

            setWhite();
        }

        while (touchRead(CANCEL_PIN) < TOUCH_THRESHOLD)
        {
            delay(10);
        }
    }

    delay(20);
}