# data_manage.dataset.py
import numpy as np 
from skimage.morphology import closing

import sys
sys.path.insert(0, '../helper')
import helper.threed_to_twod as threed_to_twod
import helper.mask_and_boundary_related as mask_and_boundary_related
import helper.utils as utils

class Stack:

    #Constructor
    def __init__(self, size):
        self.maxSize = size
        self.size = 0
        self.head = 0
        self.tail = 0
        self.stack = [None]*self.maxSize

    #Adding elements to the stack
    def enqueue(self,data):
        if self.size == self.maxSize:
            self.stack[self.head] = data
            self.head = (self.head + 1) % self.maxSize
            self.tail = (self.tail + 1) % self.maxSize
        else:
            self.stack[self.tail] = data
            self.tail = (self.tail + 1) % self.maxSize
            self.size = self.size + 1
        print self.head, self.tail
        return True

    #Removing elements from the stack
    def dequeue(self):
        if self.size == 0:
            return ("stack Empty!") 
        self.tail = (self.tail - 1 + self.maxSize) % self.maxSize
        data = self.stack[self.tail]
        self.size = self.size - 1
        print self.head, self.tail
        return data

        
class Sem_And_Label_Data(object):
	_label_cube_data = None		# int32
	_sem_cube_data = None		# uint8

	_bdr_cube_data = None		# bool (h,w,z,3)
								# won't update regularly
								# only update when the GUI comes to membrain_edition mode
	
	_cube_shape = None	

	_annotation_history = Stack(8)

	def init(self, cube_raw, labels_raw):

		assert cube_raw.shape == labels_raw.shape

		self._sem_cube_data = cube_raw
		self._cube_shape = cube_raw.shape

		self._label_cube_data = labels_raw
		
		self._get_bdr_cube_data()


	def _get_bdr_cube_data(self):
		self._bdr_cube_data = np.zeros(self._cube_shape, dtype='bool')
		for i in range(self._cube_shape[0]):
			bdr_slice = mask_and_boundary_related.get_all_cell_boundary(utils.label_to_rgb_ndarray(self._label_cube_data[i, :, :]))
			self._bdr_cube_data[i, :, :] = self._bdr_cube_data[i, :, :] | closing(bdr_slice)
		for i in range(self._cube_shape[1]):
			bdr_slice = mask_and_boundary_related.get_all_cell_boundary(utils.label_to_rgb_ndarray(self._label_cube_data[:, i, :]))
			self._bdr_cube_data[:, i, :] = self._bdr_cube_data[:, i, :] | closing(bdr_slice)
		for i in range(self._cube_shape[2]):
			bdr_slice = mask_and_boundary_related.get_all_cell_boundary(utils.label_to_rgb_ndarray(self._label_cube_data[:, :, i]))
			self._bdr_cube_data[:, :, i] = self._bdr_cube_data[:, :, i] | closing(bdr_slice)

	def _get_label_slice(self, view, depth):
		return threed_to_twod.get_slice_from_cube(self._label_cube_data, view, depth)

	def _get_sem_slice(self, view, depth):
		return threed_to_twod.get_slice_from_cube(self._sem_cube_data, view, depth)

	def _get_bdr_slice(self, view, depth):
		return threed_to_twod.get_slice_from_cube(self._bdr_cube_data, view, depth)
	
	def _replace_cell_with_another_label(self, mask, new_label):
		# self._label_cube_data[mask] = new_label		
		self._replace_mask_with_another_mask(mask*new_label)

	def _replace_mask_with_another_mask(self, new_mask):
		self._label_cube_data[new_mask>0] = new_mask[new_mask>0]