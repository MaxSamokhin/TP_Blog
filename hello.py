from pprint import pformat
from cgi import parse_qsl, escape

def application(environ, start_response):
    output = ['<h1>WSGI:</h1>']

    output.append('Post:')
    output.append('<form method="post">')
    output.append('<input type="text" name = "test">')
    output.append('<input type="submit" value="Send">')
    output.append('</form>')

    output.append('<br>Get:')
    output.append('<form method="get">')
    output.append('<input type="text" name = "test">')
    output.append('<input type="submit" value="Send">')
    output.append('</form>')

    if environ['REQUEST_METHOD'] == 'POST':
        output.append('<h1>Post  data:</h1>')
        output.append(pformat(environ['wsgi.input'].read()))
   
    d = parse_qsl(environ['QUERY_STRING'])
    if environ['REQUEST_METHOD'] == 'GET':
        if environ['QUERY_STRING'] != '':
            output.append('<h1>Get data:</h1>')
            for ch in d:
                output.append(' = '.join(ch))
                output.append('<br>')
    output_len = sum(len(line) for line in output)
    start_response('200 OK', [('Content-type', 'text/html'),
                              ('Content-Length', str(output_len))])
    return output

def hello(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']