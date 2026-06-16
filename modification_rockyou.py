import hashlib
import math
import time

# On place la chaîne vide en premier pour tester le mot de base avant les mutations
var = ['', '&', '@', '#']

# --- 1. ANALYSE THÉORIQUE ---
def affichage(mot_de_passe):
    longueur = len(mot_de_passe)
    
    # Sécurité si le champ est vide
    if longueur == 0:
        return {
            "longueur": 0, "minuscule": False, "majuscule": False, 
            "chiffre": False, "car_special": False, "entropie": 0, 
            "temps_CPU": 0, "temps_GPU": 0
        }

    minuscule = any(c.islower() for c in mot_de_passe)
    majuscule = any(c.isupper() for c in mot_de_passe)
    chiffre = any(c.isdigit() for c in mot_de_passe)
    car_special = any(not c.isalnum() for c in mot_de_passe)

    taille_alphabet = 0
    if minuscule: taille_alphabet += 26
    if majuscule: taille_alphabet += 26
    if chiffre: taille_alphabet += 10
    if car_special: taille_alphabet += 32
    
    if taille_alphabet == 0: taille_alphabet = 1 

    entropie = int(longueur * math.log2(taille_alphabet))
    nb_possibilites = taille_alphabet ** longueur
    
    return {
        "longueur": longueur,
        "minuscule": minuscule,
        "majuscule": majuscule,
        "chiffre": chiffre,
        "car_special": car_special,
        "entropie": entropie,
        "temps_CPU": nb_possibilites // 5400000000,
        "temps_GPU": nb_possibilites // 82000000000
    }

# --- 2. CASSAGE EN TEMPS RÉEL (Générateur) ---
def generateur_recherche(mot_de_passe_cible):
    """
    Teste les mots en RAM et yield (renvoie) la progression en direct.
    Plus aucune écriture sur le disque dur !
    """
    hash_cible = hashlib.md5(mot_de_passe_cible.encode('utf-8', errors='ignore')).hexdigest()
    tentatives = 0
    debut = time.time()
    
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for ligne in f:
                mot_de_base = ligne.strip()
                
                # On teste le mot de base + ses mutations
                for i in var:
                    candidat = mot_de_base + i
                    hash_candidat = hashlib.md5(candidat.encode('utf-8', errors='ignore')).hexdigest()
                    tentatives += 1
                    
                    # A. SI LE MOT EST TROUVÉ
                    if hash_candidat == hash_cible:
                        yield {
                            "type": "result", 
                            "trouve": True, 
                            "candidat": candidat, 
                            "tentatives": tentatives
                        }
                        return # Arrête le générateur
                        
                    # B. MISE À JOUR DE PROGRESSION (toutes les 4000 tentatives)
                    if tentatives % 4000 == 0:
                        temps_ecoule = time.time() - debut
                        vitesse = int(tentatives / temps_ecoule) if temps_ecoule > 0 else 0
                        yield {
                            "type": "progress", 
                            "tentatives": tentatives, 
                            "candidat": candidat, 
                            "vitesse": vitesse
                        }
                        
    except FileNotFoundError:
        yield {"type": "error", "message": "Le fichier rockyou.txt est introuvable."}
        return
        
    # C. SI LE DICTIONNAIRE EST ÉPUISÉ SANS SUCCÈS
    yield {"type": "result", "trouve": False, "tentatives": tentatives}