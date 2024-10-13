import os
from pymongo import MongoClient

def empty_database():
    # MongoDB connection details
    mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost')
    mongo_port = os.getenv('MONGODB_PORT', '27018')
    database_name = os.getenv('MONGODB_DATABASE', 'mydatabase')  # Replace with your database name
    collection_name = 'batch'  # The collection you want to empty

    # Connect to MongoDB
    client = MongoClient(f"{mongo_url}:{mongo_port}/")
    db = client[database_name]
    collection = db[collection_name]

    # Delete all documents in the collection
    deleted_count = collection.delete_many({}).deleted_count
    print(f"Deleted {deleted_count} documents from the '{collection_name}' collection.")

if __name__ == "__main__":
    empty_database()
