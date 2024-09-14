FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry lock --no-update
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
