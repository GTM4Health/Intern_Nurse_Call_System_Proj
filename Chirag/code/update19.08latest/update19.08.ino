#include <WiFi.h>
#include <WebServer.h>
#include <time.h>
#include <HTTPClient.h>
#include "logo.h"

const char* ssid = "Adhya";
const char* password = "hi123456";

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
struct RegisteredDevice
{
    String mac;
    String room;
    String patient;
};
struct RemoteCall
{
    String mac;

    String room;
    String patient;

    String request;
    String status;

    String callTime;
    String ackTime;

    String color;

    bool active;
};

RemoteCall remoteCalls[20];
RegisteredDevice registeredDevices[50];

int registeredCount = 0;

int remoteCount = 0;
void registerDevice(String mac, String room, String patient)
{
    // Check if MAC already exists
    for (int i = 0; i < registeredCount; i++)
    {
        if (registeredDevices[i].mac == mac)
        {
            registeredDevices[i].room = room;
            registeredDevices[i].patient = patient;
            return;
        }
    }

    if (registeredCount >= 50)
        return;

    registeredDevices[registeredCount].mac = mac;
    registeredDevices[registeredCount].room = room;
    registeredDevices[registeredCount].patient = patient;

    registeredCount++;
}
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
void addRemoteCall(String room,
                   String patient,
                   String request)
{
    // Check if this room already has an active call
    for (int i = 0; i < remoteCount; i++)
    {
        if (remoteCalls[i].room == room)
        {
            // Update the existing call instead of creating another
            Serial.println("Updating existing call");
            Serial.print("Room: ");
            Serial.println(room);
            remoteCalls[i].patient = patient;
            remoteCalls[i].request = request;
            remoteCalls[i].status = "Pending";
            remoteCalls[i].callTime = getTimeStamp();
            remoteCalls[i].ackTime = "--:--:--";
            remoteCalls[i].active = true;

            if (request == "Medicine Request")
                remoteCalls[i].color = "#0000ff";
            else
                remoteCalls[i].color = "#4FC3F7";

            return;
        }
    }

    // Create a new call if this room isn't already active
    if (remoteCount >= 20)
        return;

    remoteCalls[remoteCount].room = room;
    Serial.println("Creating new remote call");
Serial.print("Room: ");
Serial.println(room);
    Serial.println("----- NEW REMOTE CALL -----");
    Serial.println(remoteCalls[remoteCount].room);
    Serial.println(remoteCalls[remoteCount].patient);
    Serial.println(remoteCalls[remoteCount].request);
    remoteCalls[remoteCount].patient = patient;
    remoteCalls[remoteCount].request = request;
    remoteCalls[remoteCount].status = "Pending";
    remoteCalls[remoteCount].callTime = getTimeStamp();
    remoteCalls[remoteCount].ackTime = "--:--:--";
    remoteCalls[remoteCount].active = true;

    if (request == "Medicine Request")
        remoteCalls[remoteCount].color = "#0000ff";
    else
        remoteCalls[remoteCount].color = "#4FC3F7";

    remoteCount++;
}
String hospitalName = "{Healthcare Centre Name}";     // Change this whenever you want

