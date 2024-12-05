import threading

from flask import Flask, request
from loguru import logger

app = Flask(__name__)

response_data = {}
# server_thread = None


@app.route("/redirect", methods=["GET"])
def handle_redirect():
    global response_data
    response_data["query_params"] = request.args
    response_data["body"] = request.data.decode("utf-8")
    response_data["method"] = request.method

    # Inform the user
    return "Callback received. You can close this window.", 200


def run_server():
    # Run Flask app on a separate thread
    app.run(port=5000, use_reloader=False)


def run_flask_app_thread3():
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    logger.trace("Waiting for redirect callback...")
    while not response_data:
        try:
            # Poll until response_data is populated
            server_thread.join(timeout=0.1)
        except KeyboardInterrupt:
            logger.trace("Terminating server...")
            break

    logger.trace("Callback received:", response_data)

    # Safely exit the program
