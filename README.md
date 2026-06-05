# WriteSphere 📝

A full-featured blog platform built with Django where users can read, write, and interact with blog posts.

## Features
- User registration and login (Author/Reader roles)
- Create, edit, and delete blog posts
- Like and comment on posts
- Follow/unfollow authors
- Category-wise posts
- Search posts by title, author, tags, category
- OTP-based password reset
- Author dashboard with analytics charts

## Tech Stack
- Python / Django
- PostgreSQL
- HTML, CSS, JavaScript

## Setup Instructions

### 1. Clone the repository
git clone https://github.com/ashish8976/blog.git
cd blog

### 2. Create virtual environment
python -m venv blog_env
blog_env\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Create .env file
SECRET_KEY=your_secret_key
EMAIL_HOST_PASSWORD=your_gmail_app_password
DB_PASSWORD=your_db_password

### 5. Run migrations
python manage.py migrate

### 6. Start server
python manage.py runserver