FROM python:3.6-slim-stretch

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

VOLUME ["/app"]
VOLUME ["/opt/images"]

EXPOSE 5000

CMD ["gunicorn", "--reload", "-b", "0.0.0.0:5000", "app:app"]