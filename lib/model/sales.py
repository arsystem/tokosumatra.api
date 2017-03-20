""" Sales module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model

import arrow

class Sale(Model):
    """ Model for sale """
    @property
    def sales_date(self):
        return self._sales_date
    @sales_date.setter
    def sales_date(self, value):
        self._sales_date = arrow.get(value).datetime

    def __init__(self, **kwargs):
        self._sales_date = None

        self.code = kwargs.get("code", None)
        self.sales_date = kwargs.get("sales_date", None)
        self.product = kwargs.get("product", None)
        self.qty = kwargs.get("qty", None)
        self.price = kwargs.get("price", None)
        self.department = kwargs.get("department", None)
        self.suplier = kwargs.get("suplier", None)
        self.discount_1 = kwargs.get("discount_1", None)
        self.discount_2 = kwargs.get("discount_2", None)
        self.discount_3 = kwargs.get("discount_3", None)
        self.discount_4 = kwargs.get("discount_4", None)
        self.customer = kwargs.get("customer", None)

    def to_dict(self):
        """ Convert to dictionary object """
        product_barcode = None
        if self.product is not None:
            product_barcode = self.product.barcode

        price_value = None
        if self.price is not None:
            price_value = self.price.value

        department_code = None
        if self.department is not None:
            department_code = self.department.code

        suplier_code = None
        if self.suplier is not None:
            suplier_code = self.suplier.code

        customer_code = None
        if self.customer is not None:
            customer_code = self.customer.code

        return {
            "code": self.code,
            "sales_date": self.sales_date,
            "product": product_barcode,
            "qty": self.qty,
            "price": price_value,
            "department": department_code,
            "suplier": suplier_code,
            "discount_1": self.discount_1,
            "discount_2": self.discount_2,
            "discount_3": self.discount_3,
            "discount_4": self.discount_4,
            "customer": customer_code
        }

    def save(self):
        """ Save to databaes """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "sale"
            helper.indexes = [("code", "unique", )]
            helper.insert_one(self.to_dict())
            logger.debug("Inserted or updated one sale")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
