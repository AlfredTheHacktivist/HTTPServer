"""
Webpage example : a python script using the "sleep" function from the "time" module and delaying the webpage loading while continuing to send data.
"""

from time import sleep

def request_handler(request_details):
	a = 0
	headers = { "Content-Type":"text/html" }
	request_details.connection.send(request_details.connection.make_response(200, headers, ''))
	for i in range(5):
		print('sending packet #'+str(a))
		request_details.connection.send(str(a) + 4096*chr(0))
		sleep(1)
		a += 1
	request_details.response = [200, '', {}]
