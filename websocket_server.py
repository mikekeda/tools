from tornado import websocket, web, ioloop
import json
import os

cl = []

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

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
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
])

if __name__ == '__main__':
    ip   = 'localhost'
    port = 8080
    if os.environ.get('OPENSHIFT_PYTHON_IP'):
        ip = os.environ.get('OPENSHIFT_PYTHON_IP')
        port = int(os.environ.get('OPENSHIFT_PYTHON_PORT'))
    app.listen(port, ip)

    ioloop.IOLoop.instance().start()
