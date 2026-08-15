import json

def find_duplicates():
    with open("output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Flatten the list of books
    all_books = []
    for category, books in data.items():
        for book in books:
            all_books.append(book)

    # Group books by (normalized_title, normalized_author)
    grouped = {}
    for book in all_books:
        title = str(book.get("Títol", "")).strip().lower()
        author = str(book.get("Autor", "")).strip().lower()
        if not title or not author:
            continue
        # Skip separator placeholders
        if author.startswith("-") or title.startswith("-"):
            continue
            
        key = (title, author)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(book)

    # Find books that are both in "Catàleg general" and in another category
    repeated_books = []
    for key, books in grouped.items():
        categories = {b.get("Categoria") for b in books}
        if len(categories) > 1 and "Catàleg general" in categories:
            repeated_books.append((key, books))

    print(f"Total repeated books found: {len(repeated_books)}")
    
    # Save the duplicates to a file for easy viewing
    report = []
    for key, books in sorted(repeated_books, key=lambda x: x[0]):
        book_info = {
            "Títol": books[0]["Títol"],
            "Autor": books[0]["Autor"],
            "Occurrences": []
        }
        print(f"\nBook: \"{books[0]['Títol']}\" by \"{books[0]['Autor']}\"")
        for b in books:
            print(f"  - Category: '{b['Categoria']}', Publisher: '{b.get('Editorial', '')}', Year: '{b.get('Any', '')}'")
            book_info["Occurrences"].append({
                "Categoria": b["Categoria"],
                "Editorial": b.get("Editorial", ""),
                "Any": b.get("Any", "")
            })
        report.append(book_info)
        
    with open("duplicates_report.json", "w", encoding="utf-8") as rf:
        json.dump(report, rf, indent=4, ensure_ascii=False)
    print("\nSaved duplicate report to duplicates_report.json")

if __name__ == "__main__":
    find_duplicates()
