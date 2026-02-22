FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir uwsgi

COPY . .

RUN touch /app/app.log && chmod 666 /app/app.log

ENV FLASK_APP=app.py

EXPOSE 5000

RUN useradd -m appuser

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["uwsgi", "--ini", "uwsgi.ini"]