

import proxy.tokenizer as tokenizer

from proxy_utils import get_query_type, get_query_content

def read_query(proxy, packet):
	if get_query_type(packet) == proxy.COM_QUERY:
		tokens = tokenizer.tokenize(get_query_content(packet))
		for i, token in enumerate(tokens):
			print i, '(', token.token_name, ',', token.text, ')'
