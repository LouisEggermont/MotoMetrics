import time
import serial  
import math
import geohash2

class GPSModule:
    def __init__(self):
        self.ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0') # only get GPRMC senctices
        self.send_command(b"PMTK220,1000") # set speed
        self.send_command(b"PMTK251,9600") #set baudrate
    
    def send_command(self, command: bytes, add_checksum: bool = True) -> None:
        self.ser.write(b"$")
        self.ser.write(command)
        if add_checksum:
            checksum = 0
            for char in command:
                checksum ^= char
            self.ser.write(b"*")
            self.ser.write(bytes("{:02x}".format(checksum).upper(), "ascii"))
        self.ser.write(b"\r\n")
    

    def clear_serial_buffer(self):
        while self.ser.in_waiting > 0:
            self.ser.readline()

    def read_time(self):
        self.clear_serial_buffer()
        serial = self.ser.readline()       
        x = serial.decode().split(',')
        if x[0] == "$GPRMC":
            time_data = x[1]
            time_str = time_data[:2] + ":" + time_data[2:4] + ":" + time_data[4:6]

            # Adjust time by adding 2 hours
            adjusted_hours = (int(time_str[:2]) + 2) % 24
            adjusted_time_str = str(adjusted_hours).zfill(2) + time_str[2:]

            return adjusted_time_str
        else:
            return "no time"

    def read_GPS(self):
        self.clear_serial_buffer()
        # ----- read from gps 
        serial = self.ser.readline()       
        x = serial.decode().split(',')
        # ----- test with hardcoded coords 
        # serial = '$GPRMC,234315.00,A,5049.49206,N,00314.98151,E,0.042,,220523,,,A*72'
        # x = serial.split(',')
        # --------------------------------------
        if x[0] == "$GPRMC" and x[2] == "A":
            lat_nmea = float(x[3])
            lat_deg = lat_nmea // 100
            lat_min = lat_nmea - 100 * lat_deg
            lat_deg = lat_deg + lat_min / 60

            lon_nmea = float(x[5])
            lon_deg = lon_nmea // 100
            lon_min = lon_nmea - 100 * lon_deg
            lon_deg = lon_deg + lon_min / 60

            speed_nmea = float(x[7])
            speed_km = math.floor(speed_nmea * 1.852)

            return lat_deg, lon_deg, speed_km
        else:
            return "No or weak signal"
        
    def show_raw(self):
        return self.ser.readline()

# # Example usage:
# gps = GPSModule()
# # # print(gps.nmea_to_coord(gps.ser.readline()))
# print(gps.read_GPS())
# print(gps.show_raw())


