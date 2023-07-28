
# supprimer les containers
    # docker rm -f $(docker ps -a -q)

# supprimer les images
    # docker rmi -f $(docker images -a -q)

# build l'image
    # sudo docker build -t my-python-app . 

# run l'image
    # sudo docker run my-python-app 

# run l'image avec un volume
# La commande -v $(pwd):/app monte votre répertoire actuel dans le répertoire /app du conteneur, 
# et -w /app définit le répertoire de travail du conteneur sur /app.
    # docker run -v $(pwd):/app -w /app python python script.py 