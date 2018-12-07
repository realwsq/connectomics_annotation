import numpy as np 

import utils

'''
get slice from cube from view #view at depth #depth
'''
def get_slice_from_cube(cube, view, depth):
	if cube is None:
		return None
		
	if view == 0:
		return cube[depth, :, :]
	elif view == 1:
		return cube[:, depth, :]
	elif view == 2:
		return cube[:, :, depth]

'''
set slice to cube from view #view at depth #depth
'''
def set_slice_to_cube(cube, slc, view, depth):
	if view == 0:
		cube[depth, :, :] = slc
	elif view == 1:
		cube[:, depth, :] = slc
	elif view == 2:
		cube[:, :, depth] = slc
	return cube

'''
input: [min_h,max_h,min_w,max_w,min_z,max_z], cube
'''
def get_cube_surface(vtx, cube):
	min_h, max_h, min_w, max_w, min_z, max_z = vtx
	h, w, d = cube.shape
	min_h = utils.confine_value(min_h, (0, h-1))
	max_h = utils.confine_value(max_h, (0, h-1))
	min_w = utils.confine_value(min_w, (0, w-1))
	max_w = utils.confine_value(max_w, (0, w-1))
	min_z = utils.confine_value(min_z, (0, d-1))
	max_z = utils.confine_value(max_z, (0, d-1))
	return [cube[slice(min_h,min_h+1), slice(min_w, max_w+1), slice(min_z, max_z+1)],
			cube[slice(max_h,max_h+1), slice(min_w, max_w+1), slice(min_z, max_z+1)],
			cube[slice(min_h,max_h+1), slice(min_w, min_w+1), slice(min_z, max_z+1)],
			cube[slice(min_h,max_h+1), slice(max_w, max_w+1), slice(min_z, max_z+1)],
			cube[slice(min_h,max_h+1), slice(min_w, max_w+1), slice(min_z, min_z+1)],
			cube[slice(min_h,max_h+1), slice(min_w, max_w+1), slice(max_z, max_z+1)]]