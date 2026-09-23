# Biblioteca Pares

## Overview
Biblioteca Pares is a web-based library management application built with Python and Streamlit, backed by a MongoDB database. It provides an intuitive interface for managing a personal or organizational book inventory, allowing users to track, search, and organize their collection efficiently.

## Features
- **Authentication**: Secure access to the library system via a passcode.
- **Book Catalog**: Browse the entire collection of books.
- **Advanced Search**: Filter books by category, title, author, or publisher.
- **Book Management**:
  - Add new books to the database with details like Title, Author, Editorial, Year, and Category.
  - Edit existing book information.
  - Delete books from the catalog.
- **Interactive Data Display**: Uses Pandas and Streamlit dataframes for responsive data visualization and row selection.
- **Dashboard and Statistics**: View total book counts and category-wise distributions at a glance.

## Technology Stack
- **Frontend / UI**: Streamlit
- **Backend Language**: Python
- **Database**: MongoDB
- **Data Manipulation**: Pandas, NumPy
- **Environment Management**: python-dotenv

## Installation and Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bibliotecaPares
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory with the following variables:
   ```env
   MONGO_URI=your_mongodb_connection_string
   APP_PASSWORD=your_secure_password
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Usage
Upon running the application, you will be prompted to enter the passcode defined in your `.env` file. Once authenticated, use the sidebar navigation to:
- **Veure Llibres (View Books)**: Search, view, edit, or delete books.
- **Afegir nou Llibre (Add New Book)**: Register new entries into your catalog.
- **Estadístiques (Statistics)**: Review your library's analytics and category breakdowns.

## License
This project is open-source and available under the MIT License.