String getNavbar()
{
    String nav = "";

    // ===== HEADER =====
    nav += "<div style='background:#1565C0;height:80px;"
           "display:flex;"
           "justify-content:space-between;"
           "align-items:center;"
           "padding:0 20px;"
           "color:white;'>";

    // Left side
    nav += "<div style='display:flex;align-items:center;'>";

    nav += "<img src='data:image/png;base64,";
nav += logoBase64;
nav += "' style='height:55px;background:white;padding:4px;border-radius:5px;'>";

    nav += "<span style='font-size:34px;font-weight:bold;margin-left:18px;'>";

    nav += "NURSE CALL SYSTEM";

    nav += "</span>";

    nav += "</div>";

    // Right side
    nav += "<span style='font-size:22px;font-weight:bold;'>";

    nav += hospitalName;

    nav += "</span>";

    nav += "</div>";

    // ===== MENU BAR =====

    nav += "<div style='background:white;"
           "padding:15px;"
           "border-bottom:2px solid #dcdcdc;"
           "box-shadow:0 2px 5px rgba(0,0,0,0.1);'>";

    nav += "<a href='/' style='color:#333;text-decoration:none;font-size:18px;font-weight:bold;margin:25px;'>Dashboard</a>";

    nav += "<a href='/devices' style='color:#333;text-decoration:none;font-size:18px;font-weight:bold;margin:25px;'>Device Manager</a>";

    nav += "<a href='/admin' style='color:#333;text-decoration:none;font-size:18px;font-weight:bold;margin:25px;'>Administration</a>";

    

    nav += "</div>";

    return nav;
}
void handleRoot()
{
    String page = "";

    page += "<html><head>";
    page += "<meta http-equiv='refresh' content='1'>";

    page += "<style>";
    page += "body{font-family:Arial;background:#f2f2f2;margin:0;padding:20px;text-align:center;}";
    page += "h1{margin-bottom:20px;}";
    page += ".grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}";
    page += ".card{padding:12px;height:200px;border-radius:12px;color:white;box-shadow:0 0 8px rgba(0,0,0,0.3);}";
    page += ".card h2{margin:4px 0;font-size:28px;}";
    page += ".card h3{margin:4px 0;font-size:22px;}";
    page += "p{margin:3px 0;font-size:18px;}";
    page += "</style>";

    page += "</head><body>";


page += getNavbar();


    page += "<div class='grid' style='padding:20px;'>";

    for(int i=0;i<registeredCount;i++)
    {
        int callIndex = -1;

        for(int j=0;j<remoteCount;j++)
        {
            if(remoteCalls[j].room == registeredDevices[i].room)
            {
                callIndex = j;
                break;
            }
        }

        String colour = "#9E9E9E";
        String request = "-";
        String status = "Idle";
        String call = "--:--:--";
        String ack = "--:--:--";

        if(callIndex != -1 && remoteCalls[callIndex].active)
        {
            colour = remoteCalls[callIndex].color;
            request = remoteCalls[callIndex].request;
            status = remoteCalls[callIndex].status;
            call = remoteCalls[callIndex].callTime;
            ack = remoteCalls[callIndex].ackTime;
        }

        page += "<div class='card' style='background:";
        page += colour;
        page += ";'>";

        page += "<h2>Room ";
        page += registeredDevices[i].room;
        page += "</h2>";

        page += "<h3>";
        page += registeredDevices[i].patient;
        page += "</h3>";

        page += "<p><b>Request:</b> ";
        page += request;
        page += "</p>";

        page += "<p><b>Status:</b> ";
        page += status;
        page += "</p>";

        page += "<p><b>Call:</b> ";
        page += call;
        page += "</p>";

        page += "<p><b>Ack:</b> ";
        page += ack;
        page += "</p>";

        page += "</div>";
    }

    page += "</div>";
    page += "<footer style='position:fixed;"
        "bottom:0;"
        "left:0;"
        "width:100%;"
        "height:45px;"
        "background:#1565C0;"
        "color:white;"
        "display:flex;"
        "justify-content:center;"
        "align-items:center;"
        "font-size:18px;'>";

page += "&copy; GTM4Health 2026";

page += "</footer>";
    page += "</body></html>";

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

    page += "<body style='margin:0;background:#f2f2f2;'>";
    page += getNavbar();
    page += "<h1>HOSPITAL ADMINISTRATION DASHBOARD</h1>";

    page += "<div class='card'>";

    page += "<h2>System Status</h2>";

    page += "<p>Total calls today: " + String(totalCallsToday) + "</p>";

    page += "<p>Active calls: " + String(activeCalls) + "</p>";

    page += "<p>Completed calls: " + String(completedCalls) + "</p>";

    page += "<p>Medicine requests: " + String(medicineRequests) + "</p>";

    page += "</div>";

    page += "<h2 style='margin-top:35px;'>Activity Log</h2>";
    page += "<table>";

page += "<tr>";

page += "<th>Room</th>";
page += "<th>Request</th>";
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
void handleDevices()
{
    if (!server.authenticate(adminUser, adminPass))
    {
        return server.requestAuthentication();
    }

    String page = "";

    page += "<html><head>";

    page += "<style>";

    page += "body{font-family:Arial;background:#f2f2f2;text-align:center;}";

    page += "table{margin:auto;border-collapse:collapse;width:90%;background:white;}";

    page += "th,td{border:1px solid black;padding:10px;}";

    page += "th{background:#4FC3F7;color:white;}";

    page += "input{padding:8px;margin:5px;}";

    page += "button{padding:10px 20px;}";

    page += "</style>";

    page += "</head><body>";
    page += getNavbar();
    page += "<h1>Device Manager</h1>";
    page += "<p>Add, manage and remove Nurse Call Units from the system.</p>";

    page += "<form action='/registerDevice'>";

    page += "MAC Address<br>";
    page += "<input name='mac'><br><br>";

    page += "Room Number<br>";
    page += "<input name='room'><br><br>";

    page += "Patient Name<br>";
    page += "<input name='patient'><br><br>";

    page += "<button type='submit'>Register Device</button>";

    page += "</form><br><br>";

    page += "<table>";

    page += "<tr>";

    page += "<th>MAC Address</th>";

    page += "<th>Room</th>";

    page += "<th>Patient</th>";
    page += "<th>Action</th>";
    page += "</tr>";

   for(int i=0;i<registeredCount;i++)
{
    page += "<tr>";

    page += "<td>"+registeredDevices[i].mac+"</td>";

    page += "<td>"+registeredDevices[i].room+"</td>";

    page += "<td>"+registeredDevices[i].patient+"</td>";

    page += "<td>";

    page += "<a href='/deleteDevice?mac=";
    page += registeredDevices[i].mac;
    page += "'>";

    page += "<button style='background:red;color:white;border:none;padding:8px 15px;border-radius:6px;cursor:pointer;'>Delete</button>";

    page += "</a>";

    page += "</td>";

    page += "</tr>";
}

    page += "</table>";
    page += "<footer style='position:fixed;"
        "bottom:0;"
        "left:0;"
        "width:100%;"
        "height:45px;"
        "background:#1565C0;"
        "color:white;"
        "display:flex;"
        "justify-content:center;"
        "align-items:center;"
        "font-size:18px;'>";

page += "&copy; GTM4Health 2026";

page += "</footer>";
    page += "</body></html>";

    server.send(200,"text/html",page);
}
void handleRegisterDevice()
{
    if (!server.authenticate(adminUser, adminPass))
    {
        return server.requestAuthentication();
    }

    String mac = server.arg("mac");
    String room = server.arg("room");
    String patient = server.arg("patient");

    registerDevice(mac, room, patient);

    server.sendHeader("Location", "/devices");
    server.send(303);
}
void handleRemoteCall()
{
    String mac = server.arg("mac");
    String request = server.arg("request");

    for (int i = 0; i < registeredCount; i++)
    {
        if (registeredDevices[i].mac == mac)
        {
            addRemoteCall(
                registeredDevices[i].room,
                registeredDevices[i].patient,
                request
            );

            totalCallsToday++;
            activeCalls++;

            if(request == "Medicine Request")
                medicineRequests++;

            server.send(200, "text/plain", "OK");
            return;
        }
    }

    server.send(404, "text/plain", "Device Not Registered");
}
void handleRemoteAck()
{
    String mac = server.arg("mac");

    for (int d = 0; d < registeredCount; d++)
    {
        if (registeredDevices[d].mac == mac)
        {
            String room = registeredDevices[d].room;

            for (int i = 0; i < remoteCount; i++)
            {
                if (remoteCalls[i].room == room && remoteCalls[i].active)
                {
                    remoteCalls[i].status = "Acknowledged";
                    remoteCalls[i].color = "#ffd700";
                    remoteCalls[i].ackTime = getTimeStamp();

                    server.send(200, "text/plain", "ACK OK");
                    return;
                }
            }

            server.send(404, "text/plain", "Call not found");
            return;
        }
    }

    server.send(404, "text/plain", "Device not registered");
}
void handleRemoteCancel()
{
    String mac = server.arg("mac");

    for (int d = 0; d < registeredCount; d++)
    {
        if (registeredDevices[d].mac == mac)
        {
            String room = registeredDevices[d].room;

            for (int i = 0; i < remoteCount; i++)
            {
                if (remoteCalls[i].room == room && remoteCalls[i].active)
                {
                    remoteCalls[i].active = false;

                    remoteCalls[i].status = "Idle";
                    remoteCalls[i].request = "-";
                    remoteCalls[i].callTime = "--:--:--";
                    remoteCalls[i].ackTime = "--:--:--";
                    remoteCalls[i].color = "#9E9E9E";

                    activeCalls--;

                    if (activeCalls < 0)
                        activeCalls = 0;

                    completedCalls++;

                    server.send(200, "text/plain", "CANCEL OK");
                    return;
                }
            }

            server.send(404, "text/plain", "Call not found");
            return;
        }
    }

    server.send(404, "text/plain", "Device not registered");
}
void handleLogs()
{
    if (!server.authenticate(adminUser, adminPass))
    {
        return server.requestAuthentication();
    }

    String page = "";

    page += "<html><head>";

    page += "<meta http-equiv='refresh' content='5'>";

    page += "<style>";

    page += "body{font-family:Arial;background:#f0f0f0;text-align:center;}";

    page += "table{margin:auto;border-collapse:collapse;width:90%;background:white;}";

    page += "th,td{border:1px solid black;padding:12px;}";

    page += "th{background:#1565C0;color:white;}";

    page += "</style>";

    page += "</head><body>";

    page += getNavbar();

    page += "<h1>Activity Logs</h1>";

    page += "<table>";

    page += "<tr>";
    page += "<th>Room</th>";
    page += "<th>Request</th>";
    page += "<th>Call Time</th>";
    page += "<th>Ack Time</th>";
    page += "<th>Response Time</th>";
    page += "</tr>";

    for(int i=0;i<logCount;i++)
    {
        page += "<tr>";

        page += "<td>"+logs[i].room+"</td>";
        page += "<td>"+logs[i].requestType+"</td>";
        page += "<td>"+logs[i].callTime+"</td>";
        page += "<td>"+logs[i].ackTime+"</td>";
        page += "<td>"+logs[i].responseTime+"</td>";

        page += "</tr>";
    }

    page += "</table>";
    page += "<footer style='position:fixed;"
        "bottom:0;"
        "left:0;"
        "width:100%;"
        "height:45px;"
        "background:#1565C0;"
        "color:white;"
        "display:flex;"
        "justify-content:center;"
        "align-items:center;"
        "font-size:18px;'>";

page += "&copy; GTM4Health 2026";

page += "</footer>";
    page += "</body></html>";

    server.send(200,"text/html",page);
}
void handleDeleteDevice()
{
    if (!server.authenticate(adminUser, adminPass))
    {
        return server.requestAuthentication();
    }

    String mac = server.arg("mac");

    for (int i = 0; i < registeredCount; i++)
    {
        if (registeredDevices[i].mac == mac)
        {
            for (int j = i; j < registeredCount - 1; j++)
            {
                registeredDevices[j] = registeredDevices[j + 1];
            }

            registeredCount--;
            break;
        }
    }

    server.sendHeader("Location", "/devices");
    server.send(302, "text/plain", "");
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
server.on("/call", handleRemoteCall);
server.on("/ack", handleRemoteAck);
server.on("/cancel", handleRemoteCancel);
server.on("/devices", handleDevices);
server.on("/registerDevice", handleRegisterDevice);
server.on("/logs", handleLogs);
server.on("/deleteDevice", handleDeleteDevice);

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
        String myMac = WiFi.macAddress();

for(int i=0;i<registeredCount;i++)
{
    if(registeredDevices[i].mac == myMac)
    {
        addRemoteCall(
            registeredDevices[i].room,
            registeredDevices[i].patient,
            "Nurse Call"
        );
        break;
    }
}
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
String myMac = WiFi.macAddress();

for(int i=0;i<registeredCount;i++)
{
    if(registeredDevices[i].mac == myMac)
    {
        addRemoteCall(
            registeredDevices[i].room,
            registeredDevices[i].patient,
            "Medicine Request"
        );
        break;
    }
}
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
String myMac = WiFi.macAddress();

for(int j=0;j<registeredCount;j++)
{
    if(registeredDevices[j].mac == myMac)
    {
        for(int i=0;i<remoteCount;i++)
        {
            if(remoteCalls[i].room == registeredDevices[j].room)
            {
                remoteCalls[i].status = "Acknowledged";
                remoteCalls[i].ackTime = getTimeStamp();
                remoteCalls[i].color = "#FFC107";
                break;
            }
        }
        break;
    }
}
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
String myMac = WiFi.macAddress();

for (int j = 0; j < registeredCount; j++)
{
    if (registeredDevices[j].mac == myMac)
    {
        for (int i = 0; i < remoteCount; i++)
        {
            if (remoteCalls[i].room == registeredDevices[j].room)
            {
                remoteCalls[i].active = false;

remoteCalls[i].status = "Idle";

remoteCalls[i].request = "-";

remoteCalls[i].callTime = "--:--:--";

remoteCalls[i].ackTime = "--:--:--";

remoteCalls[i].color = "#9E9E9E";

                break;
            }
        }

        break;
    }
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