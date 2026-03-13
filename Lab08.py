from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import datetime

app = Flask(__name__)

# Replace with your MongoDB connection string (local or Atlas)
# Example local: "mongodb://localhost:27017/"
# Example Atlas: "mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>..."
app.config["MONGO_URI"] = "<your-mongodb-connection-string>"

mongo_client = MongoClient(app.config["MONGO_URI"])
db = mongo_client.bookmark_manager # The database will be created automatically on first use
bookmarks_collection = db.bookmarks

# Helper function to serialize MongoDB ObjectId to string
def serialize_bookmark(bookmark):
    bookmark['_id'] = str(bookmark['_id'])
    return bookmark

@app.route("/")
def home():
    return "Bookmark Manager API is running. Use /add_bookmark and /bookmarks/<tag> endpoints."

# Endpoint to add a new bookmark
@app.route("/add_bookmark", methods=["POST"])
def add_bookmark():
    data = request.get_json()
    if not data or 'url' not in data or 'title' not in data:
        return jsonify({"error": "Missing title or URL"}), 400

    bookmark = {
        "title": data["title"],
        "url": data["url"],
        "tags": data.get("tags", []), # Expects a list of tags
        "created_at": datetime.datetime.utcnow()
    }
    
    result = bookmarks_collection.insert_one(bookmark)
    return jsonify({"message": "Bookmark added successfully", "id": str(result.inserted_id)}), 201


# Endpoint to retrieve bookmarks by tag
@app.route("/bookmarks/<tag>", methods=["GET"])
def get_bookmarks_by_tag(tag):
    # Find bookmarks where the 'tags' array contains the specified tag
    found_bookmarks = bookmarks_collection.find({"tags": tag})
    
    # Convert cursor to list and serialize ObjectIds
    bookmarks_list = [serialize_bookmark(bookmark) for bookmark in found_bookmarks]
    
    return jsonify(bookmarks_list), 200

if __name__ == "__main__":
    # Ensure MongoDB connection is established (lazy creation happens on first insert)
    try:
        mongo_client.admin.command('ping')
        print("MongoDB connected successfully!")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    app.run(debug=True)
