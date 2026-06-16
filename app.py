import os
from flask import Flask, request, jsonify, send_from_directory
from modification_rockyou import affichage, recherche_hash, hashFilename, fichier_mutation, hacher_mdp_md5
import math


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
    
    longueur = len(mdp)
    minuscule = any(c.islower() for c in mdp)
    majuscule = any(c.isupper() for c in mdp)
    chiffre   = any(c.isdigit() for c in mdp)
    special   = any(not c.isalnum() for c in mdp)
    taille    = (26 if minuscule else 0) + (26 if majuscule else 0) \
              + (10 if chiffre else 0)   + (32 if special else 0)
    entropie  = int(longueur * math.log2(taille)) if taille else 0
    nb_poss   = taille ** longueur
    return jsonify({
        "longueur": longueur,
        "entropie": entropie,
        "classes": {"minuscule": minuscule, "majuscule": majuscule,
                    "chiffre": chiffre, "special": special},
        "temps_cpu": nb_poss // 5_400_000_000,
        "temps_gpu": nb_poss // 82_000_000_000,
    })
    

@app.route('/recherche', methods=['POST'])
def recherche():
    mdp = request.get_json()['mot_de_passe']
    tentatives = 0
    rang = None
    hash_md5 = hacher_mdp_md5(mdp)

    # cherche dans fichier simple avec comptage
    with open('fichier_hasher_simple.txt', 'r') as f:
        for i, ligne in enumerate(f, 1):
            tentatives += 1
            _, hash_candidat = ligne.strip().split(':', 1)
            if hash_candidat == hash_md5:
                rang = i
                break

    # si pas trouvé, cherche dans les mutations
    if rang is None:
        with open('fichier_alterer_hasher.txt', 'r') as f:
            for ligne in f:
                if not ligne.strip():
                    continue
                tentatives += 1
                candidat, hash_candidat = ligne.strip().rsplit(':', 1)
                if hash_candidat == hash_md5:
                    rang = tentatives
                    break

    vitesse = 500000
    return jsonify({
        "trouve": rang is not None,
        "rang": rang,
        "tentatives": tentatives,
        "vitesse": vitesse
    })
    

if __name__ == '__main__':
    app.run(debug=True)