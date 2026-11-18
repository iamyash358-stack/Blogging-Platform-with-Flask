# Inkwell – Flask Blog

A full-featured blog built with **Flask, SQLAlchemy, Flask-Migrate, Flask-Login and Flask-WTF**.

## Features (mapped to the internship tasks)
| Task | Where |
|------|-------|
| App factory, Blueprints (`auth`, `main`, `posts`), SQLAlchemy + Flask-Migrate | `app/__init__.py`, `app/extensions.py`, `config.py` |
| Register / login / logout / session mgmt (Flask-Login, remember-me, safe `next`) | `app/auth/routes.py`, `app/models.py` |
| Post, Category, Tag models + CRUD with Flask-WTF + rich text editor (Quill, sanitized with bleach) | `app/posts/routes.py`, `app/forms.py`, `app/utils.py` |
| Jinja2 templates: home, post view, profile + pagination | `app/templates/`, `app/main/routes.py` |
| Comments (login required, author/post-owner can delete) | `app/posts/routes.py` |
| Search by title/content + filter by tag/category (works together with pagination) | `app/main/routes.py` |
| Unit tests (pytest) | `tests/` |
| Deployment: Gunicorn + Docker + docker-compose | `Dockerfile`, `docker-compose.yml`, `Procfile` |

## Run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env

export FLASK_APP=wsgi.py          # Windows CMD: set FLASK_APP=wsgi.py | PowerShell: $env:FLASK_APP="wsgi.py"
flask db init                     # only the first time (creates migrations/)
flask db migrate -m "initial schema"
flask db upgrade
flask seed                        # optional demo data: demo@example.com / demo12345
flask run --debug                 # http://127.0.0.1:5000
```

## Tests
```bash
pytest -v
```

## Production (Gunicorn)
```bash
gunicorn -w 3 -b 0.0.0.0:8000 wsgi:app
```

## Docker
```bash
docker compose up --build         # http://localhost:8000
# optional demo data:
docker compose exec web flask --app wsgi seed
```
Tip: run `flask db init && flask db migrate` locally once and commit `migrations/` so Docker uses it (the entrypoint creates it automatically if missing).
Set a real `SECRET_KEY` for production, e.g. `SECRET_KEY=$(python -c "import secrets;print(secrets.token_hex(32))") docker compose up --build`.
