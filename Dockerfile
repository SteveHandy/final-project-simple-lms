FROM python:3.12-slim

# Mencegah pembuatan file .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Menampilkan log langsung ke terminal
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Install dependency sistem
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements terlebih dahulu agar cache Docker lebih optimal
COPY ./code/requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependency Python
RUN pip install -r requirements.txt

# Copy seluruh source code
COPY ./code .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]