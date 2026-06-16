# Sensibilisation-aux-mdp : Le Mur des Mots de Passe

Application interactive de médiation scientifique autour de la robustesse des mots de passe, destinée à des collégiens et lycéens dans le cadre d'événements de vulgarisation (Fête de la Science, journées portes ouvertes, ateliers en classe).



Description

L'application permet à un visiteur de saisir un mot de passe et d'obtenir en temps réel :
- Une analyse théorique : longueur, classes de caractères utilisées, entropie, temps de cassage estimé
- Une vérification dans une liste des mots de passe les plus fréquents (rockyou.txt) et dans une liste de mutations
- Un verdict pédagogique en fonction de la prévisibilité du mot de passe avec des conseils concrets



 Structure du projet

Sensibilisation-aux-mdp/
├── app.py                    # Serveur Flask 
├── modification_rockyou.py   # Analyse des mots de passe et recherche dans la wordlist et les mutations
├── index.html                # Interface utilisateur 
├── static/
│   ├── css/
│   │   └── style.css         # Styles de l'interface
│   └── js/
│       └── app.js            # Logique frontend et communication avec le backend
├── Dockerfile                # Configuration Docker
├── .dockerignore             # Fichiers exclus de l'image Docker
├── requirements.txt          # Dépendances Python
├── .gitignore                # Fichiers ignorés par Git
└── README.md                 # Ce fichier




 Prérequis

 Sans Docker
- Python 3.11+
- pip
- Le fichier rockyou.txt à placer à la racine du projet

 Avec Docker
- Docker Desktop installé et démarré
- Le fichier rockyou.txt à placer à la racine du projet



Lancement

Sans Docker

1- Cloner le repo

git clone https://github.com/awa-b/Sensibilisation-aux-mdp.git
cd Sensibilisation-aux-mdp


2- Installer les dépendances

pip install -r requirements.txt


3- Lancer l'application

python3 app.py


4- Ouvrir dans le navigateur

http://127.0.0.1:5000




Avec Docker

1- Construire l'image

docker build -t sensibilisation-mdp .


2- Lancer le conteneur

docker run -p 5000:5000 sensibilisation-mdp


3- Ouvrir dans le navigateur

http://127.0.0.1:5000



Notes importantes

- Aucun mot de passe n'est enregistré :  tout le traitement se fait en mémoire vive

- Le fichier rockyou.txt n'est pas inclus dans le repo car trop volumineux, il doit être téléchargé séparément à partir de ce lien : 
https://drive.google.com/file/d/1OhN4kPLHHObmdxKh-w9n7N9Pm_BQU5jW/view



 Mise à jour après modification du code


docker build -t sensibilisation-mdp .
docker run -p 5000:5000 sensibilisation-mdp







