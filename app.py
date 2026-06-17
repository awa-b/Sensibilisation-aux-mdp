from flask import Flask, request, jsonify, send_from_directory, Response
import json
import uuid  # OPTIMISATION : Génération de jetons uniques pour la sécurité
from modification_rockyou import affichage, generateur_recherche

# static_folder='.' permet de servir les fichiers css/js directement depuis la racine
app = Flask(__name__, static_folder='.', static_url_path='')

# Dictionnaire global pour stocker temporairement les mots de passe en RAM.
# Évite d'exposer le mot de passe dans l'URL de la requête GET (CWE-598).
sessions_attaque = {}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyser', methods=['POST'])
def analyser():
    """Route pour l'analyse théorique et l'initialisation sécurisée de l'attaque."""
    mdp = request.json.get('mot_de_passe', '')
    
    # 1. Calcul des statistiques théoriques
    resultats = affichage(mdp)
    
    # 2. SÉCURITÉ : Génération d'un jeton de session
    # Le mot de passe ne transitera plus jamais en clair dans l'URL.
    token = str(uuid.uuid4())
    sessions_attaque[token] = mdp 
    
    # On renvoie le jeton au Front-End
    resultats['token'] = token
    
    return jsonify(resultats)

@app.route('/recherche_stream')
def recherche_stream():
    """Route de streaming (SSE) : Reçoit un jeton anonyme au lieu du mot de passe."""
    token = request.args.get('token', '')
    
    # Récupération sécurisée depuis la RAM
    mdp = sessions_attaque.get(token)
    
    # Protection si quelqu'un tente d'appeler l'URL directement avec un faux jeton
    if not mdp:
        erreur = {"type": "error", "message": "Session invalide ou expirée."}
        return Response(f"data: {json.dumps(erreur)}\n\n", mimetype='text/event-stream')

    def generate():
        try:
            for data in generateur_recherche(mdp):
                # Le format "data: {...}\n\n" est obligatoire pour le protocole SSE
                yield f"data: {json.dumps(data)}\n\n"
        finally:
            # SÉCURITÉ (Nettoyage de la RAM) : 
            # Le bloc finally s'exécute TOUJOURS (fin de l'attaque ou déconnexion du client).
            # On détruit la trace du mot de passe de la mémoire du serveur.
            if token in sessions_attaque:
                del sessions_attaque[token]
                
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Démarrage du serveur...")
    print("Ouvrez http://127.0.0.1:5000 dans votre navigateur")
    print("="*50 + "\n")
    app.run(debug=True)