import RPi.GPIO as GPIO
import time

class BrightnessReader:
    def __init__(self, resistorPin):
        GPIO.setmode(GPIO.BCM)
        self.resistorPin = resistorPin

    def read_brightness(self):
        while True:
            GPIO.setup(self.resistorPin, GPIO.OUT)
            GPIO.output(self.resistorPin, GPIO.LOW)

            startTime = time.time()
            diff = 0

            while (time.time() - startTime) < 0.1:
                pass

            GPIO.setup(self.resistorPin, GPIO.IN)
            currentTime = time.time()

            while GPIO.input(self.resistorPin) == GPIO.LOW:
                diff = time.time() - currentTime

            return diff * 1000


# Example usage:
# resistorPin = 26
# brightness_reader = BrightnessReader(resistorPin)
# brightness = brightness_reader.read_brightness()
# print(brightness)