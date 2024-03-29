import asyncio
import logging

import tornado.ioloop
import tornado.platform.asyncio
import tornado.web
from tornado.log import enable_pretty_logging

from ezmonitor.app import create_app
from ezmonitor.handlers import (HomeHandler, LoginHandler, LogoutHandler,
                                WebsiteHandler, WebsitesHandler)

# class MainHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write("Hello, world\n")

def start_server():
    app = create_app([
            (r"/", HomeHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/api/website/(\w*[-]*\w*)", WebsiteHandler),
            (r"/api/websites", WebsitesHandler),
        ], 
        debug=True,
        template_path='ezmonitor/templates',
        static_path='ezmonitor/static',
        login_url="/login",
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
    )
    app.run()

if __name__ == "__main__":
    enable_pretty_logging()
    logging.getLogger('tornado.application').setLevel('DEBUG')
    start_server()
