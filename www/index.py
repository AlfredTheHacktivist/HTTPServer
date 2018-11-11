"""
Webpage example : a python script implementing the "request_handler" function
"""

def request_handler(request_details):
	get_parameters_dict = request_details.parsers.query(request_details.uri['query'])
	prenom = get_parameters_dict['firstname'] if 'firstname' in get_parameters_dict else 'stranger'
	body = """<html><body>
Hi {} !
<form action="/index.py" method="GET">
<input type="text" name="firstname" placeholder="Name" />
<input type="submit" value="Send">
</form>
</body></html>""".format(prenom)
	request_details.response = [200, body, {}]
