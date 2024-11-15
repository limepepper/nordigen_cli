import multiprocessing
import threading

from flask import Flask

# flask app to handle redirect from approval browser process
app = Flask("redirect")
# app.debug = True
shutdown_flag = threading.Event()


@app.after_request
def after_request_func(response):
    print("after request")
    shutdown_flag.set()
    print("shutdown flag set")
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
    p.terminate()
    print(code)
