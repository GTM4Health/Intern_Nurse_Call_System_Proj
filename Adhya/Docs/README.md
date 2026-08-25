
````markdown
# 🏥 Nurse Call System

A real-time, ESP32-based Nurse Call System designed to improve communication between patients and healthcare staff. The system allows patients to request assistance, enables nurses to acknowledge and resolve requests, and provides a centralized web dashboard for real-time monitoring and event tracking.

Each ESP32 device represents a ward/bed unit and communicates with a central Python server over a local Wi-Fi network using TCP/IP.

---

## ✨ Features

- 📞 Real-time patient assistance requests
- ✅ Nurse acknowledgement and request resolution
- 📡 TCP/IP communication between ESP32 and server
- 🖥️ Live browser-based monitoring dashboard
- 📱 Support for multiple ward/bed ESP32 devices
- 🔐 MAC address-based ESP32 authorization
- ⚙️ Web-based ESP32 configuration
- 🟢 Online/offline device status monitoring
- 📋 Complete event logging
- 📊 Automatic Excel log generation and download
- 🎨 RGB LED status indication
- 🔄 Automatic request reset after completion

---

## 🏗️ System Architecture

```text
┌─────────────────┐
│  Patient / Bed  │
└────────┬────────┘
         │
         │ CALL / ACK / CANCEL
         ▼
┌─────────────────┐
│      ESP32      │
│                 │
│ • Button Inputs │
│ • RGB Status    │
│ • TCP Client    │
└────────┬────────┘
         │
         │ Wi-Fi / TCP-IP
         ▼
┌─────────────────┐
│  Python Server  │
│                 │
│ • TCP Server    │
│ • Authorization │
│ • Device State  │
│ • Event Logging │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐ ┌─────────────────┐
│  Web Dashboard  │ │  Event Logs     │
│                 │ │                 │
│ Real-Time View  │ │ JSON / Excel    │
└─────────────────┘ └─────────────────┘
````

---

## 🔄 System Workflow

```text
Patient presses CALL
        │
        ▼
ESP32 detects input
        │
        ▼
RGB LED → BLUE
        │
        ▼
CALL event sent to Python Server
        │
        ▼
Dashboard displays:
PATIENT ASSISTANCE REQUESTED
        │
        ▼
Nurse presses ACK
        │
        ▼
RGB LED → GREEN
        │
        ▼
Dashboard displays:
NURSE RESPONDING
        │
        ▼
Nurse presses CANCEL
        │
        ▼
RGB LED → RED
        │
        ▼
Dashboard displays:
REQUEST RESOLVED
        │
        ▼
System returns to IDLE
```

---

## 🧩 Hardware Components

| Component              |       Quantity | Purpose                     |
| ---------------------- | -------------: | --------------------------- |
| ESP32 DevKit           | 1 per bed/ward | Main controller             |
| Push Button            |              3 | CALL, ACK and CANCEL inputs |
| 100 nF Capacitor       |              3 | Button debouncing           |
| Common Cathode RGB LED |              1 | Local status indication     |
| 220 Ω Resistor         |              3 | RGB LED current limiting    |
| Breadboard / PCB       |              1 | Circuit implementation      |

### ESP32 Pin Connections

| Function      | ESP32 GPIO |
| ------------- | ---------: |
| CALL Button   |     GPIO 4 |
| ACK Button    |    GPIO 15 |
| CANCEL Button |    GPIO 13 |
| Red LED       |    GPIO 26 |
| Green LED     |    GPIO 25 |
| Blue LED      |    GPIO 27 |

---

## 📡 Communication

The Nurse Call System uses **TCP/IP communication** over a local Wi-Fi network.

```text
ESP32
   │
   │ JSON Message
   ▼
Python TCP Server
   │
   ▼
Web Dashboard
```

Each ESP32 sends event information to the server as a JSON message.

### Example Message

```json
{
    "mac": "20:E7:C8:69:08:E0",
    "ward": 101,
    "bed": 2,
    "event": "CALL",
    "time": "16:06:34",
    "call": "16:06:34",
    "ack": "--:--:--"
}
```

Messages are separated using a newline character so that the TCP server can process individual events.

---

## 🔐 ESP32 Authorization

Each ESP32 is identified using its unique MAC address.

Before a device can send nurse call events, it must be registered through the configuration page.

```text
           ESP32
             │
             │ Connection / Event
             ▼
      ┌───────────────┐
      │ Python Server │
      └───────┬───────┘
              │
        MAC Address Check
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
  REGISTERED     NOT REGISTERED
       │             │
       ▼             ▼
  AUTHORIZED       REJECTED
