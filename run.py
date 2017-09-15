""" A module to run main program """
import logging

from falcon_cors import CORS
from wsgiref import simple_server

from lib.listeners.products import ProductsListener, ProductListener
from lib.listeners.sales import SalesListener, SaleListener
from lib.listeners.groups import GroupsListener, GroupListener, \
                                 GroupProductsListener, GroupProductListener
from lib.listeners.widgets import WidgetsListener, WidgetListener
from lib.middleware import RequireJSON, JSONTranslator

import falcon

PORT = 55671

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
    app.add_route("/sales", SalesListener())
    app.add_route("/sales/{code}", SaleListener())
    app.add_route("/groups/", GroupsListener())
    app.add_route("/groups/{code}", GroupListener())
    app.add_route("/groups/{code}/products", GroupProductsListener())
    app.add_route("/groups/{code}/products/{barcode}", GroupProductListener())
    app.add_route("/widgets", WidgetsListener())
    app.add_route("/widgets/{code}", WidgetListener())

    logger.debug("Server started at: 0.0.0.0:%s" % PORT)
    httpd = simple_server.make_server("0.0.0.0", PORT, app)
    httpd.serve_forever()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run()
