# HTTPServer
A python implementation of a basic HTTP 1.1 server, with no other dependency than the Python Standard Library
This implementation doesn't include any security feature.

## Files
`HTTPServer
|-- www
|   '-- index.py
|   '-- sleep.py
'-- HTTPServer.py`
### HTTPServer.py
The Python script creating a socket, parsing the HTTP protocol with some constants and executing the webpages in `www` to respond to the client.
### index.py
A webpage example showing how to parse the get parameters and return an appropriate response body.
### sleep.py
A webpage example showing how to use other python modules and functions (time.sleep) and how to delay the webpage loading while continuing to send data.

## Documentation
Any webpage must implement the "request handler" function :
`request_handler(request_details)`
request_details is a python object containing all the details and tools you might need to process the request :
`request_details
|-- string method
|      The method specified in the request : GET / POST / HEAD / etc...
|-- tuple client_address
|      A tuple containing the client address and opened port.
|-- RequestDetailsConnection connection
|   |      A toolset to directly manipulate the connection.
|   '-- socket low_level
|   |      The connection socket object.
|   '-- void close()
|   |      This function closes the connection.
|   '-- string recv(int bytes_count)
|   |      Reads bytes_count bytes from the connection and returns the result.
|   '-- int send(string data)
|   |      Sends the data over the connection.
|   '-- string make_response(int response_code, dict headers, string body)
|   |      Construct an HTTP response with the set response code, headers and body if response_already_made is False.
|   '-- bool response_already_made
|          True if a response was already made, False if not.
|-- RequestDetailsParsers parsers
|   '-- query()
|-- dict uri
|   |  The HTTP Uniform Resource Identifier
|   '-- string ['path']
|   |      The URI part that contains the requested path
|   '-- string ['query']
|   |      The URI part that contains the query (after the "?")
|   '-- string ['fragment']
|   |      The URI part called "fragment" (after the "#")
|-- dict headers
|      The request headers.
'-- string body
|      The request body.
`
