import os

admin_subdomain = "admin"
webapp_subdomain = "webapp"
port = os.environ.get("API_INTERNAL_PORT")
MONGO_CONNECTION_URI = os.environ.get("MONGO_CONNECTION_URI")
API_JWT_SECRET = os.environ.get("API_JWT_SECRET")

print("Config:\n")
print("admin_subdomain", admin_subdomain)
print("webapp_subdomain", webapp_subdomain)
print("mongoConnectino", MONGO_CONNECTION_URI)