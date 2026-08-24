import socket
import json
import threading
import os
import time
from datetime import datetime

from flask import Flask, render_template_string, request, redirect, send_file
from openpyxl import Workbook


# =====================================================
# CONFIGURATION
# =====================================================

HOST = "0.0.0.0"

TCP_PORT = 5000
WEB_PORT = 5001

HEALTHCARE_CENTRE_NAME = "[Healthcare Centre Name]"

HEARTBEAT_TIMEOUT = 15


# =====================================================
# FILE LOCATIONS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEVICE_FILE = os.path.join(BASE_DIR, "devices.json")
LOG_FILE = os.path.join(BASE_DIR, "events.json")
EXCEL_FILE = os.path.join(BASE_DIR, "events.xlsx")


# =====================================================
# FLASK
# =====================================================

app = Flask(__name__)


# =====================================================
# DEVICE STORAGE
# =====================================================

devices = {}
devices_lock = threading.Lock()


# =====================================================
# EVENT STORAGE
# =====================================================

events = []
events_lock = threading.Lock()

next_event_id = 1


# =====================================================
# TIME
# =====================================================

def current_datetime():
    return datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")


# =====================================================
# DEVICE STORAGE
# =====================================================

def load_devices():

    global devices

    if os.path.exists(DEVICE_FILE):

        try:

            with open(DEVICE_FILE, "r") as f:
                devices = json.load(f)

            print("Loaded registered devices.")
            print("Registered devices:", len(devices))

        except Exception as e:

            print("Could not load devices:", e)
            devices = {}

    else:

        devices = {}
        print("No devices.json found.")


def save_devices():

    with open(DEVICE_FILE, "w") as f:
        json.dump(devices, f, indent=4)


# =====================================================
# EVENT STORAGE
# =====================================================

def load_events():

    global events
    global next_event_id

    if os.path.exists(LOG_FILE):

        try:

            with open(LOG_FILE, "r") as f:
                events = json.load(f)

            if events:

                next_event_id = max(
                    int(event["id"])
                    for event in events
                ) + 1

            else:

                next_event_id = 1

            print("Loaded events:", len(events))

        except Exception as e:

            print("Could not load events:", e)

            events = []
            next_event_id = 1

    else:

        events = []
        next_event_id = 1

        print("No events.json found yet.")


def save_events():

    with open(LOG_FILE, "w") as f:
        json.dump(events, f, indent=4)


# =====================================================
# EXCEL
# =====================================================

def save_events_excel():

    wb = Workbook()

    ws = wb.active
    ws.title = "Hospital Event Logs"

    ws.append([
        "ID",
        "Time",
        "Ward",
        "Bed",
        "MAC Address",
        "Event",
        "Status"
    ])

    for event in events:

        ws.append([
            event["id"],
            event["time"],
            event["ward"],
            event["bed"],
            event["mac"],
            event["event"],
            event["status"]
        ])

    widths = {
        "A": 8,
        "B": 25,
        "C": 10,
        "D": 10,
        "E": 25,
        "F": 25,
        "G": 20
    }

    for column, width in widths.items():
        ws.column_dimensions[column].width = width

    wb.save(EXCEL_FILE)


# =====================================================
# EVENT LOGGING
# =====================================================

def add_event(
    ward,
    bed,
    mac,
    event_name,
    status
):

    global next_event_id

    with events_lock:

        event = {

            "id": next_event_id,

            "time": current_datetime(),

            "ward": ward,

            "bed": bed,

            "mac": mac,

            "event": event_name,

            "status": status

        }

        events.append(event)

        next_event_id += 1

        save_events()
        save_events_excel()

    print()
    print("========================================")
    print("EVENT LOGGED")
    print("========================================")
    print("ID     :", event["id"])
    print("Time   :", event["time"])
    print("Ward   :", ward)
    print("Bed    :", bed)
    print("MAC    :", mac)
    print("Event  :", event_name)
    print("Status :", status)
    print("========================================")


# =====================================================
# BASE PAGE
# =====================================================

BASE_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>{{ title }}</title>

<style>

/* =====================================================
   GENERAL
   ===================================================== */

* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    min-height: 100%;
}

body {

    background: #eef2f7;

    font-family:
        Arial,
        Helvetica,
        sans-serif;
}


/* =====================================================
   HEADER
   ===================================================== */

.header {

    background: #0B5ED7;

    color: white;

    height: 76px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding: 0 35px;
}


.header-left {

    display: flex;

    align-items: center;

    gap: 15px;
}


.logo {

    width: 120px;

    height: 42px;

    background: white;

    border-radius: 4px;

    display: flex;

    align-items: center;

    justify-content: center;

    overflow: hidden;
}


.logo img {

    width: 110px;

    height: 38px;

    object-fit: contain;
}


.system-name {

    font-size: 27px;

    font-weight: bold;

    white-space: nowrap;
}


.centre-name {

    font-size: 18px;

    font-weight: bold;

    white-space: nowrap;
}


/* =====================================================
   NAVIGATION TABS
   ===================================================== */

.nav {

    background: white;

    height: 55px;

    padding: 0 35px;

    display: flex;

    align-items: center;

    gap: 35px;

    border-bottom: 1px solid #ddd;
}


.nav a {

    text-decoration: none;

    color: #555;

    font-size: 16px;

    font-weight: bold;

    height: 55px;

    display: flex;

    align-items: center;

    border-bottom: 3px solid transparent;
}


.nav a:hover {

    color: #0B5ED7;
}


.nav a.active {

    color: #0B5ED7;

    border-bottom: 3px solid #0B5ED7;
}


/* =====================================================
   PAGE
   ===================================================== */

.page {

    width: 100%;

    min-height: calc(100vh - 176px);

    padding: 25px 35px 60px 35px;
}


/* =====================================================
   DASHBOARD
   ===================================================== */

.dashboard-container {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(300px, 1fr)
        );

    gap: 18px;

    align-items: start;
}


/* =====================================================
   WARD CARDS
   ===================================================== */

.card {

    width: 100%;

    min-height: 215px;

    max-width: 350px;

    border-radius: 11px;

    padding: 18px;

    color: white;

    box-shadow:
        0 3px 10px rgba(0,0,0,.18);
}


.card.call {
    background: #0d6efd;
}


.card.ack {
    background: #198754;
}


.card.done {
    background: #dc3545;
}


.card.idle {
    background: #6c757d;
}


.title {

    font-size: 23px;

    font-weight: bold;
}


.status {

    font-size: 17px;

    font-weight: bold;

    margin: 11px 0;
}


.info {

    font-size: 15px;

    line-height: 1.65;
}


.online {

    color: #d1ffd1;

    font-weight: bold;
}


.offline {

    color: #ffd1d1;

    font-weight: bold;
}


/* =====================================================
   EMPTY DASHBOARD
   ===================================================== */

.empty-state {

    width: 100%;

    text-align: center;

    margin-top: 70px;

    font-size: 32px;

    color: #666;
}


.empty-state small {

    display: block;

    margin-top: 12px;

    font-size: 18px;
}


/* =====================================================
   BOX
   ===================================================== */

.box {

    width: 100%;

    background: white;

    padding: 25px;

    border-radius: 12px;

    box-shadow:
        0 2px 10px rgba(0,0,0,.15);

    margin-bottom: 20px;
}


.box h2 {

    margin-top: 0;

    color: #222;
}


/* =====================================================
   INPUT
   ===================================================== */

input {

    width: 100%;

    padding: 11px;

    margin: 7px 0 16px;

    border: 1px solid #ccc;

    border-radius: 6px;

    font-size: 15px;
}


button {

    background: #0B5ED7;

    color: white;

    border: none;

    padding: 11px 22px;

    border-radius: 6px;

    font-size: 15px;

    cursor: pointer;
}


button:hover {

    opacity: .9;
}


.delete {

    background: #dc3545;

    padding: 7px 13px;
}


.delete-all {

    background: #dc3545;

    margin-top: 18px;
}


/* =====================================================
   TABLE
   ===================================================== */

table {

    width: 100%;

    border-collapse: collapse;

    background: white;
}


