FROM python:3.10

WORKDIR /app
COPY . .

RUN pip install flask pymongo

EXPOSE 5000 6054

CMD ["python", "app.py"]
