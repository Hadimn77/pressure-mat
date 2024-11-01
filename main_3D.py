import numpy as np
from scipy.interpolate import Rbf
import serial
from collections import deque
from PyQt6.QtCore import QThread, pyqtSignal

class PressureMapThread3D(QThread):

    data_ready = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)
    current_data = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, port, baud_rate, x_sensor, y_sensor, z_sensor, x, y, z, parent=None):
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate

        self.x_sensor = x_sensor
        self.y_sensor = y_sensor
        self.z_sensor = z_sensor
        self.x = x
        self.y = y
        self.z = z

        self.Filtering_Threshold = 10
        self.window_size = 5
        self.rbf_epsilon = 0.5
        self.running = False
        self.time_series_buffer = deque(maxlen=self.window_size)


    def check_port(self):
        try:
            ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            ser.close()
            return True
        except serial.SerialException:
            return False

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Failed to open serial port: {e}")
            return

        while self.running:
            try:
                Serial_Values = self.read_serial_data(ser)
                if Serial_Values is not None:
                    if len(Serial_Values) == len(self.x_sensor):
                        Serial_Values = self.filter_serial_values(Serial_Values, self.Filtering_Threshold)
                        self.time_series_buffer.append(Serial_Values)
                        averaged_values = self.moving_average_filter()
                        P_t = self.pressure_interpolation(self.x_sensor.values, self.y_sensor.values, self.z_sensor.values, averaged_values)
                        self.data_ready.emit(self.x.values, self.y.values, self.z.values, P_t)
                        self.current_data.emit(self.x.values, self.y.values, self.z.values, P_t)
                    else:
                        print("Mismatch between sensor values and sensor coordinates")
                else:
                    print("No data received")
            except Exception as e:
                print(f"Error during data processing: {e}")

        ser.close()

    def start_recording(self):
        self.running = True
        self.start()

    def stop_recording(self):
        self.running = False
        self.wait()

    def moving_average_filter(self):
        if len(self.time_series_buffer) < self.window_size:
            return np.mean(self.time_series_buffer, axis=0)
        else:
            return np.mean(np.array(self.time_series_buffer), axis=0)

    def pressure_interpolation(self, x_sensor, y_sensor, z_sensor, Serial_Values):
        Serial_Values = np.nan_to_num(Serial_Values).astype(int)
        # Create RBF interpolator for pressure
        rbf_interpolator = Rbf(x_sensor, y_sensor, z_sensor, Serial_Values, function='multiquadric')
        # Interpolate pressure values at the new points
        pressure_interpolated = rbf_interpolator(self.x, self.y, self.z)
        return pressure_interpolated

    def read_serial_data(self, ser):
        Serial_Data = ser.readline().decode('utf-8', errors='ignore').strip()
        if Serial_Data:
            Serial_Values = Serial_Data.split(',')
            # Remove '' from the end of array
            if Serial_Values[-1] == '':
                Serial_Values.pop()
            Serial_Values = [0 if x == '' else x for x in Serial_Values]
            return np.array([float(value) for value in Serial_Values])
        return None

    def filter_serial_values(self, values, threshold):
        return np.array([0 if x < threshold else x for x in values])
