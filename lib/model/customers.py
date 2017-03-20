""" Customer module """
import logging

from pymongo.errors import DuplicateKeyError
from ..helper.database import DatabaseHelper
from . import Model
import arrow

class Customer(Model):
    """ Class untuk customer """
    @property
    def member_since(self):
        """ Getter for `member_since` """
        return self._member_since
    @member_since.setter
    def member_since(self, value):
        self._member_since = arrow.get(value).datetime

    @property
    def birthday(self):
        """ Getter for `birthday` """
        return self._birthday
    @birthday.setter
    def birthday(self, value):
        self._birthday = arrow.get(value).datetime

    @property
    def point_expirity_date(self):
        """ Getter for `point_expirity_date` """
        return self._point_expirity_date
    @point_expirity_date.setter
    def point_expirity_date(self, value):
        self._point_expirity_date = arrow.get(value).datetime

    def __init__(self, **kwargs):
        self._member_since = None,
        self._birthday = None,
        self._point_expirity_date = None

        self.code = kwargs.get("code", None)
        self.name = kwargs.get("name", None)
        self.address = kwargs.get("address", None)
        self.city = kwargs.get("city", None)
        self.postcode = kwargs.get("postcode", None)
        self.phone = kwargs.get("phone", None)
        self.mobile = kwargs.get("mobile", None)
        self.member_since = kwargs.get("member_since", None)
        self.birthday = kwargs.get("birthday", None)
        self.gender = kwargs.get("gender", None)
        self.email = kwargs.get("email", None)
        self.point = kwargs.get("point", 0)
        self.used_point = kwargs.get("used_point", None)
        self.point_expirity_date = kwargs.get("point_expirity_date", None)
        self.expired_point = kwargs.get("expired_point", 0)

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "postcode": self.postcode,
            "phone": self.phone,
            "mobile": self.mobile,
            "member_since": self.member_since,
            "birthday": self.birthday,
            "gender": self.gender,
            "email": self.email,
            "point": self.point,
            "used_point": self.used_point,
            "point_expirity_date": self.point_expirity_date,
            "expired_point": self.expired_point
        }

    def save(self):
        """ Save to database """
        logger = logging.getLogger(__name__)
        try:
            helper = DatabaseHelper()
            helper.dbase = "tokosumatra"
            helper.collection = "customer"
            helper.indexes = [("code", "unique", )]
            helper.insert_one(self.to_dict(), upsert=True, key={"code": self.code})
            logger.debug("Inserted or updated on customer")
        except DuplicateKeyError:
            logger.warning("Duplicate code: %s", self.code)
