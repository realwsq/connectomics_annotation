from helper import gipl_to_npy
from helper import npy_to_gipl
from helper import for_debug
from helper import utils

from image_display.paintingParameters import painting_parameters
from image_display.image import three_view_images_display_manager
from image_display.image__membrane_edition import three_view_images_display_manager__membrane_edition

from GUI import label_slider
from GUI import foreground_and_background_color
from GUI import mode_control
from GUI import file_dialog

from data_manage.sliceInteractionInterface import annotate_interface

import sys
import os
import time
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np


class GUI_Control():
    def __init__(self):
        self.selection_modes = ["merge (global)", "split (global)", "edit one ID (slice)", "edit all IDs (slice)", "membrane edition", ]
        self.current_selection_mode = 0

GUI_control = GUI_Control()

def update_image_manager():

    if GUI_control.current_selection_mode == 4: # membrane edition
        three_view_images_display_manager__membrane_edition.update()
    else:
        three_view_images_display_manager.update()

def get_image_to_display_of_view_i(view):
    if GUI_control.current_selection_mode == 4: # membrane edition
        img = three_view_images_display_manager__membrane_edition.ndarray_images[view]
    else:
        img = three_view_images_display_manager.ndarray_images[view]
    return img

class Image_Label(QGraphicsView):

    def __init__(self, main_window_control, this_view):
        super(Image_Label, self).__init__(main_window_control)
        self.this_view = this_view  # 0: top  1: right  2: front
        self.main_window_control = main_window_control

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

        self._pan = False
        self._editing = False
        self._pan_start_x = 0
        self._pan_start_y = 0
    
    def hasPhoto(self):
        return not self._empty

    def _getXAndY_from_screen_input(self, point, correct=False):
        point = self.mapToScene(point[0], point[1])
        point = [int(round(point.x())), int(round(point.y()))]
        # point should be (x, y)
        if self.this_view == 0: # down_view: transpose:
            x = point[1]
            y = point[0]
        else:
            x = point[0]
            y = point[1]

        h, w = annotate_interface.get_slice_shape(self.this_view)

        if correct:
            y = utils.confine_value(y, (0, h-1))
            x = utils.confine_value(x, (0, w-1))
        else:
            if y < 0 or y >= h:
                return x, y, False
            if x < 0 or x >= w:
                return x, y, False

        return x, y, True 

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        # print "wheel event with modifiers " + str(modifiers)

        if bool(modifiers == Qt.NoModifier):
            # no modifer -> scroll z plane
            steps = event.delta() / 8 / 15
            annotate_interface.update_z_index_by_steps(steps, self.this_view) 
            self.main_window_control.update_images_in_image_label()
            
        elif bool(modifiers == Qt.ControlModifier):
            # ctrl + mouse wheel -> zoom the image
            if self.hasPhoto():
                if event.delta() > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.8
                    self._zoom -= 1
                self.scale(factor, factor)

    def mousePressEvent(self,event):

        modifiers = QApplication.keyboardModifiers()
        mouse_x, mouse_y, xy_valid = self._getXAndY_from_screen_input([event.x(), event.y()])
        print mouse_x, mouse_y, xy_valid

        if not xy_valid:
            event.ignore()
            return

        if event.button() == Qt.MidButton and bool(modifiers == Qt.NoModifier):
            # pan
            self._pan = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            # self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        elif event.button() == Qt.MidButton and bool(modifiers == Qt.ControlModifier):
            annotate_interface.relocate_center(mouse_x, mouse_y, self.this_view)
            self.main_window_control.update_images_in_image_label()
        elif event.button() == Qt.LeftButton and bool(modifiers == Qt.NoModifier):
            if GUI_control.current_selection_mode == 0: # merge all
                # select host ID
                annotate_interface.select_host_cell_for_global_merge(
                    mouse_x, mouse_y, 
                    self.this_view)
                self.main_window_control.control_window.set_foreground_color(
                    utils.label_to_rgb(annotate_interface.get_selected_cell_label()))
                self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 4: # membrane_edition
                self._editing = True
                # add membrane
                annotate_interface.add_node_on_membrane_cube_data_of_view_i(
                    mouse_x, mouse_y, 
                    self.this_view,
                    painting_parameters.membrane_edition_stroke_width)
                self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 2: # edit one ID (slice)
                annotate_interface.select_host_cell_for_global_merge(
                    mouse_x, mouse_y,
                    self.this_view)
                self.main_window_control.control_window.set_background_color(
                    utils.label_to_rgb(annotate_interface.get_selected_cell_label()))
                self.main_window_control.update_images_in_image_label()
            event.accept()
            return
        elif event.button() == Qt.LeftButton and bool(modifiers == Qt.ControlModifier):
            if GUI_control.current_selection_mode == 4: # membrane_edition
                self._editing = True
                # erase membrane
                annotate_interface.erase_node_on_membrane_cube_data_of_view_i(
                    mouse_x, mouse_y, 
                    self.this_view,
                    painting_parameters.membrane_edition_stroke_width)
                self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 2 or GUI_control.current_selection_mode == 3:
                annotate_interface.fuse_selected_region_with_this_cell(
                    mouse_x, mouse_y,
                    self.this_view)
                self.main_window_control.update_images_in_image_label()
            event.accept()
            return
        elif event.button() == Qt.RightButton and bool(modifiers == Qt.NoModifier):
            if GUI_control.current_selection_mode == 0: # merge all
                if not annotate_interface.has_selected_cell():
                    return
                annotate_interface.fuse_this_cell_with_host_cell(
                    mouse_x, mouse_y, 
                    self.this_view)
                self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 2: # edit one ID (slice)
                if not annotate_interface.has_selected_cell():
                    return 
                self._editing = True
                annotate_interface.init_drawing_slice(self.this_view)
                annotate_interface.add_node_in_draw_points(mouse_x, mouse_y)
                self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 3: # edit all ID (slice)
                self._editing = True
                annotate_interface.init_drawing_slice(self.this_view)
                annotate_interface.add_node_in_draw_points(mouse_x, mouse_y)
                self.main_window_control.update_images_in_image_label()
            event.accept()
            return

        event.ignore()

    def mouseReleaseEvent(self,event):
        modifiers = QApplication.keyboardModifiers()
        mouse_x, mouse_y, xy_valid = self._getXAndY_from_screen_input([event.x(), event.y()], True)

        if not xy_valid:
            event.ignore()
            return

        if event.button() == Qt.MidButton and bool(modifiers == Qt.NoModifier):
            # pan
            self._pan = False
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            # self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        elif self._editing:
            self._editing = False
            if (GUI_control.current_selection_mode == 4 and (bool(modifiers == Qt.NoModifier) or bool(modifiers == Qt.ControlModifier))):
                pass
            elif (GUI_control.current_selection_mode == 2 and (bool(modifiers == Qt.NoModifier))) or (GUI_control.current_selection_mode == 3 and (bool(modifiers == Qt.NoModifier))):
                annotate_interface.finish_drawing_slice()
                self.main_window_control.update_images_in_image_label()
            
            event.accept()
            return


        event.ignore()

    def mouseMoveEvent(self,event):
        modifiers = QApplication.keyboardModifiers()
        mouse_x, mouse_y, xy_valid = self._getXAndY_from_screen_input([event.x(), event.y()], True)
        
        if not xy_valid:
            event.ignore()
            return
            
        if self._pan:
            # pan
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 7 * (event.x() - self._pan_start_x));
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 7 * (event.y() - self._pan_start_y));
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            event.accept();
            return
            
        if self._editing:
            if GUI_control.current_selection_mode == 4: # membrane_edition
                if bool(modifiers == Qt.NoModifier):
                    # add membrane
                    annotate_interface.add_node_on_membrane_cube_data_of_view_i(
                        mouse_x, mouse_y, 
                        self.this_view,
                        painting_parameters.membrane_edition_stroke_width)
                    self.main_window_control.update_images_in_image_label()
                elif bool(modifiers == Qt.ControlModifier):
                    # erase membrane
                    annotate_interface.erase_node_on_membrane_cube_data_of_view_i(
                        mouse_x, mouse_y, 
                        self.this_view,
                        painting_parameters.membrane_edition_stroke_width)
                    self.main_window_control.update_images_in_image_label()
            elif GUI_control.current_selection_mode == 2 or GUI_control.current_selection_mode == 3:
                annotate_interface.add_node_in_draw_points(mouse_x, mouse_y)
                self.main_window_control.update_images_in_image_label()
            else:
                assert False

            event.accept();
            return

        event.ignore()            

    def _set_image(self, pixmap):
        # self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            print "why we don't have pixmap!!!"
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        
    def _clean_all(self):
        self._scene.clear()

    def update_image(self):
        # print "in paintevent, the event is: "
        # print event

        self._clean_all()
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)

        image_to_draw = get_image_to_display_of_view_i(self.this_view)

        im = np.require(image_to_draw, np.uint8, 'C')
        qimage = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888)

        self._set_image(QPixmap.fromImage(qimage))


