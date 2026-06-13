from flask import Flask, render_template, request, redirect, url_for, flash
from data import books

app = Flask(__name__)

app.secret_key = "mysecretkey"

# Reading List
reading_list = []


@app.route("/")
def home():
    return render_template("home.html")


# Checks whether a book is already in the user's reading list
def is_book_in_reading_list(title):
    for book in reading_list:
        if book["title"] == title:
            return True

    return False


# Available Books List
@app.route("/books")
def books_page():
    # Get the current limit from the URL
    limit = request.args.get("limit", default=8, type=int)

    # Prevent the limit from going below 8 or above the total number of books
    limit = max(8, min(limit, len(books)))

    # Only show the books needed for the current page
    visible_books = books[:limit]

    enriched_books = []

    for book in visible_books:
        enriched_book = {
            **book,
            "in_reading_list": is_book_in_reading_list(book["title"])
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
    book_anchor = request.form.get("book_anchor")

    if title and author and not is_book_in_reading_list(title):
        reading_list.append({
            "title": title,
            "author": author
        })

        flash("Your book has been added successfully!")
    else:
        flash("This book is already in your reading list.")

    redirect_url = request.referrer or url_for("books_page")

    if book_anchor:
        redirect_url = redirect_url.split("#")[0] + f"#{book_anchor}"

    return redirect(redirect_url)


# Remove book from reading list
@app.route("/remove-book", methods=["POST"])
def remove_book():
    title = request.form.get("title")
    book_anchor = request.form.get("book_anchor")

    for book in reading_list:
        if book["title"] == title:
            reading_list.remove(book)
            break

    flash("Book removed from your reading list.")

    redirect_url = request.referrer or url_for("reading_list_page")

    if book_anchor:
        redirect_url = redirect_url.split("#")[0] + f"#{book_anchor}"

    return redirect(redirect_url)


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
