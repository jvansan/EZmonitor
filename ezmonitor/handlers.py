import json
import logging
from tornado.web import RequestHandler, authenticated, HTTPError
import tornado.ioloop
import traceback

from ezmonitor import db
from ezmonitor.utils import json_encoder


class BaseHandler(RequestHandler):
    @property
    def pool(self):
        return self.application.db_pool

    def log(self, message, level="INFO"):
        level = eval(f"logging.{level}")
        return logging.getLogger('tornado.application').log(level, message)

    async def prepare(self):
        conn =  await self.pool.acquire()
        self.conn = conn

    def write_error(self, status_code: int, **kwargs) -> None:
        self.log(f"Error - {status_code}")
        self.set_status(status_code)
        self.write(json.dumps({"status": status_code, "error": str(kwargs["exc_info"][1])}, indent=2))

    def get_current_user(self):
        return self.get_secure_cookie("ezmonitor-user")

    def on_finish(self):
        tornado.ioloop.IOLoop.current().add_callback(self.async_on_finish)

    async def async_on_finish(self):
        await self.pool.release(self.conn)


class ExampleHandler(BaseHandler):
    async def get(self):
        res = await self.conn.fetch("SELECT 1")
        self.log("TEST")
        self.log("ERROR", level="ERROR")
        self.write(f"{res[0][0]}, Hello, world\n")


class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html")


class LoginHandler(BaseHandler):
    def get(self):
        if self.get_secure_cookie("ezmonitor-user"):
            self.redirect("/")
        self.render("login.html", next=self.get_argument("next","/"), message=self.get_argument("error",""))
    
    async def post(self):
        email = self.get_argument("email", "")
        passwd = self.get_argument("password", "")
        self.log(f"{email}, {passwd}")
        if await db.authenticate(self.conn, email, passwd):
            self.set_secure_cookie("ezmonitor-user", email)
            self.redirect(self.get_argument("next", u"/"))
        else:
            raise HTTPError(401)


class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("ezmonitor-user")
        self.redirect(u"/")


class WebsiteHandler(BaseHandler):
    @authenticated
    async def get(self, name):
        # self.log(f"GET name {name}", "DEBUG")
        res = await db.get_one_status(self.conn, name)
        self.write(json_encoder(res, indent=2))


class WebsitesHandler(BaseHandler):
    @authenticated
    async def get(self):
        # self.log(f"GET name {name}", "DEBUG")
        res = await db.get_all_status(self.conn)
        self.write(json_encoder(res, indent=2))