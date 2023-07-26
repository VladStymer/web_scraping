# Utilisez une image de base Python
FROM python:3.8-slim

# Mettez à jour et installez les dépendances nécessaires pour Chrome et ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Installez Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb

# Installez ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/`google-chrome-stable --version | sed -E 's/.* ([0-9]+).*/\1/'`/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip

# Copiez votre script et les dépendances Python dans le conteneur
COPY ./requirements.txt /app/requirements.txt
COPY ./main.py /app/main.py
COPY ./scrap.py /app/scrap.py
COPY ./interpret_result.py /app/interpret_result.py
COPY ./smtp_transfer.py /app/smtp_transfer.py

# Définissez le répertoire de travail
WORKDIR /app

# Installez les bibliothèques Python nécessaires
RUN pip install --upgrade pip && pip install -r requirements.txt

# Exécutez le script
CMD ["python", "./main.py"]
