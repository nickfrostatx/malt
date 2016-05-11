from malt import Malt, json
from wsgiref.simple_server import make_server


app = Malt()


def headers_dict(headers):
    data = {}
    for key in headers:
        data[key] = headers[key]
    return data


@app.get('/ip')
def ip(request):
    return json({'origin': request.remote_addr})


@app.get('/user-agent')
def user_agent(request):
    return json({
        'user-agent': request.headers.get('User-Agent'),
    })


@app.get('/headers')
def headers(request):
    return json({
        'headers': headers_dict(request.headers),
    })


@app.get('/get')
def get(request):
    return json({
        'args': {},
        'headers': headers_dict(request.headers),
        'origin': request.remote_addr,
        'url': request.url,
    })


@app.post('/post')
def post(request):
    return json({
        'args': {},
        'data': request.data,
        'headers': headers_dict(request.headers),
        'origin': request.remote_addr,
        'url': request.url,
    })


if __name__ == '__main__':
    server = make_server('localhost', 5000, app)
    print('Running locally on http://localhost:5000')
    server.serve_forever()
