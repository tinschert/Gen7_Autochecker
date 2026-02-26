# -*- coding: utf-8 -*-
# @file debug_window.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import sys
from PyQt5 import QtWidgets
import logging

# Uncomment below for terminal log messages
# logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')

class QTextEditLogger(logging.Handler):
    """ """
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
    
    def emit(self, record):
        """
        

        Args:
          record: 

        Returns:

        """
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        

class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    """ """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        logTextBox = QTextEditLogger(self)
        logTextBox.widget.setFixedSize(800,300)
        logTextBox.widget.zoomIn(2)
        # Change window title
        self.setWindowTitle("Debug Information")
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [%(filename)s] [%(message)s]'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        layout = QtWidgets.QVBoxLayout()
       
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dlg = MyDialog()
    dlg.show()
    dlg.raise_()
    sys.exit(app.exec_())

