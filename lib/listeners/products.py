""" A module for all `Products` listeners """
import copy
import re
import logging

import falcon
import pymongo

from ..helper.requirements import RequirementsHelper
from ..helper.database import DatabaseHelper
from ..model.products import Product
from ..model.supliers import Suplier
from ..model.prices import Price
from ..model.departments import Department

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
        name = req.get_param("name")
        barcodes = req.get_param("barcodes")
        suplier = req.get_param("suplier")
        department = req.get_param("department")
        skip = req.get_param_as_int("skip") or 0
        limit = req.get_param_as_int("limit") or 10
        regex = req.get_param_as_bool("regex") or True

        query = []
        if name is not None:
            if regex:
                query.append({"name": re.compile(name, re.IGNORECASE)})
            else:
                query.append({"name": name})
        if barcodes is not None:
            query.append({"$or": [
                {"barcode": barcode} for barcode in barcodes.split(";")
            ]})
        if suplier is not None:
            query.append({"suplier": re.compile(suplier, re.IGNORECASE)})
        if department is not None:
            query.append({"department": re.compile(department, re.IGNORECASE)})

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "product"

        products = []
        try:
            if len(query) == 0:
                documents = helper.find({}).skip(skip).limit(limit) \
                            .sort([("name", pymongo.ASCENDING)])
            else:
                documents = helper.find({"$and": query}).skip(skip).limit(limit) \
                            .sort([("name", pymongo.ASCENDING)])
            products = [Product(**document).to_dict() for document in documents]
        finally:
            helper.close()

        result = {
            "data" : products,
            "status": {"code": 200, "message": "success"}
        }
        if len(products) == limit:
            result.update({"pagination": {"next": skip + limit}})
        req.context["result"] = result
        res.status = falcon.HTTP_200

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
