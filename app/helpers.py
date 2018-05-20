# response ajax
from django.http import HttpResponse
import urllib2
import json


class HttpResponseAjax(HttpResponse):
    def __init__(self, status='ok', **kwargs):
        kwargs['status'] = status
        super(HttpResponseAjax, self).__init__(
            content=json.dumps(kwargs),
            content_type='application/json',
        )


class HttpResponseAjaxError(HttpResponseAjax):
    def __init__(self, code, id, identificate, message):
        super(HttpResponseAjaxError, self).__init__(
            status='error', code=code, message=message,id=id,identificate=identificate
        )