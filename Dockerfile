# Utilisez une image de base Python
FROM python:3.8

# Mettez à jour et installez les dépendances nécessaires pour Chrome, ChromeDriver et autres outils
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    cron \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copiez votre code et les dépendances dans le conteneur
WORKDIR /app
COPY . /app
COPY /usr/bin/chromedriver /app/chromedriver

# RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip \
#     && unzip chromedriver-linux64.zip -d /usr/bin \
#     && mv /usr/bin/chromedriver-linux64/chromedriver /usr/bin/chromedriver \
#     && rm -rf /usr/bin/chromedriver-linux64 \
#     && rm chromedriver-linux64.zip \
#     && chmod +x /usr/bin/chromedriver

RUN mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver


# Set display port as an environment variable
ENV DISPLAY=:99

# Installez les dépendances Python
RUN pip install --default-timeout=1000 --upgrade pip

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Configurations pour le cron
COPY mycron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron

# Exécutez le script principal comme point d'entrée
CMD ["python", "./main.py"]
