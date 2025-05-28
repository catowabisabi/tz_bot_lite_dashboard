import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from bson import json_util

load_dotenv(override=True)


from datetime import datetime
from zoneinfo import ZoneInfo


ny_time = datetime.now(ZoneInfo("America/New_York"))
today_str = ny_time.strftime('%Y-%m-%d')


class MongoHandler:

    #region Constructor
    def __init__(self):
        try:
            mongo_uri = os.getenv("MONGODB_CONNECTION_STRING")
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[os.getenv("MONGO_DBNAME", "TradeZero_Bot")]
        except Exception as e:
            print(f"Connection error: {e}")
            self.client = None
            self.db = None


    #region Is Connected
    def is_connected(self):
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False


    #region Find Collection
    def find_collection(self, name):
        if not self.is_connected():
            return False
        collections = self.db.list_collection_names()
        return True if name in collections else []


    #region Create Collection
    def create_collection(self, name):
        if not self.is_connected():
            return False
        if name not in self.db.list_collection_names():
            self.db.create_collection(name)
            return True
        return False


    #region Create Document
    def create_doc(self, collection_name, doc):
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            # 加入今天日期
            doc["today_date"] = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
            result = self.db[collection_name].insert_one(doc)
            return result.inserted_id
        except Exception as e:
            print(f"Insert error: {e}")
            return None


    #region Find Document
    def find_doc(self, collection_name, query):
        if not self.is_connected():
            return []
        if collection_name not in self.db.list_collection_names():
            return []
        try:
            return list(self.db[collection_name].find(query))
        except Exception as e:
            print(f"Find error: {e}")
            return []


    #region Update Document
    def update_doc(self, collection_name, query, update):
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            result = self.db[collection_name].update_many(query, {'$set': update})
            return result.modified_count  # 回傳更新的筆數
        except Exception as e:
            print(f"Update error: {e}")
            return None


    #region Upsert Document

    def upsert_doc(self, collection_name, query_keys: dict, new_data: dict):
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None

        try:
            # 加入今天日期
            new_data["today_date"] = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')

            result = self.db[collection_name].update_one(
                filter=query_keys,
                update={"$set": new_data},
                upsert=True
            )
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
        except Exception as e:
            print(f"Upsert error: {e}")
            return None
        
    #region Upsert Top List
    def upsert_top_list(self, collection_name: str, new_symbols: list):
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None

        try:
            today_str = datetime.now(ZoneInfo("America/New_York")).strftime('%Y-%m-%d')
            query = {"today_date": today_str}

            existing_doc = self.db[collection_name].find_one(query)

            if existing_doc and "top_list" in existing_doc:
                combined_list = list(set(existing_doc["top_list"] + new_symbols))
            else:
                combined_list = new_symbols

            result = self.db[collection_name].update_one(
                filter=query,
                update={"$set": {
                    "today_date": today_str,
                    "top_list": combined_list
                }},
                upsert=True
            )

            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }

        except Exception as e:
            print(f"Upsert error: {e}")
            return None
    

    #region Delete Document                 
    def delete_doc(self, collection_name, query):
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            result = self.db[collection_name].delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f"Delete error: {e}")
            return None
        

    #region Find One
    def find_one(self, collection_name, query):
        print(f"Finding one in {collection_name} with query: {query}")
        """查找单个文档"""
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            return self.db[collection_name].find_one(query)
        except Exception as e:
            print(f"Find one error: {e}")
            return None

    #region Update One
    def update_one(self, collection_name, query, update):
        print(f"Updating one in {collection_name} with query: {query} and update: {update}")
        """更新单个文档"""
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            result = self.db[collection_name].update_one(query, {'$set': update})
            return {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count
            }
        except Exception as e:
            print(f"Update one error: {e}")
            return None
    #region Delete One
    def delete_one(self, collection_name, query):
        """删除单个文档"""
        if not self.is_connected():
            return None
        if collection_name not in self.db.list_collection_names():
            return None
        try:
            result = self.db[collection_name].delete_one(query)
            return result.deleted_count
        except Exception as e:
            print(f"Delete one error: {e}")
            return None
        




if __name__ == "__main__":
    mongo_handler = MongoHandler()
    print(f"Document is found: {mongo_handler.find_doc('fundamentals_of_top_list_symbols', {'today_date': today_str})}")
    
