import sys
import argparse
from app.config import Config
from app.icode import app_name, app_version
import uvicorn


class DefaultHelpParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def error(self, message):
        print(f"{message}", file=sys.stderr)
        self.print_help()
        sys.exit(1)

    def add_options(self):
        self.add_argument(
            "--listen",
            default="0.0.0.0:8817",
            required=False,
            help=f"Default listen address 0.0.0.0:8817.",
        )
        self.add_argument(
            "--config", default=None, required=True, help=f"Configuration file path."
        )
        self.add_argument(
            "--init-db",
            action="store_true",
            default=False,
            help=f"Initialize database and exit (no server start).",
        )
        self.add_argument(
            "--timeout",
            default=30,
            type=int,
            help=f"Global request timeout. Default 30 seconds.",
        )
        self.add_argument(
            "--log-level",
            default="INFO",
            type=lambda x: x.upper(),
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            required=False,
            help=f"Log level. Default INFO.",
        )
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{app_name} {app_version}",
            help="Show program version and exit.",
        )


class Parser:
    def __init__(self):
        self.parser = DefaultHelpParser()
        self.parser.add_options()

    @property
    def parse(self):
        args = self.parser.parse_args()
        return args


# def signal_handler(signum, frame):
#     global exit_event
#     Logger().warn(
#         f"Received signal {signum}. Program interrupted by user: {getpass.getuser()}"
#     )
#     exit_event.set()


if __name__ == "__main__":
    args = Parser().parse
    # init logger
    from app.log import logger

    logger.set_level(args.log_level)

    # init config
    try:
        config = Config(args.config)
    except:
        logger.error(f"init config failed")
        sys.exit(1)

    # init database
    try:
        from app.db.migrate import init_database

        init_database()
        logger.info("database initialized.")
    except Exception as e:
        logger.error(f"init database failed: {e}")
        sys.exit(1)

    if args.init_db:
        logger.info("database init only, exit.")
        sys.exit(0)

    # callback router
    from app.routers import router
    from fastapi import FastAPI

    app = FastAPI(
        title=app_name,
        version=app_version,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.include_router(router)
    app.state.config = config

    import time as _time
    from fastapi import Request as _Request

    @app.middleware("http")
    async def access_log_middleware(request: _Request, call_next):
        start = _time.time()
        response = await call_next(request)
        elapsed = (_time.time() - start) * 1000
        logger.info(
            f"{request.client.host if request.client else '-'} "
            f"{request.method} {request.url.path} "
            f"{response.status_code} "
            f"({elapsed:.0f}ms)"
        )
        return response

    uvicorn.run(
        app,
        host=args.listen.split(":")[0],
        port=int(args.listen.split(":")[1]),
        access_log=False,
    )


# config.map_["oip"] = oip
# config.map_["logger"] = logger
# config.map_["logger"] = xlogger
# ap = src.views.create_app(config, args)

# xlogger.info(
#     "\n".join(
#         list(
#             map(
#                 lambda rule: f"enable api http://{args.listen}{rule.rule}",
#                 ap.url_map.iter_rules(),
#             )
#         )[:-1]
#     )
# )
# threading.Thread(
#     target=ap.run,
#     kwargs={
#         "host": args.listen.split(":")[0],
#         "port": int(args.listen.split(":")[1]),
#         "debug": False,
#     },
#     daemon=True,
# ).start()

# # exit signal
# for sig in [signal.SIGINT, signal.SIGTERM]:
#     signal.signal(sig, signal_handler)

# exit_event = threading.Event()
# try:
#     while not exit_event.is_set():
#         exit_event.wait(timeout=1)
#     Mlogger().warn("All threads terminated. Exiting.")
# except Exception as e:
#     Mlogger().fatal(str(e))