```

Only registered ESP32 devices are accepted by the system.

---

## 🚦 Request States

The system follows four main states:

```text
IDLE → CALL → ACK → DONE → IDLE
```

| State | Description                 | Dashboard Status             | RGB LED  |
| ----- | --------------------------- | ---------------------------- | -------- |
| IDLE  | No active request           | No Active Request            | OFF      |
| CALL  | Patient requests assistance | Patient Assistance Requested | 🔵 Blue  |
| ACK   | Nurse acknowledges request  | Nurse Responding             | 🟢 Green |
| DONE  | Request is completed        | Request Resolved             | 🔴 Red   |

---

## 🖥️ Web Dashboard

The web dashboard provides real-time monitoring of all registered ward/bed units.

The dashboard displays:

* Ward number
* Bed number
* Current request status
* Patient call time
* Nurse acknowledgement time
* ESP32 MAC address
* ESP32 online/offline status

Access the dashboard at:

```text
http://localhost:5001
```

---

## ⚙️ ESP32 Configuration

The configuration page allows administrators to manage ESP32 devices.

Functions include:

* Registering a new ESP32
* Assigning ward numbers
* Assigning bed numbers
* Adding ESP32 MAC addresses
* Viewing registered devices
* Deleting individual devices
* Deleting all registered devices

Access the configuration page at:

```text
http://localhost:5001/config
```

---

## 📋 Event Logs

The system records important events generated during operation.

Events include:

* ESP32 Connected
* ESP32 Disconnected
* ESP32 Registered
* ESP32 Deleted
* Patient CALL
* Nurse ACK
* Request Resolved

Logs are stored as:

```text
events.json
events.xlsx
```

The Excel event log can be downloaded directly from the Event Logs page.

Access the logs at:

```text
http://localhost:5001/admin
```

---

## 💻 Software Requirements

### Python

Python 3 is required.

Install the required packages:

```bash
pip install -r requirements.txt
```

Required packages include:

* Flask
* OpenPyXL

### ESP32

The ESP32 firmware is developed using:

* Arduino IDE
* ESP32 Board Package
* WiFi Library
* ArduinoJson Library

---

## 📁 Project Structure

```text
nurse-call-system/
│
├── README.md
├── requirements.txt
│
├── esp32/
│   └── nurse_call_esp32.ino
│
└── python/
    └── tcp.py
```

The following files are generated during system operation:

```text
devices.json
events.json
events.xlsx
```

These runtime files do not need to be included in the source repository.

---

## 🚀 Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nurse-call-system
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Python Server

Navigate to the Python folder and run:

```bash
python tcp.py
```

The TCP server will start and the dashboard will be available at:

```text
http://localhost:5001
```

---

### 4. Configure the ESP32

Open:

```text
esp32/nurse_call_esp32.ino
```

Configure the following values:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

const char* SERVER_IP = "YOUR_LAPTOP_IP";
const int SERVER_PORT = 5000;
```

Upload the code to the ESP32 using Arduino IDE.

---

### 5. Register the ESP32

Open:

```text
http://localhost:5001/config
```

Enter:

* Ward Number
* Bed Number
* ESP32 MAC Address

Save the configuration.

The ESP32 will then be authorized to communicate with the server.

---

## 🧪 Testing the System

After the ESP32 is connected and registered:

### CALL

1. Press the CALL button.
2. The RGB LED changes to Blue.
3. The server receives the CALL event.
4. The dashboard displays:

```text
PATIENT ASSISTANCE REQUESTED
```

### ACK

1. Press the ACK button.
2. The RGB LED changes to Green.
3. The dashboard updates to:

```text
NURSE RESPONDING
```

### CANCEL

1. Press the CANCEL button.
2. The RGB LED changes to Red.
3. The dashboard displays:

```text
REQUEST RESOLVED
```

The system then automatically returns to the IDLE state.

---

## 🔒 Security Notes

Do not upload real Wi-Fi credentials to GitHub.

Before committing the ESP32 code, replace credentials with placeholders:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

You should also avoid committing generated runtime files such as:

```text
devices.json
events.json
events.xlsx
```

These can be added to `.gitignore`.

---

## 📌 Future Scope

Possible future improvements include:

* Automatic ESP32 device discovery
* Push or mobile notifications for nurse alerts
* User authentication for administrators
* Multiple hospital department support
* Cloud-based data storage
* Advanced analytics for response times
* Priority-based emergency alerts
* Battery backup and power monitoring

---

## ❤️ Nurse Call System

**Connecting patients and caregivers for faster, smarter, and more responsive care.**

```
