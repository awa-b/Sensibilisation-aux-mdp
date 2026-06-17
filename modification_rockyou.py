import hashlib
import math
import time
from datetime import datetime

ANNEE_COURANTE = str(datetime.now().year)

# --- 1. ANALYSE THÉORIQUE ---
# OPTIMISATION : Ajout du typage (str -> dict) pour un code plus professionnel
def affichage(mot_de_passe: str) -> dict:
    longueur = len(mot_de_passe)
    hash_md5 = hashlib.md5(mot_de_passe.encode('utf-8', errors='ignore')).hexdigest()
    
    if longueur == 0:
        return {
            "longueur": 0, "minuscule": False, "majuscule": False, 
            "chiffre": False, "car_special": False, "entropie": 0, 
            "temps_CPU": 0, "temps_GPU": 0,
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
        # OPTIMISATION : Utilisation des séparateurs '_' pour la lisibilité
        "temps_CPU": nb_possibilites // 5_400_000_000,
        "temps_GPU": nb_possibilites // 82_000_000_000,
        "hash_md5": hash_md5
    }

# --- 2. CASSAGE EN TEMPS RÉEL ---
def generer_mutations(mot_de_base: str) -> list:
    """Génère les 10 mutations les plus courantes et efficaces d'un mot."""
    if not mot_de_base:
        return []
        
    mot_cap = mot_de_base.capitalize()
    
    # L'ordre correspond aux statistiques d'utilisation humaine
    return [
        mot_de_base,                  # 1. Mot original ("soleil")
        mot_cap,                      # 2. Première lettre majuscule ("Soleil")
        mot_de_base + "123",          # 3. Ajout suite de chiffres ("soleil123")
        mot_cap + "123",              # 4. Majuscule + suite de chiffres ("Soleil123")
        mot_de_base + "!",            # 5. Ajout caractère spécial classique ("soleil!")
        mot_cap + "!",                # 6. Majuscule + caractère spécial ("Soleil!")
        mot_de_base + "123!",         # 7. Combo imposé classique ("soleil123!")
        mot_cap + "123!",             # 8. Combo classique + Majuscule ("Soleil123!")
        mot_de_base + ANNEE_COURANTE, # 9. Ajout année dynamique ("soleil2026")
        mot_cap + ANNEE_COURANTE + "!"# 10. Combo "Parfait" ("Soleil2026!")
    ]

def generateur_recherche(mot_de_passe_cible: str):
    """
    Teste les mots et leurs 10 mutations en RAM. Yield la progression en direct.
    """
    # On garde l'ignore ici au cas où la cible tapée au clavier contienne des caractères étranges
    hash_cible = hashlib.md5(mot_de_passe_cible.encode('utf-8', errors='ignore')).hexdigest()
    tentatives = 0
    debut = time.time()
    
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for ligne in f:
                mot_de_base = ligne.strip()
                mutations = generer_mutations(mot_de_base)
                
                # On teste les 10 variantes pour ce mot
                for candidat in mutations:
                    # OPTIMISATION : Suppression du errors='ignore' dans cette boucle critique 
                    # car les mutations et la lecture du fichier sont déjà propres. Gain de vitesse.
                    hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                    tentatives += 1
                    
                    # A. SI LE MOT EST TROUVÉ
                    if hash_candidat == hash_cible:
                        yield {
                            "type": "result", 
                            "trouve": True, 
                            "candidat": candidat, 
                            "tentatives": tentatives
                        }
                        return 
                        
                    # B. MISE À JOUR (toutes les 10 000 tentatives pour que le réseau suive la cadence)
                    if tentatives % 10000 == 0:
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
        
    # C. SI LE DICTIONNAIRE ET LES MUTATIONS SONT ÉPUISÉS
    yield {"type": "result", "trouve": False, "tentatives": tentatives}