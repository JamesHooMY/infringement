VERSION ?= "default version"

run:
	# fastapi run --reload app/main.py
	uvicorn app.main:app --reload --log-level debug

migrate:
	alembic revision --autogenerate -m $(VERSION) && alembic upgrade head

