import socket
import json
import threading
import os
from datetime import datetime

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    send_file
)

from openpyxl import Workbook

# =====================================================
# CONFIGURATION
# =====================================================

HOST = "0.0.0.0"

TCP_PORT = 5000
WEB_PORT = 5001

# =====================================================
# FILE LOCATIONS
# Everything is stored beside tcp.py
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DEVICE_FILE = os.path.join(
    BASE_DIR,
    "devices.json"
)

LOG_FILE = os.path.join(
    BASE_DIR,
    "events.json"
)

EXCEL_FILE = os.path.join(
    BASE_DIR,
    "events.xlsx"
)


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

    return datetime.now().strftime(
        "%d-%b-%Y %I:%M:%S %p"
    )


# =====================================================
# LOAD DEVICES
# =====================================================

def load_devices():
    global devices
    if os.path.exists(DEVICE_FILE):
        try:
            with open(
                DEVICE_FILE,
                "r"
            ) as f:
                devices = json.load(f)
            print(
                "Loaded registered devices."
            )
            print(
                "Registered devices:",
                len(devices)
            )
        except Exception as e:
            print(
                "Could not load devices:",
                e
            )
            devices = {}
    else:
        devices = {}

        print(
            "No devices.json found."
        )

# =====================================================
# SAVE DEVICES
# =====================================================

def save_devices():

    with open(
        DEVICE_FILE,
        "w"
    ) as f:

        json.dump(
            devices,
            f,
            indent=4
        )

# =====================================================
# LOAD EVENTS
# =====================================================

def load_events():

    global events
    global next_event_id
    if os.path.exists(LOG_FILE):
        try:
            with open(
                LOG_FILE,
                "r"
            ) as f:
                events = json.load(f)
            if events:
                next_event_id = max(
                    int(event["id"])
                    for event in events
                ) + 1
            else:
                next_event_id = 1
            print(
                "Loaded events:",
                len(events)
            )
        except Exception as e:
            print(
                "Could not load events:",
                e
            )
            events = []
            next_event_id = 1
    else:
        events = []
        next_event_id = 1
        print(
            "No events.json found yet."
        )

# =====================================================
# SAVE EVENTS JSON
# =====================================================

def save_events():
    with open(
        LOG_FILE,
        "w"
    ) as f:
        json.dump(
            events,
            f,
            indent=4
        )


# =====================================================
# SAVE EVENTS TO EXCEL
# =====================================================

def save_events_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Hospital Event Logs"

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------

    ws.append([
        "ID",
        "Time",
        "Ward",
        "Bed",
        "MAC Address",
        "Event",
        "Status"
    ])

    # -------------------------------------------------
    # DATA
    # -------------------------------------------------

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

    # -------------------------------------------------
    # COLUMN WIDTHS
    # -------------------------------------------------

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
        ws.column_dimensions[
            column
        ].width = width

    # -------------------------------------------------
    # SAVE
    # -------------------------------------------------

    wb.save(
        EXCEL_FILE
    )


# =====================================================
# ADD EVENT
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


        events.append(
            event
        )

        next_event_id += 1

        # Save JSON
        save_events()

        # Save Excel
        save_events_excel()

    print()
    print(
        "========================================"
    )
    print(
        "EVENT LOGGED"
    )
    print(
        "========================================"
    )
    print(
        "ID     :",
        event["id"]
    )
    print(
        "Time   :",
        event["time"]
    )
    print(
        "Ward   :",
        ward
    )
    print(
        "Bed    :",
        bed
    )
    print(
        "MAC    :",
        mac
    )
    print(
        "Event  :",
        event_name
    )
    print(
        "Status :",
        status
    )
    print(
        "========================================"
    )

# =====================================================
# DASHBOARD HTML
# =====================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>N-Bed Nurse Calling System</title>
<meta http-equiv="refresh" content="2">
<style>
body {
    margin: 0;
    background: #eef2f7;
    font-family: Arial;
}
.header {
    background: #0B5ED7;
    color: white;
    text-align: center;
    padding: 20px;
    font-size: 30px;
    font-weight: bold;
}

.nav {
    background: white;
    padding: 15px 30px;

    box-shadow: 0 2px 5px rgba(0,0,0,.1);

}


