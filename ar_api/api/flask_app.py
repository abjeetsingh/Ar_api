import datetime
import json
import time

from flask import Flask, g, request
from flask_cors import CORS
from api.controller.api import api
from flask_jwt_extended import JWTManager
from settings import API_JWT_SECRET

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = API_JWT_SECRET
jwt = JWTManager(app)
app.register_blueprint(api)
print("This file is changed again")



# Create the api route for loadbalancer health check
@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200


# @app.before_request
# def before_request():
#     g.start_time = time.time()
#     g.request_payload = request.data.decode('utf-8')


# mongo_logger = MongoDBLogger()


# @app.teardown_request
# def teardown_request(exception=None):
#     response_time = time.time() - g.start_time
#     response_status = getattr(g, 'response_status', 200)
#     date_key = datetime.datetime.now().strftime('%d-%m-%y')
#     request_path = request.path
#     timestamp = datetime.datetime.now()

#     mongo_logger.log_request(
#         response_status=response_status,
#         request_path=request_path,
#         date_key=date_key,
#         response_time=response_time,
#         ip=request.remote_addr,
#         user_agent=request.user_agent.string,
#         request_payload=g.request_payload,
#         timestamp=timestamp
#     )


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(0, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o)

        return json.JSONEncoder.default(self, o)


# sentry_sdk.init(
#     dsn="https://ef2ed9d66badce73ec12b89ade082786@o4505809383653376.ingest.sentry.io/4505809806163968",
#     integrations=[FlaskIntegration()],
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )

app.debug = True
app.json_encoder = JSONEncoder
app.config["CORS_HEADERS"] = "Content-Type/js"
CORS(app, resources={r"/*": {"origins": "*"}})
