from api.mongo import _MongoClient
from passlib.hash import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
from pytz import timezone
class Users:
    def __init__(self):
        self.mongoClient = _MongoClient("users", "user_details")
        self.jwt_manager = JWTManager()

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        ist_tz = timezone('Asia/Kolkata')
        return datetime.now(ist_tz).isoformat()

    def create_user(self, name: str, email: str, password: str, module_accessible: list) -> dict:
        """Create a new user and store password securely in MongoDB."""
        # Ensure email is unique
        if self.mongoClient.find(query_object={'email': email}):
            return {"success": False, "message": "Email already exists"}

        # Hash the password
        hashed_password = bcrypt.hash(password)
        
        user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "module_accessible": module_accessible,
            "created_at": self._get_timestamp(),
        }
        
        self.mongoClient.insert_one(user)
        return {"success": True, "message": "User has been successfully created"}

    def login(self, email: str, password: str) -> dict:
        user = self.mongoClient.find(query_object={'email': email})[0]
        if user and bcrypt.verify(password, user['password']):
            # Generate JWT token
            access_token = create_access_token(
                identity=str(user['_id']),
                additional_claims={
                    "userData": {
                    "id": user['id'],
                    "name": user['name'],
                    "module_accessible": user['module_accessible'],
                    "email": user['email']
                }  # Use only the ID as the subject
                }
            )
            return {"success": True, "message": "Login successful", "access_token": access_token}
        return {"success": False, "message": "Invalid credentials"}

    
    @jwt_required()
    def change_password(self, current_password: str, new_password: str) -> dict:
        """Change the user's password."""
        current_user = get_jwt_identity()
        user = self.mongoClient.find_document_by_id(doc_id=current_user['id'])

        if not user:
            return {"success": False, "message": "User not found"}

        if bcrypt.verify(current_password, user['password']):
            hashed_new_password = bcrypt.hash(new_password)
            self.mongoClient.update_one(
                filter={"_id": user["_id"]},
                update={"$set": {"password": hashed_new_password}}
            )
            return {"success": True, "message": "Password changed successfully"}

        return {"success": False, "message": "Invalid current password"}

    @jwt_required()
    def update_user_info(self, name: str = None, email: str = None, module_accessible: list = None) -> dict:
        """Update user information."""
        current_user = get_jwt_identity()
        user = self.mongoClient.find_document_by_id(doc_id=current_user['id'])

        if not user:
            return {"success": False, "message": "User not found"}

        updated_data = {}
        if name:
            updated_data["name"] = name
        if email:
            import re
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"success": False, "message": "Invalid email format"}
            updated_data["email"] = email
        if module_accessible:
            updated_data["module_accessible"] = module_accessible

        if updated_data:
            updated_data["updated_at"] = self._get_timestamp()
            self.mongoClient.update_one(
                filter={"_id": user["_id"]},
                update={"$set": updated_data}
            )
            return {"success": True, "message": "User information updated successfully"}
        return {"success": False, "message": "No updates to make"}
    
    def delete_user(self, user_id: str) -> dict:
        """Delete a user by ID."""
        result = self.mongoClient.delete_one(filter={"id": user_id})
        if result.deleted_count > 0:
            return {"success": True, "message": "User deleted successfully"}
        return {"success": False, "message": "User not found"}

    def update_user(self, user_id: str, name: str = None, email: str = None, module_accessible: list = None) -> dict:
        """Update user information by ID."""
        user = self.mongoClient.find_document_by_id(doc_id= user_id)
        if not user:
            return {"success": False, "message": "User not found"}

        updated_data = {}
        if name:
            updated_data["name"] = name
        if email:
            import re
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"success": False, "message": "Invalid email format"}
            updated_data["email"] = email
        if module_accessible:
            updated_data["module_accessible"] = module_accessible

        if updated_data:
            updated_data["updated_at"] = self._get_timestamp()
            self.mongoClient.update_one(
                filter={"id": user_id},
                update={"$set": updated_data}
            )
            return {"success": True, "message": "User updated successfully"}
        return {"success": False, "message": "No updates to make"}