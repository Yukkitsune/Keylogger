FROM python:3-slim

WORKDIR /app

COPY server.py keylogger.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]