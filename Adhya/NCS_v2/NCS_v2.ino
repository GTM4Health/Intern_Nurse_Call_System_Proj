#include <WiFi.h>
#include <time.h>

// =====================================================
// WIFI
// =====================================================

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// =====================================================
// LAPTOP TCP SERVER
// =====================================================

const char* SERVER_IP = "192.168.1.3";
const uint16_t SERVER_PORT = 5000;

WiFiClient tcpClient;

// =====================================================
// WARD CONFIGURATION
// =====================================================

#define WARD_NO 101
#define BED_NO 2

// =====================================================
// TOUCH SENSORS
// =====================================================

#define TOUCH_CALL   4
#define TOUCH_ACK    15
#define TOUCH_CANCEL 13

const int THRESHOLD = 30;

// =====================================================
// RGB LED
// =====================================================

#define RED_PIN   26
#define GREEN_PIN 25
#define BLUE_PIN  27

// =====================================================
// STATE MACHINE
// =====================================================

enum State
{
  IDLE,
  CALL,
  ACK,
  DONE
};

State state = IDLE;

// =====================================================
// TIMESTAMPS
// =====================================================

String callTime = "--:--:--";
String ackTime  = "--:--:--";
String doneTime = "--:--:--";

unsigned long doneStart = 0;

// =====================================================
// TOUCH LATCHING
// =====================================================

bool callLatched = false;
bool ackLatched = false;
bool cancelLatched = false;

// =====================================================
// SERVER AUTHORIZATION
// =====================================================

// IMPORTANT:
// Touch events are allowed ONLY after the server
// confirms that this MAC address is registered.

bool serverAuthorized = false;

// =====================================================
// CONNECTION TIMING
// =====================================================

unsigned long lastConnectionAttempt = 0;

const unsigned long RECONNECT_INTERVAL = 5000;

// =====================================================
// GET CURRENT TIME
// =====================================================

String ts()
{
  struct tm t;

  if (getLocalTime(&t))
  {
    char b[9];

    strftime(b, sizeof(b), "%H:%M:%S", &t);

    return String(b);
  }

  return "--:--:--";
}

// =====================================================
// LED FUNCTIONS
// =====================================================

void off()
{
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, HIGH);
}

void blue()
{
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, LOW);
}

void green()
{
  digitalWrite(RED_PIN, HIGH);
  digitalWrite(GREEN_PIN, LOW);
  digitalWrite(BLUE_PIN, HIGH);
}

void red()
{
  digitalWrite(RED_PIN, LOW);
  digitalWrite(GREEN_PIN, HIGH);
  digitalWrite(BLUE_PIN, HIGH);
}

// =====================================================
// WIFI CONNECTION
// =====================================================

void connectWiFi()
{
  if (WiFi.status() == WL_CONNECTED)
    return;

  Serial.println();
  Serial.println("Connecting to WiFi...");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);

  WiFi.begin(ssid, password);

  int retries = 0;

  while (WiFi.status() != WL_CONNECTED && retries < 30)
  {
    delay(500);

    Serial.print(".");

    retries++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("WiFi Connected!");

    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    Serial.print("ESP32 MAC: ");
    Serial.println(WiFi.macAddress());
  }
  else
  {
    Serial.println("WiFi Connection Failed!");
  }
}

// =====================================================
// WAIT FOR SERVER AUTHORIZATION
// =====================================================

bool waitForAuthorization()
{
  unsigned long startTime = millis();

  String response = "";

  Serial.println("Waiting for server authorization...");

  while (millis() - startTime < 3000)
  {
    while (tcpClient.available())
    {
      char c = tcpClient.read();

      response += c;

      // Server sends one JSON response per line
      if (c == '\n')
      {
        response.trim();

        Serial.print("Server response: ");
        Serial.println(response);

        if (response.indexOf("\"AUTHORIZED\"") >= 0)
        {
          Serial.println("ESP32 AUTHORIZED!");

          serverAuthorized = true;

          return true;
        }

        if (response.indexOf("\"REJECTED\"") >= 0)
        {
          Serial.println("ESP32 REJECTED!");

          serverAuthorized = false;

          tcpClient.stop();

          return false;
        }

        response = "";
      }
    }

    delay(10);
  }

  Serial.println("Authorization timeout.");

  serverAuthorized = false;

  tcpClient.stop();

  return false;
}

// =====================================================
// TCP CONNECTION
// =====================================================

bool connectToServer()
{
  if (tcpClient.connected() && serverAuthorized)
    return true;

  // Reset authorization every time we create
  // a new TCP connection.

  serverAuthorized = false;

  if (tcpClient.connected())
  {
    tcpClient.stop();
    delay(100);
  }

  Serial.println();
  Serial.print("Connecting to laptop server: ");
  Serial.print(SERVER_IP);
  Serial.print(":");
  Serial.println(SERVER_PORT);

  if (tcpClient.connect(SERVER_IP, SERVER_PORT))
  {
    Serial.println("TCP Server Connected!");

    // -------------------------------------------------
    // REGISTER THIS ESP32
    // -------------------------------------------------

    sendEvent("REGISTER");

    // -------------------------------------------------
    // WAIT FOR AUTHORIZED / REJECTED
    // -------------------------------------------------

    if (waitForAuthorization())
    {
      Serial.println("Ready for nurse call events.");

      return true;
    }

    Serial.println("Server did not authorize this ESP32.");

    tcpClient.stop();

    return false;
  }

  Serial.println("TCP Connection Failed.");

  return false;
}