class Control_Window(QWidget):
    def __init__(self, main_window_control):
        super(Control_Window, self).__init__(main_window_control)

        self.main_window_control = main_window_control
        self.selection_modes = GUI_control.selection_modes
        self.initUI()

    def _label_opacity_changed(self, label_opacity_value):
        print "label opacity changed to " + str(label_opacity_value)
        painting_parameters.label_transparency = label_opacity_value/100.0
        self.main_window_control.update_images_in_image_label()
        
    def _selected_cell_boundary_opacity_changed(self, selected_cell_boundary_opacity):
        painting_parameters.special_cell_boundary_opacity = selected_cell_boundary_opacity/100.0
        self.main_window_control.update_images_in_image_label()

    def _boundary_opacity_changed(self, cell_boundary_opacity):
        painting_parameters.common_cell_boundary_opacity = cell_boundary_opacity/100.0
        self.main_window_control.update_images_in_image_label()

    def _selection_mode_changed(self, selection_mode):
        print "selection mode changed to " + str(selection_mode)
        GUI_control.current_selection_mode = selection_mode
        annotate_interface.clear_user_added()
        self.set_foreground_color(
                    [255,255,255])
        self.set_background_color(
                    [255,255,255])
                
        if selection_mode == 4: # membrane_edition
            annotate_interface.init_membrane_cube_data()
        self.main_window_control.update_images_in_image_label()

    def _fg_thres_changed(self, fg_thres):
        print "fg thres changed to " + str(fg_thres)

    def _fg_erode_itr_changed(self, fg_erode_itr):
        print "fg erode itr changed to " + str(fg_erode_itr)

    def _erase_stroke_changed(self, stroke_width):
        painting_parameters.membrane_edition_stroke_width = stroke_width
        
    def set_foreground_color(self, rgb):
        self.label_color_control.set_foreground_color(QColor(rgb[0], rgb[1], rgb[2]))

    def set_background_color(self, rgb):
        self.label_color_control.set_background_color(QColor(rgb[0], rgb[1], rgb[2]))

        
    def initUI(self):
        
        self.label_opacity = label_slider.Label_Slider(
            'label opacity%', 
            0, 100, 40, 
            self._label_opacity_changed)
        self.selected_cell_boundary_width = label_slider.Label_Slider(
            'selected cell outline opacity', 
            0, 100, 100, 
            self._selected_cell_boundary_opacity_changed)
        self.boundary_opacity = label_slider.Label_Slider(
            'outline opacity', 
            0, 100, 50, 
            self._boundary_opacity_changed)
        self.label_color_control = foreground_and_background_color.Foreground_and_Background_Color(QColor(255,255,255), QColor(255,255,255))
        self.mode_control = mode_control.Mode_Control(
            self.selection_modes, 
            self._selection_mode_changed)
        # self.draw_width__manipulating = label_slider.Label_Slider(
        #     'draw width when manipulating cell boundary', 
        #     1, 10, 3,
        #     self.notify_draw_width__manipulating__change)
        self.fg_thres_control = label_slider.Label_Slider(
            'fg thres', 
            200, 255, 254, 
            self._fg_thres_changed)
        self.fg_erode_itr_control = label_slider.Label_Slider(
            'fg erode iterations', 
            0, 10, 4, 
            self._fg_erode_itr_changed)
        self.erase_stroke_control = label_slider.Label_Slider(
            'stroke width', 
            0, 5, 1, 
            self._erase_stroke_changed)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        self.grid.addWidget(self.label_opacity, 2, 0)
        self.grid.addWidget(self.selected_cell_boundary_width, 3, 0)
        self.grid.addWidget(self.boundary_opacity, 4, 0)
        self.grid.addWidget(self.label_color_control, 5, 0)
        self.grid.addWidget(self.mode_control, 6, 0)
        # self.grid.addWidget(self.draw_width__manipulating, 7, 0)
        self.grid.addWidget(self.fg_thres_control, 7, 0)
        self.grid.addWidget(self.fg_erode_itr_control, 8, 0)
        self.grid.addWidget(self.erase_stroke_control, 9, 0)

        
        self.setLayout(self.grid) 


