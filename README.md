`Билд:` docker-compose build

`Запуск:` docker-compose up -d

`Создать супер юзера:` docker-compose exec -it web uv run python manage.py createsuperuser


`ENV:`

DJANGO_DEBUG=True

DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1


POSTGRES_DB=mydb

POSTGRES_USER=user

POSTGRES_PASSWORD=testpass

POSTGRES_HOST=db

POSTGRES_PORT=5432
