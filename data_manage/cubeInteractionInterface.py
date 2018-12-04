import numpy as np 

from dataset import Sem_And_Label_Data

class Cube_Interaction_Interface(Sem_And_Label_Data):
	_center_point = [0, 0, 0]

	# regardless of action
	# _selected_cell_slice = None # in order to save the memory
	_selected_cell_label = None # mask with label
	_selected_cell_mask = None
	# _selected_cell_boundary = None

	def init(self, cube_raw, labels_raw):
		super(Cube_Interaction_Interface, self).init(cube_raw, labels_raw)
		self._center_point = [self._cube_shape[0]/2, self._cube_shape[1]/2, self._cube_shape[2]/2]