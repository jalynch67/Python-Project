import requests
import pprint
from data import books


def get_static_book_data(title, author, year):
    fallback = {
        "cover": "https://placehold.co/200x300?text=No+Cover",
        "description": f"First published in {year}.",
        "subjects": []
    }

    search_url = "https://openlibrary.org/search.json"

    params = {
        "title": title,
        "author": author,
        "limit": 1
    }

    try:
        search_response = requests.get(search_url, params=params, timeout=10)
        search_response.raise_for_status()

        search_data = search_response.json()
        docs = search_data.get("docs", [])

        if not docs:
            return fallback

        book_data = docs[0]

        cover_id = book_data.get("cover_i")

        if cover_id:
            cover = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        else:
            cover = fallback["cover"]

        subjects = book_data.get("subject", [])[:3]

        description = fallback["description"]

        work_key = book_data.get("key")

        if work_key:
            work_url = f"https://openlibrary.org{work_key}.json"

            work_response = requests.get(work_url, timeout=10)
            work_response.raise_for_status()

            work_data = work_response.json()
            work_description = work_data.get("description")

            if isinstance(work_description, dict):
                description = work_description.get("value", description)
            elif isinstance(work_description, str):
                description = work_description

        if description == fallback["description"] and subjects:
            description = "Themes include " + ", ".join(subjects).lower() + "."

        return {
            "cover": cover,
            "description": description,
            "subjects": subjects
        }

    except Exception as error:
        print(f"Error fetching {title}: {error}")
        return fallback


enriched_books = []

for index, book in enumerate(books, start=1):
    print(f"{index}. Fetching {book['title']}...")

    extra = get_static_book_data(
        book["title"],
        book["author"],
        book["year"]
    )

    enriched_books.append({
        **book,
        **extra
    })


with open("data_static.py", "w") as file:
    file.write("books = ")
    file.write(pprint.pformat(enriched_books, width=120))
    file.write("\n")

print("Done. Created data_static.py")