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
    && rm -rf /var/lib/apt/lists/*

# Spécifiez la version de Chrome
ENV CHROME_VERSION="115.0.5790.102-1"

# Installer la version spécifique de Google Chrome
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && dpkg -i google-chrome-stable_${CHROME_VERSION}_amd64.deb || apt-get -fy install

# Détecter la version de Chrome et télécharger le pilote correspondant
RUN CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | awk -F'.' '{print $1}') \
    && wget https://chromedriver.storage.googleapis.com/$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/bin \
    && chmod +x /usr/bin/chromedriver

# Set display port as an environment variable
ENV DISPLAY=:99

# Copiez votre code et les dépendances dans le conteneur
WORKDIR /app
COPY . /app

# Installez les dépendances Python
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Configurations pour le cron
COPY mycron /etc/cron.d/mycron
RUN chmod 0644 /etc/cron.d/mycron

# Exécutez le script principal comme point d'entrée
CMD ["python", "./main.py"]
