import numpy as np
from scipy.interpolate import Rbf
import serial
from collections import deque
from PyQt6.QtCore import QThread, pyqtSignal

class PressureMapThread2D(QThread):
    data_ready = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)
    current_data = pyqtSignal(np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, port, baud_rate, X_Sensors, Y_Sensors, Xm, Ym, parent=None):
        super().__init__(parent)
        self.port = port
        self.baud_rate = baud_rate
        self.X_Sensors = X_Sensors
        self.Y_Sensors = Y_Sensors
        self.Xm = Xm
        self.Ym = Ym
        self.running = False
        self.window_size = 5
        self.time_series_buffer = deque(maxlen=self.window_size)
        self.Filtering_Threshold = 100

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
            Serial_Values = self.read_serial_data(ser)
            if Serial_Values is not None:
                if len(Serial_Values) == len(self.X_Sensors):
                    Serial_Values = self.filter_serial_values(Serial_Values, self.Filtering_Threshold)
                    self.time_series_buffer.append(Serial_Values)
                    averaged_values = self.moving_average_filter()
                    Zm = self.pressure_interpolation(self.X_Sensors, self.Y_Sensors, averaged_values)
                    self.data_ready.emit(self.Xm, self.Ym, Zm)
                    self.current_data.emit(self.Xm, self.Ym, Zm)
                else:
                    print("Mismatch between sensor values and sensor coordinates")
            else:
                print("No data received")

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

    def pressure_interpolation(self, X_Sensors, Y_Sensors, Serial_Values):
        rbf = Rbf(X_Sensors, Y_Sensors, Serial_Values, function='inverse_multiquadric')
        Zm = rbf(self.Xm, self.Ym)
        Zm = np.nan_to_num(Zm).astype(int)
        return Zm

    def read_serial_data(self, ser):
        Serial_Data = ser.readline().decode('utf-8', errors='ignore').strip()
        if Serial_Data:
            Serial_Values = Serial_Data.split(',')
            if Serial_Values[-1] == '':
                Serial_Values.pop()
            Serial_Values = [0 if x == '' else x for x in Serial_Values]
            return np.array([float(value) for value in Serial_Values])
        return None

    def filter_serial_values(self, values, threshold):
        return np.array([0 if x < threshold else x for x in values])
