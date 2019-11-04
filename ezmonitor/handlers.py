import logging
from tornado.web import RequestHandler
import tornado.ioloop


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

    def on_finish(self):
        tornado.ioloop.IOLoop.current().add_callback(self.async_on_finish)

    async def async_on_finish(self):
        await self.pool.release(self.conn)


class ExampleHandler(BaseHandler):
    async def get(self):
        res = await self.conn.fetch("SELECT 1")
        self.log("TEST")
        self.log("ERROR", level="ERROR")
        self.write(f"{res}, Hello, world\n")