from streamlit.elements.widgets.number_input import Number
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import json
import streamlit as st
import numpy as np

load_dotenv()

# Page configuration
st.set_page_config(page_title="Biblioteca Pares", page_icon="📚", layout="wide")

# Simple passcode protection
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Accés Restringit")
    password = st.text_input("Introdueix la contrasenya per accedir a la biblioteca:", type="password")
    if st.button("Entrar"):
        correct_password = os.getenv("APP_PASSWORD", "biblioteca123")
        if password == correct_password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contrasenya incorrecta. Torna-ho a provar.")
    st.stop()

# MongoDB connection
@st.cache_resource
def get_db_collection():
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        mongo_uri = mongo_uri.replace("<", "").replace(">", "")
        
    client = MongoClient(mongo_uri or "mongodb://localhost:27017/", tlsAllowInvalidCertificates=True)
    db = client["books_db"]
    return db["books"]

bookCollection = get_db_collection()


# Basic UI
st.title("📚 Biblioteca Coronel Pedo")

try:
    count = bookCollection.count_documents({})
    st.write(f"Total de llibres a la base de dades: **{count}**")
except Exception as e:
    st.error(f"Error connectant a MongoDB: {e}")

#-----MENÚ LATERAL
st.sidebar.title("Navegació")
menu = st.sidebar.radio("Anar a:", [
    "Veure Llibres", 
    "Afegir nou Llibre",
    "Estadístiques"
])

# ------ STATE INITIALIZATION
if "contador_reset" not in st.session_state:
    st.session_state.contador_reset = 0

if "confirm_payload" not in st.session_state:
    st.session_state.confirm_payload = None

if "editing_book" not in st.session_state:
    st.session_state.editing_book = None

def resetForm():
    st.session_state.contador_reset += 1
    st.session_state.confirm_payload = None
    st.rerun()

# -------- MODALS DE CONFIRMACIO DE LA OPERACIO
def modal_confirmar(data, operation):
    st.write(f"### Resum de l'operació")
    st.json(data)
    st.warning("Esteu segurs de procedir?")
    
    col1, col2 = st.columns(2) #creates 2 buttons side by side
    if col1.button("✅ Sí, continuar"):
        if operation == "insertar":
            bookCollection.insert_one(data)
            st.success("Llibre guardat!")
        elif operation == "eliminar":
            bookCollection.delete_one({"_id": data["_id"]})
            st.success("Llibre Eliminat!")
        elif operation == "update":
            update_data = data.copy()
            update_data.pop("operation", None)
            bookCollection.update_one({"_id": data["_id"]}, {"$set": update_data})
            st.success("Llibre modificat!")
                
            
        import time
        time.sleep(2)
        resetForm()
        
    if col2.button("❌ No, cancel·lar"):
        resetForm()





#----------- veure llibres + search page



def getBooksByCategory(category):
    allBooks = get_db_collection()
    query = {} if category == "Tots" else {"Categoria": category}
    selectedBooks = list(allBooks.find(query))
    if selectedBooks:
        original_books = [book.copy() for book in selectedBooks]
        for book in selectedBooks:
            book.pop("_id", None)
        df = pd.DataFrame(selectedBooks).astype(str)
        
        results = st.dataframe(df, on_select="rerun", selection_mode="single-row", width="stretch")
        selectedRows = results["selection"]["rows"]
        
        if selectedRows:
            selected_book = original_books[selectedRows[0]]
            if st.button("Eliminar llibre/s"):
                st.session_state.confirm_payload = selected_book
                st.session_state.confirm_payload["operation"] = "eliminar"
                st.rerun()
    else:
        st.write("No books found in this category")

def getBooksBySearch(searchOption, searchQuery):
    allBooks = get_db_collection()
    query = {searchOption: {
        "$regex": searchQuery,
        "$options": "i"
    }}
    selectedBooks = list(allBooks.find(query))
    if selectedBooks:
        original_books = [book.copy() for book in selectedBooks]
        for book in selectedBooks:
            book.pop("_id", None)   
        df = pd.DataFrame(selectedBooks).astype(str)
        results = st.dataframe(df, on_select="rerun", selection_mode="single-row", width="stretch")
        selectedRows = results["selection"]["rows"]
        
        if selectedRows:
            selected_book = original_books[selectedRows[0]]
            if st.button("Eliminar llibre"):
                st.session_state.confirm_payload = selected_book
                st.session_state.confirm_payload["operation"] = "eliminar"
                st.rerun()
            if st.button("Modificar llibre") or (st.session_state.editing_book and st.session_state.editing_book["_id"] == selected_book["_id"]):
                st.session_state.editing_book = selected_book
                cats = ["Tots", "Catàleg general", "Literatura estrangera", "Literatura catalana", "Biografies-Memòries", "Història", "Filosofia", "Assaig", "Economia", "Humanitats Diversos", "Matemàtiques", "Física i Química", "Divulgació física i química", "Ciències naturals", "Ciència diversos", "Divulgació ciències naturals", "Divulgació i història de la matemática", "Història de la ciència"]
                current_cat = selected_book.get("Categoria", "Tots")
                try:
                    cat_idx = cats.index(current_cat)
                except ValueError:
                    cat_idx = 0
                
                titol = st.text_input("Títol", value=selected_book["Títol"])
                autor = st.text_input("Autor", value=selected_book["Autor"])
                editorial = st.text_input("Editorial", value=selected_book["Editorial"])
                any_llibre = st.number_input("Any", value=int(selected_book["Any"]))
                categoria = st.selectbox("Categoria", cats, index=cat_idx)
                
                if st.button("Guardar canvis"):
                    updated_book = selected_book.copy()
                    updated_book["Títol"] = titol
                    updated_book["Autor"] = autor
                    updated_book["Editorial"] = editorial
                    updated_book["Any"] = any_llibre
                    updated_book["Categoria"] = categoria
                    updated_book["operation"] = "update"
                    
                    st.session_state.confirm_payload = updated_book
                    st.session_state.editing_book = None
                    st.rerun()


                    
    else:
        st.write("No books found")

