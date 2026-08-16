import os
import json
import re
import unicodedata
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

import datetime

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ObjectId, datetime.datetime, datetime.date)):
            return str(o)
        return super().default(o)

def normalize(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", "", s).lower().strip()
    return s

def run_deletion():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        mongo_uri = mongo_uri.replace("<", "").replace(">", "")

    print("Connecting to MongoDB Atlas...")
    client = MongoClient(mongo_uri or "mongodb://localhost:27017/", tlsAllowInvalidCertificates=True)
    db = client["books_db"]
    collection = db["books"]

    all_books = list(collection.find({}))
    total_before = len(all_books)
    print(f"Total documents found in MongoDB: {total_before}")

    # Step 1: Create backup
    backup_file = "books_backup.json"
    print(f"Creating safety backup in '{backup_file}'...")
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(all_books, f, indent=4, ensure_ascii=False, cls=JSONEncoder)
    print(f"Backup created successfully with {len(all_books)} records.")

    # Step 2: Group books by normalized (title, author)
    grouped = {}
    for b in all_books:
        t = normalize(b.get("Títol", ""))
        a = normalize(b.get("Autor", ""))
        if not t:
            continue
        grouped.setdefault((t, a), []).append(b)

    to_delete_ids = []
    cat_gen_deleted_count = 0

    for (t, a), books in grouped.items():
        cat_gen_books = [b for b in books if b.get("Categoria") == "Catàleg general"]
        other_cat_books = [b for b in books if b.get("Categoria") != "Catàleg general"]

        if cat_gen_books and other_cat_books:
            # Delete all Catàleg general entries since book exists in specific category/categories
            for b in cat_gen_books:
                to_delete_ids.append(b["_id"])
                cat_gen_deleted_count += 1
        elif len(cat_gen_books) > 1 and not other_cat_books:
            # Book exists multiple times ONLY in Catàleg general; keep 1, delete extra copies
            for b in cat_gen_books[1:]:
                to_delete_ids.append(b["_id"])
                cat_gen_deleted_count += 1

    print(f"\nFound {len(to_delete_ids)} duplicate 'Catàleg general' records to delete.")
    print(f"Expected remaining documents in database: {total_before - len(to_delete_ids)}")

    if to_delete_ids:
        print("\nDeleting duplicates from MongoDB...")
        result = collection.delete_many({"_id": {"$in": to_delete_ids}})
        print(f"Successfully deleted {result.deleted_count} documents from MongoDBAtlas.")

    # Step 3: Fetch updated remaining books
    remaining_books = list(collection.find({}))
    total_after = len(remaining_books)
    print(f"Total documents remaining in MongoDB: {total_after}")

    # Step 4: Regenerate output.json grouped by Categoria
    output_data = {}
    for b in remaining_books:
        cat = b.get("Categoria", "Catàleg general")
        book_clean = {k: v for k, v in b.items() if k != "_id"}
        output_data.setdefault(cat, []).append(book_clean)

    print("Updating 'output.json'...")
    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, indent=4, ensure_ascii=False, default=str)
    print("'output.json' updated successfully.")

    # Step 5: Regenerate duplicates_report.json for remaining duplicates (if any)
    report = []
    regrouped = {}
    for cat, books in output_data.items():
        for b in books:
            t = normalize(b.get("Títol", ""))
            a = normalize(b.get("Autor", ""))
            if t:
                regrouped.setdefault((t, a), []).append(b)

    remaining_dups = [books for key, books in regrouped.items() if len(books) > 1]
    for books in sorted(remaining_dups, key=lambda x: x[0].get("Títol", "")):
        book_info = {
            "Títol": books[0].get("Títol", ""),
            "Autor": books[0].get("Autor", ""),
            "Occurrences": []
        }
        for b in books:
            book_info["Occurrences"].append({
                "Categoria": b.get("Categoria", ""),
                "Editorial": b.get("Editorial", ""),
                "Any": b.get("Any", "")
            })
        report.append(book_info)

    with open("duplicates_report.json", "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=4, ensure_ascii=False, cls=JSONEncoder)
    print(f"Updated 'duplicates_report.json' with {len(report)} remaining duplicate groups.")

    print("\nDeletion & sync completed successfully!")

if __name__ == "__main__":
    run_deletion()
