FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    chromium \
    chromium-driver \
    cron \
    && apt-get clean

# Variáveis de ambiente do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos
COPY . /app

# Instalar dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Adicionar crontab
COPY scheduler/crontab /etc/cron.d/bot-cron
RUN chmod 0644 /etc/cron.d/bot-cron && crontab /etc/cron.d/bot-cron

# Criar log para o cron
RUN touch /var/log/cron.log

# Comando padrão do container
CMD cron && tail -f /var/log/cron.log



