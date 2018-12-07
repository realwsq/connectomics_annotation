import numpy as np
import cv2
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
		self.slice_shape = None
		self.label_slice = None
		self.label_img = None
		self.sem_img = None
		self.all_cells_bdr_mask = None # 2d bool array
		self.one_slice_of_selected_cell_boundary_mask = None # 2d bool array
		self.stroke_mask = None # 2d bool array
		

class Slice_Interaction_Interface(Cube_Interaction_Interface):
	
	# regardless of action
	_crt_draw_view = -1 # 0: top  1: right  2: front
	_draw_points = [] 	# be VERY CAREFUL that it's [x, y] 
	_selected_region_label = None # mask with label
	_selected_region_mask = None
	_selected_region_boundary = None

	three_slices_data = [Slice_Data(0), Slice_Data(1), Slice_Data(2)]

	def _update_slice_related(self, mode, *argv):
		if mode == "clear":
			# clear all slice-related
			self._crt_draw_view = -1
			self._draw_points = []
			# below all 2d array
			self._selected_region_mask = None
			self._selected_region_boundary = None
		elif mode == 'add_point':
			node = argv[0]
			self._draw_points.append(node)
		elif mode == 'assemble_selected_region':
			self._draw_points.append(self._draw_points[0])
			view = self._crt_draw_view
			drawing_region = np.zeros(self.three_slices_data[view].label_img.shape, 'uint8')
			cv2.drawContours(drawing_region, [np.array(self._draw_points)], -1, (255,255,255), thickness=-1)
			random_selection_mask = (drawing_region[:,:,0] == 255)

			crt_label_image = self.three_slices_data[view].label_slice
			if self._selected_cell_label:
				selected_cell_mask = threed_to_twod.get_slice_from_cube(self._selected_cell_mask, view, self._center_point[view])
				random_selection_mask = random_selection_mask & selected_cell_mask

			mask = np.zeros(crt_label_image.shape, 'uint16')
			mask[random_selection_mask] = crt_label_image[random_selection_mask] 
			boundary = mask_and_boundary_related.get_all_cell_boundary(random_selection_mask.astype('uint8'))
			self._selected_region_mask = mask
			self._selected_region_boundary = boundary
			self._draw_points = []
			self._update_cell_related('clear')
		elif mode == 'fuse_region':
			view = self._crt_draw_view
			depth = self._center_point[view]
			# merge the randomly selected region to this label
			label_slice = self._get_label_slice(view, depth)
			target_label = argv[0]

			print self._get_label_slice(view, depth).sum()
			label_slice[self._selected_region_mask>0] = target_label
			self._set_label_slice(label_slice, view, depth)
			print self._get_label_slice(view, depth).sum()

			selected_region_mask_cube = np.zeros(self._cube_shape, dtype = label_slice.dtype)
			selected_region_mask_cube = threed_to_twod.set_slice_to_cube(
				selected_region_mask_cube, 
				self._selected_region_mask, 
				view, depth)

			self._annotation_history.enqueue([selected_region_mask_cube])



	def _update_slice_data(self, mode):
		# 1. reset label + sem
		# 2. recalculate all_cells_bdr
		# 3. recalculate one_slice_of_selected_cell_boundary_mask
		# 4. recalculate strok_mask
		def _reset_sem_and_label():
			for view in range(3):
				lbl_slice = self._get_label_slice(view, self._center_point[view])
				lbl_img = utils.label_to_rgb_ndarray(lbl_slice)
				sem_slice = self._get_sem_slice(view, self._center_point[view])
				sem_img = np.dstack((sem_slice, sem_slice, sem_slice))

				self.three_slices_data[view].label_slice = lbl_slice
				self.three_slices_data[view].label_img = lbl_img
				self.three_slices_data[view].sem_img = sem_img
				self.three_slices_data[view].slice_shape = sem_slice.shape
		def _cal_all_cells_bdr():
			for view in range(3):
				all_cells_bdr = mask_and_boundary_related.get_all_cell_boundary(
					self.three_slices_data[view].label_slice)

				self.three_slices_data[view].all_cells_bdr_mask = all_cells_bdr
		def _cal_selected_cell_bdr():
			for view in range(3):
				slc_cell_bdr = mask_and_boundary_related.get_boundary_from_threed_mask_on_view_i(
					self._selected_cell_mask, view, self._center_point[view])

				self.three_slices_data[view].one_slice_of_selected_cell_boundary_mask = slc_cell_bdr
		def _cal_stroke_mask():
			for view in range(3):
				self.three_slices_data[view].stroke_mask = None
			if self._crt_draw_view != -1:
				stroke_mask = np.zeros(self.three_slices_data[self._crt_draw_view].slice_shape, dtype='bool')
				if type(self._selected_region_boundary) is np.ndarray:
					stroke_mask = self._selected_region_boundary | stroke_mask
				for p in self._draw_points:
					stroke_mask[p[1], p[0]] = True
				self.three_slices_data[self._crt_draw_view].stroke_mask = stroke_mask
		if mode == "all":
			# 1 + 2 + 3 + 4
			_reset_sem_and_label()
			_cal_all_cells_bdr()
			_cal_selected_cell_bdr()
			_cal_stroke_mask()
		elif mode == "cell":
			# 3
			_cal_selected_cell_bdr()
		elif mode == "slice":
			_cal_stroke_mask()
		elif mode == "user_added":
			_cal_selected_cell_bdr()
			_cal_stroke_mask()
		else:
			assert False

	def _valid_coord(self, x, y, shape):
		if x < 0 or x >= shape[1]:
			return False
		if y < 0 or y >= shape[0]:
			return False
		return True

	def _voxel_and_nearby_value_change_from_view_i(self, cube, image_shape, x, y, r, view, value):

		if view == 0:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					cube[self._center_point[0], y+j, x+i] = value
		elif view == 1:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					cube[y+j, self._center_point[1], x+i] = value
		elif view == 2:
			for i in range(-r, r+1):
				for j in range(-r, r+1):
					if not self._valid_coord(x+i, y+j, image_shape):
						continue
					cube[y+j, x+i, self._center_point[2]] = value

		return cube

	'''
		1. call _update_slice_related (clear)
		2. call _update_slice_data (all) 
	'''
	def _update_center(self):
		self._update_slice_related('clear')
		self._update_slice_data('all')

	'''
		return label, mask
	'''
	def _get_cell_label_and_mask__pixel(self, x, y, view):
		pass


	# TODO! 
	# idle, merging
	# _state = "idle"

	''' 
		1. set data
		2. reset cetner point
		3. call _update_center
	'''
	def init(self, cube_raw, labels_raw):
		super(Slice_Interaction_Interface, self).init(cube_raw, labels_raw)
		self._center_point = [self._cube_shape[0]/2, self._cube_shape[1]/2, self._cube_shape[2]/2]
		self._update_center()

	def init_membrane_cube_data(self):
		self._get_membrane_cube_data()

	def get_membrane_mask_of_view_i(self, view):
		return self._get_bdr_slice(view, self._center_point[view])

	def add_node_on_membrane_cube_data_of_view_i(self, x, y, view, r):
		image_shape = self.get_slice_shape(view)
		self._bdr_cube_data = self._voxel_and_nearby_value_change_from_view_i(
			self._bdr_cube_data, image_shape, x, y, r, view, True)

	def erase_node_on_membrane_cube_data_of_view_i(self, x, y, view, r):
		image_shape = self.get_slice_shape(view)
		self._bdr_cube_data = self._voxel_and_nearby_value_change_from_view_i(
			self._bdr_cube_data, image_shape, x, y, r, view, False)

	'''
		clear cell related and slice related
	'''
	def clear_user_added(self):
		self._update_slice_related('clear')
		self._update_cell_related('clear')
		self._update_slice_data('user_added')

	'''
		1. reset center point
		2. call _update_center
	'''
	def relocate_center(self, x, y, view):
		self.set_other_two_slices_pos_from_view_i(x, y, view)
		self._update_center()
		
	'''
		1. reset center point
		2. call _update_center
	'''
	def update_z_index_by_steps(self, steps, view):
		target_depth = self._center_point[view] + steps
		if target_depth < 0:
			target_depth = 0
		elif target_depth >= self._cube_shape[view]:
			target_depth = self._cube_shape[view]-1
		
		self._center_point[view] = target_depth
		self._update_center()

	'''
		2. update selected cell info (call _get_cell_label_and_mask__pixel)
		3. call _update_slice_data (cell)
	'''
	def select_host_cell_for_global_merge(self, x, y, view):
		selected_cell_label = self._get_label_slice(view, self._center_point[view])[y,x]
		self._update_cell_related('select_cell', selected_cell_label)
		self._update_slice_data('cell')

	'''
		1. verify (x. y)
		2. 
	'''
	def fuse_this_cell_with_host_cell(self, x, y, view):
		selected_label = self._get_label_slice(view, self._center_point[view])[y, x]
		
		self._update_cell_related('fuse_cell', selected_label)
		self._update_slice_data('all')


	def init_drawing_slice(self, view):
		self._crt_draw_view = view
		self._draw_points = []
		self._selected_region_mask = None
		self._selected_region_boundary = None
		self._update_slice_related('user_added')

	def add_node_in_draw_points(self, x, y):
		self._update_slice_related('add_point', [x, y])
		self._update_slice_data('slice')

	def finish_drawing_slice(self):
		self._update_slice_related('assemble_selected_region')
		self._update_slice_data('user_added')

	def fuse_selected_region_with_this_cell(self, x, y, view):
		selected_label = self._get_label_slice(view, self._center_point[view])[y, x]

		self._update_slice_related('fuse_region', selected_label)
		self._update_slice_data('all')


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
		self._update_slice_data('all')

	def clear_small_fragments(self, threshold):
		props = np.asarray(regionprops(self._label_cube_data))
		areas = np.asarray([x.area for x in props])
		reassign = np.where(areas < threshold)[0]
		[self._correct_label("region", props[pidx].coords) for pidx in reassign]

		self._update_slice_data('all')
	
	def undo_one_annotation_history(self):
		# print "ohh, you want to undo"
		if self._annotation_history.size <= 0:
			return
		history = self._annotation_history.dequeue()
		mask = history[0]
		# label_after = history[1]
		# update the cell with the previous label in the whole cube
		self._label_cube_data[mask>0] = mask[mask>0]
		# update the visualization
		self._update_cell_related("select_cell", self._selected_cell_label)
		self._update_slice_data('all')

	def has_selected_cell(self):
		return self._selected_cell_label

	def get_label_cube_data(self):
		return self._label_cube_data	

	def get_selected_cell_label(self):
		return self._selected_cell_label

	def get_slice_shape(self, view):
		return self.three_slices_data[view].slice_shape

	def set_other_two_slices_pos_from_view_i(self, x, y, view):
		if view == 0:
			self._center_point = [self._center_point[0], y, x]
		elif view == 1:
			self._center_point = [y, self._center_point[1], x]
		elif view == 2:
			self._center_point = [y, x, self._center_point[2]]

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