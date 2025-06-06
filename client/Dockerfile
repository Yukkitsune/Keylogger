FROM python:3.-slim

WORKDIR /app

COPY client.py keylogger.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "client.py"]