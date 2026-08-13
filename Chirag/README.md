"# Intern_Nurse_Call_System_Proj" 

# Nurse Call System (NCS)

## Project Overview

The **Nurse Call System (NCS)** is a digital patient-to-nurse communication and monitoring system designed to allow patients to request assistance from a centralized nurse station.

The system provides multiple types of patient requests, including **Call, Acknowledge, Cancel, and Medication Request**. Each request is displayed at the nurse station using color-coded blocks that indicate the current state of the request.

The system also records important response-time information such as the **call time, acknowledgement time, and response time**, allowing the performance of the nurse response process to be monitored and analyzed.

An **Admin User Portal** is also included for authorized users to monitor and manage system information.

---

## Main Features

* Patient call functionality
* Call acknowledgement
* Call cancellation
* Medication request
* Multiple patient call handling
* Color-coded call status display
* Audible buzzer indication
* LED status indication
* Call timestamp logging
* Acknowledgement timestamp logging
* Response time calculation
* Patient/request identification
* Nurse station monitoring
* Admin user portal
* Centralized call management
* Call history and response monitoring

---

## System Functions

### 1. CALL

The **CALL** button is used by the patient to request assistance from the nursing station.

When pressed:

1. The patient unit generates a call request.
2. The request is transmitted to the nurse station.
3. A new patient block appears on the display.
4. The corresponding status color is displayed.
5. The buzzer provides an audible notification.
6. LED indicators provide a visual indication.
7. The exact **call time** is recorded.

---

### 2. ACKNOWLEDGE (ACK)

The **ACK** function allows the nurse to acknowledge that the call has been received and noticed.

When a call is acknowledged:

* The call status changes on the display.
* The corresponding block changes color.
* The acknowledgement time is recorded.
* The system stops or changes the notification indication as configured.
* The call remains available until it is completed/cancelled.

---

### 3. CANCEL

The **CANCEL** function is used to close an active request after the required assistance has been provided or when the request is no longer required.

When cancelled:

* The call status is updated.
* The corresponding patient block is removed/updated according to the system logic.
* The call event is recorded.
* The system retains the relevant timing information for monitoring.

---

### 4. MEDICATION REQUEST

The **MED REQ** button allows the patient to specifically request medication or assistance related to medication.

The request is transmitted to the nurse station and displayed separately from a normal call so that the nurse can identify the type of assistance required.

---

# Display and Color-Coded Status

The nurse station display provides a visual representation of active patient requests.

Each patient/request is represented using a **separate block**.

The block color changes according to the current state of the request.

Typical states include:

| State               | Description                                 |
| ------------------- | ------------------------------------------- |
| Call                | Patient has initiated a request             |
| Acknowledged        | Nurse has received/acknowledged the request |
| Medication Request  | Patient has requested medication            |
| Cancelled/Completed | Request has been completed or cancelled     |

The color-coded interface allows the nurse to quickly identify the current condition of each request without having to inspect individual records.

The display also supports **multiple simultaneous patient requests**, with the requests appearing as separate blocks.

---

# Audible and Visual Indicators

## Buzzer

The buzzer provides an audible notification when a new patient request is received.

This helps attract the nurse's attention even when the display is not being actively monitored.

## LED Indicators

LEDs provide additional visual feedback for system states and request activity.

The LED indication is synchronized with the system state to provide a quick physical indication of an active request or system event.

---

# Call Timing and Response Monitoring

One of the important features of the NCS is the recording of timestamps associated with each patient request.

For every call, the system records:

### Call Time

The exact time at which the patient initiates the request.

### Acknowledgement Time

The time at which the nurse acknowledges the request.

### Response Time

The time taken between the initial patient request and the nurse's acknowledgement.

**Response Time = Acknowledgement Time − Call Time**

This information can be used to evaluate nurse response performance and identify delays in responding to patient requests.

### Example

```text
Call Time          : 10:30:15
Acknowledgement    : 10:31:02
Response Time      : 47 seconds
```

The recorded information can be used for monitoring, analysis, and future improvements to the nurse call workflow.

---

# Admin User Portal

The system includes an **Admin User Portal** for authorized system administrators.

The portal can be used to monitor system information and manage the nurse call system.

### Admin Functions

* View patient requests
* Monitor active calls
* View request status
* Monitor call history
* View call and acknowledgement timestamps
* Monitor response times
* Analyze response performance
* Manage system information

### Authentication

The Admin Portal uses username/password authentication.

**Username:** `hospital_admin`

**Password:** `Not stored in GitHub`

> The administrator password should be configured securely and must not be committed to the GitHub repository. Credentials should be stored using a secure configuration mechanism or environment variables.

---

# System Workflow

```text
Patient
   │
   ▼
Press CALL / MED REQ
   │
   ▼
Patient Unit
   │
   ▼
Request Transmitted
   │
   ▼
Nurse Station
   │
   ├── Display Patient Block
   ├── Activate Buzzer
   └── Activate LED Indication
   │
   ▼
Nurse Acknowledges
   │
   ▼
Acknowledgement Time Recorded
   │
   ▼
Response Time Calculated
   │
   ▼
Patient Request Completed
   │
   ▼
CANCEL / Completion
   │
   ▼
Request Logged
```

---

# Hardware

The prototype consists of embedded hardware and user-interface components required to implement the nurse call system.

Main components include:

* Microcontroller
* Patient call buttons
* Acknowledge button
* Cancel button
* Medication request button
* LEDs / RGB LED indicators
* Buzzer
* Display
* Resistors
* Capacitors
* Connecting wires
* Power supply
* Patient-side hardware
* Nurse-station hardware

---

# Software

The system software consists of embedded firmware and the monitoring/admin interface.

### Development Tools

* Arduino IDE
* Visual Studio Code
* GitHub
* Embedded C/C++

---

# Project Structure

```text
NCS-System/
│
├── Main_Code/
│   └── Main system code
│
├── Patient_Code/
│   └── Patient unit code
│
├── Technical_Document/
│   └── NCS Technical Document
│
├── Requirement_Document/
│   └── NCS Requirement Document
│
├── Circuit_Diagram/
│   └── NCS Circuit Diagram
│
└── README.md
```

---

# Documentation

### Technical Document

Contains detailed information about:

* System architecture
* Hardware components
* Circuit design
* Communication
* Software architecture
* Button functions
* Display operation
* LED and buzzer operation
* Timing and response-time logging
* Admin portal
* System workflow

### Requirement Document

Contains:

* Functional requirements
* Hardware requirements
* Software requirements
* User requirements
* System constraints
* Performance requirements
* Safety/reliability considerations

### Circuit Diagram

The circuit diagram illustrates the electrical connections between the controller, buttons, LEDs, buzzer, display, and other system components.

---

# Repository Purpose

This repository contains the source code, circuit design, technical documentation, requirement documentation, and supporting files required for the development and testing of the Nurse Call System.

The project is maintained as a prototype with the objective of developing a reliable and scalable digital nurse call solution.

---

## Project Status

**Prototype / Development Stage**

The system is currently under development and testing. Future development may include improved hardware integration, enhanced communication reliability, database integration, advanced analytics, and deployment on a dedicated PCB.

---

## Security Note

Sensitive information such as administrator passwords, API keys, Wi-Fi credentials, tokens, and other authentication information **must not be stored in this repository**.

Use environment variables, secure configuration files, or another appropriate credential-management method for deployment.

---

## Authors

Developed as part of an engineering/internship project.

