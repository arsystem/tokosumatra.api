""" A Module for `sales` listener """
import datetime

import arrow
import falcon

from bson.son import SON

from ..helper.database import DatabaseHelper
from ..model.sales import Sale

class SalesListener:
    """ SalesListener """
    def on_get(self, req, res):
        """ GET request.
            You can provide as many params as you want
        """
        start_date = req.get_param("startdate")
        end_date = req.get_param("enddate")
        products = req.get_param("products")
        customer = req.get_param("customer")
        cashier = req.get_param("cashier")
        department = req.get_param("department")
        limit = req.get_param_as_int("limit") or 10
        skip = req.get_param_as_int("skip") or 0
        sort_by = req.get_param("sortby") or "product"
        group_by = req.get_param("groupby")

        query = []
        if start_date is not None and end_date is None:
            start_date = arrow.get(start_date).datetime
            query.append({"sales_date": {"$gte": start_date}})
        if start_date is not None and end_date is not None:
            start_date = arrow.get(start_date).datetime
            end_date = arrow.get(end_date).datetime
            query.append({"sales_date": {
                "$gte": start_date,
                "$lte": end_date
            }})
        if products is not None:
            query.append({"$or": [
                {"product": product} for product in products.split(";")
            ]})
        if customer is not None:
            query.append({"customer": customer})
        if cashier is not None:
            query.append({"cashier": cashier})
        if department is not None:
            query.append({"department": department})

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "sale"

        if group_by is None:
            if len(query) == 0:
                documents = helper.find()
            else:
                documents = helper.find({"$and": query})
            data = []
            for document in documents.skip(skip).limit(limit):
                data.append(Sale(**document).to_dict())
        else:
            if group_by != "product" and group_by != "customer" and \
                group_by != "sales_date" and group_by != "machine" and \
                group_by != "cashier":
                raise falcon.HTTPBadRequest(
                    "Unknown Group By argument",
                    "Please make sure you have a proper Group By argument"
                )
            pipeline = []
            match = {}
            if len(query) != 0:
                match = {"$and": query}
            pipeline.append({"$match": match})

            if sort_by == "product":
                pipeline.append({"$group": {
                    "_id": "$%s" % group_by,
                    "count": {"$sum": "$qty"}
                }})
            elif sort_by == "code":
                pipeline.append({"$group": {"_id": {
                    "id": "$%s" % group_by,
                    "code": "$code"
                }}})
                pipeline.append({"$group": {
                    "_id": "$_id.id",
                    "code": {"$push": "$_id.code"}
                }})
                pipeline.append({"$project": {
                    "_id": 1,
                    "count": {"$size": "$code"}
                }})

            if group_by == "product":
                pipeline.append({"$lookup": {
                    "from": "product",
                    "localField": "_id",
                    "foreignField": "barcode",
                    "as": "groupDetail"
                }})
            elif group_by == "customer" or group_by == "machine" or group_by == "cashier":
                pipeline.append({"$lookup": {
                    "from": "%s" % group_by,
                    "localField": "_id",
                    "foreignField": "code",
                    "as": "groupDetail"
                }})

            if group_by == "product" or group_by == "customer" or group_by == "cashier" \
                or group_by == "machine":
                pipeline.append({"$project": {
                    "_id": 1,
                    "count": 1,
                    "name": {"$arrayElemAt": ["$groupDetail.name", 0]}
                }})

            if group_by == "sales_date":
                pipeline.append({"$sort": SON([("_id", 1)])})
            else:
                pipeline.append({"$sort": SON([("count", -1)])})
            pipeline.append({"$skip": skip})
            pipeline.append({"$limit": limit})
            documents = helper.aggregate(pipeline)

            data = []
            for document in documents:
                value = {group_by: document["_id"], "count": document["count"]}
                if isinstance(document["_id"], datetime.datetime):
                    value.update({group_by: arrow.get(document["_id"]).isoformat()})
                if group_by != "sales_date":
                    name = "No Name"
                    if "name" in document:
                        name = document["name"]
                    value.update({"name": name})
                data.append(value)
        result = {
            "data": data,
            "status": {"code": 200, "message": "success"}
        }
        if len(data) == limit:
            result.update({"pagination": {"next": skip + limit}})
        req.context["result"] = result
        res.status = falcon.HTTP_200


class SaleListener:
    """ SalesListener """
    def on_get(self, req, res, code):
        """ GET Handler """
        sales = Sale()
        sales = sales.get(code=code)
        req.context["result"] = {
            "data": [sale.to_dict() for sale in sales],
            "status": {"code": "200", "message": "success"}
        }
        res.status = falcon.HTTP_200
