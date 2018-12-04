
from paintingParameters import painting_parameters

import sys
sys.path.insert(0, '../data_manage')
from data_manage.sliceInteractionInterface import annotate_interface

import cv2
import numpy as np

# overlay label on sem img
def _get_cube_and_label_nparray(sem_img, label_img):
	label_transparency = painting_parameters.label_transparency
	return cv2.addWeighted(sem_img, 1-label_transparency, label_img, label_transparency, 0)

# draw all the boundary on a mask
# (mask means a boolean matrix)
def _get_boundary_opacity_nparray(common_bdr_mask, special_bdr_mask, datum_mask): 
	bon = np.zeros(common_bdr_mask.shape, dtype='float32')

	bon = bon + datum_mask * 1.0

	if painting_parameters.common_cell_boundary_visible:
		bon = bon + common_bdr_mask * painting_parameters.common_cell_boundary_opacity
	if painting_parameters.special_cell_boundary_visible:
		bon = bon + special_bdr_mask * painting_parameters.special_cell_boundary_opacity

	bon[bon>1] = 1

 	bon = bon[..., np.newaxis]
 	
	return np.dstack((bon, bon, bon))


class Three_View_Images():

	def __init__(self):
		self.ndarray_images = [None, None, None]

	def _assemble_special_bdr_mask_for_view_i(self, view):
		slice_data = annotate_interface.three_slices_data[view]
		selected_region_boundary = annotate_interface.get_selected_region_boundary_of_view_i_for_vis(view)
		
		h, w = annotate_interface.get_slice_shape(view)
		bdr_mask = np.zeros((h,w), dtype="bool")

		if type(selected_region_boundary) is np.ndarray:
			bdr_mask = bdr_mask | selected_region_boundary
		if type(slice_data.one_slice_of_selected_cell_boundary) is np.ndarray:
			bdr_mask = bdr_mask | slice_data.one_slice_of_selected_cell_boundary

		return bdr_mask

	def _assemble_datum_mask_for_view_i(self, view):
		h, w = annotate_interface.get_slice_shape(view)
		on_y, on_x = annotate_interface.get_other_two_slices_pos_from_view_i(view)

		bdr_mask = np.zeros((h,w), dtype="bool")
		bdr_mask[on_y, :] = True
		bdr_mask[:, on_x] = True
		
		return bdr_mask

	def _update_view_i_qimage(self, view):
		slice_data = annotate_interface.three_slices_data[view]

		cube_and_label_nparray = _get_cube_and_label_nparray(slice_data.sem_img, slice_data.label_img) # [h * w * 3]
		boundary_opacity_nparray = _get_boundary_opacity_nparray(slice_data.all_cells_bdr_img,  
																 self._assemble_special_bdr_mask_for_view_i(view),
																 self._assemble_datum_mask_for_view_i(view)) # [h * w * 3]
		image_to_draw = (cube_and_label_nparray * (1-boundary_opacity_nparray)).astype('uint8') # boundary is (0,0,0)

		if view == 0:
			image_to_draw = image_to_draw.transpose((1,0,2))

		self.ndarray_images[view] = image_to_draw

	def _update_three_view_qimages(self):
		[self._update_view_i_qimage(i) for i in range(3)]

	def init(self):
		self._update_three_view_qimages()

	def update(self, view=None):
		if view == None:
			self._update_three_view_qimages()
		else:
			self._update_view_i_qimage(view)

			
three_view_images_display_manager = Three_View_Images()