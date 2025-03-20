# How to use mongodb

--- Basic Connection ---
from backend.mongodb_config import MongoDBConfig

# Create config and connect
mongo = MongoDBConfig(db_name="uq")
mongo.connect()

# List collections
collections = mongo.list_collections()
print(collections)

# Close when done
mongo.close()

--- Quick testing ---
from backend.mongodb_config import test_mongodb_connection

# Run the test function
test_mongodb_connection()

--- working with collections ---
from backend.mongodb_config import connect_to_mongodb

# Connect
mongo = connect_to_mongodb()

# Get a specific collection
patients = mongo.get_collection("patients")

# Query data
results = list(patients.find({"age": {"$gt": 50}}))

# Close connection when done
mongo.close()