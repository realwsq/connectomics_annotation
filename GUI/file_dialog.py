from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

class File_Dialog(QWidget):
    # def __init__(self, sem, lab, output_folder, parent = None):
    def __init__(self, parent = None):
        super(File_Dialog, self).__init__(parent)

        # self.sem_file = sem
        # self.lab_file = lab
        # self.output_folder = output_folder
        self.done = False

        layout = QVBoxLayout()
        self.sem_btn = QPushButton("select sem data")
        self.sem_btn.clicked.connect(self.get_sem_file)
        layout.addWidget(self.sem_btn)

        self.lab_btn = QPushButton("select label data")
        self.lab_btn.clicked.connect(self.get_lab_file)
        layout.addWidget(self.lab_btn)

        self.of_btn = QPushButton("select output folder")
        self.of_btn.clicked.connect(self.get_output_folder)
        layout.addWidget(self.of_btn)

        # self.confirm_btn = QPushButton("done")
        # self.confirm_btn.clicked.connect(self.done_func)
        # layout.addWidget(self.confirm_btn)

        self.setLayout(layout)
        self.setWindowTitle("File Dialog demo")
        self.show()
        
    def get_sem_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
           '/media/data_cifs/shuqi/')
        self.sem_file = fname
        self.sem_btn.setEnabled(False)

    def get_lab_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 
           '/media/data_cifs/shuqi/')
        self.lab_file = fname
        self.lab_btn.setEnabled(False)
        
    def get_output_folder(self):
        print "in get output folder"
        foldername = QFileDialog.getExistingDirectory(self, 'choose a folder',
            '/media/data_cifs/shuqi/')
        self.output_folder = None
        self.of_btn.setEnabled(False)

    # def done_func(self):
    #     # sys.exit(self.exec_())
    #     self.done = True
    #     # return self.sem_file, self.lab_file, self.output_folder