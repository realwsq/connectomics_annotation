import numpy as np
from skimage.measure import label 
from skimage.measure import regionprops
from tqdm import tqdm
import time

from cubeInteractionInterface import Cube_Interaction_Interface

import sys
sys.path.insert(0, '../helper')
import helper.utils as utils
import helper.threed_to_twod as threed_to_twod
import helper.mask_and_boundary_related as mask_and_boundary_related

class Slice_Data():

	def __init__(self, view):
		self.this_view = view
		self.label_slice = None
		self.label_img = None
		self.sem_img = None
		self.all_cells_bdr_img = None
		self.one_slice_of_selected_cell_boundary = None
		

class Slice_Interaction_Interface(Cube_Interaction_Interface):
	
	# regardless of action
	_crt_draw_view = -1 # 0: top  1: right  2: front
	_draw_points = [] 	# be VERY CAREFUL that it's [x, y] 
	_selected_region_label = None # mask with label
	_selected_region_mask = None
	_selected_region_boundary = None

	three_slices_data = [Slice_Data(0), Slice_Data(1), Slice_Data(2)]

	# TODO! 
	# idle, merging
	_state = "idle"

	# clear all that because of drawing (on particular slice and on particular view)
	def _clear_all__drawed(self):
		self._crt_draw_view = -1 # 0: top  1: right  2: front
		self._draw_points = [] 	# be VERY CAREFUL that it's [x, y] 
		self._selected_region_label = None # mask with label
		self._selected_region_mask = None
		# self._selected_region_boundary = None

	def _valid_coord(self, x, y, shape):
		if x < 0 or x >= shape[1]:
			return False
		if y < 0 or y >= shape[0]:
			return False
		return True

	# center changed, we need to do something related to the last particular slice
	# i.e., clear all things
	def _update_slice_related__center_changed(self):
		self._clear_all__drawed()

	# center changed, we need to update all the global things to this particular slice
	def _update_slice_data_from_view_i__all(self, view):
		self.three_slices_data[view].label_slice = self._get_label_slice(view, self._center_point[view])
		self.three_slices_data[view].label_img = utils.label_to_rgb_ndarray(self.three_slices_data[view].label_slice)
		self.three_slices_data[view].all_cells_bdr_img = mask_and_boundary_related.get_all_cell_boundary(self.three_slices_data[view].label_img)
		# self.three_slices_data[view].all_cells_bdr_img = (self.three_slices_data[view].label_slice == 0)
		_sem = self._get_sem_slice(view, self._center_point[view])
		self.three_slices_data[view].sem_img = np.dstack((_sem, _sem, _sem))
		self.three_slices_data[view].one_slice_of_selected_cell_boundary = mask_and_boundary_related.get_boundary_from_threed_mask_on_view_i(self._selected_cell_mask, view, self._center_point[view])
		
	# selected cell changed, we need to update one_slice_of_selected_cell_boundary
	def _update_slice_data_from_view_i__selected_cell_changed(self, view):
		self.three_slices_data[view].one_slice_of_selected_cell_boundary = mask_and_boundary_related.get_boundary_from_threed_mask_on_view_i(self._selected_cell_mask, view, self._center_point[view])

	def _update_global_related__center_changed(self):
		[self._update_slice_data_from_view_i__all(i) for i in range(3)]

	def _update_global_related__selected_cell_changed(self):
		[self._update_slice_data_from_view_i__selected_cell_changed(i) for i in range(3)]

	def _update_global_related__label_changed(self):
		[self._update_slice_data_from_view_i__all(i) for i in range(3)]

	# get the _selected_cell_label, update _selected_cell_mask and _selected_cell_boundary accordingly
	def _get_selected_cell_mask__label_changed(self):
		if self._selected_cell_label:
			self._selected_cell_mask = self._label_cube_data == self._selected_cell_label

	def _correct_label(self, mode, coords):
		coords = np.asarray(coords)
		if coords.shape[0] == 0:
			return

		def _get_swaps(padding):
			surface_slice = threed_to_twod.get_cube_surface(
				[np.min(coords[:, 0])-padding, 
				np.max(coords[:, 0])+padding,
				np.min(coords[:,1])-padding,
				np.max(coords[:,1])+padding,
				np.min(coords[:,2])-padding,
				np.max(coords[:,2])+padding],
				self._label_cube_data)
			swaps = []
			for sf in surface_slice:
				swaps = np.concatenate((swaps, sf.reshape(-1)))
			return swaps

		if mode == "node":
			# print coords[0]
			# padding = 1
			# while True:
			# 	swaps = _get_swaps(padding)
			# 	if np.all(swaps == 0):
			# 		padding = padding+1
			# 	else:
			# 		swaps = swaps[swaps != 0]
			# 		break
			padded_label_cube = np.zeros((self._cube_shape[0]+2,self._cube_shape[1]+2, self._cube_shape[2]+2), dtype=self._label_cube_data.dtype)
			padded_label_cube[1:-1,1:-1,1:-1] = self._label_cube_data
			coord_num = coords[0].shape[0]			
			for node_i in range(coord_num):
				x, y, z = coords[0][node_i], coords[1][node_i], coords[2][node_i]
				swaps = padded_label_cube[x:x+3,y:y+3,z:z+3]
				swaps = swaps[swaps!=0]
				swap = utils.most_frequent(swaps)
				if swap:
					self._label_cube_data[x,y,z] = swap
		elif mode == "region":
			swaps = _get_swaps(0)
			swap = utils.most_frequent(swaps)
			for coord in coords:
				self._label_cube_data[coord[0], coord[1], coord[2]] = swap

	def init(self, cube_raw, labels_raw):
		super(Slice_Interaction_Interface, self).init(cube_raw, labels_raw)
		self._update_slice_related__center_changed() # draw (one slice)
		self._update_global_related__center_changed() # 

	# _bdr_cube_data won't update regularly
	# only update when the GUI comes to membrain_edition mode
	def init_bdr_cube_data(self):
		self._get_bdr_cube_data()

	def get_bdr_img_of_view_i(self, view):
		return self._get_bdr_slice(view, self._center_point[view])

	def update_z_index_by_steps(self, steps, view):
		target_depth = self._center_point[view] + steps
		if target_depth < 0:
			target_depth = 0
		elif target_depth >= self._cube_shape[view]:
			target_depth = self._cube_shape[view]-1
		
		self._center_point[view] = target_depth

		self._update_slice_related__center_changed()
		self._update_global_related__center_changed()

	def relocate_center(self, x, y, view):
		if view == 0:
			self._center_point = [self._center_point[0], y, x]
		elif view == 1:
			self._center_point = [y, self._center_point[1], x]
		elif view == 2:
			self._center_point = [y, x, self._center_point[2]]

		self._update_slice_related__center_changed()
		self._update_global_related__center_changed()

	def select_host_cell_for_global_merge(self, x, y, view):
		if not self._valid_coord(x, y, self.three_slices_data[view].label_slice.shape):
			return
			
		self._clear_all__drawed()
		self._state = "merging"

		self._selected_cell_label = self.three_slices_data[view].label_slice[y, x]
		print "this cells label: " + str(self._selected_cell_label) + "!!"

		self._get_selected_cell_mask__label_changed()

		self._update_global_related__selected_cell_changed()

	def fuse_this_cell_with_host_cell(self, x, y, view):
		if not self._valid_coord(x, y, self.three_slices_data[view].label_slice.shape):
			return		

		if self._selected_cell_label == None:
			# no receive cell
			return
		selected_label = self.three_slices_data[view].label_slice[y, x]

		if selected_label == self._selected_cell_label:
			# no need to merge
			return

		# merge cells
		host_cell_label = self._selected_cell_label
		selected_cell_mask_cube = self._label_cube_data == selected_label 
		# update the second cell with the first cell's label in the whole cube
		self._replace_cell_with_another_label(selected_cell_mask_cube, host_cell_label)

		self._get_selected_cell_mask__label_changed()
		self._update_global_related__label_changed()

		# log the annotation history
		self._annotation_history.enqueue([selected_cell_mask_cube*selected_label])

	def add_node_on_bdr_cube_data_of_view_i(self, x, y, view):
		if not self._valid_coord(x, y, self.three_slices_data[view].label_slice.shape):
			return
			
		if view == 0:
			self._bdr_cube_data[self._center_point[0], y, x] = True
		elif view == 1:
			self._bdr_cube_data[y, self._center_point[1], x] = True
		elif view == 2:
			self._bdr_cube_data[y, x, self._center_point[2]] = True

	def erase_node_on_bdr_cube_data_of_view_i(self, x, y, view, r):
		image_shape = self.three_slices_data[view].label_slice.shape
		if not self._valid_coord(x, y, image_shape):
			return

		if view == 0:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					self._bdr_cube_data[self._center_point[0], y+j, x+i] = False
		elif view == 1:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					self._bdr_cube_data[y+j, self._center_point[1], x+i] = False
		elif view == 2:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					self._bdr_cube_data[y+j, x+i, self._center_point[2]] = False

	def flood_fill_from_membrane_cube_data(self):
		self._label_cube_data, label_num = label(self._bdr_cube_data, connectivity=1, background=1, return_num=True)
		bdr_coords = np.where(self._label_cube_data == 0)
		bdr_num = bdr_coords[0].shape[0]
		while bdr_num != 0:
			print "round: "+str(bdr_num)
			self._correct_label('node', bdr_coords)
			bdr_coords = np.where(self._label_cube_data == 0)
			bdr_num = bdr_coords[0].shape[0]
		# [self._correct_label("node", [[bdr_coords[0][i], bdr_coords[1][i], bdr_coords[2][i]]]) for i in range(bdr_coords[0].shape[0])]
		self._update_global_related__label_changed()

	def clear_small_fragments(self, threshold):
		# mode = 'reassign'  # 'remove' or 'reassign'
		
		# if mode == 'remove':
		# 	segments = morphology.remove_small_objects(segments, min_size=threshold)
		# else:

		props = np.asarray(regionprops(self._label_cube_data))
		areas = np.asarray([x.area for x in props])
		reassign = np.where(areas < threshold)[0]
		[self._correct_label("region", props[pidx].coords) for pidx in reassign]

		self._update_global_related__label_changed()

	def undo_one_annotation_history(self):
		if self._annotation_history.size <= 0:
			return
		history = self._annotation_history.dequeue()
		mask = history[0]
		# label_after = history[1]
		# update the cell with the previous label in the whole cube
		self._replace_mask_with_another_mask(mask)
		# update the visualization
		self._get_selected_cell_mask__label_changed()
		self._update_global_related__label_changed()

	def get_label_cube_data(self):
		return self._label_cube_data
		
	# return the boundary mask of hand-drawing on the particular view
	def get_selected_region_boundary_of_view_i_for_vis(self, view):
		if self._crt_draw_view == view:
			return self._selected_region_boundary
		else:
			return None

	def get_selected_cell_label(self):
		return self._selected_cell_label

	def get_slice_shape(self, view):
		return self.three_slices_data[view].label_slice.shape
		
	def get_other_two_slices_pos_from_view_i(self, view):
		center_x = 0
		center_y = 0
		if view == 0:
			center_x = self._center_point[2]
			center_y = self._center_point[1]
		elif view == 1:
			center_x = self._center_point[2]
			center_y = self._center_point[0]
		elif view == 2:
			center_x = self._center_point[1]
			center_y = self._center_point[0]
		return [center_y, center_x]

annotate_interface = Slice_Interaction_Interface()