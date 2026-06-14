from flask import Flask, render_template, request, redirect, url_for, flash
from data import books
import re
import random
import json
import os
from difflib import SequenceMatcher

app = Flask(__name__)

app.secret_key = "mysecretkey"

READING_LIST_FILE = "reading_list.json"


# Creates a URL-friendly version of a book title
def create_slug(title):
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


# Finds a book in data.py by title
def find_book_by_title(title):
    for book in books:
        if book["title"] == title:
            return book

    return None


# Finds a book in data.py by its URL slug
def find_book_by_slug(slug):
    for book in books:
        if create_slug(book["title"]) == slug:
            return book

    return None


# Makes older reading list items compatible with the new status system
def normalise_reading_list_book(saved_book):
    title = saved_book.get("title")
    original_book = find_book_by_title(title)

    if original_book:
        book = {
            **original_book,
            **saved_book
        }
    else:
        book = saved_book

    if "slug" not in book and book.get("title"):
        book["slug"] = create_slug(book["title"])

    if "status" not in book:
        if book.get("finished"):
            book["status"] = "Finished"
        else:
            book["status"] = "Want to Read"

    return book


# Loads reading list data from a JSON file
def load_reading_list():
    if os.path.exists(READING_LIST_FILE):
        try:
            with open(READING_LIST_FILE, "r", encoding="utf-8") as file:
                saved_books = json.load(file)

            return [
                normalise_reading_list_book(book)
                for book in saved_books
            ]

        except json.JSONDecodeError:
            print("reading_list.json is empty or invalid. Starting with an empty reading list.")
            return []

    return []


# Saves reading list data to a JSON file
def save_reading_list():
    with open(READING_LIST_FILE, "w", encoding="utf-8") as file:
        json.dump(reading_list, file, indent=4)


# Reading List
reading_list = load_reading_list()


@app.route("/")
def home():
    # Randomly select books with cover images for the homepage carousel
    available_books = [
        book for book in books
        if book.get("cover") and "placehold.co" not in book.get("cover")
    ]

    selected_books = random.sample(
        available_books,
        min(14, len(available_books))
    )

    carousel_books = []

    for book in selected_books:
        carousel_books.append({
            **book,
            "slug": create_slug(book["title"])
        })

    return render_template(
        "home.html",
        carousel_books=carousel_books
    )


# Checks whether a book is already in the user's reading list
def is_book_in_reading_list(title):
    for book in reading_list:
        if book["title"] == title:
            return True

    return False


# Calculates dashboard stats for the reading list page
def get_reading_stats():
    total_books = len(reading_list)

    want_to_read_count = 0
    currently_reading_count = 0
    finished_count = 0
    dnf_count = 0

    ratings = []

    for book in reading_list:
        status = book.get("status", "Want to Read")

        if status == "Want to Read":
            want_to_read_count += 1
        elif status == "Currently Reading":
            currently_reading_count += 1
        elif status == "Finished":
            finished_count += 1
        elif status == "Did Not Finish":
            dnf_count += 1

        if book.get("rating"):
            ratings.append(int(book["rating"]))

    if ratings:
        average_rating = round(sum(ratings) / len(ratings), 1)
    else:
        average_rating = "N/A"

    return {
        "total_books": total_books,
        "want_to_read_count": want_to_read_count,
        "currently_reading_count": currently_reading_count,
        "finished_count": finished_count,
        "dnf_count": dnf_count,
        "average_rating": average_rating
    }


# Gets related books for the book detail page
def get_related_books(current_book):
    related_books = []

    current_title = current_book.get("title")
    current_author = current_book.get("author")
    current_category = current_book.get("category")
    current_subjects = set(current_book.get("subjects", []))

    for book in books:
        if book.get("title") == current_title:
            continue

        same_author = book.get("author") == current_author
        same_category = book.get("category") == current_category
        shared_subjects = bool(current_subjects.intersection(set(book.get("subjects", []))))

        if same_author or same_category or shared_subjects:
            related_books.append({
                **book,
                "slug": create_slug(book["title"]),
                "in_reading_list": is_book_in_reading_list(book["title"])
            })

    return related_books[:4]


