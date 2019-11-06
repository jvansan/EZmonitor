import logging
import tornado.ioloop
import tornado.web
import yaml
from apscheduler.schedulers.tornado import TornadoScheduler

from ezmonitor import db, uimodules
from ezmonitor.utils import load_config, datetime_in_n_seconds
from ezmonitor.tasks import run_checks

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
        self.db_pool = None
        self.scheduler = None

    def run(self, port=8888):
        self.listen(port)
        tornado.ioloop.IOLoop.current().start()

    async def _init(self):
        self.db_pool = await db.create_pool(**self.config.get("database", {}))
        await self.__setup_db()
        await self.__setup_scheduler()

    async def __setup_db(self):
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
    
    async def __setup_scheduler(self):
        self.scheduler = TornadoScheduler()
        for server in self.config.get("servers", []):
            self.scheduler.add_job(
                run_checks, 'interval', [self.db_pool, server], name=f"check_{server.get('name')}",
                next_run_time=datetime_in_n_seconds(30),
                hours=24, jitter=300
            )
        self.scheduler.start()