th {

    background: #0B5ED7;

    color: white;

    padding: 11px;

    text-align: center;
}


td {

    border: 1px solid #ddd;

    padding: 10px;

    text-align: center;
}


tr:nth-child(even) {

    background: #f7f7f7;
}


/* =====================================================
   LOG TOPBAR
   ===================================================== */

.log-topbar {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 18px;
}


.total {

    font-size: 17px;

    font-weight: bold;
}


.download {

    background: #198754;

    color: white;

    padding: 9px 16px;

    text-decoration: none;

    border-radius: 6px;

    margin-right: 8px;

    font-weight: bold;
}


.clear {

    background: #dc3545;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {

    width: 100%;

    height: 45px;

    background: #0B5ED7;

    display: flex;

    justify-content: center;

    align-items: center;

    color: white;

    font-size: 14px;
}

</style>

</head>


<body>


<!-- =================================================
     HEADER
     ================================================= -->

<div class="header">

    <div class="header-left">

        <div class="logo">

            <img
                src="/static/gtm_logo.jpg"
                alt="GTM4Health"
            >

        </div>


        <div class="system-name">

            NURSE CALL SYSTEM

        </div>

    </div>


    <div class="centre-name">

        {{ healthcare_centre }}

    </div>

</div>


<!-- =================================================
     NAVIGATION
     ================================================= -->

<div class="nav">

    <a
        href="/"
        class="{% if active == 'dashboard' %}active{% endif %}"
    >

        Dashboard

    </a>


    <a
        href="/config"
        class="{% if active == 'config' %}active{% endif %}"
    >

        ESP32 Configuration

    </a>


    <a
        href="/admin"
        class="{% if active == 'logs' %}active{% endif %}"
    >

        Event Logs

    </a>

</div>


<!-- =================================================
     PAGE CONTENT
     ================================================= -->

<div class="page">

{{ content | safe }}

</div>


<!-- =================================================
     FOOTER
     ================================================= -->

<div class="footer">

    © GTM4Health 2026

</div>


</body>

</html>

"""


# =====================================================
# DASHBOARD
# =====================================================

DASHBOARD_CONTENT = """

<div
    id="dashboard-container"
    class="dashboard-container"
>


{% if devices %}


{% for mac, device in devices.items() %}


    {% if device.status == "CALL" %}

        <div class="card call">

    {% elif device.status == "ACK" %}

        <div class="card ack">

    {% elif device.status == "DONE" %}

        <div class="card done">

    {% else %}

        <div class="card idle">

    {% endif %}


        <div class="title">

            WARD {{ device.ward }}

        </div>


        <div class="status">


            {% if device.status == "CALL" %}

                PATIENT ASSISTANCE REQUESTED


            {% elif device.status == "ACK" %}

                NURSE RESPONDING


            {% elif device.status == "DONE" %}

                REQUEST RESOLVED


            {% else %}

                SYSTEM IDLE

            {% endif %}


        </div>


        <div class="info">

            <b>Bed:</b>

            {{ "%02d"|format(device.bed|int) }}

            <br>


            <b>Patient Call:</b>

            {{ device.call }}

            <br>


            <b>Nurse ACK:</b>

            {{ device.ack }}

            <br>


            <b>ESP32:</b>


            {% if device.online %}

                <span class="online">

                    ● ONLINE

                </span>

            {% else %}

                <span class="offline">

                    ● OFFLINE

                </span>

            {% endif %}


            <br>


            <b>MAC:</b>

            {{ mac }}

        </div>


    </div>


{% endfor %}


{% else %}


    <div class="empty-state">

        SYSTEM IDLE

        <small>

            No registered patient requests.

        </small>

    </div>


{% endif %}


</div>


<script>

/*
    LIVE DASHBOARD UPDATE

    Only the cards are replaced.
    Header, tabs and footer remain untouched.
*/