.nav a {

    text-decoration: none;

    color: #0B5ED7;

    font-weight: bold;

    margin-right: 20px;

}


.container {

    padding: 30px;

    display: flex;

    flex-wrap: wrap;

    gap: 20px;

}


.card {

    width: 330px;

    min-height: 270px;

    border-radius: 12px;

    padding: 22px;

    color: white;

    box-sizing: border-box;

    box-shadow: 0 3px 10px rgba(0,0,0,.2);

}


.idle {

    background: #6c757d;

}


.call {

    background: #0d6efd;

}


.ack {

    background: #198754;

}


.done {

    background: #dc3545;

}


.title {

    font-size: 27px;

    font-weight: bold;

}


.status {

    font-size: 21px;

    font-weight: bold;

    margin: 18px 0;

}


.info {

    font-size: 17px;

    line-height: 1.8;

}


.idle-message {

    width: 100%;

    text-align: center;

    margin-top: 100px;

    color: #666;

}


.online {

    font-weight: bold;

}


.offline {

    font-weight: bold;

}

</style>

</head>


<body>


<div class="header">

HOSPITAL NURSE CALLING SYSTEM

</div>


<div class="nav">

<a href="/">

Dashboard

</a>


<a href="/config">

ESP32 Configuration

</a>


<a href="/admin">

Hospital Event Logs

</a>

</div>


<div class="container">


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


<b>MAC:</b>

{{ mac }}

<br>


<b>ESP32:</b>


{% if device.online %}

<span class="online">
ONLINE
</span>

{% else %}

<span class="offline">
OFFLINE
</span>

{% endif %}


</div>


</div>


{% endfor %}


{% else %}


<div class="idle-message">

<h2>SYSTEM IDLE</h2>

<p>
No registered ESP32 devices.
</p>

<p>
Go to ESP32 Configuration to register a device.
</p>

</div>


{% endif %}


</div>


</body>

</html>

"""


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def dashboard():

    with devices_lock:

        current_devices = dict(
            devices
        )


    return render_template_string(

        DASHBOARD_HTML,

        devices=current_devices

    )


# =====================================================
# CONFIG PAGE HTML
# =====================================================

CONFIG_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>ESP32 Configuration</title>


<style>

body {

    margin: 0;

    background: #eef2f7;

    font-family: Arial;

}


.header {

    background: #0B5ED7;

    color: white;

    text-align: center;

    padding: 20px;

    font-size: 28px;

    font-weight: bold;

}


.nav {

    background: white;

    padding: 15px 30px;

}


.nav a {

    color: #0B5ED7;

    text-decoration: none;

    font-weight: bold;

    margin-right: 20px;

}


.container {

    padding: 30px;

    max-width: 1100px;

    margin: auto;

}


.box {

    background: white;

    padding: 25px;

    border-radius: 12px;

    box-shadow: 0 2px 10px rgba(0,0,0,.15);

    margin-bottom: 30px;

}


input {

    width: 100%;

    box-sizing: border-box;

    padding: 12px;

    margin: 8px 0 18px;

    border: 1px solid #ccc;

    border-radius: 6px;

    font-size: 16px;

}


button {

    background: #0B5ED7;

    color: white;

    border: none;

    padding: 12px 25px;

    border-radius: 6px;

    font-size: 16px;

    cursor: pointer;

}


.delete {

    background: #dc3545;

    padding: 8px 14px;

}


.deleteAll {

    background: #dc3545;

    margin-top: 20px;

}


table {

    width: 100%;

    border-collapse: collapse;

    background: white;

}


th, td {

    padding: 12px;

    border: 1px solid #ddd;

    text-align: center;

}


th {

    background: #0B5ED7;

    color: white;

}

</style>

</head>


<body>


<div class="header">

ESP32 CONFIGURATION

</div>


<div class="nav">

<a href="/">

Dashboard

</a>


<a href="/config">

Configuration

</a>


<a href="/admin">

Hospital Event Logs

</a>

</div>


<div class="container">


<div class="box">


<h2>

Register ESP32

</h2>


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

placeholder="20:E7:C8:69:08:E0"

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

ONLINE

{% else %}

OFFLINE

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

class="deleteAll"

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


</div>


</body>

</html>

"""