def getBooksByCategoryAndSearch(category, search_query):
    allBooks = get_db_collection()
    query = {}
    
    if category != "Tots":
        query["Categoria"] = category
        
    if search_query.strip():
        query["$or"] = [
            {"Títol": {"$regex": search_query, "$options": "i"}},
            {"Autor": {"$regex": search_query, "$options": "i"}}
        ]
        
    selectedBooks = list(allBooks.find(query))
    if selectedBooks:
        original_books = [book.copy() for book in selectedBooks]
        for book in selectedBooks:
            book.pop("_id", None)
        df = pd.DataFrame(selectedBooks).astype(str)
        
        results = st.dataframe(df, on_select="rerun", selection_mode="single-row", width="stretch")
        selectedRows = results["selection"]["rows"]
        
        if selectedRows:
            selected_book = original_books[selectedRows[0]]
            if st.button("Eliminar llibre/s"):
                st.session_state.confirm_payload = selected_book
                st.session_state.confirm_payload["operation"] = "eliminar"
                st.rerun()
    else:
        st.write("No books found matching this filter.")

    


if menu == "Veure Llibres":
    if st.session_state.confirm_payload is not None:
        operation = st.session_state.confirm_payload.get("operation", "eliminar")
        modal_confirmar(st.session_state.confirm_payload, operation)
    else:
        st.subheader("Cerca de Llibres:")
        searchOption = st.selectbox("Opcions de cerca:", ["Títol", "Autor", "Categoria", "Editorial"])

        if searchOption == "Categoria":
            category = st.selectbox("Escollir una categoria: ", ["Tots", "Catàleg general", "Literatura estrangera", "Literatura catalana", "Biografies-Memòries", "Història", "Filosofia", "Assaig", "Economia", "Humanitats Diversos", "Matemàtiques", "Física i Química", "Divulgació física i química", "Ciències naturals", "Ciència diversos", "Divulgació ciències naturals", "Divulgació i història de la matemática", "Història de la ciència"])
            searchQuery = st.text_input("Filtrar per títol o autor (opcional):")
            # getBooksByCategory(category)
            getBooksByCategoryAndSearch(category, searchQuery)
            
        else:
            searchQuery = st.text_input("Escriu aquí la teva cerca:")
            getBooksBySearch(searchOption, searchQuery)


# -------------ADD BOOK PAGE
if menu == "Afegir nou Llibre":
    st.subheader("Registre de Llibres")

    if st.session_state.confirm_payload is not None:
        modal_confirmar(st.session_state.confirm_payload, "insertar")
    else:
        c1, c2 = st.columns(2)

        with c1:
            title = st.text_input("Títol", key=f"titol_{st.session_state.contador_reset}")
            author = st.text_input("Autor", key=f"autor_{st.session_state.contador_reset}")
            cathegory = st.selectbox("Categoria", ["Catàleg general", "Literatura estrangera", "Literatura catalana", "Biografies-Memòries", "Història", "Filosofia", "Assaig", "Economia", "Humanitats Diversos", "Matemàtiques", "Física i Química", "Divulgació física i química", "Ciències naturals", "Ciència diversos", "Divulgació ciències naturals", "Divulgació i història de la matemática", "Història de la ciència"], key=f"cat_{st.session_state.contador_reset}")
        with c2:
            editorial = st.text_input("Editorial", key=f"edit_{st.session_state.contador_reset}")
            year = st.number_input("Any", min_value=1800, step=1, key=f"any_{st.session_state.contador_reset}")

        blocked = False
        if not title.strip():
            blocked = True
            st.warning("Has d'afegir un títol")
        
        if st.button("Registrar Llibre", disabled=blocked):
            st.session_state.confirm_payload = {
                "Autor": author,
                "Títol": title,
                "Editorial": editorial,
                "Any": year,
                "Categoria": cathegory,
            }
            st.rerun()
#_______________ STATISTICS

if menu == "Estadístiques":
    st.subheader("Estadístiques")
    st.write(f"Total de llibres: {bookCollection.count_documents({})}")
    st.markdown("### Llibres per categories")

    # Aggregate counts by category from MongoDB
    pipeline = [
        {"$group": {"_id": "$Categoria", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    category_counts = list(bookCollection.aggregate(pipeline))

    # Render metrics in rows of 4 columns
    cols_per_row = 4
    for i in range(0, len(category_counts), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(category_counts):
                item = category_counts[i + j]
                cat_name = item["_id"] or "Sense categoria"
                count = item["count"]
                cols[j].metric(cat_name, count)