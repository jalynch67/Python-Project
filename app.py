from flask import Flask, render_template, request, redirect, url_for, flash
from data import books
import requests
import json
import os

app = Flask(__name__)

app.secret_key = "mysecretkey"

# Reading List
reading_list = []

# File used to store book details so API results are saved between app restarts
CACHE_FILE = "book_cache.json"


# Loads saved book details from the cache file if it exists
def load_book_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            return json.load(file)

    return {}


# Saves book details to the cache file
def save_book_cache():
    with open(CACHE_FILE, "w") as file:
        json.dump(book_cache, file, indent=4)


# Stores book details fetched from Open Library
book_cache = load_book_cache()


# Fetching book details from Open Library
def get_book_info(title, author):
    """
    Fetch extra book details from Open Library, including the cover image,
    subjects, and a fuller description where available.
    Cache results to improve performance and avoid repeated API calls.
    """

    cache_key = f"{title}-{author}"

    # Return saved book details if this book has already been fetched
    if cache_key in book_cache:
        return book_cache[cache_key]

    fallback = {
        "cover": "https://placehold.co/200x300?text=No+Cover",
        "description": "No description available.",
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
            book_cache[cache_key] = fallback
            save_book_cache()
            return fallback

        book_data = docs[0]

        cover_id = book_data.get("cover_i")

        if cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        else:
            cover_url = fallback["cover"]

        subjects = book_data.get("subject", [])[:3]

        description = "No description available."

        # Open Library search results often include a work key.
        # We use this to make a second request for a better description.
        work_key = book_data.get("key")

        if work_key:
            work_url = f"https://openlibrary.org{work_key}.json"

            work_response = requests.get(work_url, timeout=10)
            work_response.raise_for_status()

            work_data = work_response.json()

            work_description = work_data.get("description")

            if isinstance(work_description, dict):
                description = work_description.get("value", "No description available.")
            elif isinstance(work_description, str):
                description = work_description

        # If no full description was found, use subjects as a better fallback
        if description == "No description available.":
            if subjects:
                description = "Themes include " + ", ".join(subjects).lower() + "."
            elif book_data.get("first_publish_year"):
                description = f"First published in {book_data.get('first_publish_year')}."

        book_info = {
            "cover": cover_url,
            "description": description,
            "subjects": subjects
        }

        # Save the fetched book details so future page loads are faster
        book_cache[cache_key] = book_info
        save_book_cache()

        return book_info

    except Exception as error:
        print(f"Open Library error for {title}: {error}")

        # Do not save fallback here, so temporary API errors are not cached permanently
        return fallback


@app.route("/")
def home():
    return render_template("home.html")


# Available Books List
@app.route("/books")
def books_page():
    # Get the current limit from the URL
    limit = request.args.get("limit", default=8, type=int)

    # Prevent the limit from going below 8 or above the total number of books
    limit = max(8, min(limit, len(books)))

    # Only fetch details for the books we are actually showing
    visible_books = books[:limit]

    enriched_books = []

    for book in visible_books:
        extra = get_book_info(
            book["title"],
            book["author"]
        )

        enriched_book = {
            **book,
            **extra
        }

        enriched_books.append(enriched_book)

    # Increase the number of books shown by 8, but do not go past the total
    next_limit = min(limit + 8, len(books))

    # Check if there are more books available to show
    has_more_books = limit < len(books)

    # Used by the See More button to scroll to the first newly loaded book
    next_anchor = limit + 1

    return render_template(
        "books.html",
        books=enriched_books,
        limit=limit,
        next_limit=next_limit,
        has_more_books=has_more_books,
        next_anchor=next_anchor
    )


# User Reading List
@app.route("/reading-list")
def reading_list_page():
    return render_template("reading_list.html", reading_list=reading_list)


# Book Search
@app.route("/search", methods=["GET", "POST"])
def search():
    results = []

    if request.method == "POST":
        search_term = request.form.get("search", "").lower()

        for book in books:
            if search_term in book["title"].lower():
                results.append(book)

    return render_template("search.html", results=results)


# Contact form
@app.route("/contact", methods=["GET", "POST"])
def contact():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "")

        if len(name) < 2:
            message = "Name must be at least 2 characters."
        else:
            message = f"Thank you for your message, {name}!"

    return render_template("contact.html", message=message)


# Add book to reading list
@app.route("/add-book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")

    if title and author:
        reading_list.append({
            "title": title,
            "author": author
        })

    flash("Your book has been added successfully!")

    return redirect(url_for("books_page"))


# Remove book from reading list
@app.route("/remove-book", methods=["POST"])
def remove_book():
    title = request.form.get("title")

    for book in reading_list:
        if book["title"] == title:
            reading_list.remove(book)
            break

    flash("Book removed from your reading list.")

    return redirect(url_for("reading_list_page"))


# Mark finished
@app.route("/finish-book", methods=["POST"])
def finish_book():
    title = request.form.get("title")

    for book in reading_list:
        if book["title"] == title:
            book["finished"] = True
            break

    flash("Book marked as finished!")

    return redirect(url_for("reading_list_page"))


# Rating system
@app.route("/rate-book", methods=["POST"])
def rate_book():
    title = request.form.get("title")
    rating = request.form.get("rating")

    for book in reading_list:
        if book["title"] == title and book.get("finished"):
            book["rating"] = int(rating)
            break

    flash("Rating saved!")

    return redirect(url_for("reading_list_page"))


if __name__ == "__main__":
    app.run(debug=True)
