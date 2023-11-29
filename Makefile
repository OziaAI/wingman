PYCACHE = $(wildcard */*/__pycache__ */__pycache__)
run:
	poetry run python3 manage.py runserver

migrate:
	poetry run python3 manage.py migrate

gen-secret:
	poetry run python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

clean:
	rm -rf $(PYCACHE)
