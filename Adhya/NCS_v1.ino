#include <WiFi.h>
#include <WebServer.h>
#include <time.h>

const char* ssid = "Prashanth 2.4G";
const char* password = "Tata@123";

WebServer server(80);

#define TOUCH_CALL 4
#define TOUCH_ACK 15
#define TOUCH_CANCEL 13

#define RED_PIN 26
#define GREEN_PIN 25
#define BLUE_PIN 27
const int THRESHOLD=30;

enum State{IDLE,CALL,ACK,DONE};
State state=IDLE;

String callTime="--:--:--";
String ackTime="--:--:--";
unsigned long doneStart=0;

bool callLatched=false,ackLatched=false,cancelLatched=false;

String ts(){
  struct tm t;
  if(getLocalTime(&t)){
    char b[9];
    strftime(b,sizeof(b),"%H:%M:%S",&t);
    return String(b);
  }
  return "--:--:--";
}

void off(){digitalWrite(RED_PIN,HIGH);digitalWrite(GREEN_PIN,HIGH);digitalWrite(BLUE_PIN,HIGH);}
void blue(){digitalWrite(RED_PIN,HIGH);digitalWrite(GREEN_PIN,HIGH);digitalWrite(BLUE_PIN,LOW);}
void green(){digitalWrite(RED_PIN,HIGH);digitalWrite(GREEN_PIN,LOW);digitalWrite(BLUE_PIN,HIGH);}
void red(){digitalWrite(RED_PIN,LOW);digitalWrite(GREEN_PIN,HIGH);digitalWrite(BLUE_PIN,HIGH);}

void handleRoot(){
 String page=R"(
<!DOCTYPE html><html><head>
<meta http-equiv='refresh' content='1'>
<style>
body{margin:0;background:#eef2f7;font-family:Arial}
.header{background:#0B5ED7;color:#fff;text-align:center;padding:18px;font-size:30px;font-weight:bold}
.container{padding:25px;display:flex;gap:20px;flex-wrap:wrap}
.card{width:320px;height:285px;border-radius:12px;padding:20px;color:#fff;box-sizing:border-box;box-shadow:0 0 10px rgba(0,0,0,.25)}
.title{font-size:28px;font-weight:bold}
.status{font-size:21px;font-weight:bold;margin:18px 0}
.info{font-size:18px;line-height:1.8}
.idle{width:100%;margin-top:80px;text-align:center;font-size:34px;color:#666}
.idle small{display:block;margin-top:15px;font-size:20px}
</style></head><body>
<div class='header'>HOSPITAL NURSE DASHBOARD</div><div class='container'>
)";
 if(state==IDLE){
   page+="<div class='idle'>SYSTEM IDLE<small>No active patient requests.</small></div>";
 }else{
   String color="#0d6efd",txt="PATIENT ASSISTANCE REQUESTED";
   if(state==ACK){color="#198754";txt="NURSE RESPONDING";}
   if(state==DONE){color="#dc3545";txt="REQUEST RESOLVED";}
   page+="<div class='card' style='background:"+color+"'><div class='title'>WARD 101</div>";
   page+="<div class='status'>"+txt+"</div>";
   page+="<div class='info'><b>Bed:</b> 02<br><b>Patient Call:</b> "+callTime+"<br><b>Nurse ACK:</b> "+ackTime+"<br><b>ESP32:</b> ONLINE</div></div>";
 }
 page+="</div></body></html>";
 server.send(200,"text/html",page);
}

void setup() {

  Serial.begin(115200);
  delay(1000);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  off();

  Serial.println();
  Serial.println("================================");
  Serial.println("ESP32 Nurse Call System");
  Serial.println("================================");

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int retries = 0;

  while (WiFi.status() != WL_CONNECTED && retries < 30) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println("WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    configTime(19800, 0, "pool.ntp.org", "time.google.com");

    Serial.println("Web Server Started");
    Serial.print("Open: http://");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.begin();

  } else {

    Serial.println("WiFi Connection Failed!");
    Serial.print("WiFi Status Code: ");
    Serial.println(WiFi.status());

    Serial.println();
    Serial.println("Check:");
    Serial.println("1. SSID and password");
    Serial.println("2. Hotspot is ON");
    Serial.println("3. WiFi is 2.4 GHz");
  }
}

void loop(){
 server.handleClient();

 int c=touchRead(TOUCH_CALL);
 int a=touchRead(TOUCH_ACK);
 int x=touchRead(TOUCH_CANCEL);

 if(c<THRESHOLD){
   if(!callLatched && state==IDLE){
     callLatched=true;
     callTime=ts();
     ackTime="--:--:--";
     state=CALL;
     blue();
   }
 } else callLatched=false;

 if(a<THRESHOLD){
   if(!ackLatched && state==CALL){
     ackLatched=true;
     ackTime=ts();
     state=ACK;
     green();
   }
 } else ackLatched=false;

 if(x<THRESHOLD){
   if(!cancelLatched && state==ACK){
     cancelLatched=true;
     state=DONE;
     red();
     doneStart=millis();
   }
 } else cancelLatched=false;

 if(state==DONE && millis()-doneStart>=5000){
   off();
   state=IDLE;
   callTime="--:--:--";
   ackTime="--:--:--";
 }
}
