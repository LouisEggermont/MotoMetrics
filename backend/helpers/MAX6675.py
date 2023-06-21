import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)  # Bus SPI0, CS0
spi.max_speed_hz = 500000  # Set the maximum clock speed (Hz)


class MAX6675:
    def __init__(self, bus=0, cs=0, max_speed_hz=500000):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, cs)
        self.spi.max_speed_hz = max_speed_hz


    def read_temperature(self):
        #stuur 16 bits 
        resp = self.spi.xfer([0x00, 0x00])

        temp = ((resp[0] & 0x7F) << 8) | resp[1] #combineer beide bytes en de "DUMMY SIGN BIT" uit maskeren
        temp = temp >> 3  # De 3 LSB verwijderen

        temp = temp * 0.25 # Omrekenen naar celcius

        return temp

    def cleanup(self):
        self.spi.close()

# Example usage:
# sensor = MAX6675()
# print(sensor.read_temperature())
    