class Main_Window(QWidget):
    def __init__(self, output_folder):
        super(Main_Window, self).__init__()

        self.output_folder = output_folder

        self.setFocusPolicy( Qt.StrongFocus)

        self.initUI()

    def keyPressEvent(self, event):
        # c = event.text()
        modifiers = QApplication.keyboardModifiers()
        if (bool(modifiers == Qt.ControlModifier)) and (event.key() == Qt.Key_B):
            print 'ctrl+b pressed, undo'
            annotate_interface.undo_one_annotation_history()
            self.update_images_in_image_label()
        elif (bool(modifiers == Qt.ControlModifier)) and (event.key() == Qt.Key_S):
            print 'ctrl+s pressed'
            os.chdir(self.output_folder)
            file_ = 'annotated_segs_'+time.strftime("%Y%m%d_%H%M%S")
            file_npy = file_+'.npy'
            file_gipl = file_+'.gipl'
            np.save(file_npy, annotate_interface.get_label_cube_data())
            npy_to_gipl.main(file_npy, file_gipl)
            os.remove(file_npy)
        elif (bool(modifiers == Qt.ControlModifier)) and (event.key() == Qt.Key_D):
            print 'ctrl+d pressed'
            annotate_interface.flood_fill_from_membrane_cube_data()
            self.control_window.mode_control.cb.setCurrentIndex(0)
        elif (bool(modifiers == Qt.ControlModifier)) and (event.key() == Qt.Key_C):
            print 'ctrl+c pressed'
            annotate_interface.clear_small_fragments(1000)
            self.update_images_in_image_label()
        elif (bool(modifiers == Qt.NoModifier)) and (event.key() == Qt.Key_Q):
            print 'q pressed'
            painting_parameters.special_cell_boundary_visible = not painting_parameters.special_cell_boundary_visible
        elif (bool(modifiers == Qt.NoModifier)) and (event.key() == Qt.Key_W):
            print 'w pressed'
            painting_parameters.common_cell_boundary_visible = not painting_parameters.common_cell_boundary_visible

    def update_images_in_image_label(self):
        update_image_manager()
        self.down_view.update_image()
        self.right_view.update_image()
        self.front_view.update_image()

    def initUI(self):

        self.control_window = Control_Window(self)
        self.down_view = Image_Label(self, 0)
        self.right_view = Image_Label(self, 1)
        self.front_view = Image_Label(self, 2)


        grid = QGridLayout()
        grid.setSpacing(2)

        grid.addWidget(self.front_view, 1, 0)
        grid.addWidget(self.right_view, 1, 1)
        grid.addWidget(self.down_view, 2, 0)
        grid.addWidget(self.control_window, 2, 1)
        
        self.setLayout(grid)
        
        # self.setGeometry(500, 300, 1600, 1200)
        self.setWindowTitle('Main Window')    

        # three_view_images_display_manager.update()
        # three_view_images_display_manager__membrane_edition.update()
        # don't need to call annotation_interface.init_bdr_cube_data 
        # because _bdr_cube_data will be initialized when construct annotation_interface
        self.update_images_in_image_label()

        self.show()




