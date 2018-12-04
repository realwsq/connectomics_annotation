from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Mode_Control(QWidget):


    def __init__(self, modes, value_changed_func):
        super(Mode_Control, self).__init__()

        self.modes = modes
        self.value_changed_func = value_changed_func

        self.initUI()

    def get_current_mode(self):
        return self.cb.currentText()

    def initUI(self):

        self.label = QLabel("mode")
        self.cb = QComboBox()
        self.cb.addItems(self.modes)
        self.cb.currentIndexChanged.connect(self.value_changed_func)
        self.cb.setCurrentIndex(4)

        grid = QGridLayout()
        grid.addWidget(self.label,1,0)
        grid.addWidget(self.cb,1,1)

        self.setLayout(grid)

