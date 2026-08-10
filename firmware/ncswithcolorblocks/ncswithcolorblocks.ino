#include <WiFi.h>
#include <WebServer.h>
#include <time.h>

const char* ssid = "Sapthagiri 2nd F";
const char* password = "9916514093";

WebServer server(80);

#define CALL_PIN 4
#define ACK_PIN 13
#define CANCEL_PIN 14
#define MEDICINE_PIN 27

#define BUZZER_PIN 15

#define RED_PIN 33
#define GREEN_PIN 26
#define BLUE_PIN 25

#define TOUCH_THRESHOLD 500

String roomNumber = "101";
String patientName = "John Doe";

bool activeCall = false;

String requestType = "";
String statusText = "";

String callTime = "--:--:--";
String ackTime = "--:--:--";

String blockColor = "#ffffff";
const char* adminUser = "hospital_admin";
const char* adminPass = "NCS2026";

int totalCallsToday = 0;
int activeCalls = 0;
int completedCalls = 0;
int medicineRequests = 0;
struct Log
{
    String room;
    String requestType;
    String callTime;
    String ackTime;
    String responseTime;
};

Log logs[100];

int logCount = 0;
unsigned long callMillis = 0;
unsigned long ackMillis = 0;

int responseTime = 0;
bool logSaved = false;
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

