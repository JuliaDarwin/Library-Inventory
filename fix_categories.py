import os
from dotenv import load_dotenv
from pymongo import MongoClient

def fix_categories():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        mongo_uri = mongo_uri.replace("<", "").replace(">", "")
        
    print("Connecting to MongoDB...")
    client = MongoClient(mongo_uri or "mongodb://localhost:27017/", tlsAllowInvalidCertificates=True)
    db = client["books_db"]
    collection = db["books"]
    
    category_updates = {
        "Fisica i Química": "Física i Química",
        "Humanitats diversos": "Humanitats Diversos",
        "Divulgació i història de la mat": "Divulgació i història de la matemática"
    }
    
    print("\nUpdating categories in MongoDB Atlas...")
    total_modified = 0
    for old_cat, new_cat in category_updates.items():
        result = collection.update_many(
            {"Categoria": old_cat},
            {"$set": {"Categoria": new_cat}}
        )
        print(f"  • Fixed '{old_cat}' ➔ '{new_cat}': updated {result.modified_count} books")
        total_modified += result.modified_count
        
    print(f"\nDone! Successfully updated {total_modified} books without removing any added books.")

if __name__ == "__main__":
    fix_categories()
