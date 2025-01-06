from api.mongo import _MongoClient
from pytz import timezone
from datetime import datetime
from bson.objectid import ObjectId

class model:
    def __init__(self):
        self.mongoClient = _MongoClient("model", "models")  # Database: "model", Collection: "models"

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        ist_tz = timezone('Asia/Kolkata')
        return datetime.now(ist_tz).isoformat()

    def create_model(self, name, url):
        """Create a new model in the database."""
        model = {
            "name": name,
            "url": url,
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp()
        }
        inserted_id = self.mongoClient.insert_one(model).inserted_id
        return {"success": True, "message": "The model has been successfully stored", "id": str(inserted_id)}

    def get_model_by_id(self, id):
        """Retrieve a model by its ID."""
        try:
            document = self.mongoClient.find_document_by_id(doc_id=id)
            if not document:
                return {"success": False, "message": "Model not found"}
            return {"success": True, "data": document}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_model_by_id(self, id):
        """Delete a model by its ID."""
        try:
            delete_result = self.mongoClient.delete_one({"_id": ObjectId(id)})
            if delete_result.deleted_count == 0:
                return {"success": False, "message": "Model not found"}
            return {"success": True, "message": "Model deleted successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def update_model(self, id, name=None, url=None):
        """Update a model's details by its ID."""
        try:
            update_fields = {}
            if name:
                update_fields["name"] = name
            if url:
                update_fields["url"] = url
            if not update_fields:
                return {"success": False, "message": "No fields to update"}

            update_fields["updated_at"] = self._get_timestamp()

            update_result = self.mongoClient.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_fields}
            )

            if update_result.matched_count == 0:
                return {"success": False, "message": "Model not found"}
            
            return {"success": True, "message": "Model updated successfully"}
        except Exception as e:
            return {"success": False, "message": str(e)}