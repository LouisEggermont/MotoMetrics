from smbus import SMBus
import math

class MPU6050:
    def __init__(self, par_addr, num_samples=10, alpha=0.5):
        self.addr = par_addr
        self.i2c = SMBus()
        self.i2c.open(1)
        self.__setup()
        self.num_samples = num_samples
        self.alpha = alpha
        self.filtered_accel_x = 0
        self.filtered_accel_y = 0
        
    def get_tilt_with_filter(self):
        accel_scale = 16384  # Resolution for accel range of ±2g

        accel_x_sum = 0
        accel_y_sum = 0
        accel_z_sum = 0
        for _ in range(self.num_samples):
            accel_x_sum += self.__read_data(0x3B) / accel_scale
            accel_y_sum += self.__read_data(0x3D) / accel_scale
            accel_z_sum += self.__read_data(0x3F) / accel_scale

        accel_x_avg = accel_x_sum / self.num_samples
        accel_y_avg = accel_y_sum / self.num_samples
        accel_z_avg = accel_z_sum / self.num_samples

        self.filtered_accel_x = self.alpha * accel_x_avg + (1 - self.alpha) * self.filtered_accel_x
        self.filtered_accel_y = self.alpha * accel_y_avg + (1 - self.alpha) * self.filtered_accel_y

        tilt_x = math.atan2(self.filtered_accel_y, self.__dist(self.filtered_accel_x, accel_z_avg))
        tilt_y = math.atan2(self.filtered_accel_x, self.__dist(self.filtered_accel_y, accel_z_avg))

        tilt_x_deg = math.degrees(tilt_x)
        tilt_y_deg = math.degrees(tilt_y)

        return tilt_x_deg, tilt_y_deg
    
    def get_tilt(self):
        accel_scale = 16384  # Resolution for accel range of ±2g

        accel_x = self.__read_data(0x3B) / accel_scale
        accel_y = self.__read_data(0x3D) / accel_scale
        accel_z = self.__read_data(0x3F) / accel_scale

        tilt_x = math.atan2(accel_y, self.__dist(accel_x, accel_z))
        tilt_y = math.atan2(accel_x, self.__dist(accel_y, accel_z))

        tilt_x_deg = math.degrees(tilt_x)
        tilt_y_deg = math.degrees(tilt_y)

        return tilt_x_deg, tilt_y_deg

    def __setup(self):
        self.i2c.write_byte_data(self.addr, 0x6B, 0x1)  # wake up from sleep mode

    def __read_data(self, register):
        raw_data = self.i2c.read_i2c_block_data(self.addr, register, 2)
        return self.merge_bytes(raw_data[0], raw_data[1])

    def __dist(self, a, b):
        return math.sqrt(a * a + b * b)

   

    def get_acceleration(self):
        accel_scale = 16384  # Resolution for accel range of ±2g

        accel_x = self.__read_data(0x3B) / accel_scale
        accel_y = self.__read_data(0x3D) / accel_scale
        accel_z = self.__read_data(0x3F) / accel_scale

        return accel_x, accel_y, accel_z

    @staticmethod
    def merge_bytes(MSB, LSB):
        val = (MSB << 8) | LSB
        if val & 0x8000:
            val = val - (2 ** 16)
        return val


# Example usage:
# MPU = MPU6050(0x68)
# print(MPU.get_tilt()[0])
# print(MPU.get_acceleration()[1])