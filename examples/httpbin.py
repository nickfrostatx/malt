from malt import Malt, json
from wsgiref.simple_server import make_server


app = Malt()


@app.error_handler
def err_response(exc):
    return json({
        'msg': exc.message,
    }, pretty=True, code=exc.status_code)


def headers_dict(headers):
    data = {}
    for key in headers:
        data[key] = headers[key]
    return data


@app.get('^/ip$')
def ip(request):
    return json({
        'origin': request.remote_addr,
    }, pretty=True)


@app.get('^/user-agent$')
def user_agent(request):
    return json({
        'user-agent': request.headers.get('User-Agent'),
    }, pretty=True)


@app.get('^/headers$')
def headers(request):
    return json({
        'headers': headers_dict(request.headers),
    }, pretty=True)


@app.get('^/get$')
def get(request):
    return json({
        'args': {},
        'headers': headers_dict(request.headers),
        'origin': request.remote_addr,
        'url': request.url,
    }, pretty=True)


@app.post('^/post$')
def post(request):
    return json({
        'args': {},
        'data': request.data(),
        'headers': headers_dict(request.headers),
        'origin': request.remote_addr,
        'url': request.url,
    }, pretty=True)


wsgi = app.wsgi_app({})


if __name__ == '__main__':
    server = make_server('localhost', 5000, wsgi)
    print('Running locally on http://localhost:5000')
    server.serve_forever()
