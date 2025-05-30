FROM python:3.10-slim

# Instalar dependências essenciais
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean

# Variáveis do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copiar arquivos
WORKDIR /app
COPY . .

# Instalar dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "main.py"]