// =====================================================
// SEND DATA TO LAPTOP
// =====================================================

void sendEvent(String event)
{
  if (!tcpClient.connected())
  {
    Serial.println("Server not connected. Data not sent.");
    return;
  }

  String mac = WiFi.macAddress();

  String timeValue = ts();

  String json = "{";

  json += "\"mac\":\"";
  json += mac;
  json += "\",";

  json += "\"ward\":";
  json += String(WARD_NO);
  json += ",";

  json += "\"bed\":";
  json += String(BED_NO);
  json += ",";

  json += "\"event\":\"";
  json += event;
  json += "\",";

  json += "\"time\":\"";
  json += timeValue;
  json += "\",";

  json += "\"call\":\"";
  json += callTime;
  json += "\",";

  json += "\"ack\":\"";
  json += ackTime;
  json += "\"";

  json += "}";

  tcpClient.println(json);

  Serial.println();
  Serial.println("Data sent to laptop:");
  Serial.println(json);
}

// =====================================================
// SETUP
// =====================================================

void setup()
{
  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("====================================");
  Serial.println(" N-BED NURSE CALL - WARD ESP32");
  Serial.println("====================================");

  // ---------------------------------------------------
  // RGB LED
  // ---------------------------------------------------

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  off();

  // ---------------------------------------------------
  // WIFI
  // ---------------------------------------------------

  connectWiFi();

  if (WiFi.status() == WL_CONNECTED)
  {
    // -------------------------------------------------
    // TIME
    // -------------------------------------------------

    configTime(
      19800,
      0,
      "pool.ntp.org",
      "time.google.com"
    );

    Serial.println();
    Serial.println("Device Information:");

    Serial.print("Ward: ");
    Serial.println(WARD_NO);

    Serial.print("Bed: ");
    Serial.println(BED_NO);

    Serial.print("MAC: ");
    Serial.println(WiFi.macAddress());

    Serial.println();
    Serial.println("Ready.");
  }
}

// =====================================================
// LOOP
// =====================================================

void loop()
{
  // ===================================================
  // WIFI
  // ===================================================

  if (WiFi.status() != WL_CONNECTED)
  {
    serverAuthorized = false;

    connectWiFi();

    delay(100);

    return;
  }

  // ===================================================
  // TCP SERVER CONNECTION
  // ===================================================

  if (!tcpClient.connected() || !serverAuthorized)
  {
    unsigned long now = millis();

    if (now - lastConnectionAttempt >= RECONNECT_INTERVAL)
    {
      lastConnectionAttempt = now;

      connectToServer();
    }

    // VERY IMPORTANT:
    // Do NOT process touch buttons until the server
    // has authorized this ESP32.

    delay(10);

    return;
  }

  // ===================================================
  // PATIENT CALL
  // ===================================================

  int c = touchRead(TOUCH_CALL);

  if (c < THRESHOLD)
  {
    if (!callLatched && state == IDLE)
    {
      callLatched = true;

      callTime = ts();

      ackTime = "--:--:--";

      doneTime = "--:--:--";

      state = CALL;

      blue();

      Serial.println();
      Serial.println("PATIENT CALL");

      sendEvent("CALL");
    }
  }
  else
  {
    callLatched = false;
  }

  // ===================================================
  // NURSE ACK
  // ===================================================

  int a = touchRead(TOUCH_ACK);

  if (a < THRESHOLD)
  {
    if (!ackLatched && state == CALL)
    {
      ackLatched = true;

      ackTime = ts();

      state = ACK;

      green();

      Serial.println();
      Serial.println("NURSE ACK");

      sendEvent("ACK");
    }
  }
  else
  {
    ackLatched = false;
  }

  // ===================================================
  // CANCEL
  // ===================================================

  int x = touchRead(TOUCH_CANCEL);

  if (x < THRESHOLD)
  {
    if (!cancelLatched && state == ACK)
    {
      cancelLatched = true;

      doneTime = ts();

      state = DONE;

      red();

      doneStart = millis();

      Serial.println();
      Serial.println("REQUEST CANCELLED");

      sendEvent("DONE");
    }
  }
  else
  {
    cancelLatched = false;
  }

  // ===================================================
  // RETURN TO IDLE AFTER 5 SECONDS
  // ===================================================

  if (
    state == DONE &&
    millis() - doneStart >= 5000
  )
  {
    off();

    state = IDLE;

    callTime = "--:--:--";

    ackTime = "--:--:--";

    doneTime = "--:--:--";

    Serial.println();
    Serial.println("SYSTEM IDLE");

    sendEvent("IDLE");
  }

  delay(10);
}
