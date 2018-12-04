from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Label_Slider(QWidget):
    def __init__(self, label_text, slider_min, slider_max, slider_default, value_changed_func):
        super(Label_Slider, self).__init__()
        self.label_text = label_text
        self.slider_min = slider_min
        self.slider_max = slider_max
        self.slider_default = slider_default
        self.value_changed_func = value_changed_func
        self.initUI()
        
    def initUI(self):
        
        self.label = QLabel(self.label_text)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.slider_min)
        self.slider.setMaximum(self.slider_max)
        self.slider.setValue(self.slider_default)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.value_changed_func)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.label, 1, 0)
        grid.addWidget(self.slider, 1, 1)
        
        self.setLayout(grid) 
        
        # self.setGeometry(300, 300, 350, 300)
        # self.show()