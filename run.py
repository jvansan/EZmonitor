import asyncio
import logging
import tornado.web
import tornado.ioloop
from tornado.log import enable_pretty_logging
import tornado.platform.asyncio

from ezmonitor.app import create_app
from ezmonitor.handlers import HomeHandler

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world\n")

def start_server():
    app = create_app([
        (r"/", HomeHandler)
        ], 
        debug=True,
        template_path='ezmonitor/templates',
        static_path='ezmonitor/static'
    )
    app.run()

if __name__ == "__main__":
    enable_pretty_logging()
    start_server()