void setBlue()
{
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(GREEN_PIN, HIGH);
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

String getTimeStamp()
{
    struct tm timeinfo;

    if (!getLocalTime(&timeinfo))
    {
        return "--:--:--";
    }

    char buffer[12];

    strftime(buffer, sizeof(buffer), "%I:%M:%S %p", &timeinfo);

    return String(buffer);
}

void handleRoot()
{
    String page = "";

    page += "<html>";

    page += "<head>";

    page += "<meta http-equiv='refresh' content='1'>";

    page += "<style>";

    page += "body{background:#f0f0f0;font-family:Arial;text-align:center;}";

    page += "h1{color:#222;}";

    page += ".card{";

    page += "width:700px;";
    page += "margin:20px auto;";
    page += "padding:20px;";
    page += "border-radius:15px;";
    page += "color:white;";
    page += "box-shadow:0 0 10px gray;";

    page += "}";

    page += "</style>";

    page += "</head>";

    page += "<body>";

    page += "<h1>NURSE CALL SYSTEM</h1>";

    if (activeCall)
    {
        page += "<div class='card' style='background:";
        page += blockColor;
        page += ";'>";

        page += "<h2>Room ";
        page += roomNumber;
        page += "</h2>";

        page += "<h3>";
        page += patientName;
        page += "</h3>";

        page += "<p><b>Request:</b> ";
        page += requestType;
        page += "</p>";

        page += "<p><b>Status:</b> ";
        page += statusText;
        page += "</p>";

        page += "<p><b>Call Time:</b> ";
        page += callTime;
        page += "</p>";

        page += "<p><b>Ack Time:</b> ";
        page += ackTime;
        page += "</p>";

        page += "</div>";
    }
    else
    {
        page += "<h2 style='color:#666; margin-top:150px;'>";
        page += "No active requests";
        page += "</h2>";
    }

    page += "</body>";

    page += "</html>";

    server.send(200, "text/html", page);
}
void handleAdmin()
{
    if (!server.authenticate(adminUser, adminPass))
    {
        return server.requestAuthentication();
    }

    String page = "";

    page += "<html>";

    page += "<head>";

    page += "<meta http-equiv='refresh' content='5'>";

    page += "<style>";

    page += "body{font-family:Arial;background:#f0f0f0;text-align:center;}";

    page += "table{margin:auto;border-collapse:collapse;width:90%;background:white;}";

    page += "th,td{border:1px solid black;padding:12px;}";

    page += "th{background:#4FC3F7;color:white;}";

    page += ".card{background:white;padding:20px;margin:20px auto;width:700px;border-radius:15px;box-shadow:0 0 10px gray;}";

    page += "</style>";

    page += "</head>";

    page += "<body>";

    page += "<h1>HOSPITAL ADMINISTRATION DASHBOARD</h1>";

    page += "<div class='card'>";

    page += "<h2>System Status</h2>";

    page += "<p>Total calls today: " + String(totalCallsToday) + "</p>";

    page += "<p>Active calls: " + String(activeCalls) + "</p>";

    page += "<p>Completed calls: " + String(completedCalls) + "</p>";

    page += "<p>Medicine requests: " + String(medicineRequests) + "</p>";

    page += "</div>";

    page += "<h2>Recent Activity</h2>";

    page += "<table>";

    page += "<tr>";

    page += "<th>Room</th>";
    page += "<th>Request Type</th>";
    page += "<th>Call Time</th>";
    page += "<th>Acknowledged</th>";
    page += "<th>Response Time</th>";

    page += "</tr>";

    for (int i = 0; i < logCount; i++)
    {
        page += "<tr>";

        page += "<td>" + logs[i].room + "</td>";

        page += "<td>" + logs[i].requestType + "</td>";

        page += "<td>" + logs[i].callTime + "</td>";

        page += "<td>" + logs[i].ackTime + "</td>";

        page += "<td>" + logs[i].responseTime + "</td>";

        page += "</tr>";
    }

    page += "</table>";

    page += "</body>";

    page += "</html>";

    server.send(200, "text/html", page);
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

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();

    Serial.println(WiFi.localIP());

    configTime(19800, 0, "pool.ntp.org");

    Serial.println("Waiting for time...");

    struct tm timeinfo;

    while (!getLocalTime(&timeinfo))
    {
        Serial.print(".");
        delay(1000);
    }

    Serial.println("\nTime synchronized!");

    server.on("/", handleRoot);
    server.on("/admin", handleAdmin);

    server.begin();

    Serial.println("Server started");
}

void loop()
{
    server.handleClient();

    if (touchRead(CALL_PIN) < TOUCH_THRESHOLD)
    {
        activeCall = true;

        requestType = "Nurse Call";

        statusText = "Pending";

        callTime = getTimeStamp();

        logSaved = false;

        callMillis = millis();

        totalCallsToday++;

        activeCalls++;
        ackTime = "--:--:--";

        blockColor = "#4FC3F7";

        setCyan();

        server.handleClient();

        digitalWrite(BUZZER_PIN, HIGH);

        delay(3000);

        digitalWrite(BUZZER_PIN, LOW);

        while (touchRead(CALL_PIN) < TOUCH_THRESHOLD)
        {
            delay(10);
        }
    }

    if (touchRead(MEDICINE_PIN) < TOUCH_THRESHOLD)
    {
        activeCall = true;

        requestType = "Medicine Request";

        statusText = "Pending";

        callTime = getTimeStamp();

        logSaved = false;

        callMillis = millis();

        totalCallsToday++;

        medicineRequests++;

        activeCalls++;

        ackTime = "--:--:--";

        blockColor = "#0000ff";

        setBlue();

        for (int i = 0; i < 3; i++)
        {
            digitalWrite(BUZZER_PIN, HIGH);

            delay(500);

            digitalWrite(BUZZER_PIN, LOW);

            delay(500);
        }

        while (touchRead(MEDICINE_PIN) < TOUCH_THRESHOLD)
        {
            delay(10);
        }
    }

    if (touchRead(ACK_PIN) < TOUCH_THRESHOLD)
{
    if (!logSaved)
    {
        statusText = "Acknowledged";

        blockColor = "#ffd700";

        setYellow();

        ackTime = getTimeStamp();

        ackMillis = millis();

        responseTime = (ackMillis - callMillis) / 1000;

        logs[logCount].room = roomNumber;

        logs[logCount].requestType = requestType;

        logs[logCount].callTime = callTime;

        logs[logCount].ackTime = ackTime;

        if (responseTime < 60)
        {
            logs[logCount].responseTime =
                String(responseTime) + " sec";
        }
        else
        {
            int minutes = responseTime / 60;
            int seconds = responseTime % 60;

            logs[logCount].responseTime =
                String(minutes) + " min " +
                String(seconds) + " sec";
        }

        logCount++;

        logSaved = true;
    }

    while (touchRead(ACK_PIN) < TOUCH_THRESHOLD)
    {
        delay(10);
    }
}

    if (touchRead(CANCEL_PIN) < TOUCH_THRESHOLD)
{
    if (activeCall)
{
    activeCalls--;
    if (activeCalls < 0)
        {
            activeCalls = 0;
        }
    completedCalls++;

    activeCall = false;
}

    requestType = "";

    statusText = "";

    callTime = "--:--:--";

    ackTime = "--:--:--";

    blockColor = "#ffffff";

    setWhite();

    while (touchRead(CANCEL_PIN) < TOUCH_THRESHOLD)
    {
        delay(10);
    }
}
}