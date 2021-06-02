

def bytes_to_uuid4str(b:bytes):
	binValue = b
	hexValue = binValue.hex()
	result = hexValue[2:10] + "-" + hexValue[10:14] + "-" + hexValue[14:18] + "-" + hexValue[18:22] + "-" + hexValue[22:34]

	return result

def serializilation_errors_to_response(source_errors:dict):
	errors = {}
	for error_key in source_errors.keys():
		err_list = source_errors[error_key]
		if not errors.__contains__(error_key):
			errors[error_key] = []
		for err in err_list:
			errors[error_key].append({
				"string": str(err),
				"code": err.code
			})

	return errors