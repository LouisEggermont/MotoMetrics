import geohash2
from helpers.GPS import GPSModule
import subprocess
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import Adafruit_SSD1306
from helpers.MPU6050 import MPU6050
from helpers.LDR import BrightnessReader
from helpers.MAX6675 import MAX6675
from helpers.DS18B29 import DS18B29
import threading
import time
from datetime import datetime, timedelta
from repositories.DataRepository import DataRepository
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from RPi import GPIO
import math


GPIO.setmode(GPIO.BCM)

# Give power to components with transistor and wait to power up
powerpin = 18
GPIO.setup(powerpin, GPIO.OUT)
GPIO.output(powerpin, GPIO.HIGH)
time.sleep(10)

# Setup and import sensors and actuators
ambient_temp = DS18B29('/sys/bus/w1/devices/28-00d5b70000af/w1_slave')

engine_temp = MAX6675()

ldr = BrightnessReader(26)

buzz = 19
alarm_status = 0
led = 13
led_status = 2
led_auto_status = 0
auto_sensitivity = 2

MPU = MPU6050(0x68)

RST = None
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

gps = GPSModule()


def base36encode(number):
    if number < 0:
        sign = "-"
        number = -number
    else:
        sign = ""
    if 0 <= number < 36:
        return sign + "0123456789abcdefghijklmnopqrstuvwxyz"[number]
    else:
        return base36encode(number // 36) + "0123456789abcdefghijklmnopqrstuvwxyz"[number % 36]


def calculateDistance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Earth's radius in meters
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)

    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + math.cos(φ1) * \
        math.cos(φ2) * math.sin(Δλ / 2) * math.sin(Δλ / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


GPIO.setup(led, GPIO.OUT)
GPIO.output(led, GPIO.LOW)

GPIO.setup(buzz, GPIO.OUT)
GPIO.output(buzz, GPIO.LOW)

tracking = 0
rideid = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HELLOTHISISSCERET'

endpoint = '/api/v1'

# ping interval forces rapid B2F communication
socketio = SocketIO(app, cors_allowed_origins="*",
                    async_mode='gevent', ping_interval=0.5)
CORS(app)


def thread():
    # ride tracking
    global rideid, start_time
    time_send_to_dash = 0
    time_log_to_db = 0
    counter = 9

    # alarm tracking
    global alarm_status
    time_check_alarm = 0
    prev_tilt = round(MPU.get_tilt()[1])
    hysteresis = 20

    # LDR
    time_check_ldr = 0

    while True:
        # time.sleep(2)
        # print(gps.read_time())
        # print(gps.read_GPS())
        if tracking == 1:
            if time_send_to_dash + 0.5 < time.time():
                counter += 1
                current_time = gps.read_time()
                if current_time == "no time":
                    current_time_formatted = "00:00"
                    past_time = "00:00:00"
                else:
                    current_time_formatted = current_time[:5]  # Format as "HH:MM"
                    past_time = calculate_past_time(start_time, current_time)

                tilt = MPU.get_tilt_with_filter()[0]
                accel = MPU.get_acceleration()[2]
                engine_temp_value = engine_temp.read_temperature()
                ambient_temp_value = ambient_temp.read_temperature()
                socketio.emit('dash', {'time': current_time_formatted, 'time_ride': past_time, 'tilt': tilt,
                                       'accel': accel, 'engine_temp': engine_temp_value, 'ambient_temp': ambient_temp_value})
                if counter == 10:
                    location = gps.read_GPS()
                    DataRepository.create_log(6, rideid, engine_temp_value, 5)
                    DataRepository.create_log(7, rideid, ambient_temp_value, 6)
                    DataRepository.create_log(1, rideid, accel, 1)
                    DataRepository.create_log(2, rideid, tilt, 2)

                    if location != "No or weak signal":
                        encoded_geohash = geohash2.encode(location[0], location[1])
                        geohash_integer = int(encoded_geohash, 36)
                        DataRepository.create_log(4, rideid, geohash_integer, 4)
                        DataRepository.create_log(5, rideid, location[2], 5)
                    else:
                        DataRepository.create_log(4, rideid, 0, 4)
                        DataRepository.create_log(5, rideid, 0, 5)

                    counter = 0

                time_send_to_dash = time.time()

        if alarm_status == 1:
            if time_check_alarm + 1 < time.time():
                tilt = round(MPU.get_tilt()[1])
                if tilt > prev_tilt + hysteresis or tilt < prev_tilt - hysteresis:
                    alarm_triggered()
                prev_tilt = tilt
                time_check_alarm = time.time()

        if time_check_ldr + 5 < time.time():
            global led_status, led_auto_status, auto_sensitivity
            if led_status == 2:
                if ldr.read_brightness() > auto_sensitivity:
                    if led_auto_status != 1:
                        GPIO.output(led, GPIO.HIGH)
                        led_auto_status = 1
                        send_status()
                else:
                    if led_auto_status != 0:
                        GPIO.output(led, GPIO.LOW)
                        led_auto_status = 0
                        send_status()
            time_check_ldr = time.time()

def calculate_past_time(start_time, current_time):
    start_seconds = time_to_seconds(start_time)
    current_seconds = time_to_seconds(current_time)
    return seconds_to_time(current_seconds - start_seconds)

def time_to_seconds(time_str):
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def seconds_to_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def start_thread():
    t = threading.Thread(target=thread, daemon=True)
    t.start()
    print("Thread started")

def start_ride():
    global rideid, tracking, start_time
    rideid = DataRepository.create_ride()
    start_time = gps.read_time()
    tracking = 1
    socketio.emit('ride', 1)
    print(f"Ride {rideid} started")



def stop_ride():
    global rideid
    global tracking
    tracking = 0
    name = f"Ride{str(rideid).zfill(2)}"
    distance = get_distance_by_rideid(rideid)
    max_speed = DataRepository.get_speeds_by_rideid(rideid)['max(value)']
    avg_speed = DataRepository.get_speeds_by_rideid(rideid)['avg(value)']
    max_amb_temp = DataRepository.get_amb_temp_by_rideid(rideid)['max(value)']
    avg_amb_temp = DataRepository.get_amb_temp_by_rideid(rideid)['avg(value)']
    max_eng_temp = DataRepository.get_eng_temp_by_rideid(rideid)['max(value)']
    avg_eng_temp = DataRepository.get_eng_temp_by_rideid(rideid)['avg(value)']
    start_location = DataRepository.get_start_location_by_rideid(rideid)[
        'value']
    stop_location = DataRepository.get_stop_location_by_rideid(rideid)['value']
    max_tilt = DataRepository.get_tilt_by_rideid(rideid)['max(value)']
    min_tilt = DataRepository.get_tilt_by_rideid(rideid)['min(value)']
    max_accel = DataRepository.get_accel_by_rideid(rideid)['max(value)']
    min_accel = DataRepository.get_accel_by_rideid(rideid)['min(value)']
    DataRepository.update_ride(rideid, name, distance, max_speed, avg_speed, max_amb_temp, avg_amb_temp,
                               max_eng_temp, avg_eng_temp, start_location, stop_location, max_tilt, min_tilt, max_accel, min_accel)
    socketio.emit('ride', 0)
    print(f"Ride {rideid} stopped")


def start_alarm():
    global alarm_status
    alarm_status = 1
    socketio.emit('alarm', 1)
    print("Alarm on")


def stop_alarm():
    global alarm_status
    alarm_status = 0
    GPIO.output(buzz, GPIO.LOW)
    socketio.emit('alarm', 0)
    print("Alarm on")


def alarm_triggered():
    print("alarm triggered")
    GPIO.output(buzz, GPIO.HIGH)


def get_distance_by_rideid(rideid):
    latlngs = []
    totalDistance = 0
    data = DataRepository.get_locations_by_rideid(rideid)
    for i in data:
        decoded_geohash = base36encode(int(i['value']))
        decoded_latitude, decoded_longitude = geohash2.decode(decoded_geohash)
        latlngs.append([float(decoded_latitude), float(decoded_longitude)])
    # print(latlngs)
    for i in range(1, len(latlngs)):
        lat1 = latlngs[i - 1][0]
        lon1 = latlngs[i - 1][1]
        lat2 = latlngs[i][0]
        lon2 = latlngs[i][1]

        distance = calculateDistance(lat1, lon1, lat2, lon2)
        totalDistance += distance
    return totalDistance


def showIP():
    disp.begin()
    disp.clear()
    disp.display()

    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    padding = -2
    top = padding
    x = 0
    font = ImageFont.load_default()
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

# did not show ip when was run as service
    # cmd = "hostname -I"
    # IP = subprocess.check_output(cmd, shell=True)
    # ips = IP.decode('utf-8').split(" ")
    # draw.text((x, top), "IP: " + ips[0], font=font, fill=255)
    # draw.text((x, top+10), "IP: " + ips[1], font=font, fill=255)

    # ipwlancmd = "ip -o -4 addr show wlan0 | awk '{print $4}' | cut -d/ -f1"
    # iplancmd = "ip -o -4 addr show eth0 | awk '{print $4}' | cut -d/ -f1"

    # # show ip's when available and only then

    ipwlancmd = "ip addr show wlan0 | grep -Po 'inet \K[\d.]+'"
    try:
        ipwlan = subprocess.check_output(
            ipwlancmd, shell=True).decode().strip()
    except subprocess.CalledProcessError:
        ipwlan = "N/A"  # Set a fallback value when WLAN IP is not available

    iplancmd = "ip addr show eth0 | grep -Po 'inet \K[\d.]+'"
    try:
        iplan = subprocess.check_output(iplancmd, shell=True).decode().strip()
    except subprocess.CalledProcessError:
        iplan = "N/A"  # Set a fallback value when LAN IP is not available

    if iplan != "N/A":
        draw.text((x, top), "LAN: " + iplan, font=font, fill=255)

    if ipwlan != "N/A":
        draw.text((x, top+10), "WLAN: " + ipwlan, font=font, fill=255)

    disp.image(image)
    disp.display()


# API ENDPOINTS
@app.route('/')
def hallo():
    return "Server is running, er zijn momenteel geen API endpoints beschikbaar."


@app.route(endpoint + '/rides')
def rides():
    data = DataRepository.get_rides()
    return jsonify(rides=data)


@app.route(endpoint + '/rides/<rideid>')
def ride(rideid):
    data = DataRepository.get_ride_by_id(rideid)
    return jsonify(ride=data)


@app.route(endpoint + '/rides/totaldistance')
def total_distance():
    data = DataRepository.get_total_distance()
    return jsonify(totaldistance=data)


@app.route(endpoint + '/rides/locations/<rideid>')
def locations(rideid):
    data = DataRepository.get_locations_by_rideid(rideid)
    latlngs = []
    for i in data:
        decoded_geohash = base36encode(int(i['value']))
        # print(decoded_geohash)
        decoded_latitude, decoded_longitude = geohash2.decode(decoded_geohash)
        latlngs.append([float(decoded_latitude), float(decoded_longitude)])
    # print(latlngs)
    return latlngs


# SOCKET IO
@socketio.on('connect')
def initial_connection():
    print('A new client connect')


@socketio.on('led')
def change_led_status(data):
    global led_status
    led_status = data['led']
    if led_status < 2:
        GPIO.output(led, data['led'])
    send_status()


@socketio.on('sensitivity')
def change_led_status(data):
    global auto_sensitivity
    auto_sensitivity = data['sensitivity']
    send_status()


@socketio.on('GPS')
def send_gps():
    # print("gps call")
    location = gps.read_GPS()
    # print(location)
    if location != "No or weak signal":
        socketio.emit(
            'GPS', {'long': location[0], 'lat': location[1], 'speed': location[2]})
    else:
        socketio.emit('GPS', {'long': 0, 'lat': 0, 'speed': 0})


@socketio.on('status')
def send_status():
    global led_status, alarm_status, auto_sensitivity
    # print(led_auto_status)
    socketio.emit('status', {'led': led_status, 'auto-on/off': led_auto_status,
                  'alarm': alarm_status, 'sensitivity': auto_sensitivity})


@socketio.on('ride')
def change_ride_status(data):
    global tracking
    if data == 1:
        start_ride()
    if data == 0:
        stop_ride()


@socketio.on('ridestatus')
def send_ride_status():
    global tracking
    socketio.emit('ride', tracking)


@socketio.on('alarm')
def change_alarm_status(data):
    # print(data['alarm'])
    global tracking
    if data['alarm'] == 1:
        start_alarm()
    if data['alarm'] == 0:
        stop_alarm()
    send_status()


if __name__ == '__main__':
    try:
        showIP()
        start_thread()
        print("**** Starting APP ****")
        socketio.run(app, debug=False, host='0.0.0.0')
    except KeyboardInterrupt:
        print('KeyboardInterrupt exception is caught')
    finally:
        GPIO.output(buzz, GPIO.LOW)
        disp.clear()
        disp.display()
        GPIO.output(powerpin, GPIO.LOW)
        print("finished")