# Available Books List
@app.route("/books")
def books_page():
    # Get selected category from the URL
    selected_category = request.args.get("category", "All")

    # Get the current limit from the URL
    limit = request.args.get("limit", default=8, type=int)

    # Create category filter options from data.py
    category_options = sorted(
        set(book.get("category", "Uncategorised") for book in books)
    )

    # Start with all books
    filtered_books = books

    # Filter by category if one has been selected
    if selected_category != "All":
        filtered_books = [
            book for book in books
            if book.get("category", "Uncategorised") == selected_category
        ]

    # Prevent the limit from going below 8 or above the filtered book total
    if filtered_books:
        limit = max(8, min(limit, len(filtered_books)))
    else:
        limit = 8

    # Only show the books needed for the current page
    visible_books = filtered_books[:limit]

    enriched_books = []

    for book in visible_books:
        enriched_book = {
            **book,
            "slug": create_slug(book["title"]),
            "in_reading_list": is_book_in_reading_list(book["title"])
        }

        enriched_books.append(enriched_book)

    # Increase the number of books shown by 8, but do not go past the filtered total
    next_limit = min(limit + 8, len(filtered_books))

    # Check if there are more filtered books available to show
    has_more_books = limit < len(filtered_books)

    # Used by the See More button to scroll to the first newly loaded book
    next_anchor = limit + 1

    return render_template(
        "books.html",
        books=enriched_books,
        limit=limit,
        next_limit=next_limit,
        has_more_books=has_more_books,
        next_anchor=next_anchor,
        selected_category=selected_category,
        category_options=category_options,
        result_count=len(filtered_books)
    )


# Individual book detail page
@app.route("/books/<slug>")
def book_detail(slug):
    book = find_book_by_slug(slug)

    if book is None:
        return redirect(url_for("books_page"))

    book = {
        **book,
        "slug": create_slug(book["title"]),
        "in_reading_list": is_book_in_reading_list(book["title"])
    }

    related_books = get_related_books(book)

    return render_template(
        "book_detail.html",
        book=book,
        related_books=related_books
    )


# User Reading List
@app.route("/reading-list")
def reading_list_page():
    stats = get_reading_stats()

    return render_template(
        "reading_list.html",
        reading_list=reading_list,
        stats=stats
    )


# Normalises text for better searching
def normalise_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# Checks if the search term matches the start of any word
def matches_word_start(search_term, text):
    words = normalise_text(text).split()

    for word in words:
        if word.startswith(search_term):
            return True

    return False


# Gives each book a search score based on how strongly it matches
def get_search_score(book, search_term):
    if not search_term:
        return 0

    search_term = normalise_text(search_term)

    title = normalise_text(book.get("title", ""))
    author = normalise_text(book.get("author", ""))
    category = normalise_text(book.get("category", ""))
    book_type = normalise_text(book.get("type", ""))
    year = normalise_text(book.get("year", ""))
    description = normalise_text(book.get("description", ""))
    subjects = normalise_text(" ".join(book.get("subjects", [])))

    searchable_text = " ".join([
        title,
        author,
        category,
        book_type,
        year,
        description,
        subjects
    ])

    score = 0

    if search_term == title:
        score += 100

    if title.startswith(search_term):
        score += 80

    if matches_word_start(search_term, title):
        score += 70

    if search_term in title:
        score += 60

    if matches_word_start(search_term, author):
        score += 45

    if search_term in author:
        score += 40

    if search_term in category:
        score += 35

    if search_term in subjects:
        score += 30

    if search_term in book_type:
        score += 20

    if search_term in year:
        score += 20

    if search_term in description:
        score += 10

    if len(search_term) >= 3:
        title_similarity = SequenceMatcher(None, search_term, title).ratio()

        if title_similarity > 0.55:
            score += int(title_similarity * 30)

    if search_term in searchable_text:
        score += 5

    return score


