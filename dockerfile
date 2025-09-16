#imagem de execução do projeto django
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#* Instalar dependências necessárias
RUN apt-get update && apt-get install -y \
    wget \
    xfonts-75dpi \
    xfonts-base \
    fontconfig \
    libjpeg62-turbo \
    libxrender1 \
    libxext6 \
    libssl3 \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#* Instalar wkhtmltopdf via .deb oficial
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb

WORKDIR /app

# Copiar apenas requirements (cache de dependências no build)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

WORKDIR /app/src

EXPOSE 8000

# Executar servidor Django
ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
