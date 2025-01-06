from flask import jsonify
from settings import port
from api.flask_app import app
#from flask import Flask


@app.route("/")
def index():
    return jsonify({"success": True, "👋": "🌏"})

@app.route("/mongo")
def MongoCheck():
   return jsonify({"success": True, "👋": "🌏"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
