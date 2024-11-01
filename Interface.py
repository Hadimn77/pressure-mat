import sys
import os
import json
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QHBoxLayout, QGridLayout, QSizePolicy, QSplashScreen,
    QPushButton, QLineEdit, QVBoxLayout, QMenu, QFileDialog, QMessageBox, QTabWidget, QToolButton, QLabel
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QEvent

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class UserInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.userinput = QLineEdit(self)
        self.userinput.setPlaceholderText('Enter Text')
        self.userinput.setObjectName("userinput")
        self.userinput.setCursorPosition(0)

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

class WelcomeButtons(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.initUI(text)

    def initUI(self, text):
        self.button = QPushButton(text, self)
        self.button.setObjectName("WelcomeButtons")

class TabContent(QWidget):
    def __init__(self, parent=None, title="Plot"):
        super().__init__(parent)
        self.initUI(title)

    def initUI(self, title):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(50)

        input_layout = QVBoxLayout()
        input_layout.setSpacing(5)

        grid = QGridLayout(self)
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(5)
        grid.setContentsMargins(12, 0, 0, 0)

        self.userinput1_label = InputLabel('Plot Name')
        self.userinput2_label = InputLabel('Detail 1')
        self.userinput3_label = InputLabel('Detail 2')

        self.userinput1_widget = UserInput()
        self.userinput2_widget = UserInput()
        self.userinput3_widget = UserInput()
        self.button1_widget = RecordingButtons('Start')
        self.button2_widget = RecordingButtons('Stop')
        self.button3_widget = RecordingButtons('Save')

        self.userinput1_widget.userinput.setText(title)

        grid.addWidget(self.userinput1_label.inputlabel, 0, 0)
        grid.addWidget(self.userinput1_widget.userinput, 1, 0)
        grid.addWidget(self.userinput2_label.inputlabel, 2, 0)
        grid.addWidget(self.userinput2_widget.userinput, 3, 0)
        grid.addWidget(self.userinput3_label.inputlabel, 4, 0)
        grid.addWidget(self.userinput3_widget.userinput, 5, 0)

        input_layout.addLayout(grid)

        recordingButtonsLayout = QGridLayout()
        recordingButtonsLayout.addWidget(self.button1_widget.button, 0, 0)
        recordingButtonsLayout.addWidget(self.button2_widget.button, 0, 1)
        recordingButtonsLayout.addWidget(self.button3_widget.button, 1, 0, 1, 2)
        recordingButtonsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        input_layout.addLayout(recordingButtonsLayout)

        recordingButtonsLayout.setContentsMargins(12, 30, 0, 0)
        recordingButtonsLayout.columnMinimumWidth(200)

        input_layout.addLayout(recordingButtonsLayout)
        input_layout.addStretch(1)

        self.button1_widget.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.button2_widget.button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.button1_widget.button.setMinimumWidth(100)
        self.button2_widget.button.setMinimumWidth(100)

        self.button1_widget.button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.button2_widget.button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.button1_widget.button.setMaximumWidth(200)
        self.button2_widget.button.setMaximumWidth(200)

        self.userinput1_widget.userinput.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.userinput2_widget.userinput.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.userinput3_widget.userinput.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.userinput1_widget.userinput.setMaximumWidth(405)
        self.userinput2_widget.userinput.setMaximumWidth(405)
        self.userinput3_widget.userinput.setMaximumWidth(405)

        main_layout.addLayout(input_layout)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        self.canvas.setMinimumWidth(400)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.canvas.setMaximumHeight(800)
        self.canvas.setMaximumWidth(800)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

        canvas_layout = QVBoxLayout()
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addStretch(1)

        main_layout.addLayout(canvas_layout)

        self.setLayout(main_layout)

        self.userinput1_widget.userinput.editingFinished.connect(self.updateTabName)

    def plot(self, data):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(data)
        self.figure.tight_layout()
        self.canvas.draw()



    def resizeEvent(self, event: QEvent):
        super().resizeEvent(event)
        self.figure.tight_layout()
        self.canvas.draw()

    def updateTabName(self):
        title = self.userinput1_widget.userinput.text()
        if len(title) < 1:
            QMessageBox.critical(self, "Error", "Plot Name must be at least 1 character")
            self.userinput1_widget.userinput.setFocus()
            return
        parent = self.parentWidget()
        if parent:
            parent = parent.parentWidget()
            if parent and isinstance(parent, QTabWidget):
                index = parent.indexOf(self)
                parent.setTabText(index, title)
class Main(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentFile = None
        self.lastSerializedData = None
        self.initUI()
        self._createActions()
        self._createMenuBar()
        self._connectActions()

    def initUI(self):
        self.setWindowTitle('Untitled - 2D Plot')
        self.setGeometry(100, 100, 800, 400)
        self.tab_widget = QTabWidget(self)
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

    def _createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu('&File', self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        editMenu = QMenu('&Edit', self)
        menuBar.addMenu(editMenu)

        editMenu.addAction(self.addTabAction)
        editMenu.addAction(self.removeTabAction)

    def _createActions(self):
        self.newAction = QAction("&New", self)
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.saveAsAction = QAction("&Save As...", self)
        self.exitAction = QAction("&Exit", self)

        self.newAction.setShortcut("Ctrl+N")
        self.openAction.setShortcut("Ctrl+O")
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAsAction.setShortcut("Ctrl+Shift+S")

        self.addTabAction = QAction("&Add Plot", self)
        self.removeTabAction = QAction("&Delete Plot", self)
        self.addTabAction.setShortcut("Ctrl+T")
        self.removeTabAction.setShortcut("Ctrl+W")

    def _connectActions(self):
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.exitAction.triggered.connect(self.exitApp)
        self.addTabAction.triggered.connect(self.addTab)
        self.removeTabAction.triggered.connect(self.removeCurrentTab)

    def addTab(self):
        title = "Plot " + str(self.tab_widget.count() + 1)
        new_tab = TabContent(title=title)
        index = self.tab_widget.addTab(new_tab, title)
        self.tab_widget.setCurrentIndex(index)
        new_tab.plot([1, 2, 3, 4, 5])
        self.tab_widget.update()

    def removeTab(self, index):
        tab = self.tab_widget.widget(index)
        if self.hasChanges(tab):
            reply = self.confirmRemoveTab()
            if reply == QMessageBox.StandardButton.Discard:
                pass
            else:
                return

        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.warning(self, "Warning", "You must have at least one tab open.")

    def removeCurrentTab(self):
        current_index = self.tab_widget.currentIndex()
        self.removeTab(current_index)

    def newFile(self):
        if self.hasChanges():
            reply = self.confirmSaveChanges()
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.tab_widget.clear()
        self.addTab()
        self.currentFile = None
        self.lastSerializedData = {}
        self.setWindowTitle('Untitled - 2D Plot')

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
                    self.setWindowTitle(os.path.basename(filename) + " - 2D Plot")
                    self.lastSerializedData = self.serializeData()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")

    def saveFile(self):
        if self.currentFile:
            try:
                with open(self.currentFile, 'w') as file:
                    data = self.serializeData()
                    json.dump(data, file, indent=4)
                    self.setWindowTitle(os.path.basename(self.currentFile) + " - 2D Plot")
                    self.lastSerializedData = data
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            self.saveAsFile()

    def saveAsFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Application Files (*.app)")
        if filename:
            try:
                with open(filename, 'w') as file:
                    data = self.serializeData()
                    json.dump(data, file, indent=4)
                    self.currentFile = filename
                    self.setWindowTitle(os.path.basename(filename) + " - 2D Plot")
                    self.lastSerializedData = data
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")

    def exitApp(self):
        self.close()

    def serializeData(self):
        data = {}
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab_data = {
                'userinput1': tab.userinput1_widget.userinput.text(),
                'userinput2': tab.userinput2_widget.userinput.text(),
                'userinput3': tab.userinput3_widget.userinput.text(),
            }
            data[f'Tab_{i}'] = tab_data
        return data

    def deserializeData(self, data):
        self.tab_widget.clear()
        for key, tab_data in data.items():
            new_tab = TabContent()
            new_tab.userinput1_widget.userinput.setText(tab_data.get('userinput1', ''))
            new_tab.userinput2_widget.userinput.setText(tab_data.get('userinput2', ''))
            new_tab.userinput3_widget.userinput.setText(tab_data.get('userinput3', ''))
            self.tab_widget.addTab(new_tab, key)

    def clearUserInputs(self):
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            tab.userinput1_widget.userinput.clear()
            tab.userinput2_widget.userinput.clear()
            tab.userinput3_widget.userinput.clear()

    def hasChanges(self, specific_tab=None):
        if specific_tab is not None:
            tab_data = {
                'userinput1': specific_tab.userinput1_widget.userinput.text(),
                'userinput2': specific_tab.userinput2_widget.userinput.text(),
                'userinput3': specific_tab.userinput3_widget.userinput.text(),
            }
            return tab_data != self.lastSerializedData.get(f'Tab_{self.tab_widget.indexOf(specific_tab)}', {})

        return self.lastSerializedData is not None and self.serializeData() != self.lastSerializedData

    def confirmSaveChanges(self):
        return QMessageBox.question(
            self,
            "Save Changes",
            "Do you want to save your changes?",
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
        if self.hasChanges():
            reply = self.confirmSaveChanges()
            if reply == QMessageBox.StandardButton.Save:
                self.saveFile()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Welcome - 2D Plot')
        self.setGeometry(100, 100, 800, 520)

        self.setObjectName("WelcomeScreen")
        layout = QVBoxLayout()

        self.newFileButton = WelcomeButtons("New File")
        self.openFileButton = WelcomeButtons("Open File")

        self.newFileButton.button.clicked.connect(lambda: [main.newFile(), welcomeScreen.close(), main.show()])
        self.openFileButton.button.clicked.connect(lambda: [main.openFile(), welcomeScreen.close(), main.show()])
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.newFileButton.button)
        layout.addWidget(self.openFileButton.button)
        layout.addStretch(1)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    welcomeScreen = WelcomeScreen()
    welcomeScreen.show()



    main = Main()

    sys.exit(app.exec())
