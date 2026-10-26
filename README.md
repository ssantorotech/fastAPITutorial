# Simple Social

A minimal social media web application where authenticated users can share images and videos with a caption and browse a shared feed. The backend is built with **FastAPI**, the interface with **Streamlit**, and media files are stored and served through **ImageKit**.

## Features

- User registration and login with JWT authentication (via `fastapi-users`)
- Upload of images and videos with an optional caption
- Shared feed ordered from newest to oldest
- Deletion of your own posts only
- Captions rendered as text overlays on images through ImageKit transformations
- Interactive API documentation generated automatically (Swagger UI)

## Tech Stack

| Layer          | Technology                                   |
| -------------- | -------------------------------------------- |
| Backend API    | FastAPI, Uvicorn                             |
| Authentication | fastapi-users (JWT, bearer transport)        |
| Database       | SQLite with SQLAlchemy (async) and aiosqlite |
| Media storage  | ImageKit                                     |
| Frontend       | Streamlit                                    |

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── app.py          # FastAPI application and endpoints
│   ├── db.py           # Database models and session handling
│   ├── images.py       # ImageKit client configuration
│   ├── schemas.py      # Pydantic schemas
│   └── users.py        # Authentication and user management
├── frontend.py         # Streamlit interface
├── main.py             # Backend entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A free [ImageKit](https://imagekit.io) account

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env      # on Windows: copy .env.example .env
```

```env
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_imagekit_id
```

Both values are available in your ImageKit dashboard under **Developer options**.

### 4. Start the backend

```bash
python main.py
```

The API runs at `http://localhost:8000`. Interactive documentation is available at `http://localhost:8000/docs`. The SQLite database and its tables are created automatically on first launch.

### 5. Start the frontend

In a second terminal (with the virtual environment active):

```bash
streamlit run frontend.py
```

The interface opens at `http://localhost:8501`. Enter an email and password, click **Sign Up** to create an account, then **Login**.

## API Overview

| Method | Endpoint                 | Description                         | Auth |
| ------ | ------------------------ | ----------------------------------- | ---- |
| POST   | `/auth/register`         | Create a new account                | No   |
| POST   | `/auth/jwt/login`        | Obtain a JWT access token           | No   |
| GET    | `/users/me`              | Current user profile                | Yes  |
| POST   | `/upload`                | Upload a file with an optional caption | Yes |
| GET    | `/feed`                  | List all posts                      | Yes  |
| DELETE | `/posts/{post_id}`       | Delete one of your own posts        | Yes  |

Password reset and email verification routes provided by `fastapi-users` are also exposed under `/auth`. The full schema is available at `/docs`.

## Security Notes

- The JWT secret in `app/users.py` is a placeholder. Replace it with a strong, private value before any real deployment.
- Never commit your `.env` file. It is already excluded through `.gitignore`.

## Status

This is an early version of the project and it is under active development.
