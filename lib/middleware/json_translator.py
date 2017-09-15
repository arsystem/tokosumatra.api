import falcon
import json

class JSONTranslator(object):
    """ Translate request from JSON String to Python Dictionary """

    def process_request(self, req, resp):
        """ Process a request that come from server """
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return
        try:
            body = req.stream.read()
            # print(body)

            req.context['doc'] = json.loads(body.decode("utf8"))
            if not req.context['doc']:
                raise falcon.HTTPBadRequest(
                    'Empty request body',
                    'A valid JSON document is required.'
                )
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        """ Process a response that sent by API.
            Assuming all response is inside `req.context` and stored in `result` key
        """
        if 'result' not in req.context:
            return
        resp.body = json.dumps(req.context['result'])
