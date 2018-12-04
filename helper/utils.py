import numpy as np 


'''
input: ndarray of uint16
output: [r, g, b]
'''
def label_to_rgb_ndarray(lbl):
	r = (((lbl >> 8) & 0x0f) << 4).astype('uint8')           # first 4 byte
	b = (((lbl >> 4) & 0x0f) << 4).astype('uint8')        # middle 4 byte
	g = (((lbl     ) & 0x0f) << 4).astype('uint8')              # last 4 byte
	return np.dstack((r,g,b))

'''
input: number of uint16
output: [r, g, b]
'''
def label_to_rgb(lbl):
	r = (((lbl >> 8) & 0x0f) << 4).astype('uint8')           # first 4 byte
	b = (((lbl >> 4) & 0x0f) << 4).astype('uint8')        # middle 4 byte
	g = (((lbl     ) & 0x0f) << 4).astype('uint8')              # last 4 byte
	return (r,g,b)
	
'''
get the most frequent item of a list
'''
def most_frequent(lst):
	lst = list(lst)
	if len(lst) == 0:
		return None
	return max(set(lst), key=lst.count)

'''
range: (min_v, max_v)
confine v in this range (if v < min_v return min_v, if v > max_v return max_v)
'''
def confine_value(v, range):
	if v < range[0]:
		return range[0]
	elif v > range[1]:
		return range[1]
	else:
		return v