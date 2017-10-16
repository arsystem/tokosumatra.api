""" Module for database helper """
import pymongo
import arrow

class DatabaseHelper:
    """ A helper class to save something into database
        This class will add some extra fields
    """
    def __init__(self, **kwargs):
        self.conn = None
        self.dbase = kwargs.get("dbase", None)
        self.collection = kwargs.get("collection", None)
        self.indexes = kwargs.get("indexes", [])
        self.connection_string = "mongodb://10.42.232.81"

    def close(self):
        """ Close connection. Necessary for manually close the connection """
        assert self.conn is not None, "conn is not defined."
        self.conn.close()

    def delete_many(self, condition=None):
        """ Delete all document based on given condition """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert self.connection_string is not None, "connecion_string is not defined."
        assert condition is not None, "condition is not defined."

        self.conn = pymongo.MongoClient(self.connection_string)
        deleted_count = 0
        try:
            dbase = self.conn[self.dbase]
            result = dbase[self.collection].delete_many(condition)
            deleted_count = result.deleted_count
        finally:
            self.conn.close()
        return deleted_count

    def update_many(self, condition=None, new_value=None):
        """ Update based on given condition """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert self.connection_string is not None, "connection_string is not defined."
        assert condition is not None, "condition is not defined."
        assert new_value is not None, "new_value is not defined."

        self.conn = pymongo.MongoClient(self.connection_string)
        result = None
        try:
            dbase = self.conn[self.dbase]
            result = dbase[self.collection].update_many(condition, new_value)
        finally:
            self.conn.close()
        return (result.matched_count, result.modified_count,) if result is not None else None


    def find(self, condition=None, field=None):
        """ Find all records in database """
        return self._execute_find(condition=condition, field=field, multiple=True)

    def find_one(self, condition=None, field=None):
        """ Find only one record in database """
        return self._execute_find(condition=condition, field=field, multiple=False)

    def _execute_find(self, condition=None, field=None, multiple=False):
        """ get data from database  based on given condition and field.

            Exceptions:
            - AssertionError
        """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert self.connection_string is not None, "connection_string is not defined."

        if condition is None:
            condition = {}

        self.conn = pymongo.MongoClient(self.connection_string)
        try:
            dbase = self.conn[self.dbase]
            if multiple:
                return dbase[self.collection].find(condition, field)
            else:
                return dbase[self.collection].find_one(condition, field)
        finally:
            self.conn.close()

    def aggregate(self, pipeline=None):
        """ Run MongoDB Aggregation using pipeline and
            automatically close the connection once it finish
        """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert self.connection_string is not None, "connection_string is not defined."
        assert pipeline is not None, "pipeline is not defined."

        self.conn = pymongo.MongoClient(self.connection_string)
        try:
            dbase = self.conn[self.dbase]
            return dbase[self.collection].aggregate(pipeline)
        finally:
            self.conn.close()

    def insert_one(self, document=None, upsert=False, key=None):
        """ Save something to database """
        assert self.dbase is not None, "dbase is not defined."
        assert self.collection is not None, "collection is not defined."
        assert self.connection_string is not None, "connection_string is not defined."
        assert document is not None, "document is not defined."
        assert upsert is not None, "upsert is not defined."

        conn = pymongo.MongoClient(self.connection_string)
        dbase = conn[self.dbase]
        result = None
        try:
            for field, index_type in self.indexes:
                if index_type == "unique":
                    dbase[self.collection].create_index(field, unique=True)
                else:
                    dbase[self.collection].create_index(field)
            document.update({"insertTime": arrow.utcnow().datetime})
            if upsert:
                assert key is not None, "key is not defined."
                assert isinstance(key, dict), "incorrect data type for key. Found %s" % type(key)
                result = dbase[self.collection].update_one(key, {"$set": document}, upsert=True)
            else:
                result = dbase[self.collection].insert_one(document)
        finally:
            conn.close()
        return str(result.inserted_id) if result is not None else None
