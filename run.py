""" A module to run main program """
import logging

from falcon_cors import CORS
from wsgiref import simple_server

from lib.listeners.products import ProductsListener, ProductListener
from lib.middleware import RequireJSON, JSONTranslator

import falcon

def run():
    """ Main program runs here """
    logger = logging.getLogger(__name__)
    logger.debug("Starting server...")

    cors = CORS(
        allow_all_origins=True,
        allow_all_headers=True,
        allow_all_methods=True
    )

    app = falcon.API(middleware=[
        cors.middleware,
        RequireJSON(),
        JSONTranslator()
    ])

    app.add_route("/products", ProductsListener())
    app.add_route("/products/{barcode}", ProductListener())

    logger.debug("Server started at: 0.0.0.0:55671")
    httpd = simple_server.make_server("0.0.0.0", 55671, app)
    httpd.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
