""" A module for `widgets` """
import re
import copy

import falcon

from ..helper.database import DatabaseHelper
from ..helper.requirements import RequirementsHelper
from ..model.widgets import Widget

class WidgetsListener:
    """ A `widgets` listener """
    def on_get(self, req, res):
        """ GET Handler """
        name = req.get_param("name")
        widget_type = req.get_param("type")
        size = req.get_param("size")
        limit = req.get_param_as_int("limit") or 10
        skip = req.get_param_as_int("skip") or 0
        regex = req.get_param_as_bool("regex") or True

        query = []
        if name is not None:
            if regex:
                query.append({"name": re.compile(name, re.IGNORECASE)})
            else:
                query.append({"name": name})
        if widget_type is not None:
            widget_type = widget_type.lower()
            query.append({"type": widget_type})
        if size is not None:
            size = size.lower()
            query.append({"size": size})

        helper = DatabaseHelper()
        helper.dbase = "tokosumatra"
        helper.collection = "widget"
        widgets = []
        try:
            if len(query) == 0:
                documents = helper.find({}).skip(skip).limit(limit)
            else:
                documents = helper.find({"$and": query}).skip(skip).limit(limit)
            widgets = [Widget(**document).to_dict(with_id=True) for document in documents]
        finally:
            helper.close()

        result = {
            "data": widgets,
            "status": {"code": 200, "message": "success"}
        }
        if len(widgets) == limit:
            result.update({"pagination": {"next": skip + limit}})
        req.context["result"] = result
        res.status = falcon.HTTP_200


    def on_post(self, req, res):
        """ POST Handler """
        helper = RequirementsHelper()
        helper.check("doc", req.context)

        data = copy.deepcopy(req.context["doc"])
        helper.check("type", data)
        helper.check("value", data)
        helper.check("name", data)
        helper.check("size", data)

        helper.check_type(data["type"], str)
        helper.check_type(data["name"], str)
        helper.check_type(data["size"], str)

        widget = Widget(
            widget_type=data["type"],
            name=data["name"],
            size=data["size"],
            value=data["value"]
        )
        inserted_id = widget.save()
        req.context["result"] = {
            "data": {"id": inserted_id},
            "status": {"code": 200, "message": "success"}
        }
        res.status = falcon.HTTP_200

    def on_delete(self, req, res):
        """ DELETE Handler """
        pass

class WidgetListener:
    """ A `widget` listener """
    def on_get(self, req, res, code):
        """ GET Handler """
        pass

    def on_put(self, req, res, code):
        """ PUT Handler """
        pass

    def on_delete(self, req, res, code):
        """ DELETE Handler """
        pass
