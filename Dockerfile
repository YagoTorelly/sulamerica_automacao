FROM python:3.10-slim

# Instalar dependências básicas e Chrome + ChromeDriver
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    chromium-driver chromium && \
    apt-get clean

# Variáveis de ambiente do Chrome headless
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER=/usr/bin/chromedriver

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar cron
RUN apt-get update && apt-get install -y cron

# Copiar crontab e registrar
COPY scheduler/crontab /etc/cron.d/sula-cron
RUN chmod 0644 /etc/cron.d/sula-cron && crontab /etc/cron.d/sula-cron

# Criar log
RUN touch /var/log/cron.log

# Comando de entrada
CMD cron && tail -f /var/log/cron.log


# rodar 'docker build -t sulamerica_bot .'
