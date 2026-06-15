import os
from flask import Flask, request, jsonify, send_from_directory
from modification_rockyou import affichage, recherche_hash, hashFilename, fichier_mutation

app = Flask(__name__, static_folder='static', template_folder='.')

# générer les fichiers au premier lancement
if not os.path.exists('fichier_hasher.txt'):
    print("Génération des fichiers de hash...")
    hashFilename('rockyou.txt', 'fichier_hasher.txt')
    file_mod = fichier_mutation('rockyou.txt')
    hashFilename(file_mod, 'fichier_alterer_hasher.txt')

    print("Fichiers générés !")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyser', methods=['POST'])
def analyser():
    mot_de_passe = request.json['mot_de_passe']
    
    #renvoie des données au front
    
    

if __name__ == '__main__':
    app.run(debug=True)