# =====================================================
# CONFIG
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


        mac = mac.replace(
            "-",
            ":"
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


                devices[mac][
                    "ward"
                ] = ward


                devices[mac][
                    "bed"
                ] = bed


            else:


                devices[mac] = {

                    "ward": ward,

                    "bed": bed,

                    "status": "IDLE",

                    "call": "--:--:--",

                    "ack": "--:--:--",

                    "online": False,

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

        current_devices = dict(
            devices
        )


    return render_template_string(

        CONFIG_HTML,

        devices=current_devices

    )


# =====================================================
# DELETE ONE DEVICE
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


    with devices_lock:


        if mac in devices:


            ward = devices[mac][
                "ward"
            ]


            bed = devices[mac][
                "bed"
            ]


            del devices[mac]


            save_devices()


            add_event(

                ward,

                bed,

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
# ADMIN / LOGS HTML
# =====================================================

LOGS_HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Hospital Event Logs</title>


<style>

body {

    margin: 0;

    background: #eef2f7;

    font-family: Arial;

}


.header {

    background: #0B5ED7;

    color: white;

    text-align: center;

    padding: 18px;

    font-size: 30px;

    font-weight: bold;

}


.nav {

    background: white;

    padding: 15px 30px;

}


.nav a {

    color: #0B5ED7;

    text-decoration: none;

    font-weight: bold;

    margin-right: 20px;

}


.container {

    padding: 20px;

}


.topbar {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 20px;

}


.total {

    font-size: 18px;

    font-weight: bold;

}


.download {

    background: #198754;

    color: white;

    padding: 10px 18px;

    text-decoration: none;

    border-radius: 6px;

    margin-right: 10px;

    font-weight: bold;

}


.clear {

    background: #dc3545;

    color: white;

    padding: 10px 18px;

    border: none;

    border-radius: 6px;

    font-weight: bold;

    cursor: pointer;

}


table {

    width: 100%;

    border-collapse: collapse;

    background: white;

}


th {

    background: #0B5ED7;

    color: white;

    padding: 12px;

    text-align: center;

}


td {

    border: 1px solid #ddd;

    padding: 11px;

    text-align: center;

}


tr:nth-child(even) {

    background: #f7f7f7;

}


</style>

</head>


<body>


<div class="header">

HOSPITAL EVENT LOGS

</div>


<div class="nav">

<a href="/">

Dashboard

</a>


<a href="/config">

ESP32 Configuration

</a>


<a href="/admin">

Hospital Event Logs

</a>

</div>


<div class="container">


<div class="topbar">


<div class="total">

Total Events :

{{ events|length }}

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


</body>

</html>

"""


# =====================================================
# ADMIN
# =====================================================

@app.route("/admin")
def admin():


    with events_lock:

        current_events = list(
            events
        )


    return render_template_string(

        LOGS_HTML,

        events=current_events

    )


# =====================================================
# DOWNLOAD EXCEL
# =====================================================

@app.route("/admin/download")
def download_excel():


    # Make sure latest data is in Excel.

    with events_lock:

        save_events_excel()


    return send_file(

        EXCEL_FILE,

        as_attachment=True,

        download_name="Hospital_Event_Logs.xlsx"

    )


# =====================================================
# CLEAR ALL LOGS
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


        # Clear JSON

        save_events()


        # Create empty Excel

        save_events_excel()


    return redirect(
        "/admin"
    )


# =====================================================
# HANDLE ESP32 PACKET
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


            # -----------------------------------------
            # UNREGISTERED
            # -----------------------------------------

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


                # NO LOG

                return False


            # -----------------------------------------
            # REGISTERED
            # -----------------------------------------

            device = devices[mac]


            device[
                "online"
            ] = True


            device[
                "last_event"
            ] = "REGISTER"


            ward = device[
                "ward"
            ]


            bed = device[
                "bed"
            ]


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
    # OTHER EVENTS
    # =================================================

    with devices_lock:


        # ---------------------------------------------
        # UNREGISTERED
        # ---------------------------------------------

        if mac not in devices:


            print()

            print(
                "Ignored event from unregistered ESP32:"
            )

            print(
                "MAC:",
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


        # ---------------------------------------------
        # REGISTERED
        # ---------------------------------------------

        device = devices[mac]


        ward = device[
            "ward"
        ]


        bed = device[
            "bed"
        ]


        # =================================================
        # CALL
        # =================================================

        if event == "CALL":


            device[
                "status"
            ] = "CALL"


            device[
                "call"
            ] = packet.get(

                "call",

                "--:--:--"

            )


            device[
                "ack"
            ] = "--:--:--"


            event_name = (
                "Patient Call"
            )


            event_status = (
                "Pending"
            )


        # =================================================
        # ACK
        # =================================================

        elif event == "ACK":


            device[
                "status"
            ] = "ACK"


            device[
                "call"
            ] = packet.get(

                "call",

                device["call"]

            )


            device[
                "ack"
            ] = packet.get(

                "ack",

                "--:--:--"

            )


            event_name = (
                "Nurse ACK"
            )


            event_status = (
                "Acknowledged"
            )


        # =================================================
        # DONE
        # =================================================

        elif event == "DONE":


            device[
                "status"
            ] = "DONE"


            event_name = (
                "Request Resolved"
            )


            event_status = (
                "Completed"
            )


        # =================================================
        # IDLE
        # =================================================

        elif event == "IDLE":


            device[
                "status"
            ] = "IDLE"


            device[
                "call"
            ] = "--:--:--"


            device[
                "ack"
            ] = "--:--:--"


            event_name = (
                "System Idle"
            )


            event_status = (
                "Idle"
            )


        # =================================================
        # UNKNOWN
        # =================================================

        else:


            event_name = event

            event_status = "Received"


        device[
            "last_event"
        ] = event


        device[
            "online"
        ] = True


    # =================================================
    # LOG
    # =================================================

    add_event(

        ward,

        bed,

        mac,

        event_name,

        event_status

    )


    return True


# =====================================================
# ESP32 CLIENT HANDLER
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


    # FALSE until REGISTER is authorized.

    authorized = False


    device_mac = None


    try:


        while True:


            data = conn.recv(
                1024
            )


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


                    # =================================================
                    # FIRST MESSAGE MUST BE REGISTER
                    # =================================================

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


                    # =================================================
                    # AUTHORIZED
                    # =================================================

                    else:


                        if not handle_packet(

                            packet,

                            conn

                        ):


                            return


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


        # =================================================
        # DISCONNECT
        # ONLY REGISTERED DEVICES ARE LOGGED
        # =================================================

        if authorized and device_mac:


            mac = device_mac.upper()


            with devices_lock:


                if mac in devices:


                    devices[mac][
                        "online"
                    ] = False


                    ward = devices[mac][
                        "ward"
                    ]


                    bed = devices[mac][
                        "bed"
                    ]


                else:


                    ward = None

                    bed = None


            if (

                ward is not None

                and

                bed is not None

            ):


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


    server.listen(
        20
    )


    print()

    print(
        "========================================"
    )

    print(
        " N-BED NURSE CALL TCP SERVER"
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
        "Admin:",
        f"http://localhost:{WEB_PORT}/admin"
    )


    print()

    print(
        "Files:"
    )


    print(
        "Devices:",
        DEVICE_FILE
    )


    print(
        "Logs JSON:",
        LOG_FILE
    )


    print(
        "Logs Excel:",
        EXCEL_FILE
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
        "Starting N-Bed Nurse Call System..."
    )


    print(
        "Python file:",
        os.path.abspath(__file__)
    )


    print(
        "Data folder:",
        BASE_DIR
    )


    # ---------------------------------------------
    # LOAD DATA
    # ---------------------------------------------

    load_devices()

    load_events()


    # ---------------------------------------------
    # CREATE EXCEL IF IT DOESN'T EXIST
    # ---------------------------------------------

    if not os.path.exists(EXCEL_FILE):

        with events_lock:

            save_events_excel()

        print(
            "Created events.xlsx"
        )


    # ---------------------------------------------
    # START TCP SERVER
    # ---------------------------------------------

    tcp_thread = threading.Thread(

        target=tcp_server,

        daemon=True

    )


    tcp_thread.start()


    # ---------------------------------------------
    # START WEB SERVER
    # ---------------------------------------------

    app.run(

        host="0.0.0.0",

        port=WEB_PORT,

        debug=False,

        use_reloader=False

    )
