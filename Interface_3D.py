import sys
import os
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from main_3D import PressureMapThread3D
from PyQt6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QHBoxLayout, QGridLayout, QSizePolicy,
    QPushButton, QLineEdit, QVBoxLayout, QMenu, QFileDialog, QMessageBox, QTabWidget, QToolButton, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer, QElapsedTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

matplotlib.use('QtAgg')


class UserInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.userinput = QLineEdit(self)
        self.userinput.setPlaceholderText('Enter Text')
        self.userinput.setObjectName("userinput")
        self.userinput.setCursorPosition(0)

        self.userinput.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.userinput.setMaximumWidth(405)


class InputLabel(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.inputlabel = QLabel(text)
        self.inputlabel.setObjectName("inputlabel")


class RecordingButtons(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.button = QPushButton(text, self)
        self.button.setObjectName("RecordingButtons")
        self.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.button.setMinimumWidth(100)
        self.button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.button.setMaximumWidth(200)


class SaveButton(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.button = QPushButton(text, self)
        self.button.setObjectName("RecordingButtons")
        self.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.button.setMinimumWidth(205)
        self.button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.button.setMaximumWidth(405)


class DiscardButton(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.button = QPushButton(text, self)
        self.button.setObjectName("RecordingButtons")
        self.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.button.setMinimumWidth(205)
        self.button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.button.setMaximumWidth(405)


class TabContent3D(QWidget):
    def __init__(self, parent=None, title="Plot"):
        super().__init__(parent)
        self.initUI(title)
        self.data_buffer = []
        self.recording_timer = QElapsedTimer()
        self.default_title = title

    def initUI(self, title):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(50, 40, 50, 40)
        main_layout.setSpacing(50)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(5)

        grid = QGridLayout(self)
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(5)
        grid.setContentsMargins(0, 0, 0, 0)

        self.userinput1_label = InputLabel('Plot Name')
        self.userinput2_label = InputLabel('Detail 1')
        self.userinput3_label = InputLabel('Detail 2')

        self.userinput1_widget = UserInput()
        self.userinput2_widget = UserInput()
        self.userinput3_widget = UserInput()

        self.start_button = RecordingButtons('Start')
        self.stop_button = RecordingButtons('Stop')
        self.saveData_button = SaveButton('Save Data')
        self.discardData_button = DiscardButton('Delete Data')

        self.stop_button.setEnabled(False)

        self.start_button.button.clicked.connect(self.start_recording)
        self.stop_button.button.clicked.connect(self.stop_recording)
        self.saveData_button.button.clicked.connect(self.save_data)
        self.discardData_button.button.clicked.connect(self.discard_data)

        self.userinput1_widget.userinput.setText(title)

        grid.addWidget(self.userinput1_label.inputlabel, 0, 0)
        grid.addWidget(self.userinput1_widget.userinput, 1, 0)
        grid.addWidget(self.userinput2_label.inputlabel, 2, 0)
        grid.addWidget(self.userinput2_widget.userinput, 3, 0)
        grid.addWidget(self.userinput3_label.inputlabel, 4, 0)
        grid.addWidget(self.userinput3_widget.userinput, 5, 0)

        input_layout.addLayout(grid)

        recordingButtonsLayout = QGridLayout()
        recordingButtonsLayout.addWidget(self.start_button.button, 0, 0)
        recordingButtonsLayout.addWidget(self.stop_button.button, 0, 1)
        recordingButtonsLayout.addWidget(self.saveData_button.button, 1, 0, 1, 2)
        recordingButtonsLayout.addWidget(self.discardData_button.button, 2, 0, 1, 2)
        recordingButtonsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout.addLayout(recordingButtonsLayout)

        recordingButtonsLayout.setContentsMargins(0, 40, 0, 0)
        recordingButtonsLayout.columnMinimumWidth(200)

        input_layout.addStretch(1)

        main_layout.addLayout(input_layout)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.canvas.setMinimumHeight(400)
        self.canvas.setMinimumWidth(550)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.canvas.setMaximumWidth(850)

        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addStretch(1)

        main_layout.addLayout(canvas_layout)


        self.setLayout(main_layout)

        self.userinput1_widget.userinput.editingFinished.connect(self.updateTabName)


        self.port = 'COM3'
        self.baud_rate = 9600
        self.X_dimension = 200
        self.Y_dimension = 200
        self.resolution = 100

        self.sensor_location_file = 'Sensor_points.txt'
        self.Sensor_data = pd.read_csv(self.sensor_location_file, sep=",", header=None, names=['X', 'Y', 'Z', 'Pressure'])

        self.interpolation_points_file = 'interpolation_points.txt'
        self.data_with_pressure = pd.read_csv(self.interpolation_points_file, sep="\t", header=None,
                                         names=['X', 'Y', 'Z', 'Pressure'])

        self.x_sensor = self.Sensor_data['X']
        self.y_sensor = self.Sensor_data['Y']
        self.z_sensor = self.Sensor_data['Z']

        self.x = self.data_with_pressure['X']
        self.y = self.data_with_pressure['Y']
        self.z = self.data_with_pressure['Z']

        self.thread = PressureMapThread3D(self.port, self.baud_rate, self.x_sensor, self.y_sensor, self.z_sensor,
                                          self.x, self.y, self.z)

        self.save_timer = QTimer(self)
        self.save_timer.setInterval(100)
        self.save_timer.timeout.connect(self.collect_data)

        self.thread.data_ready.connect(self.plot)
        self.thread.current_data.connect(self.collect_data)

        self.recording_active = False

        self.initialize_plot()

    def start_recording(self):
        main_window = self.window()

        if isinstance(main_window, Main3D):
            recording_tab_index = main_window.is_any_tab_recording()

            if recording_tab_index is not None:
                recording_tab_name = main_window.tab_widget.tabText(recording_tab_index)
                QMessageBox.critical(self, "Error",
                                     f"Recording is active in the tab: '{recording_tab_name}'. Stop the current recording before starting a new one.")
                return

        if not self.thread.check_port():
            QMessageBox.critical(self, "Error", "Failed to open serial port. Please check the connection.")
            return

        if self.data_buffer:
            reply = QMessageBox.warning(
                self,
                "Unsaved Data",
                "There is unsaved data from the previous recording. Do you want to discard the previous data and start a new recording?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.data_buffer = []
            else:
                return

        self.start_button.button.setEnabled(False)
        self.stop_button.button.setEnabled(True)
        self.recording_active = True
        self.recording_timer.start()
        self.thread.start_recording()

    def stop_recording(self):
        self.start_button.button.setEnabled(True)
        self.stop_button.button.setEnabled(False)
        self.recording_active = False
        self.thread.stop_recording()
        self.initialize_plot()

    def save_data(self):
        if self.recording_active:
            QMessageBox.critical(self, "Error", "Please stop recording before saving data.")
            return

        if not self.data_buffer:
            QMessageBox.information(self, "Error", "No data recorded.")
            return

        self.save_timer.stop()
        self.save_to_file_dialog()

    def save_to_file_dialog(self):
        try:
            filePath, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "Text Files (*.txt);;All Files (*)")
            if filePath:
                self.save_to_file(filePath)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to open file manager: {e}")
            print(f"Error in save_to_file_dialog: {e}")

    def save_to_file(self, filePath):
        try:
            with open(filePath, 'w') as file:
                for elapsed_time, x, y, z, P in self.data_buffer:
                    if isinstance(x, (np.ndarray, list)) and isinstance(y, (np.ndarray, list)) and isinstance(z, (
                    np.ndarray, list)) and isinstance(P, (np.ndarray, list)):
                        for x_val, y_val, z_val, P_val in zip(x, y, z, P):
                            file.write(f"{elapsed_time:.3f}: {x_val}, {y_val}, {z_val}, {P_val:.3f}\n")
                    else:
                        file.write(f"{elapsed_time:.3f}: {x}, {y}, {z}, {P:.3f}\n")
            self.data_buffer = []
            QMessageBox.information(self, "Success", "Data saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")

    def discard_data(self):
        if self.recording_active:
            QMessageBox.critical(self, "Error", "Please stop recording before deleting data.")
            return

        if not self.data_buffer:
            QMessageBox.critical(self, "Error", "No data recorded.")
            return

        reply = QMessageBox.question(self, "Delete Data", "Do you want to delete the current data? This action cannot be undone.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.data_buffer = []
            QMessageBox.information(self, "Success", "Data deleted successfully!")
        else:
            return

    def collect_data(self, x, y, z, P):
        elapsed_time = self.recording_timer.elapsed() / 1000.0
        self.data_buffer.append((elapsed_time, x.copy(), y.copy(), z.copy(), P.copy()))

    def plot(self, x, y, z, P):
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        c = ax.scatter(x, y, z, c=P, cmap='coolwarm')
        colorbar = self.figure.colorbar(c, ax=ax)
        colorbar.set_label("Pressure (kPa)")
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        ax.set_zlabel("Z Label")

        if self.recording_active:
            ax.set_title("Pressure Measurement in Progress...")
        else:
            ax.set_title("Pressure Measurement")

        self.figure.subplots_adjust(left=-1.95, right=1.25, top=0.95, bottom=0.05)
        self.canvas.draw()

    def initialize_plot(self):
        default_Z = np.zeros_like(self.x)
        self.plot(self.x, self.y, self.z, default_Z)
        self.stop_button.button.setEnabled(False)

    def updateTabName(self):
        title = self.userinput1_widget.userinput.text()
        if len(title) < 1:
            QMessageBox.warning(self, "Error", "Plot Name must be at least 1 character")
            self.userinput1_widget.userinput.setFocus()
            return

        parent = self.parentWidget()
        if parent:
            parent = parent.parentWidget()
            if parent and isinstance(parent, QTabWidget):
                for i in range(parent.count()):
                    if parent.tabText(i) == title and i != parent.indexOf(self):
                        QMessageBox.warning(self, "Error", f"A tab with the title '{title}' already exists.")
                        self.userinput1_widget.userinput.setFocus()
                        return

                index = parent.indexOf(self)
                parent.setTabText(index, title)


class Main3D(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_counter = 0
        self.currentFile = None
        self.lastSerializedData = {}
        self.initUI()
        self.createActions()
        self.createMenuBar()
        self.connectActions()


    def initUI(self):
        self.setWindowTitle('Untitled - 3D Plot')
        self.setGeometry(100, 100, 850, 500)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)
        self.tab_widget.tabCloseRequested.connect(self.removeTab)
        self.setCentralWidget(self.tab_widget)

        self.addTabButton = QToolButton(self)
        self.addTabButton.setText('+')
        self.addTabButton.setObjectName('plusTab')
        self.tab_widget.setCornerWidget(self.addTabButton)
        self.addTabButton.clicked.connect(self.addTab)

        self.addTab()

    def is_any_tab_recording(self):

        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.recording_active:
                return i
        return None

    def createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu('&File', self)
        menuBar.addMenu(fileMenu)

        newMenu = QMenu('New', self)
        newMenu.addAction(self.new2DPlotAction)
        newMenu.addAction(self.new3DPlotAction)

        fileMenu.addMenu(newMenu)

        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        editMenu = QMenu('&Edit', self)
        menuBar.addMenu(editMenu)

        editMenu.addAction(self.addTabAction)
        editMenu.addAction(self.removeTabAction)

    def createActions(self):
        self.new2DPlotAction = QAction("New 2D Plot", self)
        self.new3DPlotAction = QAction("New 3D Plot", self)
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.saveAsAction = QAction("&Save As...", self)
        self.exitAction = QAction("&Exit", self)

        self.openAction.setShortcut("Ctrl+O")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAsAction.setShortcut("Ctrl+Shift+S")

        self.addTabAction = QAction("&Add Plot", self)
        self.removeTabAction = QAction("&Delete Plot", self)
        self.addTabAction.setShortcut("Ctrl+T")
        self.removeTabAction.setShortcut("Ctrl+W")

    def connectActions(self):
        self.new2DPlotAction.triggered.connect(self.new2DPlot)
        self.new3DPlotAction.triggered.connect(self.new3DPlot)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.exitAction.triggered.connect(self.exitApp)
        self.addTabAction.triggered.connect(self.addTab)
        self.removeTabAction.triggered.connect(self.removeCurrentTab)

    def addTab(self):
        self.plot_counter += 1
        title = f"Plot {self.plot_counter}"
        new_tab = TabContent3D(title=title)
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        self.tab_widget.update()
        new_tab.updateTabName()


    def removeTab(self, index):
        tab = self.tab_widget.widget(index)

        if tab.recording_active:
            QMessageBox.critical(self, "Error", "Recording is active. Please stop the recording before deleting this tab.")
            return

        if self.tab_has_changes(tab):
            reply = self.confirmRemoveTab()
            if reply == QMessageBox.StandardButton.Discard:
                pass
            else:
                return

        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.critical(self, "Error", "You must have at least one tab open.")

    def tab_has_changes(self, specific_tab=None):
        if specific_tab is not None:
            default_title = specific_tab.default_title
            tab_data = {
                'userinput1': specific_tab.userinput1_widget.userinput.text(),
                'userinput2': specific_tab.userinput2_widget.userinput.text(),
                'userinput3': specific_tab.userinput3_widget.userinput.text(),
            }

            detect_changes = (tab_data['userinput1'] != default_title or
                           tab_data['userinput2'] != "" or
                           tab_data['userinput3'] != "")

            return detect_changes
        else:
            return self.serializeData() != self.lastSerializedData

    def removeCurrentTab(self):
        current_index = self.tab_widget.currentIndex()
        self.removeTab(current_index)

    def new3DPlot(self):
        if self.hasChanges():
            reply = self.confirmSaveChanges()
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()

            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.tab_widget.clear()
        self.lastSerializedData = {}
        self.plot_counter = 0
        self.addTab()
        self.currentFile = None
        self.setWindowTitle('Untitled - 3D Plot')

    def new2DPlot(self):

        self.close()

        if not self.close_event_accepted:
            return

        from Interface_2D import Main2D
        self.tab_widget.clear()
        self.currentFile = None
        self.lastSerializedData = {}
        self.plotWindow3D = Main2D()
        self.plotWindow3D.showMaximized()

    def openFile(self):
        if self.hasChanges():
            reply = self.confirmSaveChanges()
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Application Files (*.app)")
        if filename:
            try:
                with open(filename, 'r') as file:
                    data = json.load(file)
                    self.tab_widget.clear()
                    self.addTab()
                    self.deserializeData(data)
                    self.currentFile = filename

                    if data.get('plot_type') == '2D':
                        self.setWindowTitle(os.path.basename(filename) + " - 2D Plot")
                    if data.get('plot_type') == '3D':
                        self.setWindowTitle(os.path.basename(filename) + " - 3D Plot")

                    self.lastSerializedData = self.serializeData()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def saveFile(self):
        if self.currentFile:
            try:
                with open(self.currentFile, 'w') as file:
                    data = self.serializeData()
                    json.dump(data, file, indent=4)
                    self.setWindowTitle(os.path.basename(self.currentFile) + " - 3D Plot")
                    self.lastSerializedData = data
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            self.saveAsFile()

    def saveAsFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Application Files (*.app)")
        if not filename:
            return False
        if filename:
            try:
                with open(filename, 'w') as file:
                    data = self.serializeData()
                    json.dump(data, file, indent=4)
                    self.currentFile = filename
                    self.setWindowTitle(os.path.basename(filename) + " - 3D Plot")
                    self.lastSerializedData = data
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def exitApp(self):
        self.close()

    def serializeData(self):
        data = {
            'plot_type': '3D',
            'tabs': {}
        }
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab_title = self.tab_widget.tabText(i)

            tab_data = {
                'title': tab_title,
                'userinput1': tab.userinput1_widget.userinput.text(),
                'userinput2': tab.userinput2_widget.userinput.text(),
                'userinput3': tab.userinput3_widget.userinput.text(),
            }
            data[f'Tab_{i}'] = tab_data
        return data

    def deserializeData(self, data):
        self.tab_widget.clear()

        for tab_key, tab_data in data.items():
            if tab_key.startswith('Tab_'):
                if data.get('plot_type') == '2D':
                    from Interface_2D import TabContent2D
                    new_tab = TabContent2D()
                    new_tab.userinput1_widget.userinput.setText(tab_data.get('userinput1', ''))
                    new_tab.userinput2_widget.userinput.setText(tab_data.get('userinput2', ''))
                    new_tab.userinput3_widget.userinput.setText(tab_data.get('userinput3', ''))

                    title = tab_data.get('title', 'Untitled')
                    self.tab_widget.addTab(new_tab, title)

                elif data.get('plot_type') == '3D':
                    new_tab = TabContent3D()
                    new_tab.userinput1_widget.userinput.setText(tab_data.get('userinput1', ''))
                    new_tab.userinput2_widget.userinput.setText(tab_data.get('userinput2', ''))
                    new_tab.userinput3_widget.userinput.setText(tab_data.get('userinput3', ''))

                    title = tab_data.get('title', 'Untitled')
                    self.tab_widget.addTab(new_tab, title)

        self.currentFile = data.get('currentFile', None)

        self.tab_widget.update()
        self.tab_widget.repaint()

    def clearUserInputs(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab.userinput1_widget.userinput.clear()
            tab.userinput2_widget.userinput.clear()
            tab.userinput3_widget.userinput.clear()

    def hasChanges(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if self.tab_has_changes(tab):
                return True

        if self.tab_widget.count() > 1:
            return True

        if self.tab_widget.count() == 1:
            single_tab = self.tab_widget.widget(0)
            tab_title = self.tab_widget.tabText(0)

            if tab_title == "Plot 1" and not self.tab_has_changes(single_tab):
                return False

        return True

    def confirmSaveChanges(self):
        return QMessageBox.warning(
            self,
            "Save Changes",
            "Do you want to save your changes to this file?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )

    def confirmRemoveTab(self):
        return QMessageBox.question(
            self,
            "Delete Plot",
            "Are you sure you want to discard this plot? This action cannot be undone.",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )

    def closeEvent(self, event):
        unsaved_tabs = []
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.recording_active:
                QMessageBox.critical(self, "Recording in Progress",
                                     f"Stop the recording in tab '{self.tab_widget.tabText(i)}' before exiting.")
                event.ignore()
                return
            elif tab.data_buffer:
                unsaved_tabs.append(i)

        if unsaved_tabs:
            tab_names = ", ".join([self.tab_widget.tabText(i) for i in unsaved_tabs])
            reply = QMessageBox.warning(
                self,
                "Unsaved Data",
                f"There is unsaved data in the following tabs: {tab_names}. Do you want to save before exiting?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                for i in unsaved_tabs:
                    tab = self.tab_widget.widget(i)
                    tab.save_to_file_dialog()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

        if self.hasChanges():
            reply = self.confirmSaveChanges()
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
                self.close_event_accepted = True
                event.accept()

            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.close_event_accepted = True
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("stylesheet3.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)

    main = Main3D()
    main.showMaximized()
    sys.exit(app.exec())
