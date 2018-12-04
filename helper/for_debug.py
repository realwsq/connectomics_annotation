'''
input: NULL
output: NULL
----
print:
	"#nparray_name info:"
	"shape: #nparray_shape"
	"dtype: #nparray_dtype"
'''
def print_nparray_info(nparray_name, nparray_shape, nparray_dtype):
	print nparray_name + " info:"
	print "shape: "+str(nparray_shape)
	print "dtype: "+str(nparray_dtype)