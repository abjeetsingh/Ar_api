from flask import jsonify


def error(message="An unknown error occurred", code=500, data={}):
    raise Exception({"message": message, "code": code, "data": data})


def authentication_error(message="Not authenticated", data={}):
    error(message, 401, data)


def authorisation_error(message="Not authorised", data={}):
    error(message, 403, data)


def bad_request_error(message="Bad request", data={}):
    error(message, 400, data)


def not_found_error(message="Not found", data={}):
    error(message, 403, data)


# Handler

def error_response(e):
    if type(e.args[0]) is dict:
        message = e.args[0].get('message') or "An error occurred"
        code = e.args[0].get('code') or 500
        data = e.args[0].get("data") or {}

        return {"message": message, "success": False, "code": code, "data": data}
    return {"message": e.args[0], "success": False, "code": 500, "data": None}


def api_error_response(error):
    message, success, code, data = error_response(error).values()
    return jsonify({"success": success, "message": message, "code": code, "data": data}), code
