from flask import Flask, render_template, request, redirect, url_for, flash
from data import books
import requests

app = Flask(__name__)

app.secret_key = "mysecretkey"

# Reading List
reading_list = []

app = Flask(__name__)
app.secret_key = "mysecretkey"

reading_list = []

# Cache Google Books results so each book is only fetched once
book_cache = {}

def get_book_info(title, author):
    cache_key = f"{title}-{author}"

    if cache_key in book_cache:
        return book_cache[cache_key]

    fallback = {
        "cover": "https://placehold.co/200x300?text=No+Cover",
        "description": "No description available.",
        "rating": "N/A",
        "ratings_count": 0
    }

    url = "https://openlibrary.org/search.json"

    params = {
        "title": title,
        "author": author,
        "limit": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        docs = data.get("docs", [])

        if not docs:
            book_cache[cache_key] = fallback
            return fallback

        book_data = docs[0]

        cover_id = book_data.get("cover_i")

        if cover_id:
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        else:
            cover_url = fallback["cover"]

        description = (
            f"First published in {book_data.get('first_publish_year', 'unknown year')}."
            if book_data.get("first_publish_year")
            else "No description available."
        )

        book_info = {
            "cover": cover_url,
            "description": description,
            "rating": "N/A",
            "ratings_count": 0
        }

        book_cache[cache_key] = book_info
        return book_info

    except Exception as error:
        print(f"Open Library error for {title}: {error}")
        book_cache[cache_key] = fallback
        return fallback

@app.route("/")
def home():
    return render_template("home.html")


# Available Books List
@app.route("/books")
def books_page():

    enriched_books = []

    for book in books[:20]:
        extra = get_book_info(
            book["title"],
            book["author"]
        )

        enriched_book = {
            **book,
            **extra
        }

        enriched_books.append(enriched_book)

    return render_template(
        "books.html",
        books=enriched_books
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
        if book["title"] == title and book["finished"]:
            book["rating"] = int(rating)
            break

    flash("Rating saved!")

    return redirect(url_for("reading_list_page"))


if __name__ == "__main__":
    app.run(debug=True)
