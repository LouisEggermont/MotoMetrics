from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)
powerpin = 18
GPIO.setup(powerpin, GPIO.OUT)
GPIO.output(powerpin, GPIO.HIGH)
time.sleep(2)

# from DS18B29 import DS18B29
# temp = DS18B29('/sys/bus/w1/devices/28-00d5b70000af/w1_slave') #Remember to use your specific addres

# from LDR import BrightnessReader
# ldr = BrightnessReader(26)

# from MPU6050 import MPU6050
# MPU = MPU6050(0x68)

# from MAX6675 import MAX6675
# engine_temp = MAX6675()

# from GPS import GPSModule
# gps = GPSModule()

try:
    while True:
        time.sleep(1)
        #  print(temp.read_temperature())
        # print(ldr.read_brightness())
        # print(gps.show_raw())
        # print(gps.read_GPS())
        # print(gps.read_time())
        # print(MPU.get_acceleration()[2])
        # print(MPU.get_tilt()[0])
        # print(engine_temp.read_temperature())
        # print(MPU.calculate_tilt_angle(0.1))
        # print(engine_temp.read_temperature())
        # pass

except KeyboardInterrupt as e:
    print("interupt {0}".format(e))
finally:
    GPIO.output(powerpin, GPIO.LOW)
    GPIO.cleanup()
    # pass
