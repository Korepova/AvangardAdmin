FROM python:3.11-slim
WORKDIR /app
COPY bot.py .
RUN pip install --no-cache-dir python-telegram-bot==20.6
CMD ["python", "bot.py"]
