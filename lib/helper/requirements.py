""" A module for requirements helper.
    This helper will help to check requirements
"""
from falcon import HTTPBadRequest

class RequirementsHelper:
    """ Helping to check requirements """
    def check(self, to_check=None, data=None):
        """ Check given parameters if exists on data.
            This checker assume that you are using falcon to thrown an Exception

            Exceptions:
            - AssertionError
            - HTTPBadRequest
        """
        assert to_check is not None, "to_check is not defined."
        assert data is not None, "data is not defined."

        if to_check not in data:
            raise HTTPBadRequest(
                "Cannot find %s" % to_check,
                "%s is not provided when you are requesting this API." % to_check
            )

    def check_type(self, to_check=None, check_type=None):
        """ Check `to_check` if it is in correct type with `check_type` """
        assert to_check is not None, "to_check is not defined."
        assert check_type is not None, "check_type is not defined."

        if not isinstance(to_check, check_type):
            raise HTTPBadRequest(
                "Incorrect data type.",
                "You are requesting with incorrect data type. Please correct it."
            )
