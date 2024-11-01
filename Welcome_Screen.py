import sys
import json
import os
from Interface_3D import Main3D
from Interface_2D import Main2D
from PyQt6.QtWidgets import (QWidget, QApplication, QToolButton, QGridLayout, QFileDialog, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize

class WelcomeButtons(QWidget):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.initUI(text, icon_path)

    def initUI(self, text, icon_path):
        self.button = QToolButton(self)
        self.button.setText(text)
        if icon_path:
            self.button.setIcon(QIcon(icon_path))
        self.button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button.setObjectName("WelcomeButtons")

class WelcomeScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Welcome - 2D Plot')
        self.setGeometry(100, 100, 900, 540)
        self.showMaximized()

        self.setObjectName("WelcomeScreen")
        layout = QGridLayout()

        self.openFileButton = WelcomeButtons("Open File", "open_file.png")
        self.openFileButton.button.setIconSize(QSize(80, 80))
        self.NewFile2D = WelcomeButtons("New 2D Plot", "new-file-2d.png")
        self.NewFile2D.button.setIconSize(QSize(80, 80))
        self.NewFile3D = WelcomeButtons("New 3D Plot", "new-file-3d.png")
        self.NewFile3D.button.setIconSize(QSize(80, 80))

        self.openFileButton.button.clicked.connect(self.openFile)
        self.NewFile2D.button.clicked.connect(lambda: [welcomeScreen.close(), self.open_2d_plot()])
        self.NewFile3D.button.clicked.connect(lambda: [welcomeScreen.close(), self.open_3d_plot()])

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.openFileButton.button, 0, 0)
        layout.addWidget(self.NewFile2D.button, 0, 1)
        layout.addWidget(self.NewFile3D.button, 0, 2)

        self.setLayout(layout)

    def open_2d_plot(self):
        self.plotWindow2D = Main2D()
        self.plotWindow2D.showMaximized()
        self.close()

    def open_3d_plot(self):
        self.plotWindow3D = Main3D()
        self.plotWindow3D.showMaximized()
        self.close()

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Application Files (*.app)")
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    data = json.load(file)
                    plot_type = data.get('plot_type', None)

                    if plot_type == '2D':
                        self.plotWindow2D = Main2D()
                        self.plotWindow2D.deserializeData(data)
                        self.plotWindow2D.currentFile = fileName
                        self.plotWindow2D.setWindowTitle(os.path.basename(fileName) + " - 2D Plot")
                        self.plotWindow2D.showMaximized()
                        self.close()

                    elif plot_type == '3D':
                        self.plotWindow3D = Main3D()
                        self.plotWindow3D.deserializeData(data)
                        self.plotWindow3D.currentFile = fileName
                        self.plotWindow3D.setWindowTitle(os.path.basename(fileName) + " - 3D Plot")
                        self.plotWindow3D.showMaximized()
                        self.close()

                    else:
                        QMessageBox.critical(self, "Error", "The selected file is not recognized as a 2D or 3D plot.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    welcomeScreen = WelcomeScreen()
    welcomeScreen.show()

    with open("stylesheet3.qss", "r") as f:
        style = f.read()
        app.setStyleSheet(style)

    sys.exit(app.exec())
