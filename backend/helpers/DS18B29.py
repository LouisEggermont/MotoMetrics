class DS18B29:
    def __init__(self, sensor_file_name):
        self.sensor_file_name = sensor_file_name
    
    def read_temperature(self):

        sensor_file = open(self.sensor_file_name, 'r')
        for line in sensor_file:
            line = line.rstrip('\n')
            index = line.find('t=')
            if index != -1:
                temperature = int(line[index+2:]) / 1000
                return temperature
        sensor_file.close()


# Example usage:
# sensor = DS18B29('/sys/bus/w1/devices/28-00d5b70000af/w1_slave')
# print(sensor.read_temperature())
