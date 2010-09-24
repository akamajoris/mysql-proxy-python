

def get_query_type(packet):
	return ord(packet[0])

def get_query_content(packet):
	return packet[1:]
