# -*- coding: utf-8 -*-

from malt import Malt, Response
from wsgiref.simple_server import make_server

app = Malt()


@app.get('/')
def hello(request):
    return Response(request.url + '\n')


@app.post('/users')
def hello(request):
    return Response('Creating new user\n')


@app.get('/tasks')
def hello(request):
    return Response(
        '1. Buy groceries\n'
        '2. Clean the patio\n'
        '3. Take over the world\n'
    )


@app.post('/tasks')
def hello(request):
    return Response('Adding a task!\n')


server = make_server('localhost', 5000, app)
server.serve_forever()
