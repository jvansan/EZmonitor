import yaml
import logging
import tornado.web
import tornado.ioloop

from ezmonitor import uimodules
from ezmonitor.utils import load_config
from ezmonitor import db 

log = logging.getLogger('tornado.application')

def create_app(routed_handlers, **app_settings):
    app = Application(routed_handlers, **app_settings)
    tornado.ioloop.IOLoop.current().run_sync(app._init)
    return app


class Application(tornado.web.Application):

    def __init__(self, routed_handlers, **app_settings):
        super(Application, self).__init__(
            routed_handlers, 
            ui_modules=uimodules,
            **app_settings
            )
        self.config = load_config()
        log.debug(self.config)

    async def _init(self):
        self.db_pool = await db.create_pool(**self.config.get("database", {}))
        async with self.db_pool.acquire() as conn:
            # Setup DB
            await db.setup_tables(conn)
            # Add configurated servers
            for server in self.config.get("servers", []):
                if not await db.server_exists(conn, server.get("name")):
                    await db.add_server(
                        conn,
                        server.get("name"),
                        server.get("url"),
                        server.get("port")
                    )

    def run(self, port=8888):
        self.listen(port)
        tornado.ioloop.IOLoop.current().start()