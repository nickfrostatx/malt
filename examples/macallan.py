# -*- coding: utf-8 -*-

from malt import Malt, Response, HTTPException, json
from wsgiref.simple_server import make_server

app = Malt()

tasks = [
    {'id': 0, 'name': 'Buy groceries'},
    {'id': 1, 'name': 'Clean the patio'},
    {'id': 2, 'name': 'Take over the world'},
]


@app.get('^/$')
def print_url(request):
    return Response(request.url + '\n')


@app.get('^/tasks$')
def list_tasks(request):
    return json({'tasks': tasks})


@app.post('^/tasks$')
def create_task(request):
    data = request.json()
    try:
        name = data['name']
    except (KeyError, TypeError):
        raise HTTPException(400, 'Missing task name')

    task = {'id': len(tasks), 'name': name}
    tasks.append(task)

    return Response('/tasks/{0:d}'.format(task['id']))


@app.get('^/tasks/(\d+)$')
def get_task(request, task_id):
    task_id = int(task_id)
    try:
        task = tasks[task_id]
    except IndexError:
        raise HTTPException(404)
    return json({'task': task})


wsgi = app.wsgi_app({})

server = make_server('localhost', 5000, wsgi)
print('Running locally on http://localhost:5000')
server.serve_forever()
