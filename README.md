Django REST API for a simple book review book_platform where users can register, log in, browse books, and submit reviews. The focus is on creating a well-structured, efficient backend without any frontend or design components.

### Running requires:
- Python 3.11 (tested under Python 3.11)

---

### Create environment file in BASE DIR /.env (see .env-example)
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

---

### Docker Launch
all you need to do is run it
#### run
```bash
docker-compose up -d --build
```
#### Creating superuser
```bash
docker-compose exec web python manage.py createsuperuser
```
the project will be launched on the port that you specify in the .env file in the variable 
NGINX_EXTERNAL_PORT
---

### Local Launch
You must have postgres and redis running for caching (I tried to achieve RESTfull)

You can replace all the necessary settings in the .env file using the example .env-example
#### 1. Install dependencies
```bash
pip install -r requirements.txt
```

#### 2. Migrations
- make migrations
  ```bash
  python manage.py makemigrations
  ```
- migrate
  ```bash
  python manage.py migrate
  ```

#### 3. Filling demo data
- Categories
    ```bash 
    python manage.py loaddata static/fixtures/category_fixtures.json
    ```
- Books
    ```bash 
    python manage.py loaddata static/fixtures/book_fixtures.json
    ```

#### 4. Running tests
- all
    ```bash
    python manage.py test
    ```
- book
    ```bash
    python manage.py test book
    ```
- accounts
    ```bash
    python manage.py test accounts
    ```
#### 5. Creating superuser 
```bash
python manage.py createsuperuser
```

#### 6. Running server
```bash
python manage.py runserver
```
---

After that successful launch you can navigate to the following pages in your browser

- Swagger - /api/v1/schema/swagger-ui/
- Redoc - /api/v1/schema/redoc/
- Admin Panel - /admin
---

GOOD LUCK
