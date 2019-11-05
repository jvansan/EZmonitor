import asyncio
import logging
import tornado.web
import tornado.ioloop
from tornado.log import enable_pretty_logging
import tornado.platform.asyncio

from ezmonitor.app import create_app
from ezmonitor.handlers import HomeHandler, WebsiteHandler, WebsitesHandler

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world\n")

def start_server():
    app = create_app([
        (r"/", HomeHandler),
        (r"/api/website/(\w*[-]*\w*)", WebsiteHandler),
        (r"/api/websites", WebsitesHandler),
        ], 
        debug=True,
        template_path='ezmonitor/templates',
        static_path='ezmonitor/static'
    )
    app.run()

if __name__ == "__main__":
    enable_pretty_logging()
    logging.getLogger('tornado.application').setLevel('DEBUG')
    start_server()
