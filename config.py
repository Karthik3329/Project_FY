from pymongo import MongoClient

MongoClient("your_atlas_connection_string")
db = MongoClient["liver_prediction"]

users_collection = db["users"]
predictions_collection = db["predictions"]