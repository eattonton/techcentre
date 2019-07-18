from django.http import HttpResponse
#from utils.logger import Logger
import json
def cros(func):
    def wrapper(*args,**kwargs):
        response = func(*args,**kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    return wrapper


def jsonfy(func):
    def wrapper(*args,**kwargs):
        #Logger.list(func.__name__)
        #Logger.list(args)
        #Logger.list(kwargs)
        data,state = func(*args,**kwargs)
        obj1 = {"state": state, "data": data}
        str2 = json.dumps(obj1, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        response = HttpResponse(str2, content_type="application/json")
        return response
    return wrapper