async function updateDashboard() {

    try {

        const response =
            await fetch(
                "/api/dashboard"
            );


        if (!response.ok) {
            return;
        }


        const html =
            await response.text();


        const temporary =
            document.createElement(
                "div"
            );


        temporary.innerHTML = html;


        const newContainer =
            temporary.querySelector(
                "#dashboard-container"
            );


        const currentContainer =
            document.getElementById(
                "dashboard-container"
            );


        if (
            newContainer &&
            currentContainer
        ) {

            currentContainer.replaceWith(
                newContainer
            );

        }

    }

    catch (error) {

        console.log(
            "Dashboard update failed:",
            error
        );

    }

}


/*
    Update every second.
*/

setInterval(
    updateDashboard,
    1000
);

</script>

"""


# =====================================================
# CONFIGURATION PAGE
# =====================================================

CONFIG_CONTENT = """

<div class="box">

<h2>Register ESP32</h2>


<form
    method="POST"
    action="/config"
>


<label>

ESP32 MAC Address

</label>


<input
    type="text"
    name="mac"
    placeholder="AA:BB:CC:DD:EE:FF"
    required
>


<label>

Ward Number

</label>


<input
    type="number"
    name="ward"
    placeholder="101"
    required
>


<label>

Bed Number

</label>


<input
    type="number"
    name="bed"
    placeholder="2"
    required
>


<button type="submit">

REGISTER ESP32

</button>


</form>

</div>


<div class="box">

<h2>

Registered ESP32 Devices

</h2>


{% if devices %}


<table>


<tr>

<th>MAC Address</th>

<th>Ward</th>

<th>Bed</th>

<th>Status</th>

<th>Action</th>

</tr>


{% for mac, device in devices.items() %}


<tr>

<td>

{{ mac }}

</td>


<td>

{{ device.ward }}

</td>


<td>

{{ device.bed }}

</td>


<td>


{% if device.online %}

<span class="online">

ONLINE

</span>

{% else %}

<span class="offline">

OFFLINE

</span>

{% endif %}


</td>


<td>


<form
    method="POST"
    action="/config/delete"
    style="margin:0;"
>


<input
    type="hidden"
    name="mac"
    value="{{ mac }}"
>


<button
    type="submit"
    class="delete"
>

DELETE

</button>


</form>


</td>


</tr>


{% endfor %}


</table>


<form
    method="POST"
    action="/config/delete-all"
>


<button
    type="submit"
    class="delete-all"
>

DELETE ALL DEVICES

</button>


</form>


{% else %}


<p>

No ESP32 devices registered.

</p>


{% endif %}


</div>

"""


# =====================================================
# LOG PAGE
# =====================================================

LOG_CONTENT = """

<div class="log-topbar">


<div class="total">

Total Events : {{ events|length }}

</div>


<div>


<a
    href="/admin/download"
    class="download"
>

DOWNLOAD EXCEL

</a>


<form
    method="POST"
    action="/admin/clear"
    style="display:inline;"
    onsubmit="return confirm('Delete ALL hospital event logs?');"
>


<button
    type="submit"
    class="clear"
>

CLEAR ALL LOGS

</button>


</form>


</div>


</div>


<div
    class="box"
    style="padding:0; overflow:hidden;"
>


<table>


<tr>

<th>ID</th>

<th>Time</th>

<th>Ward</th>

<th>Bed</th>

<th>MAC Address</th>

<th>Event</th>

<th>Status</th>

</tr>


{% for event in events|reverse %}


<tr>

<td>

{{ event.id }}

</td>


<td>

{{ event.time }}

</td>


<td>

{{ event.ward }}

</td>


<td>

{{ event.bed }}

</td>


<td>

{{ event.mac }}

</td>


<td>

{{ event.event }}

</td>


<td>

{{ event.status }}

</td>


</tr>


{% endfor %}


</table>


</div>

