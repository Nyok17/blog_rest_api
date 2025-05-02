# blog_rest_api17

A simple RESTful API for a blog application built with Flask, SQLAlchemy, and SQLite.

## Features
- Create (POST), Retrieve (GET), Update (PUT), Delete (DELETE) blog posts
- Filter posts by search term
- SQLite database (easy to use locally)

## Tech Stack
- Python
- Flask
- Flask SQLAlchemy
- SQLite

## Getting Started
1. Clone the Repo:
    ```bash
    git clone https://github.com/Nyok17/blog_rest_api17.git
    project url https://roadmap.sh/projects/blogging-platform-api
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the API:
    ```bash
    python app.py
    ```

## API Endpoints
| Method | Endpoint   | Description                |
|--------|------------|----------------------------|
| GET    | /posts     | Retrieve all posts         |
| POST   | /posts     | Create a new post          |
| PUT    | /posts/:id | Update a specific post     |
| DELETE | /posts/:id | Delete a specific post     |

## License
MIT
