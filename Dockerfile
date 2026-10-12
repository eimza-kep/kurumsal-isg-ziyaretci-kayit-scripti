FROM python:3.12-alpine

WORKDIR /app

COPY . /app

RUN chmod -R 755 /app

ENV PORT=8089
EXPOSE 8089

CMD ["python", "server.py"]
