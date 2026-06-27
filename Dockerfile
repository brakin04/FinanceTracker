# Set Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y libgomp1
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5050

CMD ["python", "app.py"]