# Book Search
@app.route("/search", methods=["GET", "POST"])
def search():
    results = []

    # Support both GET and POST searches
    if request.method == "POST":
        search_term = request.form.get("search", "").strip()
        selected_category = request.form.get("category", "All")
        sort_by = request.form.get("sort", "relevance")
    else:
        search_term = request.args.get("search", "").strip()
        selected_category = request.args.get("category", "All")
        sort_by = request.args.get("sort", "relevance")

    # Create category dropdown options from data.py
    category_options = sorted(
        set(book.get("category", "Uncategorised") for book in books)
    )

    # Only search once the user has entered a term or selected a category
    has_searched = bool(search_term) or selected_category != "All"

    if has_searched:
        for book in books:
            matches_category = (
                selected_category == "All"
                or book.get("category", "Uncategorised") == selected_category
            )

            search_score = get_search_score(book, search_term)

            # If no search term is entered, category filtering alone should show results
            matches_search = bool(search_score) or not search_term

            if matches_search and matches_category:
                results.append({
                    **book,
                    "slug": create_slug(book["title"]),
                    "in_reading_list": is_book_in_reading_list(book["title"]),
                    "search_score": search_score
                })

    # Sort results
    if sort_by == "relevance":
        results = sorted(
            results,
            key=lambda book: book.get("search_score", 0),
            reverse=True
        )
    elif sort_by == "title":
        results = sorted(results, key=lambda book: book.get("title", ""))
    elif sort_by == "author":
        results = sorted(results, key=lambda book: book.get("author", ""))
    elif sort_by == "year_old":
        results = sorted(results, key=lambda book: book.get("year", 0))
    elif sort_by == "year_new":
        results = sorted(
            results,
            key=lambda book: book.get("year", 0),
            reverse=True
        )

    return render_template(
        "search.html",
        results=results,
        search_term=search_term,
        selected_category=selected_category,
        category_options=category_options,
        sort_by=sort_by,
        has_searched=has_searched,
        result_count=len(results)
    )


# Contact form
@app.route("/contact", methods=["GET", "POST"])
def contact():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "")

        if len(name) < 2:
            message = "Name must be at least 2 characters."
        else:
            message = f"Thank you for your request, {name}! We will review your suggestion."

    return render_template("contact.html", message=message)


# Add book to reading list
@app.route("/add-book", methods=["POST"])
def add_book():
    title = request.form.get("title")
    book_anchor = request.form.get("book_anchor")
    current_limit = request.form.get("current_limit", default=8, type=int)

    selected_book = find_book_by_title(title)

    if selected_book and not is_book_in_reading_list(title):
        reading_list.append({
            **selected_book,
            "slug": create_slug(selected_book["title"]),
            "status": "Want to Read",
            "rating": None
        })

        save_reading_list()

        flash("Your book has been added to your reading list.")
    else:
        flash("This book is already in your reading list.")

    redirect_url = request.referrer or url_for("books_page", limit=current_limit)

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

    save_reading_list()

    flash("Book removed from your reading list.")

    redirect_url = request.referrer or url_for("reading_list_page")

    if book_anchor:
        redirect_url = redirect_url.split("#")[0] + f"#{book_anchor}"

    return redirect(redirect_url)


# Update reading status
@app.route("/update-status", methods=["POST"])
def update_status():
    title = request.form.get("title")
    status = request.form.get("status")
    book_anchor = request.form.get("book_anchor")

    allowed_statuses = [
        "Want to Read",
        "Currently Reading",
        "Finished",
        "Did Not Finish"
    ]

    if status not in allowed_statuses:
        flash("Invalid reading status.")
        return redirect(url_for("reading_list_page"))

    for book in reading_list:
        if book["title"] == title:
            book["status"] = status

            if status != "Finished":
                book["rating"] = None

            break

    save_reading_list()

    flash(f"Book status updated to {status}.")

    redirect_url = url_for("reading_list_page")

    if book_anchor:
        redirect_url = redirect_url + f"#{book_anchor}"

    return redirect(redirect_url)


# Mark finished - kept for compatibility with older forms
@app.route("/finish-book", methods=["POST"])
def finish_book():
    title = request.form.get("title")
    book_anchor = request.form.get("book_anchor")

    for book in reading_list:
        if book["title"] == title:
            book["status"] = "Finished"
            break

    save_reading_list()

    flash("Book marked as finished.")

    redirect_url = url_for("reading_list_page")

    if book_anchor:
        redirect_url = redirect_url + f"#{book_anchor}"

    return redirect(redirect_url)


# Rating system
@app.route("/rate-book", methods=["POST"])
def rate_book():
    title = request.form.get("title")
    rating = request.form.get("rating")
    book_anchor = request.form.get("book_anchor")

    for book in reading_list:
        if book["title"] == title and book.get("status") == "Finished":
            book["rating"] = int(rating)
            break

    save_reading_list()

    flash("Rating saved.")

    redirect_url = url_for("reading_list_page")

    if book_anchor:
        redirect_url = redirect_url + f"#{book_anchor}"

    return redirect(redirect_url)


if __name__ == "__main__":
    app.run(debug=True)
