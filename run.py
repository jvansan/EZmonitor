import asyncio
import logging
import tornado.web
import tornado.ioloop
from tornado.log import enable_pretty_logging
import tornado.platform.asyncio

from ezmonitor.app import create_app
from ezmonitor.handlers import ExampleHandler

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world\n")

def start_server():
    app = create_app([
        (r"/", ExampleHandler)
    ], debug=True)
    app.run()

if __name__ == "__main__":
    enable_pretty_logging()
    start_server()
