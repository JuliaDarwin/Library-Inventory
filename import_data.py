# import pandas as pd
# from pymongo import MongoClient
# import json
# import os
# from dotenv import load_dotenv

# CATEGORY_MAPPING = {
#     "Fisica i Química": "Física i Química",
#     "Humanitats diversos": "Humanitats Diversos",
#     "Divulgació i història de la mat": "Divulgació i història de la matemática"
# }

# def transform_json():
#     load_dotenv()
#     mongo_uri = os.getenv("MONGO_URI")
#     if mongo_uri:
#         mongo_uri = mongo_uri.replace("<", "").replace(">", "")
        
#     print("Connecting to MongoDB...")
#     client = MongoClient(mongo_uri or "mongodb://localhost:27017/", tlsAllowInvalidCertificates=True)
#     db = client["books_db"]
#     collection = db["books"]
    
#     # CAUTION: collection.delete_many({}) is commented out so running this script 
#     # will never wipe books added through the Streamlit web application.
#     # print("Clearing existing documents in collection...")
#     # collection.delete_many({})
    
#     file = "Biblioteca.xlsx"
#     print(f"Reading {file}...")
#     # Added header=1 because row 0 is just a title, and row 1 has the real headers (Autor, Títol, etc.)
#     sheets = pd.read_excel(file, sheet_name=None, header=1)  
    
#     final_json = {}
#     total_inserted = 0
    
#     for tab_name, df in sheets.items():
#         # Drop any empty columns that pandas parsed as 'Unnamed'
#         df = df.loc[:, [not (isinstance(col, str) and col.startswith("Unnamed")) for col in df.columns]]
        
#         # Fill empty cells (NaN) with empty strings so the JSON looks clean
#         df = df.fillna("")
#         tab_json = df.to_dict(orient='records')
#         category_name = CATEGORY_MAPPING.get(tab_name, tab_name)
#         final_json[category_name] = tab_json
        
#         # Add the normalized tab name as a 'Categoria' field to each book
#         for book in tab_json:
#             book["Categoria"] = category_name
            
#         # Insert the list of books into the collection (if the list isn't empty)
#         if tab_json:
#             collection.insert_many(tab_json)
#             total_inserted += len(tab_json)

#     # Save everything to a JSON file
#     print("Saving output to output.json...")
#     with open("output.json", "w", encoding="utf-8") as json_file:
#         json.dump(final_json, json_file, indent=4, ensure_ascii=False, default=str)
        
#     print(f"Migration completed successfully! Imported {total_inserted} books into MongoDB.")

# if __name__ == "__main__":
#     transform_json()
