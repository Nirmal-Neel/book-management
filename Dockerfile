FROM python:3.11

COPY app /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "main:application", "--host", "0.0.0.0", "--port", "8000"]