"""


# =====================================================
# PAGE RENDERING
# =====================================================

def render_page(
    title,
    active,
    content,
    **kwargs
):

    rendered_content = render_template_string(
        content,
        **kwargs
    )


    return render_template_string(

        BASE_HTML,

        title=title,

        active=active,

        healthcare_centre=HEALTHCARE_CENTRE_NAME,

        content=rendered_content

    )


# =====================================================
# DASHBOARD ROUTE
# =====================================================

@app.route("/")
def dashboard():

    with devices_lock:

        current_devices = {

            mac: dict(device)

            for mac, device in devices.items()

        }


    return render_page(

        "Nurse Call System",

        "dashboard",

        DASHBOARD_CONTENT,

        devices=current_devices

    )


# =====================================================
# LIVE DASHBOARD API
# =====================================================

@app.route("/api/dashboard")
def dashboard_api():

    with devices_lock:

        current_devices = {

            mac: dict(device)

            for mac, device in devices.items()

        }


    return render_template_string(

        DASHBOARD_CONTENT,

        devices=current_devices

    )


# =====================================================
# CONFIGURATION
# =====================================================

@app.route(
    "/config",
    methods=["GET", "POST"]
)

def config():

    if request.method == "POST":

        mac = request.form.get(
            "mac",
            ""
        ).strip().upper()


        mac = mac.replace(
            "-",
            ":"
        )


        ward = request.form.get(
            "ward",
            ""
        ).strip()


        bed = request.form.get(
            "bed",
            ""
        ).strip()


        if not mac or not ward or not bed:

            return (
                "Missing configuration information."
            )


        try:

            ward = int(ward)
            bed = int(bed)

        except ValueError:

            return (
                "Ward and Bed must be numbers."
            )


        with devices_lock:

            if mac in devices:

                devices[mac]["ward"] = ward
                devices[mac]["bed"] = bed

            else:

                devices[mac] = {

                    "ward": ward,

                    "bed": bed,

                    "status": "IDLE",

                    "call": "--:--:--",

                    "ack": "--:--:--",

                    "online": False,

                    "last_seen": 0,

                    "last_event": "CONFIG"

                }


            save_devices()


        add_event(

            ward,
            bed,
            mac,
            "ESP32 Registered",
            "Configured"

        )


        return redirect(
            "/config"
        )


    with devices_lock:

        current_devices = {

            mac: dict(device)

            for mac, device in devices.items()

        }


    return render_page(

        "ESP32 Configuration",

        "config",

        CONFIG_CONTENT,

        devices=current_devices

    )


# =====================================================
# DELETE DEVICE
# =====================================================

@app.route(
    "/config/delete",
    methods=["POST"]
)

def delete_device():

    mac = request.form.get(
        "mac",
        ""
    ).strip().upper()


    device_to_log = None


    with devices_lock:

        if mac in devices:

            device_to_log = dict(
                devices[mac]
            )

            del devices[mac]

            save_devices()


    if device_to_log:

        add_event(

            device_to_log["ward"],
            device_to_log["bed"],
            mac,
            "ESP32 Deleted",
            "Removed"

        )


    return redirect(
        "/config"
    )


# =====================================================
# DELETE ALL DEVICES
# =====================================================

@app.route(
    "/config/delete-all",
    methods=["POST"]
)

def delete_all_devices():

    with devices_lock:

        old_devices = dict(
            devices
        )

        devices.clear()

        save_devices()


    for mac, device in old_devices.items():

        add_event(

            device["ward"],
            device["bed"],
            mac,
            "ESP32 Deleted",
            "Removed"

        )


    return redirect(
        "/config"
    )


# =====================================================
# EVENT LOGS
# =====================================================

@app.route("/admin")
def admin():

    with events_lock:

        current_events = list(
            events
        )


    return render_page(

        "Event Logs",

        "logs",

        LOG_CONTENT,

        events=current_events

    )


# =====================================================
# DOWNLOAD EXCEL
# =====================================================

@app.route("/admin/download")
def download_excel():

    with events_lock:

        save_events_excel()


    return send_file(

        EXCEL_FILE,

        as_attachment=True,

        download_name="Hospital_Event_Logs.xlsx"

    )


# =====================================================
# CLEAR LOGS
# =====================================================

@app.route(
    "/admin/clear",
    methods=["POST"]
)

def clear_logs():

    global events
    global next_event_id


    with events_lock:

        events = []

        next_event_id = 1

        save_events()

        save_events_excel()


    return redirect(
        "/admin"
    )


# =====================================================
# PACKET PROCESSING
# =====================================================

def handle_packet(
    packet,
    connection
):

    mac = packet.get(
        "mac"
    )


    if not mac:

        print(
            "Packet without MAC. Ignored."
        )

        return False


    mac = mac.upper()


    event = packet.get(
        "event",
        "UNKNOWN"
    )


    # =================================================
    # REGISTER
    # =================================================

    if event == "REGISTER":

        with devices_lock:

            if mac not in devices:

                print()
                print(
                    "========================================"
                )
                print(
                    "UNAUTHORIZED ESP32"
                )
                print(
                    "MAC:",
                    mac
                )
                print(
                    "Connection rejected."
                )
                print(
                    "NO LOG CREATED"
                )
                print(
                    "========================================"
                )


                try:

                    connection.sendall(
                        b'{"status":"REJECTED"}\n'
                    )

                except:

                    pass


                return False


            device = devices[mac]

            device["online"] = True

            device["last_seen"] = time.time()

            device["last_event"] = "REGISTER"

            ward = device["ward"]

            bed = device["bed"]


            save_devices()


        print()
        print(
            "========================================"
        )
        print(
            "AUTHORIZED ESP32"
        )
        print(
            "MAC  :",
            mac
        )
        print(
            "Ward :",
            ward
        )
        print(
            "Bed  :",
            bed
        )
        print(
            "========================================"
        )


        try:

            connection.sendall(
                b'{"status":"AUTHORIZED"}\n'
            )

        except:

            pass


        add_event(

            ward,
            bed,
            mac,
            "ESP32 Connected",
            "Online"

        )


        return True


    # =================================================
    # AUTHORIZATION
    # =================================================

    with devices_lock:

        if mac not in devices:

            print(
                "Ignored event from unregistered ESP32:",
                mac
            )

            print(
                "Event:",
                event
            )

            print(
                "NO LOG CREATED"
            )

            return False


        device = devices[mac]

        device["last_seen"] = time.time()

        device["online"] = True

        ward = device["ward"]

        bed = device["bed"]


        # =================================================
        # HEARTBEAT
        # =================================================

        if event == "HEARTBEAT":

            device["last_event"] = "HEARTBEAT"

            save_devices()

            return True


        # =================================================
        # CALL
        # =================================================

        if event == "CALL":

            device["status"] = "CALL"

            device["call"] = packet.get(
                "call",
                "--:--:--"
            )

            device["ack"] = "--:--:--"

            event_name = "Patient Call"

            event_status = "Pending"


        # =================================================
        # ACK
        # =================================================

        elif event == "ACK":

            device["status"] = "ACK"

            device["call"] = packet.get(
                "call",
                device["call"]
            )

            device["ack"] = packet.get(
                "ack",
                "--:--:--"
            )

            event_name = "Nurse ACK"

            event_status = "Acknowledged"


        # =================================================
        # DONE
        # =================================================

        elif event == "DONE":

            device["status"] = "DONE"

            event_name = "Request Resolved"

            event_status = "Completed"


        # =================================================
        # IDLE
        # =================================================

        elif event == "IDLE":

            device["status"] = "IDLE"

            device["call"] = "--:--:--"

            device["ack"] = "--:--:--"

            event_name = "System Idle"

            event_status = "Idle"


        else:

            device["last_event"] = event

            save_devices()

            return True


        device["last_event"] = event

        save_devices()


    add_event(

        ward,
        bed,
        mac,
        event_name,
        event_status

    )


    return True


# =====================================================
# ESP32 CLIENT
# =====================================================

def handle_client(
    conn,
    address
):

    print()
    print(
        "----------------------------------------"
    )

    print(
        "ESP32 TCP CONNECTION"
    )

    print(
        "IP   :",
        address[0]
    )

    print(
        "PORT :",
        address[1]
    )

    print(
        "----------------------------------------"
    )


    buffer = ""

    authorized = False

    device_mac = None


    try:

        while True:

            data = conn.recv(1024)


            if not data:

                break


            buffer += data.decode(
                "utf-8",
                errors="ignore"
            )


            while "\n" in buffer:

                message, buffer = buffer.split(
                    "\n",
                    1
                )


                message = message.strip()


                if not message:

                    continue


                try:

                    packet = json.loads(
                        message
                    )


                    if not authorized:

                        if packet.get(
                            "event"
                        ) != "REGISTER":

                            print(
                                "ESP32 did not send REGISTER."
                            )

                            print(
                                "NO LOG CREATED."
                            )

                            return


                        device_mac = packet.get(
                            "mac"
                        )


                        authorized = handle_packet(

                            packet,

                            conn

                        )


                        if not authorized:

                            return


                    else:

                        handle_packet(

                            packet,

                            conn

                        )


                except json.JSONDecodeError:

                    print(
                        "Invalid JSON received:"
                    )

                    print(
                        message
                    )


    except ConnectionResetError:

        print(
            "ESP32 connection reset."
        )


    except Exception as e:

        print(
            "Connection error:",
            e
        )


    finally:

        conn.close()


        if authorized and device_mac:

            mac = device_mac.upper()

            should_log = False

            ward = None

            bed = None


            with devices_lock:

                if mac in devices:

                    if devices[mac].get(
                        "online",
                        False
                    ):

                        devices[mac]["online"] = False

                        ward = devices[mac]["ward"]

                        bed = devices[mac]["bed"]

                        should_log = True

                        save_devices()


            if should_log:

                add_event(

                    ward,
                    bed,
                    mac,
                    "ESP32 Disconnected",
                    "Offline"

                )


        print(
            "ESP32 connection closed:",
            address[0]
        )


# =====================================================
# HEARTBEAT MONITOR
# =====================================================

def check_device_status():

    while True:

        time.sleep(5)

        now = time.time()

        devices_to_mark_offline = []


        with devices_lock:

            for mac, device in devices.items():

                if not device.get(
                    "online",
                    False
                ):

                    continue


                last_seen = device.get(
                    "last_seen",
                    0
                )


                if last_seen == 0:

                    continue


                if (
                    now - last_seen
                    > HEARTBEAT_TIMEOUT
                ):

                    device["online"] = False

                    devices_to_mark_offline.append(

                        (
                            mac,
                            device["ward"],
                            device["bed"]
                        )

                    )


            if devices_to_mark_offline:

                save_devices()


        for mac, ward, bed in devices_to_mark_offline:

            print()

            print(
                "ESP32 OFFLINE:",
                mac
            )


            add_event(

                ward,
                bed,
                mac,
                "ESP32 Disconnected",
                "Offline"

            )


# =====================================================
# TCP SERVER
# =====================================================

def tcp_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )


    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )


    server.bind(
        (
            HOST,
            TCP_PORT
        )
    )


    server.listen(20)


    print()
    print(
        "========================================"
    )

    print(
        " NURSE CALL SYSTEM TCP SERVER"
    )

    print(
        "========================================"
    )

    print(
        "TCP Port:",
        TCP_PORT
    )

    print(
        "Dashboard:",
        f"http://localhost:{WEB_PORT}"
    )

    print(
        "Config:",
        f"http://localhost:{WEB_PORT}/config"
    )

    print(
        "Event Logs:",
        f"http://localhost:{WEB_PORT}/admin"
    )

    print()

    print(
        "Waiting for ESP32 devices..."
    )


    while True:

        conn, address = server.accept()


        thread = threading.Thread(

            target=handle_client,

            args=(
                conn,
                address
            ),

            daemon=True

        )


        thread.start()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print()

    print(
        "Starting Nurse Call System..."
    )

    print(
        "Python file:",
        os.path.abspath(__file__)
    )

    print(
        "Data folder:",
        BASE_DIR
    )


    load_devices()

    load_events()


    if not os.path.exists(
        EXCEL_FILE
    ):

        with events_lock:

            save_events_excel()

        print(
            "Created events.xlsx"
        )


    heartbeat_thread = threading.Thread(

        target=check_device_status,

        daemon=True

    )

    heartbeat_thread.start()


    tcp_thread = threading.Thread(

        target=tcp_server,

        daemon=True

    )

    tcp_thread.start()


    app.run(

        host="0.0.0.0",

        port=WEB_PORT,

        debug=False,

        use_reloader=False

    )
