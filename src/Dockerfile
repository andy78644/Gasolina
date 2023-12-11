FROM python:3.12.0-slim-bookworm

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . src
RUN rm src/.env
RUN rm src/celerybeat-schedule || exit 0
RUN rm -rf src/__pycache__ || exit 0

CMD [ "uvicorn", "api.main:src", "--host 0.0.0.0", "--log-level info" ]
