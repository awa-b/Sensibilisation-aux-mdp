import os
from flask import Flask, request, jsonify, send_from_directory
from modification_rockyou import affichage, recherche_hash, hashFilename, fichier_mutation



app = Flask(__name__, static_folder='static', template_folder='.')

# générer les fichiers au premier lancement
if not os.path.exists('fichier_hasher.txt'):
    print("Génération des fichiers de hash...")
    hashFilename('rockyou.txt', 'fichier_hasher_simple.txt')
    
    fichier_mutation('rockyou.txt')
    hashFilename('fichier_alterer.txt', 'fichier_alterer_hasher.txt')
    

    print("Fichiers générés !")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyser', methods=['POST'])
def analyser():
    mdp = request.json['mot_de_passe']
    
    resultats = affichage(mdp)
    return jsonify({
        "longueur": resultats["longueur"],
        "entropie": resultats["entropie"],
        "classes": {
            "minuscule": resultats["minuscule"],
            "majuscule": resultats["majuscule"],
            "chiffre": resultats["chiffre"],
            "special": resultats["car_special"]
        },
        "temps_cpu": resultats["temps_CPU"],
        "temps_gpu": resultats["temps_GPU"],
    })
    

@app.route('/recherche', methods=['POST'])
def recherche():
    mdp = request.get_json()['mot_de_passe']
    resultat = recherche_hash(mdp)
    resultat['vitesse'] = 500000
    return jsonify(resultat)
    


if __name__ == '__main__':
    app.run(debug=True)