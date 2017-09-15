""" Sales module """
import logging
import datetime

import arrow

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from .products import Product
from .cashier import Cashier
from .customers import Customer
from .departments import Department
from .machine import Machine
from .supliers import Suplier
from .prices import Price
from . import Model

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
        self.customer = kwargs.get("customer", None)
        self.cashier = kwargs.get("cashier", None)
        self.machine = kwargs.get("machine", None)

        if isinstance(self.product, str):
            self.product = Product(barcode=self.product)
        if isinstance(self.price, str):
            self.price = Price(value=int(self.price))
        if isinstance(self.price, int):
            self.price = Price(value=self.price)
        if isinstance(self.price, float):
            self.price = Price(value=int(self.price))
        if isinstance(self.department, str):
            self.department = Department(code=self.department)
        if isinstance(self.suplier, str):
            self.suplier = Suplier(code=self.suplier)
        if isinstance(self.customer, str):
            self.customer = Customer(code=self.customer)
        if isinstance(self.cashier, str):
            self.cashier = Cashier(code=self.cashier)
        if isinstance(self.machine, str):
            self.machine = Machine(code=self.machine)

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

        cashier_code = None
        if self.cashier is not None:
            cashier_code = self.cashier.code

        machine_code = None
        if self.machine is not None:
            machine_code = self.machine.code

        sales_date = self.sales_date
        if isinstance(self.sales_date, datetime.datetime):
            sales_date = arrow.get(self.sales_date).isoformat()

        return {
            "code": self.code,
            "sales_date": sales_date,
            "product": product_barcode,
            "qty": self.qty,
            "price": price_value,
            "department": department_code,
            "suplier": suplier_code,
            "customer": customer_code,
            "cashier": cashier_code,
            "machine": machine_code
        }

    def save(self):
        """ Save to databaes """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "sale"
            helper.indexes = [("code", "")]
            helper.insert_one(self.to_dict())
            logger.debug("Inserted or updated one sale")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)

    def get(self, code=None):
        """ Get data from database """
        assert code is not None, "code is not defined."

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "sale"
        documents = helper.find({"code": code})

        if documents is not None:
            return [Sale(**document) for document in documents]
