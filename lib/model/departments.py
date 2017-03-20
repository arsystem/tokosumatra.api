""" Department module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model

class Department(Model):
    """ Class untuk department """
    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.name = kwargs.get("name", None)

    def to_dict(self):
        """ Convert from model to dict """
        return {
            "code": self.code,
            "name": self.name
        }

    def save(self):
        """ Save to database """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "department"
            helper.indexes = [("code", "unique",)]
            helper.insert_one(self.to_dict(), upsert=True, key={"code": self.code})
            logger.debug("Inserted or updated one department")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
