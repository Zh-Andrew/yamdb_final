FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod ugo+x start.sh

CMD ["./api_yamdb/start.sh"]