import socket, os, sys, mimetypes

HOST = 'localhost'
PORT = 8080
CRLF = "\r\n"
HTTP_VERSION = "HTTP/1.1"
SPACE = " "
HEADER_VALUE_SPLIT = ":"
HTTP_RESPONSE_MESSAGES = {
	100: "Continue",
	101: "Switching Protocols",
	200: "OK",
	201: "Created",
	202: "Accepted",
	203: "Non-Authoritative Information",
	204: "No Content",
	205: "Reset Content",
	206: "Partial Content",
	300: "Multiple Choices",
	301: "Moved Permanently",
	302: "Found",
	303: "See Other",
	304: "Not Modified",
	305: "Use Proxy",
	306: "(Unused)",
	307: "Temporary Redirect",
	400: "Bad Request",
	401: "Unauthorized",
	402: "Payment Required",
	403: "Forbidden",
	404: "Not Found",
	405: "Method Not Allowed",
	406: "Not Acceptable",
	407: "Proxy Authentication Required",
	408: "Request Timeout",
	409: "Conflict",
	410: "Gone",
	411: "Length Required",
	412: "Precondition Failed",
	413: "Request Entity Too Large",
	414: "Request-URI Too Long",
	415: "Unsupported Media Type",
	416: "Requested Range Not Satisfiable",
	417: "Expectation Failed",
	500: "Internal Server Error",
	501: "Not Implemented",
	502: "Bad Gateway",
	503: "Service Unavailable",
	504: "Gateway Timeout",
	505: "HTTP Version Not Supported"
} # found at https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html

class RequestDetailsConnection:
	response_already_made = False
	def make_response(self, *args, **kwds):
		if self.response_already_made: return ''
		self.response_already_made = True
		return make_response(*args, **kwds)
	def __init__(self, conn):
		self.low_level = conn
		self.close = conn.close
		self.recv = conn.recv
		self.send = conn.send

class RequestDetailsParsers:
	def __init__(self):return None
	def query(self, query):return { i.split('=')[0]:i.split('=')[1] for i in query.split('&') } if len(query) else {}

class RequestDetails:
	def __init__(self, method, addr, conn, parsed_uri, headers, body):
		self.method = method
		self.client_address = addr
		self.connection = RequestDetailsConnection(conn)
		self.parsers = RequestDetailsParsers()
		self.uri = parsed_uri
		self.headers = headers
		self.body = body

def unquote(text, i = 0):
	def is_hex(c):return ord('0') <= ord(c) <= ord('9') or ord('A') <= ord(c) <= ord('F')
	while i < len(text):
		if text[i] == '%' and is_hex(text[i+1]) and is_hex(text[i+2]):text = text[:i] + chr(int(text[i+1:i+3], 16)) + text[i+3:]
		i += 1
	return text

def error(http_error_code, custom_message = 'Unknown error'):
	return "Server error : " + str(http_error_code) + " (" + HTTP_RESPONSE_MESSAGES[http_error_code] + ")<br>" + custom_message

def make_response(response_code, headers, body):
	response = HTTP_VERSION + SPACE + str(response_code) + SPACE + HTTP_RESPONSE_MESSAGES[response_code] + CRLF
	for header in headers:response += header + HEADER_VALUE_SPLIT + SPACE + headers[header] + CRLF
	response += CRLF + body
	return response
	
def internal_request_handler(addr, conn, method, request_uri, http_version, headers, body):
	# DEBUG
	# print('New request from ' + str(addr) + ' :')
	# print("Method: " + method)
	# print("Uri: " + request_uri)
	# print("Headers: " + str(headers))
	# print("Body: " + body)
	
	# URI PARSING
	uri_fragment_i = request_uri.find('#')
	uri_fragment_i = uri_fragment_i if uri_fragment_i != -1 else len(request_uri)
	uri_query_i = request_uri.find('?')
	uri_query_i = uri_query_i if uri_query_i != -1 else uri_fragment_i
	
	uri_file = request_uri[:uri_query_i]
	uri_query = unquote(request_uri[uri_query_i + 1:uri_fragment_i])
	uri_fragment = unquote(request_uri[uri_fragment_i + 1:])
	parsed_uri = {'file':uri_file, 'query':uri_query, 'fragment':uri_fragment}
	
	print("URI : " + request_uri)
	print("Parsed URI : " + str(parsed_uri))
	
	# REQUEST_DETAILS CLASS
	request_details = RequestDetails(method, addr, conn, parsed_uri, headers, body)
	
	# FILE PROCESSING
	real_path = "www" + uri_file
	dir_path = os.path.dirname(real_path)
	if os.path.isfile(real_path):
	
		if os.path.basename(real_path).endswith('.py'):
			# PUT __init__.py IN THE DIR SO IT BECOMES IMPORTABLE
			init_file_path = os.path.join(dir_path, '__init__.py')
			init_file_exists = os.path.isfile(init_file_path)
			if not init_file_exists:
				init_file = open(init_file_path, 'w')
				init_file.write('')
				init_file.close()
			
			importable_file = real_path.replace('.py', '').replace('/', '.')
			try:
				webpage_module = __import__(importable_file, fromlist='*')
				reload(webpage_module)
				if "request_handler" in dir(webpage_module):
					request_details.response = [200, '', {}]
					webpage_module.request_handler(request_details)
				else:request_details.response = [500, error(500, 'Missing request handler in {}'.format(uri_file)), {}]
			except ImportError:request_details.response = [500, error(500, 'Unknown import error'), {}]
		
			# REMOVING __init__.py
			if not init_file_exists:os.remove(init_file_path)
			
		else:request_details.response = [200, open(real_path, 'rb').read(), { 'Content-Type': mimetypes.guess_type(real_path)[0] }]
		
	else:request_details.response = [404, error(404), {}]
	
	
	# CLEANING & ASSEMBLING
	response_code, response_body, additionnal_headers = request_details.response
	os.chdir(BASE_DIRECTORY)
	default_headers = { "Connection":"close", "Content-Type":"text/html", "Content-Length":str(len(response_body)) }
	headers = dict(default_headers.items() + additionnal_headers.items())
	
	# RESPOND
	response = request_details.connection.make_response(response_code, headers, response_body)
	if len(response):request_details.connection.send(response)

def HTTPServer():
	# CREATE SOCKET AND WAIT FOR REQUESTS
	s = socket.socket()
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	s.bind((HOST, PORT))
	s.listen(10)
	while 1:
		socket_conn, addr = s.accept()
		data = ""
		while 1:
			part = socket_conn.recv(4096)
			data += part
			if len(part) < 4096:break
		# TCP TO HTTP
		method, request_uri, http_version = data.split(CRLF)[0].split(SPACE)
		headers_and_body = data.split(CRLF + CRLF)
		headers_lines = headers_and_body[0]
		body = (CRLF + CRLF).join(headers_and_body[1:])
		headers = { i.split(': ')[0] : i.split(': ')[1] for i in headers_lines.split(CRLF)[1:] }
		internal_request_handler(addr, socket_conn, method, request_uri, http_version, headers, body)
		socket_conn.close()

# SAVE CURRENT DIRECTORY
BASE_DIRECTORY = os.getcwd()
# AVOID PYC FILES
sys.dont_write_bytecode = True
HTTPServer()
