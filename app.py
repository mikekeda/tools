from tornado import websocket, web, ioloop
import json
import os

cl = []

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()

    @web.asynchronous
    def post(self, *args):
        self.finish()
        message = self.get_argument("m")
        data = {"message": message}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

app = web.Application([
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
])

if __name__ == '__main__':
    ip = 'localhost'
    if os.environ.get('OPENSHIFT_PYTHON_IP'):
        ip = os.environ.get('OPENSHIFT_PYTHON_IP')
    app.listen(15888, ip)

    ioloop.IOLoop.instance().start()
