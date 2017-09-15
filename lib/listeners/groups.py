""" A Module for `groups` listeners """
import copy
import re

import falcon

from bson.objectid import ObjectId

from ..helper.database import DatabaseHelper
from ..helper.requirements import RequirementsHelper
from ..model.groups import Group
from ..model.products import Product

class GroupsListener:
    """ `groups` listener """
    def on_get(self, req, res):
        """ GET Handler """
        query = []
        name = req.get_param("name")
        skip = req.get_param_as_int("skip") or 0
        limit = req.get_param_as_int("limit") or 10
        regex = req.get_param_as_bool("regex") or True

        if name is not None:
            name_query = {"name": name}
            if regex:
                name_query.update({"name": re.compile(name, re.IGNORECASE)})
            query.append(name_query)

        helper = DatabaseHelper()
        groups = []
        try:
            helper.dbase = "tokosumatra"
            helper.collection = "groups"

            match = {}
            if len(query) != 0:
                match = {"$and": query}
            pipeline = []
            pipeline.append({"$match": match})
            pipeline.append({"$unwind": "$products"})
            pipeline.append({"$lookup": {
                "from": "product",
                "localField": "products.barcode",
                "foreignField": "barcode",
                "as": "productDetail"
            }})
            pipeline.append({"$project": {
                "_id": 1,
                "name": 1,
                "products": {
                    "barcode": 1,
                    "name": {"$arrayElemAt": ["$productDetail.name", 0]}
                }
            }})
            pipeline.append({"$group": {
                "_id": "$_id",
                "name": {"$first": "$name"},
                "products": {"$push": "$products"}
            }})
            pipeline.append({"$skip": skip})
            pipeline.append({"$limit": limit})

            documents = helper.aggregate(pipeline)
            groups = [Group(**document).to_dict() for document in documents]
        finally:
            helper.close()

        result = {
            "data": groups,
            "status": {"code": 200, "message": "success"}
        }
        if len(groups) == limit:
            result.update({"pagination": {"next": skip + limit}})
        req.context["result"] = result
        res.status = falcon.HTTP_200

    def on_post(self, req, res):
        """ POST Handler """
        helper = RequirementsHelper()
        helper.check("doc", req.context)

        data = copy.deepcopy(req.context["doc"])
        helper.check_type(data["name"], str)
        helper.check("name", data)

        group = Group(name=data["name"], products=[])
        group_id = group.save()
        req.context["result"] = {
            "data": {"id": group_id},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

    def on_delete(self, req, res):
        """ DELETE Handler """
        name = req.get_param("name")
        if name is None:
            raise falcon.HTTPBadRequest(
                "Incomplete parameter",
                "You need to provide `name` parameter"
            )
        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        deleted_count = helper.delete_many({"name": name})
        req.context["result"] = {
            "data": {"deleted_count": deleted_count},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

class GroupListener:
    """ `group` listener """
    def on_get(self, req, res, code):
        """ GET Handler """
        helper = DatabaseHelper()
        groups = []
        try:
            helper.dbase = "tokosumatra"
            helper.collection = "groups"
            documents = helper.find({"_id": ObjectId(code)})
            groups = [Group(**document).to_dict() for document in documents]
        finally:
            helper.close()
        req.context["result"] = {
            "data": groups,
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

    def on_delete(self, req, res, code):
        """ DELETE Handler """
        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        deleted_count = helper.delete_many({"_id": ObjectId(code)})
        req.context["result"] = {
            "data": {"deletedCount": deleted_count},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

    def on_put(self, req, res, code):
        """ PUT Handler """
        helper = RequirementsHelper()
        helper.check("doc", req.context)

        data = copy.deepcopy(req.context["doc"])
        helper.check("name", data)
        helper.check_type(data["name"], str)

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        matched_count, modifed_count = helper.update_many(
            {"_id": ObjectId(code)},
            {"$set": {"name": data["name"]}}
        )
        req.context["result"] = {
            "data": {"matched_count": matched_count, "modifed_count": modifed_count},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

class GroupProductsListener:
    """ `group` and `products` listener """
    def on_post(self, req, res, code):
        """ POST Handler """
        helper = RequirementsHelper()
        helper.check("doc", req.context)

        data = copy.deepcopy(req.context["doc"])
        helper.check("barcode", data)
        helper.check_type(data["barcode"], str)

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        matched_count, modifed_count = helper.update_many(
            {"_id": ObjectId(code)},
            {"$push": {"products": {"barcode": data["barcode"]}}}
        )
        req.context["result"] = {
            "data": {"matched_count": matched_count, "modifed_count": modifed_count},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

class GroupProductListener:
    """ `group` and `product` listener """
    def on_delete(self, req, res, code, barcode):
        """ DELETE Handler """
        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "groups"
        matched_count, modifed_count = helper.update_many(
            {"_id": ObjectId(code)},
            {"$pull": {"products": {"barcode": barcode}}}
        )
        req.context["result"] = {
            "data": {"matched_count": matched_count, "modifed_count": modifed_count},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

