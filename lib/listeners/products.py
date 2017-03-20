""" A module for all `Products` listeners """
import copy
import logging

from ..helper.requirements import RequirementsHelper
from ..model.products import Product
from ..model.supliers import Suplier
from ..model.prices import Price
from ..model.departments import Department

import falcon

class ProductsListener:
    """ A class for `Products` listener.
        This listener only accept:
        - Post, Insert a `Product` to database
        - Get, get all `Product`s from database
    """
    def on_post(self, req, res):
        """ Handling posts requests """
        helper = RequirementsHelper()
        helper.check("doc", req.context)

        data = copy.deepcopy(req.context["doc"])
        helper.check("barcode", data)
        helper.check("name", data)
        helper.check("prices", data)
        helper.check_type(data["prices"], list)

        for price in data["prices"]:
            helper.check("min_qty", price)
            helper.check("value", price)
        helper.check("suplier", data)
        helper.check("department", data)

        product = Product()
        product.barcode = data["barcode"]
        product.name = data["name"]
        for price in data["prices"]:
            product.prices.append(Price(
                value=price["value"], min_qty=price["min_qty"]
            ))
        product.suplier = Suplier(code=data["suplier"])
        product.department = Department(code=data["department"])
        product.save()


        req.context["result"] = {"status":{
            "code": "200",
            "message": "success"
        }}
        res.status_code = falcon.HTTP_200

    def on_get(self, req, res):
        """ Handling get requests """
        pass

class ProductListener:
    """ A class for `Product` listener.
        This listener only accept:
        - Get, get a `Product` based on barcode
    """
    def on_get(self, req, res, barcode):
        """ Handling get requests """
        logger = logging.getLogger(__name__)
        logger.debug("Receving get request: %s", barcode)

        product = Product(barcode=barcode)
        product = product.get()

        req.context["result"] = {
            "data": [product.to_dict()],
            "status": {"code": "200", "message": "success"}
        }
        res.status_code = falcon.HTTP_200
