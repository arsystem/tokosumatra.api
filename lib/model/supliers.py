""" Suplier module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model

class Suplier(Model):
    """ Model untuk suplier """
    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.name = kwargs.get("name", None)
        self.address = kwargs.get("address", None)
        self.city = kwargs.get("city", None)
        self.phone = kwargs.get("phone", None)
        self.mobile = kwargs.get("mobile", None)
        self.contact_person = kwargs.get("contact_person", None)

    def to_dict(self):
        """ Convert from model to dict """
        return {
            "code": self.code,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "phone": self.phone,
            "mobile": self.mobile,
            "contactPerson": self.contact_person
        }

    def save(self):
        "Save model to MongoDB database"
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "suplier"
            helper.indexes = [("code", "unique",)]
            helper.insert_one(self.to_dict(), upsert=True, key={"code": self.code})
            logger.debug("Inserted or updated one suplier")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
