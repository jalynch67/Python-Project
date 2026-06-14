# Deployment Guide — Bookiverse

## 1. Add dependencies

Create `requirements.txt`:
Flask
gunicorn

## 2. Use environment variables

In `app.py`, replace the hard-coded secret key:
app.secret_key = "mysecretkey"

with:
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

Your app already imports `os`, so no extra import is needed.

If you want the reading list JSON path configurable, update:
READING_LIST_FILE = "reading_list.json"

to:
READING_LIST_FILE = os.environ.get("READING_LIST_FILE", "reading_list.json")

Your app stores the reading list in `reading_list.json`.

## 3. Confirm project structure

Use this structure:
project-root/
├── app.py
├── data.py
├── requirements.txt
├── templates/
│ ├── base.html
│ ├── home.html
│ ├── books.html
│ ├── book_detail.html
│ ├── reading_list.html
│ ├── search.html
│ └── contact.html
└── static/
└── css/
└── style.css

`base.html` loads the custom stylesheet from `static/css/style.css`, so that file needs to be included.

## 4. Local production-style test

Install dependencies:
pip install -r requirements.txt

Run with Gunicorn:
gunicorn app:app

## 5. Deploy on Render

Create a new **Web Service** and use:

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Set environment variables:
SECRET_KEY=<generated-secret-key>

Optional, if you make the reading-list path configurable:
READING_LIST_FILE=/var/data/reading_list.json

If using email from the contact form, also add:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<your-email>
SMTP_PASSWORD=<your-password-or-app-password>
CONTACT_TO_EMAIL=<recipient-email>
MAIL_FROM=<sender-email>

Those SMTP variables are read by the book request email function.

## 6. Note on persistence

If you leave the reading list as `reading_list.json`, make sure your host preserves that file between deploys/restarts. Otherwise, use a persistent disk or move it to a database.

## 7. Final smoke test

After deploy, check:
/
/books
/search
/reading-list
/contact

Then test:

- add a book
- remove a book
- update reading status
- save a rating/comment
- submit the contact form if SMTP is configured
