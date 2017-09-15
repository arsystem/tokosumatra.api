""" `groups` module """
from bson.objectid import ObjectId

from ..helper.database import DatabaseHelper
from .products import Product
from . import Model

class Group(Model):
    """ `group` model """
    def __init__(self, **kwargs):
        self._id = kwargs.get("_id", None)
        self.name = kwargs.get("name", None)
        self.products = kwargs.get("products", None)

        if self._id is not None:
            self._id = str(self._id)

        if isinstance(self.products, list) and len(self.products) > 0 \
            and isinstance(self.products[0], dict):
            for index, product in enumerate(self.products):
                new_product = Product(barcode=product["barcode"])
                if "name" in product:
                    new_product.name = product["name"]
                self.products[index] = new_product

    def to_dict(self, with_id=True):
        """ Convert from object to dictionar """
        document = {
            "name": self.name,
            "products": [{
                "barcode": product.barcode,
                "name": product.name
            } for product in self.products]
        }
        if self._id is not None and with_id:
            document.update({"_id": str(self._id)})
        return document

    def save(self):
        """ Save model to database """
        assert self.name is not None, "name is not defined."

        if self.products is None:
            self.products = []

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        helper.indexes = [("name", None,)]
        return helper.insert_one(self.to_dict())
