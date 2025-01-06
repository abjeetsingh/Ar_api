from pymongo import MongoClient, results
from datetime import datetime, timedelta
from settings import MONGO_CONNECTION_URI
from bson.objectid import ObjectId
import json
from typing import Union, Any, Mapping, NoReturn


class _MongoClient:
    def __init__(self, collection_name, db_name, ttl=None) -> None:
        self._db_url = MONGO_CONNECTION_URI
        self._db_name = db_name
        self._collection_name = collection_name
        self._db = None
        self._collection = None
        self._client = None
        self._last_refresh_time = None
        self._ttl = ttl

    def _setup_ttl_index(self) -> None:
        self._collection.create_index([("timestamp", 1)], expireAfterSeconds=self._ttl)

    def init_mongo(self) -> None:
        print("DB URL", self._db_url)
        if self._client is None or (
            datetime.now() - self._last_refresh_time > timedelta(hours=1)
        ):
            if self._client is not None:
                self._client.close()
            self._client = MongoClient(self._db_url)
            self._db = self._client[self._db_name]
            self._collection = self._db[self._collection_name]
            if self._ttl:
                self._setup_ttl_index()
            self._last_refresh_time = datetime.now()

    def insert_one(self, data: dict):
        self.init_mongo()
        return self._collection.insert_one(data)

    def get_collection(
        self,
        page: int = 0,
        items_per_page: int = 0,
        sort: Union[dict, None] = None,
        _filter: Union[dict, None] = None,
    ) -> Union[dict[str, Any], list[Any]]:
        self.init_mongo()
        collection = []
        skip = items_per_page * (int(page) - 1)
        limit = int(items_per_page)
        mongo_filter = _filter or {}
        for document in (
            self._collection.find(filter=mongo_filter, skip=skip, limit=limit)
            if not sort
            else self._collection.find(filter=mongo_filter, skip=skip, limit=limit).sort(
                sort.get("field"), sort.get("order")
            )
        ):
            collection.append(document)
        return json.loads(json.dumps(collection, default=str))

    def get_collection_length(self, filter={}):
        return int(self._collection.count_documents(filter=filter))

    def find_document_by_id(self, doc_id: int) -> Union[dict, None]:
        self.init_mongo()
        if ObjectId.is_valid(doc_id):
            doc_id = ObjectId(doc_id)

        return self._collection.find_one({"_id": doc_id})
    
    def find(self, query_object: dict) -> Union[list, NoReturn]:
        self.init_mongo()
        return list(self._collection.find(query_object))
    

    def upsert_document_with_custom_id(self, doc_id: int, data: dict) -> bool:
        self.init_mongo()
        data["_id"] = doc_id
        result = self._collection.update_one(
            {"_id": doc_id}, {"$set": data}, upsert=True
        )
        return result.acknowledged

    def get_aggregate(self, aggregation_pipeline):
        self.init_mongo()
        return list(self._collection.aggregate(aggregation_pipeline))

    def get_email_delivery(self, payload, fields_to_include):
        self._client = MongoClient(self._db_url)
        self._db = self._client[self._db_name]
        try:
            print("Getting data from MongoDB")
            filter_query = {}
            if payload["userSearch"]["csvId"]:
                filter_query["csv_import_id"] = payload["userSearch"]["csvId"]

            if payload["userSearch"]["status"]:
                filter_query["status"] = payload["userSearch"]["status"]

            if payload["userSearch"]["email"]:
                filter_query["email"] = payload["userSearch"]["email"]

            if (
                payload["userSearch"]["startDate"]
                and payload["userSearch"]["startDate"]
            ):
                start_date = datetime.strptime(
                    payload["userSearch"]["startDate"], "%Y-%m-%d"
                )
                end_date = datetime.strptime(
                    payload["userSearch"]["startDate"], "%Y-%m-%d"
                )

                start_of_day = start_date.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_of_day = end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999
                )

                filter_query["$and"] = [
                    {"createdAt": {"$gte": start_of_day}},
                    {"updatedAt": {"$lte": end_of_day}},
                ]

            projection = fields_to_include or {}
            projection["_id"] = 0

            results = list(self._db.email_deliveries.find(filter_query, projection))
            return results

        except Exception as e:
            print(f"Error while getting data from MongoDB: {str(e)}")
            return None

    def get_user_bulk_onboard_import(self, csv_import_id):
        try:
            self.init_mongo()
            print("Getting data from MongoDB")

            csv_import_id = int(csv_import_id)
            results = list(
                self._collection.find(
                    {
                        "csv_import_id": {"$eq": csv_import_id},
                    }
                )
            )
            for data in results:
                data.pop("_id", None)

            return results

        except Exception as e:
            print(f"Error while getting data from MongoDB: {str(e)}")
            return None
        
    def delete_many(self, query_object: Mapping[str,Any]) -> results.DeleteResult:
        self.init_mongo()
        return self._collection.delete_many(filter=query_object)
    
    def delete_one(self, query_object: Mapping[str,Any]) -> results.DeleteResult:
        self.init_mongo()
        return self._collection.delete_one(filter=query_object)
    

    def update_entity(self, update_query: dict, value_object: dict) -> results.UpdateResult:
        self.init_mongo()
        return self._collection.update_one(update_query, {"$set": value_object})

    def increment_attribute(self, update_query: dict, attribute_name: str) -> results.UpdateResult:
        self.init_mongo()
        return self._collection.update_one(update_query, {"$inc": {f"{attribute_name}": 1}})
    
    def decrement_attribute(self, update_query: dict, attribute_name: str) -> results.UpdateResult:
        self.init_mongo()
        return self._collection.update_one(update_query, {"$inc": {f"{attribute_name}": -1}})
    