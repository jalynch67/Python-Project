# Bookiverse

Bookiverse is a Flask web application for exploring fantasy books, viewing book details, building a personal reading list, searching the catalogue, and requesting new titles to be added. The project is designed around server-rendered Jinja templates, local JSON persistence, and a locally stored book dataset for fast and reliable page loading.

## Live Project

The project has been deployed using Render as a Python web service.

## Purpose of the Project

The aim of Bookiverse is to provide a fantasy-focused reading companion where users can:

- browse a curated catalogue of fantasy books
- view individual book detail pages
- filter books by category
- search by title, author, subject, category, year, or description keyword
- add books to a personal reading list
- remove books from the reading list
- update reading status
- mark books as finished
- add an optional rating and comment for completed books
- submit a request for a fantasy book to be added

## Features

### Homepage

The homepage introduces the application and displays:

- a featured carousel of fantasy book covers
- reading-list activity statistics
- currently reading or up-next books
- quick category links based on the catalogue

### Book Catalogue

The books page allows users to:

- browse available books
- filter books by category
- progressively load more books using a “See More Books” control
- open book detail pages
- add or remove books from the reading list

### Book Detail Page

Each book has its own detail page showing:

- cover image
- title
- author
- category
- type
- publication year
- subjects
- description
- related books based on author, category, or subject
- reading-list actions

### Search

The search page supports:

- keyword searching
- category filtering
- sorting by relevance, title, author, oldest first, or newest first
- quick-search links
- trending suggestions when no search has been made
- recommended books when no results are found

### Reading List

The reading list page allows users to:

- view saved books
- remove books from the list
- update reading status to:
  - Want to Read
  - Currently Reading
  - Finished
  - Did Not Finish
- mark books as finished
- add optional star ratings
- add optional comments or reviews
- view reading statistics

### Request a Book

The request page allows users to submit a book suggestion with:

- name
- email
- book title
- author
- reason for suggesting the book

The backend includes validation for required fields, length limits, email format, and restricted characters. Email sending was implemented through SMTP, but hosting limitations on free Render services mean SMTP traffic may be blocked unless using a paid service or an email API provider.

## Technologies Used

- Python
- Flask
- Jinja2 templates
- HTML5
- CSS3
- Bootstrap 5
- JSON file storage
- Gunicorn for production deployment
- Render for deployment

## Project Structure

Python-Project-master/
├── app.py
├── data.py
├── reading_list.json
├── book_requests.json
├── requirements.txt
├── static/
│ └── css/
│ └── style.css
└── templates/
├── base.html
├── home.html
├── books.html
├── book_detail.html
├── reading_list.html
├── search.html
└── contact.html
