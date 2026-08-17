# N-Bed Nurse Call System

An ESP32-based nurse call system for monitoring patient assistance requests across multiple hospital beds. The system uses **TCP/IP communication** between ESP32 devices and a Python server, with a web-based dashboard for monitoring and event logging.

## System Architecture

```
ESP32
  │
  │ TCP/IP
  ▼
Python TCP Server
  │
  ├── Hospital Dashboard
  ├── ESP32 Configuration
  ├── Event Logs
  └── Excel Logs
```

## Features

* ESP32-based patient nurse call system
* Touch-based **CALL**, **ACK**, and **CANCEL** controls
* TCP/IP communication between ESP32 and server
* MAC-address-based ESP32 authorization
* Support for multiple ESP32 devices
* Ward and bed configuration
* Real-time hospital nurse dashboard
* ESP32 online/offline status
* Patient call status tracking
* Event logging
* JSON-based event storage
* Excel event log generation
* Unauthorized ESP32 rejection
* ESP32 registration through a web configuration page

## Project Structure

```
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

## Hardware

* ESP32
* Touch input sensors
* RGB LED

## Software

* Arduino IDE
* Python 3
* Flask
* OpenPyXL

## Installation
### Python Server

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
python tcp.py
```

The Python server provides the following interfaces:

```text
Dashboard       http://localhost:5001
Configuration   http://localhost:5001/config
Event Logs      http://localhost:5001/admin
```

### ESP32

1. Open `nurse_call_esp32.ino` in Arduino IDE.
2. Select the appropriate ESP32 board.
3. Configure the Wi-Fi SSID and password.
4. Configure the Python server IP address.
5. Configure the ward and bed number.
6. Upload the code to the ESP32.
7. Open Serial Monitor at **115200 baud**.

## ESP32 Registration

Each ESP32 is identified using its MAC address.

Open:

```text
http://localhost:5001/config
```

Enter:

* ESP32 MAC address
* Ward number
* Bed number

Only registered ESP32 devices are authorized to communicate with the server.

## Event Flow

```text
Patient touches CALL
        │
        ▼
      ESP32
        │
        │ TCP/IP
        ▼
 Python TCP Server
        │
        ▼
   Nurse Dashboard
        │
        ▼
PATIENT ASSISTANCE REQUESTED
        │
        │ Nurse ACK
        ▼
   NURSE RESPONDING
        │
        │ Cancel / Resolve
        ▼
   REQUEST RESOLVED
```

## Event Logging

The server records events such as:

* ESP32 Connected
* Patient Call
* Nurse ACK
* Request Resolved
* ESP32 Disconnected
* ESP32 Registration
* ESP32 Deletion

The system maintains:

```text
devices.json
events.json
events.xlsx
```

`events.xlsx` can be downloaded directly from the Event Logs page.

## Web Interfaces
### Dashboard

Displays registered ESP32 devices and their current status.

```text
/
```

### ESP32 Configuration
Used to register, update, and delete ESP32 devices.

```text
/config
```

### Hospital Event Logs
Displays recorded system events and provides options to download Excel logs or clear existing logs.

```text
/admin
```
