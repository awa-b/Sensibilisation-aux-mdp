from flask import Flask, request, jsonify, send_from_directory, Response
import json
from modification_rockyou import affichage, generateur_recherche

# static_folder='.' permet de servir tes fichiers css/js directement depuis la racine
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyser', methods=['POST'])
def analyser():
    """Route classique pour l'analyse théorique instantanée"""
    mdp = request.json.get('mot_de_passe', '')
    resultats = affichage(mdp)
    return jsonify(resultats)

@app.route('/recherche_stream')
def recherche_stream():
    """Route de streaming (Server-Sent Events) pour le temps réel"""
    mdp = request.args.get('mot_de_passe', '')
    
    def generate():
        for data in generateur_recherche(mdp):
            # Le format "data: {...}\n\n" est obligatoire pour le protocole SSE
            yield f"data: {json.dumps(data)}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Démarrage du serveur... (Instantané !)")
    print("Ouvrez http://127.0.0.1:5000 dans votre navigateur")
    print("="*50 + "\n")
    app.run(debug=True)