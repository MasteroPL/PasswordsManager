

def bytes_to_uuid4str(b:bytes):
	binValue = b
	hexValue = binValue.hex()
	result = hexValue[2:10] + "-" + hexValue[10:14] + "-" + hexValue[14:18] + "-" + hexValue[18:22] + "-" + hexValue[22:34]

	return result
