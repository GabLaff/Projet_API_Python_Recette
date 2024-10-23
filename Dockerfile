# Utiliser une image de base appropriée
FROM python:3.10

# Installer supervisord
RUN apt-get update && apt-get install -y supervisor

# Définir l'étiquette du mainteneur
LABEL maintainer="toto@provider.com"

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source de l'application dans le conteneur
COPY app/ ./app/

# Copier le fichier de configuration de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exposer les ports nécessaires
EXPOSE 5501 5051 5500 5050

# Commande pour démarrer supervisord
CMD ["/usr/bin/supervisord"]
