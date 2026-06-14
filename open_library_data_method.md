# Open Library Data Generation and Category Assignment Method

## Overview

At first, I considered using a live book API to fetch the book catalogue, book covers, and metadata dynamically while the web app was running. However, this created performance and reliability concerns because the application would depend on external API calls every time users browsed, searched, or opened pages in the catalogue.

To solve this, I changed the approach so that the API was used during the data preparation stage instead of during normal page rendering. I created a separate Python script to collect, clean, organise, and categorise the book data in advance. The final result was saved locally in a Python data file, which the Flask app can import directly.

This means the app loads book information from local project data rather than repeatedly calling a live API.

---

## Method Used to Generate the Open Library Book Data

### 1. I used a Python script to collect book data

I created a Python script that queried the external book source/API for fantasy-related books. The purpose of the script was to gather the data once, prepare it properly, and then store it locally for the Flask application to use.

The script collected information such as:

- book title
- author
- publication year
- description
- subjects
- book type
- cover image URL

This gave me a structured dataset that could be reused throughout the application.

---

### 2. I generated a local Python data file

Instead of making the Flask app call the API every time the user loaded a page, I used the script to generate a local Python file called `data.py`.

Inside this file, I stored the book catalogue as a list of dictionaries. Each dictionary represents one book.

Example structure:

```python
books = [
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "year": 1937,
        "category": "Classic Fantasy",
        "type": "Novel",
        "description": "A fantasy adventure about Bilbo Baggins and his journey with a group of dwarves.",
        "subjects": ["Fantasy", "Adventure", "Dragons"],
        "cover": "https://..."
    }
]
```

This made the book data easy to access from the Flask app without needing another API request.

---

### 3. I imported the local dataset into Flask

In `app.py`, I imported the generated book data using:

```python
from data import books
```

This allowed all of the main pages to use the local book catalogue, including:

- the homepage carousel
- the books catalogue page
- the book detail pages
- the search page
- related book suggestions
- category filtering
- reading-list actions

Because the data is stored locally, the app can load the catalogue quickly and consistently.

---

## Why I Changed from a Live API to Local Data

Using a live API during normal app usage caused several problems.

The main issues were:

- slower page load times when many books or covers needed to be fetched
- dependency on the external API being available
- possible delays caused by network requests
- inconsistent or missing cover images
- repeated API calls during browsing and testing
- more complex error handling
- risk of API limits or unavailable data

By generating the data first and storing it locally, I made the application:

- faster
- more reliable
- easier to deploy
- easier to test
- more predictable for users
- less dependent on external services

The API was still useful, but I used it as a data preparation tool rather than a live dependency during normal use.

---

## How I Added Categories

After generating the base book data, I added categories so users could filter and browse the catalogue more easily.

The categories were based on available metadata such as:

- subjects
- keywords
- book descriptions
- titles
- known fantasy subgenres

For example, the category assignment logic could check whether certain words appeared in the book subjects or description.

Example logic:

```python
if "dragon" in subjects or "dragon" in description:
    category = "Dragon Fantasy"
elif "urban" in subjects:
    category = "Urban Fantasy"
elif "dark" in subjects or "grimdark" in description:
    category = "Grimdark Fantasy"
else:
    category = "Fantasy"
```

The final category was then stored directly inside each book dictionary.

Example:

```python
{
    "title": "Fourth Wing",
    "author": "Rebecca Yarros",
    "category": "Dragon Fantasy"
}
```

This made it possible for the Flask app to build the category filter automatically from the local dataset.

In `app.py`, the category options are generated using:

```python
category_options = sorted(
    set(book.get("category", "Uncategorised") for book in books)
)
```

This means I do not need to manually hard-code the filter options into the HTML. The app reads the available categories from the book data itself.

---

