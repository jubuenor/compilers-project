FROM python:3.9-slim

WORKDIR /backend

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /backend

CMD ["fastapi", "run", "main.py", "--port", "8080"]
