""" Price module """
class Price:
    """ Model for price """
    def __init__(self, **kwargs):
        self._min_qty = None

        self.min_qty = kwargs.get("min_qty", None)
        self.value = kwargs.get("value", None)

    @property
    def min_qty(self):
        """ min_qty property of Price """
        return self._min_qty

    @min_qty.setter
    def min_qty(self, value):
        if value is None or value < 1:
            value = 1
        self._min_qty = value

    def to_dict(self):
        """ Convert model to dict """
        return {
            "minQty": self.min_qty,
            "value": self.value
        }
