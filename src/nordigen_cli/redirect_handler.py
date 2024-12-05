import multiprocessing
import threading

import flask
from flask import Flask
from loguru import logger
from werkzeug.serving import make_server

# flask app to handle redirect from approval browser process
app = Flask("redirect")
# app.debug = True
shutdown_flag = threading.Event()


@app.after_request
def after_request_func(response):
    logger.trace("after request")
    shutdown_flag.set()
    logger.trace("shutdown flag set")
    return response


def run_flask_app(q: multiprocessing.Queue):
    @app.route("/redirect")
    def handle_redirect():
        q.put("shutdown plz")
        return "you have been redirected back after approval process"

    app.run()


def run_flask_app_thread():
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=run_flask_app, args=(q,))
    p.start()
    code = q.get(block=True)
    logger.trace("got here, should terminate now")
    p.terminate()
    logger.trace(code)


class ServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.server = make_server(
            "127.0.0.1",
            5000,
            app,
        )
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logger.trace("Starting server")
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


def run_flask_app_thread2():
    app = flask.Flask("myapp")

    @app.after_request
    def after_request_func(response):
        logger.trace("after request in server 2")
        server.shutdown()
        return response

    @app.teardown_request
    def teardown_request_func(error):
        logger.trace("teardown request")
        server.shutdown()

    @app.route("/redirect")
    def handle_redirect():
        return "you have been redirected back after approval process"

    server = ServerThread(app)
    server.start()
    logger.trace("Server started")
