import hashlib
import math
import time
from datetime import datetime
import itertools
import string

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
        "temps_CPU": nb_possibilites // 5_400_000_000,
        "temps_GPU": nb_possibilites // 82_000_000_000,
        "hash_md5": hash_md5
    }

# --- 2. CASSAGE EN TEMPS RÉEL ---
def generer_mutations(mot_de_base: str) -> list:
    """Génère uniquement les mutations (le mot de base a déjà été testé)."""
    if not mot_de_base:
        return []
        
    mot_cap = mot_de_base.capitalize()
    
    return [
        mot_cap,                      # 1. Première lettre majuscule ("Soleil")
        mot_de_base + "123",          # 2. Ajout suite de chiffres ("soleil123")
        mot_cap + "123",              # 3. Majuscule + suite de chiffres ("Soleil123")
        mot_de_base + "!",            # 4. Ajout caractère spécial classique ("soleil!")
        mot_cap + "!",                # 5. Majuscule + caractère spécial ("Soleil!")
        mot_de_base + "123!",         # 6. Combo imposé classique ("soleil123!")
        mot_cap + "123!",             # 7. Combo classique + Majuscule ("Soleil123!")
        mot_de_base + ANNEE_COURANTE, # 8. Ajout année dynamique ("soleil2026")
        mot_cap + ANNEE_COURANTE + "!"# 9. Combo "Parfait" ("Soleil2026!")
    ]

def generateur_recherche(mot_de_passe_cible: str):
    hash_cible = hashlib.md5(mot_de_passe_cible.encode('utf-8', errors='ignore')).hexdigest()
    tentatives = 0
    debut = time.time()
    dernier_envoi = debut 
    
    def envoyer_progression(tents, cand):
        """Sous-fonction pour gérer l'envoi au Front-End proprement (Anti-Glitch)"""
        nonlocal dernier_envoi
        if tents % 5000 == 0:
            maintenant = time.time()
            if maintenant - dernier_envoi >= 0.06:
                temps_ecoule = maintenant - debut
                vit = int(tents / temps_ecoule) if temps_ecoule > 0 else 0
                dernier_envoi = maintenant
                return {"type": "progress", "tentatives": tents, "candidat": cand, "vitesse": vit}
        return None

    # --- ÉTAPE 1 : FORCE BRUTE PURE (Uniquement si <= 4 caractères) ---
    if len(mot_de_passe_cible) <= 4:
        import itertools
        import string
        alphabet = string.ascii_letters + string.digits 
        
        for longueur in range(1, 5):
            for tentative_tuple in itertools.product(alphabet, repeat=longueur):
                candidat = "".join(tentative_tuple)
                hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                tentatives += 1
                
                if hash_candidat == hash_cible:
                    yield {"type": "result", "trouve": True, "candidat": candidat, "tentatives": tentatives, "methode": "Force Brute pure"}
                    return
                
                progression = envoyer_progression(tentatives, candidat)
                if progression: yield progression

    # --- ÉTAPE 2 : DICTIONNAIRE PUR ---
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            rang = 0
            for ligne in f:
                rang += 1
                candidat = ligne.strip()
                hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                tentatives += 1
                
                if hash_candidat == hash_cible:
                    yield {
                        "type": "result", 
                        "trouve": True, 
                        "candidat": candidat, 
                        "tentatives": tentatives, 
                        "methode": "Dictionnaire (Mot exact)",
                        "rang": rang 
                    }
                    return 
                    
                progression = envoyer_progression(tentatives, candidat)
                if progression: yield progression
    except FileNotFoundError:
        yield {"type": "error", "message": "Le fichier rockyou.txt est introuvable."}
        return

    # --- ÉTAPE 3 : DICTIONNAIRE + MUTATIONS ---
    try:
        with open('rockyou.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for ligne in f:
                mot_de_base = ligne.strip()
                mutations = generer_mutations(mot_de_base)
                
                for candidat in mutations:
                    hash_candidat = hashlib.md5(candidat.encode('utf-8')).hexdigest()
                    tentatives += 1
                    
                    if hash_candidat == hash_cible:
                        yield {"type": "result", "trouve": True, "candidat": candidat, "tentatives": tentatives, "methode": "Dictionnaire + Mutation intelligente"}
                        return 
                        
                    progression = envoyer_progression(tentatives, candidat)
                    if progression: yield progression
    except FileNotFoundError:
        pass

    # --- FIN : CIBLE INTROUVABLE ---
    yield {"type": "result", "trouve": False, "tentatives": tentatives}