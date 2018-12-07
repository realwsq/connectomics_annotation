import numpy as np 

from dataset import Sem_And_Label_Data

class Cube_Interaction_Interface(Sem_And_Label_Data):
	_center_point = [0, 0, 0]

	# regardless of action
	# _selected_cell_slice = None # in order to save the memory
	_selected_cell_label = None # None or number
	_selected_cell_mask = None
	# _selected_cell_boundary = None

	def init(self, cube_raw, labels_raw):
		super(Cube_Interaction_Interface, self).init(cube_raw, labels_raw)
		# self._center_point = [self._cube_shape[0]/2, self._cube_shape[1]/2, self._cube_shape[2]/2]

	def _update_cell_related(self, mode, *argv):
		if mode == 'clear':
			# clear all selected_cell related
			# below all 3d array
			self._selected_cell_label = None
			self._selected_cell_mask = None
		elif mode == 'select_cell':
			label = argv[0]
			self._selected_cell_label = label
			self._selected_cell_mask = (self._label_cube_data == label)
		elif mode == 'fuse_cell':
			selected_label = argv[0]
			receive_cell_label = self._selected_cell_label
			if selected_label == receive_cell_label:
				# no need to merge
				return

			# merge cells
			selected_cell_mask_cube = (self._label_cube_data == selected_label) 
			self._replace_cell_with_another_label(selected_cell_mask_cube, receive_cell_label)

			self._update_cell_related('select_cell', receive_cell_label)

			self._annotation_history.enqueue([selected_cell_mask_cube*selected_label])
