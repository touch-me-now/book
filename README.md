Django REST API for a simple book review book_platform where users can register, log in, browse books, and submit reviews. The focus is on creating a well-structured, efficient backend without any frontend or design components.

#### Running requires:
- Python 3.11 (tested under Python 3.11)

---

#### Create environment file in BASE DIR /.env (see .env-example)
> :warning: **Required!**
```text
    .
    ├── ...
    ├── Base dir
    │   ├── .env-example
>>> │   ├── .env
    │   ├── manage.py
    │   └── ...
    └── ...
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

Running tests
```bash
python manage.py test
```

Running
```bash
python manage.py shell
```