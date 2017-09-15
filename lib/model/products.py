import logging

from pymongo.errors import DuplicateKeyError

from . import Model
from .prices import Price
from .supliers import Suplier
from .departments import Department
from ..helper.database import DatabaseHelper

class Product(Model):
    """ Model for product """
    def __init__(self, **kwargs):
        self._id = kwargs.get("_id", None)
        self.barcode = kwargs.get("barcode", None)
        self.name = kwargs.get("name", None)
        self.prices = kwargs.get("prices", None)
        self.suplier = kwargs.get("suplier", None)
        self.department = kwargs.get("department", None)

        if isinstance(self.prices, list):
            self.prices = [Price(**price) for price in self.prices]
        if isinstance(self.suplier, str):
            self.suplier = Suplier(code=self.suplier)
        if isinstance(self.department, str):
            self.department = Department(code=self.department)

    def to_dict(self):
        """ Convert to dictionary object """
        suplier_code = None
        if self.suplier is not None:
            suplier_code = self.suplier.code

        department_code = None
        if self.department is not None:
            department_code = self.department.code

        prices = []
        if self.prices is not None:
            prices = self.prices

        document = {
            "barcode": self.barcode,
            "name": self.name,
            "prices": [price.to_dict() for price in prices],
            "suplier": suplier_code,
            "department": department_code
        }
        return document

    def save(self):
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "product"
            helper.indexes = [("barcode", "unique",)]
            helper.insert_one(self.to_dict(), upsert=True, key={"barcode": self.barcode})
            logger.debug("Inserted or updated one product")
        except DuplicateKeyError:
            logger.warning("Duplicate barcode: %s", self.barcode)

    def get(self):
        """ Get product from database """
        logger = logging.getLogger(__name__)

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "product"

        logger.debug("Getting product: %s", self.barcode)
        document = helper.find_one({"barcode": self.barcode})

        result = Product()
        result.barcode = self.barcode
        result.name = document["name"]
        result.prices = []
        for price in document["prices"]:
            result.prices.append(Price(
                value=price["value"], min_qty=price["minQty"]
            ))
        result.suplier = Suplier(code=document["suplier"])
        result.department = Department(code=document["department"])
        return result
