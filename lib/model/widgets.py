""" A module for `widget` class """
from . import Model
from ..helper.database import DatabaseHelper

class Widget(Model):
    def __init__(self, **kwargs):
        self._id = kwargs.get("_id", None)
        self.type = kwargs.get("widget_type", None) or kwargs.get("type", None)
        self.value = kwargs.get("value", None)
        self.name = kwargs.get("name", None)
        self.size = kwargs.get("size", None)

    def to_dict(self, with_id=False):
        """ Convert object to dictionary """
        document = {
            "type": self.type,
            "value": self.value,
            "name": self.name,
            "size": self.size
        }
        if with_id:
            document.update({"_id": str(self._id)})
        return document

    def save(self):
        """ Save `widget` to database """
        assert self.type is not None, "type is not defined."
        assert self.value is not None, "value is not defined."
        assert self.name is not None, "name is not defined."
        assert self.size is not None, "size is not defined."

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "widget"
        helper.indexes = [("name", "",)]
        return helper.insert_one(self.to_dict())
