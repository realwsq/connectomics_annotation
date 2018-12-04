from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Label_Color_Icon(QWidget):
    def __init__(self, label_text, default_color):
        super(Label_Color_Icon, self).__init__()
        self.label_text = label_text
        self.default_color = default_color

        self.initUI()
    
    def icon_display_color(self, new_color):

        pixmap = QPixmap(16, 16)
        pixmap.fill(new_color)
        return QIcon(pixmap)


    def initUI(self):
        
        self.label = QLabel(self.label_text)
        # self.icon = QIcon()
        self.icon = QToolButton()
        self.icon.setIcon(self.icon_display_color(self.default_color))

        grid = QGridLayout()
        grid.setSpacing(3)

        grid.addWidget(self.label, 1, 0)
        grid.addWidget(self.icon, 1, 1)
        
        self.setLayout(grid) 
        
        # self.setGeometry(300, 300, 350, 300)
        # self.show()

class Foreground_and_Background_Color(QWidget):
    def __init__(self, fg_color, bg_color):
        super(Foreground_and_Background_Color, self).__init__()
        self.foreground_color = fg_color
        self.background_color = bg_color

        self.initUI()

    def set_foreground_color(self, color):
        self.foreground.icon.setIcon(self.foreground.icon_display_color(color))

    def set_background_color(self, color):
        self.background.icon.setIcon(self.background.icon_display_color(color))

    def initUI(self):
        
        self.foreground = Label_Color_Icon("foreground", self.foreground_color)
        self.background = Label_Color_Icon("background", self.background_color)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.foreground, 1, 0)
        grid.addWidget(self.background, 1, 1)
        
        self.setLayout(grid) 
        
        # self.setGeometry(300, 300, 350, 300)
        # self.show()