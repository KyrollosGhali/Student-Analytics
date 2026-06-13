from pymongo import MongoClient
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv(".env")
uri = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "student_analytics")
client = MongoClient(uri)

db = client[MONGO_DB]

for file in os.listdir("cleaned_data"):
    if file.endswith(".csv"):
        collection_name = file.split(".")[0]
        if collection_name in db.list_collection_names():
            print(f"Collection '{collection_name}' already exists. Skipping upload for {file}.")
        else:
            collection = db[collection_name]
            with open(os.path.join("cleaned_data", file), "r") as f:
                header = f.readline().strip().split(",")
                for line in f:
                    values = line.strip().split(",")
                    document = {header[i]: values[i] for i in range(len(header))}
                    collection.insert_one(document)
            print(f"Data from {file} uploaded to MongoDB collection '{collection_name}'.")