def main(*argv): # sem, lab, output_folder
    # # Create an PyQT4 application object.
    # a = QApplication(sys.argv) 
     
    # # The QWidget widget is the base class of all user interface objects in PyQt4.
    # w = QWidget() 
    
    
    if len(argv) == 0:
        app = QApplication(sys.argv)
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        fd = file_dialog.File_Dialog()
        # while not fd.done:
        #     continue

        app.exec_()
        sem = str(fd.sem_file)
        lab = str(fd.lab_file)
        output_folder = str(fd.output_folder)
        print "get all needed folder"

    elif len(argv) == 3:
        sem = argv[0]
        lab = argv[1]
        output_folder = argv[2]
    else:
        sys.exit(1)

    if sem[-4:]==".npy":
        sem_raw_data_file = str(sem)
        sem_raw_data = np.load(sem_raw_data_file)#['volume'].astype('uint8')#[:,:192,:]
    else:
        sem_raw_data_file_gipl = str(sem)
        sem_raw_data_file = os.path.join(output_folder, 'cub.npy')

        # convert from gipl to npy
        gipl_to_npy.main(sem_raw_data_file_gipl, sem_raw_data_file)

        # readin file
        sem_raw_data = np.load(sem_raw_data_file)

        # delete npy file
        os.remove(sem_raw_data_file)

    if lab[-4:]==".npy":
        label_raw_data_file = str(lab)
        label_raw_data = np.load(label_raw_data_file)
    else:
        label_raw_data_file_gipl = str(lab)
        label_raw_data_file = os.path.join(output_folder, 'lab.npy')
        gipl_to_npy.main(label_raw_data_file_gipl, label_raw_data_file)
        label_raw_data = np.load(label_raw_data_file)#[:,:192,:]
        os.remove(label_raw_data_file)


    # here we transpose! to put the cube landscape
    sem_raw_data = sem_raw_data.transpose((1,0,2))
    label_raw_data = label_raw_data.transpose((1,0,2))
    
    for_debug.print_nparray_info("sem_raw_data", sem_raw_data.shape, sem_raw_data.dtype)
    for_debug.print_nparray_info("label_raw_data", label_raw_data.shape, label_raw_data.dtype)
    print "origin label num: " + str((np.unique(label_raw_data).shape))
    # ! shape (768, 384, 384) ~ (h, w, depth)
    # .reshape((768,384,384))

        

    app_main = QApplication(sys.argv)
    QApplication.setOverrideCursor(Qt.ArrowCursor)

    annotate_interface.init(sem_raw_data, label_raw_data)
    # painter = QPainter()
    main_window = Main_Window(output_folder)

    sys.exit(app_main.exec_())