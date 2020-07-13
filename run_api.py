import argparse
from explorebaduk.app import create_app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ExploreBaduk Game Server API")
    parser.add_argument("--host", type=str, default="localhost", help="Server IP (default localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default 8080)")
    parser.add_argument("--debug", action="store_true", help="Enable debugging")
    parser.add_argument("--access-log", action="store_true", help="Enable access log (default False)")
    parser.add_argument("--auto-reload", action="store_true", help="Auto reload when code changes")
    arguments = parser.parse_args()

    app = create_app()
    app.run(
        host=arguments.host,
        port=arguments.port,
        debug=arguments.debug,
        access_log=arguments.access_log,
        auto_reload=arguments.auto_reload,
    )
