PYCACHE = $(wildcard */*/__pycache__ */__pycache__)
run:
	poetry run python3 manage.py runserver

migrate:
	poetry run python3 manage.py migrate

clean:
	rm -rf $(PYCACHE)
