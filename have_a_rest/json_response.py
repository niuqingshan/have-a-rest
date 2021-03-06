# coding=utf8

import json
from django import http
from django.core.serializers.json import DjangoJSONEncoder



__all__ = ['JSONResponse', 'JSONErrorResponse', 'HttpError',
    'Http200', 'Http201', 'Http400', 'Http401', 'Http403']


class JSONResponse(http.HttpResponse):
    """HTTP response with JSON body ("application/json" content type)"""

    def __init__(self, data, serializer=lambda x:x, **kwargs):
        """
        Create a new JSONResponse with the provided data (will be serialized
        to JSON using django.core.serializers.json.DjangoJSONEncoder).
        """

        kwargs['content_type'] = 'application/json; charset=utf-8'
        super(JSONResponse, self).__init__(json.dumps(serializer(data),
            cls=DjangoJSONEncoder), **kwargs)


class JSONErrorResponse(JSONResponse):
    """HTTP Error response with JSON body ("application/json" content type)"""

    def __init__(self, reason, serializer=lambda x:x, **additional_data):
        """
        Create a new JSONErrorResponse with the provided error reason (string)
        and the optional additional data (will be added to the resulting
        JSON object).
        """
        resp = {'error': reason}
        resp.update(additional_data)
        super(JSONErrorResponse, self).__init__(resp, serializer=serializer)


class Http200(JSONResponse):
    """HTTP 200 OK"""
    pass


class Http201(JSONResponse):
    """HTTP 201 CREATED"""
    status_code = 201


class Http400(JSONErrorResponse, http.HttpResponseBadRequest):
    """HTTP 400 Bad Request"""
    pass


class Http401(http.HttpResponse):
    """HTTP 401 UNAUTHENTICATED"""
    status_code = 401

    def __init__(self, typ='basic', realm="api"):
        super(Http401, self).__init__()
        if typ == 'basic':
            self['WWW-Authenticate'] = 'Basic realm="%s"' % realm
        else:
            assert False, 'Invalid type ' + str(typ)
            self.status_code = 403


class Http403(JSONErrorResponse, http.HttpResponseForbidden):
    """HTTP 403 FORBIDDEN"""
    pass


class Http404(JSONErrorResponse):
    """HTTP 404 Not Found"""
    status_code = 404


class Http409(JSONErrorResponse):
    """HTTP 409 Conflict"""
    status_code = 409


class Http500(JSONErrorResponse):
    """HTTP 500 Internal Server Error"""
    status_code = 500


class HttpError(Exception):
    """Exception that results in returning a JSONErrorResponse to the user."""

    def __init__(self, code, reason, **additional_data):
        super(HttpError, self).__init__(self, reason)
        self.response = JSONErrorResponse(reason, **additional_data)
        self.response.status_code = code

