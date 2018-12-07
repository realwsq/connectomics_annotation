import cv2
import numpy as np 

import threed_to_twod

def get_all_cell_boundary(crt_label_image):
    grad = np.gradient(crt_label_image)
    if len(crt_label_image.shape) == 3:
        grad = [np.any(grad[0]!=0, axis=2), np.any(grad[1]!=0, axis=2)]
    # else:
    # 	grad = np.gradient(crt_label_image)

    bdr = np.zeros((crt_label_image.shape[0], crt_label_image.shape[1]), dtype="bool")

    bdr[grad[1]!=0] = True # gradient in raw != 0
    bdr[grad[0]!=0] = True # gradient in colume != 0

    return bdr

def get_boundary_from_threed_mask_on_view_i(threed_mask, view, detph):
	if threed_mask is None:
		return None
		
	twod_mask = threed_to_twod.get_slice_from_cube(threed_mask, view, detph)
	# contours, _ = cv2.findContours(twod_mask.astype('uint8'), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	# print contours, len(contours), contours[0], contours[0].shape
	# return contours.sum(0)
	return get_all_cell_boundary(twod_mask.astype('uint8'))
	# return cv2.Canny(twod_mask.astype('uint8'), 0, 0)>0 

