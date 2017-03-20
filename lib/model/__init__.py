""" Base module """
class Model:
    """ Base class for model """
    def to_dict(self):
        """ Convert from model to dict """
        raise NotImplementedError

    def save(self):
        """ Save model to database """
        raise NotImplementedError
