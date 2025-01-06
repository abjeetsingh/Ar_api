from flask import Blueprint, jsonify, request
from api.model import model
from bson import ObjectId
import json
import traceback
from api.errors import (
    authentication_error,
    authorisation_error,
    api_error_response,
)
from flask_jwt_extended import jwt_required
from api.users import Users
api = Blueprint("api", __name__, url_prefix="/api")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)
    
api.json_encoder = CustomJSONEncoder

@api.route("/", methods=["GET"])
def fun():

    return jsonify({"succes":False})

@api.route("/userCreate", methods=["POST"])
def createUser():
    try:
        payload = json.loads(request.data)
        response = Users().create_user(name=payload.get("name"), email=payload.get("email"), password=payload.get("password"), module_accessible=payload.get("module_accessible"))
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)


@api.route("/login", methods=["POST"])
def loginUser():
    try:
        payload = json.loads(request.data)
        return Users().login(email=payload.get("email"), password=payload.get("password"))
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)    
    
@api.route("/user/<user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    try:
        payload = json.loads(request.data)
        name = payload.get("name")
        email = payload.get("email")
        module_accessible = payload.get("module_accessible")
        response = Users().update_user(
            user_id=user_id, name=name, email=email, module_accessible=module_accessible
        )
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)

@api.route("/user/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        response = Users().delete_user(user_id=user_id)
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)


#i want to protect the following routes
@api.route("/model", methods=["POST"])
@jwt_required()
def createModel():
    try:
        payload = json.loads(request.data)
        url=payload.get("url")
        name=payload.get("name")
        if(not name or not url): 
            return jsonify({"success":False, "message":"Name and URL are required"})
        response = model().create_model(name=name, url=url)
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e) 
    
@api.route("/model", methods=["GET"])
@jwt_required()
def GetModel():
    try:
        payload = request.args
        id = payload.get("id")
        if(not id): 
            return jsonify({"success":False, "message":"Id is required"})
        response = model().get_model_by_id(id=payload.get("id"))
        return jsonify({
            "success":True,
            "data":response
        })
        # return jsonify({"succes":False})
    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)

    # return jsonify({"succes":False})

@api.route("/model", methods=["PUT"])
@jwt_required()
def updateModel():
    """
    Update a model's details by its ID.
    """
    try:
        payload = json.loads(request.data)
        id = payload.get("id")
        name = payload.get("name")
        url = payload.get("url")

        if not id:
            return jsonify({"success": False, "message": "Model ID is required"})

        if not (name or url):
            return jsonify({"success": False, "message": "At least one of 'name' or 'url' is required"})

        response = model().update_model(id=id, name=name, url=url)
        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)


@api.route("/model", methods=["DELETE"])
@jwt_required()
def deleteModel():
    """
    Delete a model by its ID.
    """
    try:
        payload = request.args
        id = payload.get("id")

        if not id:
            return jsonify({"success": False, "message": "Model ID is required"})

        response = model().delete_model_by_id(id=id)
        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return api_error_response(e)